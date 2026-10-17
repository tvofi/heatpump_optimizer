#!/usr/bin/env bash
# ARCH2-s5: the scoped gate and tests/structure.py with every prototype patch applied, then the
# tree restored. Run from the repository root with the seat python first on PATH.
#
#   PATH=$HOME/.local/state/hpo/bin:$PATH bash dev/audit/rounds/round10/D7/arch2-s5/gate_union.sh [BASE]
set -u
BASE=${1:-9061fbd3d}
D=dev/audit/rounds/round10/D7/arch2-s5
P=$D/patches
ALL="C1_textwidth_owner C2_setup_slot_deep_link C3_reading_rules C4_empty_state_and_finite_owner F1_wizard_widgets_from_registry"
ROOT=$(mktemp -d "${TMPDIR:-/tmp}/arch2-s5-gate.XXXXXX")
echo "logs: $ROOT"
for n in $ALL; do patch -p1 -s -f --no-backup-if-mismatch -i "$P/$n.patch" || exit 3; done
PYTHONPATH=tests/hastub python3 tests/structure.py > "$ROOT/structure.log" 2>&1
echo "RESULT structure_rc=$? $(grep -c '^ *ok' "$ROOT/structure.log") ok-lines; $(grep -ciE 'fail|over budget' "$ROOT/structure.log") fail-lines"
GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF="$BASE" HPO_PLANDATA="$ROOT/plandata.json" ./tests/run.sh > "$ROOT/gate.log" 2>&1
echo "RESULT gate_rc=$?"
grep -E "MODE:|^(PASS|FAIL)|FAILED|passed|failed" "$ROOT/gate.log" | tail -40
for n in F1_wizard_widgets_from_registry C4_empty_state_and_finite_owner C3_reading_rules C2_setup_slot_deep_link C1_textwidth_owner; do
  patch -R -p1 -s -f --no-backup-if-mismatch -i "$P/$n.patch"
done
git checkout -q -- tools/audit/round4/D6 dev/audit/rounds/round4/D6 2>/dev/null
git diff --quiet -- custom_components && echo "RESULT production_files_restored=1" || echo "RESULT production_files_restored=0"
