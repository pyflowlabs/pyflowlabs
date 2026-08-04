"""Test des Text-Werkzeugaufruf-Fallbacks. Braucht ollama (via agent) – skip sonst."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pytest.importorskip("ollama")
pytest.importorskip("requests")
pytest.importorskip("bs4")

import agent


def test_fenced_json_tool_call_detected():
    content = '```json\n{"name": "run_python", "arguments": {"code": "print(1)"}}\n```'
    call = agent._extract_tool_call(content)
    assert call is not None
    assert call["function"]["name"] == "run_python"
    assert call["function"]["arguments"]["code"] == "print(1)"


def test_plain_text_is_not_a_tool_call():
    assert agent._extract_tool_call("Hier ist eine ganz normale Antwort.") is None


def test_unknown_tool_ignored():
    assert agent._extract_tool_call('{"name": "does_not_exist", "arguments": {}}') is None


def test_degenerate_answer_detected():
    assert agent._is_degenerate('```json\n{"name": null, "arguments": null}\n```') is True
    assert agent._is_degenerate("Die Primzahlen sind [2, 3, 5].") is False
