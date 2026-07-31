# Was kann die KI? Lernt sie? Kann ich sie füttern?

Kurzer Merkzettel — die drei häufigsten Fragen ehrlich beantwortet.

---

## 1. Was kann sie?

| Fähigkeit | Ab Phase | Bedeutung |
| --- | --- | --- |
| Chatten & Texte | 1 | Antworten, schreiben, erklären, übersetzen — lokal |
| Programmieren | 1–2 | Code schreiben, erklären, Fehler finden |
| Code ausführen | 2 | Code in Sandbox laufen lassen, Fehler lesen, verbessern |
| Dateien lesen/schreiben | 2 | Zugriff auf deine Projekte (Grenzen bestimmst du) |
| Websuche | 3 | Aktuelle Infos mit Quellen, neutral (SearxNG) |
| Dein Wissen nutzen | 3 | Antwortet auf Basis deiner Dokumente (RAG) |
| Aufgaben abschließen | 4 | Auftrag → Schritte → Werkzeuge → Ergebnis |
| Deine Projekte steuern | 4 | Bots / Scraper / APIs anbinden |

---

## 2. Lernt sie?

Das **Modell selbst** lernt beim Chatten **nicht** automatisch dazu — sein „Gehirn" ist nach dem
Training fix. Aber es gibt **drei echte Wege**, wie sie sich anpasst:

### Weg 1 — Gedächtnis (einfach, sofort)
- Innerhalb eines Gesprächs merkt sie sich alles.
- Open WebUI **Memory**: dauerhafte Fakten über dich, über Gespräche hinweg.
- Alle Chats werden gespeichert und sind durchsuchbar.

### Weg 2 — Füttern mit Wissen (RAG) ← die Antwort auf „kann ich sie füttern?"
- **Ja.** Du gibst ihr PDFs, Notizen, Code, Handbücher, ganze Ordner.
- Sie legt das in einer durchsuchbaren Wissens-DB ab und **antwortet auf Basis deiner Inhalte** —
  mit Quellenangabe.
- Das Modell ändert sich nicht, aber es *weiß* plötzlich alles, was du reingegeben hast.
- In Open WebUI: **„Knowledge / Documents"** → Dateien hochladen, fertig.
- Für die meisten Fälle ist **genau das** mit „füttern" gemeint.

### Weg 3 — Feintuning / LoRA (fortgeschritten, optional, Phase 5)
- Hier wird das Modell wirklich *trainiert* — auf deinen Stil, deinen Fachbereich.
- Geht auf der RTX 4080 Super für kleinere Modelle.
- Braucht vorbereitete Beispieldaten + Rechenzeit.

---

## 3. Kurzformel

- Automatisch beim Reden mitlernen → **nein**
- Füttern und dadurch schlauer/spezifischer machen → **ja, jederzeit (RAG)**
- Charakter/Stil dauerhaft umtrainieren → **ja, optional (Feintuning)**

---

## 4. Was du schon vorbereiten kannst (vom Handy aus)

- Überleg dir, **womit** du sie füttern willst: Ordner mit PDFs, Notizen, Code, Doku.
- Überleg dir deine **eigenen Regeln / System-Prompt** (Tonfall, Verhalten, Sicherheitsregeln).
- Am PC dann: Docker + Treiber installieren → `docker compose up -d` → Modell ziehen → loslegen.
  Anleitung: `SETUP.md`.
