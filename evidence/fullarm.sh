#!/bin/bash
set -u
cd /tmp/rev2853-def || exit 2
. /tmp/rev2853-tools/claims_block.sh
export CLAIMS_GEN CLAIMS_INPUTS CLAIMS_DOCS
T=$(mktemp -d)
printf 'docs/architecture.md\n' > "$T.paths"
git archive HEAD | tar -x -C "$T"
echo "full-copy KB: $(du -sk "$T" | cut -f1)"
echo "== the same commit eb7e1dee2, full-tree copy (what step 6g did before this PR):"
claims_reg_line "$T.paths" "$T"; echo "rc=$?"
echo "== and the narrow copy at the same commit, for the contrast:"
N=$(mktemp -d); printf 'docs/architecture.md\n' > "$N.paths"
git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$N"
echo "narrow-copy KB: $(du -sk "$N" | cut -f1)"
claims_reg_line "$N.paths" "$N"; echo "rc=$?"
rm -rf "$T" "$T.paths" "$N" "$N.paths"
