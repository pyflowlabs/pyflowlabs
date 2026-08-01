"""Beispiel-Plugin: Archiv-Werkzeuge (ZIP entpacken, Ordner auflisten).

Zeigt, wie ein Plugin neue Werkzeuge beiträgt. Kopiere diese Datei als Vorlage
für eigene Plugins (spotify.py, finance.py, weather.py ...).
"""

import os
import zipfile


def _safe(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def unzip(path: str, target: str = "") -> str:
    """Entpackt ein ZIP-Archiv. Zielordner optional (Standard: neben dem Archiv)."""
    src = _safe(path)
    if not os.path.isfile(src):
        return f"ZIP nicht gefunden: {src}"
    dest = _safe(target) if target else os.path.splitext(src)[0]
    try:
        with zipfile.ZipFile(src) as zf:
            zf.extractall(dest)
            n = len(zf.namelist())
        return f"Entpackt: {n} Einträge -> {dest}"
    except Exception as exc:  # noqa: BLE001
        return f"Entpacken fehlgeschlagen: {exc}"


def list_dir(path: str) -> str:
    """Listet Dateien/Ordner in einem Verzeichnis auf."""
    d = _safe(path)
    if not os.path.isdir(d):
        return f"Ordner nicht gefunden: {d}"
    entries = sorted(os.listdir(d))
    return "\n".join(entries) if entries else "(leer)"


PLUGIN_TOOLS = [
    {"name": "unzip", "func": unzip, "spec": {"type": "function", "function": {
        "name": "unzip",
        "description": "Entpackt ein ZIP-Archiv in einen Zielordner.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Pfad zur .zip-Datei"},
            "target": {"type": "string", "description": "Zielordner (optional)"}},
            "required": ["path"]}}}},
    {"name": "list_dir", "func": list_dir, "spec": {"type": "function", "function": {
        "name": "list_dir",
        "description": "Listet den Inhalt eines Ordners auf.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Ordnerpfad"}},
            "required": ["path"]}}}},
]
