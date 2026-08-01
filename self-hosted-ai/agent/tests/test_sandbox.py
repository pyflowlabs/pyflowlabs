"""Test der Sandbox-Härtungs-Flags (#11). Braucht requests/bs4 (tools) – skip sonst."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pytest.importorskip("requests")
pytest.importorskip("bs4")

import config
import tools


def test_docker_run_args_has_limits():
    args = tools.docker_run_args()
    joined = " ".join(args)
    assert "--memory=" in joined
    assert "--cpus=" in joined
    assert f"--network={config.SANDBOX_NET}" in joined
    assert "--pids-limit=" in joined
