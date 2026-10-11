#!/bin/bash
# The merge-train launcher: one invocation shape for `merge_train.py batch`.
#
#   tools/audit/seat/train.sh --queue Q.json --repo OWNER/REPO --state-dir DIR \
#                             [--checkout DIR] [--min-runs N] [--mandate ID] \
#                             [--ignore-red CONTEXT]... [--self-test]
#
# What it adds over calling merge_train.py by hand, which the orchestrator's
# scratch re-duplicated once per session before this existed:
#   * the seat venv (seat_venv.sh's venv-ci, the pinned 3.14) first on PATH --
#     prepr's no-copies and the f-string checks refuse on an ambient 3.11;
#   * a pidfile per state dir refusing a second live train on the same state
#     (two concurrent trains on one state dir have corrupted a queue mid-run);
#   * the log and the exit code under the state dir (train.log, rc), so a
#     detached caller and the next session read the same places.
# Foreground by design: the caller detaches (`nohup ... &`) and owns the
# schedule; this script owns only the invocation shape.

set -u

die() { echo "train.sh: REFUSE: $*" >&2; exit 2; }

usage() { sed -n '2,12p' "$0" >&2; exit 2; }

selftest=0
queue="" repo="" checkout="" state="" minruns=1 mandate=""
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
      ignores=("${ignores[@]:-}" --ignore-red "$2"); shift 2 ;;
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
  echo "train.sh self-test: ok (3 refusals shown)"
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
trap 'rm -f "$pidfile"' EXIT

# The pinned seat interpreter first: the checks merge_train drives through
# prepr and no-copies need the repo's 3.14, not an ambient 3.11.
_HPO_STATE=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
if [ -d "$_HPO_STATE/venv-ci/bin" ]; then
  PATH=$_HPO_STATE/venv-ci/bin:$PATH
  export PATH
fi
unset _HPO_STATE

if [ -z "$checkout" ]; then
  checkout=$(cd "$(dirname "$0")/../.." && pwd)
fi
[ -d "$checkout" ] || die "checkout directory not found: $checkout"

log=$state/train.log
echo "train.sh: queue=$queue repo=$repo state=$state pid=$$ start=$(date -u +%FT%TZ)" >> "$log"
(
  cd "$checkout" || exit 2
  # shellcheck disable=SC2086 # minruns is a plain integer
  python3 tools/audit/seat/merge_train.py batch "$queue" \
    --repo "$repo" \
    --state-dir "$state" \
    --min-runs "$minruns" \
    ${ignores[@]+"${ignores[@]}"} \
    ${mandate:+--mandate "$mandate"}
) >> "$log" 2>&1
rc=$?
echo "TRAIN_RC=$rc end=$(date -u +%FT%TZ)" >> "$log"
echo "$rc" > "$state/rc"
exit "$rc"
