# =====================================================================
#  NERO QUANTUM - Installer mit Modell-Auswahl (Windows / PowerShell)
#  Waehle ein oder mehrere Modelle. In der Oberflaeche schaltest du
#  danach jederzeit zwischen allen installierten Modellen um.
# =====================================================================
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$Name = @(
  "qwen2.5-coder:32b",
  "qwen2.5-coder:14b",
  "dolphin-mixtral:latest",
  "dolphin3:latest",
  "deepseek-r1:14b",
  "llama3.1:8b"
)
$Desc = @(
  "Coder & Allrounder, stark bei komplexen Tasks (Standard)",
  "Coder, schneller, komplett in VRAM",
  "Dolphin (uncensored) Allrounder, MoE",
  "Dolphin 3.0 (uncensored), klein & schnell",
  "Reasoning / Planung",
  "Allrounder, schnell"
)

Write-Host ""
Write-Host "  =============================================="
Write-Host "        N E R O   Q U A N T U M   -  Setup"
Write-Host "  =============================================="
Write-Host ""
Write-Host "  Verfuegbare Modelle:"
for ($i = 0; $i -lt $Name.Count; $i++) {
  "   [{0}] {1,-24} {2}" -f ($i+1), $Name[$i], $Desc[$i] | Write-Host
}
Write-Host "   [C] Eigenes Modell (Ollama-Name  oder  hf.co/USER/REPO:QUANT fuer HuggingFace-GGUF)"
Write-Host ""
Write-Host "  Auswahl (Zahlen mit Leerzeichen, z. B. '1 3'). Enter = nur [1] Standard:"
$Choice = Read-Host "  >"
if ([string]::IsNullOrWhiteSpace($Choice)) { $Choice = "1" }

$Selected = @()
foreach ($token in ($Choice -split '\s+')) {
  if ($token -match '^[Cc]$') {
    $Custom = Read-Host "  Eigener Modellname"
    if (-not [string]::IsNullOrWhiteSpace($Custom)) { $Selected += $Custom }
  } elseif ($token -match '^[0-9]+$' -and [int]$token -ge 1 -and [int]$token -le $Name.Count) {
    $Selected += $Name[[int]$token - 1]
  } else {
    Write-Host "  [i] Ignoriere ungueltige Eingabe: $token"
  }
}
if ($Selected.Count -eq 0) { $Selected = @("qwen2.5-coder:32b") }

Write-Host ""
Write-Host ("  Ausgewaehlt: " + ($Selected -join ", "))
Write-Host ""

try { docker version | Out-Null } catch {
  Write-Host "  [!] Docker fehlt/laeuft nicht: https://www.docker.com/products/docker-desktop/"; exit 1
}

try { docker run --rm --gpus all ubuntu nvidia-smi | Out-Null; Write-Host "  [ok] GPU erkannt." }
catch { Write-Host "  [i] Keine GPU im Docker sichtbar -> laeuft auf CPU (langsam)." }

Write-Host "  [*] Starte Dienste ..."
docker compose up -d

Write-Host "  [*] Warte auf Ollama ..."
for ($i = 0; $i -lt 60; $i++) {
  try { docker exec ollama ollama list | Out-Null; break } catch { Start-Sleep -Seconds 2 }
}

foreach ($m in $Selected) {
  Write-Host "  [*] Lade Modell: $m ..."
  try { docker exec ollama ollama pull $m } catch { Write-Host "  [!] Konnte $m nicht laden (Name pruefen)." }
}

Write-Host ""
Write-Host "  =============================================="
Write-Host "   NERO QUANTUM laeuft.  ->  http://localhost:3000"
Write-Host "   Websuche:                 http://localhost:8888"
Write-Host "   Modelle waehlst du oben in der Oberflaeche per Dropdown."
Write-Host "   Stoppen:  docker compose down"
Write-Host "  =============================================="
Write-Host ""
