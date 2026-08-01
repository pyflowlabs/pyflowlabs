"""Plugin-Auto-Erkennung.

Jede .py-Datei im Ordner `plugins/` kann neue Werkzeuge beitragen. Der Loader
importiert sie automatisch beim Start – neue Fähigkeiten = neue Datei ablegen.

Ein Plugin definiert eine Liste `PLUGIN_TOOLS`, je Eintrag:
    {
      "name": "mein_tool",
      "func": meine_funktion,          # def meine_funktion(**kwargs) -> str
      "spec": { ... OpenAI/Ollama-Tool-Schema ... },
    }
"""

import importlib
import logging
import os
import pkgutil

log = logging.getLogger("nero.plugins")


def load_plugins(dispatch: dict, tools_spec: list) -> list:
    """Lädt alle Plugins aus dem plugins/-Ordner und registriert ihre Werkzeuge."""
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.isdir(plugins_dir):
        return []

    loaded = []
    for _finder, name, _ispkg in pkgutil.iter_modules([plugins_dir]):
        if name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"plugins.{name}")
            for tool in getattr(mod, "PLUGIN_TOOLS", []):
                dispatch[tool["name"]] = tool["func"]
                tools_spec.append(tool["spec"])
                loaded.append(tool["name"])
        except Exception as exc:  # noqa: BLE001
            log.warning("Plugin '%s' konnte nicht geladen werden: %s", name, exc)
    if loaded:
        log.info("Plugins geladen: %s", ", ".join(loaded))
    return loaded
