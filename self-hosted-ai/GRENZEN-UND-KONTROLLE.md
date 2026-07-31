# Grenzen & Kontrolle – was geht, was nicht, und wer bestimmt

Ehrliche Referenz zu zwei Fragen:
1. Wo liegen die Grenzen?
2. Kann ich bestimmen, was die KI darf und was nicht?

---

## 1. Grenzen – zwei Arten

### 🧱 Harte Wände (Hardware/Physik – nicht mit Geduld lösbar)

| Grenze | Bedeutung |
| --- | --- |
| VRAM = 16 GB | Deckelt die Modellgröße: 14B bequem, 32B langsam, 70B+ unpraktisch |
| Roh-Intelligenz | Offenes 14–32B erreicht bei den schwersten Denkaufgaben nicht die größten Cloud-Modelle. Feintuning passt an, hebt nicht die Grunddecke |
| Von Null trainieren | Auf einer GPU unmöglich (Jahrhunderte) |
| Geschwindigkeit | Eine GPU ist langsamer als ein Rechenzentrum |
| Kontextlänge | Sehr lange Eingaben kosten viel VRAM |

### 🌊 Weiche Grenzen (kaum eine Grenze)

| Bereich | Grenze? |
| --- | --- |
| Fähigkeiten über Werkzeuge | Praktisch unbegrenzt – alles Programmierbare ist möglich |
| Wissen (RAG/füttern) | Praktisch unbegrenzt |
| Verhalten & Regeln | Komplett deins |
| Autonomie | So weit, wie du willst |
| Weitere Agenten | Beliebig ausbaubar |

**Kurzfassung:** Beim *rohen Denken* gibt es eine Hardware-Decke. Bei dem, was das
*System tun und wissen* kann, ist **kaum eine Grenze** gesetzt.

---

## 2. Kontrolle – du bestimmst, was die KI darf

Weil du selbst hostest, redet keine fremde Firma mit. Steuerung auf drei Ebenen:

| Ebene | Was du festlegst | Stärke |
| --- | --- | --- |
| 1. System-Prompt | Regeln, Ton, was sie tut/ablehnt | weich (überredbar) |
| 2. Werkzeuge | Was sie überhaupt kann – kein Werkzeug = unmöglich | **hart** |
| 3. Code-Grenzen | Whitelist/Blacklist, Bestätigung, Sandbox, Dateizugriff | **hart** |

**Wichtigster Grundsatz:** Echte Kontrolle liegt in Ebene 2 + 3, nicht im Prompt.
Einen Prompt kann ein Modell umschiffen; ein fehlendes Werkzeug nicht.

Beispiele harter Regeln (im Code, nicht als Bitte):
- Dateiwerkzeuge nur innerhalb `WORKSPACE_DIR` (siehe `agent/tools.py` -> `_safe_path`).
- Code-Ausführung mit Zeitlimit, später in Docker-Sandbox.
- Bestätigung erzwingen vor löschenden/destruktiven Aktionen.
- Bestimmte Werkzeuge einfach weglassen = Fähigkeit existiert nicht.

Beide Richtungen sind deine Wahl:
- **Lockern:** fremde Vorbehalte entfernen, die ein Cloud-Modell hätte.
- **Beschränken:** deine eigenen harten Regeln setzen.

---

## 3. Ehrlicher Hinweis zur Verantwortung

„Keine fremden Filter" heißt nicht „rechtsfrei":
- Es gilt weiter geltendes Recht (Urheberrecht, Datenschutz/DSGVO, Persönlichkeitsrechte).
- Ohne fremde Leitplanken kann das Modell auch **falsche** oder **schädliche**
  Ausgaben erzeugen – die Verantwortung dafür liegt dann bei dir.
- Ein Minimum eigener Regeln ist deshalb klug – nicht als Zensur, sondern gegen
  Fehler und Datenverlust. Du definierst sie, nicht ein Konzern.

---

## 4. Wo du die Regeln einstellst

| Was | Datei |
| --- | --- |
| Verhalten / Ton / Regeln (Prompt) | `agent/config.py` -> `SYSTEM_PROMPT` |
| Verfügbare Werkzeuge | `agent/tools.py` -> `TOOLS_SPEC` / `DISPATCH` |
| Harte Grenzen (Pfad, Zeitlimit) | `agent/config.py` + `agent/tools.py` |
| Regeln des Chat-Modells | Open WebUI -> Settings -> System Prompt |
