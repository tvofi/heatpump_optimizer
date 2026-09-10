#!/usr/bin/env bash
#
# Run the whole test suite in dependency order.
#
#   ./tests/run.sh
#
# The Home Assistant stub lives in `tests/hastub` and is version-controlled, so
# the suite is reproducible; it used to sit in /tmp and vanish on reboot.
# `plan_view.py` writes the plan payload (HPO_PLANDATA, or a per-checkout
# default both sides derive identically), which `card.mjs` then reads, so the
# order below is not arbitrary.
#
# GOLDEN_MODE picks how the characterization fixtures are checked:
#   strict (default) — exact comparison against the committed fixtures, plus
#     the five-fixture env_drift gate against GOLDEN_REF (default origin/main).
#   drift — no exact comparison at all; instead env_drift.py --all captures
#     every scenario from this tree AND from GOLDEN_REF in the same
#     environment and requires them identical. This is what CI runs: solver
#     floats are not bit-stable across BLAS builds, so comparing this
#     machine's output against fixtures recorded on another would cry wolf.
#
# The suite runs in LANES, not one long line. Every script still runs, with
# the same arguments, and every failure still counts; what changed is that
# independent lanes share the box. Three things decide the shape:
#
#   * `plan_view.py` writes the payload `card.mjs` reads, so those two stay
#     in one lane, in that order. That ordering is load-bearing.
#   * `stress.py` runs ALONE, after every other lane has finished. Its
#     solve-time guard measures this machine while it solves; sharing the
#     box with three other Python processes is exactly the noise that guard
#     exists to see through, and it should not have to see through noise
#     this suite made itself.
#   * Nothing else shares mutable state: the only files any of them write
#     are the plan payload above and per-run temporary directories. Two
#     scripts touch git, and both do the same thing with it: env_drift.py
#     and stress.py each add a detached worktree of GOLDEN_REF under a
#     mktemp directory, capture from it, and remove it again (#387 -- the
#     solver-work check compares this tree against the merge base in one
#     environment rather than against recorded numbers, for the same
#     reason env_drift does). Neither writes anything a lane could see.
#
# GATE_JOBS controls it: unset (default) uses the smaller of `nproc` and 3
# lanes; GATE_JOBS=1 runs everything serially with live streaming output,
# which is the old behaviour and the thing to reach for when a failure needs
# watching as it happens.
#
# SCOPING. A full run is about forty minutes; a change to the card genuinely
# needs about five seconds of it. GATE_SCOPE=auto runs only the scripts the
# change can reach, decided from the MEASURED dependency closures in
# tests/closures.json (see tests/closure.py -- they are recorded by running
# the suite under instrumentation, never written by hand).
#
#   GATE_SCOPE=full   (the DEFAULT, everywhere) run every script.
#   GATE_SCOPE=auto   scope to the diff against GATE_SCOPE_BASE
#                     (default origin/main).
#
# Scoping is off unless it is asked for, and it turns itself off again --
# running everything -- whenever it cannot be sure: no closures file, a
# closure missing for some script, a changed file no recorded closure
# mentions, or any change to the gate itself. tests/env_drift.py additionally
# always runs when anything under custom_components/ changed, because it
# compares behaviour rather than imports and no file-name argument can
# justify skipping it.
#
# Every scoped-out script is printed, with its reason and the size of the
# closure it was tested against, both up front and again in a block of its
# own at the end. This suite has a history of tests that looked like they ran
# and asserted nothing; a script that quietly did not run at all would be
# worse, because it would look like a pass.
#
# The safety net that makes this acceptable: the full unscoped suite still
# runs on every push to main and on every release (.github/workflows/tests.yml
# forces GATE_SCOPE=full there). Scoping applies to pull requests only, so a
# wrong closure turns main red within one gate instead of never.
#
# In lane mode each script's output is captured and replayed in full, one
# script at a time, after the lanes finish — interleaved output from four
# concurrent scripts is not something a human can read. Progress lines are
# printed live as scripts start and finish, so a long run still says what it
# is doing, and every script's wall-clock time is reported at the end.
set -u

cd "$(dirname "$0")/.."

# When an agent holds the gate lease, flock-wrap this run so a crash releases
# immediately (#404). The lease itself is renewed before every script below.
if [ -n "${HPO_GATE_LOCK_LABEL:-}" ] && [ "${HPO_GATE_FLOCK_CHILD:-}" != 1 ]; then
  PYTHON_WRAP="${PYTHON:-}"
  if [ -z "$PYTHON_WRAP" ]; then
    if [ -x .venv/bin/python ]; then PYTHON_WRAP=.venv/bin/python; else PYTHON_WRAP=python3; fi
  fi
  export HPO_GATE_FLOCK_CHILD=1
  exec "$PYTHON_WRAP" tests/gate_lock.py flock-wrap \
    --label "$HPO_GATE_LOCK_LABEL" -- "$0" "$@"
fi

PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
  if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=python3; fi
fi
export PYTHONPATH="$PWD/tests/hastub:${PYTHONPATH:-}"

GOLDEN_MODE="${GOLDEN_MODE:-strict}"
GOLDEN_REF="${GOLDEN_REF:-origin/main}"
# EXPORTED, not merely set (#341). tests/golden.py now reads both variables
# itself, and defaults to drift when nobody has decided -- because run
# directly it used to always strict-compare and report a fixed 34 of 55
# changed on a clean tree. Left unexported, the defaults resolved on the two
# lines above would stay inside this shell: a plain `./tests/run.sh` would
# choose strict here and hand golden.py an environment in which nobody had
# chosen anything, and the strict lane would silently run a drift comparison.
# The export is what makes the suite's decision the one that arrives.
export GOLDEN_MODE GOLDEN_REF

JOBS="${GATE_JOBS:-}"
if [ -z "$JOBS" ]; then
  if command -v nproc >/dev/null 2>&1; then JOBS=$(nproc); else JOBS=1; fi
  [ "$JOBS" -gt 3 ] && JOBS=3
fi
case "$JOBS" in (*[!0-9]*|"") JOBS=1 ;; esac
[ "$JOBS" -lt 1 ] && JOBS=1

WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/hpo-gate-XXXXXX")
trap 'rm -rf "$WORKDIR"' EXIT

# --- scoping ---------------------------------------------------------------
# Default full. The scoped path has to be asked for by name, and any doubt
# inside tests/closure.py comes back as a full run.
GATE_SCOPE="${GATE_SCOPE:-full}"
GATE_SCOPE_BASE="${GATE_SCOPE_BASE:-origin/main}"
SCOPE_RUN=""            # empty => no scoping, run everything
if [ "$GATE_SCOPE" = "auto" ]; then
  if "$PYTHON" tests/closure.py select --diff "$GATE_SCOPE_BASE" \
       --workdir "$WORKDIR" > "$WORKDIR/scope.stdout" 2>&1; then
    cat "$WORKDIR/scope.txt"
    if [ -s "$WORKDIR/scope.run" ]; then SCOPE_RUN="$WORKDIR/scope.run"; fi
  else
    echo
    echo "########## scoped gate ##########"
    echo "  MODE: FULL -- tests/closure.py could not produce a plan, so"
    echo "  nothing is scoped out. Its output:"
    sed 's/^/    /' "$WORKDIR/scope.stdout"
  fi
elif [ "$GATE_SCOPE" != "full" ]; then
  echo
  echo "########## scoped gate ##########"
  echo "  MODE: FULL -- GATE_SCOPE=$GATE_SCOPE is not a mode I know"
  echo "  (expected 'full' or 'auto'), so every script runs."
fi

# The script a `run` line is actually running, for the scope lookup: the
# first argument that names a file under tests/. Not the last argument --
# env_drift.py takes a ref after its script path.
scope_script() {
  local a
  for a in "$@"; do
    case "$a" in tests/*.py|tests/*.mjs) printf '%s' "$a"; return ;; esac
  done
}

# Is this script in the scoped run set? True when scoping is off.
in_scope() {
  [ -z "$SCOPE_RUN" ] && return 0
  local s
  s=$(scope_script "$@")
  [ -z "$s" ] && return 0          # not a test script line: never scope it out
  grep -Fxq "$s" "$SCOPE_RUN"
}

failed=0
LANE="${LANE:-main}"
step=0
suite_start=$(date +%s)

# Why a given script was scoped out, in the words tests/closure.py used.
scope_reason() {
  local line
  line=$(grep -F "$1	" "$WORKDIR/scope.skip" 2>/dev/null | head -1)
  if [ -z "$line" ]; then
    echo "not in the scoped run set"
  else
    printf 'no changed file is in its measured closure of %s file(s)' \
      "$(printf '%s' "$line" | cut -f2)"
  fi
}

# One test script. In lane mode its output goes to a file and is replayed
# later, in one piece; serially it streams, exactly as it always did. Either
# way the exit status and the wall-clock time land in the lane's manifest,
# which is what the parent adds up — a lane runs in a subshell, so a counter
# incremented in there would never come back.
run() {
  local scoped_out
  if [ -n "${HPO_GATE_LOCK_LABEL:-}" ]; then
    "$PYTHON" tests/gate_lock.py renew --label "$HPO_GATE_LOCK_LABEL"
  fi
  if ! in_scope "$@"; then
    scoped_out=$(scope_script "$@")
    skip "$scoped_out" \
      "SKIP: $scoped_out (scoped out: $(scope_reason "$scoped_out"))"
    return 0
  fi
  run_always "$@"
}

# Same as run, but GATE_SCOPE cannot skip it. Inherited claims and the
# record-PR empty rule live here: #493's roster-only three-dot left claim
# files unchanged, so in_scope skipped card_drift.mjs and env_drift.py, and
# main went red after squash.
run_always() {
  if [ -n "${HPO_GATE_LOCK_LABEL:-}" ]; then
    "$PYTHON" tests/gate_lock.py renew --label "$HPO_GATE_LOCK_LABEL"
  fi
  step=$((step + 1))
  local id started finished rc=0
  id=$(printf '%s-%03d' "$LANE" "$step")
  started=$(date +%s)
  if [ "$JOBS" -le 1 ]; then
    echo
    echo "########## $* ##########"
    "$@" || rc=$?
  else
    printf '  [%s] start  %s\n' "$(date +%H:%M:%S)" "$*"
    "$@" > "$WORKDIR/$id.log" 2>&1 || rc=$?
    finished=$(date +%s)
    printf '  [%s] %-6s %s (%ss)\n' \
      "$(date +%H:%M:%S)" "$([ "$rc" -eq 0 ] && echo ok || echo FAILED)" \
      "$*" "$((finished - started))"
  fi
  finished=$(date +%s)
  printf '%s\t%s\t%s\t%s\n' "$id" "$rc" "$((finished - started))" "$*" \
    >> "$WORKDIR/$LANE.manifest"
  if [ "$rc" -ne 0 ] && [ "$JOBS" -le 1 ]; then
    echo ">>> FAILED: $*"
  fi
}

# A script deliberately not run this time. It names the script it stands in
# for, because the accounting check below insists every test script either
# ran or was skipped on purpose — a lane function that never gets called
# would otherwise take its scripts down with it, silently, and the
# `run ... tests/<name>` grep above cannot see that: it only proves the line
# exists, not that anything executed it.
skip() {
  local script="$1"
  shift
  step=$((step + 1))
  local id
  id=$(printf '%s-%03d' "$LANE" "$step")
  printf '%s\n' "$*" > "$WORKDIR/$id.log"
  printf '%s\t0\t0\t#skip %s\n' "$id" "$script" >> "$WORKDIR/$LANE.manifest"
  [ "$JOBS" -le 1 ] && { echo; echo "$*"; }
  return 0
}

# Every test script must be wired into this file or deliberately allow-listed;
# a script added to tests/ and forgotten here would otherwise silently never
# run — which is exactly how optimality.py sat dormant for a year.
# "Wired" means an actual invocation line — `run ... tests/<name>` — not a
# mention in a comment or prose, which is how a bare-substring grep once
# counted four suites as wired when they were merely talked about. Splitting
# the suite into lanes moved those lines inside shell functions; they are
# still `run` invocations at the start of a line, so the same pattern finds
# them, and a script wired nowhere still fails here.
for f in tests/*.py tests/*.mjs; do
  base=$(basename "$f")
  case "$base" in
    harness.py|profiles.py) continue ;;  # shared plumbing, not tests
    # The shared DOM stub (#101) and the rig around it: imported by
    # card.mjs, setup_qa_render.mjs and card_drift.mjs, never run on
    # their own. node_fs_trace.mjs is the Darwin --import recorder.
    dom_stub.mjs|card_rig.mjs|node_fs_trace.mjs) continue ;;
    # The scoping instrument, not a test: it RUNS the tests to measure what
    # they touch. Wiring it into the suite would make the suite run itself.
    closure.py) continue ;;
    # Gate-lock helper (#404): agents invoke it directly; not a suite test.
    gate_lock.py) continue ;;
    # Run by features.py in a subprocess: HASTUB_TZ must be set before the
    # dt stub is imported, which an in-process import cannot arrange.
    dst_checks.py) continue ;;
    # The visual-QA renderer is WIRED into the card lane (v6.x, #101); no
    # exclusion here -- the UNWIRED check below must see it referenced.
    # The real-browser layout lane (issue #96): its own job in the
    # workflow installs Chromium for it, which this suite does not have.
    card_browser.mjs) continue ;;
    # The real-Home-Assistant lane (#521): its own nightly job pulls the
    # container image and runs the integration inside it. Docker is not
    # available to this suite, and it must never gate a pull request.
    nightly_ha.py) continue ;;
    # The nightly's reporter (#533): the `nightly-status` job runs it on every
    # pull request. It reads the GitHub Actions API, which this suite has no
    # network and no token for, and its verdict is about CI's history rather
    # than about this tree. tests/entities.py drives its classifier instead.
    nightly_status.py) continue ;;
    # The disposition gate's reporter (#678): the `record-status` job runs it
    # on every pull request. It reads the GitHub Checks API, which this suite
    # has no network and no token for, and its verdict is about `main`'s CI
    # history rather than about this tree. tests/entities.py drives its
    # classifier instead.
    record_status.py) continue ;;
  esac
  if ! grep -Eq '^[[:space:]]*run .*tests/'"$base"'( |$)' tests/run.sh; then
    echo "UNWIRED TEST: tests/$base is not referenced by tests/run.sh"
    failed=$((failed + 1))
  fi
done

# --- the lanes -------------------------------------------------------------

# Unit-style checks: fast, and a failure here explains any end-to-end failure
# that follows. Kept together and reported first for exactly that reason.
lane_units() {
  # Not a capture. Claim files unchanged => in_scope skips env_drift.py and
  # card_drift.mjs (#493); this line cannot be scoped out.
  run_always "$PYTHON" tests/env_drift.py --claims-only "$GOLDEN_REF"
  # #527: a full merge used to shrink card_drift.mjs 66→6, and a partial
  # merge aborted every sibling at the first shrink. Cheap, no recording.
  run_always "$PYTHON" tests/closure.py selftest
  run "$PYTHON" tests/features.py
  run "$PYTHON" tests/entities.py
  # The initial config flow walked end to end (#194): every step's valid
  # and invalid submissions, the duplicate abort and the reauth round
  # trip, against the real validation code over the fake Tibber session.
  run "$PYTHON" tests/config_flow_steps.py
  # The structural ratchet of the coordinator decomposition program (#193,
  # PR-0): AST counts -- god classes, monster methods, attr bags, seam cut
  # costs -- over the whole integration, each held at or below the budget
  # table in tests/structure_budgets.json. Pure counts, no runtime, no
  # timing guard. It reads every integration module, so its measured
  # closure is the whole integration; that is correct and deliberate: any
  # structural change puts this lane in scope.
  run "$PYTHON" tests/structure.py
  # The typing ratchet's dependency-free half (#303). The error count and its
  # per-code split need the pinned mypy/homeassistant-stubs pair, which no
  # gate lane has, so the `typing` CI job owns those; the `# type: ignore`
  # count is a source scan and belongs where it runs on every pull request.
  # That is the guard `--warn-unused-ignores` does NOT provide -- a live
  # ignore is a used ignore -- so it must not be the half that goes unchecked
  # whenever a toolchain install fails.
  run "$PYTHON" tests/typing_ruler.py
  # What tests/hastub owes Home Assistant (#536). Every lane here runs against
  # the stub, so a green test proves the code works against the STUB's
  # behaviour; this is the file that says what that behaviour is supposed to
  # be, and the nightly-ha job runs the same file against the real package.
  run "$PYTHON" tests/ha_contract.py
  run "$PYTHON" tests/manual_plan.py
  run "$PYTHON" tests/open_meteo.py
  run "$PYTHON" tests/solar_alignment.py
  # The only lane that runs the shape an installation runs (#513): the tracked
  # package alone, no tests/ sibling, imported as
  # custom_components.heatpump_optimizer.*. Every other script in this
  # directory runs the checkout shape, which is how #511 -- every solve
  # failing, on every install -- shipped green. It spawns its own
  # interpreters and never imports the integration into this one.
  run "$PYTHON" tests/deployment_shape.py
}

# The characterization harness: exact behaviour, pinned. Its own lane because
# it is the longest single step in the suite — in drift mode it captures every
# scenario twice — and nothing else depends on it.
lane_golden() {
  if [ "$GOLDEN_MODE" = "drift" ]; then
    # Drift mode replaces the exact comparison entirely; golden.py's
    # fixtures were recorded on another machine and comparing this one's
    # floats against them would cry wolf. Said out loud rather than left
    # as a gap: the accounting below wants every script accounted for.
    skip tests/golden.py "SKIP: tests/golden.py (GOLDEN_MODE=drift checks fixtures via env_drift.py instead)"
    run "$PYTHON" tests/env_drift.py --all "$GOLDEN_REF"
  else
    run "$PYTHON" tests/golden.py
    # The five machine-sensitive fixtures get their real check here: identical
    # to GOLDEN_REF when captured twice in THIS environment (G4b). Skipped
    # when the ref is unreachable (tarball checkouts, offline clones).
    if ! git rev-parse --verify --quiet "${GOLDEN_REF}^{commit}" >/dev/null 2>&1; then
      skip tests/env_drift.py "SKIP: tests/env_drift.py ($GOLDEN_REF is not available here)"
    elif [ "$(git rev-parse "${GOLDEN_REF}^{commit}")" = "$(git rev-parse HEAD)" ]; then
      # A checkout sitting on the comparison ref itself: comparing a tree to
      # itself proves nothing, so there is nothing to run. env_drift fails on
      # this rather than passing vacuously; here it is just where a developer
      # on an up-to-date main lands, so say so and carry on.
      skip tests/env_drift.py "SKIP: tests/env_drift.py ($GOLDEN_REF is this commit; use GOLDEN_REF=HEAD^1 to check it)"
    else
      run "$PYTHON" tests/env_drift.py "$GOLDEN_REF"
    fi
  fi
}

# End-to-end optimizer behaviour, then the plan payloads, the card that
# renders them and how it reaches the page. plan_view.py writes what card.mjs
# reads, so this lane is sequential and that pair keeps its order.
lane_e2e() {
  run "$PYTHON" tests/validate.py
  run "$PYTHON" tests/edge.py
  run "$PYTHON" tests/backtest.py
  run "$PYTHON" tests/optimality.py

  # The closed-loop simulation runs hundreds of solves and takes about a
  # quarter of an hour, so it is opt-in: a test that slow would simply stop
  # being run if it sat in the default path. Run it before a release, or
  # after touching the optimizer or the learners.
  if [ "${SLOW:-0}" = "1" ]; then
    run "$PYTHON" tests/rolling.py
  else
    skip tests/rolling.py "SKIP: tests/rolling.py (set SLOW=1 to include the closed-loop simulation)"
  fi

  run "$PYTHON" tests/plan_view.py
  run "$PYTHON" tests/frontend.py
  if command -v node >/dev/null 2>&1; then
    run node tests/card.mjs
    # The visual-QA renderer rides the same lane as the card test: it reads
    # the payload plan_view.py just wrote (same ordering constraint as
    # card.mjs) and fails if any topology's setup svg comes out empty, so a
    # dormant renderer can no longer drift unnoticed (#101). Its SVGs land
    # in ../setup-qa/ for designer review.
    run node tests/setup_qa_render.mjs
    # The card's markup gate: the working tree's card and GOLDEN_REF's,
    # rendered through the same states in one process, must agree byte
    # for byte unless tests/golden/card_claimed_drift.txt claims the
    # moved states. Same three-way ref logic as lane_golden's env_drift
    # step, for the same reasons.
    if ! git rev-parse --verify --quiet "${GOLDEN_REF}^{commit}" >/dev/null 2>&1; then
      skip tests/card_drift.mjs "SKIP: tests/card_drift.mjs ($GOLDEN_REF is not available here)"
    elif [ "$(git rev-parse "${GOLDEN_REF}^{commit}")" = "$(git rev-parse HEAD)" ]; then
      skip tests/card_drift.mjs "SKIP: tests/card_drift.mjs ($GOLDEN_REF is this commit; use GOLDEN_REF=HEAD^1 to check it)"
    else
      run node tests/card_drift.mjs "$GOLDEN_REF"
    fi
  else
    skip tests/card.mjs "SKIP: node not found, skipping tests/card.mjs"
    skip tests/setup_qa_render.mjs "SKIP: node not found, skipping tests/setup_qa_render.mjs"
    skip tests/card_drift.mjs "SKIP: node not found, skipping tests/card_drift.mjs"
  fi
}

# Alone, on an idle box, after everything else. See the header: its
# solve-time guard calibrates against this machine while it runs, and the
# rest of the suite must not be part of what it measures.
lane_stress() {
  run "$PYTHON" tests/stress.py
}

LANES="units golden e2e"

if [ "$JOBS" -le 1 ]; then
  for lane in $LANES stress; do
    LANE="$lane" step=0
    "lane_$lane"
    : > "$WORKDIR/$lane.done"
  done
else
  echo
  echo "########## $JOBS lanes in parallel: $LANES ##########"
  pids=""
  for lane in $LANES; do
    # `trap - EXIT` so a finishing lane cannot delete the report
    # directory the parent is still filling. The .done marker is written
    # last: a lane killed part-way through (OOM, a signal) leaves no marker
    # and the accounting below fails the run rather than reporting the
    # scripts it did manage as the whole story.
    ( trap - EXIT; LANE="$lane"; step=0; "lane_$lane"; : > "$WORKDIR/$lane.done" ) &
    pids="$pids $!"
  done
  for pid in $pids; do wait "$pid"; done
  echo
  echo "########## alone on the box: stress ##########"
  ( trap - EXIT; LANE="stress"; step=0; lane_stress; : > "$WORKDIR/stress.done" ) &
  wait $!
fi

# --- accounting: every lane finished, every test script is accounted for ---
for lane in $LANES stress; do
  if [ ! -f "$WORKDIR/$lane.done" ]; then
    echo "LANE DID NOT FINISH: $lane stopped before its last script"
    failed=$((failed + 1))
  fi
done

# The grep above proves a `run` line exists; this proves it ran. A lane
# function left out of $LANES, or a script wired into a function nothing
# calls, passes the first check and fails this one.
for f in tests/*.py tests/*.mjs; do
  base=$(basename "$f")
  case "$base" in
    harness.py|profiles.py|dst_checks.py|closure.py|gate_lock.py|dom_stub.mjs|card_rig.mjs|card_browser.mjs|node_fs_trace.mjs|nightly_ha.py|nightly_status.py|record_status.py) continue ;;
  esac
  if ! cat "$WORKDIR"/*.manifest 2>/dev/null | grep -Fq "tests/$base"; then
    echo "TEST NEVER RAN: tests/$base is wired into tests/run.sh but no lane"
    echo "  executed it and no lane skipped it on purpose."
    failed=$((failed + 1))
  fi
done

# --- the report ------------------------------------------------------------

if [ "$JOBS" -gt 1 ]; then
  for lane in $LANES stress; do
    [ -f "$WORKDIR/$lane.manifest" ] || continue
    while IFS=$'\t' read -r id rc seconds label; do
      echo
      case "$label" in
        "#skip "*) cat "$WORKDIR/$id.log"; continue ;;
      esac
      echo "########## $label ##########"
      cat "$WORKDIR/$id.log"
      [ "$rc" -ne 0 ] && echo ">>> FAILED: $label"
    done < "$WORKDIR/$lane.manifest"
  done
fi

echo
echo "########## wall clock ##########"
ran=0
for lane in $LANES stress; do
  [ -f "$WORKDIR/$lane.manifest" ] || continue
  while IFS=$'\t' read -r id rc seconds label; do
    case "$label" in
      "#skip "*) continue ;;
    esac
    printf '  %6ss  %s\n' "$seconds" "$label"
    ran=$((ran + 1))
    [ "$rc" -ne 0 ] && failed=$((failed + 1))
  done < "$WORKDIR/$lane.manifest"
  # `ran` is incremented inside a `while` fed by a redirect, which bash runs
  # in this shell -- not a pipeline subshell -- so the count survives. Said
  # here because the same loop shape one line up in a pipeline would not.
done
printf '  %6ss  TOTAL (%s lane(s))\n' "$(( $(date +%s) - suite_start ))" "$JOBS"

# --- what did NOT run ------------------------------------------------------
# Said twice, on purpose. A scoped gate that is quiet about what it dropped
# is indistinguishable from a gate that passed, and this codebase already has
# six known instances of a test that looked like it ran and asserted nothing.
if [ -n "$SCOPE_RUN" ]; then
  echo
  echo "########## NOT RUN: scoped out of this gate ##########"
  if [ -s "$WORKDIR/scope.skip" ]; then
    while IFS=$'\t' read -r script size reason; do
      [ -z "$script" ] && continue
      printf '  %-24s did NOT run -- %s (closure: %s files)\n' \
        "$script" "$reason" "$size"
    done < "$WORKDIR/scope.skip"
  else
    echo "  (nothing -- every script was in scope)"
  fi
  echo
  echo "  Each line above is a claim that no file changed by this branch is in"
  echo "  that script's MEASURED closure (tests/closures.json, recorded by"
  echo "  tests/derive_closures.sh from real instrumented runs). The claim is"
  echo "  re-checked in full: every push to main runs this suite unscoped, so"
  echo "  a closure that is wrong turns main red within one gate."
  echo "  Run everything here and now with: GATE_SCOPE=full ./tests/run.sh"
fi

echo
if [ "$failed" -ne 0 ]; then
  echo "$failed TEST SCRIPT(S) FAILED"
  exit 1
fi
# A scoped run whose scope came out empty -- a documentation-only change, say
# -- is a legitimate pass, but "ALL TEST SCRIPTS PASSED" is the wrong thing to
# print when none of them ran. Say what actually happened.
if [ "$ran" -eq 0 ]; then
  echo "NO TEST SCRIPT RAN: every script was scoped out of this gate."
  echo "Nothing was verified here. The full suite runs unscoped on main."
  echo "To check this change against the whole suite: GATE_SCOPE=full ./tests/run.sh"
  exit 0
fi
if [ -n "$SCOPE_RUN" ]; then
  scoped_out_count=$(grep -c . "$WORKDIR/scope.skip" 2>/dev/null || true)
  echo "$ran TEST SCRIPT(S) PASSED; ${scoped_out_count:-0} SCOPED OUT AND NOT RUN"
  echo "(see the NOT RUN block above -- this is not a full gate)"
  exit 0
fi
echo "ALL TEST SCRIPTS PASSED"
