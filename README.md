# PS4 Game Tracker for Home Assistant

A custom Home Assistant integration for tracking PlayStation 4 gaming sessions and playtime.

> **Status:** Early development (v0.1.0-dev). Not yet tested in Home Assistant. Do not disable your existing working automations until the new integration has been validated.

## Planned features
- Game start, change and end detection from an existing PS4 media player entity
- Daily, weekly, monthly and yearly playtime sensors
- Last played game and last session duration
- Game history
- Current game cover with an offline placeholder image
- Optional PlayStation Network trophy sensors
- Example Lovelace dashboard using Mushroom cards

## Requirements
- Home Assistant with a working PS4 media player entity (for example `media_player.wanstebudeps4_playstation_4`)
- HACS for installation from a custom repository
- Mushroom, vertical-stack-in-card and card-mod for the optional dashboard

## Artwork
The user-supplied God of War themed placeholder image is intended to be included in the repository under `custom_components/ps4_game_tracker/www/ps4_platzhalter.png`. The image is not yet committed to GitHub.

## Development
The initial implementation is being prepared on branch `feature/initial-hacs-integration`. This repository is not yet ready for a public release.

Not affiliated with Sony Interactive Entertainment or the creators of God of War.
