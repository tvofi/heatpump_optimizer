# usage: mutants.sh ; each mutant: file, old, new
m() { f=$1; o=$2; n=$3; name=$4; cp $f /tmp/claude-0/bak; python3 - "$f" "$o" "$n" <<'PY'
import sys;p,o,n=sys.argv[1:];s=open(p).read();assert s.count(o)==1,(o,s.count(o));open(p,'w').write(s.replace(o,n))
PY
  g=$(timeout 200 python3 -I tools/ci/gate.py --self-test 2>&1 | grep -cE '^ *FAIL'); pr=$(timeout 200 python3 -I tools/ci/prelude.py --self-test 2>&1 | grep -cE '^ *FAIL'); echo "MUTANT [$name]: gate FAIL lines=$g prelude FAIL lines=$pr"; cp /tmp/claude-0/bak $f; }
m tools/ci/prelude.py 'STANDS = ("success", "skipped")' 'STANDS = ("success", "skipped", "failure", "cancelled")' "R4: failed/cancelled stand"
m tools/ci/prelude.py 'if p and p[0] == "completed" and p[1] in STANDS:' 'if p and p[0] == "completed":' "R4 dropped"
m tools/ci/prelude.py 'or not began or not pre or pre >= began:' 'or not began or not pre:' "R2 timestamp dropped"
m tools/ci/prelude.py 'if jobs.get("prelude") != ("completed", "success") or not began' 'if not began' "R2 prelude-green dropped"
m tools/ci/prelude.py 'if int(run.get("attempt") or 1) <= 1:' 'if False:' "R1 dropped"
m tools/ci/gate.py '    others = [{**r, **dict(zip(("jobs", "starts"), standing(r)))} for r in others]' '    pass' "gate source read ignores standing"
m tools/ci/prelude.py 'jobs[k], starts[k] = (p[0], p[1]), (p[2] if len(p) > 2 else None)' 'jobs[k] = (p[0], p[1])' "overlay keeps latest start"
m tools/ci/prelude.py '    jobs = standing(run)[0]' '    jobs = run.get("jobs") or {}' "judging ignores standing"
