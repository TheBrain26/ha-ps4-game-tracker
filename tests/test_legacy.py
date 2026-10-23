"""Focused migration tests; Home Assistant interfaces are stubbed locally."""
import ast
import asyncio
import copy
from datetime import datetime, date, timedelta, timezone
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1] / 'custom_components/ps4_game_tracker'
spec = importlib.util.spec_from_file_location('legacy', ROOT / 'legacy.py')
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)
TZ = ZoneInfo('Europe/Berlin')
NOW = datetime(2026, 10, 23, 22, 0, tzinfo=TZ)
VALUES = dict(today='0', week='11', month='11', year='98', last_duration='7',
              last_game='Stray', history='Stray · 7 min · 19:00 | truncated',
              last_end='2026-10-22 19:00:49')

class MemoryStore:
    def __init__(self, *args):
        self.data = None
    async def async_load(self):
        return copy.deepcopy(self.data)
    async def async_save(self, data):
        self.data = copy.deepcopy(data)

clock = SimpleNamespace(now=lambda: NOW, utcnow=lambda: NOW.astimezone(timezone.utc),
                        as_utc=lambda d: d.astimezone(timezone.utc),
                        get_default_time_zone=lambda: TZ)
tree = ast.parse((ROOT / '__init__.py').read_text())
tracker_node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Tracker')
namespace = dict(asyncio=asyncio, datetime=datetime, timedelta=timedelta,
                 dt_util=clock, Store=MemoryStore, DOMAIN='ps4_game_tracker',
                 CONF_MEDIA_PLAYER='media_player', callback=lambda f:f,
                 baseline_minutes=legacy.baseline_minutes,
                 async_track_state_change_event=lambda *a:lambda:None,
                 async_track_time_interval=lambda *a:lambda:None)
exec(compile(ast.Module(body=[tracker_node], type_ignores=[]), '<tracker>', 'exec'), namespace)
Tracker = namespace['Tracker']

def make_tracker(snapshot=True):
    data = {'media_player':'media_player.test'}
    if snapshot:
        data['legacy_snapshot'] = legacy.snapshot_helpers(VALUES, NOW)
    return Tracker(SimpleNamespace(states=SimpleNamespace(get=lambda _:None)),
                   SimpleNamespace(entry_id='test', data=data))

class SnapshotTests(unittest.TestCase):
    def test_totals_not_summed_across_periods(self):
        s = legacy.snapshot_helpers(VALUES, NOW)
        self.assertEqual([legacy.baseline_minutes(s, NOW.date(), p)
                         for p in legacy.PERIOD_KEYS], [0,11,11,98])
        self.assertEqual(s['history'], VALUES['history'])
    def test_period_expiry_and_year_boundary(self):
        s = legacy.snapshot_helpers(VALUES, NOW)
        self.assertEqual(legacy.baseline_minutes(s,date(2026,10,26),'week'),0)
        self.assertEqual(legacy.baseline_minutes(s,date(2026,10,26),'month'),11)
        self.assertEqual(legacy.baseline_minutes(s,date(2026,11,1),'month'),0)
        self.assertEqual(legacy.baseline_minutes(s,date(2026,11,1),'year'),98)
        self.assertEqual(legacy.baseline_minutes(s,date(2027,1,1),'year'),0)
    def test_nonzero_day_expires_at_midnight(self):
        s = legacy.snapshot_helpers({**VALUES,'today':'5'}, NOW)
        self.assertEqual(legacy.baseline_minutes(s,date(2026,10,23),'today'),5)
        self.assertEqual(legacy.baseline_minutes(s,date(2026,10,24),'today'),0)
    def test_bad_input_is_rejected_atomically(self):
        for value in ['nan','inf','-1','unknown','unavailable','oops']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                legacy.snapshot_helpers({**VALUES,'year':value},NOW)
        for value in ['2026-10-22','oops','unavailable']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                legacy.snapshot_helpers({**VALUES,'last_end':value},NOW)
        with self.assertRaises(ValueError):
            legacy.snapshot_helpers({},NOW)

class TrackerTests(unittest.IsolatedAsyncioTestCase):
    async def test_restart_retains_baseline_without_double_import(self):
        t = make_tracker(); await t.load()
        self.assertEqual(t.minutes('year'),98)
        self.assertEqual(t.sessions,[])
        t.entry.data['legacy_snapshot']['periods']['year']['minutes']=999
        t2=make_tracker();t2.store.data=copy.deepcopy(t.store.data)
        await t2.load()
        self.assertEqual(t2.minutes('year'),98)
        self.assertEqual(t2.legacy['last_duration'],7)
    async def test_new_sessions_add_once_and_recovery_retains_metadata(self):
        t=make_tracker();await t.load()
        t.active={'title':'New game','start':(NOW-timedelta(minutes=3)).isoformat(),
                  'last_seen':NOW.isoformat()}
        await t.persist()
        await t.load()
        self.assertEqual(t.minutes('today'),3)
        self.assertEqual(t.minutes('week'),14)
        self.assertEqual(t.minutes('year'),101)
        self.assertEqual(len(t.sessions),1)
        self.assertEqual(t.store.data['legacy']['last_game'],'Stray')
        await t.load()
        self.assertEqual(t.minutes('year'),101)
        self.assertEqual(len(t.sessions),1)
    async def test_existing_store_never_receives_legacy_snapshot(self):
        t=make_tracker();t.store.data={'sessions':[],'active':None}
        await t.load()
        self.assertEqual(t.legacy,{})
        self.assertEqual(t.minutes('year'),0)
    async def test_opt_out(self):
        t=make_tracker(False);await t.load()
        self.assertEqual(t.minutes('year'),0)
        self.assertTrue(t.store.data['initialized'])

# Exercise config-flow control paths without installing Home Assistant.
class FakeFlow:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
    async def async_set_unique_id(self, value):
        self.unique_id = value
    def _abort_if_unique_id_configured(self):
        pass
    def async_create_entry(self, **kwargs):
        return {"type":"create_entry", **kwargs}
    def async_show_form(self, **kwargs):
        return {"type":"form", **kwargs}

flow_tree = ast.parse((ROOT / 'config_flow.py').read_text())
flow_node = next(n for n in flow_tree.body if isinstance(n, ast.ClassDef))
flow_ns = dict(config_entries=SimpleNamespace(ConfigFlow=FakeFlow),
               selector=SimpleNamespace(EntitySelector=lambda x:x, EntitySelectorConfig=lambda **x:x),
               vol=SimpleNamespace(Required=lambda key, **kw:key, Optional=lambda key, **kw:key,
                                   Schema=lambda x:x),
               DOMAIN='ps4_game_tracker', CONF_MEDIA_PLAYER='media_player',
               dt_util=clock, HELPER_DOMAINS=legacy.HELPER_DOMAINS,
               snapshot_helpers=legacy.snapshot_helpers)
exec(compile(ast.Module(body=[flow_node], type_ignores=[]), '<flow>', 'exec'), flow_ns)
Flow=flow_ns['PS4GameTrackerConfigFlow']

class FlowTests(unittest.IsolatedAsyncioTestCase):
    def make_flow(self, player='off', values=None):
        flow=Flow()
        inputs={k:'input.'+k for k in legacy.HELPER_DOMAINS}
        entities={inputs[k]:SimpleNamespace(state=v) for k,v in (values or VALUES).items()}
        entities['media_player.test']=SimpleNamespace(state=player)
        flow.hass=SimpleNamespace(states=SimpleNamespace(get=entities.get))
        return flow, {**inputs, 'console_idle':True}
    async def test_opt_in_snapshots_and_opt_out_skips(self):
        f,fields=self.make_flow()
        result=await f.async_step_user({'media_player':'media_player.test','import_legacy':True})
        self.assertEqual(result['step_id'],'legacy')
        result=await f.async_step_legacy(fields)
        self.assertEqual(result['type'],'create_entry')
        self.assertEqual(result['data']['legacy_snapshot']['periods']['year']['minutes'],98)
        f,_=self.make_flow()
        result=await f.async_step_user({'media_player':'media_player.test'})
        self.assertNotIn('legacy_snapshot',result['data'])
    async def test_active_player_and_missing_confirmation_block_import(self):
        for player,confirmed in [('playing',True),('off',False)]:
            f,fields=self.make_flow(player)
            f._player='media_player.test';fields['console_idle']=confirmed
            result=await f.async_step_legacy(fields)
            self.assertEqual(result['errors']['base'],'console_not_idle')
    async def test_invalid_helper_blocks_entry(self):
        f,fields=self.make_flow(values={**VALUES,'year':'unavailable'})
        f._player='media_player.test'
        result=await f.async_step_legacy(fields)
        self.assertEqual(result['type'],'form')
        self.assertEqual(result['errors']['base'],'missing_helper')

sensor_tree=ast.parse((ROOT / 'sensor.py').read_text())
sensor_ns=dict(SensorEntity=object, UnitOfTime=SimpleNamespace(MINUTES='min'))
exec(compile(ast.Module(body=[n for n in sensor_tree.body if isinstance(n,(ast.ClassDef,ast.Assign))],
                        type_ignores=[]),'<sensors>','exec'),sensor_ns)

class SensorTests(unittest.IsolatedAsyncioTestCase):
    async def test_legacy_last_values_then_new_session_and_history(self):
        t=make_tracker();await t.load()
        last=sensor_ns['LastGameSensor'](t)
        duration=sensor_ns['LastDurationSensor'](t)
        history=sensor_ns['HistorySensor'](t)
        self.assertEqual(last.native_value,'Stray')
        self.assertEqual(duration.native_value,7)
        self.assertEqual(history.native_value,'0 Sitzungen')
        self.assertEqual(history.extra_state_attributes['legacy_history'],VALUES['history'])
        t.sessions.append({'title':'New game','minutes':3})
        self.assertEqual(last.native_value,'New game')
        self.assertEqual(duration.native_value,3)
        self.assertEqual(history.native_value,'1 Sitzungen')

if __name__ == '__main__':
    unittest.main()
