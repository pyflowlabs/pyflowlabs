# Agent – der Task-Completer (Phase 2 + 3)

Ein Python-Agent, der das lokale Modell mit **echten Werkzeugen** verbindet:
Websuche, Seiten scrapen, Dateien schreiben/lesen, Python ausführen.
Damit *tut* die KI Dinge, statt nur zu antworten.

## Werkzeuge

| Werkzeug | Was es kann |
| --- | --- |
| `web_search` | Einzelne Websuche über SearxNG, liefert Titel + URLs + Kurztext |
| `deep_search` | **Tiefe Recherche:** mehrere Suchanfragen, liest viele Quellen, iteriert, fasst mit Quellen zusammen |
| `fetch_page` | Lädt eine URL, gibt sauberen Text **und alle Links** zurück (Scraping) |
| `read_file` / `write_file` | Dateien im `workspace/`-Ordner lesen/schreiben |
| `run_python` | Python-Code ausführen (z. B. eigene Scraper), mit Zeitlimit |

Deep Search auch einzeln nutzbar: `python deepsearch.py` (Tiefe in `config.py` →
`DEEP_QUERIES` / `DEEP_PAGES` / `DEEP_ROUNDS`).

Neue Fähigkeiten hinzufügen = eine Funktion in `tools.py` schreiben + Schema in
`TOOLS_SPEC` eintragen. Sonst nichts.

## Voraussetzung

Der Docker-Stack läuft (`docker compose up -d` im übergeordneten Ordner) und das
Hauptmodell ist geladen:

```bash
docker exec -it ollama ollama pull qwen2.5-coder:32b
```

## Start

```bash
cd self-hosted-ai/agent
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

Dann Aufgaben eingeben, z. B.:

- „Suche die 3 aktuellsten Artikel über X und fasse sie mit Links zusammen."
- „Scrape die Überschriften von <URL> und speichere sie als schlagzeilen.txt."
- „Schreib ein Python-Skript, das eine CSV nach Spalte Y filtert, und teste es."

## Einstellungen

Alles in `config.py`:
- **`MODEL`** — Hauptmodell (Standard `qwen2.5-coder:32b`; für Tempo `...:14b`)
- **`SYSTEM_PROMPT`** — deine Regeln / die „Persönlichkeit" (neutral, ohne fremde Filter)
- **`WORKSPACE_DIR`** — wo Dateiwerkzeuge arbeiten dürfen
- **`CODE_TIMEOUT`**, **`MAX_PAGE_CHARS`** — Grenzen

## Sicherheitshinweis

`run_python` läuft aktuell als lokaler Subprozess mit Zeitlimit. Für echte
Isolation (empfohlen, sobald der Agent autonomer wird) verlagern wir die
Ausführung in Phase 5 in einen Docker-Container.
