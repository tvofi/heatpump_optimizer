#!/bin/bash
W=/tmp/tmp.E6pbV6U87z; M=$W/mut; cd $M; git checkout -q -- .
off() { env -i HOME=$W/off/home PATH=/opt/hpo/venv-ci/bin:/usr/bin:/bin "$@"; }
mutate() { python3 - "$1" "$2" "$3" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); c=s.count(o); assert c==1,(p,c); open(p,'w').write(s.replace(o,n))
PY
}
echo "base gate: $(off python3 -I tools/policy/budget_raise_gate.py --self-test 2>&1 | tail -1)"
echo "base train: $(off python3 -I tools/audit/seat/merge_train.py --self-test 2>&1 | tail -1)"
mutate tools/policy/budget_raise_gate.py 'return justified(body, score_fn) if raises else justification(body)' 'return justification(body)'
echo "MV1 check_body shape-only:"; off python3 -I tools/policy/budget_raise_gate.py --self-test 2>&1 | grep -E 'FAIL|self-test:' | head -4
git checkout -q -- .
mutate tools/audit/seat/merge_train.py 'justify=lambda: g.justified(self._body(pr), lambda: self._measured_score(g, h)))' 'justify=lambda: g.justification(self._body(pr)))'
echo "MV2 train shape-only:"; off python3 -I tools/audit/seat/merge_train.py --self-test 2>&1 | grep -E 'FAIL|self-test' | head -4
git checkout -q -- .; git status --short
