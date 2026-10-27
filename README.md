# PS4 Game Tracker für Home Assistant

Benutzerdefinierte Home-Assistant-Integration zur Erfassung von PlayStation-4-Spielsitzungen und Spielzeiten – mit einer optionalen Dashboardvorlage.

> **Vorabversion.** Installation, Bildbereitstellung, Helferübernahme, Spielwechsel, Wiederherstellung nach Neustarts und der Umgang mit vorübergehender Nichterreichbarkeit wurden in einer Home-Assistant-Installation praktisch erprobt. Die abschließende Prüfung der Zeitraumwechsel und Zeitumstellungen steht noch aus. Alte Erfassungs- und Reset-Automationen nach der Übernahme deaktivieren; Helfer zunächst aufbewahren.

## Funktionsumfang

- Einrichtung über die Benutzeroberfläche von Home Assistant
- Auswahl eines vorhandenen PS4-Mediaplayers
- Spielzeit für heute, die aktuelle Woche, den aktuellen Monat und das aktuelle Jahr
- Anzeige des letzten Spiels und der letzten Spieldauer
- Spielverlauf
- Binärsensor für eine aktive Spielsitzung
- Speicherung laufender Sitzungen im Minutentakt
- Wiederherstellung gespeicherter Spielzeit nach einem Neustart
- Abgleich mit dem aktuellen Zustand des Mediaplayers
- Sofortige Zeitpause bei unbekanntem Status und verzögerter Sitzungsabschluss
- Aufteilung der Spielzeit an Tages-, Wochen-, Monats- und Jahresgrenzen
- Mitgeliefertes Platzhalterbild
- Dashboardvorlage mit neutralen Beispiel-Entitäten
- HACS-Metadaten und automatisierte Regressionstests mit pytest und GitHub Actions

Zeiten, in denen Home Assistant ausgeschaltet ist, werden **nicht mitgezählt**.

Die optionale Übernahme vorhandener Helfer ist bei der ersten Einrichtung möglich und wurde in einer laufenden Home-Assistant-Installation erfolgreich getestet. Weitere Konfigurationen können von der getesteten Umgebung abweichen.

## Voraussetzungen

- Ein vorhandener PS4-Mediaplayer in Home Assistant
- Für die optionale Dashboardvorlage:
  - Mushroom
  - vertical-stack-in-card
  - card-mod für die zusätzliche Gestaltung
  - Optional: eine PlayStation-Network-(PSN-)Integration, die Trophäen-Sensoren und gegebenenfalls das Spielcover über den ausgewählten Mediaplayer bereitstellt

Die Integration wertet den Zustand des ausgewählten Mediaplayers aus. Sie ersetzt nicht die zugrunde liegende PlayStation-4-Integration.

## Manuelle Installation zum Testen

1. Das Repository als ZIP-Datei herunterladen und entpacken.
2. Den vollständigen Ordner `custom_components/ps4_game_tracker` einschließlich des Unterordners `www` nach `/config/custom_components/` kopieren.
3. Home Assistant neu starten.
4. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach **PS4 Game Tracker** suchen.
5. Den vorhandenen PS4-Mediaplayer auswählen. Ein bestimmter Entitätsname ist nicht erforderlich.
6. Die erzeugten Entitäts-IDs unter **Entwicklerwerkzeuge → Zustände** prüfen.
7. Bei Bedarf die nachfolgend beschriebene Dashboardvorlage hinzufügen.

Die Datei `__init__.py` muss nach dem Kopieren unter folgendem Pfad liegen:

```text
/config/custom_components/ps4_game_tracker/__init__.py
```

Bestehende PS4-Automationen und Helfer während der Testphase beibehalten.

## Einmalige Übernahme bisheriger Helfer

Bei der ersten Einrichtung kann **Bisherige Helfer einmalig übernehmen** aktiviert werden. Anschließend die Helfer für heute, Woche, Monat, Jahr, letzte Spieldauer, letztes Spiel, Spielverlauf und letztes Spielende auswählen. Es sind keine festgelegten Entitätsnamen erforderlich.

Vor dem Import jede Spielsitzung beenden und warten, bis die bisherigen Automationen ihre Helfer aktualisiert haben. Alle Spielzeiten müssen in **Minuten** vorliegen. Das letzte Spielende muss Datum und Uhrzeit enthalten. Die Einrichtung lehnt unbekannte, nicht verfügbare, negative und nicht endliche Zahlenwerte ab. Bei einem Mediaplayer im Zustand `playing` ist der Import gesperrt; zusätzlich muss bestätigt werden, dass keine Sitzung läuft. `unknown` ist kein Nachweis einer ausgeschalteten Konsole.

Die aktuellen Helferwerte werden beim Abschluss der Einrichtung erfasst. Die bisherigen Helfer und Automationen werden weder verändert noch deaktiviert.

- Jede Zeitraum-Summe wird separat als Startwert übernommen und nur zur neuen Spielzeit desselben Zeitraums addiert. Die vier Summen werden nicht miteinander addiert.
- Der jeweilige Startwert entfällt beim nächsten lokalen Tages-, Wochen-, Monats- bzw. Jahreswechsel. Eine rückwirkende Verteilung auf einzelne Tage ist aus Summen nicht möglich.
- Letztes Spiel und letzte Spieldauer werden übernommen und nach der ersten neu abgeschlossenen Sitzung durch deren Werte ersetzt.
- Der alte Spielverlauf wird unverändert im Attribut `legacy_history` des Spielverlauf-Sensors aufbewahrt. Er wird nicht in einzelne Sitzungen umgerechnet oder zur Spielzeit addiert.
- `legacy_imported_at` und `legacy_last_end` dokumentieren den Übernahmezeitpunkt und das bisherige Spielende.
- Die Sitzungsanzahl zählt nur neu erfasste Sitzungen.
- Ein dauerhafter Initialisierungsstand verhindert einen erneuten Import bei Neustarts. Bereits vorhandene Tracker-Speicherstände werden nicht nachträglich importiert oder überschrieben.

Die Übernahme ist für die **erste Einrichtung** vorgesehen. Ein nachträglicher Import in einen bereits verwendeten Tracker und die Migration der Recorder-Historie werden nicht unterstützt. Die Integration zum erneuten Import nicht löschen und neu anlegen: Dadurch könnte eine zweite, unabhängige Statistik entstehen.

## Dashboardvorlage

[Dashboard-YAML öffnen](https://github.com/TheBrain26/ha-ps4-game-tracker/blob/main/dashboard/ps4-dashboard.yaml)

Die Vorlage ist ein Beispiel und wird von der Integration **nicht automatisch eingerichtet**.

Benötigt werden Mushroom und vertical-stack-in-card. Für die zusätzliche Gestaltung wird card-mod verwendet. Auto-entities ist nicht erforderlich.

Vor der Verwendung:

1. Alle Vorkommen von `media_player.deine_ps4` durch die eigene PS4-Mediaplayer-Entität ersetzen.
2. Die Entitäts-IDs `sensor.ps4_game_tracker_...` mit den tatsächlich erzeugten Entitäten der eigenen Installation abgleichen.
3. Auch `binary_sensor.ps4_game_tracker_spiel_aktiv` mit der eigenen Entität abgleichen.
4. Die vier Beispiel-Entitäten `sensor.deine_ps4_..._trophaen` durch eigene Trophäen-Sensoren ersetzen oder den optionalen Trophäen-Block entfernen.

**Optionale PlayStation-Network-Integration:** Für die Trophäenanzeige wird zusätzlich eine passende PlayStation-Network-(PSN-)Integration benötigt, die die vier Trophäen-Sensoren bereitstellt. Das Spielcover wird in der Dashboardvorlage aus dem Attribut `entity_picture` des ausgewählten PS4-Mediaplayers geladen. Dieses Attribut muss vom Mediaplayer bzw. seiner zugrunde liegenden Integration bereitgestellt werden; falls es fehlt, wird das Platzhalterbild angezeigt. Die PS4-Game-Tracker-Integration selbst liefert weder Trophäen noch Spielcover. **Die Spielzeiterfassung funktioniert unabhängig davon.**

Trophäen-Sensoren werden vom PS4 Game Tracker nicht bereitgestellt. Die Vorlage enthält keine persönlichen Wanstebude-Entitätsnamen. Das Platzhalterbild wird unter `/ps4_game_tracker/ps4_platzhalter.png` mitgeliefert. Die Anzeige der fünf Sitzungen begrenzt nur das Dashboard; der Sensor stellt die letzten 20 von maximal 2.000 gespeicherten Sitzungen bereit.

Das Dashboard zeigt:

- Ein Platzhalterbild, wenn der Tracker kein aktives Spiel meldet
- Das Spielcover und den Spieltitel während des Spielens
- Die Spielzeit für heute, diese Woche, diesen Monat und dieses Jahr
- Die letzte Spieldauer
- Das letzte Spiel
- Die letzten fünf abgeschlossenen Sitzungen, neueste zuerst, kompakt mit `|` getrennt; Uhrzeiten lokal und Spielzeiten ohne Nachkommastellen
- Optional die Anzahl der Trophäen

### Vorschau

![Vorschau des PS4-Game-Tracker-Dashboards](https://raw.githubusercontent.com/TheBrain26/ha-ps4-game-tracker/main/dashboard/preview.png)

## Bilder

Im Repository sind folgende Bilder enthalten:

- `custom_components/ps4_game_tracker/www/ps4_platzhalter.png` – Platzhalterbild
- `dashboard/preview.png` – Vorschau der Dashboardkarte

Beim Laden der Integration wird der mitgelieferte Ordner `www` unter folgendem URL-Pfad bereitgestellt:

```text
/ps4_game_tracker
```

Die Dashboardvorlage verwendet diesen Bildpfad:

```yaml
image: /ps4_game_tracker/ps4_platzhalter.png
```

Ein zusätzliches Kopieren des Bildes nach `/config/www/` ist dafür nicht erforderlich.

Der Dateiname muss exakt `ps4_platzhalter.png` lauten. Die Bildbereitstellung wurde im laufenden Home-Assistant-Betrieb erfolgreich getestet.

## Erfassung von Spielsitzungen

Eine laufende Spielsitzung wird im Minutentakt gespeichert.

Nach einem Neustart wird die zuletzt gespeicherte Sitzung bis zum letzten Speicherzeitpunkt als abgeschlossene Sitzung übernommen. Die Zeit zwischen diesem Speicherzeitpunkt und dem Neustart wird nicht nachträglich ergänzt.

Befindet sich der ausgewählte Mediaplayer beim Laden des Trackers im Zustand `playing`, beginnt ab diesem Zeitpunkt eine neue Sitzung.

Der Tracker verwendet für die Erfassung den Zustand `playing` und das Attribut `media_title` des ausgewählten Mediaplayers.

Bei `unknown`, `unavailable` oder fehlendem Player wird die Spielzeit sofort eingefroren und „Spiel aktiv“ ausgeschaltet. Nach 60 Sekunden wird beim nächsten Minutencheck die Sitzung zum Unterbrechungszeitpunkt abgeschlossen. Bei Wiederverbindung beginnt eine neue Sitzung; kurze Abbrüche können mehrere Einträge erzeugen. Die Unterbrechung wird nicht mitgezählt.

Überschreitet eine Sitzung eine lokale Tages-, Wochen-, Monats- oder Jahresgrenze, wird die Spielzeit auf die jeweiligen Zeiträume aufgeteilt.

## Abgeschlossen und geprüft

- Installation und Bildbereitstellung im laufenden Home-Assistant-Betrieb
- Wiederherstellung nach Neustarts, Spielwechsel und vorübergehender Nichterreichbarkeit
- Kompatibilität mit der getesteten Home-Assistant-Installation und HACS
- Einmalige Übernahme vorhandener Helferwerte in einer laufenden Home-Assistant-Installation
- Bereitstellung einer manuellen YAML-Dashboardvorlage; keine automatische Dashboard-Einrichtung vorgesehen
- PSN-Trophäen und Spielcover über eine separate PlayStation-Network-Integration; keine automatische Sensorauswahl vorgesehen
- Herkunft des selbst generierten Platzhalterbilds geklärt; für weitere mitgelieferte Bildinhalte gelten gegebenenfalls eigene Rechte
- Automatisierte Regressionstests mit pytest und GitHub Actions eingerichtet

## Noch offen vor einer stabilen Veröffentlichung

- [ ] **Zeitraumwechsel prüfen:** Spielzeitberechnung über Mitternacht, Wochen- und Monatswechsel sowie Sommer-/Winterzeit im Praxisbetrieb verifizieren. Der nächste gemeinsame Praxistest ist für den **2. November 2026** vorgesehen.

## Rechtlicher Hinweis

Inoffizielles Community-Projekt. Es besteht keine Verbindung zu Sony Interactive Entertainment.

