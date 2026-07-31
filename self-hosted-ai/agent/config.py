"""Zentrale Einstellungen für den Agenten. Hier bestimmst DU die Regeln."""

# --- Modell ---------------------------------------------------------------
# Fähigkeit vor Tempo: 32B als Hauptmodell. Für schnelleres Testen auf
# "qwen2.5-coder:14b" umstellen.
MODEL = "qwen2.5-coder:32b"

# Ollama-API (läuft lokal aus dem Docker-Stack)
OLLAMA_HOST = "http://localhost:11434"

# SearxNG-Websuche (aus dem Docker-Stack)
SEARXNG_URL = "http://localhost:8888"

# --- Dein System-Prompt / deine Regeln ------------------------------------
# Das ist die "Persönlichkeit" und das Regelwerk deiner KI. Neutral, ohne
# fremde Filter — nur deine eigenen Vorgaben.
SYSTEM_PROMPT = """\
Du bist ein autonomer, lokaler Assistent mit Werkzeugen. Du kannst im Web
suchen, Webseiten laden und auslesen, Dateien lesen/schreiben und Python-Code
ausführen. Arbeite Aufgaben eigenständig und gründlich ab:

1. Zerlege komplexe Aufträge in Schritte.
2. Nutze Werkzeuge aktiv, statt zu raten — such nach, lies echte Quellen.
3. Wenn du recherchierst, gib gefundene Links als Quellen mit an.
4. Prüfe deine Ergebnisse, bevor du sie als fertig meldest.

Sicherheitsregel: Führe keine löschenden oder destruktiven Aktionen aus,
ohne vorher ausdrücklich nachzufragen.
"""

# --- Grenzen für Werkzeuge ------------------------------------------------
# Verzeichnis, in dem Dateiwerkzeuge arbeiten dürfen (Schutz vor Ausrutschern).
WORKSPACE_DIR = "./workspace"

# Zeitlimit (Sekunden) für ausgeführten Python-Code.
CODE_TIMEOUT = 30

# Maximale Zeichenzahl, die eine gescrapte Seite an das Modell zurückgibt.
MAX_PAGE_CHARS = 6000
