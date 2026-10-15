#!/usr/bin/env bash
# ARCH2-s5: tests/card_browser.mjs (real Chromium geometry) on the working tree's card,
# then with the four card patches applied, then the tree restored.
#
#   PW_NODE_MODULES=<dir holding playwright 1.49.0> PY=<python> \
#     bash dev/audit/rounds/round10/D7/arch2-s5/browser_rig.sh
#
# card_browser.mjs resolves playwright with createRequire, so NODE_PATH points it at an
# existing install; the browsers come from the default playwright cache. Prints one RESULT
# line per arm with the exit code and the lane's last line.
set -u
D=dev/audit/rounds/round10/D7/arch2-s5
P=$D/patches
PY=${PY:-python3}
ROOT=$(mktemp -d "${TMPDIR:-/tmp}/arch2-s5-browser.XXXXXX")
export HPO_PLANDATA="$ROOT/plandata.json" NODE_PATH="${PW_NODE_MODULES:?set PW_NODE_MODULES}"
echo "logs: $ROOT"
PYTHONPATH=tests/hastub "$PY" tests/plan_view.py > "$ROOT/plan_view.log" 2>&1 || { echo "plan_view failed"; exit 2; }
node tests/card_browser.mjs > "$ROOT/main.log" 2>&1
echo "RESULT browser_main_rc=$? $(tail -1 "$ROOT/main.log")"
PATCHES="C1_textwidth_owner C2_setup_slot_deep_link C3_reading_rules C4_empty_state_and_finite_owner"
for n in $PATCHES; do patch -p1 -s -f --no-backup-if-mismatch -i "$P/$n.patch" || exit 3; done
node tests/card_browser.mjs > "$ROOT/union.log" 2>&1
echo "RESULT browser_union_rc=$? $(tail -1 "$ROOT/union.log")"
for n in C4_empty_state_and_finite_owner C3_reading_rules C2_setup_slot_deep_link C1_textwidth_owner; do
  patch -R -p1 -s -f --no-backup-if-mismatch -i "$P/$n.patch"
done
git diff --quiet -- custom_components && echo "RESULT production_files_restored=1" || echo "RESULT production_files_restored=0"
