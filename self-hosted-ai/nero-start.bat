@echo off
REM ============================================================
REM  NERO QUANTUM starten (Doppelklick)
REM  Startet die Dienste und oeffnet die Oberflaeche im Browser.
REM  Tipp: Rechtsklick -> Verknuepfung erstellen -> auf den Desktop.
REM ============================================================
cd /d "%~dp0"

echo Starte NERO QUANTUM ...
docker compose up -d
if errorlevel 1 (
  echo.
  echo [!] Docker laeuft nicht? Bitte Docker Desktop starten und erneut versuchen.
  pause
  exit /b 1
)

echo Warte kurz, bis alles bereit ist ...
timeout /t 4 /nobreak >nul
start "" http://localhost:3000
echo NERO QUANTUM laeuft: http://localhost:3000
