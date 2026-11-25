#!/bin/bash
# M9: swap the free-heat gains split in _valve_flow_set's valve-fed branch; run the R11-SEAM block, unmutated and mutated, at a worktree.
set -u
wt=$1; tag=$2; out=$3
OLD='        free_heat_kw = (w_upper * r + w_lower * (1.0 - r)) * p.internal_gains / w_sum'
NEW='        free_heat_kw = (w_upper * (1.0 - r) + w_lower * r) * p.internal_gains / w_sum'
f=$wt/custom_components/heatpump_optimizer/thermal_model.py
cd $wt
run() { python3 tools/audit/seat/features_block.py "# R11-SEAM-two-zone-slab (#3713): a two-zone valve feeds the radiators and the" "# R11-VALVE-REFERENCE (carries 0, 1): a single-zone valve feeds the slab, which" > $out/$tag.$1.txt 2>&1; echo "$tag $1 rc=$?" >> $out/m9.summary.txt; }
git checkout -q -- $f; run unmutated
python3 - "$f" "$OLD" "$NEW" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1, s.count(o); open(p,'w').write(s.replace(o,n))
PY
git diff --stat -- $f >> $out/$tag.M9.diff.txt; git diff -- $f >> $out/$tag.M9.diff.txt
run M9
git checkout -q -- $f; git status --porcelain -- $f >> $out/$tag.restored.txt
echo "$tag DONE" >> $out/m9.summary.txt
