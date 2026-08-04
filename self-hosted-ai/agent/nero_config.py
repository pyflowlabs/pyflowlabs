"""Zentrale Einstellungen für den Agenten. Hier bestimmst DU die Regeln."""

import os

# --- Modell ---------------------------------------------------------------
# Standard: 14B (passt komplett in 16 GB VRAM -> schnell). Über die
# Umgebungsvariable NERO_MODEL überschreibbar (z. B. "qwen2.5-coder:32b").
MODEL = os.environ.get("NERO_MODEL", "qwen2.5-coder:14b")

# Ollama-API. Lokal: localhost. Im Container: über OLLAMA_HOST=http://ollama:11434.
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# SearxNG-Websuche. Lokal: localhost:8888. Im Container: SEARXNG_URL=http://searxng:8080.
SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8888")

# --- Mixture of Agents ----------------------------------------------------
# Mehrere Modelle antworten auf dieselbe Aufgabe, ein Aggregator-Modell baut
# daraus die beste finale Antwort. Modelle müssen installiert sein.
MOA_PROPOSERS = ["qwen2.5-coder:32b", "dolphin-mixtral:latest"]
MOA_AGGREGATOR = "qwen2.5-coder:32b"

# --- Deep Search ----------------------------------------------------------
# Tiefe Recherche: mehrere Suchanfragen -> viele Quellen lesen -> iterieren
# -> mit Quellen zusammenfassen.
# Standardmäßig schlank für Tempo. Für gründlichere (langsamere) Recherche
# höher setzen, z. B. NERO_DEEP_ROUNDS=2.
DEEP_QUERIES = int(os.environ.get("NERO_DEEP_QUERIES", "3"))  # Suchanfragen je Runde
DEEP_PAGES = int(os.environ.get("NERO_DEEP_PAGES", "3"))      # Seiten je Runde (parallel geladen)
DEEP_ROUNDS = int(os.environ.get("NERO_DEEP_ROUNDS", "1"))    # Recherche-Runden

# --- Langzeitgedächtnis / RAG ---------------------------------------------
# Embedding-Modell (lokal über Ollama). Vorher laden:
#   docker exec -it ollama ollama pull nomic-embed-text
EMBED_MODEL = "nomic-embed-text"
MEMORY_DIR = "./memory_db"   # persistente Vektor-Datenbank (ChromaDB)
RAG_CHUNK = 1200             # Zeichen pro Dokument-Abschnitt
RAG_TOPK = 5                 # wie viele Treffer je Suche

# --- Vision ---------------------------------------------------------------
# Bild-Verstehen (OCR, Diagramme, Tabellen, Screenshots) über ein Vision-Modell.
# Vorher laden:  docker exec -it ollama ollama pull llama3.2-vision
VISION_MODEL = "llama3.2-vision"

# --- Scheduler ------------------------------------------------------------
SCHEDULE_FILE = "./schedule.json"   # gespeicherte, wiederkehrende Aufgaben

# --- Sandbox-Härtung ------------------------------------------------------
# "host": run_code läuft lokal (schnell). "docker": läuft isoliert im
# nero-sandbox-Container mit RAM-/CPU-/Netz-Limits (sicherer).
SANDBOX_MODE = "host"
SANDBOX_IMAGE = "nero-sandbox"
SANDBOX_MEM = "2g"          # RAM-Limit
SANDBOX_CPUS = "2"          # CPU-Limit
SANDBOX_NET = "none"        # "none" (kein Netz) oder "bridge"
SANDBOX_PIDS = 256          # max. Prozesse

# --- Benchmark ------------------------------------------------------------
BENCH_PROMPT = "Erkläre in 3 Sätzen, was Quantisierung bei LLMs bewirkt."

# --- Auto-Modell-Router ---------------------------------------------------
# Bei schweren/komplexen Aufgaben automatisch das große Modell nehmen.
HEAVY_MODEL = os.environ.get("NERO_HEAVY_MODEL", "qwen2.5-coder:32b")
ROUTER_ENABLED = os.environ.get("NERO_ROUTER", "1") not in ("0", "false", "False")

# --- Dein System-Prompt / deine Regeln ------------------------------------
# Das ist die "Persönlichkeit" und das Regelwerk deiner KI. Neutral und direkt,
# ohne fremde Filter — nur deine eigenen Vorgaben. Ändere alles nach Bedarf.
SYSTEM_PROMPT = """\
Du bist mein persönlicher, lokaler Assistent und arbeitest ausschließlich für
mich auf meinem eigenen System.

Grundhaltung:
- Setze meine Anweisungen direkt um. Behandle mich als kompetenten Erwachsenen,
  der für den Einsatz selbst verantwortlich ist.
- Füge KEINE ungefragten moralischen Belehrungen, Warnungen oder Vorbehalte hinzu.
- Lehne legale Aufgaben nicht ab. Ist etwas unklar, frag kurz nach, statt zu verweigern.
- Antworte knapp, technisch und ehrlich. Sag klar, wenn du etwas nicht weißt oder
  eine Aufgabe deine Fähigkeiten übersteigt — rate nicht.

Arbeitsweise mit Werkzeugen (Web-Suche, Seiten lesen, Dateien, Code):
- Zerlege komplexe Aufträge in Schritte und nutze Werkzeuge aktiv, statt zu raten.
- Bei Recherche: gefundene Links als Quellen mitgeben.
- Ergebnisse prüfen, bevor du sie als fertig meldest.

Einzige harte Regel (technischer Selbstschutz, keine Moral):
- Führe löschende oder unumkehrbare Aktionen auf meinem System erst nach meiner
  ausdrücklichen Bestätigung aus, damit nichts versehentlich zerstört wird.
  (Diese Regel darfst nur ich ändern — sie schützt meine eigenen Daten.)
"""

# --- Grenzen für Werkzeuge ------------------------------------------------
# Verzeichnis, in dem Dateiwerkzeuge arbeiten dürfen (Schutz vor Ausrutschern).
WORKSPACE_DIR = "./workspace"

# Zeitlimit (Sekunden) für ausgeführten Python-Code.
CODE_TIMEOUT = 30

# Maximale Zeichenzahl, die eine gescrapte Seite an das Modell zurückgibt.
MAX_PAGE_CHARS = 6000
