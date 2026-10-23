"""PS4 Game Tracker: session tracking from an existing media player."""
from __future__ import annotations
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util
from .const import DOMAIN, CONF_MEDIA_PLAYER

PLATFORMS = ["sensor", "binary_sensor"]

class Tracker:
    def __init__(self, hass, entry):
        self.hass, self.entry = hass, entry
        self.entity_id = entry.data[CONF_MEDIA_PLAYER]
        self.store = Store(hass, 1, f"{DOMAIN}_{entry.entry_id}")
        self.sessions, self.active, self.listeners = [], None, []
        self.unsub = None
        self._transition_lock = __import__("asyncio").Lock()

    async def load(self):
        self.sessions = (await self.store.async_load() or {}).get("sessions", [])
        self.active = None
        state = self.hass.states.get(self.entity_id)
        if state and state.state == "playing":
            self.start(state.attributes.get("media_title") or "Unbekanntes Spiel")
        self.unsub = async_track_state_change_event(self.hass, [self.entity_id], self.on_change)

    def start(self, title):
        self.active = {"title": title, "start": dt_util.utcnow().isoformat()}
        self.notify()

    async def finish(self):
        if not self.active:
            return
        start = datetime.fromisoformat(self.active["start"])
        end = dt_util.utcnow()
        self.sessions.append({"title": self.active["title"], "start": start.isoformat(),
                              "end": end.isoformat(), "minutes": round(max(0, (end-start).total_seconds())/60, 2)})
        self.sessions = self.sessions[-2000:]
        self.active = None
        await self.store.async_save({"sessions": self.sessions})
        self.notify()

    @callback
    def on_change(self, event):
        state = event.data.get("new_state")
        if state and state.state == "playing":
            title = state.attributes.get("media_title") or "Unbekanntes Spiel"
            if self.active and self.active["title"] == title:
                return
            if self.active:
                self.hass.async_create_task(self.switch(title))
            else:
                self.start(title)
        elif self.active:
            self.hass.async_create_task(self.finish_locked())
        else:
            self.notify()

    async def finish_locked(self):
        async with self._transition_lock:
            await self.finish()

    async def switch(self, title):
        async with self._transition_lock:
            if self.active and self.active["title"] == title:
                return
            if self.active:
                await self.finish()
            self.start(title)

    def notify(self):
        for listener in list(self.listeners):
            listener()

    def minutes(self, period):
        """Sum overlapping session time, clipping at the local period boundary.

        Calculate overlaps in UTC so daylight-saving transitions are handled
        correctly. Sessions spanning midnight are counted in both periods.
        """
        now_local = dt_util.now()
        today = now_local.date()
        if period == "today":
            first = today
        elif period == "week":
            first = today - timedelta(days=today.weekday())
        elif period == "month":
            first = today.replace(day=1)
        elif period == "year":
            first = today.replace(month=1, day=1)
        else:
            return 0

        start_local = dt_util.start_of_local_day(
            datetime.combine(first, datetime.min.time()).replace(
                tzinfo=dt_util.get_default_time_zone()
            )
        )
        boundary = dt_util.as_utc(start_local)
        now_utc = dt_util.utcnow()
        total_seconds = 0.0
        for session in self.sessions:
            started = dt_util.as_utc(datetime.fromisoformat(session["start"]))
            ended = dt_util.as_utc(datetime.fromisoformat(session["end"]))
            total_seconds += max(
                0.0, (min(ended, now_utc) - max(started, boundary)).total_seconds()
            )
        if self.active:
            started = dt_util.as_utc(datetime.fromisoformat(self.active["start"]))
            total_seconds += max(0.0, (now_utc - max(started, boundary)).total_seconds())
        return round(total_seconds / 60, 1)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    tracker = Tracker(hass, entry)
    await tracker.load()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = tracker
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        tracker = hass.data[DOMAIN].pop(entry.entry_id)
        if tracker.unsub:
            tracker.unsub()
    return ok
