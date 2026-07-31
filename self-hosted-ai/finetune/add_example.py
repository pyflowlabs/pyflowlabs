#!/usr/bin/env python3
"""Ein Trainingsbeispiel sammeln = ein Befehl.

Hängt ein geprüftes Beispiel an den Datensatz an. So sammelst du im Alltag
nebenbei Material fürs spätere Feintuning.

Beispiele:
    python add_example.py -i "Wie stoppe ich alle Docker-Container?" \
                          -o "docker stop \$(docker ps -q)"

    # mit optionalem Kontext (input):
    python add_example.py -i "Fasse den Text zusammen." \
                          --context "<langer Text>" -o "<Zusammenfassung>"

Der Datensatz wächst in dataset/collected.jsonl. Vor dem Training prüft der
'reviewer'-Subagent die gesammelten Beispiele auf Qualität.
"""

import argparse
import json
import os

DATASET = os.path.join(os.path.dirname(__file__), "dataset", "collected.jsonl")


def add(instruction: str, output: str, context: str = "") -> None:
    example = {"instruction": instruction.strip(), "input": context.strip(), "output": output.strip()}
    if not example["instruction"] or not example["output"]:
        raise SystemExit("Fehler: instruction (-i) und output (-o) dürfen nicht leer sein.")

    os.makedirs(os.path.dirname(DATASET), exist_ok=True)
    # Validieren, dass es sauberes JSON ergibt, dann anhängen.
    line = json.dumps(example, ensure_ascii=False)
    with open(DATASET, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    total = sum(1 for _ in open(DATASET, encoding="utf-8"))
    print(f"Gespeichert. Gesammelte Beispiele: {total}  ->  {DATASET}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Ein Trainingsbeispiel zum Datensatz hinzufügen.")
    p.add_argument("-i", "--instruction", required=True, help="Anweisung/Frage")
    p.add_argument("-o", "--output", required=True, help="Gewünschte Antwort")
    p.add_argument("--context", default="", help="Optionaler Kontext (input)")
    args = p.parse_args()
    add(args.instruction, args.output, args.context)
