#!/bin/bash
# Collect a merged pull request's worktree, branch and seat scratch.
#
#   tools/audit/worktree_gc.sh <owner/repo> [--dry-run] [--strict] [--keep-dir <path>]
#   tools/audit/worktree_gc.sh --self-test
#
# WHY THIS EXISTS. Seats work in /tmp/hpo-orch/<seat>/wt/ and nothing removed
# them: #716 collected detached review worktrees only, and a branch worktree --
# a fixer's -- was never touched by design. The disk filled at 9.5 GB of
# orphaned seat directories whose worktrees git had already pruned. The owner
# ruled the behaviour permanent and mechanistic (2026-09-19): after every merge
# the merged pull request's worktree, local branch and seat scratch go now,
# and cited evidence survives somewhere a verdict can still reach. The
# orchestrator calls this after each merge (`briefs/orchestrator.md` section
# 11); it is idempotent and safe to call at any moment, because everything it
# deletes is proved dead first. The remote branch is GitHub's auto-delete's,
# not this tool's.
#
# WHAT IT DELETES, and only after the proof names it:
#   A. a BRANCH worktree whose branch's pull request is MERGED, read from the
#      API (`gh pr list --state all --head <branch>`), never from the local
#      branch's existence. Merged work is on main, so `git worktree remove
#      --force` is safe however dirty the worktree is; its uncommitted diff is
#      PRINTED first (the orchestrator's stop-a-seat check). Then the local
#      branch (`git branch -D`), then the seat scratch directory.
#   B. a DETACHED worktree (reviewers check out merged pull request heads)
#      whose HEAD sha is a PROPER ancestor of origin/main -- the tip itself is
#      excluded, because reading live main is a running seat, not a leftover --
#      and only when clean including untracked: uncommitted work in a detached
#      worktree is on no branch and no remote, so no merge state can vouch
#      for it, and #716's round-4 evidence survived exactly that predicate.
#   C. an ORPHANED seat directory under the seats root whose wt/ is no longer
#      a registered worktree, with nothing under it modified within 2 hours
#      (the guard that protects a running seat) and no unmerged branch
#      readable inside it -- the 9.5 GB class.
#   D. a stale venv (a *-venv* directory under /tmp) untouched for 24 hours
#      that no registered worktree symlinks into at depth <= 2.
#
# THE KEEP RULES, ahead of every deletion and printed with their reason: the
# main checkout and the directory this runs from; `git worktree lock` (a
# seat's claim, HANDOVER trap 34); a branch with an OPEN pull request, ever; a
# branch with no pull request at all (ambiguous, not proved merged); a
# detached worktree that is dirty, at the origin/main tip, not an ancestor of
# origin/main, or younger than WORKTREE_GC_MIN_AGE; a seat directory holding
# another live worktree or anything that is not logs, scratch files or
# evidence; and everything at once when gh is missing or unauthenticated --
# that is a NOTICE and rc 0, fail-soft by design, not a refusal.
#
# EVIDENCE. Every evidence*/ev-* subdirectory of a seat directory is moved
# into --keep-dir (default /tmp/hpo-ev) before that seat directory is removed,
# because verdicts cite those paths; the move is printed so the log carries
# the new location. --dry-run prints every removal and every keep, moves
# nothing, removes nothing. rc is 0 on every fail-soft path; rc 1 only when
# --strict was passed and nothing eligible was found; rc 2 is a usage or
# environment error (no checkout, unreadable worktree list).
#
# Environment, for the self-test and for seats on another machine:
#   WORKTREE_GC_SEATS_ROOT (default /tmp/hpo-orch), WORKTREE_GC_TMP_ROOT
#   (default /tmp), WORKTREE_GC_MIN_AGE (3600, the detached guard),
#   WORKTREE_GC_ORPHAN_AGE (7200), WORKTREE_GC_VENV_AGE (86400).
set -uo pipefail

SEATS_ROOT="${WORKTREE_GC_SEATS_ROOT:-/tmp/hpo-orch}"
TMP_ROOT="${WORKTREE_GC_TMP_ROOT:-/tmp}"
MIN_AGE_DETACHED="${WORKTREE_GC_MIN_AGE:-3600}"
ORPHAN_AGE="${WORKTREE_GC_ORPHAN_AGE:-7200}"
VENV_AGE="${WORKTREE_GC_VENV_AGE:-86400}"
KEEP_DIR_DEFAULT=/tmp/hpo-ev

# --- self-test ---------------------------------------------------------------
# approve_held_runs.sh's stub style: `git` and `gh` are stubs on PATH, no
# network, no token, and this process's own worktrees are never walked -- the
# seats root and /tmp are redirected into the fixture. The stubs record every
# argv line, so keep/delete is asserted on the log as well as on the disk, and
# each case class has a mutation that turns it red (the pairs are recorded in
# the pull request that carried this file).
if [ "${1:-}" = "--self-test" ]; then
  SELF="$(cd "$(dirname -- "$0")" && pwd)/$(basename -- "$0")"
  W=$(mktemp -d) || exit 2
  trap 'rm -rf "$W"' EXIT
  mkdir -p "$W/bin"
  FAILS=0; N=0
  st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }

  cat > "$W/bin/git" <<'STUB'
#!/bin/bash
printf 'git %s\n' "$*" >> "$STUB/log"
enc() { printf '%s' "$1" | tr '/ ' '__'; }
case "$*" in
  "rev-parse --show-toplevel") cat "$STUB/rootfile" ;;
  "rev-parse origin/main") cat "$STUB/origin-main" ;;
  "worktree list --porcelain") cat "$STUB/porcelain" ;;
  "merge-base --is-ancestor "*)
      if grep -qx "$3" "$STUB/ancestors" 2>/dev/null; then exit 0; else exit 1; fi ;;
  "-C "*" status --porcelain")
      f="$STUB/status/$(enc "$2")"; [ -f "$f" ] && cat "$f"; exit 0 ;;
  "-C "*" diff")
      f="$STUB/diff/$(enc "$2")"; [ -f "$f" ] && cat "$f"; exit 0 ;;
  "-C "*" rev-parse --abbrev-ref HEAD")
      f="$STUB/branch-of/$(enc "$2")"; [ -f "$f" ] && cat "$f" || { echo "fatal: not a git repository" >&2; exit 128; } ;;
  "worktree remove --force "*) rm -rf "$4" ;;
  "branch -D "*) exit 0 ;;
  *) echo "git-stub: unexpected call: $*" >&2; exit 9 ;;
esac
STUB
  cat > "$W/bin/gh" <<'STUB'
#!/bin/bash
printf 'gh %s\n' "$*" >> "$STUB/log"
case "$1" in
  auth) [ -f "$STUB/noauth" ] && { echo "gh: not logged in" >&2; exit 1; }; exit 0 ;;
  pr)
      head=""; prev=""
      for a in "$@"; do if [ "$prev" = "--head" ]; then head=$a; fi; prev=$a; done
      f="$STUB/pr/$(printf '%s' "$head" | tr '/ ' '__').json"
      [ -f "$f" ] && cat "$f" || printf '[]' ;;
  *) echo "gh-stub: unexpected call: $*" >&2; exit 9 ;;
esac
STUB
  chmod +x "$W/bin/gh" "$W/bin/git"

  age_old() { # seconds dirs... -> every mtime under each back to now-seconds
    python3 - "$@" <<'PY'
import os, sys, time
t = time.time() - float(sys.argv[1])
for root in sys.argv[2:]:
    for dp, dns, fns in os.walk(root):
        try: os.utime(dp, (t, t))
        except OSError: pass
        for f in fns:
            try: os.utime(os.path.join(dp, f), (t, t))
            except OSError: pass
PY
  }
  H3=10800; H25=90000
  encpath() { printf '%s' "$1" | tr '/ ' '__'; }

  mkcase() { local d="$W/$1"; mkdir -p "$d/tmp" "$d/ev" "$d/root"; : > "$d/log"; printf '%s\n' "$d/root" > "$d/rootfile"; }
  run() { # name args... -> rc; out/err captured in the case dir
    local d="$W/$1"; shift
    # The redirect variables MUST be exported: set as plain shell variables
    # they reach no subprocess, and the sweep below then walks the REAL
    # /tmp/hpo-orch -- which a buggy early copy of this fixture did, removing
    # a live seat directory on the shared box. The sweep's "/tmp/hpo-orch"
    # null control pins the redirect itself.
    ( cd "$d/root"
      export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp"
      export WORKTREE_GC_SEATS_ROOT="$d/orch" WORKTREE_GC_TMP_ROOT="$d/tmp"
      bash "$SELF" "$@" > "$d/out" 2> "$d/err" )
  }
  gots() { grep -c -- "$2" "$W/$1/out"; }
  gone() { [ ! -e "$1" ]; }

  # The registered worktrees under test. PR state comes from the gh stub:
  # fix/merged MERGED, fix/open OPEN, fix/nopr none, fix/dirty MERGED.
  build() { # case-name
    local d="$W/$1"
    printf '1111111111111111111111111111111111111111\n' > "$d/origin-main"
    printf '2222222222222222222222222222222222222222\n2222222222222222222222222222222222222223\n' > "$d/ancestors"
    mkdir -p "$d/pr" "$d/status" "$d/diff" "$d/branch-of"
    printf '[{"state":"MERGED"}]\n' > "$d/pr/fix_merged.json"
    printf '[{"state":"OPEN"}]\n' > "$d/pr/fix_open.json"
    printf '[{"state":"MERGED"}]\n' > "$d/pr/fix_dirty.json"
    printf '[{"state":"MERGED"}]\n' > "$d/pr/fix_orphan-merged.json"
    printf '[{"state":"OPEN"}]\n' > "$d/pr/fix_orphan-open.json"
    { printf 'worktree %s/root\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n' "$d"
      printf 'worktree %s/orch/seat-merged/wt\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/fix/merged\n\n' "$d"
      printf 'worktree %s/orch/seat-open/wt\nHEAD 3333333333333333333333333333333333333333\nbranch refs/heads/fix/open\n\n' "$d"
      printf 'worktree %s/orch/seat-nopr/wt\nHEAD 4444444444444444444444444444444444444444\nbranch refs/heads/fix/nopr\n\n' "$d"
      printf 'worktree %s/orch/seat-detached/wt\nHEAD 2222222222222222222222222222222222222223\ndetached\n\n' "$d"
      printf 'worktree %s/orch/seat-unmerged/wt\nHEAD 5555555555555555555555555555555555555555\ndetached\n\n' "$d"
      printf 'worktree %s/orch/seat-dirtymerged/wt\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/fix/dirty\n\n' "$d"
      printf 'worktree %s/orch/seat-locked/wt\nHEAD 6666666666666666666666666666666666666666\ndetached\nlocked\n\n' "$d"
    } > "$d/porcelain"
    mkdir -p "$d/orch/seat-merged/wt" "$d/orch/seat-open/wt" "$d/orch/seat-nopr/wt" \
             "$d/orch/seat-detached/wt" "$d/orch/seat-detached/evidence-run12" \
             "$d/orch/seat-unmerged/wt" "$d/orch/seat-dirtymerged/wt" \
             "$d/orch/seat-locked/wt"
    printf 'x\n' > "$d/orch/seat-merged/wt/f"
    printf 'x\n' > "$d/orch/seat-detached/evidence-run12/ev.txt"
    printf 'M f\n' > "$d/status/$(encpath "$d/orch/seat-dirtymerged/wt")"
    printf -- '--- a/f\n+++ b/f\n-uncommitted\n+changed\n' > "$d/diff/$(encpath "$d/orch/seat-dirtymerged/wt")"
    # Collectable detached worktrees must be older than the hour guard.
    age_old "$H3" "$d/orch/seat-detached" "$d/orch/seat-unmerged" "$d/orch/seat-locked"
  }

  # The main sweep: every class in one run, so the interactions (one seat's
  # removal must not make another eligible) are pinned too.
  mkcase sweep; build sweep
  mkdir -p "$W/sweep/orch/seat-orph-old/wt" "$W/sweep/orch/seat-orph-old/ev-3" \
           "$W/sweep/orch/seat-orph-fresh/wt" "$W/sweep/orch/seat-orph-unmerged/wt" \
           "$W/sweep/orch/seat-orph-mergedwt/wt"
  printf 'e\n' > "$W/sweep/orch/seat-orph-old/ev-3/ev.txt"
  printf 'b\n' > "$W/sweep/orch/seat-orph-old/wt/b"
  printf 'o\n' > "$W/sweep/orch/seat-orph-unmerged/wt/o"
  printf 'm\n' > "$W/sweep/orch/seat-orph-mergedwt/wt/m"
  printf 'fix/orphan-open\n' > "$W/sweep/branch-of/$(encpath "$W/sweep/orch/seat-orph-unmerged/wt")"
  printf 'fix/orphan-merged\n' > "$W/sweep/branch-of/$(encpath "$W/sweep/orch/seat-orph-mergedwt/wt")"
  # No branch-of file for seat-orph-old: unreadable git, the pruned class.
  age_old "$H3" "$W/sweep/orch/seat-orph-old" "$W/sweep/orch/seat-orph-mergedwt" "$W/sweep/orch/seat-orph-unmerged"
  # seat-orph-fresh stays at natural now: the 2h guard's null control.
  mkdir -p "$W/sweep/tmp/stale-venv" "$W/sweep/tmp/inuse-venv"
  ln -s "$W/sweep/tmp/inuse-venv" "$W/sweep/orch/seat-open/wt/.venv"
  age_old "$H25" "$W/sweep/tmp/stale-venv" "$W/sweep/tmp/inuse-venv"

  run sweep --keep-dir "$W/sweep/ev" o/r; RC=$?
  st "$RC" 0 "the sweep over every class exits 0 (fail-soft)"
  D="$W/sweep"
  gone "$D/orch/seat-merged/wt"; st $? 0 "merged+clean: worktree removed"
  st "$(grep -c "^git worktree remove --force $D/orch/seat-merged/wt$" "$D/log")" 1 "with git worktree remove --force"
  st "$(grep -c "^git branch -D fix/merged$" "$D/log")" 1 "and the local branch deleted"
  gone "$D/orch/seat-merged"; st $? 0 "and the seat scratch directory removed"
  [ -d "$D/orch/seat-open/wt" ] && [ -d "$D/orch/seat-open" ]; st $? 0 "open PR: worktree and seat kept"
  st "$(gots sweep "keep  $D/orch/seat-open/wt  open-pr")" 1 "kept naming open-pr"
  st "$(grep -c "remove --force $D/orch/seat-open" "$D/log")" 0 "and no remove call for it (null control)"
  [ -d "$D/orch/seat-nopr/wt" ]; st $? 0 "no pull request at all: kept (ambiguous, not proved merged)"
  st "$(gots sweep "keep  $D/orch/seat-nopr/wt  no-merged-pr")" 1 "kept naming no-merged-pr"
  gone "$D/orch/seat-detached/wt"; st $? 0 "detached at a merged sha: worktree removed"
  [ -d "$D/ev/seat-detached/evidence-run12/ev.txt" ]; st $? 0 "its cited evidence moved into the keep-dir"
  gone "$D/orch/seat-detached/evidence-run12"; st $? 0 "out of the seat directory"
  gone "$D/orch/seat-detached"; st $? 0 "and the seat directory removed"
  st "$(gots sweep "kept-evidence  $D/orch/seat-detached/evidence-run12 -> $D/ev/seat-detached/evidence-run12")" 1 "and the move printed"
  [ -d "$D/orch/seat-unmerged/wt" ]; st $? 0 "detached at an unmerged sha: kept"
  st "$(gots sweep "keep  $D/orch/seat-unmerged/wt  unmerged-head")" 1 "kept naming unmerged-head"
  gone "$D/orch/seat-dirtymerged/wt"; st $? 0 "dirty merged: removed (force; merged work is on main)"
  st "$(grep -c "^git worktree remove --force $D/orch/seat-dirtymerged/wt$" "$D/log")" 1 "with force"
  st "$(gots sweep "uncommitted  $D/orch/seat-dirtymerged/wt")" 1 "its uncommitted state printed"
  st "$(gots sweep "+changed")" 1 "diff text included"
  l1=$(grep -n "^git -C $D/orch/seat-dirtymerged/wt diff$" "$D/log" | head -1 | cut -d: -f1)
  l2=$(grep -n "^git worktree remove --force $D/orch/seat-dirtymerged/wt$" "$D/log" | head -1 | cut -d: -f1)
  if [ -n "$l1" ] && [ -n "$l2" ] && [ "$l1" -lt "$l2" ]; then ORD=ordered; else ORD="diff=$l1 remove=$l2"; fi
  st "$ORD" ordered "the diff is printed BEFORE the removal (stop-a-seat check)"
  [ -d "$D/orch/seat-locked/wt" ]; st $? 0 "locked: kept (a seat's claim, trap 34)"
  st "$(gots sweep "keep  $D/orch/seat-locked/wt  locked")" 1 "kept naming locked"
  gone "$D/orch/seat-orph-old"; st $? 0 "orphan dir old and dead: seat dir removed"
  [ -d "$D/ev/seat-orph-old/ev-3/ev.txt" ]; st $? 0 "with its evidence preserved to the keep-dir"
  [ -d "$D/orch/seat-orph-fresh" ]; st $? 0 "orphan dir fresh: kept (2h guard)"
  st "$(gots sweep "keep  $D/orch/seat-orph-fresh  fresh")" 1 "kept naming fresh"
  [ -d "$D/orch/seat-orph-unmerged" ]; st $? 0 "orphan with an open-PR branch: kept"
  st "$(gots sweep "keep  $D/orch/seat-orph-unmerged  unmerged-branch")" 1 "kept naming unmerged-branch"
  gone "$D/orch/seat-orph-mergedwt"; st $? 0 "orphan with a merged branch: removed"
  gone "$D/tmp/stale-venv"; st $? 0 "stale venv: removed"
  [ -d "$D/tmp/inuse-venv" ]; st $? 0 "venv a live worktree symlinks: kept"
  st "$(gots sweep "keep  $D/tmp/inuse-venv  venv-in-use")" 1 "kept naming venv-in-use"
  [ -d "$D/root" ]; st $? 0 "the main checkout is never touched"
  st "$(gots sweep "/tmp/hpo-orch")" 0 "the fixture redirect holds: the real seats root is never walked (null control)"
  st "$(grep -c "^gh pr list" "$D/log")" 6 "one PR read per branch worktree plus the two orphan branches"
  st "$(grep -c "remove --force $D/orch/seat-nopr" "$D/log")" 0 "a no-PR branch is never removed"

  # --dry-run over a rebuilt fixture: identical decisions, nothing moved.
  mkcase dry; build dry
  run dry --dry-run --keep-dir "$W/dry/ev" o/r; st $? 0 "--dry-run exits 0"
  D="$W/dry"
  st "$(grep -c "^git worktree remove" "$D/log")" 0 "removes no worktree"
  st "$(grep -c "^git branch -D" "$D/log")" 0 "deletes no branch"
  [ -d "$D/orch/seat-merged/wt" ] && [ -d "$D/orch/seat-merged" ]; st $? 0 "leaves the merged seat on disk"
  [ -d "$D/orch/seat-detached/evidence-run12" ]; st $? 0 "moves no evidence"
  st "$(gots dry "remove  $D/orch/seat-merged/wt")" 1 "and says what would go"
  st "$(gots dry "keep  $D/orch/seat-open/wt  open-pr")" 1 "and what is kept, with the reason"

  # No gh: notice, rc 0, nothing removed.
  mkcase noauth; build noauth; : > "$W/noauth/noauth"
  run noauth --keep-dir "$W/noauth/ev" o/r; st $? 0 "unauthenticated gh: rc 0 (fail-soft)"
  st "$(grep -c "gh missing or unauthenticated" "$W/noauth/out")" 1 "a notice, not a refusal"
  st "$(grep -c "^git worktree remove" "$W/noauth/log")" 0 "and nothing removed"
  [ -d "$W/noauth/orch/seat-merged/wt" ]; st $? 0 "the merged worktree survives"

  # --strict: rc 1 only when nothing eligible was found at all.
  mkcase nothing
  printf 'worktree %s/root\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n' "$W/nothing" > "$W/nothing/porcelain"
  printf '1111111111111111111111111111111111111111\n' > "$W/nothing/origin-main"
  mkdir -p "$W/nothing/orch" "$W/nothing/tmp"
  run nothing --strict --keep-dir "$W/nothing/ev" o/r; st $? 1 "--strict with nothing eligible: rc 1"
  run nothing --keep-dir "$W/nothing/ev" o/r; st $? 0 "without --strict the same run is rc 0"

  # Usage refusals, before any subprocess runs.
  mkcase usage
  run usage; st $? 2 "no repository argument is a usage error"
  run usage not-a-repo; st $? 2 "and so is a repo without owner/repo shape"
  st "$(wc -l < "$W/usage/log" | tr -d ' ')" 0 "refused before any git or gh call"

  echo "worktree_gc self-test: $N checks, $FAILS failed"
  [ "$FAILS" -eq 0 ]
  exit $?
fi

# --- production --------------------------------------------------------------
DRY=0; STRICT=0; KEEP_DIR=""; REPO=""
die() { printf 'worktree_gc: REFUSE: %s\n' "$*" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --strict) STRICT=1 ;;
    --keep-dir) [ $# -ge 2 ] || die "--keep-dir needs a path"; KEEP_DIR=$2; shift ;;
    -*) die "unknown option '$1'" ;;
    *) [ -z "$REPO" ] || die "one repository argument, not several"; REPO=$1 ;;
  esac
  shift
done
[ -n "$REPO" ] || die "usage: worktree_gc.sh [--dry-run] [--strict] [--keep-dir <path>] <owner/repo>"
[[ $REPO =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repository '$REPO' is not owner/repo shaped"
KEEP_DIR="${KEEP_DIR:-$KEEP_DIR_DEFAULT}"

# Do not inherit a caller's GIT_DIR: that would make `git worktree list`
# describe the wrong repository, or none.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR
TOP=$(git rev-parse --show-toplevel 2>/dev/null) || die "this directory is no git checkout, so there is no worktree list to read"
cd "$TOP" || die "cannot cd to $TOP"
HERE=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$TOP")

realpath_of() { python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$1"; }

# Fail-soft gate: without an authenticated gh no merge state can be proved, so
# nothing is eligible and the run reports a notice rather than refusing.
gh_ready() { command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; }
if ! gh_ready; then
  printf 'worktree_gc: gh missing or unauthenticated; nothing removed (fail-soft)\n'
  exit 0
fi

LIST=$(mktemp) || die "cannot create a temp file"
LIVE_FILE=$(mktemp) || die "cannot create a temp file"
REMOVED_FILE=$(mktemp) || die "cannot create a temp file"
trap 'rm -f "$LIST" "$LIVE_FILE" "$REMOVED_FILE"' EXIT
git worktree list --porcelain >"$LIST" 2>/dev/null || die "git worktree list failed; nothing removed"

ORIGIN_MAIN_SHA=$(git rev-parse origin/main 2>/dev/null || printf '')

# state: open | merged | none | error -- from the API, never from the local
# branch's existence.
pr_state_of() {
  local out
  out=$(gh pr list -R "$REPO" --head "$1" --state all --json state --limit 50 2>/dev/null) || { printf 'error'; return; }
  printf '%s' "$out" | python3 -c '
import sys, json
try:
    d = json.loads(sys.stdin.read() or "[]")
except ValueError:
    print("error"); raise SystemExit
s = {(x.get("state") or "").upper() for x in d if isinstance(x, dict)}
print("open" if "OPEN" in s else ("merged" if "MERGED" in s else "none"))'
}

# A merged pull request's head is a PROPER ancestor of origin/main under this
# repository's merge method; the tip itself is a seat reading live main.
head_is_merged_ancestor() {
  [ -n "$ORIGIN_MAIN_SHA" ] || return 1
  [ "$1" = "$ORIGIN_MAIN_SHA" ] && return 1
  git merge-base --is-ancestor "$1" origin/main 2>/dev/null
}

# 0 iff something under dir was modified within the given seconds; the keep
# side of every age guard reads rc 0 as recent.
recently_modified() {
  python3 -c '
import os, sys, time
root, secs = sys.argv[1], float(sys.argv[2])
cutoff = time.time() - secs
def recent(dp):
    try:
        if os.stat(dp).st_mtime > cutoff: return True
    except OSError: pass
    if os.path.isfile(dp) or os.path.islink(dp): return False
    try: entries = os.listdir(dp)
    except OSError: return False
    return any(recent(os.path.join(dp, e)) for e in entries)
sys.exit(0 if recent(root) else 1)' "$1" "$2"
}

# 0 iff a registered worktree this run did not remove sits under seat-dir.
another_live_under() {
  python3 - "$1" "$REMOVED_FILE" "$LIVE_FILE" <<'PY'
import os, sys
seat = os.path.realpath(sys.argv[1])
def rd(p):
    try: return [l.rstrip("\n") for l in open(p) if l.strip()]
    except OSError: return []
removed = set(rd(sys.argv[2]))
for wt in rd(sys.argv[3]):
    if wt in removed: continue
    if wt == seat or wt.startswith(seat + os.sep):
        sys.exit(0)
sys.exit(1)
PY
}

# Move a seat directory's cited evidence into the keep-dir before removal.
preserve_evidence() { # seat-dir; one kept-evidence line per move
  local seat=$1 e dst_root dst n base
  for e in "$seat"/evidence* "$seat"/ev-*; do
    [ -d "$e" ] || continue
    base=$(basename "$e")
    dst_root="$KEEP_DIR/$(basename "$seat")"
    dst="$dst_root/$base"; n=1
    while [ -e "$dst" ]; do dst="$dst_root/$base-$n"; n=$((n+1)); done
    if [ "$DRY" -eq 1 ]; then
      printf 'kept-evidence  %s would move under %s (dry-run)\n' "$e" "$dst_root"
      continue
    fi
    if mkdir -p "$dst_root" && mv "$e" "$dst"; then
      printf 'kept-evidence  %s -> %s\n' "$e" "$dst"
    else
      printf 'worktree_gc: FAILED to preserve evidence %s\n' "$e" >&2
    fi
  done
}

# A seat directory goes only when nothing in it is another live worktree and
# what remains is logs, scratch files or (already preserved) evidence.
dispose_seat_dir() { # seat-dir, after its worktree was removed
  local seat=$1 e ok
  [ -d "$seat" ] || return 0
  if another_live_under "$seat"; then
    printf 'keep  %s  live-worktree\n' "$seat"; return 0
  fi
  preserve_evidence "$seat"
  ok=1
  while IFS= read -r e; do
    [ -n "$e" ] || continue
    if [ -d "$e" ] && [ -n "$(ls -A "$e" 2>/dev/null)" ]; then
      case "$(basename "$e")" in
        logs|*.log) ;;
        *) ok=0; printf 'keep  %s  nondisposable-contents (%s)\n' "$seat" "$(basename "$e")" ;;
      esac
    fi
  done < <(find "$seat" -mindepth 1 -maxdepth 1 2>/dev/null)
  [ "$ok" -eq 1 ] || return 0
  printf 'remove  %s (seat scratch)\n' "$seat"
  if [ "$DRY" -eq 0 ]; then
    rm -rf "$seat" && printf 'removed  %s\n' "$seat" \
      || printf 'worktree_gc: FAILED to remove %s\n' "$seat" >&2
  fi
}

seat_dir_of() { # a worktree's real path -> its seat dir when it is <seats>/<seat>/wt
  case "$1" in
    "$SEATS_REAL"/*/wt) dirname "$1" ;;
    *) printf '' ;;
  esac
}

SEATS_REAL=$(realpath_of "$SEATS_ROOT" 2>/dev/null || printf '%s' "$SEATS_ROOT")
KEEP_REAL=$(realpath_of "$KEEP_DIR" 2>/dev/null || printf '%s' "$KEEP_DIR")
ELIGIBLE=0; REMOVED_N=0; KEPT_N=0
HANDLED_SEATS=""

print_uncommitted() { # wt-path: the orchestrator's stop-a-seat check
  printf 'uncommitted  %s\n' "$1"
  git -C "$1" status --porcelain 2>/dev/null
  git -C "$1" diff 2>/dev/null
}

remove_worktree() { # wt-path
  printf 'remove  %s\n' "$1"
  printf '%s\n' "$(realpath_of "$1" 2>/dev/null || printf '%s' "$1")" >>"$REMOVED_FILE"
  if [ "$DRY" -eq 0 ]; then
    if git worktree remove --force "$1"; then
      printf 'removed  %s\n' "$1"; REMOVED_N=$((REMOVED_N+1))
    else
      printf 'worktree_gc: FAILED to remove worktree %s\n' "$1" >&2
    fi
  fi
}

# --- classes A and B: registered worktrees -----------------------------------
main_wt=""
wt=""; head=""; branch=""; has_branch=0; detached=0; locked=0

flush() {
  [ -n "$wt" ] || return 0
  classify
  wt=""; head=""; branch=""; has_branch=0; detached=0; locked=0
}

classify() {
  local real state seat st_out st_rc
  real=$(realpath_of "$wt" 2>/dev/null || printf '%s' "$wt")
  printf '%s\n' "$real" >>"$LIVE_FILE"

  if [ -z "$main_wt" ]; then main_wt=$real; fi
  if [ "$real" = "$main_wt" ]; then printf 'keep  %s  main\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0; fi
  if [ "$real" = "$HERE" ]; then printf 'keep  %s  current\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0; fi
  if [ "$locked" -eq 1 ]; then printf 'keep  %s  locked\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0; fi
  if [ ! -d "$wt" ]; then printf 'keep  %s  missing\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0; fi

  if [ "$has_branch" -eq 1 ]; then
    # Class A: a branch worktree goes only on an API-read MERGED pull request.
    state=$(pr_state_of "$branch")
    case "$state" in
      open) printf 'keep  %s  open-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
      merged) ;;
      none) printf 'keep  %s  no-merged-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
      *) printf 'keep  %s  gh-error\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
    esac
    ELIGIBLE=$((ELIGIBLE+1))
    st_out=$(git -C "$wt" status --porcelain 2>/dev/null); st_rc=$?
    if [ -n "$st_out" ] || [ "$st_rc" -ne 0 ]; then print_uncommitted "$wt"; fi
    remove_worktree "$wt"
    if [ "$DRY" -eq 0 ]; then
      git branch -D "$branch" 2>/dev/null \
        || printf 'worktree_gc: FAILED to delete branch %s\n' "$branch" >&2
    else
      printf 'remove  branch %s\n' "$branch"
    fi
    seat=$(seat_dir_of "$real")
    if [ -n "$seat" ]; then HANDLED_SEATS="$HANDLED_SEATS$seat\n"; dispose_seat_dir "$seat"; fi
    return 0
  fi

  # Class B: detached. Clean first -- uncommitted work is on no branch, so no
  # merge state can vouch for it (#716's round-4 evidence survived this).
  st_out=$(git -C "$wt" status --porcelain 2>/dev/null); st_rc=$?
  if [ -n "$st_out" ] || [ "$st_rc" -ne 0 ]; then
    printf 'keep  %s  dirty-detached\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0
  fi
  if ! head_is_merged_ancestor "$head"; then
    printf 'keep  %s  unmerged-head\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0
  fi
  if recently_modified "$real" "$MIN_AGE_DETACHED"; then
    printf 'keep  %s  young\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0
  fi
  ELIGIBLE=$((ELIGIBLE+1))
  remove_worktree "$wt"
  seat=$(seat_dir_of "$real")
  if [ -n "$seat" ]; then HANDLED_SEATS="$HANDLED_SEATS$seat\n"; dispose_seat_dir "$seat"; fi
}

while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in
    worktree\ *) flush; wt="${line#worktree }" ;;
    HEAD\ *) head="${line#HEAD }" ;;
    branch\ *) has_branch=1; branch="${line#branch refs/heads/}" ;;
    detached) detached=1 ;;
    locked*) locked=1 ;;
    "") flush ;;
  esac
done <"$LIST"
flush

# --- class C: orphaned seat directories --------------------------------------
is_registered() { awk -v p="$1" 'BEGIN{f=1} index(p, $0)==1 {f=0} END{exit f}' "$LIVE_FILE"; }
handled_seat() { printf '%b' "$HANDLED_SEATS" | grep -qx "$1"; }

if [ -d "$SEATS_REAL" ]; then
  for seat in "$SEATS_REAL"/*/; do
    [ -d "$seat" ] || continue
    seat_real=$(realpath_of "$seat")
    case "$seat_real" in "$KEEP_REAL"|"$KEEP_REAL"/*) continue ;; esac
    handled_seat "$seat_real" && continue
    [ -d "$seat/wt" ] || { printf 'keep  %s  no-wt\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue; }
    is_registered "$(realpath_of "$seat/wt")" && continue
    if recently_modified "$seat_real" "$ORPHAN_AGE"; then
      printf 'keep  %s  fresh\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue
    fi
    wt_branch=""
    if wt_branch=$(git -C "$seat_real/wt" rev-parse --abbrev-ref HEAD 2>/dev/null) \
       && [ "$wt_branch" != "HEAD" ]; then
      state=$(pr_state_of "$wt_branch")
      case "$state" in
        merged) ;;
        *) printf 'keep  %s  unmerged-branch\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue ;;
      esac
    elif [ "$wt_branch" = "HEAD" ]; then
      # A detached orphan goes only on a merged head whose sha still resolves.
      ohead=$(git -C "$seat_real/wt" rev-parse HEAD 2>/dev/null) || ohead=""
      if [ -z "$ohead" ] || ! head_is_merged_ancestor "$ohead"; then
        printf 'keep  %s  unmerged-head\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue
      fi
    fi
    ELIGIBLE=$((ELIGIBLE+1))
    printf 'remove  %s (orphaned seat)\n' "$seat"
    preserve_evidence "$seat_real"
    if [ "$DRY" -eq 0 ]; then
      rm -rf "$seat_real" && printf 'removed  %s\n' "$seat" && REMOVED_N=$((REMOVED_N+1)) \
        || printf 'worktree_gc: FAILED to remove %s\n' "$seat" >&2
    fi
  done
fi

# --- class D: stale venvs ----------------------------------------------------
venv_referenced() { # vdir -> 0 when a live worktree symlinks into it (depth <= 2)
  python3 - "$1" "$REMOVED_FILE" "$LIVE_FILE" <<'PY'
import os, sys
vdir = os.path.realpath(sys.argv[1])
def rd(p):
    try: return [l.rstrip("\n") for l in open(p) if l.strip()]
    except OSError: return []
removed = set(rd(sys.argv[2]))
for wt in rd(sys.argv[3]):
    if wt in removed: continue
    for dp, dns, fns in os.walk(wt):
        if os.path.relpath(dp, wt).count(os.sep) >= 2:
            dns[:] = []
        for f in fns:
            p = os.path.join(dp, f)
            try:
                if os.path.islink(p) and os.path.realpath(p).startswith(vdir + os.sep):
                    sys.exit(0)
            except OSError: pass
sys.exit(1)
PY
}

if [ -d "$TMP_ROOT" ]; then
  for venv in "$TMP_ROOT"/*-venv*; do
    [ -d "$venv" ] && [ ! -L "$venv" ] || continue
    case "$(realpath_of "$venv")" in "$KEEP_REAL"*) continue ;; esac
    if recently_modified "$venv" "$VENV_AGE"; then
      printf 'keep  %s  fresh-venv\n' "$venv"; KEPT_N=$((KEPT_N+1)); continue
    fi
    if venv_referenced "$venv"; then
      printf 'keep  %s  venv-in-use\n' "$venv"; KEPT_N=$((KEPT_N+1)); continue
    fi
    ELIGIBLE=$((ELIGIBLE+1))
    printf 'remove  %s (stale venv)\n' "$venv"
    if [ "$DRY" -eq 0 ]; then
      rm -rf "$venv" && printf 'removed  %s\n' "$venv" && REMOVED_N=$((REMOVED_N+1)) \
        || printf 'worktree_gc: FAILED to remove %s\n' "$venv" >&2
    fi
  done
fi

printf 'worktree_gc: summary -- eligible %d, removed %d, kept %d\n' "$ELIGIBLE" "$REMOVED_N" "$KEPT_N"
if [ "$ELIGIBLE" -eq 0 ] && [ "$STRICT" -eq 1 ]; then
  printf 'worktree_gc: --strict and nothing eligible\n'
  exit 1
fi
exit 0
