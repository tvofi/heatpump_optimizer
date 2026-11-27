cd /tmp/tmp.eoMwHtglNF/wt
m() { f=$1; old=$2; new=$3; name=$4
  cp "$f" /tmp/tmp.eoMwHtglNF/bak
  python3 - "$f" "$old" "$new" <<'P'
import sys; f,o,n=sys.argv[1:]; t=open(f).read(); assert t.count(o)==1, (o, t.count(o)); open(f,'w').write(t.replace(o,n))
P
  out=$(PYTHONPATH=tests/hastub python3 /tmp/tmp.eoMwHtglNF/ctl.py 2>&1 | head -1); rc=$?
  r=$(PYTHONPATH=tests/hastub python3 /tmp/tmp.eoMwHtglNF/ctl.py >/dev/null 2>&1; echo $?)
  echo "$name rc=$r :: $out"
  cp /tmp/tmp.eoMwHtglNF/bak "$f"
}
R=tests/replay.py
m $R "    if wall_s <= limit:" "    if True:" pred-true
m $R "    if wall_s <= limit:" "    if wall_s <= limit * 2:" pred-loose
m $R "    if cap_minutes is None:
        return [f\"no replay" "    if False:
        return [f\"no replay" none-not-red
m $R '(?:    .*\n|[ \t]*\n)*?' '(?:.*\n)*?' regex-loose
m $R 'REPLAY_HEADROOM_SHARE = 0.8' 'REPLAY_HEADROOM_SHARE = 1.0' share-1
m $R 'REPLAY_JOB_SETUP_S = 20.0' 'REPLAY_JOB_SETUP_S = 0.0' setup-0
m $R 'return draw["owner_s"] * budget / draw["owner_cpu_ratio"] + draw["rest_s"]' 'return draw["owner_s"] + draw["rest_s"]' budget-unscaled
m $R '"rest_s": 81.0}' '"rest_s": 0.0}' rest-0
m .github/workflows/tests.yml '    timeout-minutes: 60
    env:
      HPO_JOB_GRADES: nothing' '    timeout-minutes: 58
    env:
      HPO_JOB_GRADES: nothing' cap-58
m .github/workflows/tests.yml '    timeout-minutes: 60
    env:
      HPO_JOB_GRADES: nothing' '    timeout-minutes: 600
    env:
      HPO_JOB_GRADES: nothing' cap-600
git status --short
