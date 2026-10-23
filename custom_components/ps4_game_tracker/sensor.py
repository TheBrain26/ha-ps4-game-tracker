"""Playtime and history sensors."""
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTime
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN

PERIODS = {"today": "Heute", "week": "Woche", "month": "Monat", "year": "Jahr"}

async def async_setup_entry(hass, entry, async_add_entities):
    tracker = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [PlaytimeSensor(tracker, key, label) for key, label in PERIODS.items()]
        + [LastGameSensor(tracker), LastDurationSensor(tracker), HistorySensor(tracker)]
    )

class BaseSensor(SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, tracker, key, label):
        self.tracker = tracker
        self._attr_unique_id = f"{tracker.entry.entry_id}_{key}"
        self._attr_name = label
        self._attr_suggested_object_id = f"ps4_game_tracker_{key if key not in PERIODS else 'spielzeit_' + {'today': 'heute', 'week': 'woche', 'month': 'monat', 'year': 'jahr'}[key]}"
        self._attr_should_poll = False

    async def async_added_to_hass(self):
        self.tracker.listeners.append(self.async_write_ha_state)
        self.async_on_remove(lambda: self.tracker.listeners.remove(self.async_write_ha_state))
        unsub = async_track_time_interval(
            self.hass, lambda _: self.async_write_ha_state(), timedelta(minutes=1)
        )
        self.async_on_remove(unsub)

class PlaytimeSensor(BaseSensor):
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:timer-outline"
    def __init__(self, tracker, key, label):
        super().__init__(tracker, key, f"Spielzeit {label}")
        self.period = key
    @property
    def native_value(self):
        return self.tracker.minutes(self.period)

class LastGameSensor(BaseSensor):
    _attr_icon = "mdi:gamepad-variant"
    def __init__(self, tracker):
        super().__init__(tracker, "letztes_spiel", "Letztes Spiel")
    @property
    def native_value(self):
        return self.tracker.sessions[-1]["title"] if self.tracker.sessions else "Kein Spiel erfasst"

class LastDurationSensor(BaseSensor):
    _attr_icon = "mdi:timer"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    def __init__(self, tracker):
        super().__init__(tracker, "letzte_spieldauer", "Letzte Spieldauer")
    @property
    def native_value(self):
        return round(self.tracker.sessions[-1]["minutes"], 1) if self.tracker.sessions else 0

class HistorySensor(BaseSensor):
    _attr_icon = "mdi:history"
    def __init__(self, tracker):
        super().__init__(tracker, "spielverlauf", "Spielverlauf")
    @property
    def native_value(self):
        return f"{len(self.tracker.sessions)} Sitzungen"
    @property
    def extra_state_attributes(self):
        return {"sessions": self.tracker.sessions[-20:]}
