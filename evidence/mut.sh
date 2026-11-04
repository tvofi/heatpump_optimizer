set -u
cd $HOME/wt
run(){ name="$1"; old="$2"; new="$3"
  cp tests/ci_ratchet.py /tmp/orig.py
  python3 - "$old" "$new" <<'P'
import sys;p='tests/ci_ratchet.py';s=open(p).read();o,n=sys.argv[1],sys.argv[2]
assert s.count(o)==1,(o,s.count(o));open(p,'w').write(s.replace(o,n))
P
  st=$(python3 tests/ci_ratchet.py --self-test 2>&1 | grep -cE "^\s*FAIL"); last=$(python3 tests/ci_ratchet.py --self-test 2>&1|tail -1)
  rp=$(python3 dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py 2>&1|tail -1)
  echo "MUTANT $name: self-test FAIL lines=$st | $last | replay: $rp"
  cp /tmp/orig.py tests/ci_ratchet.py; }
run median-to-max 'floor = statistics.median(seen) * OTHER_WORK_FRACTION' 'floor = max(seen) * OTHER_WORK_FRACTION'
run median-to-min 'floor = statistics.median(seen) * OTHER_WORK_FRACTION' 'floor = min(seen) * OTHER_WORK_FRACTION'
run floor-removed 'price[name] = min(w for w in seen if w >= floor)' 'price[name] = min(seen)'
run priced-not-skipped '"priced": j.get("conclusion") == "success"' '"priced": j.get("conclusion") != "skipped"'
run priced-all '"priced": j.get("conclusion") == "success"' '"priced": True'
run no-conclusion-guard 'if not j.get("conclusion"):' 'if False:'
run price-max 'price[name] = min(w for w in seen if w >= floor)' 'price[name] = max(w for w in seen if w >= floor)'
run fraction-half 'OTHER_WORK_FRACTION = 1 / 3' 'OTHER_WORK_FRACTION = 1 / 2'
git status --short
