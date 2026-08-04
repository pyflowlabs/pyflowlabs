@echo off
REM ============================================================
REM  NERO QUANTUM stoppen (Doppelklick)
REM  Faehrt die Dienste herunter (Modelle/Daten bleiben erhalten).
REM ============================================================
cd /d "%~dp0"

echo Stoppe NERO QUANTUM ...
docker compose down
echo Gestoppt. Starten wieder mit nero-start.bat
timeout /t 2 /nobreak >nul
