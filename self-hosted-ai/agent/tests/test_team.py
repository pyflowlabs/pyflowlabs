"""Test des Team-Planers (#6) – ohne externe Libs."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import team


def test_parse_plan_valid():
    text = 'Hier der Plan: [{"role":"researcher","task":"Quellen suchen"},' \
           '{"role":"developer","task":"Skript schreiben"}]'
    plan = team.parse_plan(text)
    assert len(plan) == 2
    assert plan[0]["role"] == "researcher"
    assert plan[1]["task"] == "Skript schreiben"


def test_parse_plan_unknown_role_falls_back():
    plan = team.parse_plan('[{"role":"zauberer","task":"x"}]')
    assert plan[0]["role"] == "developer"  # DEFAULT_ROLE


def test_parse_plan_garbage():
    assert team.parse_plan("kein json hier") == []
