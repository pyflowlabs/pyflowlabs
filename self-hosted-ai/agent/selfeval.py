"""Selbstbewertung (#8): Antwort -> Selbst-Kritik -> ggf. verbesserte Antwort.

Die KI bewertet ihre eigene Antwort (richtig? vollständig? was besser?) und
liefert bei Bedarf eine überarbeitete Fassung.
"""

import config


def critique_and_improve(client, task: str, answer: str, model: str = None) -> dict:
    """Bewertet und verbessert eine Antwort. Gibt {verdict, improved, final} zurück."""
    model = model or config.MODEL
    review_prompt = (
        f"Bewerte die folgende Antwort auf die Aufgabe kritisch.\n\n"
        f"AUFGABE:\n{task}\n\nANTWORT:\n{answer}\n\n"
        "Prüfe: (1) Ist sie sachlich richtig? (2) Vollständig? (3) Was wäre besser?\n"
        "Wenn sie gut genug ist, antworte NUR mit: OK\n"
        "Sonst gib eine verbesserte, finale Antwort aus (ohne Vorrede)."
    )
    resp = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": review_prompt},
        ],
    )
    verdict = resp["message"]["content"].strip()
    if verdict.strip().upper().startswith("OK"):
        return {"verdict": "ok", "improved": False, "final": answer}
    return {"verdict": "verbessert", "improved": True, "final": verdict}
