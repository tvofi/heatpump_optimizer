#!/usr/bin/env bash
# D4-s3 perturbation arms for m3_look.mjs, each on the states its finding names, all three
# viewports, both themes, en/de/sv. Base and perturbed arms run back to back with the same
# arguments; every number is a count (contention-immune).
#   HPO_PY=$HOME/venv-ci/bin/python3 bash dev/audit/rounds/round11/D4/s3/perturb.sh
# Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B10.
set -u
H="node dev/audit/rounds/round11/D4/s3/m3_look.mjs --vp=375,768,1280"
arm() { # name states perturb extra-args grep
  echo "== $1 ${3:-base}"
  $H --states="$2" ${3:+--perturb=$3} $4 2>&1 | grep -E "$5"
}
ERR=pin_fail,save_fail
arm err "$ERR" "" "--err=ha" "english_error|non_en_error"
arm err "$ERR" err_localize "--err=ha" "english_error|non_en_error"
arm err-null "$ERR" "" "--err=plain" "english_error|non_en_error"
ROW=score_open,score_open_typical,score_open_no_evidence,score_open_graded_pump,savings_open,folds_open
arm align "$ROW" "" "" "headline_rows|tile_row"
arm align "$ROW" tile_nowrap "" "headline_rows|tile_row"
TIP=tooltip_hover,shared_steps_hover,estimated_price_hover,layout_editing,picker_twins,setup_clear_armed
arm floor "$TIP" "" "" "below_floor"
arm floor "$TIP" tooltip_floor "" "below_floor"
ROLE=status_stale,status_fallback,live_default,draft_menu_open,pin_ok,pin_fail,save_ok,save_fail,wood_alert,health_page
arm role "$ROLE" "" "" "role_colour"
arm role "$ROLE" one_error_colour "" "role_colour"
TYPE=live_default_expanded,score_open,tooltip_hover,shared_steps_hover,savings_page,health_page,setup_two_tank,advisor_page,draft_menu_open,save_confirm
arm type "$TYPE" "" "" "offscale"
arm type "$TYPE" type_tokens "" "offscale"
arm type "$TYPE" space_snap "" "offscale"
