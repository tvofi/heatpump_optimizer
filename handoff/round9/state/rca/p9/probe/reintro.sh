#!/bin/bash
S=/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad/rca-p9
cd $S
export HPO_PLANDATA=$S/tmp/plandata.json NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers
for k in status_text_token confirm_fill menu_clamp picker_wrap now_temp_below estimated_label; do
  echo "=== reintroduce $k"; P9_SKIP=slot_hit_half_gap,$k node probe/run_grid.mjs $S/base probe/fixed.mjs 2>&1 | grep -E 'FAIL|wall|^P9 grid' -A1 | grep -v '^--'
done
echo "=== null: drop the status states from the catalogue"
P9_DROP=pin_ok,pin_fail,save_ok,save_fail,dhw_clamped,save_confirm,setup_clear_armed P9_SKIP=slot_hit_half_gap node probe/run_grid.mjs $S/base probe/fixed.mjs 2>&1 | grep -E 'FAIL|wall|^P9 grid' -A1 | grep -v '^--'
