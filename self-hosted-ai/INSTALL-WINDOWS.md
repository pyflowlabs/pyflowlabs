# NERO QUANTUM – Installation unter Windows (RTX 4080 Super)

Vorhanden: NVIDIA-Treiber, Git, Python. **Fehlt nur:** Docker Desktop.
Reihenfolge einfach von oben nach unten abarbeiten.

---

## Schritt 1 – WSL2 aktivieren (Docker braucht das)
PowerShell **als Administrator** öffnen:
```powershell
wsl --install
```
Danach **PC neu starten**. (Wenn WSL schon da ist, überspringen.)

## Schritt 2 – Docker Desktop installieren
1. Herunterladen: https://www.docker.com/products/docker-desktop/
2. Installieren, bei der Installation **„Use WSL 2 based engine"** aktiviert lassen.
3. Docker Desktop **starten** und einmal laufen lassen (Wal-Symbol unten rechts).

## Schritt 3 – Prüfen, dass Docker + GPU laufen
Normale PowerShell:
```powershell
docker version
docker run --rm --gpus all ubuntu nvidia-smi
```
Zeigt der zweite Befehl deine **RTX 4080 Super** → alles bereit.
(Auf Windows/WSL2 ist kein extra „NVIDIA Container Toolkit" nötig – Treiber +
Docker Desktop genügen.)

## Schritt 4 – Projekt holen
```powershell
git clone https://github.com/pyflowlabs/pyflowlabs.git
cd pyflowlabs
git checkout claude/custom-neutral-ai-network-482n4z
cd self-hosted-ai
```

## Schritt 5 – NERO QUANTUM starten
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```
Im Menü Modelle wählen:
- nur Standard (starkes 32B): **Enter**
- Coder + Dolphin (uncensored): **`1 3`**

Der erste Download des 32B-Modells (~19 GB) dauert je nach Internet etwas.
Alles wird zusätzlich in `install.log` protokolliert.

## Schritt 6 – Loslegen
- Browser: **http://localhost:3000** → lokales Konto anlegen (bleibt auf dem PC)
- Oben das Modell wählen → chatten
- Als App: im Browser „App installieren" (PWA)

---

## Optionale Zusätze (jederzeit nachrüstbar)

**Gedächtnis + eigene Dokumente (RAG):**
```powershell
docker exec -it ollama ollama pull nomic-embed-text
cd agent
pip install -r requirements-memory.txt
```

**Vision (Bilder/Screenshots/OCR):**
```powershell
docker exec -it ollama ollama pull llama3.2-vision
```

**Agent mit Werkzeugen (Deep Search, Code, Team, Rollen):**
```powershell
cd agent
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

**Bild & Video (ComfyUI):**
```powershell
docker compose -f docker-compose.yml -f docker-compose.multimodal.yml up -d
```

---

## Wenn etwas hakt – hier stehen die Ursachen
| Problem | Log |
| --- | --- |
| Setup bricht ab | `install.log` |
| Agent-/Werkzeugfehler | `logs\nero-agent.log` |
| Dienst startet nicht | `docker compose logs -f` bzw. `docker compose logs -f <dienst>` |

Schick mir einfach die betroffene Datei (oder die letzten Zeilen), dann fixen wir's gezielt.

## Stoppen / Neustarten
```powershell
docker compose down        # stoppen
.\install.ps1              # wieder starten (oder: docker compose up -d)
```
