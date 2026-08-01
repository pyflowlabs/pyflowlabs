#!/usr/bin/env python3
"""Autonome Multi-Agenten-Kollaboration (#6): ein Koordinator verteilt Teilaufgaben
an spezialisierte Rollen-Agenten und fasst die Ergebnisse zusammen.

Ablauf:
  1. Koordinator zerlegt die Aufgabe in Teilaufgaben mit je einer passenden Rolle.
  2. Jede Teilaufgabe wird vom passenden Rollen-Agenten bearbeitet (eigene
     Werkzeuge/Prompt).
  3. Der Koordinator baut aus den Teilergebnissen die finale Antwort.

Start:  python team.py
"""

import json
import re

import config
import logsetup
import roles

log, LOG_FILE = logsetup.setup("nero.team")


def parse_plan(text: str) -> list:
    """Extrahiert [{role, task}, ...] aus der Modellantwort (robust). Testbar."""
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    plan = []
    for step in data:
        if isinstance(step, dict) and step.get("task"):
            role = step.get("role", roles.DEFAULT_ROLE)
            if role not in roles.ROLES:
                role = roles.DEFAULT_ROLE
            plan.append({"role": role, "task": step["task"]})
    return plan


def run_team(task: str) -> str:
    import ollama
    import agent
    client = ollama.Client(host=config.OLLAMA_HOST)

    role_list = ", ".join(f"{n} ({roles.get(n)['desc']})" for n in roles.names())
    plan_prompt = (
        f"Zerlege die folgende Aufgabe in 2–5 Teilaufgaben und weise jeder die am "
        f"besten passende Rolle zu. Verfügbare Rollen: {role_list}.\n"
        f"Antworte NUR als JSON-Liste: [{{\"role\": \"...\", \"task\": \"...\"}}].\n\n"
        f"AUFGABE:\n{task}"
    )
    resp = client.chat(model=config.MODEL, messages=[{"role": "user", "content": plan_prompt}])
    plan = parse_plan(resp["message"]["content"])
    if not plan:
        plan = [{"role": roles.DEFAULT_ROLE, "task": task}]

    results = []
    for step in plan:
        print(f"   👥 {step['role']}: {step['task']}")
        agent.STATE["role"] = step["role"]
        history = agent.run(step["task"], None)
        # letzte Assistenten-Antwort einsammeln
        answer = next((m.get("content", "") for m in reversed(history)
                       if m.get("role") == "assistant" and m.get("content")), "")
        results.append((step["role"], step["task"], answer))

    combined = "\n\n".join(f"[{r}] {t}\n{a}" for r, t, a in results)
    synth = client.chat(model=config.MODEL, messages=[
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": f"Aufgabe: {task}\n\nTeilergebnisse:\n{combined}\n\n"
                                    f"Fasse zu einer vollständigen, finalen Antwort zusammen."},
    ])
    return synth["message"]["content"].strip()


def main() -> None:
    print("Team-Modus (Multi-Agenten). Aufgabe eingeben (oder 'exit').")
    print(f"Rollen: {', '.join(roles.names())}\nProtokoll: {LOG_FILE}\n")
    while True:
        try:
            task = input("👥 ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if task.lower() in {"exit", "quit", "ende"}:
            break
        if task:
            print(f"\n🤖 {run_team(task)}\n")


if __name__ == "__main__":
    main()
