# Kann die KI wirklich lernen? (Feintuning)

Kurz: **Ja.** Das Modell ist nicht für immer fix — du kannst es dauerhaft
weitertrainieren, immer wieder. Nur nicht in Echtzeit mitten im Gespräch,
sondern in Trainingsläufen.

---

## Die zwei Bedeutungen von „lernen"

**A) Sofort im Gespräch mitlernen (wie ein Mensch)**
→ Technisch heute nicht möglich — bei keinem lokalen und keinem Cloud-Modell.

**B) Das Modell dauerhaft trainieren, wiederholbar**
→ Möglich, auf deiner RTX 4080 Super. Nennt sich **Feintuning (LoRA/QLoRA)**.
   Die Gewichte werden angepasst → das Modell kann/weiß danach dauerhaft Neues.

Ein System, das „mit der Zeit lernt", = **B in Wiederholung**: Beispiele sammeln,
regelmäßig kurz nachtrainieren (z. B. wöchentlich, über Nacht).

---

## Drei Ebenen kombinieren (empfohlen)

| Ebene | Wofür | Modell verändert? | Geschwindigkeit |
| --- | --- | --- | --- |
| Gedächtnis | Fakten über dich merken | nein | sofort |
| RAG (füttern) | Wissen/Dokumente parat | nein | sofort |
| Feintuning (LoRA) | Fähigkeiten, Stil, Verhalten | **ja, dauerhaft** | Stunden, wiederholbar |

**Faustregel:** *Wissen* → RAG. *Können & Charakter* → Feintuning.

---

## Was du für Feintuning brauchst

1. **Beispiele** im Format „Anweisung → gewünschte Antwort" — deine Fälle, dein
   Ton, dein Fachwissen. Schon ein paar hundert gute Beispiele wirken viel.
   Vorlage: `finetune/beispieldaten.jsonl`.
2. **Werkzeug:** [Unsloth](https://github.com/unslothai/unsloth) (sparsam, passt in 16 GB),
   Alternativen: Axolotl, Hugging Face PEFT/TRL.
3. **Zeit:** QLoRA auf 7B–14B läuft auf der 4080 Super meist in wenigen Stunden.
   32B geht auch, ist aber langsamer.

---

## Ablauf (Prinzip)

```
   KI nutzen  ──▶  gute/korrigierte Antworten als Beispiele sammeln
        ▲                              │
        │                              ▼
  besseres Modell  ◀──  QLoRA-Feintuning (z. B. über Nacht)
        │
        ▼
  neues Modell in Ollama laden und weiterverwenden
```

---

## Zwei ehrliche Warnungen

1. **Nicht in Echtzeit** — Lernen ist ein Trainingslauf, kein Sofort-Effekt.
2. **„Vergessen" vermeiden** — nur auf enge Daten trainieren lässt das Modell
   Allgemeinwissen verlieren. Gegenmittel: LoRA (kleine Zusatzmodule statt alles
   umzuschreiben) + etwas allgemeine Daten beimischen. Beherrschbar.

---

## Datenqualität schlägt Datenmenge

- Lieber 300 saubere, korrekte Beispiele als 5.000 schlechte.
- Jedes Beispiel sollte genau so aussehen, wie das Modell später antworten soll
  (Ton, Format, Genauigkeit).
- Am einfachsten sammelst du Beispiele im Alltag: gute Antworten der KI behalten,
  schlechte korrigieren und die korrigierte Fassung als Beispiel speichern.

Wann es so weit ist (Phase 5), richte ich dir das Trainings-Skript passend zu
deiner Hardware ein.
