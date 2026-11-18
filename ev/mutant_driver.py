import subprocess, sys, pathlib, os
WT = pathlib.Path(os.environ["HOME"]) / "wt"
P = "custom_components/heatpump_optimizer/"
M = [
 ("M1 owed_scale not experiment->True", P+"coordinator.py", "dt_util.now(), not experiment)", "dt_util.now(), True)"),
 ("M2 judge_floor experiment guard off", P+"accuracy.py", "        if experiment:\n            return COP_REFUSED_OFF_ASK", "        if False:\n            return COP_REFUSED_OFF_ASK"),
 ("M3 judge_floor caller drops experiment", P+"coordinator.py", "params, draw, experiment)", "params, draw)"),
 ("M4 experiment flag False", P+"coordinator.py", 'experiment = self._current_action.get("mode") == "system_identification"', "experiment = False"),
 ("M5 owed_scale read ignored", P+"accuracy.py", "configured, now, read and self.refusal", "configured, now, self.refusal"),
 ("M6 arbiter inputs draw dropped", P+"coordinator.py", "            draw=self._accuracy.draw,\n", ""),
 ("M7 action kind dropped", P+"coordinator.py", '            "kind": self._sysid.kind,\n', ""),
 ("M8 _note_pass call dropped", P+"pump_arbiter.py", "    _note_pass(held, inp, served, boosted, now)\n", ""),
 ("M9 commit_runs keep always", P+"draw_range.py", "draw.map.commit_runs(keep=not (frozen or distorted))", "draw.map.commit_runs(keep=True)"),
 ("M10 space-only filter off", P+"draw_range.py", 'for r in self.closed if r[-1] == "space")', "for r in self.closed)"),
 ("M11 map rows not persisted", P+"draw_range.py", '**({"map_rows": self.map.as_columns()} if self.map.rows else {}),', ""),
 ("M12 map rows not restored", P+"draw_range.py", "        out.map = _stored_map(data)\n", ""),
 ("M13 probe origin -> fit", P+"pump_arbiter.py", "return ORIGIN_PROBE if action.get(\"kind\") == KIND_PROBE else ORIGIN_FIT", "return ORIGIN_FIT"),
 ("M14 settle filter off", P+"draw_range.py", ">= SEGMENT_SETTLE_MIN * 60.0]", ">= 0.0]"),
 ("M15 stopped-close off", P+"draw_range.py", "stopped = rec.defrost or rec.drawn_kw is None or rec.drawn_kw <= RUNNING_FLOOR_KW", "stopped = False"),
 ("M16 max-run close off", P+"draw_range.py", "(rec.at - first.at).total_seconds() >= SEGMENT_MAX_MIN * 60.0)", "False)"),
 ("M17 boost origin off", P+"pump_arbiter.py", "    if boost_on:\n        return ORIGIN_BOOST\n", ""),
 ("M18 unequal-column guard off", P+"draw_range.py", "    if len({len(c) for c in split}) != 1:\n        return out\n", ""),
]
S = 'R.section("R10-DRAW-MAP-EVIDENCE part A: map rows and the learner exclusion")'
pre = os.environ["HOME"] + "/prelude.py"
sel = sys.argv[1:] 
for name, f, old, new in M:
    if sel and name.split()[0] not in sel: continue
    p = WT / f; src = p.read_text()
    n = src.count(old)
    if n != 1:
        print(f"{name}: SKIP anchor count {n}", flush=True); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", f"exec(open('{pre}').read())", S],
            cwd=WT, env={**os.environ, "PYTHONPATH": "tests/hastub"}, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if l.lstrip().startswith("FAIL")]
        last = out.strip().splitlines()[-1] if out.strip() else ""
        print(f"{name}: rc={r.returncode} fails={len(fails)} last={last[:160]}", flush=True)
        for l in fails[:3]: print("   ", l.strip()[:220], flush=True)
    finally:
        p.write_text(src)
