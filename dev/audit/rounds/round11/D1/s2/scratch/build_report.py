import json, glob, subprocess, sys, os

ROOT = "dev/audit/rounds/round11/D1/s2"
PY = sys.executable
env = dict(os.environ, PYTHONPATH="tests/hastub")
stores = subprocess.run([PY, "tools/audit/enumerate.py", "d1-stores"], capture_output=True, text=True, env=env).stdout.splitlines()
inputs = subprocess.run([PY, "tools/audit/enumerate.py", "d1-inputs"], capture_output=True, text=True, env=env).stdout.splitlines()
findings = [json.load(open(f)) for f in sorted(glob.glob(f"{ROOT}/findings/*.json"))]
H = lambda n: f"{ROOT}/{n}"  # noqa: E731
harnesses = [H(n) for n in ("d1s2_lib.py", "store_fuzz.py", "nan_boundary.py", "config_fuzz.py", "upgrade_fuzz.py",
                            "clock_save.py", "hold_restore.py", "off_restore_race.py", "boost_settle.py",
                            "staleness.py", "consumers.py", "staleness_unread.py", "pv_stale.py", "price_weather.py",
                            "weather_stuck.py", "presence_dst.py", "booked.py")]
cmd = lambda n, a="": f"PYTHONPATH=tests/hastub python3 {ROOT}/{n}{(' ' + a) if a else ''}"  # noqa: E731
non_findings = [
    {"claim": "Store fuzz: 200 seeded structural mutants per d1-stores store (17 stores, 3400 mutants; boost, manual_plan and away populated with a running hold each) loaded through the real loaders on a real asyncio loop: no loader raise, no cycle failure, no best-effort step failing on both cycles, no non-finite value live, against the healthy control per store",
     "command": cmd("store_fuzz.py", "--n 200 --real-solve 5"),
     "value": "loader_raise=0, cycle_fail=0, repeat_fence=0, log_repeat=0, nonfinite_live=0 for all 17; task_raise=3 (boost, reported as D1-s2-06); log_multi 1-2 per store in ledger/manual_plan/price_model/thermal_learning (see below)"},
    {"claim": "Positive control: the fuzz harness counts a cycle failure and a repeated best-effort failure (round-10 C1's missing control)",
     "command": cmd("store_fuzz.py", "--stores ledger,away --control"),
     "value": "control_ledger_kinds=cycle_fail,repeat_fence; control_away_kinds=cycle_fail,repeat_fence"},
    {"claim": "The one-log-line check is taken against each store's healthy-restart control (templates a healthy load already logs are subtracted -- round-10 C1's confound); the only multi-line case is a far-future ISO string planted in a NON-instant field, which store._bound_instants rewrites and logs as 'stored instant ... ahead of the clock' beside the loader's own quarantine warning: two lines for one leaf, the cycle completes",
     "command": cmd("store_fuzz.py", "--n 200"),
     "value": "log_multi: ledger 1, manual_plan 2 (+2 populated), price_model 2, thermal_learning 1 of 200 each; 0 elsewhere"},
    {"claim": "Previous-version records load and migrate: LEDGER v1->2 and defrost v1->2, healthy and 200 seeded mutants each, no loader raise, cycle failure or repeat",
     "command": cmd("upgrade_fuzz.py"),
     "value": "ledger: all kinds 0 except log_multi=1 (the instant_far case above); defrost: all 0"},
    {"claim": "A writer clock 48 h ahead across a full restart (every store at once): both cycles complete and no instant beyond now+1h is published that the true-clock control does not publish",
     "command": cmd("clock_save.py"),
     "value": "clock_ahead_cycle_fail=0, clock_ahead_extra_future_published=0"},
    {"claim": "Save during the learners' load: the coordinator's savers wait for their read (their documents equal the race-free control); disabling QuarantiningStore.async_wait_for_read raises the clobber set from 5 to 7 (accuracy, ledger join), so the wait is load-bearing. Of the 5 that differ at baseline: dhw_legionella differs only in the instant's +00:00 suffix; duty_switch and pump_duty were persisted by the harness calling their private _persist before their lazy _load, which production never does (both load first, pump_arbiter under held.lock); dhw_draws' saver (DhwLearner.async_save_draws) builds its payload before the store's wait and its read is not awaited by DhwLearner.async_wait_for_read (profile store only), but no production path folds a draw before the first interval has passed; off_restore is D1-s2-04",
     "command": cmd("clock_save.py") + " ; " + cmd("clock_save.py", "--no-wait"),
     "value": "save_during_load_clobbered=5 (dhw_draws, dhw_legionella, duty_switch, off_restore, pump_duty); --no-wait: 7"},
    {"claim": "A previous run's hold whose expiry passed during the downtime is released at restart (away override, DHW/space boost, DHW block); the same holds still running survive, read at the first cycle, whose first actuator write (switch.turn_on on the configured heat-pump switch) is made with no expired hold in force",
     "command": cmd("hold_restore.py"),
     "value": "expired_hold_in_force=0, running_hold_lost=0 (9 scenarios)"},
    {"claim": "Config-entry migration v1..v6->7 with a healthy entry: migrate, construct and two cycles complete at every version",
     "command": cmd("config_fuzz.py", "--n 0"),
     "value": "CTRL v1..v6 all ok"},
    {"claim": "Watchdog staleness for the 24 d1-inputs slots the coordinator's InputHealth reads: unavailable/unknown flagged, the value returned inside one interval is read fresh, a last_reported 90 min ahead is refused (problem stale), a host clock stepped back 2 h publishes no negative age, and a reading past its own max_age is flagged",
     "command": cmd("staleness.py"),
     "value": "stale_after_return=0, missing_not_flagged=0, future_accepted=0, neg_age_after_jump=0, stale_not_flagged=0, cycle_fail=0 over 51 slots (27 'unread' handed to staleness_unread.py)"},
    {"claim": "The 27 slots outside that watchdog, through their own consumer: none uses a dead (unavailable/unknown) reading or a stale value after return; past-limit use only for PV production (D1-s2-02); external heat's numeric arm is held to its 60 min limit and its flag arm is unbounded by design (const.py comment); MIXING_VALVE_WRITE, SPACE_PUMP and VVC_PUMP are write-only (no read path, consumers.py shows no getter); AWAY_RETURN has no reader (away.py pops it at migration); PRICE and WEATHER are driven by price_weather.py",
     "command": cmd("staleness_unread.py") + " ; " + cmd("consumers.py"),
     "value": "dead_used=0, stale_after_return=0, past_limit_used=1 (PV), cycle_fail=0"},
    {"claim": "A price fetch that raises (ClientError, RuntimeError, TimeoutError) while the last prices still cover now is bridged: the cycle completes on the last prices with one WARNING; a price entity that stops updating publishes current_price None and plan_stale True once its rows no longer cover now; an unavailable price entity whose rows still cover now keeps planning",
     "command": cmd("price_weather.py"),
     "value": "price_stuck_hidden=0; weather_empty_hidden=0 (an empty forecast marks stale_hours)"},
    {"claim": "A presence entity changing between two scheduled updates requests one refresh per change through away.watch_away_inputs and the next cycle publishes the new away state; the holiday calendar's change requests one refresh",
     "command": cmd("presence_dst.py"),
     "value": "presence_missed=0 of 3"},
    {"claim": "Age readings across DST (Europe/Stockholm spring and autumn, +20/+70 min across the change) and host-clock jumps (-2 h, +3 h): the probe's published age equals true elapsed time, none negative; a stamp ahead of a stepped-back clock is flagged stale, not aged negative",
     "command": cmd("presence_dst.py"),
     "value": "age_cells_wrong=0 of 6"},
    {"claim": "While the power and energy meters are unavailable no measured value is published (measured_power None, available False); the energy totals keep integrating the modelled draw (0.34, 0.40 kWh per cycle) and the 45-minute total (1.12 kWh) matches the meter's own delta over the outage (1.1 kWh)",
     "command": cmd("booked.py"),
     "value": "unavailable_cycles_claiming_measurement=0"},
]
universe2 = len(stores)
universe3 = len(inputs)
rep = {
    "dimension": "D1",
    "baseline_sha": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692",
    "report_path": f"{ROOT}/REPORT.md",
    "exposure": "",
    "coverage": [
        {"step": "D1.M2", "enumerator": "PYTHONPATH=tests/hastub python3 tools/audit/enumerate.py d1-stores",
         "universe": universe2, "examined": universe2, "not_reached": [],
         "redispatched": [{"item": "C1", "state": "examined"}],
         "evidence": "17 store lines: store_fuzz.py 200 seeded mutants each (boost/manual_plan/away populated), nan_boundary.py every numeric leaf, clock_save.py (writer clock +48 h across a restart; save during the load), hold_restore.py (expired/running holds to the first cycle), off_restore_race.py, boost_settle.py. 24 upgrade lines: CONFIG_ENTRY_VERSION v1..v6 by config_fuzz.py (200 each), LEDGER v1->2 and defrost v1->2 by upgrade_fuzz.py (healthy old record + 200 mutants), the 16 'v1 (no earlier version)' lines as the v1 record loaded by this release = that store's healthy control and fuzz in store_fuzz.py. C1: manual_plan, dhw profile/draws, boost, pump_arbiter, notifier and debug all fuzzed with populated payloads; positive control --control; healthy-restart WARNINGs subtracted per store."},
        {"step": "D1.M3", "enumerator": "PYTHONPATH=tests/hastub python3 tools/audit/enumerate.py d1-inputs",
         "universe": universe3, "examined": universe3, "not_reached": [],
         "redispatched": [{"item": "C2", "state": "examined"}],
         "evidence": "staleness.py over all 51 (24 reach the coordinator watchdog: h/u/r/k/f/j/s phases); staleness_unread.py over the other 27 through their own consumers (consumers.py names them); pv_stale.py, weather_stuck.py, price_weather.py (price fetch raising with covering prices, price list stopping, empty forecast), presence_dst.py (presence between updates, DST spring/autumn, host clock -2 h/+3 h), booked.py (published and booked value). C2: DST via dt DEFAULT_TIME_ZONE Europe/Stockholm with dt.freeze across both 2026 changes, and the backward host-clock jump on the watchdog (staleness.py phase j, 24 slots) and the age readings (presence_dst.py)."},
    ],
    "unfinished": [],
    "findings": findings,
    "non_findings": non_findings,
    "harnesses": harnesses,
    "leads": [
        {"owner_seat": "D1-s3", "file": "custom_components/heatpump_optimizer/coordinator.py", "symbol": "HeatPumpOptimizerCoordinator._spawn",
         "what": "A spawned store-load/restore task that raises is never awaited or logged by the integration (boost restore_session's OverflowError surfaces only as asyncio's 'Task exception was never retrieved'); whether every spawned load owns its failure is M5's handler question."},
        {"owner_seat": "D1-s3", "file": "custom_components/heatpump_optimizer/store.py", "symbol": "_bound_instants",
         "what": "Rewrites any ISO-looking string in any stored field (not only declared instants) and logs it as 'stored instant ... ahead of the clock'; for a corrupt non-instant field that is a misleading second WARNING beside the loader's quarantine line (store_fuzz.py log_multi cases)."},
    ],
}
json.dump(rep, open(f"{ROOT}/REPORT.json", "w"), indent=1)
print("findings", len(findings), "universe", universe2, universe3)
try:
    import jsonschema
    jsonschema.validate(rep, json.load(open("dev/audit/config/finding.schema.json")))
    print("schema ok")
except ImportError:
    print("no jsonschema")
