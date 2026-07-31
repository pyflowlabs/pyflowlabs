# Erster Lernlauf – so fängst du an

Ehrliche Einordnung vorweg:

- **Modell von Null bauen (wie Claude entstand):** braucht tausende GPUs. Auf
  einer GPU nicht mit Zeit lösbar (wären Jahrhunderte). Machen wir **nicht**.
- **Ein fertiges Modell weitertrainieren (Feintuning):** läuft auf deiner
  RTX 4080 Super in Minuten bis Stunden, ist wiederholbar. **Das ist echtes
  Lernen – und genau hier fangen wir an.**

---

## Ablauf

### 1. Beispiele sammeln (je mehr, desto besser)
Schon vorhanden: `dataset/seed.jsonl`. Mehr sammeln:
```bash
python add_example.py -i "Frage/Anweisung" -o "Gewünschte Antwort"
```
Richtwert für spürbare Wirkung: grob **200+ gute** Beispiele. Der Lauf
funktioniert aber auch mit wenigen (dann v. a. als Test der Schleife).

### 2. Trainingsumgebung einrichten (einmalig, am PC mit GPU)
```bash
cd self-hosted-ai/finetune
python -m venv .venv-train && source .venv-train/bin/activate   # Win: .venv-train\Scripts\activate
pip install -r requirements-train.txt
```

### 3. Lernlauf starten
```bash
python train.py
```
- Nutzt automatisch `seed.jsonl` + `collected.jsonl`.
- Erster Lauf mit einem 7B-Modell (passt sicher in 16 GB, schnell).
- GPU beobachten: `nvidia-smi -l 1`.
- Ergebnis: LoRA-Adapter in `outputs/lora_model/`.

### 4. Neues Modell in Betrieb nehmen
Macht der **deployer**-Subagent: erzeugt das Ollama-Modelfile, registriert das
Modell (`ollama create`), testet es und stellt um – ohne das alte Modell zu
löschen (Rückweg bleibt).

---

## Erwartung – ehrlich

- Nach dem ersten Lauf **klingt** das Modell mehr nach dir und kennt deinen
  Stack/Stil besser. Es wird dadurch **nicht** schlagartig „schlauer als Claude".
- Der große Hebel ist **Wiederholung**: sammeln → trainieren → einsetzen, immer
  wieder. So wächst es mit dir.
- Für reines Faktenwissen ist **RAG (füttern)** oft besser als Training.
  Faustregel bleibt: *Wissen → RAG, Können & Stil → Feintuning.*

---

## Skalieren, wenn der erste Lauf sitzt

- Basismodell in `train.py` auf **14B** hochstufen
  (`unsloth/Qwen2.5-Coder-14B-Instruct-bnb-4bit`).
- `EXPORT_GGUF = True` setzen, damit direkt ein Ollama-taugliches Modell entsteht.
- Gegen „Vergessen": ein paar allgemeine Beispiele beimischen (macht der `learner`).
