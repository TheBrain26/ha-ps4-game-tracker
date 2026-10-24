# v0.1.4 – Kompaktes Dashboard als öffentliche Vorlage

- Dashboardvorlage auf die aktuellen Tracker-Sensoren umgestellt.
- Maximal fünf abgeschlossene Sitzungen, neueste zuerst, als Fließtext mit `|` und lokaler Uhrzeit.
- Spielzeiten und letzte Spieldauer ohne Nachkommastellen.
- Automatischer Wechsel zwischen mitgeliefertem Platzhalterbild und Spielcover.
- Neutrale Mediaplayer- und Trophäen-Platzhalter statt persönlicher Entitätsnamen; Tracker-IDs vor Verwendung abgleichen.
- README mit Einrichtungshinweisen und Verhalten bei unbekanntem Playerstatus aktualisiert.

Benötigt: Mushroom, vertical-stack-in-card und für die Gestaltung card-mod. Dashboard-YAML unter `dashboard/ps4-dashboard.yaml`; Bild unter `/ps4_game_tracker/ps4_platzhalter.png`, kein zusätzliches Kopieren notwendig. Trophäen-Sensoren sind optional und stammen nicht aus dieser Integration.

Die entsprechende persönliche Dashboardkarte wurde praktisch erprobt; die öffentliche Vorlage muss nach Eintragen der eigenen Entitäten geprüft werden. Sitzungsabschluss kann nach Ausschalten etwa ein bis zwei Minuten dauern.
