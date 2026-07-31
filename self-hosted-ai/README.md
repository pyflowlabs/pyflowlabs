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

Der Installer zeigt ein **Menü**: wähle **ein oder mehrere** Modelle (Zahlen mit
Leerzeichen, z. B. `1 3`) oder `C` für ein eigenes Modell. Danach:

- **NERO QUANTUM (Chat):** http://localhost:3000
- **Websuche:** http://localhost:8888

Beim ersten Öffnen ein lokales Konto anlegen (bleibt auf deiner Maschine).

Stoppen: `docker compose down` · Wieder starten: `./install.sh` oder `docker compose up -d`

---

## Mehrere Modelle & Umschalten

- Im Installer mehrere Modelle auswählen → alle werden geladen.
- **In der Oberfläche** wählst du oben per **Dropdown** jederzeit zwischen allen
  installierten Modellen (pro Chat frei umschaltbar).
- **Mehrere Modelle gleichzeitig in EINEM Chat:** ja — im Modell-Dropdown einfach
  **mehrere** anhaken (z. B. Dolphin + Qwen-Coder). Dann antwortet **jedes Modell**
  auf dieselbe Frage (nebeneinander zum Vergleich), und du kannst die Antworten
  per „Merge/Zusammenführen" zu einer kombinieren. Hinweis: Sie laufen
  nacheinander durch dieselbe GPU (nicht parallel) — bei großen Modellen dauert es
  also entsprechend länger.
- Später ein Modell nachrüsten:
  ```bash
  docker exec -it ollama ollama pull <name>
  ```
- **Eigene / uncensored Modelle:** über den Menüpunkt `C` oder direkt per Pull.
  Zwei Quellen:
  - **Ollama-Bibliothek:** einfach der Name, z. B. `dolphin-mixtral`.
  - **HuggingFace-GGUF:** `hf.co/USER/REPO:QUANT` — so ziehst du beliebige
    Community-Fine-tunes (z. B. Dolphin-Varianten, Sao10K-, TheDrummer-,
    BeaverAI-Modelle). Deine Maschine, deine Wahl.
- Welches Modell der **Agent** nutzt: `agent/config.py` → `MODEL`.

---

## Multimodal (optional): Bild & Sprache

Zusätzlicher Stack für Bildgenerierung; Sprachein-/ausgabe ist bereits eingebaut.

```bash
docker compose -f docker-compose.yml -f docker-compose.multimodal.yml up -d
```

| Modalität | Womit | Status auf RTX 4080 Super (16 GB) |
| --- | --- | --- |
| **Bild** | ComfyUI + SDXL / FLUX | SDXL komfortabel · FLUX nur quantisiert (fp8/GGUF) |
| **Video** | ComfyUI + Wan 2.2 / HunyuanVideo | Wan 2.2 (klein) gut · Hunyuan quantisiert, kurze Clips |
| **Sprachausgabe (TTS)** | in der Oberfläche eingebaut | Admin → Audio (leicht) |
| **Speech-to-Text** | Whisper, eingebaut | Admin → Audio (leicht) |

Bild **und** Video laufen beide über **ComfyUI** (per Workflow) — ein Dienst.

**Hardware-Realität (bei Einzelnutzung entspannt):** Da du immer nur *eine*
Aufgabe zur Zeit machst (coden **oder** Bild **oder** Video), hat jede die volle
Karte für sich — der VRAM wird nicht geteilt. Tipp: vorher das LLM freigeben
(`docker exec ollama ollama stop <modell>`), dann steht der ganze Speicher für
Bild/Video bereit. Für Video bleibt die Karte der Engpass: kurze Clips, moderate
Auflösung, Geduld — aber es geht.

Bild-Anbindung: NERO QUANTUM → Admin → Einstellungen → Bilder → Engine „ComfyUI",
URL `http://comfyui:8188`.

### Grenze bei Bild/Video
Allgemeine, legale Kreativnutzung: deine Sache. **Nicht** dabei: sexuelle Inhalte
von **echten Personen** oder **Minderjährigen** (Deepfakes/NCII/CSAM) — das ist
hart illegal und wird hier nicht eingerichtet.

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
