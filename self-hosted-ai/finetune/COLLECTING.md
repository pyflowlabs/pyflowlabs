# Trainingsdaten sammeln (im Alltag, nebenbei)

Ziel: ohne Aufwand genug **gute** Beispiele ansammeln, damit das spätere
Feintuning (Phase 5) Wirkung zeigt. **Qualität schlägt Menge** — 300 saubere
Beispiele sind mehr wert als 5.000 schlechte.

## Dateien

| Datei | Inhalt |
| --- | --- |
| `dataset/seed.jsonl` | Startbeispiele (dein Stack, dein Stil) — schon angelegt |
| `dataset/collected.jsonl` | Was du im Alltag dazusammelst (wächst mit der Zeit) |

Format je Zeile (JSONL):
```json
{"instruction": "Frage/Anweisung", "input": "optionaler Kontext", "output": "gewünschte Antwort"}
```

## So sammelst du ein Beispiel (ein Befehl)

```bash
cd self-hosted-ai/finetune
python add_example.py -i "Wie stoppe ich alle Docker-Container?" -o "docker stop \$(docker ps -q)"
```

## Woher gute Beispiele kommen

1. **Gute KI-Antworten behalten** — wenn die lokale KI etwas gut beantwortet,
   als Beispiel speichern.
2. **Schlechte Antworten korrigieren** — die *korrigierte* Fassung als Beispiel
   speichern. Genau daraus lernt das Modell deinen Anspruch.
3. **Wiederkehrende Aufgaben** — Dinge, die du oft brauchst (Scraping-Muster,
   Docker-Befehle, Code-Snippets in deinem Stil).
4. **Dein Fachwissen** — Fakten über deine Projekte, deine Konventionen, deinen Ton.

## Qualitätsregeln

- Jede `output` soll **exakt so** aussehen, wie das Modell später antworten soll
  (Ton, Format, Genauigkeit).
- Keine Widersprüche zwischen Beispielen.
- Lieber weglassen als unsicher — falsche Beispiele bringen dem Modell Falsches bei.

## Die Pipeline (Subagenten)

```
 writer  ──▶  reviewer  ──▶  learner  ──▶  deployer
 erzeugt      prüft &        Feintuning     neues Modell
 Kandidaten   korrigiert,    vorbereiten    in Ollama laden
              gute -> Datensatz
```

- **writer** erzeugt neue Beispiele (z. B. aus einem Thema/Dokument) nach `dataset/candidates.jsonl`.
- **reviewer** prüft Kandidaten, korrigiert/verwirft und übernimmt gute in `dataset/collected.jsonl`.
- **learner** validiert den Datensatz und bereitet den QLoRA-Trainingslauf vor.
- **deployer** lädt das fertige Modell in Ollama und startet den Stack neu.

Definitionen der Subagenten: `.claude/agents/`.
