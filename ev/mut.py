import subprocess, sys, pathlib
S=sys.argv[1]; P="custom_components/heatpump_optimizer/"
M=[
 ("M1 judge_floor experiment arm off", "accuracy.py", "        if experiment:\n            return COP_REFUSED_OFF_ASK\n", ""),
 ("M2 coordinator passes experiment=False", "coordinator.py", 'draw, self._current_action.get("mode") == "system_identification")', "draw, False)"),
 ("M3 commit_runs ignores keep", "draw_range.py", "        if keep:\n            self.rows.extend", "        if True:\n            self.rows.extend"),
 ("M4 run_key drops level", "draw_range.py", "return (self.written_c, self.level_kw, self.duty, self.origin)", "return (self.written_c, self.duty, self.origin)"),
 ("M5 _note_pass not called", "pump_arbiter.py", "    _note_pass(held, inp, served, boosted, now)\n", ""),
 ("M6 space filter off", "draw_range.py", 'for r in self.closed if r[-1] == "space")', "for r in self.closed)"),
 ("M7 settle drop off", "draw_range.py", ">= SEGMENT_SETTLE_MIN * 60.0]", ">= 0.0]"),
 ("M8 defrost not a stop", "draw_range.py", "stopped = rec is None or rec.defrost or", "stopped = rec is None or"),
 ("M9 max-run close off", "draw_range.py", ">= SEGMENT_MAX_MIN * 60.0)", ">= 1e12)"),
 ("M10 one-pass-a-minute off", "draw_range.py", "            return  # one pass a minute", "            pass  # one pass a minute"),
 ("M11 probe->fit", "pump_arbiter.py", "return ORIGIN_PROBE if action.get(\"kind\") == KIND_PROBE else ORIGIN_FIT", "return ORIGIN_FIT"),
 ("M12 feedback_start never", "pump_arbiter.py", "return ORIGIN_FEEDBACK_START if held_start else ORIGIN_FEEDBACK", "return ORIGIN_FEEDBACK"),
 ("M13 map_rows always stored", "draw_range.py", 'if self.map.rows else {}),', 'if True else {}),'),
 ("M14 from_dict drops map", "draw_range.py", "        out.map = _stored_map(data)\n", ""),
 ("M15 kind key dropped", "coordinator.py", '            "kind": self._sysid.kind,\n', ""),
 ("M16 draw not handed", "coordinator.py", "            draw=self._accuracy.draw,\n", ""),
 ("M17 boost origin off", "pump_arbiter.py", "    if boost_on:\n        return ORIGIN_BOOST\n", ""),
 ("M18 gate vs hold swapped", "pump_arbiter.py", "return ORIGIN_HOLD if duty is None else ORIGIN_GATE", "return ORIGIN_GATE if duty is None else ORIGIN_HOLD"),
]
cmd=["python3","tools/audit/seat/features_block.py","--prelude",f"exec(open('{S}/prelude.py').read())","# --- R10-DRAW-MAP-EVIDENCE part A"]
for name,f,a,b in M:
    p=pathlib.Path(P+f); src=p.read_text()
    if src.count(a)!=1: print(f"{name}: SKIP anchor count {src.count(a)}",flush=True); continue
    p.write_text(src.replace(a,b))
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=600,env={**__import__('os').environ,"PYTHONPATH":"tests/hastub"})
        fails=[l.strip() for l in (r.stdout+r.stderr).splitlines() if l.strip().startswith("FAIL") or "Error" in l][:3]
        print(f"{name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {fails}",flush=True)
    finally:
        p.write_text(src)
