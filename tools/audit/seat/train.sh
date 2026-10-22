#!/bin/bash
# The merge-train launcher: one invocation shape for `merge_train.py batch`.
#
#   tools/audit/seat/train.sh --queue Q.json --repo OWNER/REPO --state-dir DIR \
#                             [--checkout DIR] [--min-runs N] [--mandate ID] \
#                             [--ignore-red CONTEXT]... [--skip-bad] [--overlap] \
#                             [--approval-carry] [--bot-prs] [--pre-flight] \
#                             [--free-holders] [--main-moved-tries N] [--self-test]
#
# What it adds over calling merge_train.py by hand, which the orchestrator's
# scratch re-duplicated once per session before this existed:
#   * the seat venv (seat_venv.sh's venv-ci, the pinned 3.14) first on PATH --
#     prepr's no-copies and the f-string checks refuse on an ambient 3.11;
#   * the child python runs UNBUFFERED (`python3 -u`): a detached caller's log
#     shows a train stop, a SKIP line or an OVERLAP recarry in real time, not
#     after a block buffer fills;
#   * a pidfile per state dir refusing a second live train on the same state
#     (two concurrent trains on one state dir have corrupted a queue mid-run);
#   * the log and the exit code under the state dir (train.log, rc), so a
#     detached caller and the next session read the same places.
# `--skip-bad` and `--overlap` pass straight through to `merge_train.py batch`:
# a bad entry is skipped and reported instead of stopping the train, and the
# serial entries are re-carried up front with main's CI waited on log-only.
# So do `--approval-carry`, `--bot-prs`, `--pre-flight`, `--free-holders` and
# `--main-moved-tries N` (merge_train.py's own help states each). Without
# --checkout the child runs from the repository root this script sits in.
# Foreground by design: the caller detaches (`nohup ... &`) and owns the
# schedule; this script owns only the invocation shape.

set -u

die() { echo "train.sh: REFUSE: $*" >&2; exit 2; }

usage() { sed -n '2,16p' "$0" >&2; exit 2; }

selftest=0
queue="" repo="" checkout="" state="" minruns=1 mandate=""
skipbad="" overlap="" opts=()
ignores=()
while [ $# -gt 0 ]; do
  case $1 in
    --queue) [ $# -ge 2 ] || die "--queue needs a value"; queue=$2; shift 2 ;;
    --repo) [ $# -ge 2 ] || die "--repo needs a value"; repo=$2; shift 2 ;;
    --state-dir) [ $# -ge 2 ] || die "--state-dir needs a value"; state=$2; shift 2 ;;
    --checkout) [ $# -ge 2 ] || die "--checkout needs a value"; checkout=$2; shift 2 ;;
    --min-runs) [ $# -ge 2 ] || die "--min-runs needs a value"; minruns=$2; shift 2 ;;
    --mandate) [ $# -ge 2 ] || die "--mandate needs a value"; mandate=$2; shift 2 ;;
    --ignore-red) [ $# -ge 2 ] || die "--ignore-red needs a value"
      ignores+=("--ignore-red" "$2"); shift 2 ;;
    --skip-bad) skipbad=1; shift ;;
    --overlap) overlap=1; shift ;;
    --approval-carry|--bot-prs|--pre-flight|--free-holders) opts+=("$1"); shift ;;
    --main-moved-tries) [ $# -ge 2 ] || die "--main-moved-tries needs a value"
      opts+=("$1" "$2"); shift 2 ;;
    --self-test) selftest=1; shift ;;
    --help|-h) usage ;;
    *) die "unknown argument '$1'" ;;
  esac
done

if [ "$selftest" = 1 ]; then
  # 1. missing required arguments refuse.
  for miss in "--repo x" "--state-dir x"; do
    if "$0" --queue /dev/null $miss >/dev/null 2>&1; then
      die "self-test: '$miss' alone did not refuse"
    fi
  done
  # 2. a live pidfile refuses a second train on the same state dir.
  st=$(mktemp -d)
  echo $$ > "$st/train.pid"
  if "$0" --queue /dev/null --repo x/r --state-dir "$st" >/dev/null 2>&1; then
    rm -rf "$st"
    die "self-test: a live pidfile did not refuse"
  fi
  rm -rf "$st"
  # 3. an unknown argument refuses.
  if "$0" --frobnicate >/dev/null 2>&1; then
    die "self-test: an unknown argument did not refuse"
  fi
  # 4. --ignore-red must reach the child with no stray empty element (a
  #    bash-3.2 `${arr[@]:-}` guard put one there; argparse then refused the
  #    stray positional before the flags were ever read). A stub venv-ci
  #    python3 records the argv it receives; the assertion is on that record,
  #    not on which refusal text came back -- the queue check fires before
  #    the child runs, so a refusal-text observable cannot see the bug.
  st=$(mktemp -d)
  mkdir -p "$st/venv-ci/bin" "$st/state"
  printf '#!/bin/bash\nfor a in "$@"; do printf "%%s\\n" "$a" >> "%s/argv"; done\nexit 0\n' "$st" \
    > "$st/venv-ci/bin/python3"
  chmod +x "$st/venv-ci/bin/python3"
  : > "$st/queue.json"
  if ! HPO_STATE_DIR="$st" "$0" --queue "$st/queue.json" --repo x/r \
      --state-dir "$st/state" --ignore-red ctx >/dev/null 2>&1; then
    rm -rf "$st"
    die "self-test: the stubbed --ignore-red run did not succeed"
  fi
  if [ ! -s "$st/argv" ]; then
    rm -rf "$st"
    die "self-test: the stubbed python3 never ran (ambient fallback?)"
  fi
  # adjacency: the element after --ignore-red must be ctx, and no element
  # anywhere in the argv may be empty (a stray empty element IS the bug).
  flags=$(tr '\n' '|' < "$st/argv")
  case $flags in
    *"--min-runs|1|--ignore-red|ctx|"*) : ;;
    *)
      rm -rf "$st"
      die "self-test: --ignore-red argv shape wrong: $flags"
      ;;
  esac
  if [ "$(grep -c '^$' "$st/argv")" -gt 0 ]; then
    rm -rf "$st"
    die "self-test: an empty element reached the child argv"
  fi
  rm -rf "$st"
  # 5. an absent seat venv refuses with the build instruction -- the tool
  #    exists to stop an ambient-python3 train, so the fallback is a defect.
  st=$(mktemp -d)
  : > "$st/q"
  out=$(HPO_STATE_DIR="$st" "$0" --queue "$st/q" --repo x/r \
    --state-dir "$st/s" 2>&1)
  rc=$?
  rm -rf "$st"
  [ "$rc" = 2 ] || die "self-test: an absent venv did not refuse (rc=$rc)"
  case $out in
    *seat_venv.sh*) : ;;
    *) die "self-test: an absent venv refused without naming seat_venv.sh: $out" ;;
  esac
  # 6. --skip-bad and --overlap pass through to merge_train.py, and the child
  #    python runs unbuffered (-u): a detached caller's log shows a SKIP
  #    report or an OVERLAP recarry in real time, not after a buffer fills.
  #    Same stub-argv technique as arm 4.
  st=$(mktemp -d)
  mkdir -p "$st/venv-ci/bin" "$st/state"
  printf '#!/bin/bash\nfor a in "$@"; do printf "%%s\\n" "$a" >> "%s/argv"; done\nexit 0\n' "$st" \
    > "$st/venv-ci/bin/python3"
  chmod +x "$st/venv-ci/bin/python3"
  : > "$st/queue.json"
  if ! HPO_STATE_DIR="$st" "$0" --queue "$st/queue.json" --repo x/r \
      --state-dir "$st/state" --skip-bad --overlap >/dev/null 2>&1; then
    rm -rf "$st"
    die "self-test: the stubbed --skip-bad/--overlap run did not succeed"
  fi
  [ -s "$st/argv" ] || { rm -rf "$st"; die "self-test: the stubbed python3 never ran (ambient fallback?)"; }
  flags=$(tr '\n' '|' < "$st/argv")
  case $flags in
    "-u|tools/audit/seat/merge_train.py|batch|"*) : ;;
    *) rm -rf "$st"; die "self-test: the child is not run unbuffered (-u first): $flags" ;;
  esac
  case $flags in
    *"|--skip-bad|--overlap|"*) : ;;
    *) rm -rf "$st"; die "self-test: --skip-bad/--overlap did not reach the child argv: $flags" ;;
  esac
  rm -rf "$st"
  # 7. launched WITHOUT --checkout, the child runs from the REPOSITORY ROOT,
  #    where tools/audit/seat/merge_train.py is (R10-TICK-TRAIN: the default
  #    resolved to tools/, and every launch without --checkout died with
  #    "can't open file '<repo>/tools/tools/audit/seat/merge_train.py'" --
  #    arm 4's stub records argv only, so it never saw the cwd). The stub
  #    records its cwd; the new options reach the child too.
  st=$(mktemp -d)
  mkdir -p "$st/venv-ci/bin" "$st/state"
  printf '#!/bin/bash\npwd > "%s/cwd"\nfor a in "$@"; do printf "%%s\\n" "$a" >> "%s/argv"; done\nexit 0\n' "$st" "$st" \
    > "$st/venv-ci/bin/python3"
  chmod +x "$st/venv-ci/bin/python3"
  : > "$st/queue.json"
  HPO_STATE_DIR="$st" "$0" --queue "$st/queue.json" --repo x/r --state-dir "$st/state" \
    --approval-carry --bot-prs --pre-flight --free-holders --main-moved-tries 2 >/dev/null 2>&1
  top=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
  ran=$(cat "$st/cwd" 2>/dev/null)
  [ -n "$ran" ] && [ "$(cd "$ran" && pwd -P)" = "$(cd "$top" && pwd -P)" ] \
    && [ -f "$ran/tools/audit/seat/merge_train.py" ] \
    || { rm -rf "$st"; die "self-test: launched without --checkout the child ran in '$ran', not the repository root $top"; }
  flags=$(tr '\n' '|' < "$st/argv")
  case $flags in
    *"|--approval-carry|--bot-prs|--pre-flight|--free-holders|--main-moved-tries|2|"*) : ;;
    *) rm -rf "$st"; die "self-test: the train options did not reach the child argv: $flags" ;;
  esac
  rm -rf "$st"
  # 8. a flag NOT given never reaches the child: `${skipbad:+--skip-bad}`
  #    over a default of 0 (non-empty) passed --skip-bad and --overlap on
  #    EVERY launch (measured at origin/main 613b10c51). The bare launch's
  #    argv must end at --min-runs 1.
  st=$(mktemp -d)
  mkdir -p "$st/venv-ci/bin" "$st/state"
  printf '#!/bin/bash\nfor a in "$@"; do printf "%%s\\n" "$a" >> "%s/argv"; done\nexit 0\n' "$st" \
    > "$st/venv-ci/bin/python3"
  chmod +x "$st/venv-ci/bin/python3"
  : > "$st/queue.json"
  HPO_STATE_DIR="$st" "$0" --queue "$st/queue.json" --repo x/r --state-dir "$st/state" >/dev/null 2>&1
  flags=$(tr '\n' '|' < "$st/argv" 2>/dev/null)
  rm -rf "$st"
  case $flags in
    *"|--min-runs|1|") : ;;
    *) die "self-test: a bare launch passed flags it was not given: $flags" ;;
  esac
  # 9. a stopped train ends its whole tree (R10-PUSHER-REAP): TERM or HUP to the pid
  #    in train.pid reaches the merge_train.py child, the tree under it is reaped,
  #    and the pidfile goes only once that tree is gone -- a pidfile removed while
  #    the train still runs lets a second train start on the same state dir. The
  #    child is a stub running a two-level tree (5 pids, the review's harness);
  #    the seat venv's python3 is the ambient one. "early": the pidfile was gone
  #    while a pid of the tree was still alive.
  for sig in TERM HUP; do
    st=$(mktemp -d)
    mkdir -p "$st/venv-ci/bin" "$st/state" "$st/C/tools/audit/seat"
    ln -s "$(command -v python3)" "$st/venv-ci/bin/python3"
    printf '#!/bin/bash\necho $$ >> "%s/pids"\nbash -c '"'"'sleep 30; :'"'"' & echo $! >> "%s/pids"\nbash -c '"'"'sleep 30 & echo $! >> "$0"; wait'"'"' "%s/pids" & echo $! >> "%s/pids"\nwait\n' \
      "$st" "$st" "$st" "$st" > "$st/tree.sh"
    printf 'import os, subprocess\nopen("%s", "a").write("%%d\\n" %% os.getpid())\nsubprocess.Popen(["bash", "%s"]).wait()\n' \
      "$st/pids" "$st/tree.sh" > "$st/C/tools/audit/seat/merge_train.py"
    : > "$st/queue.json"; : > "$st/pids"
    HPO_STATE_DIR="$st" "$0" --queue "$st/queue.json" --repo x/r --state-dir "$st/state" --checkout "$st/C" >/dev/null 2>&1 &
    lp=$!; k=0
    while [ "$(wc -l < "$st/pids")" -lt 5 ] && [ $k -lt 200 ]; do sleep 0.05; k=$((k + 1)); done
    tn=$(wc -l < "$st/pids" | tr -d ' '); held=$(cat "$st/state/train.pid" 2>/dev/null)
    tlive() { live=0; for p in $(cat "$st/pids"); do
      kill -0 "$p" 2>/dev/null && [ "$(ps -o stat= -p "$p" | cut -c1)" != Z ] && live=$((live + 1)); done; }
    kill -"$sig" "$held" 2>/dev/null; early=none; k=0
    while [ $k -lt 100 ]; do
      [ -f "$st/state/train.pid" ] && pf=1 || pf=0
      tlive
      [ "$pf" = 0 ] && [ "$live" -gt 0 ] && early=early
      [ "$pf" = 0 ] && [ "$live" = 0 ] && ! kill -0 "$lp" 2>/dev/null && break
      sleep 0.05; k=$((k + 1))
    done 2>/dev/null  # the shell reports the launcher's signal death here
    { wait "$lp"; } 2>/dev/null; tlive
    for p in $(cat "$st/pids"); do kill -KILL "$p" 2>/dev/null; done
    pf=$([ -f "$st/state/train.pid" ] && echo present || echo removed)
    rm -rf "$st"
    [ "$tn $held $live $pf $early" = "5 $lp 0 removed none" ] \
      || die "self-test: $sig to the train (pid $held, launcher $lp) left $live of $tn pids of its tree alive (pidfile $pf, $early)"
  done
  # 10. merge_train.py stops first, as the reap's lead: its own stop TERMs the tool it
  #     runs and releases the train's hold, which a TERM to the whole tree at once
  #     would cut short. The stub's child G marks a TERM it gets; the stub, TERMed,
  #     waits 0.5 s, writes "early" when G was TERMed beside it, then ends G.
  st=$(mktemp -d)
  mkdir -p "$st/venv-ci/bin" "$st/state" "$st/C/tools/audit/seat"
  ln -s "$(command -v python3)" "$st/venv-ci/bin/python3"
  printf 'import os, signal, subprocess, sys, time\nopen("%s/pids", "a").write("%%d\\n" %% os.getpid())\ng = subprocess.Popen(["bash", "-c", "trap \\"echo G >> %s/marks; exit 0\\" TERM; while :; do sleep 0.1; done"])\nopen("%s/pids", "a").write("%%d\\n" %% g.pid)\ndef stop(*_):\n    time.sleep(0.5)\n    if "G" in open("%s/marks").read(): open("%s/marks", "a").write("early\\n")\n    g.terminate(); g.wait(); sys.exit(143)\nsignal.signal(signal.SIGTERM, stop)\nwhile True: time.sleep(0.1)\n' \
    "$st" "$st" "$st" "$st" "$st" > "$st/C/tools/audit/seat/merge_train.py"
  : > "$st/queue.json"; : > "$st/pids"; : > "$st/marks"
  HPO_STATE_DIR="$st" "$0" --queue "$st/queue.json" --repo x/r --state-dir "$st/state" --checkout "$st/C" >/dev/null 2>&1 &
  lp=$!; k=0
  while [ "$(wc -l < "$st/pids")" -lt 2 ] && [ $k -lt 200 ]; do sleep 0.05; k=$((k + 1)); done
  kill -TERM "$(cat "$st/state/train.pid" 2>/dev/null)" 2>/dev/null
  { wait "$lp"; } 2>/dev/null
  tlive
  for p in $(cat "$st/pids"); do kill -KILL "$p" 2>/dev/null; done
  marks=$(tr '\n' ' ' < "$st/marks"); pf=$([ -f "$st/state/train.pid" ] && echo present || echo removed)
  rm -rf "$st"
  [ "$live $marks$pf" = "0 G removed" ] \
    || die "self-test: a TERMed train did not stop merge_train.py first (alive $live, marks '$marks', pidfile $pf)"
  echo "train.sh self-test: ok (5 refusals shown, root and options reach the child, no unasked flag, a stop reaps the tree, merge_train.py first)"
  exit 0
fi

[ -n "$queue" ] || usage
[ -n "$repo" ] || usage
[ -n "$state" ] || usage
[ -f "$queue" ] || die "queue file not found: $queue"

mkdir -p "$state" || die "cannot create state dir $state"
pidfile=$state/train.pid
if [ -f "$pidfile" ]; then
  held=$(cat "$pidfile" 2>/dev/null || true)
  [ -n "$held" ] && kill -0 "$held" 2>/dev/null &&
    die "a live train holds $pidfile (pid $held); one train per state dir"
  echo "train.sh: stale pidfile ($held), taking over" >&2
fi
echo $$ > "$pidfile"
# A stopped train ends its whole tree, and frees the state dir only after
# (R10-PUSHER-REAP): pr_args.sh's EXIT trap runs when TERM, INT or HUP end this
# shell, TERMs merge_train.py first as the lead -- its own stop TERMs the tool it
# runs and releases the train's hold -- then reaps whatever is left, and only
# then removes the pidfile. A bare `rm` trap removed it at once, while the
# child, which no signal reached, went on pushing.
. "$(dirname -- "$0")/pr_args.sh"
PR_AFTER_REAP='rm -f "$pidfile"'
pr_exit_trap

# The pinned seat interpreter first: the checks merge_train drives through
# prepr and no-copies need the repo's 3.14, not an ambient 3.11. There is no
# ambient fallback: this launcher exists to keep the train off the ambient
# interpreter, so an absent venv refuses rather than silently running.
_HPO_STATE=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
if [ -f "$_HPO_STATE/venv-ci/bin/python3" ]; then
  PATH=$_HPO_STATE/venv-ci/bin:$PATH
  export PATH
else
  die "no seat venv at $_HPO_STATE/venv-ci/bin/python3; build it first: bash tools/audit/seat/seat_venv.sh venv-ci"
fi
unset _HPO_STATE

if [ -z "$checkout" ]; then
  # This script is tools/audit/seat/train.sh: the root is three levels up
  # (two named tools/, and every launch without --checkout died there).
  checkout=$(git -C "$(dirname "$0")" rev-parse --show-toplevel) || die "no repository around $0; pass --checkout"
fi
[ -d "$checkout" ] || die "checkout directory not found: $checkout"

log=$state/train.log
echo "train.sh: queue=$queue repo=$repo state=$state pid=$$ start=$(date -u +%FT%TZ)" >> "$log"
(
  cd "$checkout" || exit 2
  # shellcheck disable=SC2086 # minruns is a plain integer
  exec python3 -u tools/audit/seat/merge_train.py batch "$queue" \
    --repo "$repo" \
    --state-dir "$state" \
    --min-runs "$minruns" \
    ${ignores[@]+"${ignores[@]}"} \
    ${skipbad:+--skip-bad} \
    ${overlap:+--overlap} \
    ${mandate:+--mandate "$mandate"} \
    ${opts[@]+"${opts[@]}"}
) >> "$log" 2>&1 &
# Asynchronous, then `wait`: a stop signal interrupts the wait, where it would
# wait behind a foreground child. The exec makes this pid merge_train.py itself.
PR_REAP_LEAD=$!
rc=0; wait "$PR_REAP_LEAD" || rc=$?
echo "TRAIN_RC=$rc end=$(date -u +%FT%TZ)" >> "$log"
echo "$rc" > "$state/rc"
exit "$rc"
