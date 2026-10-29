#!/bin/bash
# usage: mut.sh name file sed-expr
set -u
H=a5b8603b2fd49196105b4238a205b39a038f6944
d=$SCRATCH/m_$1; rm -rf $d; mkdir -p $d
git -C $REPO archive $H | tar -x -C $d
if [ -n "$3" ]; then before=$(md5sum < $d/$2); sed -i "$3" $d/$2; after=$(md5sum < $d/$2); [ "$before" = "$after" ] && { echo "MUTANT $1 DID NOT APPLY"; exit 2; }; git -C $REPO diff --no-index --stat /dev/null /dev/null; diff <(git -C $REPO show $H:$2) $d/$2; fi
cd $d && timeout 900 python3 tools/audit/seat/features_block.py "# Single-zone behind a valve, the reference's charge" "_tz_kw = _two_zone_rad_demand()" 2>&1 | tail -4
echo "RESULT $1 rc=${PIPESTATUS[0]}"
