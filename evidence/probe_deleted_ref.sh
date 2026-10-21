#!/bin/bash
# reviewer's own probe (not the finder's, not the fixer's): a ref deleted from origin
# leaves the level after one pass; tree passed as $1
set -e; T=$(cd "$1" && pwd); d=$(mktemp -d); export HPO_STATE_DIR=$d/state HPO_BUS_STATE=$d/bus
git init -q --bare $d/o.git; git init -q $d/w; cd $d/w; git -c user.name=x -c user.email=x@x commit -q --allow-empty -m a
git remote add origin $d/o.git
for r in handoff/a handoff/b probe/scan-z; do git push -q origin HEAD:refs/heads/$r; done
printf '#!/bin/sh\nexit 0\n' > $d/l.sh; chmod +x $d/l.sh; export HPO_RELAY_PRS=$d/l.sh
bash $T/tools/audit/seat/cloud_relay.sh pass >/dev/null 2>&1; bash $T/tools/audit/seat/cloud_relay.sh pass >/dev/null 2>&1
git push -q origin :refs/heads/handoff/b :refs/heads/probe/scan-z
bash $T/tools/audit/seat/cloud_relay.sh pass >/dev/null 2>&1
L=$d/state/cloud-relay.log
n=$(python3 - "$T" "$L" <<'P'
import sys,importlib.util;T,L=sys.argv[1:];sys.path.insert(0,T+"/tools/audit/seat")
s=importlib.util.spec_from_file_location("t",T+"/tools/audit/seat/orchestrator_tick.py");m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
t=m.Tick("o/r",T,relay_log=L);t.relay_owed("P");r=[x["text"] for x in t.sections.get("P",[]) if x["flag"]];print(len(r));[print(" ",x,file=sys.stderr) for x in r]
P
)
echo "RESULT tree=$(git -C $T rev-parse --short=9 HEAD) owed_after_delete=$n want=1 match=$([ "$n" = 1 ] && echo yes || echo no)"
rm -rf $d
