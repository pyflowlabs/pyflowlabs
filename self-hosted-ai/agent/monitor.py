#!/usr/bin/env python3
"""Monitoring (#14): Live-Statistiken zu CPU, RAM, GPU, VRAM, Temperatur, Strom.

CPU/RAM über psutil (falls installiert), GPU-Werte über `nvidia-smi`.
Start:  python monitor.py        (aktualisiert alle 2 s)
        python monitor.py --once (einmalige Momentaufnahme)
"""

import shutil
import subprocess
import sys
import time


def cpu_ram() -> str:
    try:
        import psutil
    except ImportError:
        return "CPU/RAM: psutil nicht installiert (pip install psutil)"
    cpu = psutil.cpu_percent(interval=None)
    vm = psutil.virtual_memory()
    return f"CPU {cpu:5.1f}%   RAM {vm.percent:5.1f}% ({vm.used // 2**20} / {vm.total // 2**20} MB)"


def gpu() -> str:
    if not shutil.which("nvidia-smi"):
        return "GPU: nvidia-smi nicht gefunden"
    fields = "utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw"
    try:
        out = subprocess.run(
            ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"GPU: Abfrage fehlgeschlagen ({exc})"
    lines = []
    for row in out.splitlines():
        util, mem_u, mem_t, temp, power = [x.strip() for x in row.split(",")]
        lines.append(f"GPU {util:>3}%   VRAM {mem_u}/{mem_t} MB   {temp}°C   {power} W")
    return "\n".join(lines) or "GPU: keine Daten"


def snapshot() -> str:
    return cpu_ram() + "\n" + gpu()


def main() -> None:
    if "--once" in sys.argv:
        print(snapshot())
        return
    try:
        while True:
            print("\033[2J\033[H", end="")  # Bildschirm löschen
            print("NERO QUANTUM – Monitoring (Strg+C beendet)\n")
            print(snapshot())
            time.sleep(2)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
