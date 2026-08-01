"""Tests für das Rollen-System (#3/#17) – ohne externe Abhängigkeiten."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import roles


def test_roles_wellformed():
    assert roles.DEFAULT_ROLE in roles.ROLES
    for name, r in roles.ROLES.items():
        assert r["desc"] and r["prompt"]
        assert isinstance(r["tools"], list)


def test_filter_specs():
    all_specs = [
        {"function": {"name": "run_python"}},
        {"function": {"name": "web_search"}},
        {"function": {"name": "deep_search"}},
    ]
    # 'math' erlaubt run_python, aber nicht web_search
    filtered = roles.filter_specs("math", all_specs)
    got = {s["function"]["name"] for s in filtered}
    assert "run_python" in got
    assert "web_search" not in got


def test_empty_toolset_allows_all():
    all_specs = [{"function": {"name": "x"}}]
    # 'translator' hat leeren Werkzeugsatz -> alle erlaubt
    assert roles.filter_specs("translator", all_specs) == all_specs
