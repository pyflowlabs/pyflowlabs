"""Tests für den Polyglot-Code-Runner. Braucht requests/bs4 (via tools) – wird
übersprungen, wenn nicht installiert."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pytest.importorskip("requests")
pytest.importorskip("bs4")

import tools


def test_run_python():
    out = tools.run_code("python", "print(6*7)")
    assert "42" in out


def test_workspace_path_safety():
    # Pfad außerhalb des Workspace muss abgelehnt werden
    out = tools.write_file("../../etc/evil.txt", "x")
    assert "außerhalb" in out or "nicht schreiben" in out


def test_unsupported_language():
    assert "nicht unterstützt" in tools.run_code("brainfuck", "+++")
