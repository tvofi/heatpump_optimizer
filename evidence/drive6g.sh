#!/bin/bash
# My instrument: drive step 6g's claims_reg_line (sourced verbatim from a given
# prepr.sh extraction) over a fixture, and report rc, the line, whether the
# fixture's unlisted target is present in the copy AFTER the run, and a manifest
# of the copy AFTER the run (so two variants' copies can be compared exactly).
# Usage: drive6g.sh <block-file> <fixture repo> <changed-paths file> <tag> [target]
set -uo pipefail
BLOCK=$1; FX=$2; CH=$3; TAG=$4; TARGET=${5:-}
. "$BLOCK"
export CLAIMS_GEN CLAIMS_DOCS
COPY=$(mktemp -d)
( cd "$FX" && git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" 2>/dev/null | tar -x -C "$COPY" )
PRE="n/a"; [ -n "$TARGET" ] && { [ -e "$COPY/$TARGET" ] && PRE=yes || PRE=no; }
out=$( cd "$FX" && claims_reg_line "$CH" "$COPY" ); rc=$?
POST="n/a"; [ -n "$TARGET" ] && { [ -e "$COPY/$TARGET" ] && POST=yes || POST=no; }
man=$(cd "$COPY" && find . -type f -print0 | xargs -0 shasum -a 256 2>/dev/null | sort -k2 | shasum -a 256 | cut -d' ' -f1)
echo "== $TAG rc=$rc target_before=$PRE target_after=$POST copy_files=$(cd "$COPY" && find . -type f | wc -l | tr -d ' ') manifest=$man"
echo "   line: $(tail -1 <<<"$out")"
rm -rf "$COPY"
