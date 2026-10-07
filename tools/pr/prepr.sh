#!/bin/bash
# Pre-PR self-check: everything a seat can refuse about its own branch before it
# asks anyone to look at it.
#
# WHY THIS EXISTS. `preflight.sh` reads a body for unmeasured claims. Nothing
# read the BRANCH. The 2026-09 governance audit measured the result: 55 percent
# of review verdicts blocked, a mean of 1.79 review rounds and one pull request
# at eleven, and the blocking reasons were dominated by things a script can
# decide -- a stale head SHA in the body, a claim file that should have been
# byte-identical, a MODE line nobody read, a carry destination that did not
# exist. A reviewer is the most expensive way to discover any of those.
#
# Every step refuses on non-zero. Run it before opening a pull request; the
# `pr-contract` job in .github/workflows/governance.yml re-executes the steps
# that are re-executable in CI, so the PRE-PR line this prints is a claim and
# the re-execution is the proof.
#
#   tools/audit/prepr.sh [body.md] [intended-issue-numbers...]
#
# Self-test (used by the `pr-contract` job, and by anyone changing this file):
#
#   tools/audit/prepr.sh --self-test
#
set -uo pipefail
# This file. A seat runs `bash tools/pr/prepr.sh`; CI may restore the base
# copy at tools/audit/prepr.sh and run that instead. Reads of the script use
# the path it was invoked as.
PREPR_PATH=$0
cd "$(git rev-parse --show-toplevel)" || exit 2

# --- the push-order verdict --------------------------------------------------
# WHY THIS EXISTS. Step 7 below gates `## Head` against the LOCAL head, the one
# head that is certain at the moment a body is written. `pr-contract` gates it
# against the PULL REQUEST's head, which is the remote tip. The two disagree for
# exactly as long as a commit sits unpushed, and #691 spent that window in it: at
# head b2cfbc9 a `synchronize` run passed at 19:53:33Z and the `edited` run that
# setting the body fired failed 54 seconds later -- "`## Head` does not name
# b2cfbc9, which is the head this ran on" -- because the body named the newer
# local commit. This script was green in between. The check that exists to refuse
# a stale head could not see the one staleness that reaches CI.
#
# WARN RATHER THAN REFUSE on an unpushed head, and the reason is policy, not
# taste. .claude/skills/steward/SKILL.md S10 PRESCRIBES passing through this
# state: of the two available orders it chooses "edit, then push", precisely so
# that the one refused run lands on a commit being abandoned rather than on the
# head a reviewer will read. #691 is that arm working -- head b2cfbc9 carries a
# green run at 19:53:33Z and a refused one 54 seconds later, and 99ee4b9 became
# the head. A refusal here would refuse the prescribed order, which is worse
# than the defect it answers. So the warning states the INVARIANT the two arms
# turn on -- a push must follow this body edit, or the refusal stays on your
# head -- rather than an order that contradicts the skill.
#
# What IS refused is the state no push repairs: the branch's own remote branch
# already carrying commits this head does not, where `## Head` names a SHA that
# pushing will not make current, because there is nothing to push. An autofix
# commit (S1) is exactly that shape -- S10's closing paragraph says to correct
# `## Head` after the bot pushes, and nothing checked it.
#
# THE ARM'S PREMISE IS THE RELATIONSHIP; WHAT VARIES IS WHICH REF IS COMPARED.
# A fresh local commit leaves HEAD ahead of the branch's own remote branch and
# never behind it, so on the ordinary path the refusing arm has nothing to fire
# on -- and that holds only because the compared ref is
# `refs/remotes/<remote>/<branch>`, derived from the branch's OWN name, which is
# the local mirror of `refs/heads/<branch>`, which is the pull request's head
# ref. The first version of this check read `@{u}` instead, and `@{u}` is not
# that ref: `git checkout -b foo origin/main` with `branch.autoSetupMerge` unset
# -- git's own default -- sets `branch.foo.merge = refs/heads/main`, so `@{u}`
# is `origin/main`, `behind` counts MAIN's own new commits, and the arm refused
# branches with nothing wrong with them while telling them "no push makes
# `## Head` the pull request's head" -- false there, because a push to
# `refs/heads/foo` is exactly the thing that does. The #694 review measured the
# configuration live in this repository's own clone; re-derive rather than carry
# a count, because it moves whenever a seat pushes with `-u`, and the rule is
# `git config --get branch.<name>.merge` not equal to `refs/heads/<name>`.
# `pr_head_ref` below is the repair and `main-tracking.case` pins it.
#
# NO NETWORK, EVER. The counts come from `refs/remotes/<remote>/<branch>`, a
# local mirror; nothing here fetches, because a check that hangs or fails
# offline is run with `|| true` inside a week. The cost is stated rather than
# hidden: a mirror not updated since somebody else pushed makes this too QUIET,
# never too loud -- it can report `ok` where the remote has since moved on, and
# it cannot invent an unpushed commit. A mirror that was never fetched at all is
# quiet in the same direction: the branch reads as never pushed and reaches the
# skip arm rather than a refusal. `git fetch origin "$(git branch
# --show-current)"` beforehand is what buys certainty, and the ok line names the
# ref it compared so that line is not read as CI's agreement.
#
# Arguments are DATA, not a repository: the compared ref is a function of the
# branch's name and its remote, the verdict a function of that ref's sha and the
# two counts, and of nothing else -- so --self-test drives both from fixtures
# that need no commits built and no refs written.
pr_head_ref() { # branch name ('' or '-' when detached), remote ('' or '-' -> origin)
  case "${1:-}" in ''|-) return 1 ;; esac   # a detached HEAD is nobody's head ref
  case "${2:-}" in
    ''|-) printf 'origin/%s\n' "$1" ;;
    *)    printf '%s/%s\n' "$2" "$1" ;;
  esac
}

# Steps 3e-3g: the graders CI pins to the base, run on THIS head's copy.
#
# WHY THIS EXISTS. A job that restores its check source from the base --
# `git checkout "$PINNED" --` with PINNED = base.sha || github.sha -- grades a
# pull request with the BASE's copy of every pinned file, and main's push with
# the HEAD's. The two verdicts differ exactly when the diff touches a pinned
# path, and the pull request's own run cannot show the difference: at #1633
# (R1a) head a897272a a leads fixture in `check-wave-script.mjs` quoted
# `boost.py`, `codeowners_gap.py --check` refused 2 files on that head, and
# `policy-docs` was green because it read the base's `check-wave-script.mjs`.
# The push to main would have gone red; the fix reviewer running the check by
# hand was the only detector. `graders-head-copy` in tests.yml answers this
# shape for the tests/ graders, keyed on the GRADER changing; a pinned file
# that another grader reads as DATA is outside that key, and nothing here ran
# `codeowners_gap.py` at all.
#
# So both lists are read from the workflows, not written here: a grader added
# to a pinned job, or a path added to a pin, reaches this script with no edit
# to it, and `pinned_unrun` refuses a grader this script neither runs nor
# names in PINNED_ELSEWHERE with the reason it cannot.
# The reader FAILS CLOSED (#1637 review): a job that names PINNED in a shape it
# does not know is refused as unclassified, and a script named on a pinned
# job's run line with no interpreter on that logical line is refused as
# unparsed. A reader that only matched what it expected passed nine of
# thirteen one-job perturbations of governance.yml silently; the second
# review found two more, a YAML-equal file indented four spaces and PINNED
# renamed, so jobs are found at the file's own indent and any checkout from a
# ref counts as naming a pin.
PIN_AWK=$(cat <<'AWK'
function flush_job(   p) {
  if (job == "" && mentions)
    problems = problems "unclassified " jfile ": outside any job the reader found -- it names a pin or a checkout from one\n"
  if (job != "" && mentions && pinstyle != "both" && pinstyle != "pr")
    problems = problems "unclassified " jfile ":" job " -- it names a pin or a checkout from one, but has no `PINNED: ${{ github.event.pull_request.base.sha[ || github.sha] }}` line with a `git checkout \"$PINNED\" --` after it\n"
  if (job != "" && pinstyle == "both") {
    for (p in mentioned) if (!(p in invoked))
      problems = problems "unparsed " jfile ":" job " " p " -- named on a run line where no interpreter is read\n"
    for (p in invoked) graders[p] = 1
  }
  split("", mentioned); split("", invoked)
  job = ""; mentions = 0; pinstyle = ""; expr = ""; inpin = 0; buf = ""
}
FNR == 1 { flush_job(); injobs = 0; jind = ""; jfile = FILENAME }
# A job header is a key at the indent of the first key under `jobs:`, which
# YAML leaves to the file: two spaces here, four in an equal file.
injobs && /^ +[A-Za-z0-9_-]+:[[:space:]]*(#.*)?$/ {
  ind = $0; sub(/[^ ].*$/, "", ind)
  if (jind == "") jind = ind
  if (ind == jind) { flush_job(); job = $1; sub(/:$/, "", job); next }
}
/^[^ ]/ { flush_job(); injobs = ($0 ~ /^jobs:[[:space:]]*(#.*)?$/); jind = ""; next }
/^[[:space:]]*#/ { next }
{
  # A pin under another name is still a pin: a checkout that restores paths
  # from a ref counts as naming one, so a renamed PINNED is unclassified.
  if ($0 ~ /PINNED/ || $0 ~ /git (checkout|restore) [^#]*--/) mentions = 1
  # The merge queue's base sits between the two (round-9 process review item 2):
  # a `merge_group` run has no pull request and grades like one, never like main.
  if ($0 ~ /^[[:space:]]+PINNED:[[:space:]]*\$\{\{ github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)? \|\| github\.sha \}\}[[:space:]]*$/) expr = "both"
  else if ($0 ~ /^[[:space:]]+PINNED:[[:space:]]*\$\{\{ github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)? \}\}[[:space:]]*$/) expr = "pr"
  # A listed restore (R9-RO-2) names its pathspecs on the `git diff` line.
  if ($0 ~ /git (checkout|diff --name-only -z .*) "\$PINNED" --( |$)/) { if (expr != "") pinstyle = expr; inpin = 1; next }
  if (inpin) {
    s = $0
    while (match(s, q "[^" q "]+" q)) {
      if (pinstyle == "both") pins[substr(s, RSTART + 1, RLENGTH - 2)] = 1
      s = substr(s, RSTART + RLENGTH)
    }
    if ($0 !~ /\\[[:space:]]*$/) inpin = 0
    next
  }
  if (pinstyle != "both") next
  buf = buf " " $0
  if ($0 ~ /\\[[:space:]]*$/) next
  l = buf; buf = ""
  # A presence test runs nothing. `if test -f <old>` is that test on its own
  # line; a one-line `if test; then node` still has an interpreter and is parsed.
  if (l ~ /(^|[[:space:]])(test|\[) +-[efs] / && l !~ /(^|[^A-Za-z0-9_.\/-])(node|python|python3|bash|sh)([[:space:]]|$)/) next
  interp = (l ~ /(^|[^A-Za-z0-9_.\/-])(node|python|python3|bash|sh)([[:space:]]|$)/)
  s = l
  while (match(s, /[A-Za-z0-9_.\/-]+\.(mjs|py|sh|js)([^A-Za-z0-9_]|$)/)) {
    p = substr(s, RSTART, RLENGTH); sub(/[^A-Za-z0-9_]$/, "", p)
    mentioned[p] = 1; if (interp) invoked[p] = 1
    s = substr(s, RSTART + RLENGTH)
  }
}
END {
  flush_job()
  if (mode == "graders") for (p in graders) print p
  if (mode == "paths") for (p in pins) print p
  if (mode == "problems") printf "%s", problems
}
AWK
)
pin_read() { # mode (graders|paths|problems), workflow files
  local mode=$1; shift
  awk -v mode="$mode" -v q="'" "$PIN_AWK" "$@" | sort -u
}
pinned_graders() { pin_read graders "$@"; }  # each program a pinned job that also grades main runs
pinned_paths() { pin_read paths "$@"; }      # each pathspec those jobs restore from the base
PINNED_ELSEWHERE='
.claude/workflows/policy_lint_envmatrix.mjs builds the six environment shapes CI declares, 50 s here, and whether they hold depends on the host
tools/policy/policy_lint_envmatrix.mjs builds the six environment shapes CI declares, 50 s here, and whether they hold depends on the host
.claude/workflows/budget_raise_gate.py reads a review off the GitHub API, not the tree; this script never reaches the network
tools/policy/budget_raise_gate.py reads a review off the GitHub API, not the tree; this script never reaches the network
tests/coverage_ratchet.py needs the coverage payload of a full gate run; graders-head-copy runs the head copy on the pull request
'
# No `| grep -q` below: under `pipefail` a grep that exits on its first match
# can SIGPIPE the writer, and the pipeline then reads as no match: the first
# draft of this guard named a grader unrun on 27 of 200 runs. Here-strings
# have no writer; this form named none in 200. A local run is a call on an
# interpreter line after `rc=0`: not a comment, not the helpers above it.
pinned_unrun() { # this script, workflow files -> each pinned grader with no local path
  local self=$1; shift
  local g
  for g in $(pinned_graders "$@"); do
    awk -v g="$g" 'index($0, g " ") == 1 { f = 1 } END { exit !f }' <<<"$PINNED_ELSEWHERE" && continue
    awk -v g="$g" '/^rc=0$/ { on = 1; next }
      on && !/^[[:space:]]*#/ && /(^|[^A-Za-z0-9_.\/-])(node|python|python3|bash)[[:space:]]/ && index($0, g) { f = 1 }
      END { exit !f }' "$self" || printf '%s\n' "$g"
  done
}
# Step 3g's verdict: rc 0 and nothing printed, or rc 1 and the reason.
pinned_verdict() { # this script, workflow files
  local self=$1; shift
  local problems unrun
  problems=$(pin_read problems "$@")
  if [ -n "$problems" ]; then printf '%s\n' "$problems" | head -3; return 1; fi
  if [ -z "$(pinned_graders "$@")" ]; then
    echo "no pinned grader found -- the pin reader no longer matches the workflows"; return 1
  fi
  unrun=$(pinned_unrun "$self" "$@")
  if [ -n "$unrun" ]; then
    echo "no local path for: $(echo $unrun) -- run it below rc=0, or name it in PINNED_ELSEWHERE with the reason"; return 1
  fi
  return 0
}
# Steps 3f and 4's trigger: does a changed path fall under a pin? Git's
# pathspec glob, where `*` crosses `/`, or a directory and what is under it.
pinned_touched() { # file of changed paths, pins (one per line)
  local f p
  while IFS= read -r f; do
    while IFS= read -r p; do
      [ -n "$p" ] || continue
      # shellcheck disable=SC2053 -- $p is a pattern on purpose
      if [[ $f == $p || $f == "$p"/* ]]; then return 0; fi
    done <<<"$2"
  done <"$1"
  return 1
}

# Step 7a's whole body, so `--self-test` drives the code the step runs rather
# than a second copy of the command. A step wired into the run and demonstrated
# by a sibling command is a step nothing pins: the assertion passes while the
# call site names the wrong file, or no longer exists.
figures_check() { # body file
  if test -f .claude/workflows/figure_lint.mjs; then node .claude/workflows/figure_lint.mjs --pr-body "$1"; else node tools/policy/figure_lint.mjs --pr-body "$1"; fi
}

# Steps 6a and 6b: the two failures CI already repairs, refused before the push.
# `claims-autofix` and `closures-autofix` fire only after `fast` or `closures`
# has gone red, so every repair they make costs a gate run, a held-run approval
# and a bot commit on a head a reviewer may already be reading. In the week to
# 2026-09-24 they were the most frequent repairable reds (the census and its
# per-job tables are /mnt/project-files/ci-autofix/). The checks are CI's own
# commands, so this is the cheaper detector for the same refusal, never a
# second opinion, and the jobs stay as the backstop.
#
# CI's `fast` passes the MERGE BASE and names the head as CLAIM_HEAD, so the
# claim list is compared with its own fork point (#1361). Main's tip would
# refuse a docs-only branch whenever main moved its list after the fork, and
# pass one that inherits a list main later dropped -- the #1591 review
# measured 38 of 188 main commits moving a list. So the base is derived here,
# not passed in: a caller cannot hand it the tip.
claims_check() { # prints env_drift's verdict; rc 0 holds, 1 refused, 2 no base
  local base
  base=$(git merge-base origin/main HEAD 2>/dev/null) || { echo "no merge base with origin/main"; return 2; }
  CLAIM_HEAD=$(git rev-parse HEAD) PYTHONPATH=tests/hastub \
    python3 tests/env_drift.py --claims-only "$base"
}

# The remedy each refusal names, keyed on what env_drift printed: the two
# refusals want opposite repairs, so one fixed hint is wrong for one of them.
claims_remedy() { # env_drift output file
  local base; base=$(git merge-base origin/main HEAD 2>/dev/null)
  case "$(cat "$1")" in
    *"INHERITED CLAIMS"*) echo "run \`python3 tests/env_drift.py --drop-inherited $base\` and commit what it empties, the commit claims-autofix would push" ;;
    *"RECORD PR CLAIMS"*) echo "restore both claim files to $base's content: this branch claims nothing" ;;
    *) echo "run \`python3 tests/env_drift.py --claims-only $base\` for the whole refusal" ;;
  esac
}

# Which scripts this machine may record for the closure check. Python lanes
# record through `sys.addaudithook`, so any platform is sound for them; a node
# recording on a machine without strace is not the recording CI compares, and
# ci-autofix.md forbids it replacing a Linux one, so it is left to CI. A
# script the gate lease guards (`gate_lock.py needs-lease`: stress.py, which
# measures the machine) is left to CI too: a push is no place to wait on or
# break another seat's lease.
closure_lane() { # script, strace present (1 or 0)
  local one; one=$(mktemp)
  printf '%s\n' "$1" > "$one"
  if [ "$(python3 tests/gate_lock.py needs-lease "$one" 2>/dev/null)" = lease ]; then
    rm -f "$one"; echo needs-lease; return
  fi
  rm -f "$one"
  case "$1" in
    *.mjs|*.js) if [ "$2" = 1 ]; then echo record; else echo node-needs-linux; fi ;;
    *) echo record ;;
  esac
}

# The closures recorder's interpreter, resolved deliberately. WHY THIS EXISTS.
# derive_closures.sh records under `${PYTHON:-python3}`, the first python3 on
# PATH. On a seat whose PATH still resolves to pyenv 3.11 that interpreter
# cannot parse the tree -- the nested same-quote f-string in tests/entities.py
# is 3.12 syntax -- so the recording dies at compile, and step 6b refuses it
# as "failed while being recorded ... fix the script first": advice pointed at
# the wrong artifact, and R9-FR-3 and R9-WEB-5 each lost a full prepr pass to
# exactly that. The interpreter a recording runs under is a property of the
# recording, not of the shell it inherits (#1091/#1099/#1095 are the same
# class at the mypy census, where an unpinned interpreter fails rather than
# measuring), so it is resolved here, in one place, in this order:
#
#   1. $HPO_RECORDER_PYTHON -- an override in the style of HPO_TYPING_PYTHON.
#      CHECKED, never trusted and never skipped past: an override that cannot
#      parse the tree refuses the run, because a seat that named one asked for
#      it by name and silently recording under something else is the defect.
#   2. the seat venv tools/audit/seat/seat_venv.sh builds, whose pins are what
#      the recorded scripts import, at $HPO_STATE_DIR/venv-ci/bin/python3.
#   3. the ambient python3 -- the adaptation, not the default: a candidate is
#      kept only if it parses the tree, so a seat already running under a good
#      interpreter gets the recording it always got, byte-unchanged.
#
# None of those parsing the tree is a refusal naming the build command, before
# anything is recorded. A recording taken under an interpreter that cannot
# parse the tree is not a shorter recording but a wrong one, and the refusal
# a truncated recording produces ("fix the script first") is worse than none.
recorder_parses() { # candidate interpreter -> rc 0 when it parses every source the recorder may run or import
  "$1" - <<'PY' 2>/dev/null
import ast, pathlib, sys
bad = 0
for p in [*sorted(pathlib.Path("tests").glob("*.py")),
          *sorted(pathlib.Path("custom_components").rglob("*.py"))]:
    try:
        ast.parse(p.read_text(), filename=str(p))
    except SyntaxError:
        bad += 1
sys.exit(1 if bad else 0)
PY
}
recorder_python() { # -> the interpreter on stdout; rc 1 with the remedy when none parses
  local c state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
  if [ -n "${HPO_RECORDER_PYTHON:-}" ]; then
    if recorder_parses "$HPO_RECORDER_PYTHON"; then
      printf '%s\n' "$HPO_RECORDER_PYTHON"; return 0
    fi
    echo "\$HPO_RECORDER_PYTHON=$HPO_RECORDER_PYTHON cannot parse the tree -- point it at one that can or unset it, or build the seat venv: tools/audit/seat/seat_venv.sh"
    return 1
  fi
  for c in "$state/venv-ci/bin/python3" "python3"; do
    command -v "$c" >/dev/null 2>&1 || continue
    if recorder_parses "$c"; then printf '%s\n' "$c"; return 0; fi
  done
  echo "no interpreter that parses the tree was found (tried the seat venv at $state/venv-ci/bin/python3 and the ambient python3) -- build the seat venv: tools/audit/seat/seat_venv.sh"
  return 1
}

# The verdict over a directory of `--record-only` recordings. A recording's
# own `rc` is read from its JSON, as `closure.py merge` reads it for
# `skip-failed-recording`: derive_closures.sh echoes the recording WRAPPER's
# status, which is 0 when the script under it died (the #1591 review's G).
# A failed recording is refused as that, never as UNDER-SCOPED, whose remedy
# (re-derive) ci-autofix.md says records the same truncation.
closures_verdict() { # recording dir; prints one detail line; rc 0 covered, 1 refused
  local failed out
  failed=$(python3 - "$1" <<'PY'
import json, pathlib, sys
for p in sorted(pathlib.Path(sys.argv[1]).glob("*.json")):
    rec = json.loads(p.read_text())
    if rec.get("rc", 1) != 0:
        print(f"{rec.get('script', p.stem)} (exit {rec.get('rc')})")
PY
) || { echo "the recordings could not be read"; return 1; }
  if [ -n "$failed" ]; then
    echo "failed while being recorded: $(echo $failed) -- fix the script first; a re-derive would record the same truncation"
    return 1
  fi
  out=$(PYTHONPATH=tests/hastub python3 tests/closure.py check --in-dir "$1" --partial 2>&1) && {
    echo "scoped recordings are covered"; return 0; }
  echo "$(printf '%s\n' "$out" | grep -m1 'UNDER-SCOPED\|NOT A FILE') -- run \`./tests/derive_closures.sh --single <script>\` for each UNDER-SCOPED script and commit tests/closures.json, the commit closures-autofix would push"
  return 1
}

# Step 6d's whole body: tools/pr/ci_predict.py over the three-dot diff, read
# statically -- no test, recording or mutant runs, so it costs seconds where
# step 6b's recordings cost the scoped scripts' run time and are left to CI
# under the owner's heavy-scripts rule (2026-10-07). It predicts `closures`'s
# UNDER-SCOPED, INERT READS and NO RECORDING and entities' unclassified file,
# which R9-RO-11's pre-study measured reddening this round's fix heads after
# the handoff while the autofix jobs repaired none of them; those refuse. The
# `mutation` sites the diff adds are a WARNING, never a refusal: ci-autofix.md
# has `mutation-autofix` pin them after the push, so the step lists them into
# a file and step 7's `unpinned_line` asks the body for each one's disposition.
# Every PREDICT line prints above the step line; the step line is the last.
predict_line() { # base ref, [file the unpinned site keys are written to]; rc 0 none, 1 predicted, 3 skipped
  local out r
  if [ ! -f tools/pr/ci_predict.py ]; then
    echo "tools/pr/ci_predict.py is not in this tree"; return 3
  fi
  out=$(PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$1" 2>&1); r=$?
  [ -n "${2:-}" ] && printf '%s\n' "$out" \
    | sed -nE 's/^PREDICT mutation +ADDED UNPINNED ([^ ]+ [A-Z_]+): .*/\1/p' > "$2"
  case "$r" in
    0|1) printf '%s\n' "$out" | grep '^PREDICT' | sed 's/^/           /' >&2
         printf '%s\n' "$out" | tail -1; return "$r" ;;
    *) echo "the predictor did not run: $(printf '%s\n' "$out" | tail -1)"; return 1 ;;
  esac
}

# Step 7d's whole body: every unpinned site step 6d listed has a line under
# `## Unpinned sites` naming it by its `file:line KIND` key, with its
# disposition (pinned by `mutation-autofix`, a value check, or a written
# triage). rc 3 when no site is owed, so a body that adds none needs no section.
unpinned_line() { # body, site-key file; rc 0 disposed, 1 refused, 3 none owed
  local sec missing n
  n=$(grep -c . "$2" 2>/dev/null); n=${n:-0}
  if [ "$n" -eq 0 ]; then echo "the diff adds no unpinned mutation site"; return 3; fi
  sec=$(awk '/^## /{on=($0 ~ /^## Unpinned sites[[:space:]]*$/)} on' "$1")
  if [ -z "$sec" ]; then
    echo "$n unpinned site(s) the diff adds and no \`## Unpinned sites\` section -- give each its key and disposition"
    return 1
  fi
  missing=$(while read -r k; do grep -qF -- "$k" <<<"$sec" || printf '%s; ' "$k"; done < "$2")
  if [ -n "$missing" ]; then
    echo "\`## Unpinned sites\` omits: ${missing%; }"; return 1
  fi
  echo "\`## Unpinned sites\` disposes of all $n site(s) step 6d listed"
}

# Steps 6a and 6b whole, as the lines the step prints: the step is `step
# <name> $? <line>` over these, so `--self-test` drives the decisions the
# step makes rather than a copy of them (the #1591 review: 10 of 12 mutants
# of the call sites survived a self-test that drove only `closure_lane`).
claims_line() { # rc 0 holds, 1 refused
  local out r; out=$(mktemp)
  claims_check >"$out" 2>&1; r=$?
  if [ "$r" -eq 0 ]; then tail -1 "$out"
  else echo "$(grep -m1 -E '[A-Z]{4}' "$out") -- $(claims_remedy "$out")"; r=1; fi
  rm -f "$out"; return "$r"
}

# The recorder is `derive_closures.sh` unless PREPR_RECORD names another one
# taking the same arguments, which only `--self-test` does. rc 3 is a skip.
closures_line() { # merge base; rc 0 covered, 1 refused, 3 skipped
  local cw kind s v left="" strace=0 r=0 rp=""
  cw=$(mktemp -d)
  if git diff --name-only "$1"...HEAD > "$cw/changed.txt"; then
    python3 tests/closure.py affected --files-from "$cw/changed.txt" --workdir "$cw/aff" >/dev/null 2>&1
    kind=$(cat "$cw/aff/affected.case" 2>/dev/null)
  else
    kind=""
  fi
  case "$kind" in
    skip) echo "the diff reaches no selectable script's closure"; r=3 ;;
    full) echo "the diff cannot be scoped, so CI re-records every closure; a full derive here is forbidden"; r=3 ;;
    scoped)
      command -v strace >/dev/null && strace=1
      rp=""
      while read -r s; do
        [ -n "$s" ] || continue
        if [ "$(closure_lane "$s" "$strace")" != record ]; then left="$left $s"; continue; fi
        # Resolved on the first script this machine will actually record, so a
        # diff whose recordings are all left to CI owes no interpreter (and
        # `closure_lane` above still ran on the ambient python3 it always did).
        if [ -z "$rp" ]; then
          rp=$(recorder_python) || { echo "$rp"; r=1; break; }
        fi
        GOLDEN_REF=origin/main PYTHON="$rp" ${PREPR_RECORD:-./tests/derive_closures.sh} --single "$s" \
          --record-only --out-dir "$cw/rec" > "$cw/derive.out" 2>&1
      done < "$cw/aff/affected.scripts"
      if [ "$r" -eq 1 ]; then : # the interpreter refusal is already printed
      elif [ ! -d "$cw/rec" ]; then
        echo "nothing scoped can be recorded on this machine; left to CI:$left"; r=3
      else
        v=$(closures_verdict "$cw/rec"); r=$?
        echo "$v${left:+; left to CI:$left}"
      fi ;;
    *) echo "closure.py affected derived no case from $1...HEAD"; r=1 ;;
  esac
  rm -rf "$cw"; return "$r"
}

# Step 7's body check, and the path list the `## Approval` gate is keyed on.
# Same argument as `figures_check` above: the step calls these, so `--self-test`
# drives the code the step runs rather than a second copy of the command.
#
# WHY THE PATHS ARE PASSED AT ALL. `checkPrBody` requires a `## Approval`
# heading when the change is a policy change, and since R3-D11-03 that is keyed
# on the DIFF, not on the title -- a title is written by the same seat the
# section exists to constrain, so a one-word title change switched the
# requirement off. `pr-contract` passes `--paths-file`; this script passed
# `--pr-body`, `--head` and `--title` and nothing else, so `policyPaths` was
# empty on every branch and the requirement could not fire here at all. That is
# not a check that disagreed with CI: it is a check that reported `ok` on the
# one question it had no input for. #1053 is the cost -- the body passed this
# script, the push went out, and `pr-contract` refused it with "no `## Approval`
# section, and this diff touches `docs/HANDOVER.md`".
#
# THREE-DOT, AND `--no-renames`, FOR CI'S OWN TWO REASONS. `$BASE` is the merge
# base, so `"$BASE"...HEAD` names what the BRANCH changed; a two-dot diff
# against `origin/main` attributes main's own newer commits to the branch and
# would demand `## Approval` for a policy file the branch never touched. And a
# rename is reported by its DESTINATION only, so `--no-renames` is what keeps
# moving `CLAUDE.md` to `RENAMED.md` inside the gate rather than outside it.
#
# FAIL CLOSED, AND THE LOAD-BEARING KEY IS THE RETURN CODE. A range that does
# not resolve makes this return non-zero and the caller refuses instead of
# running the check: `policy_lint.mjs` refuses an empty `--paths-file` for the
# same reason, because an empty list reads as "touches no policy file", which is
# the fail-open the keying exists to close. A seat in a shallow clone must not be
# told its body is clean when nothing looked.
#
# THE ABSENCE OF THE FILE IS THE SECOND KEY, and it is deliberate rather than
# incidental. Writing straight to `$2` would truncate it before `git` ran, so a
# failed derivation left a 0-BYTE FILE behind -- measured at rc=128 with the file
# present, by the #1054 review. Nothing in this script keyed on the file, so that
# was harmless the day it was written and exactly the shape that stops being
# harmless later: a caller added afterwards, reading the list because it is
# there, would satisfy every assertion below while reading an empty diff as
# "touches no policy file". Writing through `.part` and renaming only on success
# makes both keys agree. If a later edit drops the rename, the return code is
# still the one a caller must read.
#
# THE CLEANUP IS UNCONDITIONAL, AND THAT IS THE #1054 REVIEW'S FINDING. The
# first form cleaned up only on the redirect's failure, so a failing `mv` left
# `.part` behind -- and the caller's cleanup names `$2`, not `$2.part`, so
# nothing removed it. 138 bytes, on a path that needs `mv` to fail. Removing it
# here rather than adding a word to the caller is the point: the function owns
# the temp file it invents, under every outcome, and no caller has to know the
# name exists. `rm` runs after `$?` is captured so it cannot overwrite the
# status being returned.
diff_paths() { # merge base, out file
  local rc
  git diff --no-renames --name-only "$1"...HEAD > "$2.part" 2>/dev/null \
    && mv -f "$2.part" "$2"
  rc=$?
  rm -f "$2.part"
  return "$rc"
}

body_check() { # body file, head sha, title, paths file, red names...
  # The red names ride the SAME flags CI's pr-contract job passes: one `--red`
  # per name, never a comma-joined value, so a check name containing a comma
  # reaches `## Red checks` whole (policy_lint splits only a LONE `--red`
  # value). Step 7's `body_line` passes `budget-raise-gate` when the diff
  # raises a budget leaf; step 7c passes every red the branch's pushed
  # commits carry -- one implementation, `policy_lint.mjs --pr-body`, decides
  # whether the body answers a red in both callers.
  local args=(--pr-body "$1" --head "$2" --title "$3" --paths-file "$4") n
  shift 4
  for n in "$@"; do args+=(--red "$n"); done
  if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs "${args[@]}"; else node tools/policy/policy_lint.mjs "${args[@]}"; fi
}

# --- the predicted head reds (#1951, R9-FR-12) ---------------------------------
# WHY THIS EXISTS. Every root-cause-unanswered block of the v6.7.16 window named
# a red standing at the reviewed head, and step 7c reads only commits already
# pushed, so it cannot see the first red the handoff push itself produces. Two
# of those reds are functions of the diff alone and are predicted here, before
# that push (pre-study R9-FR-1 round 2, section 3).
#
# THE BUDGET RED IS THE BASE'S GATE, RUN OFFLINE. `budget-raise-gate.yml`
# restores `.claude/workflows/*.py` from the base and runs `gate()`, which is
# red on any raise until the owner approves at the head. So the base's copy of
# budget_raise_gate.py is loaded and its own `gate()` run with the review read
# replaced by a refusal: the enumeration, the schema and `file_raises` are the
# gate's, never copied here, and no network is reached. Its `__file__` is this
# tree's path, so its `tests/layout.py` import is the head's, as in CI. A raise
# feeds one extra `--red budget-raise-gate` to `body_check`: the same body check
# pr-contract runs, fed one more name. A base without the gate, or a gate
# without `gate()`, is a skip; an answer that does not parse is a refusal,
# because a gate that ran and was not read is not a gate that found nothing.
raise_red() { # merge base, head -> one line; rc 0 no raise, 4 raised, 3 skipped, 1 unread
  local src out r n total
  src=$(mktemp)
  if git show "$1:.claude/workflows/budget_raise_gate.py" >"$src" 2>/dev/null \
     || git show "$1:tools/policy/budget_raise_gate.py" >"$src" 2>/dev/null; then
    :
  else
    rm -f "$src"
    echo "the merge base carries no budget_raise_gate.py, so no budget raise was predicted"
    return 3
  fi
  if [ -f "$PWD/tools/policy/budget_raise_gate.py" ]; then brg_home=$PWD/tools/policy/budget_raise_gate.py
  else brg_home=$PWD/.claude/workflows/budget_raise_gate.py; fi
  out=$(python3 -I - "$src" "$1" "$2" "$brg_home" 2>&1 <<'PY'
import sys, types
src, base, head, home = sys.argv[1:]
m = types.ModuleType("budget_raise_gate")
m.__file__ = home
sys.modules[m.__name__] = m
exec(compile(open(src).read(), f"{base[:12]}:.claude/workflows/budget_raise_gate.py", "exec"), m.__dict__)
for name in ("gate", "_reviews", "_mandate"):
    if not callable(getattr(m, name, None)):
        print(f"SKIP the merge base's budget_raise_gate.py has no {name}()")
        sys.exit(3)
def offline(*_a):
    raise RuntimeError("offline: prepr.sh never reads a review")
m._reviews = m._mandate = offline
sys.exit(m.gate(base, head, "0", "offline/offline"))
PY
); r=$?
  rm -f "$src"
  if [ "$r" -eq 3 ] && [ "${out#SKIP }" != "$out" ]; then echo "${out#SKIP }, so no budget raise was predicted"; return 3; fi
  total=$(printf '%s\n' "$out" | sed -n 's/^RESULT budget_raises=\([0-9][0-9]*\) count$/\1/p')
  n=$(printf '%s\n' "$out" | grep -c '^RAISE ')
  if [ -z "$total" ] || [ "$total" != "$n" ]; then
    echo "the base's budget_raise_gate.py answered without a readable RESULT line ($(printf '%s\n' "$out" | tail -1)), so the raises are UNREAD"
    return 1
  fi
  if [ "$n" -eq 0 ]; then echo "no budget leaf raised over $(git rev-parse --short "$1")...$(git rev-parse --short "$2")"; return 0; fi
  echo "$n budget raise(s), budget-raise-gate red until tvofi approves at the head: $(printf '%s\n' "$out" | sed -n 's/^RAISE //p' | head -1)"
  return 4
}

# Step 7's whole body: the predicted budget red, then the body check fed it.
# rc 0 the body answers, 1 refused.
body_line() { # body file, head sha, title, paths file, merge base, head
  local raised r out reds=()
  raised=$(raise_red "$5" "$6"); r=$?
  case "$r" in
    4) reds=(budget-raise-gate) ;;
    1) printf 'REFUSE: %s' "$raised"; return 1 ;;
  esac
  out=$(mktemp)
  body_check "$1" "$2" "$3" "$4" ${reds[@]+"${reds[@]}"} >"$out" 2>&1; r=$?
  if [ "$r" -eq 0 ]; then printf '%s -- %s' "$(tail -1 "$out")" "$raised"
  else printf '%s -- %s' "$(grep -m1 'does not name it' "$out" || tail -1 "$out")" "$raised"; fi
  rm -f "$out"; return "$r"
}

# THE COPY CLAIM IS CI'S OWN COMMAND. `tests.yml`'s closures job runs
# `tests/closure.py no-copies` on both arms and nothing local ran it: a diff
# that can introduce a copy -- a `.py` under tests/ (a new definition) or under
# custom_components/ (a new production name a test already defines) -- runs it
# here. The scan reads the whole tree, so its wall time is paid only then.
copies_line() { # tree root, changed-paths file -> one line; rc 0 clean, 1 a copy, 3 skipped
  local out r
  if ! grep -qE '^(tests|custom_components)/.*\.py$' "$2" 2>/dev/null; then
    echo "the diff changes no .py under tests/ or custom_components/, so no test can newly share a production name"
    return 3
  fi
  [ -f "$1/tests/closure.py" ] || { echo "no tests/closure.py under $1, so no-copies was not run"; return 3; }
  out=$(cd "$1" && PYTHONPATH=tests/hastub python3 tests/closure.py no-copies 2>&1); r=$?
  if [ "$r" -eq 0 ]; then printf '%s\n' "$out" | tail -1; return 0; fi
  echo "$(printf '%s\n' "$out" | grep -m1 '^COPY-CLAIMED' || printf '%s\n' "$out" | tail -1) ($(printf '%s\n' "$out" | grep -c '^COPY-CLAIMED') in all) -- import the production symbol instead (tests/README.md), or the closures job refuses it"
  return 1
}

# --- the ancestry red-check arm (#1860, R9-FR-2) -------------------------------
# WHY THIS EXISTS. defect-root-cause.md's enforced trigger fires on "a check
# that went red on a commit in the branch", but the push-time enforcement that
# existed read only the HEAD: `pr-contract` lists the head's check runs, and a
# red an earlier push carried and a later push cleared leaves no check-run
# record at the head at all -- so the fix reviewer was the first reader of it,
# at the most expensive moment. The round-9 friction sweep measured the class:
# `root-cause-unanswered` blocked 8 of W14's 14 merges, 6 of the 8 on reds a
# branch check-run sweep sees (pre-study R9-FR-1, #1860). This arm is that
# trigger moved to push time -- the cheaper detector the rule itself prefers.
#
# THE RED KEY IS pr-contract.yml's OWN ("List the red checks at this head"),
# reused verbatim rather than re-worded: status completed, conclusion failure,
# check-run name not `pr-contract` (this repository's only job by that name;
# an id-keyed exclusion would let its own red back in and deadlock), sorted
# unique. The refusal is the SAME body check's: step 7c feeds each name to
# `body_check` above as one `--red`, so one implementation decides whether the
# body answers a red, not two. The nightly-status/delivery-status exemption is
# deliberately NOT copied here: it already lives in policy_lint's `--pr-body`
# machinery, which the `--red` flags feed, and a second copy would drift.
#
# THE RANGE IS THE COMMITS THE REMOTE ALREADY HAS, derived through
# `pr_head_ref` (step 7b's rule, never `@{u}`): the branch's own remote branch
# is the local mirror of the pull request's head ref, so the arm reads exactly
# the history a reviewer of the pull request reads. A run before the first
# push has nothing to read and says so. policy_lint's own red-history
# derivation (inside `--pr-body`) covers the same range but only when a token
# sits in the environment -- CI's pr-contract step exports none and a seat's
# credential usually lives in `gh`'s store, which is exactly the gap this arm
# closes by asking `gh` itself.
#
# SKIP, NEVER REFUSE, AT EVERY BOUNDARY OF WHAT THE ARM CAN SEE: `gh` absent,
# no credential, origin not a GitHub remote, no merge base, nothing pushed, no
# pushed commit carrying any check run, or a read that failed. policy_lint's
# internal derivation REFUSES a failed read because it runs in CI holding a
# granted token; this arm runs on a seat at push time, where a hung or
# rate-limited call must not block a push, so it prints what went UNCHECKED
# instead -- the push-order arm's NO NETWORK argument, relaxed only to reads
# that print their own skip line. This is the CI determinism bound too: no
# job that re-executes this script exports a credential to it, so there the
# arm prints its skip line and stays local-only-deterministic, the position
# PREPR_SKIP_CLOSURES holds for the closures step.
REDS_JQ='.check_runs[]
         | select(.status == "completed" and .conclusion == "failure")
         | select(.name != "pr-contract")
         | .name'

gh_credential() { # gh binary -> the token on stdout, rc 1 when none
  case "${GITHUB_TOKEN:-}" in ?*) printf '%s' "$GITHUB_TOKEN"; return 0 ;; esac
  case "${GH_TOKEN:-}" in ?*) printf '%s' "$GH_TOKEN"; return 0 ;; esac
  command -v "$1" >/dev/null 2>&1 || return 1
  "$1" auth token 2>/dev/null
}

ancestry_reds() { # the branch's own remote head ref
  # -> rc 0: the red names, one per line, sorted unique
  #    rc 3: the skip reason (one line)
  local ghc tok url repo base shas sha out names any
  ghc=${PREPR_GH:-gh}   # --self-test replaces the gh binary word, argv identical
  command -v "$ghc" >/dev/null 2>&1 || { echo "gh is absent, so no branch check run could be read"; return 3; }
  tok=$(gh_credential "$ghc") || { echo "no token: GITHUB_TOKEN and GH_TOKEN are unset and \`$ghc auth token\` refuses, so no branch check run could be read"; return 3; }
  url=$(git remote get-url origin 2>/dev/null)
  case "$url" in
    *github.com:*) repo=${url##*github.com:} ;;
    *github.com/*) repo=${url##*github.com/} ;;
    *) repo="" ;;
  esac
  repo=${repo%.git}
  case "$repo" in */*) ;; *) echo "origin is not a GitHub remote, so no check run could be read"; return 3 ;; esac
  base=$(git merge-base origin/main HEAD 2>/dev/null) || { echo "no merge base with origin/main, so no ancestry could be enumerated"; return 3; }
  shas=$(git rev-list "$base..$1" 2>/dev/null) || { echo "$1 could not be read, so no ancestry was enumerated"; return 3; }
  [ -n "$shas" ] || { echo "no commit of this branch is on $1 yet -- the first push has no ancestry to read"; return 3; }
  names=""; any=""
  for sha in $shas; do
    out=$("$ghc" api --paginate "repos/$repo/commits/$sha/check-runs" --jq "$REDS_JQ" 2>/dev/null) || {
      echo "the check runs at $sha could not be read, so the ancestry reds are UNCHECKED this run, not confirmed empty"; return 3; }
    [ -n "$out" ] && { names="$names$out"$'\n'; any=1; }
  done
  if [ -z "$any" ]; then
    # Nothing failed anywhere: say whether that was MEASURED or merely
    # unpopulated -- a branch whose commits never ran CI owes no answer and
    # confirms nothing, and `total_count` is on the first page of the same
    # endpoint this loop already read. Only the all-green branch pays for
    # this second pass.
    for sha in $shas; do
      out=$("$ghc" api "repos/$repo/commits/$sha/check-runs" --jq '.total_count' 2>/dev/null) || {
        echo "the check runs at $sha could not be read, so the ancestry reds are UNCHECKED this run, not confirmed empty"; return 3; }
      [ "${out:-0}" -gt 0 ] 2>/dev/null && { any=1; break; }
    done
    [ -n "$any" ] || { echo "no pushed commit carries any check run, so there is no red to answer and none confirmed absent"; return 3; }
  fi
  printf '%s' "$names" | sort -u
}

# Step 7c's whole body, so `--self-test` drives the code the step runs (the
# #1591 lesson: a self-test that drove only a helper left the call site
# unpinned). rc 0 answered or no red, 1 an unanswered red, 3 a skip boundary.
reds_line() { # body file, head sha, title, paths file, remote head ref
  local names r n out reds=()
  names=$(ancestry_reds "$5"); r=$?
  [ "$r" -eq 3 ] && { printf '%s\n' "$names"; return 3; }
  if [ -z "$names" ]; then
    printf 'no red check run stands on any commit this branch pushed'
    return 0
  fi
  while IFS= read -r n; do [ -n "$n" ] && reds+=("$n"); done <<<"$names"
  out=$(mktemp)
  body_check "$1" "$2" "$3" "$4" "${reds[@]}" >"$out" 2>&1; r=$?
  if [ "$r" -eq 0 ]; then
    printf 'the body answers every red this branch pushed (%s)' "$(echo $names)"
  else
    # The refusal printed is the red gate's own sentence, not this wrapper's,
    # so the row that reads it pins WHICH check refused.
    printf 'RED UNANSWERED (%s): %s' "$(echo $names)" "$(grep -m1 'does not name it' "$out" || tail -1 "$out")"
  fi
  rm -f "$out"; return "$r"
}

# A BODY IN A SHARED ROOT IS ANOTHER SEAT'S BODY WAITING TO HAPPEN. Seats of one
# session are all told the same scratchpad, and a machine has one `/tmp`, so a
# `body.md` written directly in either is overwritten by the next seat that picks
# the obvious name -- five destroyed files and one pattern kill on 2026-09-16/17,
# in the root-cause comment on #201 for the pull request that added this.
#
# SCOPE: a directory handed to more than one seat -- a `scratchpad`, its
# `claude-<uid>` parent, the system temp roots, `$TMPDIR` and `$HOME`. A worktree
# root is out of it: a worktree is one seat's by contract. The FILE is resolved
# first, so a link in a seat's own directory pointing at a shared root refuses.
# Plain `mktemp` names a unique file directly in `$TMPDIR` and is refused too:
# deliberately, since telling a unique name from a chosen one is guessing, and
# `mktemp -d` costs two characters. `<abs-scratch>/<seat>/body.md` passes.
shared_root() { # body path -> 0 when the file sits directly in a shared root
  local f d r
  f=$(realpath -- "$1" 2>/dev/null) || f=$1
  d=$(cd "$(dirname -- "$f")" 2>/dev/null && pwd -P) || return 1
  case "$d" in /tmp|/private/tmp|/var/tmp|/private/var/tmp) return 0 ;; esac
  for r in "${TMPDIR:-}" "${HOME:-}"; do
    [ -n "$r" ] && [ "$d" = "$(cd "$r" 2>/dev/null && pwd -P)" ] && return 0
  done
  case "$(basename -- "$d")" in scratchpad|claude-[0-9]*) return 0 ;; esac
  return 1
}

push_order() { # own remote branch's sha ('' or '-' for none), behind, ahead
  case "${1:-}" in ''|-) return 3 ;; esac   # 3 no remote branch: nothing to compare
  if [ "${2:-0}" -gt 0 ]; then
    if [ "${3:-0}" -gt 0 ]; then return 5; fi # 5 both moved: a non-fast-forward
    return 1                                  # 1 it holds commits HEAD lacks
  fi
  if [ "${3:-0}" -gt 0 ]; then return 4; fi # 4 HEAD is not on it yet
  return 0                                  # 0 it is at this head
}

stamp_paths() { # name-only diff over VERSION, unified diffs of manifest.json and RELEASE_NOTES.md
  # Step 5's predicate, a pure function of its inputs so --self-test can
  # drive it. Prints the stamp-shaped paths it finds, space-separated; empty
  # means the branch touched no version.
  #
  # KEYED ON THE FIELD, NOT THE FILE. CLAUDE.md rule 4 forbids touching
  # "VERSION, the manifest VERSION, or the RELEASE_NOTES.md heading"; the
  # first form of this step diffed manifest.json by NAME and so refused every
  # manifest edit, including the one that adds `quality_scale` -- a predicate
  # wider than the rule it enforced, found by the first branch that made a
  # legitimate non-version manifest edit. The manifest's other keys are
  # ordinary production state; only its `version` line is the stamp's.
  local out=""
  if [ -n "${1// /}" ]; then out="VERSION"; fi
  if printf '%s\n' "$2" | grep -qE '^[-+][[:space:]]*"version"[[:space:]]*:'; then
    out="${out:+$out }custom_components/heatpump_optimizer/manifest.json(version)"
  fi
  # The notes: a `## ` line added or removed is a release heading, which only
  # the stamp writes. `### ` subsections do not match, because the pattern
  # needs the space straight after two hashes.
  if printf '%s\n' "${3:-}" | grep -qE '^[-+]## '; then
    out="${out:+$out }RELEASE_NOTES.md(heading)"
  fi
  printf '%s' "$out"
}

# Step 5's whole body, and the one command `pr-contract` runs for it, so CLAUDE.md
# rule 4 is refused by CI rather than only by a seat that remembered to run this
# script. Before this, the step ran locally and nowhere else: `pr-contract` ran
# `--self-test`, which drives `stamp_paths` over strings and never reads a diff,
# so a pull request bumping VERSION was refused by no check at all.
#
# THREE-DOT, FROM THE MAIN REF, NOT FROM A MERGE BASE A CALLER COMPUTED. `git diff
# A...B` takes the merge base itself, so a main that has stamped since the branch
# forked contributes nothing -- the stamp is main's commit, not the branch's. The
# argument is the main ref precisely so that `...` is load-bearing: handed a
# precomputed merge base, two dots and three would print the same diff, and a
# regression to two dots would pass every fixture. The moved-main fixture in
# --self-test is the arm that refuses two dots.
#
# FAIL CLOSED: a range that does not resolve returns 2, never an empty list,
# because an empty list is this function's all-clear.
#
# THE DIFF IS FORCED TEXTUAL, because two of the three matchers read diff BODY
# and the branch under test owns the attributes that decide whether a body is
# printed at all. `.gitattributes` is a tracked file, so a pull request adds
# `custom_components/heatpump_optimizer/manifest.json -diff` in the same commit
# that bumps the version, and `git diff` prints `Binary files a/... and b/...
# differ` with no `+  "version":` line anywhere -- `stamp_paths` then finds
# nothing and this function returns its all-clear. `--text` overrides the
# attribute and restores the hunks; `--no-textconv` covers the other half of the
# same surface, a `diff=<driver>` attribute whose driver has a textconv, so the
# matchers read the blob rather than a rendering of it. Neither flag changes
# what an ordinary diff prints, which is the null control in --self-test.
# `--name-only` is not attribute-sensitive -- VERSION cannot be hidden this way,
# and `tests/entities.py` pins the manifest version to VERSION besides -- but
# the flags are passed on all three so no later edit has to re-derive which
# call reads a body.
version_edit() { # main ref, head -> prints the stamp-owned items the range moved
  local names manifest notes out
  git rev-parse --verify --quiet "$1^{commit}" >/dev/null || return 2
  git rev-parse --verify --quiet "$2^{commit}" >/dev/null || return 2
  names=$(git diff --text --no-textconv --name-only "$1...$2" -- VERSION 2>/dev/null) || return 2
  manifest=$(git diff --text --no-textconv "$1...$2" -- custom_components/heatpump_optimizer/manifest.json 2>/dev/null) || return 2
  notes=$(git diff --text --no-textconv "$1...$2" -- RELEASE_NOTES.md 2>/dev/null) || return 2
  out=$(stamp_paths "$names" "$manifest" "$notes")
  printf '%s' "$out"
  [ -z "$out" ]
}

# --- transport files in the code head's ancestry -------------------------------
# WHY THIS EXISTS. A pull-request body used to travel as a commit above the code
# head, under `tools/audit/handoff/`, with resume notes under `handoff/`, and any
# commit a seat then added on top dragged the transport into the code head. The
# round-9 process review counted at least seven such incidents, every one found
# by a reviewer or by a re-cut (#1783 re-cut as #1785, #1801, #1815). Transport
# now travels on an orphan ref (`fixer.md` step 6), so no commit a branch adds
# writes under either root, and a reviewer never has to look.
#
# `--full-history` because default history simplification follows only the
# first parent of a merge whose tree matches it, which hides a side branch that
# added a body and deleted it again: the exact shape a re-cut leaves.
# `-c` because a merge's combined diff lists only a file that matches none of
# its parents: a body written while resolving a merge of main is read, and
# main's own files, which match main's parent, stay out (`--no-merges` read
# neither, so a conflict resolution was a bypass). Deletions pass, so a branch removing a stray file main still
# carries is not refused. Fail-closed: a range git cannot read returns 2.
TRANSPORT_ROOTS=(tools/audit/handoff/ handoff/)
transport_in_ancestry() { # merge base, head -> 0 clean, 1 found (prints `<sha> <path>`), 2 unreadable
  local out
  out=$(git log --full-history -c --diff-filter=ACMRT --name-only \
        --format='@%h' "$1..$2" -- "${TRANSPORT_ROOTS[@]}" 2>/dev/null) || return 2
  out=$(printf '%s\n' "$out" | awk '/^@/{c=substr($0,2);next} NF{print c" "$0}')
  [ -z "$out" ] && return 0
  printf '%s\n' "$out"
  return 1
}

# --- whether a diff owes the self-test -----------------------------------------
# WHY THIS EXISTS. #1811 went red in CI's `governance` job on a self-test row its
# own diff had made stale, a run of seconds here; its fixer named this as the
# cheaper detector. The rows drive this script, the programs it shells out to
# and their fixtures, so a change to any of them can move a row. The program
# list is derived from this file, never carried: every tracked script path it
# names. A path named only in a comment over-selects, which costs one self-test
# run; a carried list under-selects the day a step is added. The two modules
# named after it are imported by `policy_lint.mjs`, not named here, and its
# `--pr-body` rows move when they do.
SELFTEST_FIXTURES=tools/policy/fixtures/
[ -d .claude/workflows/fixtures ] && SELFTEST_FIXTURES=.claude/workflows/fixtures/
selftest_inputs() { # -> one path per line; a trailing / is a directory prefix
  { printf '%s\n' "$PREPR_PATH"
    grep -oE '(\.claude/workflows|tools|tests)/[A-Za-z0-9_./-]+\.(mjs|js|py|sh)' "$PREPR_PATH"
  } | sort -u | while read -r p; do
    git ls-files --error-unmatch -- "$p" >/dev/null 2>&1 && printf '%s\n' "$p"
  done
  if [ -f tools/policy/counts.mjs ]; then
    printf '%s\n' tools/policy/counts.mjs tools/policy/render_md.mjs
  else
    printf '%s\n' .claude/workflows/counts.mjs .claude/workflows/render_md.mjs
  fi
  printf '%s\n' "$SELFTEST_FIXTURES"
}
selftest_owed() { # changed-paths file -> 0 when a changed path is a self-test input
  awk 'NR==FNR { if ($0 ~ /\/$/) d[$0]=1; else f[$0]=1; next }
       ($0 in f) { hit=1; exit }
       { for (p in d) if (index($0, p) == 1) { hit=1; exit } }
       END { exit !hit }' <(selftest_inputs) "$1"
}

# `pr-contract`'s entry point: `prepr.sh --version-edit <main ref> <head>`. It
# exits before anything below, which needs a body, node and the closures.
if [ "${1:-}" = "--version-edit" ]; then
  found=$(version_edit "${2:-}" "${3:-}"); ve=$?
  case $ve in
    0) printf 'no version edit: %s...%s moves none of VERSION, the manifest version or a notes heading\n' "${2:-}" "${3:-}" ;;
    1) printf 'REFUSE no version edit: %s...%s moves %s\n' "${2:-}" "${3:-}" "$found"
       printf 'CLAUDE.md rule 4: versions are assigned after the merge by tools/release/stamp.py; restore these to the merge base.\n' ;;
    *) printf 'REFUSE no version edit: %s...%s did not resolve, so nothing was compared -- fetch the main ref and full history\n' "${2:-}" "${3:-}" ;;
  esac
  exit "$ve"
fi

# --- self-test ---------------------------------------------------------------
# A check that cannot be shown failing does not merge. This drives the two steps
# that are pure functions of their input -- the body checks -- against the rot
# fixtures, and asserts the healthy one stays silent. The branch-shape steps
# (merge base, gate mode, version edit, claim files) are demonstrated by the
# `pr-contract` job running this script on every pull request.
if [ "${1:-}" = "--self-test" ]; then
  D=tools/policy/fixtures/policy-rot/prepr
  ZERO=0000000000000000000000000000000000000000
  # A base that DOES resolve, for the success arm below. HEAD always resolves
  # and needs no remote, so this arm runs in a clone with no `origin` too.
  BASE_ST=HEAD
  st_pass=0; st_fail=0
  # `$1` is a return code for most assertions and a ref NAME for the push-order
  # fixtures' first one, so the failure line says `got`, not `rc`.
  st() { if [ "$1" = "$2" ]; then st_pass=$((st_pass+1)); printf '  ok   %s\n' "$3";
         else st_fail=$((st_fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$3" "$1" "$2"; fi; }

  for f in missing-section no-figures empty-section wrong-head dead-carry bad-friction backtick-bad-event bare-na folded-entry bullet-after-entry; do
    if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs --pr-body "$D/$f.md" --head "$ZERO" >/dev/null 2>&1; else node tools/policy/policy_lint.mjs --pr-body "$D/$f.md" --head "$ZERO" >/dev/null 2>&1; fi
    st $? 1 "a body with $f is refused"
  done
  if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs --pr-body "$D/unnamed-red.md" --head "$ZERO" --red 'fast (3.14)' >/dev/null 2>&1; else node tools/policy/policy_lint.mjs --pr-body "$D/unnamed-red.md" --head "$ZERO" --red 'fast (3.14)' >/dev/null 2>&1; fi
  st $? 1 "a body that does not name its red check is refused"
  # TWO null controls, not one. `good-none.md` answers every section with the
  # accepted WORD; `good.md` answers `## Friction` with a well-formed line. A
  # single fixture covering only `none` left the friction parser's accept path
  # unexercised, and the first real body written against this check was refused
  # for writing its rule id the way every other file in this corpus writes an
  # identifier. A rot fixture proves a check fires; only a healthy one that
  # exercises the same code path proves it fires for the right reason.
  if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs --pr-body "$D/good.md" --head "$ZERO" >/dev/null 2>&1; else node tools/policy/policy_lint.mjs --pr-body "$D/good.md" --head "$ZERO" >/dev/null 2>&1; fi
  st $? 0 "a healthy body with a well-formed friction line is silent (null control)"
  if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs --pr-body "$D/good-none.md" --head "$ZERO" >/dev/null 2>&1; else node tools/policy/policy_lint.mjs --pr-body "$D/good-none.md" --head "$ZERO" >/dev/null 2>&1; fi
  st $? 0 "a healthy body answering every section with a word is silent (null control)"

  # The hooks check, driven over one fixture per way a wiring can be wrong.
  # `empty` and `broken` matter most: a settings file with no hooks, and one
  # that does not parse, both read exactly like a working one to anybody who
  # only looks at whether the file is there.
  for f in missing empty unreadable broken self-test-fails bad-matcher bad-type; do
    if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs --hooks "$D/../hooks/$f.json" >/dev/null 2>&1; else node tools/policy/policy_lint.mjs --hooks "$D/../hooks/$f.json" >/dev/null 2>&1; fi
    st $? 1 "a settings file whose hook is $f is refused"
  done
  if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs --hooks >/dev/null 2>&1; else node tools/policy/policy_lint.mjs --hooks >/dev/null 2>&1; fi
  st $? 0 "this repository's own three wired hooks pass (null control)"

  # A missing matcher, `""` and `"*"` are Claude Code's own "match every tool"
  # spellings, not a pattern to compile -- `"*"` alone threw out of `RegExp`
  # and read as MATCHER BLIND on a group that in fact fires on every edit
  # (Cloud reviewer 2, PR #1692). Each fixture below is otherwise a complete,
  # correctly-wired settings file, so a regression here shows up as this
  # loop's REFUSE, not as the bad-matcher.json loop's silence.
  for f in star-matcher no-matcher empty-matcher; do
    if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs --hooks "$D/../hooks/$f.json" >/dev/null 2>&1; else node tools/policy/policy_lint.mjs --hooks "$D/../hooks/$f.json" >/dev/null 2>&1; fi
    st $? 0 "a settings file whose PreToolUse matcher is $f passes (null control)"
  done

  # The push-order verdict, one fixture per branch shape. Named in a list rather
  # than globbed, for the same reason the two loops above are: a glob that
  # matches nothing runs no assertions and prints the same "0 failed" a passing
  # set does. A missing file is a FAIL, not a skip.
  #
  # TWO assertions per fixture, because the #694 review found the defect in the
  # half that had none: the verdict function was right and the CALL SITE fed it
  # the wrong ref. So each fixture states which ref the shape must be compared
  # against as well as what the comparison must return, and `@{u}` is not among
  # the fields -- removing it from the input set is the repair.
  for f in detached no-upstream remote-at-head unpushed-head remote-ahead diverged main-tracking; do
    c="$D/upstream/$f.case"
    if [ ! -f "$c" ]; then st 1 0 "the $f push-order fixture is present"; continue; fi
    IFS=' ' read -r br rem up behind ahead want wantref why < <(grep -vE '^#|^[[:space:]]*$' "$c" | head -1)
    got=$(pr_head_ref "$br" "$rem") || got='-'
    st "$got" "${wantref:-?}" "${why:-$f} -- compared against ${wantref:-?}"
    push_order "$up" "$behind" "$ahead"
    st $? "${want:-?}" "${why:-$f}"
  done

  # Step 7a, driven through `figures_check` -- the function the step calls, so
  # a call site that stops calling it fails here. The rot fixture is the #715
  # defect itself, `--arg` passed to `gh api`; the null control is the same
  # fixture set's healthy body, whose figure names an in-tree instrument.
  # The exit status alone does not pin WHICH instrument the step runs: another
  # body check refuses the same rot fixture and passes the same healthy one, so
  # a `figures_check` rewired to it would satisfy a status-only assertion. Each
  # arm therefore also reads a string only this instrument prints.
  figures_check tools/policy/fixtures/figures/gh-arg.md >/tmp/prepr-figst.$$ 2>&1
  st $? 1 "a body whose figure command cannot resolve is refused"
  grep -q -- 'has no `--arg` flag' /tmp/prepr-figst.$$
  st $? 0 "and the step's own output names the flag, so the step runs the figure check"
  figures_check "$D/good.md" >/tmp/prepr-figst.$$ 2>&1
  st $? 0 "a body whose figure command resolves is silent (null control)"
  grep -q '0 refused' /tmp/prepr-figst.$$
  st $? 0 "and it reached a verdict rather than examining nothing (null control)"
  rm -f /tmp/prepr-figst.$$

  # Step 7's body check, driven through `body_check` -- the function the step
  # calls -- over ONE body and three path lists. One arm alone would pin a check
  # that always fires or never does, and "never does" is the state this script
  # shipped in: with no `--paths-file`, `policyPaths` was empty, `## Approval`
  # could not be required, and every branch read `ok pr-body`.
  #
  # `needs-approval.md` is the fixture for both directions because it differs
  # from the healthy body in exactly one thing -- no `## Approval` -- so the
  # only variable across these arms is the diff.
  #
  # THE NON-POLICY ARM IS THE CONTROL THAT MATTERS MORE. Over-firing here would
  # refuse every ordinary pull request in this repository, and a refusal that
  # fires on everything pins nothing. The exit status alone does not pin WHICH
  # refusal fired -- this body is refusable on other grounds by other flags -- so
  # the policy arm also reads the approval gate's own sentence.
  body_check "$D/needs-approval.md" "$ZERO" '' "$D/paths-real.txt" >/tmp/prepr-bodyst.$$ 2>&1
  st $? 1 "a body with no \`## Approval\` is refused when the diff touches a policy path"
  grep -q 'no `## Approval` section' /tmp/prepr-bodyst.$$
  st $? 0 "and the refusal is the approval gate's own, so the paths reached the check"
  body_check "$D/needs-approval.md" "$ZERO" '' "$D/paths-nonpolicy.txt" >/dev/null 2>&1
  st $? 0 "the same body is silent when the diff touches no policy path (null control)"
  body_check "$D/needs-approval.md" "$ZERO" '' "$D/paths-empty.txt" >/dev/null 2>&1
  st $? 1 "a path list that derived nothing is refused, not read as \"touches no policy file\""
  rm -f /tmp/prepr-bodyst.$$

  # Step 7c, driven through `reds_line` -- the function the step calls -- over
  # a throwaway repository whose two pushed commits carry OFFLINE check-run
  # fixtures under tools/policy/fixtures/red-ancestry/, one per way the
  # ancestry can look. The commits are built with fixed dates so their SHAs are
  # deterministic and the fixtures are keyed by them: a later edit to this
  # construction changes the SHAs, the stub finds no fixture, and these rows
  # FAIL rather than pass vacuously. The stub replaces the `gh` binary word
  # (`PREPR_GH`) with identical argv, so the URL and the jq key are built by
  # the production code the step runs, and real `jq` applies that key over the
  # fixture JSON -- no network, in CI's self-test job exactly as here.
  #
  # The throwaway repository is reached through GIT_DIR rather than `cd`: the
  # body check must still run from THIS tree, because policy_lint.mjs's entry
  # guard compares `process.argv[1]` with the realpath of its own module and a
  # copy or symlink reached from another directory silently runs nothing.
  DABS=$(cd "$D" && pwd -P)
  RAFIX=$(cd tools/policy/fixtures/red-ancestry && pwd -P)
  RA=$(mktemp -d)
  (
    set -e; cd "$RA"; git init -q -b main .
    git config user.name st; git config user.email st@st
    git remote add origin https://github.com/tvofi/heatpump_optimizer.git
    # The identity is pinned through the environment, not only `git config`:
    # GIT_AUTHOR_NAME in a seat's ambient environment outranks user.name and
    # changes both commit SHAs, so every fixture below went unfound (7 rows).
    export GIT_AUTHOR_NAME=st GIT_AUTHOR_EMAIL=st@st GIT_COMMITTER_NAME=st GIT_COMMITTER_EMAIL=st@st
    export GIT_AUTHOR_DATE='2005-04-07T22:13:13 +0000'
    export GIT_COMMITTER_DATE='2005-04-07T22:13:13 +0000'
    echo a > code; git add -A; git -c commit.gpgsign=false commit -qm base
    git -c commit.gpgsign=false checkout -q -b fix
    echo b > code; git -c commit.gpgsign=false commit -qam one
    echo c > code; git -c commit.gpgsign=false commit -qam two
    git update-ref refs/remotes/origin/fix fix
    git update-ref refs/remotes/origin/main main
  ) >/dev/null 2>&1
  cat >"$RA/gh" <<'EOS'
#!/bin/bash
# serves $REDFIX/<sha>.json through the jq filter prepr passed, like gh api
set -u
filter=""; url=""; prev=""
for a in "$@"; do
  [ "$prev" = "--jq" ] && filter=$a
  case "$a" in repos/*/commits/*/check-runs) url=$a ;; esac
  prev=$a
done
[ -n "$filter" ] && [ -n "$url" ] || exit 5
sha=${url#*/commits/}; sha=${sha%/check-runs}
[ -f "$REDFIX/$sha.json" ] || exit 1
exec jq -r "$filter" "$REDFIX/$sha.json"
EOS
  chmod +x "$RA/gh"
  printf '#!/bin/bash\nexit 1\n' >"$RA/ghdead"; chmod +x "$RA/ghdead"
  ra() { # case dir, body file, remote ref -> "<rc>:$line"
    local out r
    out=$(GIT_DIR="$RA/.git" REDFIX="$RAFIX/$1" GITHUB_TOKEN=selftest PREPR_GH="$RA/gh" \
      reds_line "$DABS/$2" "$ZERO" '' "$DABS/paths-nonpolicy.txt" "${3:-origin/fix}")
    r=$?
    echo "$r:$out"
  }
  got=$(ra red unnamed-red.md)
  st "${got%%:*}" 1 "a red an earlier pushed commit carried and the body does not name is refused"
  case "$got" in *'fast (3.14)'*'does not name it'*) st 1 1 "and the refusal is the red gate's own, naming the check";; *) st 0 1 "and the refusal is the red gate's own, naming the check";; esac
  got=$(ra red red-answered.md)
  st "${got%%:*}" 0 "the same ancestry with a body that names the red passes (null control)"
  case "$got" in *'answers every red'*) st 1 1 "and the ok line names what was answered";; *) st 0 1 "and the ok line names what was answered";; esac
  got=$(ra green red-answered.md)
  st "${got%%:*}" 0 "an ancestry whose only failure is pr-contract's own run passes (the exclusion key)"
  case "$got" in *'no red check run stands'*) st 1 1 "and the ok line says no red stands, so green was measured, not assumed";; *) st 0 1 "and the ok line says no red stands, so green was measured, not assumed";; esac
  got=$(ra bare red-answered.md)
  st "${got%%:*}" 3 "an ancestry no commit of which carries any check run skips, never refuses"
  case "$got" in *'no pushed commit carries any check run'*) st 1 1 "and the skip line names the boundary";; *) st 0 1 "and the skip line names the boundary";; esac
  got=$(ra red red-answered.md origin/main)
  st "${got%%:*}" 3 "a branch nothing of which is pushed past the merge base skips"
  got=$(ra red red-answered.md origin/never-pushed)
  st "${got%%:*}" 3 "a remote head ref that does not resolve skips"
  out=$(GIT_DIR="$RA/.git" REDFIX="$RAFIX/red" GITHUB_TOKEN= GH_TOKEN= PREPR_GH="$RA/ghdead" \
    reds_line "$DABS/red-answered.md" "$ZERO" '' "$DABS/paths-nonpolicy.txt" origin/fix)
  st $? 3 "no credential gh can use skips the arm (never refuses)"
  case "$out" in *no\ token*) st 1 1 "and the skip line says why";; *) st 0 1 "and the skip line says why";; esac
  out=$(GIT_DIR="$RA/.git" REDFIX="$RAFIX/red" GITHUB_TOKEN=selftest PREPR_GH="$RA/no-such-gh" \
    reds_line "$DABS/red-answered.md" "$ZERO" '' "$DABS/paths-nonpolicy.txt" origin/fix)
  st $? 3 "an absent gh skips the arm (never refuses)"
  case "$out" in *gh\ is\ absent*) st 1 1 "and the skip line says why";; *) st 0 1 "and the skip line says why";; esac
  rm -rf "${RA:?}"

  # Step 7's budget arm, driven through `body_line` -- the function the step
  # calls -- over a throwaway repository reached through GIT_DIR, for the reason
  # 7c's rows give. Its base commit carries THIS tree's budget_raise_gate.py, so
  # the rows grade the gate the pull request will restore; `nogate` is a base
  # with none. Each arm also reads a string only its own path prints, because a
  # body check that refused on other grounds would satisfy a status alone.
  BR=$(mktemp -d)
  (
    set -e; cd "$BR"; git init -q -b main .
    git config user.name st; git config user.email st@st
    echo a > README; git add -A; git -c commit.gpgsign=false commit -qm nogate; git tag nogate
    mkdir -p .claude/workflows tests
    cp "$OLDPWD/tools/policy/budget_raise_gate.py" .claude/workflows/
    printf '{\n "recorded_at": "x",\n "foo_loc": 10\n}\n' > tests/structure_budgets.json
    git add -A; git -c commit.gpgsign=false commit -qm base; git tag base
    git checkout -q -b raise base
    printf '{\n "recorded_at": "x",\n "foo_loc": 11\n}\n' > tests/structure_budgets.json
    git -c commit.gpgsign=false commit -qam raise
    git checkout -q -b lower base
    printf '{\n "recorded_at": "y",\n "foo_loc": 9\n}\n' > tests/structure_budgets.json
    git -c commit.gpgsign=false commit -qam lower
    git checkout -q -b docs base
    echo b > README; git -c commit.gpgsign=false commit -qam docs
  ) >/dev/null 2>&1
  bl() { # base, head, body -> "<rc>:$line"
    local out r
    out=$(GIT_DIR="$BR/.git" body_line "$DABS/$3" "$ZERO" '' "$DABS/paths-nonpolicy.txt" "$1" "$2")
    r=$?
    echo "$r:$out"
  }
  got=$(bl base raise unnamed-red.md)
  st "${got%%:*}" 1 "a diff raising a budget leaf with a body silent on budget-raise-gate is refused before the push"
  case "$got" in *'budget-raise-gate'*'does not name it'*) st 1 1 "and the refusal is the red gate's own, naming budget-raise-gate";; *) st 0 1 "and the refusal is the red gate's own, naming budget-raise-gate";; esac
  got=$(bl base raise budget-answered.md)
  st "${got%%:*}" 0 "the same raise with a body naming budget-raise-gate passes (null control)"
  case "$got" in *'1 budget raise'*'foo_loc'*) st 1 1 "and the ok line names the raise it fed";; *) st 0 1 "and the ok line names the raise it fed";; esac
  got=$(bl base lower unnamed-red.md)
  st "${got%%:*}" 0 "a budget re-recorded down owes no answer"
  case "$got" in *'no budget leaf raised'*) st 1 1 "and the ok line says no raise was found, so the gate ran";; *) st 0 1 "and the ok line says no raise was found, so the gate ran";; esac
  got=$(bl base docs unnamed-red.md)
  st "${got%%:*}" 0 "a diff touching no budget file passes"
  got=$(bl nogate raise unnamed-red.md)
  case "$got" in *'carries no budget_raise_gate.py'*) st 1 1 "a merge base with no gate skips the arm and says so";; *) st 0 1 "a merge base with no gate skips the arm and says so";; esac
  st "${got%%:*}" 0 "and the body check still runs, fed nothing (skip, never refuse)"
  rm -rf "${BR:?}"

  # Step 6c, driven through `copies_line` -- the function the step calls --
  # over a fixture tree holding THIS tree's tests/closure.py, one production
  # module and one test file, so the copy claim is the only variable.
  CR=$(mktemp -d)
  mkdir -p "$CR/tests" "$CR/custom_components/heatpump_optimizer"
  cp tests/closure.py "$CR/tests/"
  printf 'def heat_loss(x):\n    return x\n' > "$CR/custom_components/heatpump_optimizer/model.py"
  printf 'tests/thermal.py\n' > "$CR/changed-py.txt"
  printf 'README.md\ntests/golden/a.json\n' > "$CR/changed-none.txt"
  printf 'def heat_loss(x):\n    return 2 * x\n' > "$CR/tests/thermal.py"
  got=$(copies_line "$CR" "$CR/changed-py.txt"); r=$?
  st "$r" 1 "a test file defining a production top-level name is refused"
  case "$got" in *"COPY-CLAIMED: tests/thermal.py defines 'heat_loss'"*) st 1 1 "and the refusal is no-copies' own line";; *) st 0 1 "and the refusal is no-copies' own line";; esac
  printf 'def local_loss(x):\n    return 2 * x\n' > "$CR/tests/thermal.py"
  got=$(copies_line "$CR" "$CR/changed-py.txt"); r=$?
  st "$r" 0 "the same test with the name renamed passes (null control)"
  case "$got" in *'no test file defines a symbol production also defines'*) st 1 1 "and the ok line is no-copies' own, so it ran";; *) st 0 1 "and the ok line is no-copies' own, so it ran";; esac
  printf 'def heat_loss(x):\n    return 2 * x\n' > "$CR/tests/thermal.py"
  got=$(copies_line "$CR" "$CR/changed-none.txt"); r=$?
  st "$r" 3 "a diff touching no .py under tests/ or custom_components/ skips, even over a copy"
  case "$got" in *'changes no .py under tests/ or custom_components/'*) st 1 1 "and the skip line names the boundary";; *) st 0 1 "and the skip line names the boundary";; esac
  rm -f "$CR/tests/closure.py"
  got=$(copies_line "$CR" "$CR/changed-py.txt"); r=$?
  st "$r" 3 "a tree with no tests/closure.py skips, never refuses"
  rm -rf "${CR:?}"

  # The call site. Driving the two functions above does not pin that a step
  # calls them: the #1591 self-test drove a helper while the step kept calling
  # the old one. The main flow is the text after this self-test returns.
  flow=$(awk 'f{print} /^rc=0$/{f=1}' "$PREPR_PATH")
  printf '%s\n' "$flow" | grep -q 'body_line "'
  st $? 0 "the pr-body step calls body_line, so a predicted raise reaches the body check before the push"
  printf '%s\n' "$flow" | grep -q 'copies_line "'
  st $? 0 "the no-copies step calls copies_line, so a python diff runs closure.py no-copies before the push"

  # The degraded arm, asserted on BOTH keys because the first version of it
  # asserted a property the code did not have. A range that does not resolve must
  # make the DERIVATION fail, so the step refuses rather than handing the check a
  # list nothing wrote -- and it must leave no list behind either, so a caller
  # added later that reads the file rather than the status fails closed as well.
  # `git diff` exits 128 on an unknown revision, not 1, so the first assertion is
  # on the branch taken rather than on the number.
  rm -f /tmp/prepr-bodyst.$$ /tmp/prepr-bodyst.$$.part
  if diff_paths "$ZERO" /tmp/prepr-bodyst.$$ >/dev/null 2>&1; then dp=0; else dp=1; fi
  st "$dp" 1 "a base that does not resolve makes the path derivation fail"
  if [ -e /tmp/prepr-bodyst.$$ ] || [ -e /tmp/prepr-bodyst.$$.part ]; then fp=1; else fp=0; fi
  st "$fp" 0 "and leaves no list behind, not even an empty one, so the file key fails closed too"
  rm -f /tmp/prepr-bodyst.$$ /tmp/prepr-bodyst.$$.part
  # The SUCCESS path's own temp-file assertion, which nothing pinned before: a
  # derivation that works must also leave no `.part` behind.
  #
  # WHAT IT DOES NOT PIN, measured rather than assumed. A first version of this
  # comment claimed the arm would catch a later edit replacing `mv` with `cp`.
  # It does not: driven, `cp -f` leaves `--self-test` at 48/0, because the
  # unconditional cleanup above removes the copy's leftover too. That is the
  # fix working rather than a hole -- under either verb no `.part` survives --
  # but the arm's reach is the PROPERTY, not the verb, and saying otherwise
  # would be a claim stronger than the check that backs it.
  diff_paths "$BASE_ST" /tmp/prepr-bodyst.$$ >/dev/null 2>&1; dp=$?
  if [ -e /tmp/prepr-bodyst.$$.part ]; then fp=1; else fp=0; fi
  st "$dp" 0 "a base that resolves makes the path derivation succeed (null control)"
  st "$fp" 0 "and leaves no \`.part\` behind either, so the temp file is the function's own"
  rm -f /tmp/prepr-bodyst.$$ /tmp/prepr-bodyst.$$.part

  # THE `mv`-FAILURE ARM, and it exists because the #1054 review measured the
  # leak rather than reasoning about it: the first form cleaned up only on the
  # redirect's failure, so a failing `mv` left 138 bytes of `.part` behind and
  # the caller's `rm -f "$PATHS"` did not name it.
  #
  # The shape is buildable, which is the only reason this is an arm rather than
  # a disclosure. `$2` is an existing DIRECTORY holding a non-empty directory
  # called `<basename>.part`, so the redirect succeeds -- `$2.part` is an
  # ordinary file beside it -- and `mv` then refuses, because moving that file
  # into `$2` would have to replace a directory that is not empty. Source and
  # destination share a parent by construction, so every permission-based way of
  # failing `mv` fails the redirect first and never reaches this path; this is
  # the one route that separates them.
  MVD=$(mktemp -d)
  mkdir -p "$MVD/d/d.part/occupied"
  diff_paths "$BASE_ST" "$MVD/d" >/dev/null 2>&1; dp=$?
  if [ -e "$MVD/d.part" ]; then fp=1; else fp=0; fi
  st "$dp" 1 "a derivation whose rename fails is refused"
  st "$fp" 0 "and cleans up after itself, so a failing \`mv\` leaks no \`.part\`"
  rm -rf "$MVD"

  # Step 5, driven through `stamp_paths` -- the function the step calls. The
  # over-fire control is the arm that matters: the step shipped keyed on the
  # manifest's file name and refused every manifest edit, so the arm that pins
  # "a non-version manifest edit passes" is the one the old predicate fails.
  # The other three are the stamp's own shapes, each of which must still refuse.
  got=$(stamp_paths '' '+  "quality_scale": "platinum",')
  st "$got" '' "a manifest edit that is not the version field passes (over-fire control)"
  got=$(stamp_paths '' '-  "version": "6.5.1",
+  "version": "6.5.2",')
  st "$got" 'custom_components/heatpump_optimizer/manifest.json(version)' "a manifest version bump is refused, and named by field"
  got=$(stamp_paths 'VERSION' '')
  st "$got" 'VERSION' "a VERSION edit is refused"
  got=$(stamp_paths 'VERSION' '-  "version": "6.5.0",
+  "version": "6.5.1",
+  "quality_scale": "platinum",')
  st "$got" 'VERSION custom_components/heatpump_optimizer/manifest.json(version)' "a stamp-shaped diff is refused on both, and the added key does not mask it"
  got=$(stamp_paths '' '' '+## v6.5.2')
  st "$got" 'RELEASE_NOTES.md(heading)' "a release-notes heading is refused, and named"
  got=$(stamp_paths '' '' '+### Fixed
+- a line under an existing release')
  st "$got" '' "a notes subsection or bullet passes (over-fire control)"

  # `version_edit` over real commits, because what it adds to `stamp_paths` is
  # the RANGE, and a range is only exercised by a history. One throwaway
  # repository: `base` forks `main` and every PR shape; `main` then stamps.
  # Each refusing arm is one file matcher, so dropping any matcher fails its
  # own line; the moved-main arm is the one two dots fail, because a two-dot
  # diff reports the stamp main made after the fork as the branch's; and the
  # merged arm is the ordinary state of a branch updated with `git merge`.
  VER=$(mktemp -d)
  (
    set -e; cd "$VER"; git init -q -b main .
    git config user.name st; git config user.email st@st
    mkdir -p custom_components/heatpump_optimizer docs
    printf '6.5.1\n' > VERSION
    printf '{\n  "domain": "x",\n  "version": "6.5.1"\n}\n' > custom_components/heatpump_optimizer/manifest.json
    printf '# Notes\n\n## v6.5.1\n\n- a\n' > RELEASE_NOTES.md
    printf 'doc\n' > docs/a.md
    git add -A; git commit -qm base; git tag base
    pr() { git checkout -q -b "$1" base; shift; "$@"; git add -A; git commit -qm pr; }
    pr ver sh -c 'printf "6.5.2\n" > VERSION'
    pr man sh -c 'sed -i.bak "s/6.5.1/6.5.2/" custom_components/heatpump_optimizer/manifest.json && rm custom_components/heatpump_optimizer/manifest.json.bak'
    pr notes sh -c 'printf "# Notes\n\n## v6.5.2\n\n- b\n\n## v6.5.1\n\n- a\n" > RELEASE_NOTES.md'
    pr docs sh -c 'printf "more\n" >> docs/a.md'
    # THE BLINDED PAIR. `.gitattributes` is tracked, so the branch that bumps a
    # version owns whether its own diff has a body: `-diff` makes git print
    # `Binary files ... differ` instead of the hunks the two body matchers read.
    # Each is a separate branch so a regression on one file cannot be masked by
    # the other still refusing. `attr-only` is their null control -- the same
    # `.gitattributes` line with no version edit under it still passes, so an
    # implementation that simply refused any branch touching `.gitattributes`
    # fails here rather than reading as a fix.
    pr manattr sh -c 'sed -i.bak "s/6.5.1/6.5.2/" custom_components/heatpump_optimizer/manifest.json && rm custom_components/heatpump_optimizer/manifest.json.bak && printf "custom_components/heatpump_optimizer/manifest.json -diff\n" > .gitattributes'
    pr notesattr sh -c 'printf "# Notes\n\n## v6.5.2\n\n- b\n\n## v6.5.1\n\n- a\n" > RELEASE_NOTES.md && printf "RELEASE_NOTES.md -diff\n" > .gitattributes'
    pr attronly sh -c 'printf "custom_components/heatpump_optimizer/manifest.json -diff\nRELEASE_NOTES.md -diff\n" > .gitattributes'
    # AND THE OTHER HALF OF THE SAME SURFACE, which `--text` alone does not
    # cover. `diff=<driver>` with a `textconv` makes git diff a RENDERING of the
    # blob rather than the blob, and `--text` does not override it -- only
    # `--no-textconv` does. A driver whose textconv prints nothing therefore
    # produces a diff with no body at all, on a file git never called binary, so
    # the two body matchers read an empty string and the function returns its
    # all-clear. Without these arms `--no-textconv` is unpinned: dropping that
    # one flag passed every other check in this file while reopening the vector.
    # The driver is repo-local config, which is the shape a contributor controls
    # (`.git/config` is not tracked, but a `diff=` attribute IS, and a seat or a
    # runner that has ever set up a driver by that name supplies the other half).
    git config diff.blind.textconv true
    pr mantc sh -c 'sed -i.bak "s/6.5.1/6.5.2/" custom_components/heatpump_optimizer/manifest.json && rm custom_components/heatpump_optimizer/manifest.json.bak && printf "custom_components/heatpump_optimizer/manifest.json diff=blind\n" > .gitattributes'
    pr notestc sh -c 'printf "# Notes\n\n## v6.5.2\n\n- b\n\n## v6.5.1\n\n- a\n" > RELEASE_NOTES.md && printf "RELEASE_NOTES.md diff=blind\n" > .gitattributes'
    pr tconly sh -c 'printf "custom_components/heatpump_optimizer/manifest.json diff=blind\nRELEASE_NOTES.md diff=blind\n" > .gitattributes'
    git checkout -q main
    printf '6.5.2\n' > VERSION
    sed -i.bak 's/6.5.1/6.5.2/' custom_components/heatpump_optimizer/manifest.json && rm custom_components/heatpump_optimizer/manifest.json.bak
    printf '# Notes\n\n## v6.5.2\n\n- b\n\n## v6.5.1\n\n- a\n' > RELEASE_NOTES.md
    git commit -qam 'v6.5.2 stamp'
    git checkout -q -b merged docs; git merge -q --no-edit main
  ) >/dev/null 2>&1
  ve() { (cd "$VER" && version_edit "$@"); }
  # THE ATTRIBUTE ARMS NEED THE BRANCH CHECKED OUT, and that is not a fixture
  # convenience -- it is the shape CI runs in. `git diff` resolves attributes
  # from the WORKING TREE, not from the commits in the range, so a branch's own
  # `.gitattributes` only takes effect once that branch is what is checked out.
  # `pr-contract` checks the pull request out and then runs `--version-edit`, so
  # the branch's line is live there. Diffing the same two commits from a
  # different checkout -- which is what the arms above do -- reads the hunks
  # whatever the branch declared, and would have passed with no fix at all.
  veco() { (cd "$VER" && git checkout -q "$2" && version_edit "$@"); }
  got=$(ve base ver); st "$?:$got" '1:VERSION' "a pull request editing VERSION is refused"
  got=$(ve base man); st "$?:$got" '1:custom_components/heatpump_optimizer/manifest.json(version)' "a pull request editing the manifest version is refused"
  got=$(ve base notes); st "$?:$got" '1:RELEASE_NOTES.md(heading)' "a pull request adding a notes heading is refused"
  got=$(veco base manattr); st "$?:$got" '1:custom_components/heatpump_optimizer/manifest.json(version)' "a manifest version edit hidden by a .gitattributes -diff line is still refused"
  got=$(veco base notesattr); st "$?:$got" '1:RELEASE_NOTES.md(heading)' "a notes heading hidden by a .gitattributes -diff line is still refused"
  got=$(veco base attronly); st "$?:$got" '0:' "a .gitattributes-only pull request passes (over-fire control for the two arms above)"
  got=$(veco base mantc); st "$?:$got" '1:custom_components/heatpump_optimizer/manifest.json(version)' "a manifest version edit hidden by a diff=<driver> textconv is still refused"
  got=$(veco base notestc); st "$?:$got" '1:RELEASE_NOTES.md(heading)' "a notes heading hidden by a diff=<driver> textconv is still refused"
  got=$(veco base tconly); st "$?:$got" '0:' "a diff=<driver> line with no version edit under it passes (over-fire control for the two arms above)"
  (cd "$VER" && git checkout -q main)
  got=$(ve base docs); st "$?:$got" '0:' "a docs-only pull request passes (null control)"
  got=$(ve main docs); st "$?:$got" '0:' "a pull request whose main has stamped since it forked passes (the arm two dots fail)"
  got=$(ve main merged); st "$?:$got" '0:' "a pull request that merged a stamped main passes (null control)"
  got=$(ve no-such-ref docs); st "$?:$got" '2:' "a main ref that does not resolve is refused, not read as no edit"
  # The call site `pr-contract` runs, not only the function.
  out=$(cd "$VER" && bash "$OLDPWD/tools/pr/prepr.sh" --version-edit base ver 2>&1); st $? 1 "--version-edit exits non-zero on a VERSION edit"
  case "$out" in *"REFUSE no version edit"*VERSION*) st 1 1 "and names what it refused";; *) st 0 1 "and names what it refused";; esac
  (cd "$VER" && bash "$OLDPWD/tools/pr/prepr.sh" --version-edit main merged >/dev/null 2>&1); st $? 0 "--version-edit exits zero on a merged, stamped main (null control)"
  rm -rf "$VER"

  # The shared-root refusal, over real directories because the predicate resolves
  # them. The defect's two shapes refuse; a seat's own subdirectory and a bare
  # `mktemp -d` pass, so a predicate refusing every temp path fails here.
  SRD=$(mktemp -d); mkdir -p "$SRD/scratchpad/seat" "$SRD/t" "$SRD/h" "$SRD/claude-501"
  shared_root "$SRD/scratchpad/body.md"; st $? 0 "a body directly in a scratchpad is refused"
  shared_root /tmp/body.md; st $? 0 "a body directly in /tmp is refused"
  TMPDIR="$SRD/t" shared_root "$SRD/t/body.md"; st $? 0 "a body directly in \$TMPDIR is refused"
  MKF=$(mktemp); shared_root "$MKF"; st $? 0 "a plain mktemp file is refused (the stated choice)"; rm -f "$MKF"
  HOME="$SRD/h" shared_root "$SRD/h/body.md"; st $? 0 "a body directly in \$HOME is refused"
  shared_root "$SRD/claude-501/body.md"; st $? 0 "a body directly in a claude-<uid> root is refused"
  : > "$SRD/scratchpad/real.md"; ln -s "$SRD/scratchpad/real.md" "$SRD/scratchpad/seat/link.md"
  shared_root "$SRD/scratchpad/seat/link.md"; st $? 0 "a link in a seat directory to a root file is refused"
  : > "$SRD/scratchpad/seat/real.md"; ln -s "$SRD/scratchpad/seat/real.md" "$SRD/h/link.md"
  shared_root "$SRD/h/link.md"; st $? 1 "a link to a seat-directory file passes (null control)"
  shared_root "$SRD/scratchpad/seat/body.md"; st $? 1 "a body in the seat's own subdirectory passes (null control)"
  shared_root "$SRD/body.md"; st $? 1 "a body in a mktemp -d directory passes (null control)"
  # The call site, not only the function: the run stops after the body-path step.
  out=$(PREPR_BODY_PATH_ONLY=1 bash tools/pr/prepr.sh "$SRD/scratchpad/body.md" 2>&1); st $? 2 "prepr.sh refuses a root body at its call site"
  case "$out" in *"REFUSE   body path"*) st 1 1 "and names the step";; *) st 0 1 "and names the step";; esac
  out=$(PREPR_BODY_PATH_ONLY=1 bash tools/pr/prepr.sh "$SRD/scratchpad/seat/body.md" 2>&1); st $? 0 "and passes a seat body there (null control)"
  case "$out" in *"ok       body path"*) st 1 1 "printing an ok line, so a skipped step is visible";; *) st 0 1 "printing an ok line, so a skipped step is visible";; esac
  rm -rf "$SRD"

  [ "$(closure_lane tests/card_drift.mjs 0)" = node-needs-linux ]; st $? 0 "a node script is not recorded without strace"
  [ "$(closure_lane tests/card_drift.mjs 1)" = record ]; st $? 0 "and is recorded with it (null control)"
  [ "$(closure_lane tests/entities.py 0)" = record ]; st $? 0 "a Python script is recorded without strace"
  [ "$(closure_lane tests/stress.py 1)" = needs-lease ]; st $? 0 "stress.py is left to CI: a push takes no gate lease"

  # R9-FR-5: the closures recorder's interpreter, resolved deliberately.
  # R9-FR-3 and R9-WEB-5 each lost a full prepr pass to the same defect:
  # derive_closures.sh records under the first python3 on PATH, and on a seat
  # whose PATH still resolves to pyenv 3.11 that interpreter cannot parse the
  # tree (the nested same-quote f-string in tests/entities.py is 3.12 syntax),
  # so the recording died at compile and step 6b refused it as "failed while
  # being recorded ... fix the script first" -- advice pointed at the wrong
  # artifact. The stub interpreters here stand for parse outcomes, so the
  # resolution logic is hermetic; the live probe's discrimination (this tree's
  # own 3.11 refused, the seat venv passed) is a body figure, not an arm.
  FB=$(mktemp -d); mkdir -p "$FB/bin" "$FB/goodbin" "$FB/empty"
  printf '#!/bin/sh\nexit 0\n' > "$FB/bin/goodpy"; chmod +x "$FB/bin/goodpy"
  printf '#!/bin/sh\nexit 1\n' > "$FB/bin/python3"; chmod +x "$FB/bin/python3"
  cp "$FB/bin/goodpy" "$FB/goodbin/python3"
  mkdir -p "$FB/state/venv-ci/bin"; cp "$FB/bin/goodpy" "$FB/state/venv-ci/bin/python3"
  mkdir -p "$FB/badstate/venv-ci/bin"; cp "$FB/bin/python3" "$FB/badstate/venv-ci/bin/python3"
  got=$(HPO_RECORDER_PYTHON=/bin/false PATH="$FB/goodbin:$PATH" recorder_python)
  st $? 1 "an override that cannot parse the tree is refused, never skipped past"
  grep -q 'HPO_RECORDER_PYTHON' <<<"$got"
  st $? 0 "and that refusal names the override, so it is not read as a missing venv"
  got=$(HPO_RECORDER_PYTHON="$FB/bin/goodpy" HPO_STATE_DIR="$FB/empty" PATH="$FB/bin:$PATH" recorder_python)
  st "$got" "$FB/bin/goodpy" "an override that parses the tree wins over every candidate behind it"
  got=$(HPO_STATE_DIR="$FB/state" PATH="$FB/goodbin:$PATH" recorder_python)
  st "$got" "$FB/state/venv-ci/bin/python3" "a parsing seat venv outranks a parsing ambient"
  got=$(HPO_STATE_DIR="$FB/badstate" PATH="$FB/goodbin:$PATH" recorder_python)
  st "$got" "python3" "a venv that cannot parse is skipped for a parsing ambient: the guard is the parse, not the path"
  got=$(HPO_STATE_DIR="$FB/empty" PATH="$FB/goodbin:$PATH" recorder_python)
  st "$got" "python3" "a parsing ambient is used as-is, so a recording under it is byte-unchanged (null control)"
  got=$(HPO_STATE_DIR="$FB/empty" PATH="$FB/bin:$PATH" recorder_python)
  st $? 1 "no candidate parsing the tree is refused before anything is recorded"
  grep -q 'seat_venv.sh' <<<"$got"
  st $? 0 "and that refusal names the venv build command, not the recording"

  # Steps 6a and 6b over a throwaway clone, driven through the functions the
  # steps print (`claims_line`, `closures_line`). Main claims a lane AFTER the
  # branches fork. Two fork from that main: one edits the claim file and keeps
  # main's list (refused as inherited); one never edits it (passes: a file
  # byte-identical to the fork point's claims nothing, R9-F10.8). One forked before
  # it writes only a delivery row (passes: CI compares with the fork point,
  # and main's tip would refuse it -- the #1591 review's E); one writes its
  # own claim (passes). For 6b a branch edits a selectable script and a stub
  # recorder hands back a recording built from the committed closure, so no
  # script runs: covered passes, an unlisted read refuses as UNDER-SCOPED,
  # the same read by a recording that exited 3 refuses as a failed recording.
  CLM=$(mktemp -d)
  G="git -c user.name=prepr -c user.email=prepr@selftest -c commit.gpgsign=false"
  # `git clone` of a local, non-bare repository checks out a branch with the
  # SAME NAME the source has checked out -- so on a push to `main` (where
  # this self-test's own checkout IS `main`) the clone starts on a branch
  # already named `main`, and the synthetic `$G checkout -q -b main fork`
  # below collides with it ("a branch named 'main' already exists"),
  # aborting this whole `&&` chain before `inh` is ever created. Detach and
  # delete whatever the clone started on first, so the fixture is hermetic
  # to the outer checkout's branch name -- `main` included.
  (git clone -q --shared . "$CLM/r" && cd "$CLM/r" \
    && startbr=$($G symbolic-ref --quiet --short HEAD || :) \
    && $G checkout -q --detach \
    && { [ -z "$startbr" ] || $G branch -q -D "$startbr"; } \
    && $G checkout -q -b fork \
    && $G checkout -q -b rec && mkdir -p docs/delivery && echo row > docs/delivery/9999.md \
    && $G add -A && $G commit -qm rec \
    && $G checkout -q -b own fork && echo "# own" >> custom_components/heatpump_optimizer/away.py \
    && echo "own_lane  # this branch's claim" >> tests/golden/claimed_drift.txt && $G commit -qam own \
    && $G checkout -q -b cl fork && echo "# a comment" >> tests/wood_advisor.py && $G commit -qam cl \
    && $G checkout -q -b main fork && echo "main_lane  # claimed on main after the fork" >> tests/golden/claimed_drift.txt \
    && $G commit -qam main && git update-ref refs/remotes/origin/main main \
    && $G checkout -q -b unt && echo "# unt" >> custom_components/heatpump_optimizer/away.py \
    && $G commit -qam unt \
    && $G checkout -q -b inh main && echo "# inh" >> custom_components/heatpump_optimizer/away.py \
    && echo "# a note this branch wrote" >> tests/golden/claimed_drift.txt \
    && $G commit -qam inh) >/dev/null 2>&1
  claims_at() { (cd "$CLM/r" && git checkout -q "$1" && got=$(claims_line); echo "$?:$(printf '%s' "$got" | grep -o -e '--drop-inherited' -e 'restore both' | head -1)"); }
  got=$(claims_at inh); st "$got" '1:--drop-inherited' "6a refuses a branch that edited the claim file and kept main's list, naming --drop-inherited"
  got=$(claims_at unt); st "$got" '0:' "6a passes a branch that never edited the claim file it inherited (R9-F10.8)"
  got=$(claims_at rec); st "$got" '0:' "6a passes a row-only branch forked before main claimed (the fork point, not the tip)"
  got=$(claims_at own); st "$got" '0:' "6a passes a branch that writes its own claim (null control)"

  mkdir "$CLM/ok" "$CLM/under" "$CLM/dead"
  python3 - "$CLM" <<'PY'
import json, pathlib, subprocess, sys
d = pathlib.Path(sys.argv[1])
s = "tests/wood_advisor.py"
files = json.loads(pathlib.Path("tests/closures.json").read_text())["closures"][s]
extra = next(f for f in subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
             if f not in files and f.endswith(".md"))
rec = {"script": s, "rc": 0, "seconds": 0.1, "files": files, "spawned": [], "how": "audithook+sys.modules", "argv": [s]}
for sub, over in (("ok", {}), ("under", {"files": files + [extra]}), ("dead", {"rc": 3, "files": files + [extra]})):
    (d / sub / "wood_advisor.py.json").write_text(json.dumps(dict(rec, **over)))
PY
  printf '#!/bin/bash\nmkdir -p "$5" && cp "$FIXTURE_REC/$(basename "$2").json" "$5/"\n[ -n "${PYLOG:-}" ] && printf '"'"'%%s\\n'"'"' "${PYTHON-}" >> "$PYLOG"\nexit 0\n' > "$CLM/rec.sh"; chmod +x "$CLM/rec.sh"
  closures_at() { (cd "$CLM/r" && git checkout -q "$1" && got=$(PREPR_RECORD="$CLM/rec.sh" FIXTURE_REC="$CLM/$2" closures_line fork); echo "$?:${got%%:*}"); }
  got=$(closures_at cl ok); st "$got" '0:scoped recordings are covered' "6b passes a scoped script its committed closure covers (null control)"
  got=$(closures_at cl under); st "$got" '1:UNDER-SCOPED' "6b refuses a scoped script that reads an unlisted file as UNDER-SCOPED"
  got=$(closures_at cl dead); st "$got" '1:failed while being recorded' "6b refuses a recording that exited non-zero as failed, not UNDER-SCOPED"
  got=$(closures_at rec under); st "${got%%:*}" 3 "6b skips a diff that reaches no selectable script, recording nothing"
  # R9-FR-5 through the step itself: the resolved interpreter reaches the
  # recorder as $PYTHON, and a resolution that refuses stops the step before
  # anything records. `cl` is the branch whose diff makes 6b scoped; the stub
  # recorder logs the PYTHON it received, since the out-dir it writes is
  # removed with the verdict. Inlined rather than through `closures_at`,
  # whose echo truncates at the first colon -- and the remedy text names
  # "seat venv: tools/audit/seat/seat_venv.sh".
  # A seat shim named python3 execs `$HPO_STATE_DIR/venv-ci/bin/python3`
  # (`seat_venv.sh --install-shims`). This arm points that variable at a stub,
  # so the shim turns `python3 tests/closure.py affected` into the stub and
  # the arm reports "derived no case" -- a red that is the shim, not the
  # recorder. Resolve an interpreter with the variable unset and put its
  # directory first on this one call. The stub stays the absolute path
  # `recorder_python` selects.
  realpy=$(env -u HPO_STATE_DIR python3 -c 'import sys; print(sys.executable)' 2>/dev/null) || realpy=""
  pybin=$PATH
  [ -n "$realpy" ] && pybin="$(dirname "$realpy"):$PATH"
  : > "$CLM/pylog"
  full=$(cd "$CLM/r" && git checkout -q cl \
    && PREPR_RECORD="$CLM/rec.sh" FIXTURE_REC="$CLM/ok" PYLOG="$CLM/pylog" \
       HPO_STATE_DIR="$FB/state" PATH="$pybin" \
       closures_line fork 2>&1); rc=$?
  st "$rc" 0 "6b records under the interpreter the resolution chose (the R9-FR-3/R9-WEB-5 arm)"
  [ "$(tail -1 "$CLM/pylog")" = "$FB/state/venv-ci/bin/python3" ]
  st $? 0 "and the recorder received that interpreter as \$PYTHON"
  : > "$CLM/pylog"
  full=$(cd "$CLM/r" && git checkout -q cl \
    && PREPR_RECORD="$CLM/rec.sh" FIXTURE_REC="$CLM/ok" PYLOG="$CLM/pylog" \
       HPO_RECORDER_PYTHON=/bin/false closures_line fork 2>&1); rc=$?
  st "$rc" 1 "6b refuses an override that cannot parse the tree instead of recording under it"
  grep -q 'seat_venv.sh' <<<"$full"
  st $? 0 "and the step's refusal names the venv build command"
  [ ! -s "$CLM/pylog" ]
  st $? 0 "and nothing recorded under the refused interpreter"
  # Step 6d over a throwaway clone, through `predict_line`: a null branch (a
  # comment in a selectable script) must stay quiet, and each red the
  # predictor names is planted alone on its own branch and must trip it with
  # its own PREDICT line -- R9-RO-11's perturbation, one arm per class.
  PDX=$(mktemp -d)
  (git clone -q --shared . "$PDX/r" && cd "$PDX/r" \
    && $G checkout -q --detach && $G checkout -q -b pfork \
    && git update-ref refs/remotes/origin/main pfork \
    && cp "$OLDPWD/tools/pr/ci_predict.py" tools/pr/ci_predict.py \
    && $G add -A && $G commit -qm predictor --allow-empty \
    && git update-ref refs/remotes/origin/main HEAD \
    && $G checkout -q -b pnull && echo "# a comment" >> tests/wood_advisor.py && $G commit -qam pnull \
    && $G checkout -q -b porphan origin/main && echo "X = 1" > custom_components/heatpump_optimizer/zz_planted.py \
    && $G add -A && $G commit -qm porphan \
    && $G checkout -q -b pimport origin/main && echo "X = 1" > custom_components/heatpump_optimizer/zz_planted.py \
    && echo "from . import zz_planted  # planted" >> custom_components/heatpump_optimizer/away.py \
    && $G add -A && $G commit -qm pimport \
    && $G checkout -q -b pfunc origin/main && echo "X = 1" > custom_components/heatpump_optimizer/zz_planted.py \
    && printf '\n\ndef _zz_planted():\n    from . import zz_planted\n    return zz_planted.X\n' >> custom_components/heatpump_optimizer/away.py \
    && $G add -A && $G commit -qm pfunc \
    && $G checkout -q -b pinert origin/main && echo "# planted" > dev/audit/harnesses/zz_planted.py \
    && $G add -A && $G commit -qm pinert \
    && $G checkout -q -b plane origin/main && echo "# planted" > tests/zz_planted_check.py \
    && $G add -A && $G commit -qm plane \
    && $G checkout -q -b pmainred origin/main && echo "# planted on main" > tests/zz_main_unrecorded_check.py \
    && $G add -A && $G commit -qm pmainred \
    && $G checkout -q -b pinh pmainred && echo "# a comment" >> tests/wood_advisor.py && $G commit -qam pinh \
    && $G checkout -q -b pmut origin/main \
    && printf '\n\ndef _zz_planted(x):\n    if x > 3:\n        return 1\n    return 0\n' >> custom_components/heatpump_optimizer/away.py \
    && $G commit -qam pmut) >/dev/null 2>&1
  predict_at() { (cd "$PDX/r" && git checkout -q "$1" && predict_line origin/main 2>&1 >/dev/null; echo "rc=$?"); }
  got=$(predict_at pnull); st "$(tail -1 <<<"$got")" rc=0 "6d stays quiet on a comment in a selectable script (null control)"
  got=$(predict_at porphan); grep -q 'PREDICT fast .*UNCLASSIFIED custom_components/heatpump_optimizer/zz_planted.py' <<<"$got"
  st $? 0 "6d predicts entities' refusal of a new file in no closure and not on INERT"
  got=$(predict_at pimport); grep -q 'PREDICT closures .*UNDER-SCOPED custom_components/heatpump_optimizer/zz_planted.py: read by .*a new import from custom_components/heatpump_optimizer/away.py' <<<"$got"
  st $? 0 "6d predicts UNDER-SCOPED for a new import from a file a closure lists"
  got=$(predict_at pfunc); grep -q 'PREDICT closures .*UNDER-SCOPED' <<<"$got"
  st $? 1 "6d predicts no UNDER-SCOPED for an import inside a function, which runs only when called (null control)"
  got=$(predict_at pinert); grep -q 'PREDICT closures .*INERT READS tests/harness_headers.py: dev/audit/harnesses/zz_planted.py' <<<"$got"
  st $? 0 "6d predicts INERT READS for a new harness beside the ones a glob-reading script lists"
  got=$(predict_at plane); grep -q 'PREDICT closures .*NO RECORDING tests/zz_planted_check.py' <<<"$got"
  st $? 0 "6d predicts NO RECORDING for a selectable script no derive lane records"
  got=$(predict_at pmut); grep -q 'PREDICT mutation .*ADDED UNPINNED custom_components/heatpump_optimizer/away.py' <<<"$got"
  st $? 0 "6d predicts ADDED UNPINNED for a guard the diff adds with no pin"
  grep -q '^rc=0$' <<<"$got"
  st $? 0 "and an unpinned site warns, never refuses: mutation-autofix may pin it after the push"
  got=$(cd "$PDX/r" && git checkout -q pinh && predict_line pmainred 2>&1 >/dev/null; echo "rc=$?")
  grep -q 'NO RECORDING' <<<"$got"
  st $? 1 "6d charges no branch with an unrecorded script main already carries (null control)"
  st "$(tail -1 <<<"$got")" rc=0 "and so the unrelated branch passes 6d"
  (cd "$PDX/r" && git checkout -q pmut && predict_line origin/main "$PDX/sites" >/dev/null 2>&1)
  st "$(grep -c . "$PDX/sites")" 3 "6d writes the three planted site keys for step 7d"
  printf 'Why.\n\n## Head\n\nx\n' > "$PDX/b0.md"
  unpinned_line "$PDX/b0.md" "$PDX/sites" >/dev/null; st $? 1 "7d refuses a body with no ## Unpinned sites when sites are owed"
  { cat "$PDX/b0.md"; printf '\n## Unpinned sites\n\n- %s: pinned by mutation-autofix\n' "$(head -1 "$PDX/sites")"; } > "$PDX/b1.md"
  got=$(unpinned_line "$PDX/b1.md" "$PDX/sites"); r=$?
  st "$r" 1 "7d refuses a section that omits a listed site"
  grep -qF "$(sed -n 2p "$PDX/sites")" <<<"$got"; st $? 0 "and names the omitted site"
  { cat "$PDX/b0.md"; printf '\n## Unpinned sites\n\n'; sed 's/$/: pinned by mutation-autofix/; s/^/- /' "$PDX/sites"; printf '\n## Figures\n\nnone\n'; } > "$PDX/b2.md"
  unpinned_line "$PDX/b2.md" "$PDX/sites" >/dev/null; st $? 0 "7d passes a section naming every listed site (null control)"
  { cat "$PDX/b0.md"; printf '\n## Figures\n\n'; sed 's/^/- /' "$PDX/sites"; } > "$PDX/b3.md"
  unpinned_line "$PDX/b3.md" "$PDX/sites" >/dev/null; st $? 1 "7d reads the keys under ## Unpinned sites only, not anywhere in the body"
  : > "$PDX/none"
  unpinned_line "$PDX/b0.md" "$PDX/none" >/dev/null; st $? 3 "7d owes nothing when the diff adds no site"
  rm -rf "$PDX"
  rm -rf "$CLM"
  rm -rf "$FB"

  # Steps 3e-3g, driven through the functions the steps call: the reader and
  # the verdict on this repository's own workflows, on a PR-only pin it must
  # not count, and on the one-job perturbations of governance.yml the #1637
  # review found passing silently; the local-run finder on copies of this
  # script with step 3e's call deleted, commented out, or moved above rc=0;
  # and the pin matcher behind 3f and step 4.
  WF=$(mktemp -d); mkdir "$WF/wf" "$WF/empty"
  OWN=dev/audit/rounds/round6/D11/fix/codeowners_gap.py; OWN_OLD=tools/audit/round6/D11/fix/codeowners_gap.py
  BOTH=$(printf '%s\n' "$OWN" "$OWN_OLD")  # the grader at both homes, in sort order
  grep -qx "$OWN" <<<"$(pinned_graders .github/workflows/*.yml)"
  st $? 0 "the pin reader finds codeowners_gap.py in a pinned job that grades main"
  pinned_verdict "$PREPR_PATH" .github/workflows/*.yml >/dev/null
  st $? 0 "this script and these workflows pass the verdict (null control)"
  printf 'jobs:\n  only-pr:\n    steps:\n      - env:\n          PINNED: ${{ github.event.pull_request.base.sha }}\n        run: |\n          git checkout "$PINNED" -- \\\n            %s\n      - run: node .claude/workflows/pr_only.mjs\n' "'x.mjs'" > "$WF/pr.yml"
  [ -z "$(pinned_graders "$WF/pr.yml")$(pinned_paths "$WF/pr.yml")$(pin_read problems "$WF/pr.yml")" ]
  st $? 0 "a pin that never grades main is not counted, and is not a problem (null control)"
  touch "$WF/empty/none.yml"
  pinned_verdict "$PREPR_PATH" "$WF/empty/none.yml" >/dev/null
  st $? 1 "a reader that finds no pinned grader at all is refused"
  grep -v 'codeowners_gap.py --check >/tmp/prepr-owners' "$PREPR_PATH" > "$WF/deleted.sh"
  [ "$(pinned_unrun "$WF/deleted.sh" .github/workflows/*.yml)" = "$BOTH" ]
  st $? 0 "a pinned grader with its local run deleted is named"
  sed 's|^if test -f .*codeowners_gap\.py --check >.*|# &|' "$PREPR_PATH" > "$WF/commented.sh"
  [ "$(pinned_unrun "$WF/commented.sh" .github/workflows/*.yml)" = "$BOTH" ]
  st $? 0 "a pinned grader whose local run is commented out is named"
  awk -v c="python3 -I $OWN --check" '/^rc=0$/ { print c } { print }' "$WF/deleted.sh" > "$WF/above.sh"
  [ "$(pinned_unrun "$WF/above.sh" .github/workflows/*.yml)" = "$BOTH" ]
  st $? 0 "a pinned grader called only above rc=0 is named"
  for pert in unquoted braced no-pinned-line env-indirect x-flag bare-python uv-run continuation indent4 renamed queue-base; do
    rm -f "${WF:?}/wf/"*.yml; cp .github/workflows/*.yml "$WF/wf/"
    PERT=$pert python3 - "$WF/wf/governance.yml" <<'PY'
import os, sys
p = sys.argv[1]; s = open(p).read(); k = os.environ["PERT"]
own = "python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check"
full = "if test -f tools/audit/round6/D11/fix/codeowners_gap.py; then python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check; else " + own + "; fi"
if k == "unquoted": t = s.replace('git checkout "$PINNED" --', 'git checkout $PINNED --', 1)
elif k == "braced": t = s.replace('git checkout "$PINNED" --', 'git checkout "${PINNED}" --', 1)
elif k == "no-pinned-line": t = s.replace("PINNED: ${{ github.event.pull_request.base.sha || github.sha }}\n", "", 1)
elif k == "env-indirect": t = s.replace("PINNED: ${{ github.event.pull_request.base.sha || github.sha }}", "PINNED: ${{ env.PIN_SHA }}", 1)
elif k == "x-flag": t = s.replace(own, own.replace("-I ", "-I -X utf8 "), 1)
elif k == "bare-python": t = s.replace(own, own.replace("python3 ", "python "), 1)
elif k == "uv-run": t = s.replace(own, "uv run " + own.replace("python3 ", "python "), 1)
elif k == "indent4":  # YAML-equal: every line under `jobs:` two spaces deeper
    head, _, body = s.partition("\njobs:\n")
    t = head + "\njobs:\n" + "".join("  " + l if l.strip() else l for l in body.splitlines(True))
elif k == "renamed": t = s.replace("PINNED", "PIN")
elif k == "queue-base": t = s.replace("PINNED: ${{ github.event.pull_request.base.sha || github.sha }}",
                                      "PINNED: ${{ github.event.pull_request.base.sha || github.event.merge_group.base_sha || github.sha }}")
else: t = s.replace("run: " + full, "run: |\n          if test -f tools/audit/round6/D11/fix/codeowners_gap.py; then python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check; else python3 -I \\\n            dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check; fi", 1)
assert t != s, k
open(p, "w").write(t)
PY
    pinned_verdict "$WF/deleted.sh" "$WF/wf/"*.yml >/dev/null
    st $? 1 "governance.yml perturbed ($pert), with step 3e's run deleted, is refused"
    # The reader reads a shape it knows rather than refusing it: with 3e's run
    # present, each of these passes (null control).
    case $pert in x-flag|bare-python|uv-run|continuation|indent4|queue-base)
      pinned_verdict "$PREPR_PATH" "$WF/wf/"*.yml >/dev/null
      st $? 0 "governance.yml perturbed ($pert), with step 3e's run present, passes (null control)" ;;
    esac
  done
  # The last job of a file is flushed when the next file starts: its problem
  # must name its own file. A pin named outside every job is refused too.
  printf 'jobs:\n  last:\n    steps:\n      - run: git checkout "$PIN" -- %s\n' "'x.mjs'" > "$WF/a.yml"
  printf 'jobs:\n  other:\n    steps: []\n' > "$WF/b.yml"
  grep -q "^unclassified $WF/a.yml:last " <<<"$(pin_read problems "$WF/a.yml" "$WF/b.yml")"
  st $? 0 "a problem names the file its job is in, not the file read next"
  printf 'env:\n  PINNED: ${{ github.sha }}\njobs:\n  a:\n    steps: []\n' > "$WF/c.yml"
  grep -q "^unclassified $WF/c.yml: outside any job" <<<"$(pin_read problems "$WF/c.yml")"
  st $? 0 "a pin named outside every job is refused"
  printf '%s\n' .claude/workflows/check-wave-script.mjs > "$WF/changed"
  pinned_touched "$WF/changed" "$(pinned_paths .github/workflows/*.yml)"
  st $? 0 "a change to a pinned .mjs touches a pin"
  printf '%s\n' tools/audit/record-predicate/x.py > "$WF/changed"
  pinned_touched "$WF/changed" "$(pinned_paths .github/workflows/*.yml)"
  st $? 0 "a change under a pinned directory touches a pin"
  printf '%s\n' README.md docs/HANDOVER.md > "$WF/changed"
  pinned_touched "$WF/changed" "$(pinned_paths .github/workflows/*.yml)"
  st $? 1 "a change to no pinned path touches none (null control)"
  rm -rf "${WF:?}"

  printf 'Closes #999\n' | if test -f tools/audit/preflight.sh; then bash tools/audit/preflight.sh >/dev/null 2>&1; else bash tools/pr/preflight.sh >/dev/null 2>&1; fi
  st $? 1 "preflight refuses an unintended closing keyword"
  printf 'Closes #999\n' | if test -f tools/audit/preflight.sh; then bash tools/audit/preflight.sh 999 >/dev/null 2>&1; else bash tools/pr/preflight.sh 999 >/dev/null 2>&1; fi
  st $? 0 "preflight accepts an intended one (null control)"

  # transport_in_ancestry, on a throwaway repository: one null control per arm
  # that must pass, and each refused shape built the way a seat produced it.
  TR=$(mktemp -d)
  (
    set -e; cd "$TR"; git init -q -b main .
    git config user.name st; git config user.email st@st
    mkdir -p tools/audit/handoff/old; echo x > tools/audit/handoff/old/BODY.md
    echo a > code; git add -A; git commit -qm base
    git checkout -q -b clean; echo b > code; git commit -qam code
    git checkout -q -b above clean; mkdir -p tools/audit/handoff/t
    echo b > tools/audit/handoff/t/BODY.md; git add -A; git commit -qm transport
    echo c > code; git commit -qam "code above the transport"
    git checkout -q -b cancelled above; git rm -q tools/audit/handoff/t/BODY.md
    git commit -qm "strip the transport"
    git checkout -q -b side clean; git checkout -q -b note clean; mkdir -p handoff/r
    echo n > handoff/r/RESUME.md; git add -A; git commit -qm note
    git rm -q handoff/r/RESUME.md; git commit -qm "drop the note"
    git checkout -q side; git merge -q --no-ff --no-edit note
    git checkout -q -b tidy clean; git rm -q tools/audit/handoff/old/BODY.md
    git commit -qm "delete a transport file main carries"
    git checkout -q -b main2 main; mkdir -p tools/audit/handoff/m
    echo m > tools/audit/handoff/m/BODY.md; git add -A; git commit -qm "main moves"
    git checkout -q -b merged clean; git merge -q --no-edit main2
    git checkout -q -b resolved clean; git merge -q --no-commit main2
    echo r > tools/audit/handoff/t.md; git add -A; git commit -qm "merge main"
  ) >/dev/null 2>&1
  for c in "clean 0 a code head over a base that carries a transport file passes (null control)" \
           "above 1 a code commit above a body transport commit is refused" \
           "cancelled 1 a body added and deleted again is still refused" \
           "side 1 a resume note hidden behind a tree-identical merge is refused" \
           "tidy 0 deleting a transport file main carries passes (null control)"; do
    set -- $c; br=$1; want=$2; shift 2
    (cd "$TR" && transport_in_ancestry main "$br" >/dev/null 2>&1); st $? "$want" "transport: $*"
  done
  (cd "$TR" && transport_in_ancestry main2 merged >/dev/null 2>&1); st $? 0 "transport: merging a main that carries a transport file passes (null control)"
  (cd "$TR" && transport_in_ancestry main2 resolved >/dev/null 2>&1); st $? 1 "transport: a body written in a merge's own resolution is refused"
  (cd "$TR" && transport_in_ancestry main no-such-ref >/dev/null 2>&1); st $? 2 "transport: an unreadable range is refused, never passed"
  rm -rf "${TR:?}"

  # selftest_owed: the trigger for step 3h.
  SO=$(mktemp)
  printf '%s\n' "$PREPR_PATH" > "$SO"; selftest_owed "$SO"; st $? 0 "a change to prepr.sh owes the self-test"
  printf '%s\n' tools/policy/policy_lint.mjs > "$SO"; selftest_owed "$SO"; st $? 0 "a change to a program a step runs owes the self-test"
  printf '%s\n' tools/policy/fixtures/policy-rot/prepr/good.md > "$SO"; selftest_owed "$SO"; st $? 0 "a change to a fixture owes the self-test"
  printf '%s\n' README.md docs/HANDOVER.md > "$SO"; selftest_owed "$SO"; st $? 1 "a change to none of them owes nothing (null control)"
  selftest_inputs > "$SO.in"
  for p in tools/pr/preflight.sh tools/policy/figure_lint.mjs tests/env_drift.py \
           tools/policy/counts.mjs tools/policy/render_md.mjs; do
    grep -qxF "$p" "$SO.in"; st $? 0 "the derived inputs name $p"
  done
  rm -f "$SO.in"
  rm -f "$SO"

  printf '\n%s passed, %s failed\n' "$st_pass" "$st_fail"
  [ "$st_fail" -eq 0 ] || exit 2
  exit 0
fi

rc=0
digest=""
ORDER=""
say() { printf '  %-8s %-22s %s\n' "$1" "$2" "${3:-}"; }
step() { # name, rc, detail
  digest="${digest}$2"
  if [ "$2" -eq 0 ]; then say ok "$1" "${3:-}"; else say REFUSE "$1" "${3:-}"; rc=1; fi
}

# --- 0. the body is not in a root other seats write to (`shared_root` above).
# First, and fatal: every later step would read a file another seat may rewrite.
if [ -n "${1:-}" ]; then
  if shared_root "$1"; then
    say REFUSE "body path" "$1 sits directly in a root other seats write to -- move it to your own subdirectory, e.g. <abs-scratch>/<seat>/"
    exit 2
  fi
  say ok "body path" "not directly in a shared root"
  [ -z "${PREPR_BODY_PATH_ONLY:-}" ] || exit 0
fi

# --- 1. the merge base resolves.
# A shallow clone answers "no common ancestor" and every scoped command below
# then measures against nothing. HANDOVER trap 11: the fiction is silent.
BASE=$(git merge-base origin/main HEAD 2>/dev/null)
if [ -z "$BASE" ]; then
  say REFUSE "merge-base" "no common ancestor with origin/main -- git fetch --unshallow origin"
  exit 2
fi
step "merge-base" 0 "$BASE"

# --- 1a. no transport file in any commit the branch adds (`transport_in_ancestry`).
TRANSPORT=$(transport_in_ancestry "$BASE" HEAD)
case $? in
  0) step "transport" 0 "no commit since the merge base writes under ${TRANSPORT_ROOTS[*]}" ;;
  1) step "transport" 1 "$(echo $TRANSPORT) -- transport is in the code head's ancestry; the body goes on the orphan ref handoff-body/<topic> (fixer.md step 6), and the code head is re-cut without these commits" ;;
  *) step "transport" 1 "$BASE..HEAD could not be read, so nothing was compared" ;;
esac

# --- 2. the scoped gate's MODE line, printed rather than inferred.
# CLAUDE.md rule 1: `MODE: SCOPED -- 0 script(s) run` and `MODE: FULL` both
# print zero and mean opposite things. Printing it is the whole step; a seat
# that has not seen the line has not decided what to run.
MODE=$(python3 tests/closure.py select --diff "$BASE" 2>/dev/null | grep -oE 'MODE: [A-Z]+' | head -1)
step "gate mode" 0 "${MODE:-(no mode line)}"

# --- 3. the policy corpus.
if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs >/tmp/prepr-policy.$$ 2>&1; else node tools/policy/policy_lint.mjs >/tmp/prepr-policy.$$ 2>&1; fi
step "policy_lint" $? "$(tail -2 /tmp/prepr-policy.$$ | tr '\n' ' ')"
rm -f /tmp/prepr-policy.$$

# --- 3a. no corpus check survives its own deletion.
# 350ms, against 1.6s for the lint pass beside it: the lane runs the acceptance
# only, never the corpus. Three checks reached main measuring nothing, so the
# cheaper detector this answers to is this one.
if test -f .claude/workflows/policy_lint_mutants.mjs; then node .claude/workflows/policy_lint_mutants.mjs >/tmp/prepr-mutants.$$ 2>&1; else node tools/policy/policy_lint_mutants.mjs >/tmp/prepr-mutants.$$ 2>&1; fi
step "mutants" $? "$(tail -1 /tmp/prepr-mutants.$$)"
rm -f /tmp/prepr-mutants.$$

# --- 3b. the generated Cursor rules match their source.
if test -f .claude/workflows/rules_sync.mjs; then node .claude/workflows/rules_sync.mjs --check >/tmp/prepr-rules.$$ 2>&1; else node tools/policy/rules_sync.mjs --check >/tmp/prepr-rules.$$ 2>&1; fi
step "rules_sync" $? "$(tail -1 /tmp/prepr-rules.$$)"
rm -f /tmp/prepr-rules.$$

# --- 3c. the five copies of the shared prompt block are the canonical text.
if test -f .claude/workflows/fragments_sync.mjs; then node .claude/workflows/fragments_sync.mjs >/tmp/prepr-frag.$$ 2>&1; else node tools/policy/fragments_sync.mjs >/tmp/prepr-frag.$$ 2>&1; fi
step "fragments" $? "$(tail -1 /tmp/prepr-frag.$$)"
rm -f /tmp/prepr-frag.$$

# --- 3d. the hooks this repository wires are present and self-testing.
if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs --hooks >/tmp/prepr-hooks.$$ 2>&1; else node tools/policy/policy_lint.mjs --hooks >/tmp/prepr-hooks.$$ 2>&1; fi
step "hooks" $? "$(tail -1 /tmp/prepr-hooks.$$)"
rm -f /tmp/prepr-hooks.$$

# --- 3e. no file a workflow executes lacks an owner, on this head's copy of
# what the walk reads (`pinned_graders` above: #1633 R1a). 0.6 s, so always.
if test -f tools/audit/round6/D11/fix/codeowners_gap.py; then python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check >/tmp/prepr-owners.$$ 2>&1; else python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check >/tmp/prepr-owners.$$ 2>&1; fi
step "codeowners_gap" $? "$(grep -E '^REFUSED|uncovered_files=' /tmp/prepr-owners.$$ | tr '\n' ' ')"
rm -f /tmp/prepr-owners.$$

# --- 3f. when the diff touches a pinned path, CI's pinned jobs grade this
# pull request with the base's copy of it; the graders that run below only on
# their own inputs (brief_lint here, the wave script in step 4) run on this
# head's copy instead, since a pinned path can be any grader's data (#1637).
git diff --name-only "$BASE"...HEAD > /tmp/prepr-changed.$$
PIN_TOUCHED=1
pinned_touched /tmp/prepr-changed.$$ "$(pinned_paths .github/workflows/*.yml)" && PIN_TOUCHED=0
rm -f /tmp/prepr-changed.$$
if [ "$PIN_TOUCHED" -eq 0 ]; then
  if test -f .claude/workflows/brief_lint.mjs; then node .claude/workflows/brief_lint.mjs >/tmp/prepr-briefs.$$ 2>&1; else node tools/policy/brief_lint.mjs >/tmp/prepr-briefs.$$ 2>&1; fi
  step "brief_lint" $? "$(tail -1 /tmp/prepr-briefs.$$)"
  rm -f /tmp/prepr-briefs.$$
else
  say skip "brief_lint" "no pinned path changed, so CI's briefs job reads this head's copy"
fi

# --- 3f2. the contract re-run's decision, from its own fixtures (D13-s1-03).
# `pr-contract-rerun.yml` runs the default branch's copy; its self-test is
# offline and under a second, so the local path is the self-test.
if test -f .claude/workflows/contract_rerun.py; then python3 -I .claude/workflows/contract_rerun.py --self-test >/tmp/prepr-crr.$$ 2>&1; else python3 -I tools/pr/contract_rerun.py --self-test >/tmp/prepr-crr.$$ 2>&1; fi
step "contract_rerun" $? "$(tail -1 /tmp/prepr-crr.$$)"
rm -f /tmp/prepr-crr.$$

# --- 3f3. field coverage (I3 barrier), which `policy-docs` runs from the base
# once the base carries it. The whole program: without `gh` its ruleset arm
# prints its UNCHECKED skip, and the other arms are offline.
if test -f .claude/workflows/field_coverage.mjs; then node .claude/workflows/field_coverage.mjs >/tmp/prepr-fc.$$ 2>&1; else node tools/policy/field_coverage.mjs >/tmp/prepr-fc.$$ 2>&1; fi
step "field coverage" $? "$(tail -1 /tmp/prepr-fc.$$)"
rm -f /tmp/prepr-fc.$$

# --- 3f4. the agreement lane (I4 barrier), which `wave-script` runs from the
# base once the base carries it: the Python readers first, under -I, then the
# lane over their answers. Needs full history for its merge-subject corpus.
if test -f .claude/workflows/agreement_py.py; then
  python3 -I .claude/workflows/agreement_py.py --out /tmp/prepr-ag.$$.json >/tmp/prepr-ag.$$ 2>&1
else
  python3 -I tools/policy/agreement_py.py --out /tmp/prepr-ag.$$.json >/tmp/prepr-ag.$$ 2>&1
fi \
  && if test -f .claude/workflows/agreement.mjs; then node .claude/workflows/agreement.mjs --py-json /tmp/prepr-ag.$$.json >>/tmp/prepr-ag.$$ 2>&1; else node tools/policy/agreement.mjs --py-json /tmp/prepr-ag.$$.json >>/tmp/prepr-ag.$$ 2>&1; fi
step "agreement lane" $? "$(tail -1 /tmp/prepr-ag.$$)"
rm -f /tmp/prepr-ag.$$ /tmp/prepr-ag.$$.json

# --- 3f5. the register check (class R-register), which `wave-script` runs on the
# branch's own copy of the checker, not a pinned one: this head's ledger and the
# rounds in the tree. Ownership (CODEOWNERS) is the only protection against a
# branch editing the checker. Well under a second.
python3 -I tools/audit/fold_ledger.py --self-test >/tmp/prepr-fl.$$ 2>&1 \
  && python3 -I tools/audit/fold_ledger.py check >>/tmp/prepr-fl.$$ 2>&1
step "register check" $? "$(tail -1 /tmp/prepr-fl.$$)"
rm -f /tmp/prepr-fl.$$

# --- 3f6. no tracked script, workflow or decision record tied to a temp or
# machine path, which `instrument-self-tests` runs on the branch's own copy.
python3 -I tools/audit/seat/tmp_paths.py --self-test >/tmp/prepr-tp.$$ 2>&1 \
  && python3 -I tools/audit/seat/tmp_paths.py --check >>/tmp/prepr-tp.$$ 2>&1
step "temp paths" $? "$(tail -1 /tmp/prepr-tp.$$)"
rm -f /tmp/prepr-tp.$$

# --- 3g. every grader a pinned job runs has a local path here, or a reason,
# and the reader understood every pinned job (`pinned_verdict` above).
VERDICT=$(pinned_verdict "$PREPR_PATH" .github/workflows/*.yml)
step "pinned graders" $? "$(echo $VERDICT)"

# --- 3h. the self-test, when this diff can move one of its rows (`selftest_owed`).
# CI's `governance` job runs it on every pull request; this is the cheaper
# detector. A diff that cannot be listed is treated as owing it.
if ! git diff --name-only "$BASE"...HEAD > /tmp/prepr-st.$$ 2>/dev/null \
     || selftest_owed /tmp/prepr-st.$$; then
  if test -f tools/audit/prepr.sh; then bash tools/audit/prepr.sh --self-test >/tmp/prepr-stlog.$$ 2>&1; else bash tools/pr/prepr.sh --self-test >/tmp/prepr-stlog.$$ 2>&1; fi
  step "self-test" $? "$(tail -1 /tmp/prepr-stlog.$$; grep -E '^  FAIL' /tmp/prepr-stlog.$$ | head -3 | tr '\n' ' ')"
  rm -f /tmp/prepr-stlog.$$
else
  say skip "self-test" "no change to prepr.sh, a program it names or its fixtures"
fi
rm -f /tmp/prepr-st.$$

# --- 4. the wave script's branching, when the branch touched any of its inputs.
#
# THREE THINGS DECIDE THIS CHECK'S OUTCOME and the gate watched one of them.
# It keyed on `web-fix-wave.js`, the script under test, and so skipped itself
# on a branch whose change was to `check-wave-script.mjs` -- the checker -- and
# on one that deleted rosters, which are the population it measures. Both
# happened: the archive branch dropped three of seven rosters and this file
# printed `skip wave-script -- web-fix-wave.js untouched` while the roster
# population fell 30%, and the branch that fixed the checker was skipped by the
# gate meant to cover it. That is decisions/0004's class in a shell script: an
# assertion that is correct, that did not run, and whose run looks identical to
# one where it did. CI's `wave-script` job is unconditional, so nothing shipped
# unmeasured -- but a local gate that skips exactly when the change is in scope
# teaches a seat that the check is covered when it is not.
# THE BRIEFS ARE A FOURTH INPUT, and the same shape repeated once more (#1062):
# the checker parses every backticked verdict example out of tools/audit/briefs/
# against VERDICT_RE, so a briefs-only branch that shortened one example was
# printed `skip` here and went red on CI's unconditional job.
if [ "$PIN_TOUCHED" -eq 0 ] || ! git diff --quiet "$BASE"...HEAD -- \
     .claude/workflows/web-fix-wave.js \
     .claude/workflows/check-wave-script.mjs \
     tools/policy/check-wave-script.mjs \
     '.claude/workflows/wave-*-groups.json' \
     'tools/audit/briefs/*.md'; then
  if test -f .claude/workflows/check-wave-script.mjs; then node .claude/workflows/check-wave-script.mjs >/tmp/prepr-wave.$$ 2>&1; else node tools/policy/check-wave-script.mjs >/tmp/prepr-wave.$$ 2>&1; fi
  step "wave-script" $? "$(tail -1 /tmp/prepr-wave.$$)"
  rm -f /tmp/prepr-wave.$$
else
  say skip "wave-script" "no change to the script, the checker, the rosters, the briefs or a pinned path"
fi

# --- 5. VERSION, the manifest and the notes heading are untouched.
# Versions are assigned after the merge by tools/release/stamp.py. A branch that
# moves one is refused by the stamp, which is a slow way to find out.
# `version_edit` is also what `pr-contract` runs, through --version-edit above,
# so this is the cheaper detector for the same refusal rather than a second one.
STAMPED=$(version_edit origin/main HEAD)
step "no version edit" $? "$STAMPED"

# --- 6. claim files byte-identical to origin/main.
# A branch that claims nothing does not touch them at all, and one that does not
# touch them cannot collide with another branch's claim (#570).
CLAIMS=$(git diff --name-only origin/main...HEAD -- \
  tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt | tr '\n' ' ')
if [ -n "${CLAIMS// /}" ]; then
  say check "claim files" "$CLAIMS changed -- intended only if this branch claims drift"
else
  step "claim files" 0 "byte-identical to origin/main"
fi

# --- 6a. no inherited claim list: `fast`'s INHERITED CLAIMS, before CI.
# CI's own command with CI's own arguments (`claims_check` above).
CLAIMS_LINE=$(claims_line)
step "claims hygiene" $? "$CLAIMS_LINE"

# --- 6b. the closures cover what the scoped scripts read: `closures`'s
# UNDER-SCOPED, before CI. The scope is CI's own derivation (`closure.py
# affected`, three-dot), the recordings are `--record-only` so the committed
# file is compared and never rewritten, and a full re-record is never run here
# (gate-scoping.md). It runs the scoped scripts once, without the gate lease,
# so a script that needs one is left to CI (`closure_lane`);
# PREPR_SKIP_CLOSURES=1 skips it on a push that only re-bodies.
if [ -n "${PREPR_SKIP_CLOSURES:-}" ]; then
  say skip "closures" "PREPR_SKIP_CLOSURES is set -- closures-autofix is the only check left"
else
  CLOSURES_LINE=$(closures_line "$BASE")
  case $? in
    3) say skip "closures" "$CLOSURES_LINE" ;;
    0) step "closures" 0 "$CLOSURES_LINE" ;;
    *) step "closures" 1 "$CLOSURES_LINE" ;;
  esac
fi

# --- 6d. the CI reds a static read of the diff predicts (`predict_line`).
UNPINNED_SITES=/tmp/prepr-unpinned.$$
PREDICT_LINE=$(predict_line origin/main "$UNPINNED_SITES")
case $? in
  3) say skip "ci predict" "$PREDICT_LINE" ;;
  0) step "ci predict" 0 "$PREDICT_LINE" ;;
  *) step "ci predict" 1 "$PREDICT_LINE" ;;
esac
if [ -s "$UNPINNED_SITES" ]; then
  say WARN "unpinned sites" "$(grep -c . "$UNPINNED_SITES") site(s) the diff adds with no pin -- the body owes each a line under ## Unpinned sites (step 7d)"
fi

# --- 6c. a test must import the production symbol: tests.yml's `no-copies`,
# before the push. `copies_line` above. The scan reads the whole tree, so it
# runs only when the diff can introduce a shared top-level name; any other
# diff skips and says so. A path list that did not derive refuses: an empty
# list would read as "no python changed", which is the fail-open.
COPY_PATHS=/tmp/prepr-copies.$$
if diff_paths "$BASE" "$COPY_PATHS"; then
  COPIES_LINE=$(copies_line "$PWD" "$COPY_PATHS")
  case $? in
    3) say skip "no-copies" "$COPIES_LINE" ;;
    0) step "no-copies" 0 "$COPIES_LINE" ;;
    *) step "no-copies" 1 "$COPIES_LINE" ;;
  esac
else
  step "no-copies" 1 "the changed-path list did not derive from $BASE...HEAD, so no-copies was not run"
fi
rm -f "$COPY_PATHS"

# --- 7. the body, when one was passed.
BODY="${1:-}"
if [ -n "$BODY" ] && [ "$BODY" != "--self-test" ]; then
  # THE INTENDED ISSUES ARE FORWARDED, and before they were, this step refused
  # every body that closed one. `preflight.sh` refuses a closing keyword whose
  # number is not in the list it was given, and this script gave it none -- so
  # `Closes #N`, which `tools/audit/briefs/fixer.md` step 7 REQUIRES of a fix
  # body, made the pre-PR gate exit non-zero with nothing wrong. CI does not
  # catch that in either direction: `pr-contract` runs the same script as
  # `preflight.sh ... || true`, so the check binds nowhere. Found by the first
  # body in twenty merges to carry a closing keyword.
  shift
  if test -f tools/audit/preflight.sh; then bash tools/audit/preflight.sh "$@" < "$BODY"; else bash tools/pr/preflight.sh "$@" < "$BODY"; fi
  step "preflight" $?
  # THE PATHS ARE THE SECOND INPUT, and until #1053 this step had only the
  # first. `diff_paths` above carries why they are derived three-dot and with
  # `--no-renames`, and why a derivation that fails refuses here rather than
  # letting the check run against a list nothing wrote. `pr-contract` runs the
  # same node script with the same two inputs, so this stays the cheaper
  # detector rather than a second opinion.
  PATHS=/tmp/prepr-paths.$$
  if diff_paths "$BASE" "$PATHS"; then
    # body_line feeds `--red budget-raise-gate` when the diff raises a budget
    # leaf, then runs this same body_check. A base with no gate skips that
    # name and still runs the check.
    body_line "$BODY" "$(git rev-parse HEAD)" "$(git log -1 --format=%s)" "$PATHS" "$BASE" HEAD \
      >/tmp/prepr-body.$$ 2>&1
    step "pr-body" $? "$(tail -1 /tmp/prepr-body.$$)"
    rm -f /tmp/prepr-body.$$
  else
    step "pr-body" 1 "the changed-path list did not derive from $BASE...HEAD, so the \`## Approval\` gate was not run -- an empty list reads as \"touches no policy file\", which is the fail-open it exists to close"
  fi

  # --- 7a. every figure's command resolves. `pr-contract` runs the same script,
  # so this is the cheaper detector rather than a second opinion: the #715
  # defect it answers cost a review round to find, and finding it here costs one
  # node spawn on a body a seat is about to open.
  figures_check "$BODY" >/tmp/prepr-fig.$$ 2>&1
  step "figures" $? "$(tail -1 /tmp/prepr-fig.$$)"
  rm -f /tmp/prepr-fig.$$

  # --- 7d. each unpinned site step 6d listed has its disposition (`unpinned_line`).
  UNPINNED_LINE=$(unpinned_line "$BODY" "$UNPINNED_SITES")
  case $? in
    3) say skip "unpinned sites" "$UNPINNED_LINE" ;;
    0) step "unpinned sites" 0 "$UNPINNED_LINE" ;;
    *) step "unpinned sites" 1 "$UNPINNED_LINE" ;;
  esac

  # --- 7b. and is the head it names one the REMOTE already has? push_order above
  # carries the reasoning; this derives the branch's OWN remote branch -- the
  # local mirror of the ref a pull request's head points at -- and prints the
  # verdict. Never `@{u}`: that names whatever the branch was cut from, which on
  # git's default `git checkout -b foo origin/main` is `origin/main`.
  BR=$(git branch --show-current 2>/dev/null)
  UPREF=$(pr_head_ref "$BR" "$(git config --get "branch.$BR.remote" 2>/dev/null)") || UPREF=""
  UPSHA=""
  [ -n "$UPREF" ] && UPSHA=$(git rev-parse --verify --quiet "refs/remotes/$UPREF")
  BEHIND=0; AHEAD=0
  if [ -n "$UPSHA" ]; then
    read -r BEHIND AHEAD < <(git rev-list --left-right --count "$UPSHA...HEAD" 2>/dev/null)
    BEHIND=${BEHIND:-0}; AHEAD=${AHEAD:-0}
  fi
  push_order "$UPSHA" "$BEHIND" "$AHEAD"
  case $? in
    0) step "push order" 0 "$UPREF is at $(git rev-parse --short HEAD) -- local mirror, unfetched" ;;
    3) if [ -z "$UPREF" ]; then
         say skip "push order" "HEAD is detached, so no branch of this repository is the pull request's head"
       else
         say skip "push order" "no $UPREF yet; the push creates it, so pass $BODY to --body-file after it"
       fi ;;
    4) ORDER="HEAD is $AHEAD commit(s) ahead of $UPREF"
       say WARN "push order" "$ORDER -- A PUSH MUST FOLLOW THIS BODY EDIT" ;;
    1) step "push order" 1 "$UPREF -- this branch's own remote branch, which is the pull request's head ref -- holds $BEHIND commit(s) HEAD does not, so no push makes \`## Head\` the pull request's head -- merge $UPREF, then rewrite it" ;;
    5) step "push order" 1 "$UPREF and HEAD have diverged, $BEHIND commit(s) there against $AHEAD here: the push is refused as a non-fast-forward and the force-push past it is forbidden -- merge $UPREF, then rewrite \`## Head\` at the merge commit" ;;
    *) step "push order" 1 "$UPREF: unknown push-order verdict" ;;
  esac

  # --- 7c. the ancestry red-check arm (`reds_line` above): the second pass of
  # pr-body, fed every red a PUSHED commit of this branch carries -- the fix
  # reviewer's root-cause trigger (defect-root-cause.md), moved to push time,
  # where repairing it is one body edit instead of a review round (#1860). It
  # runs after 7b because it reads the same remote head ref 7b derives, and
  # needs the path list pr-body derived: without one the body check it feeds
  # was not run, and the arm says so rather than feeding it nothing.
  if [ ! -f "$PATHS" ]; then
    say skip "ancestry reds" "no changed-path list, so the body check this arm feeds was not run"
  elif [ -z "$UPREF" ]; then
    say skip "ancestry reds" "HEAD is detached or the branch unnamed, so no remote branch of this repository is the pull request's head"
  elif [ -z "$UPSHA" ]; then
    say skip "ancestry reds" "no $UPREF yet; the push creates it, so no commit of this branch has check runs to read"
  else
    REDS_LINE=$(reds_line "$BODY" "$(git rev-parse HEAD)" "$(git log -1 --format=%s)" "$PATHS" "$UPREF")
    case $? in
      0) step "ancestry reds" 0 "$REDS_LINE" ;;
      3) say skip "ancestry reds" "$REDS_LINE" ;;
      *) step "ancestry reds" 1 "$REDS_LINE" ;;
    esac
  fi
  rm -f "$PATHS"
else
  say skip "body" "no body passed"
fi

if [ -n "$ORDER" ]; then
  printf '\n  !!! %s, so `pr-contract` -- which reads\n' "$ORDER"
  printf '  !!! the PULL REQUEST head, not this one -- refuses this body on any run that\n'
  printf '  !!! fires before the push, the `edited` run setting it fires included.\n'
  printf '  !!! steward S10 ACCEPTS that on one condition: the push follows immediately, so\n'
  printf '  !!! the refusal lands on a commit you abandon. #691 head b2cfbc9 is that pair --\n'
  printf '  !!! green 19:53:33Z, refused 54s later, and 99ee4b9 became the head.\n'
  printf '  !!! If setting the body is your LAST action, the refusal stays on your head.\n'
fi

rm -f "${UNPINNED_SITES:-}"
echo
echo "PRE-PR: $(git rev-parse HEAD) $digest"
exit $rc
