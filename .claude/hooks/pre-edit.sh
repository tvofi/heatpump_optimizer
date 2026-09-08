#!/bin/bash
# PreToolUse on Edit|Write|MultiEdit|NotebookEdit.
#
# WHAT IT REFUSES, and why each is here rather than in prose. Every one of these
# is a rule the corpus already states and nothing enforced at the moment it is
# broken -- the cheapest detector for "a branch moved VERSION" was the release
# stamp, which is forty minutes and one merge away.
#
#   VERSION, the manifest version, a RELEASE_NOTES.md heading, off `main`
#       CLAUDE.md rule 4: versions are assigned after the merge by
#       tools/release/stamp.py. On `main` the stamp itself does this, so the
#       branch check is the whole condition.
#   .cursor/rules/**
#       Generated from .claude/rules/ by rules_sync.mjs and byte-compared by
#       --check. A hand edit is reverted by the next generation and fails CI in
#       between; the source is one directory away.
#
# IT FAILS OPEN. Anything this script cannot parse, resolve or understand exits
# 0. A hook that guesses wrong blocks every seat in the repository on a file it
# misread, and the checks it stands in for all still run in CI. Exit 2 is
# reserved for a path this script has positively identified.
#
#   .claude/hooks/pre-edit.sh --self-test
#
set -uo pipefail

SELF_TEST=0
[ "${1:-}" = "--self-test" ] && SELF_TEST=1

# The payload is JSON on stdin: {"tool_name": "...", "tool_input": {"file_path": "..."}}.
# Parsed with python3 rather than a regex, because a file path containing a
# quote or a backslash is escaped in the JSON and a regex would take the escape
# as the path.
# THE PAYLOAD ARRIVES AS AN ARGUMENT, NOT ON STDIN, and the first draft of this
# file got that wrong in a way worth keeping the note for: `python3 - <<'PY'`
# makes the HEREDOC stdin, so `json.load(sys.stdin)` read the end of its own
# program, threw, and fell open. Every refusal was inert. The self-test's four
# refusal cases failed on the first run; its nine ALLOW cases all passed, and
# passed vacuously. A null control cannot see this class -- only the direction
# that demands an answer can.
decide() { # $1 branch, $2 the raw payload; stdout: a refusal message, or nothing
  python3 - "$1" "$2" <<'PY'
import json, sys, os
branch = sys.argv[1]
try:
    payload = json.loads(sys.argv[2])
except Exception:
    sys.exit(0)                      # unparseable -- fail open
ti = payload.get("tool_input") or {}
if not isinstance(ti, dict):
    sys.exit(0)
p = ti.get("file_path") or ti.get("notebook_path") or ""
if not isinstance(p, str) or not p:
    sys.exit(0)
root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
try:
    rel = os.path.relpath(os.path.realpath(p), os.path.realpath(root))
except Exception:
    sys.exit(0)
if rel.startswith(".."):
    sys.exit(0)                      # outside the repository -- not ours to judge
rel = rel.replace(os.sep, "/")

STAMPED = ("VERSION", "custom_components/heatpump_optimizer/manifest.json")
if rel in STAMPED and branch != "main":
    print(f"{rel} is assigned after the merge by tools/release/stamp.py, and this "
          f"branch is '{branch}'. CLAUDE.md rule 4. The stamp refuses a branch that "
          f"moved it, which is a forty-minute way to learn this.")
    sys.exit(1)

if rel == "RELEASE_NOTES.md" and branch != "main":
    # Only the HEADING is stamped; a branch may add body lines under an
    # existing one. So this reads what is being written rather than the path.
    text = " ".join(str(v) for k, v in ti.items()
                    if k in ("new_string", "content", "new_source"))
    if any(l.lstrip().startswith("## ") for l in text.splitlines()):
        print("RELEASE_NOTES.md's version heading is written by "
              "tools/release/stamp.py after the merge, and this branch is "
              f"'{branch}'. CLAUDE.md rule 4. Body lines under an existing "
              "heading are fine; a new `## ` heading is not.")
        sys.exit(1)

if rel.startswith(".cursor/rules/"):
    print(f"{rel} is GENERATED from .claude/rules/ by "
          "node .claude/workflows/rules_sync.mjs, and byte-compared by --check. "
          "Edit the .claude/rules/ source and regenerate; a hand edit here is "
          "reverted by the next generation and fails `policy-docs` in between.")
    sys.exit(1)
PY
}

if [ "$SELF_TEST" = 1 ]; then
  # A check that cannot be shown failing does not merge. Each case drives
  # `decide` with a payload and asserts whether it produced a refusal -- and the
  # null controls are half the point: a hook that refuses everything is not a
  # working hook, it is a broken repository.
  pass=0; fail=0
  st() { # want(refuse|allow), branch, payload, label
    out=$(decide "$2" "$3")
    got=allow; [ -n "$out" ] && got=refuse
    if [ "$got" = "$1" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$4"
    else fail=$((fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$4" "$got" "$1"; fi
  }
  R=$(pwd)
  st refuse feature "{\"tool_input\":{\"file_path\":\"$R/VERSION\"}}"                                   "VERSION on a branch is refused"
  st allow  main    "{\"tool_input\":{\"file_path\":\"$R/VERSION\"}}"                                   "VERSION on main is allowed (the stamp runs there)"
  st refuse feature "{\"tool_input\":{\"file_path\":\"$R/custom_components/heatpump_optimizer/manifest.json\"}}" "the manifest on a branch is refused"
  st refuse feature "{\"tool_input\":{\"file_path\":\"$R/.cursor/rules/gate-scoping.mdc\"}}"            "a generated Cursor rule is refused"
  st refuse main    "{\"tool_input\":{\"file_path\":\"$R/.cursor/rules/gate-scoping.mdc\"}}"            "and on main too -- generation is not branch-dependent"
  st refuse feature "{\"tool_input\":{\"file_path\":\"$R/RELEASE_NOTES.md\",\"new_string\":\"## v9.9.9\\n\"}}" "a new RELEASE_NOTES heading on a branch is refused"
  st allow  feature "{\"tool_input\":{\"file_path\":\"$R/RELEASE_NOTES.md\",\"new_string\":\"- a body line\\n\"}}" "a body line under an existing heading is allowed"
  st allow  feature "{\"tool_input\":{\"file_path\":\"$R/.claude/rules/gate-scoping.md\"}}"             "the SOURCE rule is allowed (null control)"
  st allow  feature "{\"tool_input\":{\"file_path\":\"$R/custom_components/heatpump_optimizer/const.py\"}}" "ordinary production code is allowed (null control)"
  st allow  feature '{"tool_input":{"file_path":"/etc/passwd"}}'                                        "a path outside the repository is not ours to judge"
  st allow  feature 'not json at all'                                                                   "an unparseable payload fails OPEN"
  st allow  feature '{"tool_input":{}}'                                                                 "a payload with no path fails OPEN"
  st allow  feature '{"tool_input":[]}'                                                                 "a payload whose tool_input is not an object fails OPEN"
  # AND THE SCRIPT ITSELF, end to end, over its real stdin. Every case above
  # drives `decide`; none of them touches the wrapper that reads the payload,
  # asks git for the branch and turns a message into an exit status -- which is
  # exactly where this hook was inert while the cases above all passed. Two
  # cases are enough, and both are branch-independent so neither needs a test
  # seam in production code: a generated file is refused on every branch, and
  # production code is allowed on every branch.
  e2e() { # want-rc, payload, label
    printf '%s' "$2" | CLAUDE_PROJECT_DIR="$R" bash "$0" >/dev/null 2>&1
    local got=$?
    if [ "$got" -eq "$1" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$3"
    else fail=$((fail+1)); printf '  FAIL %s (rc %s, wanted %s)\n' "$3" "$got" "$1"; fi
  }
  e2e 2 "{\"tool_input\":{\"file_path\":\"$R/.cursor/rules/gate-scoping.mdc\"}}" "END TO END: a generated Cursor rule exits 2"
  e2e 0 "{\"tool_input\":{\"file_path\":\"$R/custom_components/heatpump_optimizer/const.py\"}}" "END TO END: production code exits 0 (null control)"

  printf '\n%s passed, %s failed\n' "$pass" "$fail"
  [ "$fail" -eq 0 ] || exit 2
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
BRANCH=$(git branch --show-current 2>/dev/null)
PAYLOAD=$(cat)
# NO `|| exit 0` HERE, and that is not a style choice. `decide` exits 1 when it
# has decided to refuse, so `MSG=$(decide ...) || exit 0` swallowed every
# refusal and this hook was inert in production while its self-test reported
# 13 passed -- the second time in this one file that the tested helper was
# right and the untested wrapper around it was not. The verdict is the OUTPUT;
# a crash produces none, which is the fail-open path.
MSG=$(decide "${BRANCH:-DETACHED}" "$PAYLOAD")
if [ -n "$MSG" ]; then
  printf 'pre-edit: %s\n' "$MSG" >&2
  exit 2
fi
exit 0
