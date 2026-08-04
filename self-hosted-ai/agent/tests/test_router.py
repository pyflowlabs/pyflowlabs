"""Tests für den Auto-Modell-Router (#7-Ergänzung)."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import nero_config as config
import router


def test_simple_task_uses_default(monkeypatch):
    monkeypatch.setattr(config, "ROUTER_ENABLED", True)
    monkeypatch.setattr(config, "MODEL", "qwen2.5-coder:14b")
    monkeypatch.setattr(config, "HEAVY_MODEL", "qwen2.5-coder:32b")
    assert router.pick_model("Wie spät ist es?") == "qwen2.5-coder:14b"


def test_heavy_keyword_uses_big(monkeypatch):
    monkeypatch.setattr(config, "ROUTER_ENABLED", True)
    monkeypatch.setattr(config, "MODEL", "qwen2.5-coder:14b")
    monkeypatch.setattr(config, "HEAVY_MODEL", "qwen2.5-coder:32b")
    assert router.pick_model("Entwirf die Architektur einer skalierbaren App") == "qwen2.5-coder:32b"


def test_long_task_uses_big(monkeypatch):
    monkeypatch.setattr(config, "ROUTER_ENABLED", True)
    monkeypatch.setattr(config, "MODEL", "qwen2.5-coder:14b")
    monkeypatch.setattr(config, "HEAVY_MODEL", "qwen2.5-coder:32b")
    assert router.pick_model("x" * 700) == "qwen2.5-coder:32b"


def test_router_disabled(monkeypatch):
    monkeypatch.setattr(config, "ROUTER_ENABLED", False)
    monkeypatch.setattr(config, "MODEL", "qwen2.5-coder:14b")
    assert router.pick_model("Entwirf eine komplexe Architektur") == "qwen2.5-coder:14b"
