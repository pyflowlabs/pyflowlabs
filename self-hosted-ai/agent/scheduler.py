#!/usr/bin/env python3
"""Scheduler (#10): wiederkehrende Aufgaben, die die KI selbst ausführt.

Beispiele: täglich Backup, News zusammenfassen, Dateien sortieren, Aktien prüfen.
Jobs werden in config.SCHEDULE_FILE (JSON) gespeichert und überstehen Neustarts.

CLI:
  python scheduler.py --add "Fasse die Tech-News zusammen" --daily 08:00
  python scheduler.py --add "Backup-Skript ausführen" --every 720
  python scheduler.py --list
  python scheduler.py --remove <id>
  python scheduler.py            # Schleife: fällige Jobs ausführen
"""

import argparse
import json
import os
from datetime import datetime

import nero_config as config
import logsetup

log, LOG_FILE = logsetup.setup("nero.scheduler")
SCHED = os.path.abspath(config.SCHEDULE_FILE)


def _load() -> list:
    if not os.path.exists(SCHED):
        return []
    try:
        with open(SCHED, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        log.exception("Konnte Zeitplan nicht lesen")
        return []


def _save(jobs: list) -> None:
    with open(SCHED, "w", encoding="utf-8") as fh:
        json.dump(jobs, fh, ensure_ascii=False, indent=2)


def add_job(task: str, every_minutes: int = None, daily: str = None) -> dict:
    jobs = _load()
    jid = (max([j["id"] for j in jobs], default=0) + 1)
    job = {"id": jid, "task": task, "every_minutes": every_minutes,
           "daily": daily, "enabled": True, "last_run": None}
    jobs.append(job)
    _save(jobs)
    return job


def list_jobs() -> list:
    return _load()


def remove_job(jid: int) -> bool:
    jobs = _load()
    new = [j for j in jobs if j["id"] != jid]
    _save(new)
    return len(new) != len(jobs)


def is_due(job: dict, now: datetime) -> bool:
    """Ist der Job jetzt fällig?"""
    if not job.get("enabled", True):
        return False
    last = job.get("last_run")
    if job.get("every_minutes"):
        if last is None:
            return True
        return (now.timestamp() - last) >= job["every_minutes"] * 60
    if job.get("daily"):
        if now.strftime("%H:%M") != job["daily"]:
            return False
        if last and datetime.fromtimestamp(last).date() == now.date():
            return False  # heute schon gelaufen
        return True
    return False


def run_pending(runner, now: datetime = None) -> list:
    """Führt alle fälligen Jobs über `runner(task)` aus. Gibt ausgeführte IDs zurück."""
    now = now or datetime.now()
    jobs = _load()
    ran = []
    for job in jobs:
        if is_due(job, now):
            log.info("Scheduler führt Job %s aus: %s", job["id"], job["task"])
            try:
                runner(job["task"])
            except Exception:  # noqa: BLE001
                log.exception("Job %s fehlgeschlagen", job["id"])
            job["last_run"] = now.timestamp()
            ran.append(job["id"])
    if ran:
        _save(jobs)
    return ran


def _default_runner(task: str) -> None:
    import agent  # lazy, damit CLI-Verwaltung ohne Modell-Libs funktioniert
    agent.run(task)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--add", metavar="TASK")
    p.add_argument("--every", type=int, help="Intervall in Minuten")
    p.add_argument("--daily", help="Uhrzeit HH:MM")
    p.add_argument("--list", action="store_true")
    p.add_argument("--remove", type=int)
    args = p.parse_args()

    if args.add:
        job = add_job(args.add, every_minutes=args.every, daily=args.daily)
        print(f"Job {job['id']} angelegt.")
        return
    if args.list:
        for j in list_jobs():
            trig = f"alle {j['every_minutes']} min" if j["every_minutes"] else f"täglich {j['daily']}"
            print(f"[{j['id']}] {trig:18} {'on' if j['enabled'] else 'off'}  {j['task']}")
        return
    if args.remove is not None:
        print("Entfernt." if remove_job(args.remove) else "Nicht gefunden.")
        return

    # Schleife
    import time
    print(f"Scheduler läuft. Zeitplan: {SCHED}\nProtokoll: {LOG_FILE}\n(Strg+C beendet)")
    try:
        while True:
            run_pending(_default_runner)
            time.sleep(30)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
