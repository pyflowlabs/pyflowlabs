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
import re
import shutil
import subprocess
import sys
import tempfile

import requests
from bs4 import BeautifulSoup

import nero_config as config

log = logging.getLogger("nero.tools")


# --- Websuche (über SearxNG) ----------------------------------------------
def search_web_raw(query: str, num_results: int = 8) -> list:
    """Strukturierte Suche: Liste von {title, url, content}. Basis für Deep Search."""
    try:
        resp = requests.get(
            f"{config.SEARXNG_URL}/search",
            params={"q": query, "format": "json"},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])[:num_results]
    except Exception as exc:  # noqa: BLE001
        log.warning("search_web_raw fehlgeschlagen (query=%r): %s", query, exc)
        return []


def web_search(query: str, num_results: int = 8) -> str:
    """Sucht neutral im Web (SearxNG) und gibt Titel, URL und Kurztext zurück."""
    results = search_web_raw(query, num_results)
    if not results:
        return "Keine Treffer gefunden (oder Suche fehlgeschlagen – siehe Log)."

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
    workdir = os.path.abspath(config.WORKSPACE_DIR)
    os.makedirs(workdir, exist_ok=True)  # Arbeitsordner sicher anlegen (Windows: WinError 267)
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=config.CODE_TIMEOUT,
            cwd=workdir,
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


# --- Polyglot: Code in mehreren Sprachen ausführen -------------------------
def _write(folder: str, name: str, content: str) -> str:
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def _exec(cmd: list, cwd: str, timeout: int, compile_step: bool = False):
    """Führt einen Befehl aus. compile_step=True: gibt None bei Erfolg zurück,
    sonst die Fehlermeldung (zum Abbrechen vor dem Ausführen)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired:
        return f"Abgebrochen: '{cmd[0]}' lief länger als {timeout}s."
    except FileNotFoundError:
        log.warning("Toolchain fehlt: %s", cmd[0])
        return (f"Toolchain fehlt: '{cmd[0]}' nicht gefunden. "
                f"Installieren (siehe sandbox/README.md) oder Sandbox-Container nutzen.")
    except Exception as exc:  # noqa: BLE001
        log.exception("Ausführung fehlgeschlagen: %s", cmd)
        return f"Ausführung fehlgeschlagen: {exc}"

    if compile_step:
        if r.returncode != 0:
            return f"Kompilierfehler:\n{(r.stderr or r.stdout).strip()}"
        return None
    out, err = (r.stdout or "").strip(), (r.stderr or "").strip()
    parts = []
    if out:
        parts.append(f"AUSGABE:\n{out}")
    if err:
        parts.append(f"FEHLER:\n{err}")
    return "\n\n".join(parts) or "(keine Ausgabe)"


def _java_class(code: str) -> str:
    m = re.search(r"(?:public\s+)?class\s+([A-Za-z_]\w*)", code)
    return m.group(1) if m else "Main"


def docker_run_args() -> list:
    """Gehärtete `docker run`-Flags (RAM-/CPU-/Netz-/Prozess-Limits). Testbar."""
    return [
        "docker", "run", "--rm",
        f"--memory={config.SANDBOX_MEM}",
        f"--cpus={config.SANDBOX_CPUS}",
        f"--network={config.SANDBOX_NET}",
        f"--pids-limit={config.SANDBOX_PIDS}",
    ]


def _run_inner(host_cmds: list, docker_inner: str, tmp: str, timeout: int):
    """Führt aus – entweder gehärtet im Container (SANDBOX_MODE=docker) oder auf dem Host.

    host_cmds: Liste von (argv, compile_step)-Tupeln (nacheinander).
    docker_inner: eine bash-Zeile, die im Container läuft.
    """
    if config.SANDBOX_MODE == "docker":
        cmd = docker_run_args() + ["-v", f"{tmp}:/work", "-w", "/work",
                                   config.SANDBOX_IMAGE, "bash", "-lc", docker_inner]
        return _exec(cmd, tmp, timeout)
    # Host-Modus: Schritte nacheinander (Kompilieren -> Ausführen)
    for argv, compile_step in host_cmds:
        res = _exec(argv, tmp, timeout, compile_step=compile_step)
        if compile_step and res is not None:
            return res  # Kompilierfehler
        if not compile_step:
            return res
    return "(keine Ausgabe)"


def run_code(language: str, code: str) -> str:
    """Führt Code aus: python, javascript, c, cpp, csharp, java, sql, html.

    Bei config.SANDBOX_MODE == "docker" läuft alles isoliert im nero-sandbox-
    Container mit RAM-/CPU-/Netz-Limits (siehe sandbox/README.md).
    """
    lang = language.lower().strip().lstrip(".")
    base = os.path.abspath(config.WORKSPACE_DIR)
    os.makedirs(base, exist_ok=True)
    tmp = tempfile.mkdtemp(dir=base)
    t = config.CODE_TIMEOUT
    try:
        if lang in ("python", "py"):
            _write(tmp, "main.py", code)
            return _run_inner([([sys.executable, "main.py"], False)], "python3 main.py", tmp, t)
        if lang in ("javascript", "js", "node"):
            _write(tmp, "main.js", code)
            return _run_inner([(["node", "main.js"], False)], "node main.js", tmp, t)
        if lang == "c":
            _write(tmp, "main.c", code)
            return _run_inner([(["gcc", "main.c", "-o", "prog"], True), (["./prog"], False)],
                              "gcc main.c -o prog && ./prog", tmp, t)
        if lang in ("cpp", "c++", "cxx"):
            _write(tmp, "main.cpp", code)
            return _run_inner([(["g++", "main.cpp", "-o", "prog"], True), (["./prog"], False)],
                              "g++ main.cpp -o prog && ./prog", tmp, t)
        if lang == "java":
            cls = _java_class(code)
            _write(tmp, f"{cls}.java", code)
            return _run_inner([(["javac", f"{cls}.java"], True), (["java", "-cp", ".", cls], False)],
                              f"javac {cls}.java && java -cp . {cls}", tmp, t)
        if lang in ("sql", "sqlite"):
            _write(tmp, "main.sql", code)
            return _run_inner([(["sqlite3", "db.sqlite"], False)],  # host: über stdin unten
                              "sqlite3 db.sqlite < main.sql", tmp, t) \
                if config.SANDBOX_MODE == "docker" else _exec(
                    ["sqlite3", os.path.join(tmp, "db.sqlite"), code], tmp, t)
        if lang in ("csharp", "c#", "cs"):
            proj = os.path.join(tmp, "app")
            err = _exec(["dotnet", "new", "console", "-o", proj, "--force"], tmp, t * 3, compile_step=True)
            if err:
                return err
            _write(proj, "Program.cs", code)
            return _exec(["dotnet", "run", "--project", proj], tmp, t * 3)
        if lang == "html":
            path = _write(tmp, "page.html", code)
            return (f"HTML gespeichert: {path}\n"
                    f"(HTML wird nicht ausgeführt, sondern im Browser gerendert.)")
        return f"Sprache nicht unterstützt: {language}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- Zuordnung Name -> Funktion -------------------------------------------
DISPATCH = {
    "web_search": web_search,
    "fetch_page": fetch_page,
    "read_file": read_file,
    "write_file": write_file,
    "run_python": run_python,
    "run_code": run_code,
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
    {
        "type": "function",
        "function": {
            "name": "run_code",
            "description": "Führt Code in einer Sprache aus und gibt Ausgabe/Fehler zurück. "
                           "Sprachen: python, javascript, c, cpp, csharp, java, sql, html. "
                           "Kompiliert bei Bedarf. Toolchain muss vorhanden sein.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "description": "z. B. python, java, cpp, csharp, sql"},
                    "code": {"type": "string", "description": "Quellcode"},
                },
                "required": ["language", "code"],
            },
        },
    },
]
