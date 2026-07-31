"""Der Agent: verbindet das Modell mit den Werkzeugen (Tool-Calling-Schleife).

Ablauf:
  - Nutzer stellt eine Aufgabe.
  - Das Modell entscheidet: direkt antworten ODER ein Werkzeug aufrufen.
  - Ruft es ein Werkzeug auf, führen wir es aus und geben das Ergebnis zurück.
  - Das wiederholt sich, bis das Modell eine finale Antwort gibt.

Start:  python agent.py
"""

import json

import ollama

import config
import tools

# Höchstzahl Werkzeug-Runden pro Aufgabe (Schutz vor Endlosschleifen).
MAX_STEPS = 12


def run(task: str, messages: list | None = None) -> list:
    """Bearbeitet eine Aufgabe und gibt den aktualisierten Nachrichtenverlauf zurück."""
    client = ollama.Client(host=config.OLLAMA_HOST)

    if messages is None:
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": task})

    for _ in range(MAX_STEPS):
        response = client.chat(
            model=config.MODEL,
            messages=messages,
            tools=tools.TOOLS_SPEC,
        )
        msg = response["message"]
        messages.append(msg)

        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            # Keine Werkzeug-Aufrufe mehr -> finale Antwort.
            print(f"\n🤖 {msg.get('content', '').strip()}\n")
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
            result = func(**args) if func else f"Unbekanntes Werkzeug: {name}"

            messages.append({"role": "tool", "name": name, "content": str(result)})

    print("\n⚠️  Maximale Schrittzahl erreicht.\n")
    return messages


def main() -> None:
    print("Lokaler Agent bereit. Aufgabe eingeben (oder 'exit').")
    print(f"Modell: {config.MODEL}\n")
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
        history = run(task, history)


if __name__ == "__main__":
    main()
