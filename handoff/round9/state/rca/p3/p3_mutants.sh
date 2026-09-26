#!/bin/bash
# Re-introduce each round-9 P3 instance (and R7 D2-01) one at a time on the scratch fixed tree.
S=/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad
cd $S/rca-p3
run() {  # name file python-replace-old python-replace-new
  rm -rf $S/p3mut; mkdir -p $S/p3mut; cp -r $S/p3fixed/heatpump_optimizer $S/p3mut/
  /home/claude/venv314/bin/python - "$S/p3mut/heatpump_optimizer/$2" "$3" "$4" <<'P'
import sys
f, old, new = sys.argv[1:4]
s = open(f).read(); assert s.count(old) == 1, (f, old, s.count(old)); open(f, "w").write(s.replace(old, new, 1))
P
  echo "== MUTANT $1"
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python $S/proto/run_p3_block.py $S/p3mut 2>&1 | grep "^FAIL\|^RESULT" | cut -c1-400
}
run D14-s3-01 optimizer.py "capacity = params.dhw_tank_thermal_mass" "capacity = max(params.dhw_tank_thermal_mass, 1e-6)"
run D12-s2-03 optimizer.py "        ) / self.model.params.power_range_floored, 0.0, 1.0))" "        ) / max(p_range, 0.1), 0.0, 1.0))"
run D2-s2-81 optimizer.py "                + np.sum(overshoot_l ** 2) * 5.0
            ) + weight * (np.sum(undershoot_u) + np.sum(undershoot_l)) * _COMFORT_FLOOR_L1" "                + np.sum(overshoot_l ** 2) * 5.0
                + (np.sum(undershoot_u) + np.sum(undershoot_l)) * _COMFORT_FLOOR_L1
            )"
run R7-D2-01 thermal_model.py "                - q_buf_loss + wood_draw
            ) / C_buf
" "                - q_buf_loss + wood_draw
            ) / max(C_buf, 0.01)
"
