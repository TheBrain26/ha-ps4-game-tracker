# PS4 Game Tracker for Home Assistant

Custom Home Assistant integration for PlayStation 4 gaming sessions, playtime statistics and an optional Lovelace dashboard.

> **Development preview – not released or tested in a live Home Assistant instance.** Keep your existing PS4 automations and helpers running until the new implementation is validated.

## Status (October 2026)
The development branch contains a basic config flow, playtime and history sensors, a gaming-state binary sensor, HACS metadata, a dashboard example and syntax/JSON CI checks. Active sessions are checkpointed every minute. On restart, the last saved checkpoint is recovered as a completed session; any time while Home Assistant was offline is deliberately **not** counted. Migration of existing statistics and comprehensive integration tests are still outstanding.

## Setup for development testing
1. Copy `custom_components/ps4_game_tracker` into `/config/custom_components/`.
2. Restart Home Assistant and add **PS4 Game Tracker** under Settings → Devices & services → Add integration.
3. Select your existing PS4 media player. No particular entity ID is required.
4. Confirm the generated entity IDs in Developer Tools → States.
5. Use `dashboard/ps4-dashboard.yaml` as an **example**, updating its media-player and sensor entity IDs as needed.

The example dashboard requires Mushroom, vertical-stack-in-card and optionally card-mod. It still contains the original author's media-player ID and is **not automatically configured** by the integration.

## Artwork
Two user-provided images are available in the separately prepared project ZIP:
- `custom_components/ps4_game_tracker/www/ps4_platzhalter.png` – offline placeholder
- `dashboard/preview.png` – dashboard screenshot

**These PNGs have not yet been committed to GitHub.** The dashboard currently refers to `/local/ps4_platzhalter.png?v=2`, so for testing copy the placeholder to Home Assistant's `/config/www/ps4_platzhalter.png`. Automatic serving of bundled assets is planned.

## Planned before release
- Validate restart checkpoint recovery and edge cases in a live Home Assistant test
- Correct recovery and reconciliation of interrupted sessions
- Automated tests against Home Assistant
- Bundled image URL registration and automatic dashboard configuration
- Optional PSN trophy entity selection
- Migration of legacy helper statistics

## Legal
Unofficial community project; not affiliated with Sony Interactive Entertainment.
