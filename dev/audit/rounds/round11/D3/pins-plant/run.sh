#!/bin/bash
# R11-D3-PINS-plant mutation proof: each spec beside this file through the tracked mutant driver.
# Run from the repository root:  bash dev/audit/rounds/round11/D3/pins-plant/run.sh [spec-name ...]
# Every spec entry is one wave finding's one-line patch (D3 wave judge, a826f55f8c), its `old` widened
# by neighbouring lines until it occurs once; mutant_run.py runs its NULL mutant first. A KILLED line is
# a pin failing under the patch; the NULL line SURVIVED is the same command passing on the unedited tree.
set -u
here=dev/audit/rounds/round11/D3/pins-plant
fb="python3 tools/audit/seat/features_block.py"
block() {  # block NAME START END: emit the block's prelude, then run the block
  printf '%s' "PYTHONPATH=tests/hastub $fb --emit-prelude .prelude_$1.py '$2' '$3' >/dev/null && PYTHONPATH=tests/hastub $fb --prelude \"exec(open('.prelude_$1.py').read())\" '$2' '$3'"
}
cmd_of() {
  case $1 in
    guard_pins) echo "env PYTHONPATH=tests/hastub python3 tests/guard_pins.py";;
    features_defrost) echo "bash -c \"PYTHONPATH=tests/hastub $fb 'R.section(\\\"Defrost derate (item 14)\\\")' '# Weekly DHW windows: different days, different windows (owner request #3)'\"";;
    features_flow_bias) echo "bash -c \"PYTHONPATH=tests/hastub $fb --prelude 'from dataclasses import replace as _r9f41_replace' 'R.section(\\\"R9 N-clamp-range: the flow-lift bias' '# --- R9 N-future-instant'\"";;
    features_t3_hot_water) echo "bash -c \"$(block t3 'R.section("T3 — hot water' 'R.section("T3b' | sed 's/"/\\"/g')\"";;
    features_buffer_store) echo "bash -c \"$(block buf 'R.section("The optimizer can see the buffer tank' 'R.section("Mixing valve and the buffer tank as a store' | sed 's/"/\\"/g')\"";;
    features_batch) echo "bash -c \"$(block batch 'R.section("The batched trajectory' 'R.section("R9 vi-b' | sed 's/"/\\"/g')\"";;
  esac
}
names=${*:-guard_pins features_defrost features_flow_bias features_t3_hot_water features_buffer_store features_batch}
rc=0
for n in $names; do
  echo "== $n"
  python3 tools/audit/seat/mutant_run.py --spec "$here/$n.json" --cmd "$(cmd_of "$n")" || rc=1
done
exit $rc
