# Wolkensprung

Ein eigenes Jump-and-Run mit zehn unterschiedlichen, zunehmend längeren Leveln,
animierter Spielfigur, Farbverläufen, mehreren Hintergrundebenen, Partikeleffekten,
Münzen, zwei Checkpoints pro Level und einer Zielflagge. Grafik wird direkt gezeichnet; es
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

Springe auf normale Gegner, sammle Münzen und erreiche die Flagge. Ab Level 3
gibt es Bodenstacheln, ab Level 4 bewegliche Bonusplattformen und ab Level 6
gepanzerte Gegner: Diese immer überspringen, nicht auf sie treten!
Shift gedrückt halten für größere Sprünge über die Schluchten.
Jeder neue Level füllt die vier Leben auf. Zwei orangefarbene Pfosten aktivieren
Checkpoints. Nach einem Game Over startet Enter nur den aktuellen Level neu;
R setzt die gesamte Reise zurück. Die Strecken wachsen von 4.800 auf 9.120 Pixel.

Die zehn Welten: Sonnenwiese, Pilzpfad, Bernsteinküste, Windige Höhen,
Dämmerwald, Kristalltal, Frostpass, Sternenschlucht, Glutberge, Himmelsfestung.

Der Smoke-Test prüft Spielmechanik, Rendering aller Welten und die physikalische
Erreichbarkeit aller 113 Pflichtsprünge. Er ersetzt keinen vollständigen
menschlichen Spieldurchlauf und keinen Windows-Test.

## Entwicklung

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python game.py
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python game.py --smoke-test
```

Unter Windows heißt der Interpreter `.venv\Scripts\python.exe`.
