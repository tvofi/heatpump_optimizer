# id | file | old | new  (each old must occur exactly once)
M = [
 ("G1-guard-off","tools/audit/seat/cloud_relay.sh",'git log --format=%T "$tip" > "$d/rtrees" 2>/dev/null && grep -qxF "$wt" "$d/rtrees"; then','false; then'),
 ("G2-guard-pipe","tools/audit/seat/cloud_relay.sh",'git log --format=%T "$tip" > "$d/rtrees" 2>/dev/null && grep -qxF "$wt" "$d/rtrees"; then','git log --format=%T "$tip" 2>/dev/null | head -n 1 | grep -qxF "$wt"; then'),
 ("G3-guard-noledger","tools/audit/seat/cloud_relay.sh",'    mkdir -p "$state" && echo "$ref $sha" >> "$led"\n    echo "cloud_relay: review/$pr already','    echo "cloud_relay: review/$pr already'),
 ("S1-statedir-line","tools/audit/seat/cloud_relay.sh",'    echo "cloud_relay: state dir ${HPO_STATE_DIR:-$HOME/.local/state/hpo}, ledger ${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relayed, log $(relay_log)"\n',''),
 ("C1-relay-case","tools/audit/seat/cloud_relay.sh",'k = tolower(q)\n','k = q\n'),
 ("H1-heldbody-off","tools/audit/seat/cloud_relay.sh",'if [ -z "$bonly" ] && ! grep -qF "${hs:0:8}" "$body"; then','if false; then'),
 ("B1-bodyonly-nocode","tools/audit/seat/cloud_relay.sh",'body_only_owed "$pr" "$topic" "$bs" "$head" "its body carries no Code: trailer" || echo "$topic $bs" >> "$bf"','echo "$topic $bs" >> "$bf"'),
 ("B2-bodyonly-held","tools/audit/seat/cloud_relay.sh",'[ -z "$bonly" ] || body_only_owed "$pr" "$topic" "$bs" "$head" "held by the hold file" || :; continue','continue'),
 ("B3-bodyonly-ge","tools/audit/seat/cloud_relay.sh",'[ "$bt" -gt "$ht" ]','[ "$bt" -ge 0 ]'),
 ("L1-handoff-level-late","tools/audit/seat/cloud_relay.sh",'  handoff_level\n  while IFS','  while IFS'),
 ("P1-probe-level-late","tools/audit/seat/cloud_relay.sh",'  level_set probe-ref "$state/cloud-level-probe.$$.k"; level_set probe-refused "$state/cloud-level-refused.$$.k"\n',''),
 ("T1-holdstale-off","tools/audit/seat/cloud_relay.sh",'|| level_line handoff-hold-stale','|| :'),
 ("R2-M2-head","tools/audit/seat/cloud_relay.sh",'grep REFUSE "$bd/update.out" | tail -n 1','grep REFUSE "$bd/update.out" | head -n 1'),
 ("R5-M5-replay","tools/audit/seat/cloud_relay.sh",'cat "$bd/update.out" >&2','true'),
 ("X1-bus-case","tools/audit/seat/bus.sh",'k=tolower(q)','k=q'),
 ("X2-bus-unpack","tools/audit/seat/bus.sh",'  if [ -z "$why" ] && cc=$(case_collision "$d/evidence" 2>/dev/null); then why="evidence/ names collide case-insensitively: $cc"; fi\n',''),
 ("K1-tick-setpgid","tools/audit/seat/tick_loop.sh",'os.setpgid(0, 0)  # own','pass  # own'),
 ("Y1-tick-gap","tools/audit/seat/orchestrator_tick.py",'            if n > 0:\n                self.line(S, f"GAP:','            if False:\n                self.line(S, f"GAP:'),
]
import sys
mid=sys.argv[1]; root=sys.argv[2]
for i,f,o,n in M:
    if i==mid:
        p=root+"/"+f; s=open(p).read(); c=s.count(o); assert c==1,(i,c); open(p,"w").write(s.replace(o,n)); print(f)
if mid=="list": print(" ".join(m[0] for m in M))
