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
