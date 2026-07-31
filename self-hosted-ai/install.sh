#!/usr/bin/env bash
# =====================================================================
#  NERO QUANTUM – Installer mit Modell-Auswahl (Linux / macOS)
#  Waehle ein oder mehrere Modelle. In der Oberflaeche schaltest du
#  danach jederzeit zwischen allen installierten Modellen um.
# =====================================================================
set -euo pipefail
cd "$(dirname "$0")"

# Kuratiertes Menue (klar legitime Modelle). Eigene/uncensored Modelle
# fuegst du ueber Punkt [C] als Ollama- oder HuggingFace-GGUF-Namen hinzu.
declare -a NAME=(
  "qwen2.5-coder:32b"
  "qwen2.5-coder:14b"
  "dolphin-mixtral:latest"
  "dolphin3:latest"
  "deepseek-r1:14b"
  "llama3.1:8b"
)
declare -a DESC=(
  "Coder & Allrounder, stark bei komplexen Tasks (Standard)"
  "Coder, schneller, komplett in VRAM"
  "Dolphin (uncensored) Allrounder, MoE"
  "Dolphin 3.0 (uncensored), klein & schnell"
  "Reasoning / Planung"
  "Allrounder, schnell"
)

echo ""
echo "  =============================================="
echo "        N E R O   Q U A N T U M   –  Setup"
echo "  =============================================="
echo ""
echo "  Verfuegbare Modelle:"
for i in "${!NAME[@]}"; do
  printf "   [%d] %-24s %s\n" "$((i+1))" "${NAME[$i]}" "${DESC[$i]}"
done
echo "   [C] Eigenes Modell (Ollama-Name  oder  hf.co/USER/REPO:QUANT fuer HuggingFace-GGUF)"
echo ""
echo "  Auswahl (Zahlen mit Leerzeichen, z. B. '1 3'). Enter = nur [1] Standard:"
read -r -p "  > " CHOICE
CHOICE="${CHOICE:-1}"

SELECTED=()
for token in $CHOICE; do
  if [[ "$token" =~ ^[Cc]$ ]]; then
    read -r -p "  Eigener Modellname: " CUSTOM
    [[ -n "$CUSTOM" ]] && SELECTED+=("$CUSTOM")
  elif [[ "$token" =~ ^[0-9]+$ ]] && (( token >= 1 && token <= ${#NAME[@]} )); then
    SELECTED+=("${NAME[$((token-1))]}")
  else
    echo "  [i] Ignoriere ungueltige Eingabe: $token"
  fi
done
[[ ${#SELECTED[@]} -eq 0 ]] && SELECTED=("qwen2.5-coder:32b")

echo ""
echo "  Ausgewaehlt: ${SELECTED[*]}"
echo ""

# Docker pruefen
if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  echo "  [!] Docker / 'docker compose' fehlt: https://docs.docker.com/get-docker/"
  exit 1
fi

# GPU-Hinweis
if docker run --rm --gpus all ubuntu nvidia-smi >/dev/null 2>&1; then
  echo "  [ok] GPU erkannt."
else
  echo "  [i] Keine GPU im Docker sichtbar -> laeuft auf CPU (langsam)."
fi

# Stack starten
echo "  [*] Starte Dienste ..."
docker compose up -d

echo "  [*] Warte auf Ollama ..."
for _ in $(seq 1 60); do
  docker exec ollama ollama list >/dev/null 2>&1 && break
  sleep 2
done

# Alle gewaehlten Modelle laden
for m in "${SELECTED[@]}"; do
  echo "  [*] Lade Modell: $m ..."
  docker exec ollama ollama pull "$m" || echo "  [!] Konnte $m nicht laden (Name pruefen)."
done

echo ""
echo "  =============================================="
echo "   NERO QUANTUM laeuft.  ->  http://localhost:3000"
echo "   Websuche:                 http://localhost:8888"
echo "   Installierte Modelle waehlst du oben in der Oberflaeche per Dropdown."
echo "   Standardmodell des Agenten: agent/config.py -> MODEL"
echo "   Stoppen:  docker compose down"
echo "  =============================================="
echo ""
