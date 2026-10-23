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
        now = dt_util.now()
        def key(t):
            if period == "today": return t.date()
            if period == "week": return t.isocalendar()[:2]
            if period == "month": return (t.year, t.month)
            return t.year
        total = 0.0
        records = list(self.sessions)
        if self.active:
            records.append({"start": self.active["start"], "end": dt_util.utcnow().isoformat()})
        for session in records:
            start = dt_util.as_local(datetime.fromisoformat(session["start"]))
            end = dt_util.as_local(datetime.fromisoformat(session["end"]))
            cursor = start
            while cursor < end:
                nxt = min(end, cursor + timedelta(minutes=1))
                if key(cursor) == key(now):
                    total += (nxt-cursor).total_seconds()/60
                cursor = nxt
        return round(total, 1)

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
