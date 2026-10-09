#!/usr/bin/env bash
# The throwaway-repository race (R9-RCA-stamp-race) at the sites the shared
# helper (tests/throwaway_git.py, tests/throwaway_git.sh) now covers, on a REAL
# git >= 2.54 with the repack forced -- no model. A sibling of
# git_auto_maintenance_race.sh, which drives stamp.py alone.
#
#   GIT_BIN=<dir holding a git >= 2.54> \
#     bash dev/audit/harnesses/throwaway_git_sites.sh <RUNS> <ARM> [SITE...]
#
# ARM is what the caller's environment carries, through GIT_CONFIG_PARAMETERS
# (the `-c` channel, which git reads after GIT_CONFIG_COUNT and after every
# config file):
#   forced   maintenance.geometric-repack.auto=-1: the real repack fires on
#            every commit or merge that auto-maintenance is allowed to start
#            (the #2051 fix reviewer's method).
#   hostile  forced, plus maintenance.auto=true: an inherited value that beats
#            an env-only fix (the #2051 review, round 2).
#   plain    nothing: the null control.
# SITE is a self-test command name below; default all of them. Each is run
# RUNS times from the checkout this harness sits in. Prints, per site:
# runs, runs whose output names "Directory not empty", runs that exited
# non-zero for any reason, and maintenance_spawns: how many times any git the
# site ran started `git maintenance run --auto` (GIT_TRACE to a file, which
# every git the site starts inherits -- the helper keeps GIT_TRACE). That last
# count is the deterministic one: real git 2.55 spawns after every commit and
# merge unless auto-maintenance is off, whether or not the repack then races
# the cleanup. A spawn at a site the helper covers is a git call that read
# neither layer. The site self-tests are offline and commit only in their
# throwaway repositories, so the count is theirs.
set -u
RUNS="${1:-5}"
ARM="${2:-hostile}"
shift 2 2>/dev/null || shift $#
ROOT="$(cd "$(dirname -- "$0")/../../.." && pwd)" || exit 2
[ -f "$ROOT/custom_components/heatpump_optimizer/manifest.json" ] || { echo "no repository at $ROOT" >&2; exit 2; }
[ -x "${GIT_BIN:-}/git" ] || { echo "needs GIT_BIN=<dir with git >= 2.54>" >&2; exit 2; }
case "$ARM" in
  forced) P="'maintenance.geometric-repack.auto'='-1'" ;;
  hostile) P="'maintenance.auto'='true' 'maintenance.geometric-repack.auto'='-1'" ;;
  plain) P="" ;;
  *) echo "ARM is forced, hostile or plain" >&2; exit 2 ;;
esac
site_cmd() {
  case "$1" in
    stamp) echo "python3 tools/release/stamp.py --self-test" ;;
    ledger_merge) echo "python3 tools/merge/ledger_merge.py --self-test" ;;
    layout) echo "python3 tests/layout.py --self-test" ;;
    budget_raise_gate) echo "python3 tools/policy/budget_raise_gate.py --self-test" ;;
    bus) echo "bash tools/audit/seat/bus.sh --self-test" ;;
    merge_train) echo "python3 tools/audit/seat/merge_train.py --self-test" ;;
    roster_edit) echo "python3 tools/audit/seat/roster_edit.py --self-test" ;;
    state_docs) echo "python3 tools/audit/seat/state_docs.py --self-test" ;;
    app_approve) echo "bash tools/pr/app_approve.sh --self-test" ;;
    stop_hook) echo "bash .claude/hooks/stop-selfcheck.sh --self-test" ;;
    prepr) echo "bash tools/pr/prepr.sh --self-test" ;;
    *) return 1 ;;
  esac
}
[ $# -gt 0 ] || set -- stamp ledger_merge layout budget_raise_gate bus merge_train roster_edit state_docs app_approve stop_hook prepr
for site in "$@"; do
  cmd="$(site_cmd "$site")" || { echo "unknown site $site" >&2; exit 2; }
  race=0 fail=0 last= spawns=0
  for _ in $(seq 1 "$RUNS"); do
    tr="$(mktemp)" || exit 2
    if [ -n "$P" ]; then
      out="$(cd "$ROOT" && PATH="$GIT_BIN:$PATH" GIT_TRACE="$tr" GIT_CONFIG_PARAMETERS="$P" $cmd 2>&1)"; rc=$?
    else
      out="$(cd "$ROOT" && PATH="$GIT_BIN:$PATH" GIT_TRACE="$tr" $cmd 2>&1)"; rc=$?
    fi
    spawns=$((spawns + $(grep -c "run_command: git maintenance run --auto" "$tr")))
    rm -f "$tr"
    case "$out" in *"Directory not empty"*) race=$((race + 1)); last="$(grep -m1 "Directory not empty" <<<"$out")" ;; esac
    [ "$rc" -ne 0 ] && fail=$((fail + 1))
  done
  [ -n "$last" ] && echo "last: ${last#"${last%%[![:space:]]*}"}" | cut -c1-200
  echo "site=$site arm=$ARM git=$("$GIT_BIN/git" --version | cut -d' ' -f3) runs=$RUNS directory_not_empty=$race nonzero_exit=$fail maintenance_spawns=$spawns"
done
