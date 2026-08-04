# NERO QUANTUM – alles im Browser-Chat (Agent-Integration)

Ziel: Du wählst oben im Chat **„NERO QUANTUM"** und redest einfach – die KI nutzt
automatisch Werkzeuge (Code, Suche, Deep Search, Rollen, Gedächtnis). Kein Terminal.

Technisch läuft dahinter unser Agent über einen **Pipelines-Dienst**.

---

## Schritt 1 – Update holen
Im `self-hosted-ai`-Ordner (bzw. `agent`-Unterordner):
```powershell
git checkout -- agent/nero_config.py   # falls du config.py lokal geaendert hattest
git pull
```
> Der Modell-Standard ist jetzt sowieso 14B – die lokale Änderung brauchst du
> nicht mehr. Anderes Modell später per Umgebungsvariable `NERO_MODEL`.

## Schritt 2 – Pipelines-Dienst starten
Im `self-hosted-ai`-Ordner:
```powershell
docker compose -f docker-compose.yml -f docker-compose.pipelines.yml up -d
```
Beim ersten Start installiert der Dienst seine Pakete (ollama, requests,
beautifulsoup4) – das dauert ein bis zwei Minuten. Fortschritt/Fehler:
```powershell
docker compose logs -f pipelines
```

## Schritt 3 – In der Oberfläche verbinden (einmalig)
1. **http://localhost:3000** öffnen → als Admin einloggen
2. **Admin-Einstellungen → Verbindungen** (Connections)
3. Bei **OpenAI API** auf **+** und eintragen:
   - **URL:** `http://pipelines:9099`
   - **Key:** `0p3n-w3bu!`
4. Speichern.

## Schritt 4 – Nutzen
Oben im Chat als Modell **„NERO QUANTUM"** wählen und einfach reden, z. B.:
- „Schreib ein Python-Skript, das die ersten 20 Primzahlen ausgibt, und führ es aus."
- „Such die 3 aktuellsten Meldungen über die RTX 5090 und fass sie mit Links zusammen."
- „Merk dir: Ich programmiere hauptsächlich in Python." (Gedächtnis, wenn RAG aktiv)

Die Werkzeuge laufen automatisch im Hintergrund – du siehst nur die Antwort.

---

## Was wo läuft
```
Browser (localhost:3000)
      │  du wählst "NERO QUANTUM"
      ▼
NERO-QUANTUM-Oberfläche  ──►  pipelines:9099  ──►  Agent (agent.respond)
                                                      │
                                   ┌──────────────────┼───────────────────┐
                                   ▼                  ▼                   ▼
                              Werkzeuge          Deep Search          Rollen/Gedächtnis
                              (Code, Datei)       (SearxNG)            (RAG, wenn aktiv)
```

## Modell/Rolle einstellen
- **Modell:** in `docker-compose.pipelines.yml` → `NERO_MODEL` (Standard `qwen2.5-coder:14b`).
  Nach Änderung: `docker compose -f docker-compose.yml -f docker-compose.pipelines.yml up -d`
- **Werkzeuge/Regeln:** wie gehabt in `agent/nero_config.py`, `agent/tools.py`, `agent/roles.py`.

## Optional freischalten
- **Gedächtnis/RAG:** `docker exec -it ollama ollama pull nomic-embed-text` und im
  Pipelines-Dienst `chromadb` verfügbar machen (in die `requirements`-Zeile der
  Pipeline aufnehmen). Sag mir Bescheid, dann richte ich das ein.
- **Vision:** `docker exec -it ollama ollama pull llama3.2-vision`.

## Wenn etwas hakt
- `docker compose logs -f pipelines` – zeigt Import-/Laufzeitfehler des Agenten
- `logs\nero-agent.log` – Werkzeug-Fehler
- Schick mir die Zeilen, dann fixen wir es gezielt.
