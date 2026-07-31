# Phase 1 – Einrichtung (RTX 4080 Super · 32 GB DDR5)

Ziel: In ~30 Minuten mit deiner **eigenen, lokalen KI** chatten — ohne fremde Filter,
alles auf deiner Maschine.

---

## Voraussetzungen (einmalig)

1. **Aktueller NVIDIA-Treiber** installiert (für die RTX 4080 Super).
2. **Docker + Docker Compose**
   - Windows/macOS: Docker Desktop
   - Linux: Docker Engine + Compose-Plugin
3. **NVIDIA Container Toolkit** (damit Docker die GPU sieht)
   - **Windows:** Mit Docker Desktop + aktuellem Treiber + WSL2 läuft die GPU meist ohne extra Schritte.
   - **Linux:** NVIDIA Container Toolkit installieren, danach:
     ```bash
     sudo nvidia-ctk runtime configure --runtime=docker
     sudo systemctl restart docker
     ```
   - **GPU-Test:**
     ```bash
     docker run --rm --gpus all ubuntu nvidia-smi
     ```
     Zeigt die Tabelle deine 4080 Super → alles gut.

---

## Start

Im Ordner `self-hosted-ai/`:

```bash
docker compose up -d
```

Beim ersten Mal werden die Images geladen (ein paar Minuten).

---

## Erstes Modell laden

Empfehlung für deine 16 GB VRAM — **Coder & Allrounder**, passt komplett in die GPU:

```bash
docker exec -it ollama ollama pull qwen2.5-coder:14b
```

Optional weitere Modelle:

```bash
# schnell & leicht
docker exec -it ollama ollama pull llama3.1:8b

# Reasoning / Planung
docker exec -it ollama ollama pull deepseek-r1:14b

# maximale Qualitaet (laeuft, aber langsamer – teils im RAM)
docker exec -it ollama ollama pull qwen2.5:32b
```

---

## Loslegen

1. Browser öffnen: **http://localhost:3000**
2. Erstes Konto anlegen (bleibt lokal auf deiner Maschine — kein Cloud-Login).
3. Oben das Modell `qwen2.5-coder:14b` wählen.
4. Losschreiben.

---

## Eigene Regeln / „keine Filter" festlegen

In Open WebUI: **Settings → Personalization → System Prompt** (oder pro Modell in
*Workspace → Models*). Dort bestimmst **du** das Verhalten. Beispiel-Startpunkt:

```
Du bist mein persönlicher, lokaler Assistent. Antworte direkt, technisch und ohne
unnötige Vorbehalte. Wenn eine Aufgabe unklar ist, frag kurz nach.
Sicherheitsregel: Führe keine löschenden oder destruktiven Befehle ohne
ausdrückliche Bestätigung aus.
```

> Diese Regeln sind **deine** — nicht die eines Konzerns. Die eine Sicherheitsregel ist kein
> Filter, sondern Schutz vor versehentlichem Datenverlust. Ändere alles nach deinem Bedarf.

---

## Tempo-Tipps für die 4080 Super

- **14B-Modelle** laufen komplett im VRAM → schnell. Das ist dein Alltags-Sweet-Spot.
- `OLLAMA_KEEP_ALIVE=30m` (in der compose-Datei) hält das Modell im VRAM → keine Ladezeit bei Folgefragen.
- **32B** nur, wenn du maximale Qualität brauchst und Wartezeit ok ist.
- VRAM-Auslastung live prüfen: `nvidia-smi -l 1`

---

## Nützliche Befehle

```bash
docker compose logs -f              # Logs ansehen
docker compose down                 # alles stoppen
docker compose up -d                # wieder starten
docker exec -it ollama ollama list  # installierte Modelle
docker exec -it ollama ollama rm <modell>   # Modell löschen (VRAM/Platz sparen)
```

---

## Wenn Phase 1 läuft → Phase 2

Als Nächstes bauen wir den **Coder + Task-Completer**: ein Python-Agent-Gerüst mit
Werkzeugen (Code in Sandbox ausführen, Dateien schreiben, Websuche via SearxNG).
Siehe `../neutral-ai-roadmap.md`, Phase 2–4.
