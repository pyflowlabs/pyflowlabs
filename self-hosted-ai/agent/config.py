"""Zentrale Einstellungen für den Agenten. Hier bestimmst DU die Regeln."""

# --- Modell ---------------------------------------------------------------
# Fähigkeit vor Tempo: 32B als Hauptmodell. Für schnelleres Testen auf
# "qwen2.5-coder:14b" umstellen.
MODEL = "qwen2.5-coder:32b"

# Ollama-API (läuft lokal aus dem Docker-Stack)
OLLAMA_HOST = "http://localhost:11434"

# SearxNG-Websuche (aus dem Docker-Stack)
SEARXNG_URL = "http://localhost:8888"

# --- Mixture of Agents ----------------------------------------------------
# Mehrere Modelle antworten auf dieselbe Aufgabe, ein Aggregator-Modell baut
# daraus die beste finale Antwort. Modelle müssen installiert sein.
MOA_PROPOSERS = ["qwen2.5-coder:32b", "dolphin-mixtral:latest"]
MOA_AGGREGATOR = "qwen2.5-coder:32b"

# --- Deep Search ----------------------------------------------------------
# Tiefe Recherche: mehrere Suchanfragen -> viele Quellen lesen -> iterieren
# -> mit Quellen zusammenfassen.
DEEP_QUERIES = 4   # Suchanfragen je Runde
DEEP_PAGES = 5     # Seiten je Runde tatsächlich lesen/scrapen
DEEP_ROUNDS = 2    # Recherche-Runden (Runde 2 schließt erkannte Lücken)

# --- Langzeitgedächtnis / RAG ---------------------------------------------
# Embedding-Modell (lokal über Ollama). Vorher laden:
#   docker exec -it ollama ollama pull nomic-embed-text
EMBED_MODEL = "nomic-embed-text"
MEMORY_DIR = "./memory_db"   # persistente Vektor-Datenbank (ChromaDB)
RAG_CHUNK = 1200             # Zeichen pro Dokument-Abschnitt
RAG_TOPK = 5                 # wie viele Treffer je Suche

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
