import importlib.util, sys, types, tempfile, os
tick = sys.argv[1]
spec = importlib.util.spec_from_file_location("t", tick); m = importlib.util.module_from_spec(spec); sys.modules["t"]=m; spec.loader.exec_module(m)
cls = next(c for c in vars(m).values() if isinstance(c, type) and "relay_owed" in vars(c))
U="2026-10-22T01:00:00Z"; H="a"*40
# hand-written log: one row per writer kind, as cloud_relay.sh formats them, then POSTED per PR
log = [
 f"OWED {U} 101 - push-verdict printed no 40-hex review commit",
 f"OWED {U} 102 {H} confirm failed",
 f"OWED {U} probe-ref refs/heads/probe/scan-x {H}",
 f"OWED {U} probe-ref refs/heads/probe/scan-x {H}",
 f"OWED {U} handoff-update 103 topic-a {H}",
 f"OWED {U} approve-held-runs 104 fix/x",
 f"OWED {U} dispatch 105 no new head read after the update",
 f"OWED reviewer-fire 106 {H} 0123 {U}",
 f"OWED {U} dispatch 107 {H} bus.sh dispatch failed; run it by hand",
 f"OWED {U} handoff-no-pr refs/heads/handoff/topic-b {H}",
 f"OWED {U} handoff-no-pr refs/heads/handoff/topic-b {H}",
] + [f"POSTED {U} {p} {H}" for p in range(101,108)]
d=tempfile.mkdtemp(); p=os.path.join(d,"cloud-relay.log"); open(p,"w").write("\n".join(log)+"\n")
s=types.SimpleNamespace(relay_log=p,out=[]); s.line=lambda S,t,flag=False: s.out.append(t); s.unreadable=lambda *a: s.out.append("UNREADABLE")
cls.relay_owed(s,"S")
left=[o for o in s.out if o.startswith("OWED: ")]
for o in s.out: print("  ", o)
kinds=sorted({o.split()[3] if o.split()[1]=="OWED" and not o.split()[2].startswith("reviewer") else o.split()[2] for o in left})
print(f"RESULT tick={tick} uncleared_after_POSTED={len(left)} kinds={kinds}")
