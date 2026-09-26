#!/bin/sh
# D4 verify-v1 driver: re-runs the finders' s1 Chromium harnesses (baseline, each perturbation, now null control).
# Metric definitions: the finders' own (sweep.mjs / layout_kbd.mjs headers). Counts, contention-immune; exact.
# Command (repo root): sh tools/audit/round9/D4/verify-v1/run_s1.sh <outdir>
# Expected at baseline 1936d5ca (evidence tree 6f51db2c): contrast 90->12, popup_out_cells 6->0, option_indistinct_pairs 8->0,
#   now_marker_collisions 24->0, null now 0; pipes_keyboard 0->12, pipes_click 12. Machine: G2-V1 4-core cloud box, Chromium 141.
# Thread pin: OMP/OPENBLAS/MKL/NUMEXPR/VECLIB=1. RESULT lines (thread_factor, load1, swapins) come from the harnesses.
set -e
O=${1:?outdir}; T=$(mktemp -d); mkdir -p "$O"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub TMPDIR=$T
export NODE_PATH=${NODE_PATH:-/home/claude/pwlane/node_modules} PLAYWRIGHT_BROWSERS_PATH=${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}
${PY:-/home/claude/venv/bin/python} tests/plan_view.py >/dev/null
ST=x_pin_ok,x_pin_fail,x_save_ok,x_save_fail,x_dhw_clamped,x_save_confirm,draft_dirty_menu_open,x_menu_right_edge,x_menu_right_edge_dhw,picker_open_filtered,x_live_default,x_live_default_expanded
node tools/audit/round9/D4/s1/layout_kbd.mjs > "$O/kbd_base.log" 2>&1
node tools/audit/round9/D4/s1/layout_kbd.mjs --perturb kbd > "$O/kbd_pert.log" 2>&1
node tools/audit/round9/D4/s1/sweep.mjs --no-keys --modes normal --states $ST > "$O/sw_base.log" 2>&1
for p in status_text_token menu_clamp picker_wrap now_temp_below; do
  node tools/audit/round9/D4/s1/sweep.mjs --no-keys --modes normal --states $ST --perturb $p > "$O/sw_$p.log" 2>&1
done
node tools/audit/round9/D4/s1/sweep.mjs --no-keys --modes normal --states expanded_plan,plan_inline > "$O/sw_null_now.log" 2>&1
grep -H RESULT "$O"/*.log
