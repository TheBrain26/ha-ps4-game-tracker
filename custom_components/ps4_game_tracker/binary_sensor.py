"""Gaming session state."""
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    tracker = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PlayingSensor(tracker)])

class PlayingSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Spiel aktiv"
    _attr_icon = "mdi:gamepad-variant"
    def __init__(self, tracker):
        self.tracker = tracker
        self._attr_unique_id = f"{tracker.entry.entry_id}_playing"
        self._attr_suggested_object_id = "ps4_game_tracker_spiel_aktiv"
    @property
    def is_on(self):
        return self.tracker.active is not None
    async def async_added_to_hass(self):
        self.tracker.listeners.append(self.async_write_ha_state)
        self.async_on_remove(lambda: self.tracker.listeners.remove(self.async_write_ha_state))
