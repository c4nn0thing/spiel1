# Wolkensprung

Ein eigenes Jump-and-Run mit zehn unterschiedlichen, zunehmend längeren Leveln,
einem rundlichen Rentner mit Brille, weißem Haar und Strickjacke,
Wandsprüngen, drei Wurfgegenständen, Farbverläufen, Hintergrundebenen, Partikeleffekten,
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
- An einer Wand in der Luft erneut springen: Wandsprung. Gegen die Wand halten
  bremst den Fall; beim Absprung wirst du kurz von der Wand weggeschoben.
- Shift: schneller laufen
- J oder X halten: Gegenstand werfen, in Blickrichtung
- 1: Hausschuh (schneller gerader Schuss)
- 2: Konservendose (Wurfbogen; platzt bei Kontakt mit Boden, Wand oder Gegner,
  trifft auch Gegner im Umkreis von 70 Pixeln)
- 3: Gehstock (kehrt zurück, durchdringt Wände und kann mehrere Gegner treffen)
- Q: nächsten Gegenstand auswählen
- P: Pause
- R: Spiel neu starten
- Enter: starten / nächstes Level
- Escape: beenden

Springe auf normale Gegner, sammle Münzen und erreiche die Flagge. Ab Level 3
gibt es Bodenstacheln, ab Level 4 bewegliche Bonusplattformen und ab Level 6
gepanzerte Gegner: Nicht auf sie treten! Zwei Treffer mit Hausschuh/Gehstock
oder eine Dose besiegen sie. Alle Gegenstände haben unbegrenzte Munition,
aber unterschiedliche Abklingzeiten. Mauern lassen sich mit Wandsprüngen erklimmen.
Shift gedrückt halten für größere Sprünge über die Schluchten.
Jeder neue Level füllt die vier Leben auf. Zwei orangefarbene Pfosten aktivieren
Checkpoints. Nach einem Game Over startet Enter nur den aktuellen Level neu;
R setzt die gesamte Reise zurück. Die Strecken wachsen von 4.800 auf 9.120 Pixel.

Die zehn Welten: Sonnenwiese, Pilzpfad, Bernsteinküste, Windige Höhen,
Dämmerwald, Kristalltal, Frostpass, Sternenschlucht, Glutberge, Himmelsfestung.

Der Smoke-Test prüft Spielmechanik, Wandsprünge, Waffen, Rendering aller Welten
und die physikalische Erreichbarkeit aller 113 Sprünge über Bodenlücken.
Er ersetzt keinen vollständigen
menschlichen Spieldurchlauf und keinen Windows-Test.

## Entwicklung

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python game.py
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python game.py --smoke-test
```

Unter Windows heißt der Interpreter `.venv\Scripts\python.exe`.

## Performance

Figuren, Gegner, Münzen, Gelände, Hintergrundebenen und häufige Texte werden
vorab gezeichnet bzw. zwischengespeichert. Objekte außerhalb des Bildschirms
werden beim Zeichnen übersprungen. Die Physik läuft mit festen Schritten von
1/60 Sekunde und holt kurze Frame-Einbrüche nach. Geschosse sind auf 24
gleichzeitige Objekte begrenzt und werden nach spätestens zwei Sekunden entfernt.

Ein reproduzierbarer Zeichenbenchmark für Level 10:

```sh
.venv/bin/python benchmark.py
```

Er misst die Zeichenzeit ohne FPS-Begrenzung mit dem SDL-Dummy-Treiber.
Das ist keine Vorhersage der Bildrate auf einem Windows-PC.

Beim Vergleich mit Version `25ea85b` in derselben Linux-Cloud-Umgebung
(drei abwechselnde Läufe pro Version, je 600 Bilder nach 60 Aufwärmbildern)
sank die mittlere Zeichenzeit über die drei Läufe von etwa 4,23 auf 2,74 ms
(rund 35 %). Einzelne Läufe schwanken durch die Auslastung der Cloud-Maschine.
