"""Zentrales Logging: klare Meldungen im Terminal + persistente Log-Datei.

Alle Python-Teile (agent.py, moa.py, tools.py) schreiben nach
  self-hosted-ai/logs/nero-agent.log
Unbehandelte Fehler landen dort mit vollem Traceback, und im Terminal erscheint
eine eindeutige Meldung mit dem Pfad zur Log-Datei.
"""

import logging
import os
import sys

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
LOG_FILE = os.path.join(LOG_DIR, "nero-agent.log")

_configured = False


def setup(name: str = "nero"):
    """Richtet Logging ein (idempotent) und gibt (Logger, Log-Pfad) zurück."""
    global _configured
    os.makedirs(LOG_DIR, exist_ok=True)

    if not _configured:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(LOG_FILE, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        # Unbehandelte Ausnahmen ins Log + klare Terminal-Meldung.
        def _hook(exc_type, exc, tb):
            logging.getLogger(name).error("Unbehandelter Fehler",
                                          exc_info=(exc_type, exc, tb))
            sys.stderr.write(
                f"\n[FEHLER] {exc_type.__name__}: {exc}\n"
                f"         Details im Protokoll: {LOG_FILE}\n\n"
            )

        sys.excepthook = _hook
        _configured = True

    return logging.getLogger(name), LOG_FILE
