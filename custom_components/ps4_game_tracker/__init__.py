"""PS4 Game Tracker: session tracking from an existing media player."""
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
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
        self._transition_lock = asyncio.Lock()
        self.unsub_checkpoint = None

    async def load(self):
        data = await self.store.async_load() or {}
        self.sessions = data.get("sessions", [])
        self.active = None

        # Recover only time that was actually checkpointed before restart.
        # Never assume that the console kept playing while HA was offline.
        previous = data.get("active")
        if previous and previous.get("start") and previous.get("last_seen"):
            start = datetime.fromisoformat(previous["start"])
            end = datetime.fromisoformat(previous["last_seen"])
            if end > start:
                self.sessions.append({
                    "title": previous.get("title", "Unbekanntes Spiel"),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "minutes": round((end - start).total_seconds() / 60, 2),
                })
                self.sessions = self.sessions[-2000:]
            await self.store.async_save({"sessions": self.sessions, "active": None})

        state = self.hass.states.get(self.entity_id)
        if state and state.state == "playing":
            await self.start(state.attributes.get("media_title") or "Unbekanntes Spiel")
        self.unsub = async_track_state_change_event(
            self.hass, [self.entity_id], self.on_change
        )
        self.unsub_checkpoint = async_track_time_interval(
            self.hass, self.checkpoint, timedelta(minutes=1)
        )

    async def start(self, title):
        now = dt_util.utcnow().isoformat()
        self.active = {"title": title, "start": now, "last_seen": now}
        await self.persist()
        self.notify()

    async def persist(self):
        await self.store.async_save({
            "sessions": self.sessions, "active": self.active
        })

    async def checkpoint(self, _now):
        async with self._transition_lock:
            if self.active:
                self.active["last_seen"] = dt_util.utcnow().isoformat()
                await self.persist()

    async def finish(self):
        if not self.active:
            return
        start = datetime.fromisoformat(self.active["start"])
        end = dt_util.utcnow()
        self.sessions.append({
            "title": self.active["title"],
            "start": start.isoformat(),
            "end": end.isoformat(),
            "minutes": round(max(0, (end - start).total_seconds()) / 60, 2),
        })
        self.sessions = self.sessions[-2000:]
        self.active = None
        await self.persist()
        self.notify()

    @callback
    def on_change(self, event):
        """Queue a reconciliation against the latest media-player state."""
        self.hass.async_create_task(self.reconcile())

    async def reconcile(self):
        """Serialize transitions and inspect the current state under the lock.

        Avoid acting on stale queued events when games change rapidly.
        An unavailable/unknown state is not proof that gameplay ended.
        """
        async with self._transition_lock:
            state = self.hass.states.get(self.entity_id)
            if state is None or state.state in ("unknown", "unavailable"):
                return
            if state.state == "playing":
                title = state.attributes.get("media_title") or "Unbekanntes Spiel"
                if self.active and self.active["title"] == title:
                    return
                if self.active:
                    await self.finish()
                await self.start(title)
            elif self.active:
                await self.finish()
            else:
                self.notify()

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

        start_local = datetime.combine(first, datetime.min.time()).replace(
            tzinfo=dt_util.get_default_time_zone()
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
        if tracker.unsub_checkpoint:
            tracker.unsub_checkpoint()
        async with tracker._transition_lock:
            if tracker.active:
                tracker.active["last_seen"] = dt_util.utcnow().isoformat()
                await tracker.persist()
    return ok
