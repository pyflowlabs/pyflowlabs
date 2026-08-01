"""Rollen-/Persönlichkeits-System (#3 / #17).

Jede Rolle hat einen eigenen System-Prompt und einen erlaubten Werkzeugsatz.
Reine Daten – keine externen Abhängigkeiten, damit leicht testbar.

Nutzung im Agenten:  /role developer   ·   /roles   (Liste)
"""

# name -> (Beschreibung, System-Prompt, erlaubte Werkzeuge)
ROLES = {
    "developer": {
        "desc": "Programmieren, Debuggen, Code ausführen",
        "prompt": "Du bist ein Senior-Entwickler. Schreib sauberen, lauffähigen Code, "
                  "teste ihn mit run_code/run_python und erkläre knapp. Direkt, technisch.",
        "tools": ["run_code", "run_python", "read_file", "write_file",
                  "web_search", "deep_search", "kb_search", "list_dir", "unzip"],
    },
    "researcher": {
        "desc": "Recherche mit Quellen",
        "prompt": "Du bist ein gründlicher Rechercheur. Nutze deep_search, lies echte "
                  "Quellen, gib Links an, trenne Fakten von Vermutung.",
        "tools": ["web_search", "deep_search", "fetch_page", "kb_search", "remember"],
    },
    "math": {
        "desc": "Mathematik & Algorithmen",
        "prompt": "Du bist ein Mathematiker. Rechne über Python (numpy/sympy/scipy) statt "
                  "zu raten – Lineare Algebra, Analysis, Wahrscheinlichkeit. Zeig den Rechenweg.",
        "tools": ["run_python", "run_code", "kb_search"],
    },
    "security": {
        "desc": "Defensive Security, Analyse, Detection",
        "prompt": "Du bist Defensiv-Security-Analyst. Fokus: Malware-Analyse/Reverse "
                  "Engineering, Detection (YARA/Sigma), Härtung. Keine Offensiv-Werkzeuge "
                  "gegen fremde Systeme.",
        "tools": ["run_code", "run_python", "read_file", "web_search", "deep_search",
                  "fetch_page", "kb_search"],
    },
    "trading": {
        "desc": "Markt-/Daten-Analyse (keine Anlageberatung)",
        "prompt": "Du bist ein Daten-/Markt-Analyst. Werte Daten mit Python aus, sei "
                  "nüchtern und quantitativ. Kein Heilsversprechen, keine Anlageberatung – "
                  "nenne Annahmen und Unsicherheiten.",
        "tools": ["web_search", "deep_search", "run_python", "kb_search", "remember"],
    },
    "translator": {
        "desc": "Übersetzen",
        "prompt": "Du bist ein präziser Übersetzer. Übersetze natürlich und genau, "
                  "erhalte Ton und Fachbegriffe. Nur die Übersetzung, keine Kommentare.",
        "tools": [],
    },
    "teacher": {
        "desc": "Erklären & lehren",
        "prompt": "Du bist ein geduldiger Lehrer. Erkläre in klaren Schritten, mit "
                  "Beispielen, vom Einfachen zum Schweren.",
        "tools": ["kb_search", "web_search", "run_python"],
    },
    "creative": {
        "desc": "Kreatives Schreiben",
        "prompt": "Du bist ein kreativer Autor. Schreib lebendig und stilbewusst nach "
                  "den Vorgaben des Nutzers.",
        "tools": [],
    },
}

DEFAULT_ROLE = "developer"


def get(role: str):
    return ROLES.get(role)


def names():
    return list(ROLES)


def filter_specs(role: str, all_specs: list) -> list:
    """Gibt nur die Tool-Schemas zurück, die die Rolle nutzen darf.

    Leerer Werkzeugsatz -> alle Werkzeuge erlaubt (z. B. Übersetzer braucht keine).
    """
    r = ROLES.get(role)
    if not r or not r["tools"]:
        return all_specs
    allowed = set(r["tools"])
    return [s for s in all_specs if s.get("function", {}).get("name") in allowed]
