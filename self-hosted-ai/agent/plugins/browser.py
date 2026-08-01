"""Plugin: Web-Automatisierung (#16) über Playwright.

Ermöglicht der KI, echte Webseiten zu bedienen (JavaScript-Seiten, Formulare,
Klicks) – mehr als reines Scraping. Benötigt Playwright:
    pip install playwright && playwright install chromium

Wird automatisch als Plugin geladen; ohne Playwright gibt es eine klare Meldung.
"""

import os

_HINT = ("Playwright fehlt. Installieren: pip install playwright && "
         "playwright install chromium")


def _have_playwright() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def browse(url: str, action: str = "text") -> str:
    """Öffnet eine Seite im echten Browser. action: 'text' (Inhalt) oder 'screenshot'."""
    if not _have_playwright():
        return _HINT
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            if action == "screenshot":
                out = os.path.abspath(os.path.join("workspace", "screenshot.png"))
                os.makedirs(os.path.dirname(out), exist_ok=True)
                page.screenshot(path=out, full_page=True)
                browser.close()
                return f"Screenshot gespeichert: {out}"
            text = page.inner_text("body")[:6000]
            browser.close()
            return text
    except Exception as exc:  # noqa: BLE001
        return f"Browser-Aktion fehlgeschlagen: {exc}"


def fill_form(url: str, selector: str, value: str, submit_selector: str = "") -> str:
    """Füllt ein Feld (CSS-Selector) und klickt optional einen Submit-Button."""
    if not _have_playwright():
        return _HINT
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            page.fill(selector, value)
            if submit_selector:
                page.click(submit_selector)
                page.wait_for_load_state("domcontentloaded")
            result = page.inner_text("body")[:4000]
            browser.close()
            return result
    except Exception as exc:  # noqa: BLE001
        return f"Formular-Aktion fehlgeschlagen: {exc}"


PLUGIN_TOOLS = [
    {"name": "browse", "func": browse, "spec": {"type": "function", "function": {
        "name": "browse",
        "description": "Öffnet eine Webseite im echten Browser (auch JS-Seiten) und gibt "
                       "Text zurück oder macht einen Screenshot.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string", "description": "URL"},
            "action": {"type": "string", "description": "'text' oder 'screenshot'"}},
            "required": ["url"]}}}},
    {"name": "fill_form", "func": fill_form, "spec": {"type": "function", "function": {
        "name": "fill_form",
        "description": "Füllt ein Formularfeld und klickt optional einen Button.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string"},
            "selector": {"type": "string", "description": "CSS-Selector des Feldes"},
            "value": {"type": "string"},
            "submit_selector": {"type": "string", "description": "CSS-Selector des Buttons (optional)"}},
            "required": ["url", "selector", "value"]}}}},
]
