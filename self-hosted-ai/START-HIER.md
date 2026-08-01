# 🚀 NERO QUANTUM – Start-Anleitung (alles an einem Ort)

Diese Seite ist dein „wenn ich zu Hause bin, loslegen"-Leitfaden.

---

## 0. Voraussetzungen (einmalig)
- **Docker** installiert (Windows: Docker Desktop) + Docker Compose
- Aktueller **NVIDIA-Treiber** für die RTX 4080 Super
- Dieses Repo auf dem PC (klonen oder herunterladen)

GPU-Test (optional):
```bash
docker run --rm --gpus all ubuntu nvidia-smi
```

---

## 1. Starten – ein Skript
Im Ordner `self-hosted-ai/`:
- **Windows:** `install.ps1` (Rechtsklick → „Mit PowerShell ausführen")
- **Linux/macOS:** `chmod +x install.sh && ./install.sh`

Im **Menü** wählst du ein oder mehrere Modelle (z. B. `1 3`) oder `C` für ein
eigenes. Fertig → alles läuft.

---

## 2. Nutzen – Web UND App (du entscheidest)

**Am PC (Web):** http://localhost:3000

**Andere Geräte im selben WLAN (Handy, Laptop):**
`http://<PC-IP>:3000`  (PC-IP z. B. `192.168.1.50`; Firewall muss Port 3000 erlauben)

**Als App installieren (PWA):**
Im Browser (Chrome/Edge) das Symbol „App installieren" bzw. „Zum Startbildschirm
hinzufügen" → NERO QUANTUM läuft dann wie eine eigene Desktop-/Handy-App.
Beides parallel möglich – du wählst pro Situation Web oder App.

> Zugriff von unterwegs (außerhalb des WLAN) braucht zusätzlich einen sicheren
> Zugang (HTTPS/Reverse-Proxy oder VPN). Sag Bescheid, dann richte ich das ein.

---

## 3. Modelle wählen & umschalten
- **Umschalten:** oben im Chat per **Dropdown** zwischen allen installierten Modellen.
- **Mehrere in EINEM Chat:** mehrere Modelle anhaken → jedes antwortet (Vergleich),
  optional „Merge" zu einer Antwort.
- **Zusammenarbeiten statt nur parallel (Mixture of Agents):**
  ```bash
  cd agent && pip install -r requirements.txt && python moa.py
  ```
  Proposer/Aggregator festlegen in `agent/config.py`.
- **Deep Search (tiefe Recherche mit Quellen):**
  ```bash
  cd agent && python deepsearch.py
  ```
  Bildet mehrere Suchanfragen, liest viele Quellen, iteriert, fasst mit Links
  zusammen. Der Agent (`agent.py`) kann `deep_search` auch selbst aufrufen.
  Tiefe: `config.py` → `DEEP_QUERIES` / `DEEP_PAGES` / `DEEP_ROUNDS`.

---

## 4. Uncensored / eigene Modelle hinzufügen

**Weg A – aus der Ollama-Bibliothek** (einfachster Fall):
```bash
docker exec -it ollama ollama pull dolphin-mixtral
docker exec -it ollama ollama pull dolphin3
```
Danach erscheinen sie automatisch im Dropdown.

**Weg B – beliebiges HuggingFace-GGUF** (für Dolphin-Varianten, Sao10K wie Stheno/
Euryale, TheDrummer wie Moistral/Gemmasutra, BeaverAI usw.):
```bash
docker exec -it ollama ollama pull hf.co/<USER>/<REPO>:<QUANT>
# Beispielschema:  hf.co/TheDrummer/<Modell-GGUF>:Q4_K_M
```
Den genauen `USER/REPO`-Namen und die `QUANT`-Variante (z. B. `Q4_K_M`) findest du
auf der jeweiligen HuggingFace-Modellseite.

**Als Standard setzen:**
- Für den Installer: `NERO_MODEL=<name> ./install.sh`
- Für den Agenten: `agent/config.py` → `MODEL = "<name>"`

> Modellwahl ist deine Sache – deine Maschine, deine Entscheidung. „Uncensored"
> lässt nur die modell­eigenen Vorbehalte weg, macht das Modell nicht klüger.
> Manche dieser Fine-tunes sind beim reinen Coden schwächer als Qwen-Coder – ruhig
> mehrere installieren und je Aufgabe wechseln.

---

## 5. Bild & Video (multimodal)
Zusätzlichen Stack starten:
```bash
docker compose -f docker-compose.yml -f docker-compose.multimodal.yml up -d
```
- **Bild/Video:** ComfyUI unter http://localhost:8188 → Details & Modelle in `comfyui/README.md`
- **Bilder aus dem Chat:** NERO QUANTUM → Admin → Bilder → Engine „ComfyUI", URL `http://comfyui:8188`
- **Sprachausgabe/Whisper:** in NERO QUANTUM → Admin → Audio
- Da du immer nur **eine** Aufgabe machst, hat Bild/Video die volle GPU. Tipp:
  vorher `docker exec ollama ollama stop <modell>`.

---

## 6. Langzeitgedächtnis & eigene Dokumente (RAG)
```bash
docker exec -it ollama ollama pull nomic-embed-text     # Embedding-Modell
cd agent && pip install -r requirements-memory.txt       # chromadb + pypdf
```
Dann kann der Agent (`agent.py`):
- `remember` / `recall` – merkt sich Vorlieben, Projektstände, vermiedene Fehler
- `kb_ingest "D:\\Dokumente"` – liest ganze Ordner (txt/md/pdf) ein
- `kb_search "Wo liegt die Amazon-Rechnung?"` – antwortet auf Basis deiner Dateien

## 7. Plugins (neue Fähigkeiten)
Neue `.py`-Datei in `agent/plugins/` mit `PLUGIN_TOOLS` ablegen → beim Start
automatisch erkannt. Vorlage: `agent/plugins/archive_tools.py` (unzip, list_dir).

## 8. Lernen (Feintuning)
- Beispiele sammeln: `finetune/add_example.py`
- Trainieren: `finetune/START-TRAINING.md`
- Pipeline-Agenten: writer → reviewer → learner → deployer (`.claude/agents/`)

## Was noch aussteht → `ROADMAP-V1.md`
Vision, Selbstbewertung, Scheduler, Tests, Monitoring, Benchmark, Wake-Word …
mit empfohlener Reihenfolge.

---

## 7. Deine Kontrolle (nichts versteckt)
| Was | Wo |
| --- | --- |
| Verhalten / Regeln | `agent/config.py` → `SYSTEM_PROMPT` |
| Werkzeuge | `agent/tools.py` |
| Modell (Agent) | `agent/config.py` → `MODEL` |
| Mixture of Agents | `agent/config.py` → `MOA_*` |
| Chat-Regeln (UI) | NERO QUANTUM → Settings → System Prompt |

Stoppen: `docker compose down` · Neustart: `./install.sh` oder `docker compose up -d`

---

## Fehler & Logs (wo du im Problemfall nachschaust)
Alles schreibt klare Meldungen **und** persistente Log-Dateien:

| Quelle | Wo | Was |
| --- | --- | --- |
| **Installer** | `self-hosted-ai/install.log` | kompletter Setup-Lauf; bei Abbruch Zeile + Ursache |
| **Agent / MoA** | `self-hosted-ai/logs/nero-agent.log` | Werkzeug- und Laufzeitfehler mit Traceback |
| **Dienste** (Docker) | `docker compose logs -f` | Ollama, Oberfläche, SearxNG, ComfyUI |
| **einzelner Dienst** | `docker compose logs -f <name>` | z. B. `nero-quantum`, `comfyui`, `ollama` |

Wenn etwas hakt: die passende Log-Datei (oder ihre letzten Zeilen) schicken —
darin steht die eindeutige Fehlerursache.

## Nützliche Befehle
```bash
docker exec -it ollama ollama list          # installierte Modelle
docker exec -it ollama ollama pull <name>   # Modell hinzufügen
docker exec -it ollama ollama rm <name>     # Modell entfernen
docker exec ollama ollama stop <name>       # Modell aus dem VRAM werfen
docker compose logs -f                       # Logs aller Dienste
docker compose logs -f comfyui               # Log eines Dienstes
```
