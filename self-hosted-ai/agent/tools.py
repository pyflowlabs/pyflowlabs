"""Werkzeuge, die der Agent aufrufen kann.

Jedes Werkzeug besteht aus zwei Teilen:
  1. einer Python-Funktion, die die eigentliche Arbeit macht,
  2. einem JSON-Schema (in TOOLS_SPEC), das dem Modell erklärt, wann/wie es
     das Werkzeug aufruft.

Neue Fähigkeiten fügst du hinzu, indem du eine Funktion schreibst und ihr
Schema in TOOLS_SPEC einträgst — mehr nicht.
"""

import logging
import os
import subprocess
import sys

import requests
from bs4 import BeautifulSoup

import config

log = logging.getLogger("nero.tools")


# --- Websuche (Deep Search über SearxNG) ----------------------------------
def web_search(query: str, num_results: int = 8) -> str:
    """Sucht neutral im Web (SearxNG) und gibt Titel, URL und Kurztext zurück."""
    try:
        resp = requests.get(
            f"{config.SEARXNG_URL}/search",
            params={"q": query, "format": "json"},
            timeout=20,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])[:num_results]
    except Exception as exc:  # noqa: BLE001
        log.warning("web_search fehlgeschlagen (query=%r): %s", query, exc)
        return f"Suche fehlgeschlagen: {exc}"

    if not results:
        return "Keine Treffer gefunden."

    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "").strip()
        url = r.get("url", "")
        snippet = r.get("content", "").strip()
        lines.append(f"{i}. {title}\n   {url}\n   {snippet}")
    return "\n".join(lines)


# --- Seite laden und auslesen (Scraping) ----------------------------------
def fetch_page(url: str) -> str:
    """Lädt eine Webseite, gibt sauberen Text plus die enthaltenen Links zurück."""
    try:
        resp = requests.get(
            url,
            timeout=25,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LocalAgent/1.0)"},
        )
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        log.warning("fetch_page fehlgeschlagen (url=%r): %s", url, exc)
        return f"Konnte Seite nicht laden: {exc}"

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.get_text(" ").split())[: config.MAX_PAGE_CHARS]

    links = []
    for a in soup.find_all("a", href=True)[:40]:
        label = " ".join(a.get_text(" ").split())[:80]
        links.append(f"- {label or '(kein Text)'} -> {a['href']}")

    links_block = "\n".join(links) if links else "(keine Links gefunden)"
    return f"TEXT:\n{text}\n\nLINKS:\n{links_block}"


# --- Dateien im Workspace lesen/schreiben ---------------------------------
def _safe_path(path: str) -> str:
    base = os.path.abspath(config.WORKSPACE_DIR)
    os.makedirs(base, exist_ok=True)
    full = os.path.abspath(os.path.join(base, path))
    if not full.startswith(base):
        raise ValueError("Pfad liegt außerhalb des Workspace.")
    return full


def read_file(path: str) -> str:
    """Liest eine Datei aus dem Workspace."""
    try:
        with open(_safe_path(path), "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception as exc:  # noqa: BLE001
        log.warning("read_file fehlgeschlagen (path=%r): %s", path, exc)
        return f"Konnte Datei nicht lesen: {exc}"


def write_file(path: str, content: str) -> str:
    """Schreibt eine Datei in den Workspace."""
    try:
        full = _safe_path(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(content)
        return f"Gespeichert: {path} ({len(content)} Zeichen)"
    except Exception as exc:  # noqa: BLE001
        log.warning("write_file fehlgeschlagen (path=%r): %s", path, exc)
        return f"Konnte Datei nicht schreiben: {exc}"


# --- Python-Code ausführen -------------------------------------------------
def run_python(code: str) -> str:
    """Führt Python-Code aus und gibt Ausgabe/Fehler zurück.

    Hinweis: läuft als Subprozess mit Zeitlimit. Für echte Isolation später
    in einen Docker-Container verlagern (Phase 5).
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=config.CODE_TIMEOUT,
            cwd=os.path.abspath(config.WORKSPACE_DIR),
        )
    except subprocess.TimeoutExpired:
        log.warning("run_python: Zeitlimit (%ss) überschritten.", config.CODE_TIMEOUT)
        return f"Abgebrochen: Code lief länger als {config.CODE_TIMEOUT}s."
    except Exception as exc:  # noqa: BLE001
        log.warning("run_python fehlgeschlagen: %s", exc)
        return f"Ausführung fehlgeschlagen: {exc}"

    out = result.stdout.strip()
    err = result.stderr.strip()
    parts = []
    if out:
        parts.append(f"AUSGABE:\n{out}")
    if err:
        parts.append(f"FEHLER:\n{err}")
    return "\n\n".join(parts) or "(keine Ausgabe)"


# --- Zuordnung Name -> Funktion -------------------------------------------
DISPATCH = {
    "web_search": web_search,
    "fetch_page": fetch_page,
    "read_file": read_file,
    "write_file": write_file,
    "run_python": run_python,
}


# --- Schema für das Modell (Tool-Calling) ----------------------------------
TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Sucht neutral im Web und liefert Titel, URLs und Kurztexte. "
                           "Für Recherche und um aktuelle Links zu finden.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Suchbegriff"},
                    "num_results": {"type": "integer", "description": "Anzahl Treffer (Standard 8)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page",
            "description": "Lädt eine Webseite und gibt sauberen Text plus alle Links zurück. "
                           "Zum Auslesen/Scrapen einer konkreten URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Vollständige URL"},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Liest eine Datei aus dem Arbeitsverzeichnis.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Pfad relativ zum Workspace"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Schreibt/überschreibt eine Datei im Arbeitsverzeichnis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Pfad relativ zum Workspace"},
                    "content": {"type": "string", "description": "Dateiinhalt"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Führt Python-Code aus und gibt Ausgabe/Fehler zurück. "
                           "Zum Rechnen, Testen und für eigene Scraper-Skripte.",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Python-Code"}},
                "required": ["code"],
            },
        },
    },
]
