#!/usr/bin/env python3
"""Benchmark (#13): Modelle vergleichen – Geschwindigkeit, Tokens/s, VRAM, Latenz.

Misst pro Modell mit einem festen Prompt:
  - Antwortzeit (Latenz)
  - erzeugte Tokens und Tokens/s (aus Ollamas Metriken)
  - VRAM-Nutzung (nvidia-smi)

CLI:
  python benchmark.py qwen2.5-coder:32b dolphin-mixtral:latest
  python benchmark.py            # nutzt config.MODEL
"""

import shutil
import subprocess
import sys

import config
import logsetup

log, LOG_FILE = logsetup.setup("nero.benchmark")


def tokens_per_sec(response: dict) -> float:
    """Tokens/s aus Ollama-Metriken (eval_count / eval_duration[ns]). Testbar."""
    count = response.get("eval_count") or 0
    dur_ns = response.get("eval_duration") or 0
    if not count or not dur_ns:
        return 0.0
    return count / (dur_ns / 1e9)


def vram_used_mb() -> int:
    if not shutil.which("nvidia-smi"):
        return -1
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip().splitlines()
        return int(out[0]) if out else -1
    except Exception:  # noqa: BLE001
        return -1


def bench_model(model: str) -> dict:
    import time
    import ollama
    client = ollama.Client(host=config.OLLAMA_HOST)
    t0 = time.time()
    resp = client.chat(model=model, messages=[{"role": "user", "content": config.BENCH_PROMPT}])
    latency = time.time() - t0
    return {
        "model": model,
        "latency_s": round(latency, 2),
        "tokens": resp.get("eval_count", 0),
        "tok_per_s": round(tokens_per_sec(resp), 1),
        "vram_mb": vram_used_mb(),
    }


def main() -> None:
    models = sys.argv[1:] or [config.MODEL]
    print(f"Benchmark ({len(models)} Modell(e)). Prompt: {config.BENCH_PROMPT}\n")
    print(f"{'Modell':30} {'Latenz':>8} {'Tokens':>8} {'Tok/s':>8} {'VRAM MB':>9}")
    print("-" * 66)
    for m in models:
        try:
            r = bench_model(m)
            print(f"{r['model']:30} {r['latency_s']:>7}s {r['tokens']:>8} "
                  f"{r['tok_per_s']:>8} {r['vram_mb']:>9}")
        except Exception as exc:  # noqa: BLE001
            log.exception("Benchmark für %s fehlgeschlagen", m)
            print(f"{m:30} FEHLER: {exc}")


if __name__ == "__main__":
    main()
