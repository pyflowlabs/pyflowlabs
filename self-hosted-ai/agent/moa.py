#!/usr/bin/env python3
"""Mixture of Agents – mehrere Modelle arbeiten an EINER Antwort zusammen.

Ablauf:
  1. Jedes "Proposer"-Modell (z. B. Qwen-Coder + Dolphin) beantwortet die Aufgabe.
  2. Ein "Aggregator"-Modell liest alle Entwürfe und baut die beste finale Antwort
     daraus – nimmt die stärksten Teile, korrigiert Fehler.

Das ist mehr als paralleles Antworten (wie in der Oberfläche): die Modelle
ergänzen sich zu einem Ergebnis.

Start:  python moa.py
Modelle festlegen in config.py -> MOA_PROPOSERS / MOA_AGGREGATOR.
"""

import ollama

import config


def ask_moa(task: str, proposers=None, aggregator=None):
    client = ollama.Client(host=config.OLLAMA_HOST)
    proposers = proposers or config.MOA_PROPOSERS
    aggregator = aggregator or config.MOA_AGGREGATOR

    drafts = []
    for model in proposers:
        print(f"   … {model} denkt nach")
        resp = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "user", "content": task},
            ],
        )
        drafts.append((model, resp["message"]["content"].strip()))

    combined = "\n\n".join(f"[Entwurf von {m}]\n{txt}" for m, txt in drafts)
    agg_prompt = (
        f"Aufgabe:\n{task}\n\n"
        f"Mehrere Modelle haben unabhängig geantwortet:\n\n{combined}\n\n"
        "Erstelle die bestmögliche finale Antwort. Nimm die stärksten Teile, "
        "korrigiere Fehler, löse Widersprüche auf. Gib nur die finale Antwort aus."
    )
    print(f"   … {aggregator} führt zusammen")
    final = client.chat(
        model=aggregator,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": agg_prompt},
        ],
    )
    return final["message"]["content"].strip(), drafts


def main() -> None:
    print("Mixture of Agents bereit.")
    print(f"Proposer: {', '.join(config.MOA_PROPOSERS)}")
    print(f"Aggregator: {config.MOA_AGGREGATOR}\n")
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
        answer, _ = ask_moa(task)
        print(f"\n🤖 {answer}\n")


if __name__ == "__main__":
    main()
