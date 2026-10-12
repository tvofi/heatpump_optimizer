#!/bin/bash
# a1 dispatch-arm harness (the round-9 closures pre-study): drives the
# closure-scope decide step's own shell -- extracted verbatim from
# .github/workflows/tests.yml at a ref, with GitHub's ${{ }} expressions
# substituted exactly as the runner substitutes them for a workflow_dispatch
# event -- against a fixture batch repository, for the three dispatch arms:
#
#   1. a batch whose diff touches no script's closure   -> skip (narrow arm)
#   2. a batch whose diff touches a recorded closure    -> scoped
#   3. a dispatch whose diff cannot be computed         -> full (fail closed)
#
# plus the base behaviour: at a ref where the closure-scope `if` excludes
# workflow_dispatch, no case is derived at all and the closures job runs the
# FULL arm for every dispatch whatever the diff.
#
# Usage:
#   tools/audit/seat/a1_dispatch_arms.sh <head-ref> <base-ref>
#
# The head ref is the one whose decide step is under test; the base ref
# supplies the fixture tree (tests/ only) the batch branch is cut from.
# EXPECTED RESULT: inert-only=skip closure-touching=scoped
# underivable=full base-if=off

repo_root() {
  local d="$1"
  if [ -f "$d" ]; then
    d=$(dirname "$d")
  fi
  d=$(cd "$d" && pwd) || return 1
  while [ "$d" != "/" ]; do
    if [ -f "$d/custom_components/heatpump_optimizer/manifest.json" ]; then
      printf '%s\n' "$d"
      return 0
    fi
    d=$(dirname "$d")
  done
  printf 'no repository root above %s\n' "$1" >&2
  return 1
}

set -u
HEAD_REF="${1:?head ref (the one whose decide step is under test)}"
BASE_REF="${2:?base ref (origin/main; supplies the fixture tree)}"
SRC=$(repo_root "$0") || exit 1
PY="${HPO_A1_PYTHON:-python3}"
"$PY" -c "import yaml" 2>/dev/null || {
  echo "a1_dispatch_arms: $PY has no PyYAML, which the workflow extraction" >&2
  echo "needs. Point HPO_A1_PYTHON at a seat interpreter" >&2
  echo "(tools/audit/seat/seat_venv.sh builds one); the decide step it" >&2
  echo "extracts also runs tests/closure.py, so that interpreter must parse" >&2
  echo "main's Python." >&2
  exit 2
}
WORK=$(mktemp -d "${TMPDIR:-/tmp}/hpo-a1-arms-XXXXXX")
trap 'rm -rf "$WORK"' EXIT

# The decide step's run script, verbatim, with GitHub's expressions
# substituted the way the runner does on a workflow_dispatch: event_name
# filled in, the pull_request/merge_group contexts empty.
extract() {
  local ref="$1" slug
  slug=$(echo "$ref" | cut -c1-8)
  git -C "$SRC" show "$ref:.github/workflows/tests.yml" > "$WORK/wf-$slug.yml"
  GITHUB_EVENT_NAME=workflow_dispatch "$PY" - "$WORK/wf-$slug.yml" <<'PY'
import os, re, sys, yaml
doc = yaml.safe_load(open(sys.argv[1]))
run = doc["jobs"]["closure-scope"]["steps"][2]["run"]
run = re.sub(r"\$\{\{\s*github\.event_name\s*\}\}",
             os.environ["GITHUB_EVENT_NAME"], run)
run = re.sub(r"\$\{\{[^}]*\}\}", "", run)
open(sys.argv[1] + ".sh", "w").write(run)
PY
}

# A fixture repo carrying the real tests/ tree of the base ref, plus a
# standalone clone playing origin, so refs/remotes/origin/main exists for
# the decide step's merge-base. Both repositories are built through the
# shared throwaway_git helper (tests/throwaway_git.sh, the shell twin of
# tests/throwaway_git.py), which writes auto-maintenance off into each
# repository's own config -- so the decide step's own git calls in the
# clone, which run without this harness's environment, are covered too --
# and this harness's own fixture calls run under throwaway_git_env.
. "$SRC/tests/throwaway_git.sh"
mkdir -p "$WORK/remote-tree"
git -C "$SRC" archive "$BASE_REF" tests | tar -x -C "$WORK/remote-tree"
(
  cd "$WORK/remote-tree"
  throwaway_git_init . -q -b main
  throwaway_git_env
  git add -A
  git -c user.name=w -c user.email=w@w commit -qm base
)
throwaway_git_clone -q "$WORK/remote-tree" "$WORK/repo"
cd "$WORK/repo"

run_decide() { # $1 label, $2 ref whose decide step runs
  local label="$1" ref="$2" rt case
  extract "$ref"
  rt="$WORK/rt-$label"; rm -rf "$rt"; mkdir -p "$rt"
  ( GITHUB_EVENT_NAME=workflow_dispatch RUNNER_TEMP="$rt" \
      GITHUB_OUTPUT="$rt/out" GITHUB_ENV="$rt/env" \
      PATH="$(dirname "$(command -v "$PY")"):$PATH" \
      bash "$WORK/wf-$(echo "$ref" | cut -c1-8).yml.sh" > "$rt/log" 2>&1 )
  case=$(grep -o 'case=[a-z]*' "$rt/out" | head -1 | cut -d= -f2)
  printf '  %-24s closure-scope case = %s\n' "$label" "${case:-<none derived>}"
}

arm() { # $1 label, $2 ref, $3.. spec files ("path=content")
  local label="$1" ref="$2" spec f; shift 2
  (
    throwaway_git_env
    git checkout -q -B "batch/test-$label" main
    for spec in "$@"; do
      f="${spec%%=*}"
      mkdir -p "$(dirname "$f")"; printf '%s\n' "${spec#*=}" > "$f"; git add -A
    done
    git -c user.name=w -c user.email=w@w commit -qm "batch: $label"
  )
  run_decide "$label" "$ref"
  ( throwaway_git_env; git checkout -q main )
}

echo "decide step at HEAD ($HEAD_REF):"
arm inert-only "$HEAD_REF" "SECURITY.md=some prose"
arm closure-touching "$HEAD_REF" "tests/harness.py=changed"
echo "  diff-underivable"
git update-ref -d refs/remotes/origin/main
run_decide diff-underivable "$HEAD_REF"
git update-ref refs/remotes/origin/main main
echo
echo "BASE ($BASE_REF): what a dispatch takes there"
git -C "$SRC" show "$BASE_REF:.github/workflows/tests.yml" > "$WORK/wf-base.yml"
"$PY" - "$WORK/wf-base.yml" <<'PY'
import sys, yaml
job = yaml.safe_load(open(sys.argv[1]))["jobs"]["closure-scope"]
on_dispatch = "workflow_dispatch" in str(job.get("if", ""))
print(f"  closure-scope runs on workflow_dispatch: {on_dispatch}")
print("  -> SCOPE_CASE empty -> the closures job takes the FULL arm, "
      "whatever the diff")
PY
