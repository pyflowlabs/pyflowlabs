"""Der Agent: verbindet das Modell mit den Werkzeugen (Tool-Calling-Schleife).

Ablauf:
  - Nutzer stellt eine Aufgabe.
  - Das Modell entscheidet: direkt antworten ODER ein Werkzeug aufrufen.
  - Ruft es ein Werkzeug auf, führen wir es aus und geben das Ergebnis zurück.
  - Das wiederholt sich, bis das Modell eine finale Antwort gibt.

Start:  python agent.py
"""

import json
import re

import ollama

import config
import deepsearch
import logsetup
import memory
import plugins_loader
import roles
import selfeval
import tools
import vision

log, LOG_FILE = logsetup.setup("nero.agent")

# Deep Search als Werkzeug registrieren (tiefe, mehrstufige Recherche).
tools.DISPATCH["deep_search"] = lambda question: deepsearch.deep_search(question)
tools.TOOLS_SPEC.append({
    "type": "function",
    "function": {
        "name": "deep_search",
        "description": "Tiefe, mehrstufige Web-Recherche: bildet mehrere Suchanfragen, "
                       "liest viele Quellen, iteriert und fasst mit Quellen zusammen. "
                       "Für gründliche Recherche statt einer einzelnen Suche.",
        "parameters": {
            "type": "object",
            "properties": {"question": {"type": "string", "description": "Recherchefrage"}},
            "required": ["question"],
        },
    },
})

# Langzeitgedächtnis + RAG (remember/recall/kb_ingest/kb_search) und Vision.
for _t in memory.TOOLS + vision.TOOLS:
    tools.DISPATCH[_t["name"]] = _t["func"]
    tools.TOOLS_SPEC.append(_t["spec"])

# Plugins aus plugins/ automatisch laden.
_plugins = plugins_loader.load_plugins(tools.DISPATCH, tools.TOOLS_SPEC)

# Höchstzahl Werkzeug-Runden pro Aufgabe (Schutz vor Endlosschleifen).
MAX_STEPS = 12

# Aktive Rolle + Selbstbewertung (per /role bzw. /selfcheck umschaltbar).
STATE = {"role": roles.DEFAULT_ROLE, "selfcheck": False}


def _system_prompt() -> str:
    r = roles.get(STATE["role"])
    return r["prompt"] if r else config.SYSTEM_PROMPT


# Wird an den System-Prompt gehängt, damit Modelle sich besser ans Werkzeug-
# Protokoll halten (v. a. kleinere Modelle wie das 14B).
TOOL_PROTOCOL_HINT = (
    "\n\nWerkzeug-Protokoll: Rufe ein Werkzeug nur auf, wenn nötig. Sobald ein "
    "Werkzeug ein Ergebnis geliefert hat, antworte in normaler Sprache mit dem "
    "Ergebnis. Gib dann KEIN JSON und keine weiteren Werkzeug-Aufrufe aus."
)


def _is_degenerate(answer: str) -> bool:
    """True, wenn die 'Antwort' nur ein leerer/kaputter Werkzeug-JSON ist."""
    m = re.search(r"\{.*\}", answer, re.DOTALL)
    if not m:
        return False
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return False
    # z. B. {"name": null, "arguments": null} oder leere Aufrufe
    return "name" in obj and not obj.get("name")


def _extract_tool_call(content: str):
    """Erkennt einen als Text ausgegebenen Werkzeug-Aufruf (JSON mit name/arguments).

    Manche Modelle lösen Tools nicht strukturiert aus, sondern schreiben z. B.
    {"name": "run_python", "arguments": {...}} in den Text. Das fangen wir hier ab.
    Gibt einen Aufruf im Ollama-Format zurück oder None.
    """
    if not content:
        return None
    # Zuerst in ```json ... ```-Blöcken suchen, sonst das erste JSON-Objekt.
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    candidate = m.group(1) if m else None
    if not candidate:
        m = re.search(r"(\{.*\})", content, re.DOTALL)
        candidate = m.group(1) if m else None
    if not candidate:
        return None
    try:
        obj = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    name = obj.get("name")
    args = obj.get("arguments", obj.get("parameters", {}))
    if name and name in tools.DISPATCH and isinstance(args, dict):
        log.info("Text-Werkzeugaufruf erkannt und ausgeführt: %s", name)
        return {"function": {"name": name, "arguments": args}}
    return None


def run(task: str, messages: list | None = None) -> list:
    """Bearbeitet eine Aufgabe und gibt den aktualisierten Nachrichtenverlauf zurück."""
    client = ollama.Client(host=config.OLLAMA_HOST)
    spec = roles.filter_specs(STATE["role"], tools.TOOLS_SPEC)

    if messages is None:
        messages = [{"role": "system", "content": _system_prompt() + TOOL_PROTOCOL_HINT}]
    messages.append({"role": "user", "content": task})

    last_tool_result = None
    for _ in range(MAX_STEPS):
        response = client.chat(
            model=config.MODEL,
            messages=messages,
            tools=spec,
        )
        msg = response["message"]
        messages.append(msg)

        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            # Fallback: manche Modelle geben den Werkzeug-Aufruf als Text-JSON
            # aus, statt ihn strukturiert auszulösen. Diesen erkennen und ausführen.
            fb = _extract_tool_call(msg.get("content", ""))
            if fb:
                tool_calls = [fb]

        if not tool_calls:
            # Keine Werkzeug-Aufrufe mehr -> finale Antwort.
            answer = msg.get("content", "").strip()
            # Kleine Modelle geben nach einem Werkzeug manchmal leeren/kaputten
            # JSON statt einer Antwort aus. Dann das Werkzeug-Ergebnis direkt zeigen.
            if (not answer or _is_degenerate(answer)) and last_tool_result:
                answer = last_tool_result
            if STATE["selfcheck"] and answer:
                verdict = selfeval.critique_and_improve(client, task, answer)
                if verdict["improved"]:
                    print("   🔁 Selbstbewertung: verbessert")
                    answer = verdict["final"]
            print(f"\n🤖 {answer}\n")
            return messages

        # Alle angeforderten Werkzeuge ausführen und Ergebnisse zurückgeben.
        for call in tool_calls:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}

            print(f"   ⚙️  {name}({', '.join(f'{k}={str(v)[:50]}' for k, v in args.items())})")

            func = tools.DISPATCH.get(name)
            if not func:
                result = f"Unbekanntes Werkzeug: {name}"
                log.warning(result)
            else:
                try:
                    result = func(**args)
                except Exception as exc:  # noqa: BLE001
                    result = f"Werkzeug '{name}' ist abgestürzt: {exc}"
                    log.exception("Werkzeug %s fehlgeschlagen (args=%s)", name, args)

            last_tool_result = str(result)
            messages.append({"role": "tool", "name": name, "content": str(result)})

    # MAX_STEPS erreicht: falls ein Werkzeug lief, dessen Ergebnis zeigen.
    if last_tool_result:
        print(f"\n🤖 {last_tool_result}\n")
    else:
        print("\n⚠️  Maximale Schrittzahl erreicht.\n")
    return messages


def main() -> None:
    print("Lokaler Agent bereit. Aufgabe eingeben (oder 'exit').")
    print(f"Modell: {config.MODEL}")
    print(f"Werkzeuge: {', '.join(sorted(tools.DISPATCH))}")
    if _plugins:
        print(f"Plugins: {', '.join(_plugins)}")
    print(f"Rolle: {STATE['role']}  ·  Befehle: /roles, /role <name>, /selfcheck")
    print(f"Protokoll: {LOG_FILE}\n")
    history: list | None = None
    while True:
        try:
            task = input("👤 ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if task.lower() in {"exit", "quit", "ende"}:
            break
        if not task:
            continue

        # Befehle
        if task == "/roles":
            for n in roles.names():
                print(f"   {n:12} – {roles.get(n)['desc']}")
            continue
        if task.startswith("/role "):
            new = task.split(maxsplit=1)[1].strip()
            if roles.get(new):
                STATE["role"] = new
                history = None  # neuer System-Prompt -> Verlauf zurücksetzen
                print(f"   Rolle: {new}")
            else:
                print(f"   Unbekannte Rolle: {new} (siehe /roles)")
            continue
        if task == "/selfcheck":
            STATE["selfcheck"] = not STATE["selfcheck"]
            print(f"   Selbstbewertung: {'an' if STATE['selfcheck'] else 'aus'}")
            continue

        history = run(task, history)


if __name__ == "__main__":
    main()
