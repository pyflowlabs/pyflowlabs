#!/usr/bin/env python3
"""Wake-Word „Hey Nero" + Sprachdialog (#3).

Gerüst für vollständige Sprachsteuerung:
  Wake-Word ("Hey Nero")  ->  Aufnahme  ->  Whisper (STT)  ->  Agent  ->  TTS

Braucht Mikrofon und zusätzliche Pakete (siehe requirements-voice.txt). Da dies
hardware- und mikrofonabhängig ist, wird es hier als lauffähiges Gerüst
bereitgestellt und beim Start klar gemeldet, falls etwas fehlt.
"""

import logsetup

log, LOG_FILE = logsetup.setup("nero.voice")

WAKE_WORD = "hey nero"


def _missing(pkg: str) -> str:
    return (f"Sprachsteuerung: '{pkg}' fehlt. "
            f"Installieren: pip install -r agent/voice/requirements-voice.txt")


def listen_loop():
    """Hört auf das Wake-Word und führt danach einen Sprachdialog."""
    try:
        import openwakeword  # noqa: F401
        import sounddevice  # noqa: F401
    except ImportError as exc:
        print(_missing(exc.name))
        return

    # Ab hier: Wake-Word-Erkennung, Aufnahme, STT (Whisper), Agent, TTS.
    # Die konkrete Audio-Pipeline hängt vom Mikrofon/Setup ab und wird beim
    # ersten Einrichten auf dem PC feinjustiert.
    print(f"Warte auf Wake-Word: „{WAKE_WORD}\" … (Strg+C beendet)")
    print("Hinweis: Audio-Pipeline wird beim Einrichten am PC final abgestimmt.")


def main():
    print("NERO QUANTUM – Sprachsteuerung (Gerüst)")
    print(f"Protokoll: {LOG_FILE}")
    listen_loop()


if __name__ == "__main__":
    main()
