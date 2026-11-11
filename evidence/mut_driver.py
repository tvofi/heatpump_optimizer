import subprocess, sys, os
WT=os.path.expanduser("~/wt"); P=WT+"/custom_components/heatpump_optimizer/pump_arbiter.py"
src=open(P).read()
M=[
("260 CONST rate 0.2->0.4","FEEDBACK_RATE_K_PER_MIN = 0.2","FEEDBACK_RATE_K_PER_MIN = 0.4"),
("276 CONST margin 0.2->0.4","FEEDBACK_STOP_MARGIN_K = 0.2","FEEDBACK_STOP_MARGIN_K = 0.4"),
("279 CONST gateclear 0.01->0.02","FEEDBACK_GATE_CLEAR_K = 0.01","FEEDBACK_GATE_CLEAR_K = 0.02"),
("920 CMP_BOUND > -> >=","utc_elapsed_seconds(now, rec.seen) > FEEDBACK_WINDOW","utc_elapsed_seconds(now, rec.seen) >= FEEDBACK_WINDOW"),
("922 CMP_BOUND I < -> <=","power < _ran_kw(inp)","power <= _ran_kw(inp)"),
("926 RETURN_DEL","        held.feedback = FeedbackRun(now, base, now)\n        return base\n","        held.feedback = FeedbackRun(now, base, now)\n"),
("930 CMP_BOUND > -> >=","rec.samples[0][0]) > FEEDBACK_WINDOW","rec.samples[0][0]) >= FEEDBACK_WINDOW"),
("934 CMP_BOUND < -> <=","rec.start) < FEEDBACK_START_HOLD","rec.start) <= FEEDBACK_START_HOLD"),
("953 CMP_BOUND E <= -> <","if abs(error) <= FEEDBACK_DEADBAND_SHARE","if abs(error) < FEEDBACK_DEADBAND_SHARE"),
("997 CMP_BOUND F >= -> >","rec.sent_c >= base:","rec.sent_c > base:"),
("997 GUARD_OFF","if rec.sent_c is None or rec.sent_c >= base:\n        return","if rec.sent_c is None:\n        return"),
("1000 CLAMP_DROP","gap if held.stop_gap_k is None else min(held.stop_gap_k, gap)","gap"),
("1019 CMP_BOUND low <=","if not low - SETPOINT_TOLERANCE <= observed","if not low - SETPOINT_TOLERANCE < observed"),
("1022 CMP_BOUND H > -> >=","if value > rec.prev_c:","if value >= rec.prev_c:"),
("1019b high <=","observed <= high + SETPOINT_TOLERANCE","observed < high + SETPOINT_TOLERANCE"),
("G cut_lo dropped","lows = [inlet - FEEDBACK_DOWN_K, rec.cut_lo_c, gate","lows = [inlet - FEEDBACK_DOWN_K, gate"),
("J start-hold sent_c kept","rec.w_c, rec.sent_c = base, None","rec.w_c = base"),
]
try:
  for name,a,b in M:
    n=src.count(a)
    if n!=1: print(f"MUTANT {name}: anchor count {n} SKIPPED"); continue
    open(P,"w").write(src.replace(a,b))
    r=subprocess.run([sys.executable,"tests/_r10x.py"],cwd=WT,capture_output=True,text=True,timeout=200,
       env=dict(os.environ,PYTHONPATH="tests/hastub:custom_components:tests"))
    fails=[l for l in r.stdout.splitlines() if l.startswith("  FAIL")]
    last=(r.stdout.strip().splitlines() or [r.stderr.strip()[-120:]])[-1]
    print(f"MUTANT {name}: rc={r.returncode} failing={len(fails)} | {last}"); sys.stdout.flush()
finally:
  open(P,"w").write(src)
