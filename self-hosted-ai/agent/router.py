"""Auto-Modell-Router (#7-Ergänzung): wählt je Aufgabe automatisch das Modell.

Leichte Aufgaben -> schnelles Modell (config.MODEL, z. B. 14B).
Schwere/komplexe Aufgaben -> großes Modell (config.HEAVY_MODEL, z. B. 32B).

Heuristik (schnell, vorhersehbar). Abschaltbar über NERO_ROUTER=0.
"""

import nero_config as config

# Stichwörter, die auf anspruchsvolle Aufgaben hindeuten -> großes Modell.
HEAVY_HINTS = (
    "architektur", "refactor", "refaktor", "komplex", "entwirf", "entwerfe",
    "beweise", "beweis ", "optimiere", "vollständige anwendung", "ganze app",
    "mehrere dateien", "algorithmus entwerfen", "anspruchsvoll", "schwierig",
    "design pattern", "skalier", "performance-analyse",
)


def pick_model(task: str) -> str:
    """Gibt das passende Modell für die Aufgabe zurück."""
    if not config.ROUTER_ENABLED:
        return config.MODEL
    t = (task or "").lower()
    if len(task or "") > 600 or any(h in t for h in HEAVY_HINTS):
        return config.HEAVY_MODEL
    return config.MODEL


# Signale, dass eine Frage aktuelle/externe Fakten braucht -> Suche erzwingen,
# damit das Modell nicht aus (veraltetem) Gedächtnis halluziniert.
SEARCH_HINTS = (
    "aktuell", "neueste", "neuste", "neusten", "neuesten", "heute", "momentan",
    "tier list", "tierliste", "tier-liste", "tier liste", "meta build", "meta-build",
    "meta builds", "patch", "release", "erschien", "erscheint", "preis", "kostet",
    "news", "nachricht", "wetter", "kurs", "aktie", "börse",
    "2023", "2024", "2025", "2026", "wer ist", "wann kommt", "beste build",
    "aktuelle", "dieses jahr", "letzte woche", "gerade", "version",
)


def needs_search(task: str) -> bool:
    """True, wenn die Frage aktuelle/externe Fakten braucht (Suche erzwingen)."""
    t = (task or "").lower()
    return any(h in t for h in SEARCH_HINTS)
