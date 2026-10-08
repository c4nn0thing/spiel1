@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Bitte Python 3.12 von python.org installieren.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  pause
  exit /b 1
)
.venv\Scripts\python.exe game.py
if errorlevel 1 pause
