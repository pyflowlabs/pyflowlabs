# =====================================================================
#  NERO QUANTUM - Ein-Datei-Installer (Windows / PowerShell)
#  Rechtsklick -> "Mit PowerShell ausfuehren", oder:  ./install.ps1
# =====================================================================
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$Model = if ($env:NERO_MODEL) { $env:NERO_MODEL } else { "qwen2.5-coder:32b" }

Write-Host ""
Write-Host "  =============================================="
Write-Host "        N E R O   Q U A N T U M   -  Setup"
Write-Host "  =============================================="
Write-Host ""

# 1) Docker vorhanden?
try { docker version | Out-Null }
catch {
  Write-Host "  [!] Docker fehlt oder Docker Desktop laeuft nicht."
  Write-Host "      Installieren/Starten: https://www.docker.com/products/docker-desktop/"
  exit 1
}

# 2) GPU-Hinweis (nicht blockierend)
try {
  docker run --rm --gpus all ubuntu nvidia-smi | Out-Null
  Write-Host "  [ok] GPU erkannt - Modell laeuft auf der RTX."
} catch {
  Write-Host "  [i] Keine GPU im Docker sichtbar. Laeuft dann auf der CPU (langsamer)."
  Write-Host "      Pruefe: aktueller NVIDIA-Treiber + Docker Desktop (WSL2)."
}

# 3) Stack starten
Write-Host "  [*] Starte Dienste (ollama, nero-quantum, searxng) ..."
docker compose up -d

# 4) Auf Ollama warten
Write-Host "  [*] Warte auf Ollama ..."
for ($i = 0; $i -lt 60; $i++) {
  try { docker exec ollama ollama list | Out-Null; break } catch { Start-Sleep -Seconds 2 }
}

# 5) Modell laden (einmalig)
Write-Host "  [*] Lade Modell: $Model  (einmalig, kann dauern) ..."
docker exec ollama ollama pull $Model

Write-Host ""
Write-Host "  =============================================="
Write-Host "   NERO QUANTUM laeuft."
Write-Host "   Oberflaeche:  http://localhost:3000"
Write-Host "   Websuche:     http://localhost:8888"
Write-Host "   Modell:       $Model"
Write-Host ""
Write-Host "   Beim ersten Oeffnen ein lokales Konto anlegen."
Write-Host "   Stoppen:  docker compose down"
Write-Host "  =============================================="
Write-Host ""
