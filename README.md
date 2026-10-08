# Wolkensprung

Ein eigenes kleines Jump-and-Run mit drei Leveln, Gegnern, Sprungplattformen,
Münzen, Checkpoints und einer Zielflagge. Grafik wird direkt gezeichnet; es
werden keine Nintendo-Dateien oder externen Assets benötigt.

## Windows

1. Python 3.12 oder neuer von https://www.python.org installieren (mit Python Launcher).
2. `start.bat` doppelklicken. Beim ersten Start ist Internet für pygame erforderlich.
3. Mit Enter starten.

Eine eigenständige Windows-Datei lässt sich **auf Windows** mit
`build_windows.bat` erstellen: `dist/Wolkensprung.exe`. Danach benötigt das
Spiel auf dem Zielrechner keine Python-Installation. Die EXE wurde hier unter
Linux nicht gebaut oder auf Windows getestet.

## Steuerung

- A/D oder Pfeiltasten: laufen
- Leertaste, W oder Pfeil hoch: springen (kurz halten für kleine Sprünge)
- Shift: schneller laufen
- P: Pause
- R: Spiel neu starten
- Enter: starten / nächstes Level
- Escape: beenden

Springe auf Gegner, sammle Münzen und erreiche die Flagge. Jeder neue Level
füllt die drei Leben auf. Ein orangefarbener Pfosten aktiviert den Checkpoint.

## Entwicklung

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python game.py
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python game.py --smoke-test
```

Unter Windows heißt der Interpreter `.venv\Scripts\python.exe`.
