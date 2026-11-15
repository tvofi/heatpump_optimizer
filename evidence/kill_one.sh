#!/bin/bash
# apply mutant $1 (index into the R list) to an archive copy of the head, run the driver, print failing checks
k=$1; W=$(mktemp -d); git -C $HOME/wt-head archive HEAD | tar -x -C $W; cd $W
python3 - "$k" <<'PY'
import json,sys
ms=[m for f in ("/root/rev/spec0.json","/root/rev/spec1.json","/root/rev/spec2.json") for m in json.load(open(f))]
m=[x for x in ms if x["name"].startswith("R%s "%sys.argv[1])][0]
s=open(m["file"]).read(); assert s.count(m["old"])==1; open(m["file"],"w").write(s.replace(m["old"],m["new"]))
print("MUTANT",m["name"])
PY
$HOME/rev/driver.sh; echo "driver rc=$?"; cd /; rm -rf $W
