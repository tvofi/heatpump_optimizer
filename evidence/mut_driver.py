import subprocess, sys, pathlib, os, shutil
W = pathlib.Path(os.environ["HOME"]) / "wt"
P = "custom_components/heatpump_optimizer/"
M = [
 ("first->last reading", P+"room_history.py", "        if tally[0] is None:  # the period's first reading: its calling acts from there on\n", "        if True:\n"),
 ("note floor +1 dropped", P+"room_history.py", "history.times[-1] + 1 if history.times", "history.times[-1] if history.times"),
 ("pair gap unchecked", P+"room_history.py", "            if history.times[j] - history.times[i] <= PAIR_GAP_MIN]", "            ]"),
 ("rate per row not per hour", P+"room_history.py", "/ ((np.array(history.times)[then] - np.array(history.times)[first]) / 60.0)", "/ 0.5"),
 ("pairs keep null call", P+"room_history.py", " if columns[\"call\"][i] is not None]", "]"),
 ("space ignores dhw", P+"room_history.py", "house.space_kw > 0.0 and house.dhw_kw <= 0.0", "house.space_kw > 0.0"),
 ("ring one row longer", P+"room_history.py", "cut = period.start - (HISTORY_LENGTH - 1) * PERIOD_MIN", "cut = period.start - HISTORY_LENGTH * PERIOD_MIN"),
 ("bad house empties ring", P+"room_history.py", "    house = _columns(raw.get(\"house\"), HOUSE_FIELDS, len(times))\n", "    house = _columns(raw.get(\"house\"), HOUSE_FIELDS, len(times))\n    if house is None: return History()\n"),
 ("times off-grid accepted", P+"room_history.py", "b - a < PERIOD_MIN or b % PERIOD_MIN", "b - a < PERIOD_MIN"),
 ("no load before note", P+"room_record.py", "        await _load(rec)\n", "        rec.loaded = True\n"),
 ("report cache key len only", P+"room_record.py", "rec.history.times[-1] if rec.history.times else 0", "0"),
 ("flush ignores unsaved", P+"room_record.py", "rec.loaded and rec.unsaved:", "rec.loaded:"),
 ("persist never resets unsaved", P+"room_record.py", "    rec.unsaved = 0\n", "    pass\n"),
 ("unload flush deleted", P+"__init__.py", "        await (await _async_lazy(hass, \"room_record\")).async_flush(coordinator)\n", ""),
 ("diag key always", P+"diagnostics.py", "    if room_record.record_of(coord) is not None:  # only", "    if True:  # only"),
 ("coord swaps space/dhw kw", P+"coordinator.py", "float(self._current_action.get(\"power\", 0.0)), float(self._current_action.get(\"dhw_power\", 0.0))", "float(self._current_action.get(\"dhw_power\", 0.0)), float(self._current_action.get(\"power\", 0.0))"),
 ("coord outdoor->return", P+"coordinator.py", "ctx._current_state.outdoor_temperature, self._floor_return_temp, self._measured_power", "self._floor_return_temp, self._floor_return_temp, self._measured_power"),
 ("coord step deleted", P+"coordinator.py", "            await _best_effort_cycle_step(lambda: room_record.async_note_cycle(", "            0 and (lambda: room_record.async_note_cycle("),
 ("power mean -> last", P+"room_history.py", "round(sum(period.power) / len(period.power))", "period.power[-1]"),
 ("target first not last", P+"room_history.py", "        if (target := _centi(reading.target_c, \"target\")) is not None:\n", "        if (target := _centi(reading.target_c, \"target\")) is not None and tally[1] is None:\n"),
 ("call share counts problem rows", P+"room_history.py", "if reading.problem is None and reading.calling is not None:", "if reading.calling is not None:"),
 ("house line drops space filter", P+"room_history.py", "and s >= CALLING_SHARE and reported[i]]", "and reported[i]]"),
]
CMD = ["env","PYTHONPATH=tests/hastub","PYTHONDONTWRITEBYTECODE=1","python3","tools/audit/seat/features_block.py","--prelude","from heatpump_optimizer import coordinator as _r9f13_cmod","--prelude","import json as _fi_json","R11-OUTSIDE-ROOMS-P3 (#3616, phase 3a)"]
extra = sys.argv[1:]
for name, f, old, new in M:
    p = W / f; src = p.read_text()
    if src.count(old) != 1:
        print(f"NOAPPLY {name} count={src.count(old)}", flush=True); continue
    p.write_text(src.replace(old, new))
    for c in W.rglob("__pycache__"): shutil.rmtree(c, ignore_errors=True)
    try:
        r = subprocess.run(CMD, cwd=W, capture_output=True, text=True, timeout=600)
        fails = [l for l in (r.stdout+r.stderr).splitlines() if l.strip().startswith("FAIL")]
        verdict = "KILLED" if r.returncode else "SURVIVED"
        print(f"{verdict} rc={r.returncode} {name} :: {fails[:2] or (r.stdout+r.stderr).strip().splitlines()[-1:]}", flush=True)
    finally:
        p.write_text(src)
print("DONE")
