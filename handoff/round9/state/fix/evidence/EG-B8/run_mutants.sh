#!/bin/bash
# Own mutants for R9-EG-B8: each applies one python edit to a worktree copy of HEAD and runs tests/features.py.
set -u
HEAD=$(git -C /home/claude/heatpump_optimizer rev-parse HEAD)
export PATH=/home/claude/venv/bin:$PATH OPENBLAS_CORETYPE=Haswell OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
run() {
  m=$1; file=$2; old=$3; new=$4
  wt=/home/claude/wt-$m; rm -rf $wt; git -C /home/claude/heatpump_optimizer worktree add -q --detach $wt $HEAD
  python3 - "$wt/$file" "$old" "$new" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1,(p,o); open(p,'w').write(s.replace(o,n))
PY
  (cd $wt && PYTHONPATH=tests/hastub python tests/features.py > /tmp/claude-0/ev/mut_$m.log 2>&1; echo "rc=$?" >> /tmp/claude-0/ev/mut_$m.log)
  { echo "== $m ($file)"; grep -E "^  FAIL|CHECKS FAILED|CHECKS PASSED|^rc=" /tmp/claude-0/ev/mut_$m.log | cut -c1-160; } >> /tmp/claude-0/ev/mutants.txt
  git -C /home/claude/heatpump_optimizer worktree remove --force $wt
}
: > /tmp/claude-0/ev/mutants.txt
O=custom_components/heatpump_optimizer/optimizer.py; D=custom_components/heatpump_optimizer/dhw_learning.py
run M1 $O "                blocked=h.dhw_blocked,
                step_weekdays=h.step_weekdays,
                holiday_flags=h.holiday_flags,
                wood_temps=wood_temps," "                step_weekdays=h.step_weekdays,
                holiday_flags=h.holiday_flags,
                wood_temps=wood_temps," &
run M2 $D "self.hourly_profile: list[float] = self.normalize_profile(
            params.dhw_hourly_draw_pattern
        )" "self.hourly_profile: list[float] = (
            params.dhw_hourly_draw_pattern.copy()
        )" &
wait
run M3 $D "        if abs(float(np.mean(out)) - 1.0) > 1e-12:" "        if False:" &
run M4 $D "out = raw if abs(avg - 1.0) <= 1e-12 else np.clip(raw / avg, lo, hi)" "out = np.clip(raw / avg, lo, hi)" &
wait
echo ALLDONE >> /tmp/claude-0/ev/mutants.txt
