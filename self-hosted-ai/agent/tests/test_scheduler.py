"""Tests für Scheduler (#10) und Benchmark-Metrik (#13) – ohne externe Libs."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config


def test_is_due_interval(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SCHEDULE_FILE", str(tmp_path / "s.json"))
    import importlib
    import scheduler
    importlib.reload(scheduler)

    now = datetime(2026, 1, 1, 12, 0, 0)
    job = {"enabled": True, "every_minutes": 60, "daily": None, "last_run": None}
    assert scheduler.is_due(job, now) is True          # noch nie gelaufen
    job["last_run"] = now.timestamp()
    assert scheduler.is_due(job, now) is False         # gerade gelaufen
    later = datetime(2026, 1, 1, 13, 1, 0)
    assert scheduler.is_due(job, later) is True         # >60 min später


def test_is_due_daily(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SCHEDULE_FILE", str(tmp_path / "s2.json"))
    import importlib
    import scheduler
    importlib.reload(scheduler)

    job = {"enabled": True, "every_minutes": None, "daily": "08:00", "last_run": None}
    assert scheduler.is_due(job, datetime(2026, 1, 1, 8, 0)) is True
    assert scheduler.is_due(job, datetime(2026, 1, 1, 9, 0)) is False


def test_add_list_remove(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SCHEDULE_FILE", str(tmp_path / "s3.json"))
    import importlib
    import scheduler
    importlib.reload(scheduler)

    j = scheduler.add_job("Backup", every_minutes=720)
    assert j["id"] == 1
    assert len(scheduler.list_jobs()) == 1
    assert scheduler.remove_job(1) is True
    assert scheduler.list_jobs() == []


def test_benchmark_tokens_per_sec():
    import benchmark
    # 100 Tokens in 2 Sekunden (2e9 ns) -> 50 tok/s
    assert benchmark.tokens_per_sec({"eval_count": 100, "eval_duration": 2_000_000_000}) == 50.0
    assert benchmark.tokens_per_sec({}) == 0.0
