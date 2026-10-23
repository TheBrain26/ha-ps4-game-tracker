# PS4 Game Tracker für Home Assistant

Benutzerdefinierte Home-Assistant-Integration zur Erfassung von PlayStation-4-Spielsitzungen und Spielzeiten – mit einer optionalen Dashboardvorlage.

> **Testversion – noch nicht im laufenden Home-Assistant-Betrieb validiert.** Bestehende PS4-Automationen und Helfer vorerst beibehalten, bis die neue Integration erfolgreich getestet wurde.

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
- Behandlung vorübergehender Zustände wie „unbekannt“ und „nicht verfügbar“, ohne die Sitzung sofort zu beenden
- Aufteilung der Spielzeit an Tages-, Wochen-, Monats- und Jahresgrenzen
- Mitgeliefertes Platzhalterbild
- Dashboardvorlage mit neutralen Beispiel-Entitäten
- HACS-Metadaten und automatische Prüfungen der Python-Syntax und JSON-Dateien

Zeiten, in denen Home Assistant ausgeschaltet ist, werden **nicht mitgezählt**.

Die Übernahme vorhandener Statistikwerte aus bisherigen Helfern ist noch nicht enthalten. Umfassende Integrationstests stehen ebenfalls noch aus.

## Voraussetzungen

- Ein vorhandener PS4-Mediaplayer in Home Assistant
- Für die optionale Dashboardvorlage:
  - Mushroom
  - vertical-stack-in-card
  - card-mod für die zusätzliche Gestaltung

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

## Dashboardvorlage

[Dashboard-YAML öffnen](https://github.com/TheBrain26/ha-ps4-game-tracker/blob/main/dashboard/ps4-dashboard.yaml)

Die Vorlage ist ein Beispiel und wird von der Integration **nicht automatisch eingerichtet**.

Benötigt werden Mushroom und vertical-stack-in-card. Für die zusätzliche Gestaltung wird card-mod verwendet. Auto-entities ist nicht erforderlich.

Vor der Verwendung:

1. Alle Vorkommen von `media_player.deine_ps4` durch die eigene PS4-Mediaplayer-Entität ersetzen.
2. Die Entitäts-IDs `sensor.ps4_game_tracker_...` mit den tatsächlich erzeugten Entitäten der eigenen Installation abgleichen.
3. Die vier Beispiel-Entitäten `sensor.deine_ps4_..._trophaen` durch eigene Trophäen-Sensoren ersetzen oder den optionalen Trophäen-Block entfernen.

Trophäen-Sensoren werden vom PS4 Game Tracker nicht bereitgestellt.

Das Dashboard zeigt:

- Ein Platzhalterbild, wenn der Mediaplayer nicht im Zustand `playing` ist
- Das Spielcover und den Spieltitel während des Spielens
- Die Spielzeit für heute, diese Woche, diesen Monat und dieses Jahr
- Die letzte Spieldauer
- Das letzte Spiel
- Den Spielverlauf
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

Der Dateiname muss exakt `ps4_platzhalter.png` lauten. Die Bildbereitstellung muss noch im laufenden Home-Assistant-Betrieb getestet werden.

## Erfassung von Spielsitzungen

Eine laufende Spielsitzung wird im Minutentakt gespeichert.

Nach einem Neustart wird die zuletzt gespeicherte Sitzung bis zum letzten Speicherzeitpunkt als abgeschlossene Sitzung übernommen. Die Zeit zwischen diesem Speicherzeitpunkt und dem Neustart wird nicht nachträglich ergänzt.

Befindet sich der ausgewählte Mediaplayer beim Laden des Trackers im Zustand `playing`, beginnt ab diesem Zeitpunkt eine neue Sitzung.

Vorübergehende Zustände wie `unknown` oder `unavailable` beenden eine aktive Sitzung nicht sofort. Sobald wieder ein bekannter Zustand vorliegt, gleicht der Tracker die Sitzung mit dem aktuellen Zustand des Mediaplayers ab.

Eine laufende Sitzung kann dadurch auch eine vorübergehende Unterbrechung der Erreichbarkeit enthalten.

Überschreitet eine Sitzung eine lokale Tages-, Wochen-, Monats- oder Jahresgrenze, wird die Spielzeit auf die jeweiligen Zeiträume aufgeteilt.

## Geplant vor einer stabilen Veröffentlichung

- Installation und Bildbereitstellung im laufenden Home-Assistant-Betrieb prüfen
- Wiederherstellung nach Neustarts, Spielwechsel und vorübergehende Nichterreichbarkeit testen
- Spielzeitberechnung über Mitternacht und bei Zeitumstellungen prüfen
- Automatisierte Tests mit Home Assistant ergänzen
- Kompatibilität mit Home Assistant und HACS prüfen
- Nutzungsrechte der mitgelieferten Bilder vor öffentlicher Verbreitung klären
- Automatische Einrichtung einer Dashboardkarte prüfen
- Optionale Auswahl vorhandener PSN-Trophäen-Sensoren prüfen
- Übernahme vorhandener Statistikwerte aus bisherigen Helfern ergänzen

## Rechtlicher Hinweis

Inoffizielles Community-Projekt. Es besteht keine Verbindung zu Sony Interactive Entertainment.
