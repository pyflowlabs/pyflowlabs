#!/usr/bin/env python3
"""Langzeitgedächtnis + RAG (Vektor-Datenbank).

Zwei Sammlungen in einer lokalen ChromaDB:
  - "memory"     : Fakten/Vorlieben/Erkenntnisse über den Nutzer & Projekte
  - "knowledge"  : Inhalte aus deinen Dokumenten (RAG über Ordner/Dateien)

Embeddings laufen lokal über Ollama (EMBED_MODEL). Alles bleibt auf der Maschine.

Werkzeuge (im Agenten): remember, recall, kb_ingest, kb_search
Standalone-Test:  python memory.py
"""

import glob
import hashlib
import os

import ollama

import nero_config as config
import logsetup

log, LOG_FILE = logsetup.setup("nero.memory")

try:
    import chromadb
    _HAVE_CHROMA = True
except ImportError:
    _HAVE_CHROMA = False

_MISSING = ("Vektor-DB nicht verfügbar: 'chromadb' fehlt. "
            "Installieren: pip install -r agent/requirements-memory.txt")

_client = None


def _db():
    global _client
    if _client is None:
        os.makedirs(os.path.abspath(config.MEMORY_DIR), exist_ok=True)
        _client = chromadb.PersistentClient(path=os.path.abspath(config.MEMORY_DIR))
    return _client


def _embed(text: str):
    r = ollama.Client(host=config.OLLAMA_HOST).embeddings(
        model=config.EMBED_MODEL, prompt=text)
    return r["embedding"]


def _chunks(text: str, size: int):
    text = " ".join(text.split())
    return [text[i:i + size] for i in range(0, len(text), size)] or [""]


def _add(collection: str, text: str, meta: dict):
    col = _db().get_or_create_collection(collection)
    uid = hashlib.sha1(f"{collection}:{meta}:{text}".encode()).hexdigest()
    col.add(ids=[uid], embeddings=[_embed(text)], documents=[text], metadatas=[meta])
    return uid


# --- Werkzeuge -------------------------------------------------------------
def remember(text: str) -> str:
    """Merkt sich eine Information dauerhaft (Vorliebe, Projektstand, Erkenntnis)."""
    if not _HAVE_CHROMA:
        return _MISSING
    try:
        _add("memory", text, {"type": "memory"})
        return "Gemerkt."
    except Exception as exc:  # noqa: BLE001
        log.exception("remember fehlgeschlagen")
        return f"Konnte nicht merken: {exc}"


def recall(query: str) -> str:
    """Holt passende Erinnerungen zu einer Frage aus dem Gedächtnis."""
    if not _HAVE_CHROMA:
        return _MISSING
    try:
        col = _db().get_or_create_collection("memory")
        if col.count() == 0:
            return "(noch keine Erinnerungen gespeichert)"
        res = col.query(query_embeddings=[_embed(query)],
                        n_results=min(config.RAG_TOPK, col.count()))
        docs = res.get("documents", [[]])[0]
        return "\n".join(f"- {d}" for d in docs) or "(nichts Passendes gefunden)"
    except Exception as exc:  # noqa: BLE001
        log.exception("recall fehlgeschlagen")
        return f"Konnte nicht abrufen: {exc}"


def _read_text_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return ""  # PDF-Unterstützung optional
        try:
            return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
        except Exception:  # noqa: BLE001
            return ""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except Exception:  # noqa: BLE001
        return ""


def kb_ingest(path: str) -> str:
    """Liest eine Datei oder einen ganzen Ordner in die Wissensbasis ein (RAG).

    Unterstützt .txt, .md, .pdf (weitere leicht ergänzbar). Ordner werden rekursiv
    durchsucht.
    """
    if not _HAVE_CHROMA:
        return _MISSING
    path = os.path.abspath(os.path.expanduser(path))
    if os.path.isdir(path):
        files = [f for ext in ("txt", "md", "pdf")
                 for f in glob.glob(os.path.join(path, "**", f"*.{ext}"), recursive=True)]
    elif os.path.isfile(path):
        files = [path]
    else:
        return f"Pfad nicht gefunden: {path}"

    total_chunks = 0
    for f in files:
        text = _read_text_file(f)
        if not text.strip():
            continue
        for idx, chunk in enumerate(_chunks(text, config.RAG_CHUNK)):
            try:
                _add("knowledge", chunk, {"source": f, "chunk": idx})
                total_chunks += 1
            except Exception:  # noqa: BLE001
                log.exception("kb_ingest: Abschnitt fehlgeschlagen (%s)", f)
    return f"Eingelesen: {len(files)} Datei(en), {total_chunks} Abschnitte in die Wissensbasis."


def kb_search(query: str) -> str:
    """Durchsucht die Wissensbasis (deine Dokumente) und gibt Treffer mit Quelle zurück."""
    if not _HAVE_CHROMA:
        return _MISSING
    try:
        col = _db().get_or_create_collection("knowledge")
        if col.count() == 0:
            return "(Wissensbasis ist leer – erst mit kb_ingest Dokumente einlesen)"
        res = col.query(query_embeddings=[_embed(query)],
                        n_results=min(config.RAG_TOPK, col.count()))
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        out = []
        for d, m in zip(docs, metas):
            src = os.path.basename(m.get("source", "?"))
            out.append(f"[{src}] {d[:400]}")
        return "\n\n".join(out) or "(nichts Passendes gefunden)"
    except Exception as exc:  # noqa: BLE001
        log.exception("kb_search fehlgeschlagen")
        return f"Suche fehlgeschlagen: {exc}"


# --- Tool-Schemas (für den Agenten) ---------------------------------------
TOOLS = [
    {"name": "remember", "func": remember, "spec": {"type": "function", "function": {
        "name": "remember",
        "description": "Merkt sich dauerhaft eine wichtige Information (Vorliebe, "
                       "Projektstand, Erkenntnis, vermiedener Fehler).",
        "parameters": {"type": "object", "properties": {
            "text": {"type": "string", "description": "Was gemerkt werden soll"}},
            "required": ["text"]}}}},
    {"name": "recall", "func": recall, "spec": {"type": "function", "function": {
        "name": "recall",
        "description": "Ruft passende Erinnerungen zu einer Frage ab.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Wonach gesucht wird"}},
            "required": ["query"]}}}},
    {"name": "kb_ingest", "func": kb_ingest, "spec": {"type": "function", "function": {
        "name": "kb_ingest",
        "description": "Liest eine Datei oder einen Ordner (txt/md/pdf) in die "
                       "Wissensbasis ein, damit die KI darauf antworten kann (RAG).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Datei- oder Ordnerpfad"}},
            "required": ["path"]}}}},
    {"name": "kb_search", "func": kb_search, "spec": {"type": "function", "function": {
        "name": "kb_search",
        "description": "Durchsucht deine eingelesenen Dokumente und gibt Treffer mit Quelle zurück.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Suchfrage"}},
            "required": ["query"]}}}},
]


def main() -> None:
    print("Gedächtnis/RAG – Mini-Test")
    print(f"ChromaDB verfügbar: {_HAVE_CHROMA}")
    print(f"Embedding-Modell: {config.EMBED_MODEL}")
    print(f"DB-Ordner: {os.path.abspath(config.MEMORY_DIR)}")
    if _HAVE_CHROMA:
        print(remember("Der Nutzer bevorzugt knappe, technische Antworten."))
        print(recall("Wie soll ich antworten?"))


if __name__ == "__main__":
    main()
