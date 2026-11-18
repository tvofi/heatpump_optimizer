#!/usr/bin/env bash
# Controls for vocabulary_drift.py: positive (the judged sites of D13-s2-01 and
# D13-s2-02 are listed), null (zero on a clean fixture), perturbation (+1 under
# a one-line drifting stage vocabulary appended to a copy of tools/plan/replan.py).
set -u
D=$(dirname "$0"); EN="python3 $D/vocabulary_drift.py"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
out=$($EN)
for want in "bus.sh:672 MECHANICAL_CLASSES  <>  .claude/workflows/web-fix-wave.js:175 VERDICT_CLASSES" \
            "web-fix-wave.js:272 VERDICT_RE" "policy_lint.mjs:6658 FRICTION_ID"; do
  grep -qF "$want" <<<"$out" && echo "positive: found $want" || echo "positive: MISSING $want"
done
mkdir -p "$T/clean"
printf 'COLOURS = ("red", "green", "blue")\nSIZES = ["s", "m", "l"]\nSTATUS_RE = "^(ok|fail)$"\n' > "$T/clean/a.py"
printf 'const COLOURS = ["red", "green", "blue"];\n' > "$T/clean/b.mjs"
echo "null: $($EN "$T/clean" | tail -1)"
mkdir -p "$T/pkg/tools" "$T/pkg/.claude"; cp -r tools/. "$T/pkg/tools/"; cp -r .claude/workflows .claude/hooks "$T/pkg/.claude/"
base=$($EN "$T/pkg/tools" "$T/pkg/.claude/workflows" "$T/pkg/.claude/hooks" | tail -1)
echo 'ROSTER_STAGES = ("fix", "merge", "in-review")' >> "$T/pkg/tools/plan/replan.py"
echo "perturb (one drifting stage list in replan.py): $base -> $($EN "$T/pkg/tools" "$T/pkg/.claude/workflows" "$T/pkg/.claude/hooks" | tail -1)"
