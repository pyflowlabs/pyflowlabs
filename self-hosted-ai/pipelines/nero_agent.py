"""
title: NERO QUANTUM
author: nero
description: Voller NERO-QUANTUM-Agent (Werkzeuge, Deep Search, Rollen, Gedächtnis) direkt im Chat.
requirements: ollama, requests, beautifulsoup4
"""
# Open-WebUI-Pipeline: bringt den kompletten Agenten hinter die Chat-Oberfläche.
# In der Oberfläche erscheint danach ein Modell "NERO QUANTUM" im Dropdown.

import sys
from typing import List, Union, Generator, Iterator

from pydantic import BaseModel

# Der Agent-Code wird in den Container gemountet (siehe docker-compose.pipelines.yml).
sys.path.insert(0, "/app/nero_agent")


class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.name = "NERO QUANTUM"
        self._agent = None

    async def on_startup(self):
        # Agent einmalig laden (registriert Werkzeuge, Plugins, Rollen).
        try:
            import agent
            self._agent = agent
        except Exception:  # noqa: BLE001 - Fehler wird bei pipe() gemeldet
            self._agent = None

    async def on_shutdown(self):
        pass

    def pipe(self, user_message: str, model_id: str,
             messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        if self._agent is None:
            import agent
            self._agent = agent
        try:
            prior = messages[:-1] if messages else []
            return self._agent.respond(user_message, prior_messages=prior)
        except Exception as exc:  # noqa: BLE001
            return f"NERO QUANTUM Fehler: {exc}"
