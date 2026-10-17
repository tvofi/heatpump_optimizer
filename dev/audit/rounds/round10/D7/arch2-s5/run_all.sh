#!/usr/bin/env bash
# ARCH2-s5: every number in the report, re-taken.
#
#   PY=<python 3.14> bash dev/audit/rounds/round10/D7/arch2-s5/run_all.sh [score|card|flow|shapes]...
#
# score   delta_S per patch (main), the union, F1 on main + ARCH-s2's 08 patch; each with the
#         reverse-patch perturbation (arch_delta.py)
# shapes  the card shape census at main and with each patch applied (card_shapes.mjs)
# card    every card patch alone and the union through the card instruments (card_checks.sh,
#         on a scratch copy of the card so the working tree is restored afterwards)
# flow    wizard_widgets.py at main, with F1, and both under the --bump perturbation
# Default: all four. Run from the repository root; logs under a mktemp -d root.
set -u
BASE=${BASE:-9061fbd3d}
PY=${PY:-python3}
D=dev/audit/rounds/round10/D7/arch2-s5
P=$D/patches
CARD=custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
FLOW=custom_components/heatpump_optimizer/config_flow.py
CARD_PATCHES="C1_textwidth_owner C2_setup_slot_deep_link C3_reading_rules C4_empty_state_and_finite_owner"
OUT=$(mktemp -d "${TMPDIR:-/tmp}/arch2-s5-run.XXXXXX")
echo "logs: $OUT"
[ $# -eq 0 ] && set -- score shapes card flow

with_patches() {  # with_patches "<names>" <command...>: apply, run, always reverse
  local names=$1; shift
  for n in $names; do patch -p1 -s -f --no-backup-if-mismatch -i "$P/$n.patch" || return 3; done
  "$@"; local rc=$?
  for n in $(echo "$names" | tr ' ' '\n' | tail -r 2>/dev/null || echo "$names" | tr ' ' '\n' | tac); do
    patch -R -p1 -s -f --no-backup-if-mismatch -i "$P/$n.patch"
  done
  return $rc
}

for job in "$@"; do
  case $job in
  score)
    for n in $CARD_PATCHES F1_wizard_widgets_from_registry; do
      echo "== score $n"
      PYTHONPATH=tests/hastub "$PY" $D/arch_delta.py --base "$BASE" "$P/$n.patch" > "$OUT/score_$n.log" 2>&1
      grep -E '^RESULT (delta_S|admissible|perturbed|[a-z_]+=[0-9]+->)' "$OUT/score_$n.log"
    done
    echo "== score union"
    PYTHONPATH=tests/hastub "$PY" $D/arch_delta.py --base "$BASE" \
      $(for n in $CARD_PATCHES F1_wizard_widgets_from_registry; do echo "$P/$n.patch"; done) > "$OUT/score_union.log" 2>&1
    grep -E '^RESULT (delta_S|admissible|perturbed|[a-z_]+=[0-9]+->)' "$OUT/score_union.log"
    echo "== score F1 over ARCH-s2 08"
    PYTHONPATH=tests/hastub "$PY" $D/arch_delta.py --base "$BASE" \
      --overlay $D/overlay/arch-s2_08_options_page_template.patch "$P/F1_wizard_widgets_from_registry.patch" > "$OUT/score_F1_s2.log" 2>&1
    grep -E '^RESULT (overlays|delta_S|admissible|perturbed|[a-z_]+=[0-9]+->)' "$OUT/score_F1_s2.log"
    ;;
  shapes)
    echo "== shapes main"; node $D/card_shapes.mjs "$CARD" | grep RESULT
    for n in $CARD_PATCHES; do
      echo "== shapes $n"; with_patches "$n" node $D/card_shapes.mjs "$CARD" | grep RESULT
    done
    echo "== shapes union"; with_patches "$CARD_PATCHES" node $D/card_shapes.mjs "$CARD" | grep RESULT
    ;;
  card)
    for n in $CARD_PATCHES; do
      echo "== card $n"; with_patches "$n" bash $D/card_checks.sh origin/main
    done
    echo "== card union"; with_patches "$CARD_PATCHES" bash $D/card_checks.sh origin/main
    ;;
  flow)
    echo "== flow main"; PYTHONPATH=tests/hastub "$PY" $D/wizard_widgets.py --all | grep RESULT
    echo "== flow main --bump heat_pump_cop_nominal"
    PYTHONPATH=tests/hastub "$PY" $D/wizard_widgets.py --bump heat_pump_cop_nominal | grep -E 'RESULT (spelled|disagree)|DISAGREES'
    echo "== flow F1"; with_patches F1_wizard_widgets_from_registry env PYTHONPATH=tests/hastub "$PY" $D/wizard_widgets.py --all | grep RESULT
    echo "== flow F1 --bump heat_pump_cop_nominal"
    with_patches F1_wizard_widgets_from_registry env PYTHONPATH=tests/hastub "$PY" $D/wizard_widgets.py --bump heat_pump_cop_nominal | grep -E 'RESULT (spelled|disagree)|DISAGREES'
    ;;
  esac
done
git diff --quiet -- "$CARD" "$FLOW" && echo "RESULT production_files_restored=1" || echo "RESULT production_files_restored=0"
