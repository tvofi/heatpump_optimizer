#!/bin/sh
# R10-CI-LAYOUT P2b, units U1+U2+U7: the design's static null control
# (DESIGN-P2 section 10) over hassfest.yml, validate.yml and arch-score.yml,
# one closed map each.
#   sh dev/audit/harnesses/r10_ci_layout_p2_u1u2u7/unitcheck.sh [BASE]   (BASE default: origin/main)
# BEFORE is BASE's copy of each file. Want rc 0 on each line, and rc 1 on the
# plant: a job step added to hassfest.yml that no map names.
set -u
BASE=${1:-origin/main}
TAG=archive/probe/design-ci-rev4
H=dev/audit/harnesses/r10_ci_layout_p2_u1u2u7
D=$(mktemp -d "${TMPDIR:-/tmp}/hpo-unitcheck-XXXXXX")
trap 'rm -rf "$D"' EXIT
git show "$TAG:measure/rev/unitcheck2.py" > "$D/unitcheck2.py" || exit 2
U() { python3 -I "$D/unitcheck2.py" static "$@" 2>&1 | tail -1; }
for p in "hassfest hassfest" "validate validate" "arch-score arch_score"; do
  set -- $p
  git show "$BASE:.github/workflows/$1.yml" > "$D/$1.yml" || exit 2
  echo "$1.yml: $(U "$D/$1.yml" ".github/workflows/$1.yml" --map "$H/$2_map.json")"
done
printf '      - run: "true"\n' | cat .github/workflows/hassfest.yml - > "$D/p.yml"
echo "plant, an unmapped step added (want rc 1): $(U "$D/hassfest.yml" "$D/p.yml" --map "$H/hassfest_map.json")"
