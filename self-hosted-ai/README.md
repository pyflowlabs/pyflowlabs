# NERO QUANTUM

Deine eigene, lokale KI — selbst gehostet, mit Claude-artiger Oberfläche, unter
deiner vollen Kontrolle. Läuft auf deinem Rechner (Profil: RTX 4080 Super).

---

## Start in einem Schritt

Voraussetzung: **Docker** installiert (Windows: Docker Desktop) und aktueller
**NVIDIA-Treiber**.

**Windows:**
```powershell
./install.ps1
```
**Linux / macOS:**
```bash
chmod +x install.sh && ./install.sh
```

Das Skript startet alle Dienste und lädt das Modell. Danach:

- **NERO QUANTUM (Chat):** http://localhost:3000
- **Websuche:** http://localhost:8888

Beim ersten Öffnen ein lokales Konto anlegen (bleibt auf deiner Maschine).

Stoppen: `docker compose down` · Wieder starten: `./install.sh` oder `docker compose up -d`

---

## Was drin ist

| Baustein | Rolle |
| --- | --- |
| **Oberfläche** (NERO QUANTUM) | Chat-UI im Browser, Claude-artig |
| **Modell-Kern** (Ollama + Qwen2.5-Coder 32B) | das „Gehirn", Fähigkeit vor Tempo |
| **Websuche** (SearxNG) | neutrale Deep-Web-Suche, keine Tracker |
| **Agent** (`agent/`) | Task-Completer: Suche, Scraping, Dateien, Code ausführen |
| **Feintuning** (`finetune/`) | die KI dauerhaft weitertrainieren (lernen) |

Standardmodell: `qwen2.5-coder:32b`. Anderes Modell beim Start wählbar, z. B.:
```bash
NERO_MODEL=qwen2.5-coder:14b ./install.sh
```

---

## Deine Kontrolle — nichts ist versteckt

Alles liegt offen in Dateien, die dir gehören:

| Was du bestimmst | Wo |
| --- | --- |
| Verhalten / Ton / Regeln | `agent/config.py` -> `SYSTEM_PROMPT` |
| Verfügbare Werkzeuge | `agent/tools.py` |
| Modell | `agent/config.py` -> `MODEL` bzw. `NERO_MODEL` |
| Regeln der Chat-Oberfläche | in NERO QUANTUM: Settings -> System Prompt |

Es sind **keine versteckten Grenzen** eingebaut. Die einzige mitgelieferte Regel
ist ein sichtbarer Selbstschutz (Bestätigung vor löschenden Aktionen auf deinem
System) in `agent/config.py` — den änderst nur du.

Hinweis: Das offene Basismodell kann eigene Vorbehalte aus seinem Originaltraining
mitbringen (nicht von diesem Setup). Wer weniger davon will, zieht ein
„uncensored"-Fine-tune eines offenen Modells über `NERO_MODEL`.

---

## Dokumentation

| Datei | Inhalt |
| --- | --- |
| `SETUP.md` | Ausführliche Einrichtung, GPU-Test, Modelle, Tempo-Tipps |
| `WAS-KANN-DIE-KI.md` | Fähigkeiten, Lernen, Füttern (RAG) |
| `LERNEN-UND-FEINTUNING.md` | Wie die KI dauerhaft dazulernt |
| `GRENZEN-UND-KONTROLLE.md` | Grenzen (Hardware) & wie du alles steuerst |
| `agent/README.md` | Der Agent und seine Werkzeuge |
| `finetune/START-TRAINING.md` | Erster echter Lernlauf |
