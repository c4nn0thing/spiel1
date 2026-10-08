@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller==6.16.0
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m PyInstaller --clean --onefile --windowed --name Wolkensprung game.py
if errorlevel 1 exit /b 1
echo Fertig: dist\Wolkensprung.exe
pause
