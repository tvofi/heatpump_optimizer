import subprocess, sys, pathlib
S = sys.argv[1]; root = pathlib.Path(sys.argv[2])
P = "custom_components/heatpump_optimizer/"
M = [
 ("owed_scale_read_true", P+"coordinator.py", "dt_util.now(), not experiment)", "dt_util.now(), True)"),
 ("judge_floor_no_experiment", P+"accuracy.py", "        if experiment:\n            return COP_REFUSED_OFF_ASK", "        if False:\n            return COP_REFUSED_OFF_ASK"),
 ("experiment_flag_false", P+"coordinator.py", 'experiment = self._current_action.get("mode") == "system_identification"', "experiment = False"),
 ("keep_true", P+"draw_range.py", "commit_runs(keep=not (frozen or distorted))", "commit_runs(keep=True)"),
 ("keep_not_distorted", P+"draw_range.py", "commit_runs(keep=not (frozen or distorted))", "commit_runs(keep=not distorted)"),
 ("keep_not_frozen", P+"draw_range.py", "commit_runs(keep=not (frozen or distorted))", "commit_runs(keep=not frozen)"),
 ("space_filter_off", P+"draw_range.py", 'for r in self.closed if r[-1] == "space")', "for r in self.closed)"),
 ("defrost_not_stop", P+"draw_range.py", "stopped = rec.defrost or rec.drawn_kw", "stopped = rec.drawn_kw"),
 ("settle_zero", P+"draw_range.py", ">= SEGMENT_SETTLE_MIN * 60.0]", ">= 0.0]"),
 ("max_len_off", P+"draw_range.py", "(rec.at - first.at).total_seconds() >= SEGMENT_MAX_MIN * 60.0", "False"),
 ("minute_dedupe_off", P+"draw_range.py", "        if self.open and int(rec.at.timestamp() // 60) == int(self.open[-1].at.timestamp() // 60):\n            return", "        if False:\n            return"),
 ("probe_kind_ignored", P+"pump_arbiter.py", "return ORIGIN_PROBE if action.get(\"kind\") == KIND_PROBE else ORIGIN_FIT", "return ORIGIN_FIT"),
 ("feedback_start_off", P+"pump_arbiter.py", "return ORIGIN_FEEDBACK_START if held_start else ORIGIN_FEEDBACK", "return ORIGIN_FEEDBACK"),
 ("note_pass_removed", P+"pump_arbiter.py", "    _note_pass(held, inp, served, boosted, now)\n", ""),
 ("coord_draw_none", P+"coordinator.py", "            draw=self._accuracy.draw,\n", ""),
 ("kind_absent", P+"coordinator.py", '            "kind": self._sysid.kind,\n', ""),
 ("map_not_persisted", P+"draw_range.py", '**({"map_rows": self.map.as_columns()} if self.map.rows else {}),', ""),
 ("stored_map_ignored", P+"draw_range.py", "        out.map = _stored_map(data)\n", ""),
 ("nonfinite_accepted", P+"draw_range.py", "    if not np.isfinite(value):\n        raise ValueError(cell)\n", ""),
 ("unequal_cols_kept", P+"draw_range.py", "    if len({len(c) for c in split}) != 1:\n        return out\n", ""),
]
only = sys.argv[3:] 
for name, f, old, new in M:
    if only and name not in only: continue
    p = root / f; src = p.read_text()
    if src.count(old) != 1:
        print(f"MUTANT {name}: SKIP anchor count {src.count(old)}", flush=True); continue
    p.write_text(src.replace(old, new))
    try:
        out = subprocess.run(["bash", f"{S}/blockA.sh", str(root)], capture_output=True, text=True).stdout
    finally:
        p.write_text(src)
    (pathlib.Path(S)/f"mut_{name}.txt").write_text(out)
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    last = out.strip().splitlines()[-1] if out.strip() else "no output"
    print(f"MUTANT {name}: {'KILLED' if fails or 'PASSED' not in last else 'SURVIVED'} fails={len(fails)} last={last[:160]}", flush=True)
    for l in fails[:3]: print("   ", l[:200], flush=True)
