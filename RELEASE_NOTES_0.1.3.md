# v0.1.3 – Sitzungsende bei unbekanntem PS4-Status

- Spielzeit pausiert sofort bei `unknown`, `unavailable` oder fehlendem Mediaplayer.
- „Spiel aktiv“ wird während der Unterbrechung ausgeschaltet.
- Nach 60 Sekunden anhaltender Unterbrechung wird die Sitzung beim nächsten Minutencheck abgeschlossen, ohne die Wartezeit mitzuzählen.
- Bei Wiederverbindung wird eine neue Sitzung begonnen; dadurch werden unbeobachtete Zeiträume nicht mitgezählt. Kurze Verbindungsabbrüche können mehrere Sitzungseinträge erzeugen.
- Letztes Spiel, letzte Spieldauer und Verlauf aktualisieren sich beim Abschluss.
- Neustart und Deaktivierung verlängern bei unbekanntem Status den gespeicherten Zeitraum nicht weiter.

Validierung: 15 lokale Tests mit simulierten Home-Assistant-Schnittstellen bestanden; Python-Kompilierung und Diff-Prüfung bestanden. Praxistest in Home Assistant steht aus.
