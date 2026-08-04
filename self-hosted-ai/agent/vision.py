"""Vision (#4): Bilder verstehen – OCR, Diagramme, Tabellen, Screenshots, Handschrift.

Nutzt ein lokales Vision-Modell über Ollama (config.VISION_MODEL). Für reine
Texterkennung ist zusätzlich Tesseract-OCR möglich (falls installiert).
"""

import os

import ollama

import nero_config as config
import logsetup

log, _ = logsetup.setup("nero.vision")


def analyze_image(path: str, question: str = "Beschreibe das Bild und lies allen Text.") -> str:
    """Analysiert ein Bild mit dem Vision-Modell (Inhalt, Text, Diagramme, Tabellen)."""
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isfile(path):
        return f"Bild nicht gefunden: {path}"
    try:
        resp = ollama.Client(host=config.OLLAMA_HOST).chat(
            model=config.VISION_MODEL,
            messages=[{"role": "user", "content": question, "images": [path]}],
        )
        return resp["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        log.exception("analyze_image fehlgeschlagen")
        return (f"Bildanalyse fehlgeschlagen: {exc}\n"
                f"Vision-Modell laden: docker exec -it ollama ollama pull {config.VISION_MODEL}")


def ocr(path: str) -> str:
    """Reine Texterkennung über Tesseract (falls installiert), sonst Vision-Modell."""
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isfile(path):
        return f"Bild nicht gefunden: {path}"
    try:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(path)).strip() or "(kein Text erkannt)"
    except ImportError:
        return analyze_image(path, "Gib ausschließlich den erkannten Text zurück (OCR).")
    except Exception as exc:  # noqa: BLE001
        log.exception("ocr fehlgeschlagen")
        return f"OCR fehlgeschlagen: {exc}"


TOOLS = [
    {"name": "analyze_image", "func": analyze_image, "spec": {"type": "function", "function": {
        "name": "analyze_image",
        "description": "Analysiert ein Bild: Inhalt, Text (OCR), Diagramme, Tabellen, "
                       "Screenshots, Handschrift. Braucht ein Vision-Modell.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Pfad zum Bild"},
            "question": {"type": "string", "description": "Was soll erkannt werden? (optional)"}},
            "required": ["path"]}}}},
    {"name": "ocr", "func": ocr, "spec": {"type": "function", "function": {
        "name": "ocr",
        "description": "Reine Texterkennung (OCR) aus einem Bild.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Pfad zum Bild"}},
            "required": ["path"]}}}},
]
