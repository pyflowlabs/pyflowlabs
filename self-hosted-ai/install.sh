#!/usr/bin/env bash
# =====================================================================
#  NERO QUANTUM – Ein-Datei-Installer (Linux / macOS)
#  Startet den kompletten Stack und lädt das Modell. Danach: loslegen.
# =====================================================================
set -euo pipefail
cd "$(dirname "$0")"

MODEL="${NERO_MODEL:-qwen2.5-coder:32b}"

echo ""
echo "  =============================================="
echo "        N E R O   Q U A N T U M   –  Setup"
echo "  =============================================="
echo ""

# 1) Docker vorhanden?
if ! command -v docker >/dev/null 2>&1; then
  echo "  [!] Docker fehlt. Bitte installieren: https://docs.docker.com/get-docker/"
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "  [!] 'docker compose' fehlt. Bitte Docker Compose (Plugin) installieren."
  exit 1
fi

# 2) GPU-Hinweis (nicht blockierend)
if docker run --rm --gpus all ubuntu nvidia-smi >/dev/null 2>&1; then
  echo "  [ok] GPU erkannt – Modell läuft auf der RTX."
else
  echo "  [i] Keine GPU im Docker sichtbar. Läuft dann auf der CPU (deutlich langsamer)."
  echo "      Windows/WSL: NVIDIA-Treiber + Docker Desktop prüfen."
fi

# 3) Stack starten
echo "  [*] Starte Dienste (ollama, nero-quantum, searxng) ..."
docker compose up -d

# 4) Auf Ollama warten
echo "  [*] Warte auf Ollama ..."
for _ in $(seq 1 60); do
  if docker exec ollama ollama list >/dev/null 2>&1; then break; fi
  sleep 2
done

# 5) Modell laden (einmalig)
echo "  [*] Lade Modell: ${MODEL}  (einmalig, kann je nach Größe dauern) ..."
docker exec ollama ollama pull "${MODEL}"

echo ""
echo "  =============================================="
echo "   NERO QUANTUM läuft."
echo "   Oberfläche:  http://localhost:3000"
echo "   Websuche:    http://localhost:8888"
echo "   Modell:      ${MODEL}"
echo ""
echo "   Beim ersten Öffnen ein lokales Konto anlegen."
echo "   Stoppen:  docker compose down"
echo "  =============================================="
echo ""
