#!/usr/bin/env bash
# R10-POLICY-LINT-FAMILY (dev/audit/rca/R10-RCA-RAISE-GATE-GRAMMAR.md, C2 and
# C3): does every path that writes the text the merge train reads refuse a
# budget raise whose body has no `## Raise justification`, before the train?
#
#   bash dev/audit/harnesses/r10_raise_paths.sh [<rev>]   (default HEAD)
#
# Builds a throwaway clone at <rev> (its tools are the ones measured), commits
# one cap raised by 1 in tests/structure_budgets.json on top, and points
# `origin` at a throwaway bare repository holding main=<rev> and
# handoff/r10-raise-paths=<the raise>, so nothing leaves this machine. Then
# drives each path with prepr/good.md's body (no section), and again with
# prepr/raise/good.md's (a section the gate accepts) as the null control:
#   prepr       `prepr.sh --body-check`, step 7's body_line (open_pr.sh's step 7)
#   body_push   `body_push.sh`, refused before its push (the push target is the bare repository)
#   body_patch  body_patch.sh's own `contract` function, extracted, `gh` stubbed to no reds
#   pr-contract the workflow's own `List the paths` and `Check the body` run blocks, read
#               out of .github/workflows/pr-contract.yml and run under bash -e
# Metric, one line per path and body:
#   PATH <name> body=<none|section> rc=<n> raise_errors=<n>
# raise_errors counts ERROR lines naming `Raise justification` or the raise;
# the other refusals a synthetic body draws (the predicted budget red, for one)
# are not this metric. pr-contract's blocks write /tmp/pr-*, as on a runner.
set -uo pipefail
ROOT=/Users/timmalmstrom/hpo-seats/r10s5/rev-2669/wt
REV=$(git -C "$ROOT" rev-parse "${1:-HEAD}") || exit 2
T=$(mktemp -d "${TMPDIR:-/tmp}/r10-raise-paths.XXXXXX")
trap 'rm -rf "$T"' EXIT
unset GITHUB_TOKEN GH_TOKEN
. "$ROOT/tests/throwaway_git.sh" # the one way a script builds a throwaway repository
throwaway_git_clone -q --shared --no-checkout "$ROOT" "$T/repo" || exit 2
(
throwaway_git_env
cd "$T/repo" && git checkout -q --detach "$REV" || exit 2
python3 - <<'PY' || exit 2
import json
p = "tests/structure_budgets.json"
d = json.load(open(p))
d["class_excess_loc"] += 1  # a cap the gate reads as raised when it goes up
open(p, "w").write(json.dumps(d, indent=2) + "\n")
PY
git commit -qam "a raise" && HEAD=$(git rev-parse HEAD)
throwaway_git_init "$T/origin.git" -q --bare
git push -q "$T/origin.git" "$REV:refs/heads/main" "$HEAD:refs/heads/handoff/r10-raise-paths" 2>/dev/null || exit 2
git remote set-url origin "$T/origin.git" && git fetch -q --prune origin '+refs/heads/*:refs/remotes/origin/*'
FX=$ROOT/tools/policy/fixtures/policy-rot/prepr
ZERO=0000000000000000000000000000000000000000
# The raise turns budget-raise-gate red until an approval, which prepr predicts;
# both bodies answer it, so the raise arm is the one refusal left to read.
# Forward-carry and Friction say none, so carry_audit (body_patch's second
# check) has nothing to route.
for b in none:good section:raise/good; do
  sed -e "s/$ZERO/$HEAD/" -e 's/^none$/`budget-raise-gate`: red until the owner approves this head; the raise is the change, and no cheaper detector applies./' \
    -e '/^## Forward-carry/,$d' "$FX/${b#*:}.md" > "$T/${b%%:*}.md"
  printf '## Forward-carry\n\nnone\n\n## Friction\n\nnone\n' >> "$T/${b%%:*}.md"
done
mkdir -p "$T/bin" && printf '#!/bin/sh\nexit 0\n' > "$T/bin/gh" && chmod +x "$T/bin/gh"
block() { # step name -> its run block, as the runner would execute it
  python3 -c 'import sys, yaml
for s in yaml.safe_load(open(sys.argv[1]))["jobs"]["pr-contract"]["steps"]:
    if s.get("name") == sys.argv[2]:
        print(s["run"])' .github/workflows/pr-contract.yml "$1"
}
count() { # out-file path body -> the metric; R10_RAISE_PATHS_KEEP=<dir> keeps each output
  [ -z "${R10_RAISE_PATHS_KEEP:-}" ] || cp "$1" "$R10_RAISE_PATHS_KEEP/$2-$3.txt"
  grep -cE '^ *ERROR .*(Raise justification|raises [0-9]+ cap|whether it raises a cap)' "$1"
}
for b in none section; do
  body=$T/$b.md
  bash tools/pr/prepr.sh --body-check "$body" > "$T/out" 2>&1; rc=$?
  echo "PATH prepr body=$b rc=$rc raise_errors=$(count "$T/out" prepr "$b")"
  bash tools/audit/seat/body_push.sh r10-raise-paths "$body" > "$T/out" 2>&1; rc=$?
  echo "PATH body_push body=$b rc=$rc raise_errors=$(count "$T/out" body_push "$b")"
  ( REPO=o/r; PATH="$T/bin:$PATH"
    eval "$(sed -n '/^contract() {/,/^}/p' tools/audit/seat/body_patch.sh)"
    contract '{"title": "fix: a raise", "user": {"login": "hpo-author[bot]"}}' "$REV" "$HEAD" "$body" ) > "$T/out" 2>&1; rc=$?
  echo "PATH body_patch body=$b rc=$rc raise_errors=$(count "$T/out" body_patch "$b")"
  cp "$body" /tmp/pr-body.md && printf 'hpo-author[bot]' > /tmp/pr-author.txt && printf 'budget-raise-gate\n' > /tmp/pr-reds.txt
  rm -f /tmp/pr-title.txt
  ( export PR_BASE=$REV PR_HEAD=$HEAD PR_TITLE="fix: a raise"
    bash -e -c "$(block 'List the paths this pull request changes')" >/dev/null &&
    bash -e -c "$(block 'Check the body against the contract')" ) > "$T/out" 2>&1; rc=$?
  echo "PATH pr-contract body=$b rc=$rc raise_errors=$(count "$T/out" pr-contract "$b")"
done
)
