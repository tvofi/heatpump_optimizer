#!/bin/bash
# Collect a merged pull request's worktree, branch and seat scratch.
#
#   tools/audit/worktree_gc.sh <owner/repo> [--dry-run] [--strict] [--keep-dir <path>]
#     --keep-dir is the EVIDENCE DESTINATION, not a keep list: nothing is protected by naming it.
#     A worktree a live process reads is kept by itself (cwd, argv, open file, live pidfile).
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
#      branch's existence. Merged work is on main, so removing the worktree is
#      safe however dirty it is; its uncommitted diff is PRINTED first (the
#      orchestrator's stop-a-seat check). The removal is leased at the head the
#      porcelain read, as in B (remove_worktree). Then the local
#      branch, leased at the head the porcelain read (`git update-ref -d
#      refs/heads/<branch> <head>`: a branch that moved since is kept and the
#      refusal reported), then the seat scratch directory.
#      A SEAT BRANCH (`work/<t>`, `scratch/<t>`, `seat/<t>`) has no pull request
#      of its own: its PR sits on `fix/<t>`. A MERGED or CLOSED one there frees
#      the seat, but only clean (uncommitted work is on no remote) and, as for
#      every arm, with no unpushed commit and no process cwd inside it.
#      Every removal arm keeps a worktree a process stands in (`cwd-inside`).
#   B. a DETACHED worktree (reviewers check out merged pull request heads)
#      whose HEAD sha is a PROPER ancestor of origin/main -- the tip itself is
#      excluded, because reading live main is a running seat, not a leftover --
#      and only when clean including untracked: uncommitted work in a detached
#      worktree is on no branch and no remote, so no merge state can vouch
#      for it, and #716's round-4 evidence survived exactly that predicate.
#      Its HEAD is the only ref holding a commit made there, so the removal is
#      leased at the head the porcelain read (`git -C <wt> update-ref
#      --no-deref -d HEAD <head>`, then the tree and its admin entry): a HEAD
#      that moved since is kept and the refusal reported.
#   C. an ORPHANED seat directory under the seats root whose wt/ is no longer
#      a registered worktree, with nothing under it modified within 2 hours
#      (the guard that protects a running seat), no unmerged branch readable
#      inside it and no other live worktree beneath it -- the 9.5 GB class.
#      A wt/ git can read is removed leased at the HEAD read in it (`git -C
#      <wt> update-ref --no-deref -d HEAD <head>`, then rm -rf): a HEAD that
#      moved since, or one that cannot be read, keeps the seat.
#   E. a PLAIN COPY of the repository (a `*mutant*`, `*null*` or `*head*`
#      directory without .git) directly inside a seat directory whose topic --
#      the directory name less a leading `seat-` -- has a MERGED pull request
#      on `fix/<topic>`, with nothing under the seat modified within the orphan
#      age, no live worktree beneath the seat and no process cwd in the copy.
#   D. a stale venv (a *-venv* directory under /tmp) untouched for 24 hours
#      that no registered worktree symlinks into at depth <= 2.
#
#      A detached worktree whose head is NOT on main may still go as
#      `on-remote`: clean, not young, not at the origin/main tip, head
#      reachable from refs/remotes/* or refs/tags/* (read after one
#      `git fetch --prune origin` at the start of the run; a failed fetch keeps
#      them all as unmerged-head), and no process with a working directory
#      inside it (`lsof -a -d cwd`; an unreadable lsof keeps it, naming
#      cwd-unread). Its commits are on a remote ref, so nothing is lost.
#
# THE KEEP RULES, ahead of every deletion and printed with their reason: the
# main checkout and the directory this runs from; `git worktree lock` (a
# seat's claim, HANDOVER trap 34); a branch with an OPEN pull request, ever; a
# branch with no pull request at all (ambiguous, not proved merged); a
# branch worktree holding a commit no remote ref has (`unpushed`, whatever its
# pull request says: a merged PR of the same branch name is no proof the new
# commit merged); a
# detached worktree that is dirty, at the origin/main tip, not an ancestor of
# origin/main, or younger than WORKTREE_GC_MIN_AGE; a seat directory holding
# another live worktree or anything that is not logs, scratch files or
# evidence; and everything at once when gh is missing or unauthenticated --
# that is a NOTICE and rc 0, fail-soft by design, not a refusal.
#
# EVIDENCE. Every evidence*/ev-* subdirectory of a seat directory is moved
# into --keep-dir (default $HPO_STATE_DIR/ev, outside every temp dir) before that seat directory is removed,
# because verdicts cite those paths; the move is printed so the log carries
# the new location. --dry-run prints every removal and every keep, moves
# nothing, removes nothing. rc is 0 on every fail-soft path; rc 1 only when
# --strict was passed and nothing eligible was found; rc 2 is a usage or
# environment error (no checkout, unreadable worktree list).
#
# Environment, for the self-test and for seats on another machine:
#   WORKTREE_GC_SEATS_ROOT (default /tmp/hpo-orch; a colon-separated list --
#   seats live under ~/hpo-seats/<round>), WORKTREE_GC_TMP_ROOT
#   (default /tmp), WORKTREE_GC_MIN_AGE (3600, the detached guard),
#   WORKTREE_GC_ORPHAN_AGE (7200), WORKTREE_GC_VENV_AGE (86400).
set -uo pipefail

SEATS_ROOT="${WORKTREE_GC_SEATS_ROOT:-/tmp/hpo-orch}"
TMP_ROOT="${WORKTREE_GC_TMP_ROOT:-/tmp}"
MIN_AGE_DETACHED="${WORKTREE_GC_MIN_AGE:-3600}"
ORPHAN_AGE="${WORKTREE_GC_ORPHAN_AGE:-7200}"
VENV_AGE="${WORKTREE_GC_VENV_AGE:-86400}"
KEEP_DIR_DEFAULT=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/ev

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
  # Normalize once: the tool realpaths every path it handles, and on macOS
  # mktemp's /var/... is /private/var/... after resolution -- the stubs key
  # their answers on the path they are handed, so the fixture must live on
  # the resolved form or every lookup silently misses.
  W=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$W")
  trap '[ -n "${ZPID:-}" ] && kill "$ZPID" 2>/dev/null; rm -rf "$W"' EXIT
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
  "-C "*" rev-parse HEAD")
      f="$STUB/head-of/$(enc "$2")"; [ -f "$f" ] && cat "$f" || { echo "fatal: not a git repository" >&2; exit 128; } ;;
  "fetch --prune origin") [ -f "$STUB/fetchfail" ] && exit 1; exit 0 ;;
  "for-each-ref --count=1 --contains "*)
      if grep -qx "$4" "$STUB/onremote" 2>/dev/null; then echo "refs/remotes/origin/some-branch"; fi; exit 0 ;;
  "-C "*" rev-list --count HEAD --not --remotes")
      f="$STUB/unpushed/$(enc "$2")"; [ -f "$f" ] && cat "$f" || echo 0; exit 0 ;;
  "-C "*" update-ref --no-deref -d HEAD "*)
      # The worktree lease: refuse when its HEAD's live value (a live/ file
      # keyed by the worktree path, else unmoved) is not the old value given.
      f="$STUB/live/$(enc "$2")"
      if [ -n "${7:-}" ] && [ -f "$f" ] && [ "$(cat "$f")" != "$7" ]; then
        echo "fatal: cannot lock ref 'HEAD': is at $(cat "$f") but expected $7" >&2; exit 1
      fi
      exit 0 ;;
  "worktree prune") exit 0 ;;
  "update-ref -d "*)
      # The local lease: refuse when the ref's live value (a live/ file, else
      # unmoved) is not the old value given; no old value deletes regardless.
      f="$STUB/live/$(enc "$3")"
      if [ -n "${4:-}" ] && [ -f "$f" ] && [ "$(cat "$f")" != "$4" ]; then
        echo "fatal: cannot lock ref '$3': is at $(cat "$f") but expected $4" >&2; exit 1
      fi
      printf '%s\n' "$3" >> "$STUB/deleted"; exit 0 ;;
  "branch -D "*) printf 'refs/heads/%s\n' "$3" >> "$STUB/deleted"; exit 0 ;;   # unleased: deletes wherever the ref is
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
  cat > "$W/bin/lsof" <<'STUB'
#!/bin/bash
printf 'lsof %s\n' "$*" >> "$STUB/log"
[ -f "$STUB/lsofbroken" ] && exit 1
case " $* " in *" -d cwd "*) ;; *) [ -f "$STUB/lsofopenbroken" ] && exit 1 ;; esac
printf 'p1\nn/\n'
case " $* " in *" -d cwd "*) [ -f "$STUB/cwds" ] && sed 's/^/n/' "$STUB/cwds" ;; *) [ -f "$STUB/opens" ] && sed 's/^/n/' "$STUB/opens" ;; esac
exit 0
STUB
  cat > "$W/bin/ps" <<'STUB'
#!/bin/bash
printf 'ps %s\n' "$*" >> "$STUB/log"
[ -f "$STUB/psbroken" ] && exit 1
printf 'init\n'
[ -f "$STUB/argv" ] && cat "$STUB/argv"
exit 0
STUB
  chmod +x "$W/bin/gh" "$W/bin/git" "$W/bin/lsof" "$W/bin/ps"

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

  # A live process whose pid contains a zero digit (a pidfile read must keep the 0).
  # No signal is sent here: a child whose pid has no 0 exits by itself, so no
  # forked copy of this shell can die by a signal and run the EXIT trap's rm.
  while :; do sh -c 'case $$ in *0*) exec sleep 600 ;; esac' & ZPID=$!; case $ZPID in *0*) break ;; esac; wait "$ZPID"; done
  mkcase() { local d="$W/$1"; mkdir -p "$d/tmp" "$d/ev" "$d/root"; : > "$d/log"; : > "$d/deleted"; printf '%s\n' "$d/root" > "$d/rootfile"; }
  run() { # name args... -> rc; out/err captured in the case dir
    local d="$W/$1"; shift
    # The redirect variables MUST be exported: set as plain shell variables
    # they reach no subprocess, and the sweep below then walks the REAL
    # /tmp/hpo-orch -- which a buggy early copy of this fixture did, removing
    # a live seat directory on the shared box. The sweep's "/tmp/hpo-orch"
    # null control pins the redirect itself.
    ( cd "$d/root"
      export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp"
      export WORKTREE_GC_SEATS_ROOT="$(cat "$d/seatsroot" 2>/dev/null || printf '%s' "$d/orch")" WORKTREE_GC_TMP_ROOT="$d/tmp"
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
      for n in onremote:7 cwd:8 onremote-young:9 onremote-dirty:b tip:1 nohold:d argvuse:7 openuse:7 deadpid:7 argvscr:7 argvdq:7 argvsq:7 argvcol:7 argvcom:7 argvsib:7 openeq:7 opensib:7 pidzero:7 lockuse:7 dotlock:7; do
        printf 'worktree %s/orch/seat-%s/wt\nHEAD %s\ndetached\n\n' "$d" "${n%%:*}" "$(printf '%040d' 0 | tr 0 "${n##*:}")"
      done
      printf 'worktree %s/orch/seat-onremote-locked/wt\nHEAD %s\ndetached\nlocked\n\n' "$d" "$(printf '%040d' 0 | tr 0 a)"
      printf 'worktree %s/orch/seat-unpushed/wt\nHEAD %s\nbranch refs/heads/fix/unpushed\n\n' "$d" "$(printf '%040d' 0 | tr 0 c)"
    } > "$d/porcelain"
    mkdir -p "$d/orch/seat-merged/wt" "$d/orch/seat-open/wt" "$d/orch/seat-nopr/wt" \
             "$d/orch/seat-detached/wt" "$d/orch/seat-detached/evidence-run12" \
             "$d/orch/seat-unmerged/wt" "$d/orch/seat-dirtymerged/wt" \
             "$d/orch/seat-locked/wt" "$d/orch/seat-onremote/wt" "$d/orch/seat-cwd/wt/sub" \
             "$d/orch/seat-argvuse/wt" "$d/orch/seat-openuse/wt" "$d/orch/seat-deadpid/wt" \
             "$d/orch/seat-argvscr/wt" "$d/orch/seat-argvdq/wt" "$d/orch/seat-argvsq/wt" "$d/orch/seat-argvcol/wt" "$d/orch/seat-argvcom/wt" "$d/orch/seat-argvsib/wt" "$d/orch/seat-openeq/wt" "$d/orch/seat-opensib/wt" "$d/orch/seat-pidzero/wt" "$d/orch/seat-lockuse/wt" "$d/orch/seat-dotlock/wt" \
             "$d/orch/seat-onremote-young/wt" "$d/orch/seat-onremote-dirty/wt" \
             "$d/orch/seat-tip/wt" "$d/orch/seat-nohold/wt" "$d/orch/seat-onremote-locked/wt" \
             "$d/orch/seat-unpushed/wt" "$d/unpushed"
    # Heads a remote ref holds (the origin/main tip 1111 included: a seat reading live main).
    for c in 7 8 9 a b 1; do printf '%040d\n' 0 | tr 0 "$c"; done > "$d/onremote"
    printf '%s/orch/seat-cwd/wt/sub\n' "$d" > "$d/cwds"
    # Live users that are NOT a cwd: a `git -C <wt>` argv, an open file, a live train.pid.
    { printf 'git -C %s/orch/seat-argvuse/wt log\n' "$d"
      printf 'bash %s/orch/seat-argvscr/wt/script.sh\n' "$d"
      printf 'sh -c cd "%s/orch/seat-argvdq/wt"; make\n' "$d"
      printf "sh -c cd '%s/orch/seat-argvsq/wt'; make\\n" "$d"
      printf 'git --paths=%s/orch/seat-argvcol/wt:/tmp status\n' "$d"
      printf 'git --paths=%s/orch/seat-argvcom/wt,/tmp status\n' "$d"
      printf 'git -C %s/orch/seat-argvsib/wt2 log\n' "$d"; } > "$d/argv"
    { printf '%s/orch/seat-openuse/wt/f\n' "$d"
      printf '%s/orch/seat-openeq/wt\n' "$d"
      printf '%s/orch/seat-opensib/wt2/f\n' "$d"; } > "$d/opens"
    printf '2999999\n' > "$d/orch/seat-deadpid/wt/train.pid"
    printf '%s\n' "$ZPID" > "$d/orch/seat-pidzero/wt/train.pid"
    printf '%s\n' "$$" > "$d/orch/seat-lockuse/wt/x.lock"
    printf '%s\n' "$$" > "$d/orch/seat-dotlock/wt/.x.lock"
    printf 'M f\n' > "$d/status/$(encpath "$d/orch/seat-onremote-dirty/wt")"
    printf '[{"state":"MERGED"}]\n' > "$d/pr/fix_unpushed.json"
    printf '1\n' > "$d/unpushed/$(encpath "$d/orch/seat-unpushed/wt")"
    printf 'x\n' > "$d/orch/seat-merged/wt/f"
    printf 'x\n' > "$d/orch/seat-detached/evidence-run12/ev.txt"
    printf 'M f\n' > "$d/status/$(encpath "$d/orch/seat-dirtymerged/wt")"
    printf -- '--- a/f\n+++ b/f\n-uncommitted\n+changed\n' > "$d/diff/$(encpath "$d/orch/seat-dirtymerged/wt")"
    # Collectable detached worktrees must be older than the hour guard.
    age_old "$H3" "$d/orch/seat-detached" "$d/orch/seat-unmerged" "$d/orch/seat-locked" \
            "$d/orch/seat-onremote" "$d/orch/seat-cwd" "$d/orch/seat-onremote-dirty" "$d/orch/seat-tip" \
            "$d/orch/seat-nohold" "$d/orch/seat-onremote-locked" "$d/orch/seat-unpushed" \
            "$d/orch/seat-argvuse" "$d/orch/seat-openuse" "$d/orch/seat-deadpid" \
            "$d/orch/seat-argvscr" "$d/orch/seat-argvdq" "$d/orch/seat-argvsq" "$d/orch/seat-argvcol" "$d/orch/seat-argvcom" "$d/orch/seat-argvsib" "$d/orch/seat-openeq" "$d/orch/seat-opensib" "$d/orch/seat-pidzero" "$d/orch/seat-lockuse" "$d/orch/seat-dotlock"
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
  mkdir -p "$W/sweep/head-of"
  printf '2222222222222222222222222222222222222222\n' > "$W/sweep/head-of/$(encpath "$W/sweep/orch/seat-orph-mergedwt/wt")"
  printf '5555555555555555555555555555555555555555\n' > "$W/sweep/head-of/$(encpath "$W/sweep/orch/seat-orph-unmerged/wt")"
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
  st "$(grep -c "^git -C $D/orch/seat-merged/wt update-ref --no-deref -d HEAD 2222222222222222222222222222222222222222$" "$D/log")" 1 "the removal leased at the head the porcelain read (class A)"
  st "$(grep -c "^git update-ref -d refs/heads/fix/merged 2222222222222222222222222222222222222222$" "$D/log")" 1 "and the local branch deleted, leased at the head the porcelain read"
  gone "$D/orch/seat-merged"; st $? 0 "and the seat scratch directory removed"
  [ -d "$D/orch/seat-open/wt" ] && [ -d "$D/orch/seat-open" ]; st $? 0 "open PR: worktree and seat kept"
  st "$(gots sweep "keep  $D/orch/seat-open/wt  open-pr")" 1 "kept naming open-pr"
  st "$(grep -c "$D/orch/seat-open/wt update-ref --no-deref" "$D/log")" 0 "and no remove call for it (null control)"
  [ -d "$D/orch/seat-nopr/wt" ]; st $? 0 "no pull request at all: kept (ambiguous, not proved merged)"
  st "$(gots sweep "keep  $D/orch/seat-nopr/wt  no-merged-pr")" 1 "kept naming no-merged-pr"
  gone "$D/orch/seat-detached/wt"; st $? 0 "detached at a merged sha: worktree removed"
  st "$(grep -c "^git -C $D/orch/seat-detached/wt update-ref --no-deref -d HEAD 2222222222222222222222222222222222222223$" "$D/log")" 1 "the removal leased at the head the porcelain read (class B)"
  [ -f "$D/ev/seat-detached/evidence-run12/ev.txt" ]; st $? 0 "its cited evidence moved into the keep-dir"
  gone "$D/orch/seat-detached/evidence-run12"; st $? 0 "out of the seat directory"
  gone "$D/orch/seat-detached"; st $? 0 "and the seat directory removed"
  st "$(gots sweep "kept-evidence  $D/orch/seat-detached/evidence-run12 -> $D/ev/seat-detached/evidence-run12")" 1 "and the move printed"
  [ -d "$D/orch/seat-unmerged/wt" ]; st $? 0 "detached at an unmerged sha: kept"
  st "$(gots sweep "keep  $D/orch/seat-unmerged/wt  unmerged-head")" 1 "kept naming unmerged-head"
  gone "$D/orch/seat-dirtymerged/wt"; st $? 0 "dirty merged: removed (force; merged work is on main)"
  st "$(grep -c "^git -C $D/orch/seat-dirtymerged/wt update-ref --no-deref -d HEAD 2222222222222222222222222222222222222222$" "$D/log")" 1 "dirty or not (merged work is on main)"
  st "$(gots sweep "uncommitted  $D/orch/seat-dirtymerged/wt")" 1 "its uncommitted state printed"
  st "$(gots sweep "+changed")" 1 "diff text included"
  l1=$(grep -n "^git -C $D/orch/seat-dirtymerged/wt diff$" "$D/log" | head -1 | cut -d: -f1)
  l2=$(grep -n "^git -C $D/orch/seat-dirtymerged/wt update-ref --no-deref -d HEAD " "$D/log" | head -1 | cut -d: -f1)
  if [ -n "$l1" ] && [ -n "$l2" ] && [ "$l1" -lt "$l2" ]; then ORD=ordered; else ORD="diff=$l1 remove=$l2"; fi
  st "$ORD" ordered "the diff is printed BEFORE the removal (stop-a-seat check)"
  [ -d "$D/orch/seat-locked/wt" ]; st $? 0 "locked: kept (a seat's claim, trap 34)"
  st "$(gots sweep "keep  $D/orch/seat-locked/wt  locked")" 1 "kept naming locked"
  gone "$D/orch/seat-orph-old"; st $? 0 "orphan dir old and dead: seat dir removed"
  [ -f "$D/ev/seat-orph-old/ev-3/ev.txt" ]; st $? 0 "with its evidence preserved to the keep-dir"
  [ -d "$D/orch/seat-orph-fresh" ]; st $? 0 "orphan dir fresh: kept (2h guard)"
  st "$(gots sweep "keep  $D/orch/seat-orph-fresh  fresh")" 1 "kept naming fresh"
  [ -d "$D/orch/seat-orph-unmerged" ]; st $? 0 "orphan with an open-PR branch: kept"
  st "$(gots sweep "keep  $D/orch/seat-orph-unmerged  unmerged-branch")" 1 "kept naming unmerged-branch"
  gone "$D/orch/seat-orph-mergedwt"; st $? 0 "orphan with a merged branch: removed"
  st "$(grep -c "^git -C $D/orch/seat-orph-mergedwt/wt update-ref --no-deref -d HEAD 2222222222222222222222222222222222222222$" "$D/log")" 1 "the orphan removal leased at the head the read gave (class C)"
  gone "$D/tmp/stale-venv"; st $? 0 "stale venv: removed"
  [ -d "$D/tmp/inuse-venv" ]; st $? 0 "venv a live worktree symlinks: kept"
  st "$(gots sweep "keep  $D/tmp/inuse-venv  venv-in-use")" 1 "kept naming venv-in-use"
  [ -d "$D/root" ]; st $? 0 "the main checkout is never touched"
  st "$(gots sweep "/tmp/hpo-orch")" 0 "the fixture redirect holds: the real seats root is never walked (null control)"
  st "$(grep -c "^gh pr list" "$D/log")" 7 "one PR read per branch worktree (the unpushed one included) plus the two orphan branches"
  st "$(grep -c "$D/orch/seat-nopr/wt update-ref --no-deref" "$D/log")" 0 "a no-PR branch is never removed"

  # on-remote (V137): a clean, old, detached head only a remote ref holds goes.
  gone "$D/orch/seat-onremote/wt"; st $? 0 "on-remote: a clean detached worktree at a head a remote ref holds is removed"
  st "$(gots sweep "remove  $D/orch/seat-onremote/wt  on-remote")" 1 "naming on-remote"
  [ -d "$D/orch/seat-nohold/wt" ]; st $? 0 "null control: the same at a head no remote ref or tag holds is kept"
  st "$(gots sweep "keep  $D/orch/seat-nohold/wt  unmerged-head")" 1 "naming unmerged-head"
  [ -d "$D/orch/seat-cwd/wt" ]; st $? 0 "a process cwd inside an on-remote worktree: kept"
  st "$(gots sweep "keep  $D/orch/seat-cwd/wt  cwd-inside")" 1 "naming cwd-inside"
  # P453: a live process reaching the checkout without a cwd in it (git -C, open file, live train.pid).
  [ -d "$D/orch/seat-argvuse/wt" ]; st $? 0 "argv names the worktree (git -C), cwd elsewhere: kept"
  st "$(gots sweep "keep  $D/orch/seat-argvuse/wt  argv-inside")" 1 "naming argv-inside"
  [ -d "$D/orch/seat-openuse/wt" ]; st $? 0 "an open file inside, cwd elsewhere: kept"
  st "$(gots sweep "keep  $D/orch/seat-openuse/wt  open-file")" 1 "naming open-file"
  [ -d "$D/orch/seat-argvscr/wt" ]; st $? 0 "argv names a script inside the worktree (terminator /), cwd elsewhere: kept"
  st "$(gots sweep "keep  $D/orch/seat-argvscr/wt  argv-inside")" 1 "naming argv-inside for the script path"
  [ -d "$D/orch/seat-argvdq/wt" ]; st $? 0 "argv carries a double-quoted <wt> token from sh -c cd (double-quote terminator), cwd elsewhere: kept"
  st "$(gots sweep "keep  $D/orch/seat-argvdq/wt  argv-inside")" 1 "naming argv-inside for argvdq"
  [ -d "$D/orch/seat-argvsq/wt" ]; st $? 0 "argv carries a single-quoted <wt> token (single-quote terminator), cwd elsewhere: kept"
  st "$(gots sweep "keep  $D/orch/seat-argvsq/wt  argv-inside")" 1 "naming argv-inside for argvsq"
  [ -d "$D/orch/seat-argvcol/wt" ]; st $? 0 "argv carries --paths=<wt>:/tmp (colon terminator), cwd elsewhere: kept"
  st "$(gots sweep "keep  $D/orch/seat-argvcol/wt  argv-inside")" 1 "naming argv-inside for argvcol"
  [ -d "$D/orch/seat-argvcom/wt" ]; st $? 0 "argv carries --paths=<wt>,/tmp (comma terminator), cwd elsewhere: kept"
  st "$(gots sweep "keep  $D/orch/seat-argvcom/wt  argv-inside")" 1 "naming argv-inside for argvcom"
  gone "$D/orch/seat-argvsib/wt"; st $? 0 "null control: argv naming a sibling prefix (<worktree>2) holds nothing and the worktree is collected"
  [ -d "$D/orch/seat-openeq/wt" ]; st $? 0 "an open file that is the worktree directory itself, cwd elsewhere: kept"
  st "$(gots sweep "keep  $D/orch/seat-openeq/wt  open-file")" 1 "naming open-file for the directory itself"
  gone "$D/orch/seat-opensib/wt"; st $? 0 "null control: an open file under a sibling prefix (<worktree>2/f) holds nothing and the worktree is collected"
  [ -d "$D/orch/seat-pidzero/wt" ]; st $? 0 "a live pid containing a zero digit in train.pid: kept"
  st "$(gots sweep "keep  $D/orch/seat-pidzero/wt  pidfile-live")" 1 "naming pidfile-live for the zero-digit pid"
  [ -d "$D/orch/seat-lockuse/wt" ]; st $? 0 "a live pid in <worktree>/x.lock: kept"
  st "$(gots sweep "keep  $D/orch/seat-lockuse/wt  pidfile-live")" 1 "naming pidfile-live for x.lock"
  [ -d "$D/orch/seat-dotlock/wt" ]; st $? 0 "a live pid in <worktree>/.x.lock: kept"
  st "$(gots sweep "keep  $D/orch/seat-dotlock/wt  pidfile-live")" 1 "naming pidfile-live for .x.lock"
  gone "$D/orch/seat-deadpid/wt"; st $? 0 "null control: the same worktree with a dead-pid train.pid and no live user is collected"
  [ -d "$D/orch/seat-onremote-young/wt" ]; st $? 0 "a young on-remote worktree: kept"
  st "$(gots sweep "keep  $D/orch/seat-onremote-young/wt  young")" 1 "naming young"
  [ -d "$D/orch/seat-onremote-dirty/wt" ]; st $? 0 "a dirty on-remote worktree: kept"
  st "$(gots sweep "keep  $D/orch/seat-onremote-dirty/wt  dirty-detached")" 1 "naming dirty-detached"
  [ -d "$D/orch/seat-onremote-locked/wt" ]; st $? 0 "a locked on-remote worktree: kept"
  st "$(gots sweep "keep  $D/orch/seat-onremote-locked/wt  locked")" 1 "naming locked"
  [ -d "$D/orch/seat-tip/wt" ]; st $? 0 "a worktree at the origin/main tip is kept though a remote ref holds it"
  st "$(gots sweep "keep  $D/orch/seat-tip/wt  unmerged-head")" 1 "naming unmerged-head"
  # unpushed work (the 2026-10-20 roster worktree): a branch with a merged PR, one commit on no remote ref.
  [ -d "$D/orch/seat-unpushed/wt" ]; st $? 0 "a branch worktree with an unpushed commit is kept though its PR merged"
  st "$(gots sweep "keep  $D/orch/seat-unpushed/wt  unpushed")" 1 "naming unpushed"
  st "$(grep -c "update-ref -d refs/heads/fix/unpushed" "$D/log")" 0 "and its branch is not deleted"
  st "$(grep -c "$D/orch/seat-unpushed/wt update-ref --no-deref" "$D/log")" 0 "and no remove call for it (apply path)"
  st "$(gots sweep "summary -- eligible")" 1 "one summary line"

  # The same planted case under --dry-run: classify keeps it too, and says so.
  mkcase dryup; build dryup
  run dryup --dry-run --keep-dir "$W/dryup/ev" o/r
  st "$(gots dryup "keep  $W/dryup/orch/seat-unpushed/wt  unpushed")" 1 "dry-run: the unpushed worktree is kept (classify path)"
  st "$(gots dryup "remove  $W/dryup/orch/seat-onremote/wt  on-remote")" 1 "dry-run: and the on-remote one is named for removal"

  # A branch that moves after the read (a seat commits between the porcelain
  # read and the delete) survives: the delete is leased at the head the
  # classifier read, and a refused lease is reported, not retried.
  mkcase moved; build moved
  printf 'worktree %s/orch/seat-moved/wt\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/fix/moved\n\n' "$W/moved" >> "$W/moved/porcelain"
  printf '[{"state":"MERGED"}]\n' > "$W/moved/pr/fix_moved.json"
  mkdir -p "$W/moved/orch/seat-moved/wt" "$W/moved/live"
  printf 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' > "$W/moved/live/$(encpath refs/heads/fix/moved)"
  run moved --keep-dir "$W/moved/ev" o/r; st $? 0 "a branch moved after the read: rc 0 (fail-soft)"
  D="$W/moved"
  st "$(grep -cx "refs/heads/fix/moved" "$D/deleted")" 0 "the moved branch is not deleted"
  st "$(grep -c "FAILED to delete branch fix/moved" "$D/err")" 1 "and the refused delete is reported"
  st "$(grep -cx "refs/heads/fix/merged" "$D/deleted")" 1 "null control: the unmoved merged branch in the same run deletes"

  # A DETACHED worktree whose HEAD moves after the read (a seat commits on it:
  # its HEAD is the only ref holding that commit) is kept: the removal is
  # leased at the head the porcelain read (#3085 round 3).
  mkcase dmoved; build dmoved
  printf 'worktree %s/orch/seat-dmoved/wt\nHEAD 2222222222222222222222222222222222222223\ndetached\n\n' "$W/dmoved" >> "$W/dmoved/porcelain"
  mkdir -p "$W/dmoved/orch/seat-dmoved/wt" "$W/dmoved/live"
  printf 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' > "$W/dmoved/live/$(encpath "$W/dmoved/orch/seat-dmoved/wt")"
  age_old "$H3" "$W/dmoved/orch/seat-dmoved"
  run dmoved --keep-dir "$W/dmoved/ev" o/r; st $? 0 "a detached HEAD moved after the read: rc 0 (fail-soft)"
  D="$W/dmoved"
  [ -d "$D/orch/seat-dmoved/wt" ]; st $? 0 "the detached worktree whose HEAD moved is kept"
  st "$(grep -c "FAILED to remove worktree $D/orch/seat-dmoved/wt" "$D/err")" 1 "and the refused removal is reported"
  gone "$D/orch/seat-detached/wt"; st $? 0 "null control: the unmoved detached worktree in the same run is removed"

  # An ORPHANED seat (its wt a checkout this repository does not register: a
  # separate clone, or a worktree of another checkout) DETACHED at a merged
  # sha, whose HEAD moves after the read: the seat's commit is held by that
  # HEAD alone, so the rm -rf is leased at the head read (#3085 class C).
  mkcase ocmoved; build ocmoved
  D="$W/ocmoved"; mkdir -p "$D/live" "$D/head-of"
  for s in seat-orph-dmoved seat-orph-dstill; do
    mkdir -p "$D/orch/$s/wt"; printf 'HEAD\n' > "$D/branch-of/$(encpath "$D/orch/$s/wt")"
    printf '2222222222222222222222222222222222222222\n' > "$D/head-of/$(encpath "$D/orch/$s/wt")"
  done
  printf 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' > "$D/live/$(encpath "$D/orch/seat-orph-dmoved/wt")"
  age_old "$H3" "$D/orch/seat-orph-dmoved" "$D/orch/seat-orph-dstill"
  run ocmoved --keep-dir "$D/ev" o/r; st $? 0 "an orphan's detached HEAD moved after the read: rc 0 (fail-soft)"
  [ -d "$D/orch/seat-orph-dmoved/wt" ]; st $? 0 "the orphaned seat whose HEAD moved is kept"
  st "$(grep -c "FAILED to remove $D/orch/seat-orph-dmoved: its HEAD is no longer" "$D/err")" 1 "and the refused removal is reported"
  gone "$D/orch/seat-orph-dstill"; st $? 0 "null control: the unmoved detached orphan in the same run is removed"

  # A failed fetch closes the on-remote class; an unreadable lsof keeps what it would remove.
  mkcase nofetch; build nofetch; : > "$W/nofetch/fetchfail"
  run nofetch --keep-dir "$W/nofetch/ev" o/r
  [ -d "$W/nofetch/orch/seat-onremote/wt" ]; st $? 0 "failed fetch: the on-remote worktree is kept"
  st "$(gots nofetch "keep  $W/nofetch/orch/seat-onremote/wt  unmerged-head")" 1 "naming unmerged-head"
  mkcase nolsof; build nolsof; : > "$W/nolsof/lsofbroken"
  run nolsof --keep-dir "$W/nolsof/ev" o/r
  [ -d "$W/nolsof/orch/seat-onremote/wt" ]; st $? 0 "unreadable lsof: the on-remote worktree is kept"
  mkcase nops; build nops; : > "$W/nops/psbroken"
  run nops --keep-dir "$W/nops/ev" o/r
  [ -d "$W/nops/orch/seat-onremote/wt" ]; st $? 0 "unreadable ps: the on-remote worktree is kept"
  st "$(gots nolsof "keep  $W/nolsof/orch/seat-onremote/wt  cwd-unread")" 1 "naming cwd-unread"
  # The open-file listing alone unreadable (the cwd call answers): still kept.
  mkcase noopen; build noopen; : > "$W/noopen/lsofopenbroken"
  run noopen --keep-dir "$W/noopen/ev" o/r
  [ -d "$W/noopen/orch/seat-onremote/wt" ]; st $? 0 "unreadable open-file lsof, cwd lsof readable: the on-remote worktree is kept"
  st "$(gots noopen "keep  $W/noopen/orch/seat-onremote/wt  cwd-unread")" 1 "naming cwd-unread for the open-file listing"

  # Class C must keep the seat dir holding another LIVE worktree -- the header's
  # own keep rule, which classes A/B enforce via dispose_seat_dir. The orphan
  # wt is dead (unregistered, no readable branch: the pruned class); the nested
  # open-wt is REGISTERED with an OPEN pull request, so the same run prints
  # `keep .../open-wt open-pr` for it -- and must not rm -rf the seat out from
  # under it (#1288, the reviewer's attack 1 on #1287).
  mkcase nested-live; build nested-live
  printf 'worktree %s/orch/seat-orph-live/open-wt\nHEAD 3333333333333333333333333333333333333333\nbranch refs/heads/fix/open\n\n' "$W/nested-live" >> "$W/nested-live/porcelain"
  mkdir -p "$W/nested-live/orch/seat-orph-live/wt" "$W/nested-live/orch/seat-orph-live/open-wt"
  printf 'f\n' > "$W/nested-live/orch/seat-orph-live/wt/f"
  printf 'g\n' > "$W/nested-live/orch/seat-orph-live/open-wt/g"
  age_old "$H3" "$W/nested-live/orch/seat-orph-live"
  run nested-live --keep-dir "$W/nested-live/ev" o/r; st $? 0 "nested live worktree under an orphan: rc 0"
  D="$W/nested-live"
  st "$(gots nested-live "keep  $D/orch/seat-orph-live/open-wt  open-pr")" 1 "the nested worktree itself is kept naming open-pr"
  [ -d "$D/orch/seat-orph-live/open-wt" ]; st $? 0 "the nested LIVE worktree is not deleted"
  [ -d "$D/orch/seat-orph-live" ]; st $? 0 "and the seat dir holding it is kept"
  st "$(gots nested-live "keep  $D/orch/seat-orph-live  live-worktree ($D/orch/seat-orph-live/open-wt)")" 1 "kept naming the nested worktree"
  st "$(gots nested-live "(orphaned seat)")" 0 "never announced as an orphan removal (null control)"
  [ -f "$D/orch/seat-orph-live/open-wt/g" ]; st $? 0 "the live worktree's file is intact"

  # A failed evidence move must backstop class C as it backs A/B (a leftover
  # evidence dir is nondisposable-contents there): the keep-dir path is blocked
  # by a file, the mv fails, and the seat -- evidence still in place -- is kept
  # rather than rm -rf'd (#1288 secondary).
  mkcase failed-move; build failed-move
  mkdir -p "$W/failed-move/orch/seat-orph-fail/wt" "$W/failed-move/orch/seat-orph-fail/ev-9"
  printf 'f\n' > "$W/failed-move/orch/seat-orph-fail/wt/f"
  printf 'e\n' > "$W/failed-move/orch/seat-orph-fail/ev-9/ev.txt"
  printf 'blocker\n' > "$W/failed-move/ev/seat-orph-fail" # a file where mkdir must build the evidence root
  age_old "$H3" "$W/failed-move/orch/seat-orph-fail"
  run failed-move --keep-dir "$W/failed-move/ev" o/r; st $? 0 "failed evidence move in class C: rc 0"
  D="$W/failed-move"
  st "$(grep -c "FAILED to preserve evidence" "$D/err")" 1 "the move failure is reported"
  [ -d "$D/orch/seat-orph-fail/ev-9" ]; st $? 0 "the evidence stays in the seat dir"
  [ -d "$D/orch/seat-orph-fail" ]; st $? 0 "and the seat dir is kept"
  st "$(gots failed-move "keep  $D/orch/seat-orph-fail  nondisposable-contents (ev-9)")" 1 "kept naming nondisposable-contents"

  # Carries 0 and 1 (R10-CLOSEOUT-INSTRUMENTS). Seat branches map to their topic's
  # pull request on fix/<topic>; every removal arm keeps a worktree a process
  # stands in; plain repo copies in a seat of a merged topic go; the seats root
  # is a colon-separated list.
  mkcase seatb; build seatb
  D="$W/seatb"; mkdir -p "$D/orch2" "$D/live"
  PH() { printf '%040d' 0 | tr 0 "$1"; }
  seatwt() { # seat branch head: a registered branch worktree
    printf 'worktree %s/orch/seat-%s/wt\nHEAD %s\nbranch refs/heads/%s\n\n' "$D" "$1" "$3" "$2" >> "$D/porcelain"
    mkdir -p "$D/orch/seat-$1/wt"; age_old "$H3" "$D/orch/seat-$1"
  }
  seatwt tmerged work/merged-topic "$(PH 7)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_merged-topic.json"
  seatwt tclosed work/closed-topic "$(PH 7)"; printf '[{"state":"CLOSED"}]\n' > "$D/pr/fix_closed-topic.json"
  seatwt tunp scratch/unp-topic "$(PH 7)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_unp-topic.json"
  printf '1\n' > "$D/unpushed/$(encpath "$D/orch/seat-tunp/wt")"
  seatwt tcwd seat/cwd-topic "$(PH 7)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_cwd-topic.json"
  seatwt tdirty work/dirty-topic "$(PH 7)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_dirty-topic.json"
  printf 'M f\n' > "$D/status/$(encpath "$D/orch/seat-tdirty/wt")"
  seatwt topen work/open-topic "$(PH 7)"; printf '[{"state":"OPEN"}]\n' > "$D/pr/fix_open-topic.json"
  seatwt tnone work/none-topic "$(PH 7)"
  seatwt aholder fix/aholder "$(PH 2)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_aholder.json"
  printf 'worktree %s/orch/seat-bhold/wt\nHEAD 2222222222222222222222222222222222222223\ndetached\n\n' "$D" >> "$D/porcelain"
  mkdir -p "$D/orch/seat-bhold/wt/sub"; age_old "$H3" "$D/orch/seat-bhold"
  { printf '%s/orch/seat-tcwd/wt\n%s/orch/seat-aholder/wt\n%s/orch/seat-bhold/wt/sub\n' "$D" "$D" "$D"; cat "$D/cwds"; } > "$D/cwds.n"; mv "$D/cwds.n" "$D/cwds"
  # class E: plain copies. seat-copy (merged topic, two copies and a non-copy), seat-copyopen
  # (open topic), seat-copycwd (a process in a copy), seat-copyfresh (inside the age guard);
  # the second one lives in the second root.
  for sd in "$D/orch/seat-copy" "$D/orch/seat-copyopen" "$D/orch/seat-copycwd" "$D/orch2/seat-copy2"; do
    mkdir -p "$sd/mutant-1" "$sd/null-run" "$sd/notes"; printf 'x\n' > "$sd/mutant-1/f"
  done
  mkdir -p "$D/orch/seat-copy/head-tree/.git" "$D/orch/seat-copyfresh/mutant-1"
  for t in copy copycwd copy2; do printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_$t.json"; done
  printf '[{"state":"OPEN"}]\n' > "$D/pr/fix_copyopen.json"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_copyfresh.json"
  age_old "$H3" "$D/orch/seat-copy" "$D/orch/seat-copyopen" "$D/orch/seat-copycwd" "$D/orch2/seat-copy2"
  printf '%s/orch/seat-copycwd/null-run/deep\n' "$D" >> "$D/cwds"; mkdir -p "$D/orch/seat-copycwd/null-run/deep"
  age_old "$H3" "$D/orch/seat-copycwd"
  printf '%s:%s\n' "$D/orch" "$D/orch2" > "$D/seatsroot"
  run seatb --keep-dir "$D/ev" o/r; st $? 0 "the carry-0/1 sweep exits 0"
  gone "$D/orch/seat-tmerged/wt"; st $? 0 "carry 0: a seat branch whose fix/<topic> PR merged, clean and pushed: removed"
  gone "$D/orch/seat-tclosed/wt"; st $? 0 "carry 0: and one whose fix/<topic> PR is closed"
  st "$(grep -c "^git update-ref -d refs/heads/work/merged-topic " "$D/log")" 1 "its branch deleted, leased"
  [ -d "$D/orch/seat-tunp/wt" ]; st $? 0 "null control: one unpushed commit keeps the seat"
  st "$(gots seatb "keep  $D/orch/seat-tunp/wt  unpushed")" 1 "naming unpushed"
  [ -d "$D/orch/seat-tcwd/wt" ]; st $? 0 "null control: a live process cwd in a topic-merged seat keeps it"
  st "$(gots seatb "keep  $D/orch/seat-tcwd/wt  cwd-inside")" 1 "naming cwd-inside"
  [ -d "$D/orch/seat-tdirty/wt" ]; st $? 0 "null control: an uncommitted change keeps a topic-mapped seat"
  st "$(gots seatb "keep  $D/orch/seat-tdirty/wt  dirty-topic-seat")" 1 "naming dirty-topic-seat"
  [ -d "$D/orch/seat-topen/wt" ]; st $? 0 "null control: an open fix/<topic> PR keeps the seat"
  st "$(gots seatb "keep  $D/orch/seat-topen/wt  open-pr")" 1 "naming open-pr"
  st "$(gots seatb "keep  $D/orch/seat-tnone/wt  no-merged-pr")" 1 "null control: a seat branch with no topic PR at all stays no-merged-pr"
  [ -d "$D/orch/seat-aholder/wt" ]; st $? 0 "carry 1 (c): class A with a holder keeps"
  st "$(gots seatb "keep  $D/orch/seat-aholder/wt  cwd-inside")" 1 "naming cwd-inside"
  [ -d "$D/orch/seat-bhold/wt" ]; st $? 0 "carry 1 (a): class B with a holder keeps"
  st "$(gots seatb "keep  $D/orch/seat-bhold/wt  cwd-inside")" 1 "naming cwd-inside"
  gone "$D/orch/seat-detached/wt"; st $? 0 "carry 1 (b): class B without a holder removes (null control)"
  gone "$D/orch/seat-copy/mutant-1"; st $? 0 "carry 0: a plain mutant copy in a merged-topic seat: removed"
  gone "$D/orch/seat-copy/null-run"; st $? 0 "and a null copy"
  [ -d "$D/orch/seat-copy/head-tree/.git" ] && [ -d "$D/orch/seat-copy/notes" ]; st $? 0 "null control: a copy with a .git, and a directory not named like a copy, stay"
  gone "$D/orch2/seat-copy2/mutant-1"; st $? 0 "a seat under the second root of the list is collected"
  [ -d "$D/orch/seat-copyopen/mutant-1" ]; st $? 0 "null control: copies of an open topic stay"
  st "$(gots seatb "keep  $D/orch/seat-copyopen  copies-unmerged-topic")" 1 "naming copies-unmerged-topic"
  [ -d "$D/orch/seat-copycwd/null-run" ]; st $? 0 "null control: a process cwd in a copy keeps it"
  gone "$D/orch/seat-copycwd/mutant-1"; st $? 0 "while the other copy of that seat goes"
  [ -d "$D/orch/seat-copyfresh/mutant-1" ]; st $? 0 "null control: a seat modified within the age guard keeps its copies"

  # --dry-run over a rebuilt fixture: identical decisions, nothing moved.
  mkcase dry; build dry
  run dry --dry-run --keep-dir "$W/dry/ev" o/r; st $? 0 "--dry-run exits 0"
  D="$W/dry"
  st "$(grep -c "update-ref --no-deref -d HEAD" "$D/log")" 0 "removes no worktree"
  st "$(grep -c "^git update-ref -d" "$D/log")" 0 "deletes no branch"
  [ -d "$D/orch/seat-merged/wt" ] && [ -d "$D/orch/seat-merged" ]; st $? 0 "leaves the merged seat on disk"
  [ -d "$D/orch/seat-detached/evidence-run12" ]; st $? 0 "moves no evidence"
  st "$(gots dry "remove  $D/orch/seat-merged/wt")" 1 "and says what would go"
  st "$(gots dry "keep  $D/orch/seat-open/wt  open-pr")" 1 "and what is kept, with the reason"

  # No gh: notice, rc 0, nothing removed.
  mkcase noauth; build noauth; : > "$W/noauth/noauth"
  run noauth --keep-dir "$W/noauth/ev" o/r; st $? 0 "unauthenticated gh: rc 0 (fail-soft)"
  st "$(grep -c "gh missing or unauthenticated" "$W/noauth/out")" 1 "a notice, not a refusal"
  st "$(grep -c "update-ref --no-deref -d HEAD" "$W/noauth/log")" 0 "and nothing removed"
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
[ -n "$REPO" ] || die "usage: worktree_gc.sh [--dry-run] [--strict] [--keep-dir <evidence-destination, NOT a protect list>] <owner/repo>"
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

# One fetch, so "on a remote ref" and "merged" are read at the remote's tip. A
# failed fetch (offline, no auth) keeps the on-remote class closed.
FETCH_OK=0
git fetch --prune origin >/dev/null 2>&1 && FETCH_OK=1
ORIGIN_MAIN_SHA=$(git rev-parse origin/main 2>/dev/null || printf '')

# state: open | merged | closed | none | error -- from the API, never from the local
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
print("open" if "OPEN" in s else ("merged" if "MERGED" in s else ("closed" if "CLOSED" in s else "none")))'
}

# A merged pull request's head is a PROPER ancestor of origin/main under this
# repository's merge method; the tip itself is a seat reading live main.
head_is_merged_ancestor() {
  [ -n "$ORIGIN_MAIN_SHA" ] || return 1
  [ "$1" = "$ORIGIN_MAIN_SHA" ] && return 1
  git merge-base --is-ancestor "$1" origin/main 2>/dev/null
}

# Commits of the worktree's HEAD that no remote-tracking ref has: the unpushed
# work a merged PR of the same branch name says nothing about. Prints a number,
# or "?" when git cannot say.
unpushed_of() { # wt-path
  local n
  n=$(git -C "$1" rev-list --count HEAD --not --remotes 2>/dev/null) || { printf '?'; return; }
  case "$n" in ''|*[!0-9]*) printf '?' ;; *) printf '%s' "$n" ;; esac
}

# 0 iff the fetch worked and a remote-tracking ref or a tag contains the sha.
head_on_remote() {
  [ "$FETCH_OK" -eq 1 ] || return 1
  [ -n "$ORIGIN_MAIN_SHA" ] && [ "$1" = "$ORIGIN_MAIN_SHA" ] && return 1   # a seat reading live main
  [ -n "$(git for-each-ref --count=1 --contains "$1" --format='%(refname)' refs/remotes refs/tags 2>/dev/null)" ]
}

# What holds a worktree besides a cwd: 0 nothing, 1 a live process holds it
# (names the way in HELD_WAY: cwd-inside, argv-inside, open-file or pidfile-live),
# 2 lsof or ps is unreadable. A run reaching a checkout by `git -C`, `--checkout`
# or a script path has its cwd elsewhere, so argv and open files count as well.
HELD_WAY=""
cwd_inside() { # real path of a worktree
  local out p="$1" f pid
  command -v lsof >/dev/null 2>&1 || return 2
  out=$(lsof -a -d cwd -Fn 2>/dev/null) || return 2
  [ -n "$out" ] || return 2
  if printf '%s\n' "$out" | awk -v p="$p" 'substr($0,1,1)=="n" { d=substr($0,2); if (d==p || index(d, p "/")==1) f=1 } END { exit f ? 0 : 1 }'; then
    HELD_WAY=cwd-inside; return 1
  fi
  out=$(ps -eo args= 2>/dev/null) || return 2
  if printf '%s\n' "$out" | awk -v p="$p" '{ for (i=1;i<=NF;i++) { a=$i; k=index(a, p); if (k>0) { t=substr(a, k+length(p), 1); if (t=="" || t=="/" || t=="\"" || t=="\x27" || t==":" || t==",") f=1 } } } END { exit f ? 0 : 1 }'; then
    HELD_WAY=argv-inside; return 1
  fi
  out=$(lsof -Fn 2>/dev/null) || return 2
  if printf '%s\n' "$out" | awk -v p="$p" 'substr($0,1,1)=="n" { d=substr($0,2); if (d==p || index(d, p "/")==1) f=1 } END { exit f ? 0 : 1 }'; then
    HELD_WAY=open-file; return 1
  fi
  for f in "$p/train.pid" "$p"/*.lock "$p"/.*.lock; do
    [ -f "$f" ] || continue
    pid=$(head -c 32 "$f" 2>/dev/null | tr -dc '0-9')
    kill -0 "$pid" 2>/dev/null && { HELD_WAY=pidfile-live; return 1; }
  done
  return 0
}

# 0 when no live process holds the worktree and it may go; otherwise prints the
# keep line (HELD_WAY, or cwd-unread when lsof or ps cannot say) and returns 1.
# Every removal arm asks it: a worktree a process stands in, reads through
# `git -C`, or has open goes on no arm.
cwd_free() { # wt-path real-path
  cwd_inside "$2"
  case $? in
    1) printf 'keep  %s  %s\n' "$1" "$HELD_WAY"; KEPT_N=$((KEPT_N+1)); return 1 ;;
    2) printf 'keep  %s  cwd-unread\n' "$1"; KEPT_N=$((KEPT_N+1)); return 1 ;;
  esac
  return 0
}

# A seat branch (`work/<topic>`, `scratch/<topic>`, `seat/<topic>`) never has a
# pull request of its own: its pull request sits on `fix/<topic>`. Prints the
# state of that one, or `none` for any other branch.
topic_pr_state() { # branch
  case "$1" in
    work/?*|scratch/?*|seat/?*) pr_state_of "fix/${1#*/}" ;;
    *) printf 'none' ;;
  esac
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

# The registered worktree this run did not remove that sits under seat-dir
# (at it or beneath it), printed when one exists and empty otherwise -- the
# keep line names it, so the reason reaches the seat that owns it.
live_under() {
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
        print(wt); break
PY
}

# 0 iff a registered worktree this run did not remove sits under seat-dir.
another_live_under() { [ -n "$(live_under "$1")" ]; }

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
  local root
  for root in ${SEATS_REALS[@]+"${SEATS_REALS[@]}"}; do
    case "$1" in
      "$root"/*/wt) dirname "$1"; return 0 ;;
    esac
  done
  printf ''
}

# WORKTREE_GC_SEATS_ROOT is a colon-separated list: seats live under one
# directory per round (~/hpo-seats/<round>), not under one fixed root.
SEATS_REALS=()
IFS=: read -r -a SEATS_LIST <<<"$SEATS_ROOT"
for r in ${SEATS_LIST[@]+"${SEATS_LIST[@]}"}; do
  [ -n "$r" ] && SEATS_REALS+=("$(realpath_of "$r" 2>/dev/null || printf '%s' "$r")")
done
SEATS_ONE=""
KEEP_REAL=$(realpath_of "$KEEP_DIR" 2>/dev/null || printf '%s' "$KEEP_DIR")
ELIGIBLE=0; REMOVED_N=0; KEPT_N=0
HANDLED_SEATS=""

print_uncommitted() { # wt-path: the orchestrator's stop-a-seat check
  printf 'uncommitted  %s\n' "$1"
  git -C "$1" status --porcelain 2>/dev/null
  git -C "$1" diff 2>/dev/null
}

remove_worktree() { # wt-path head [reason]
  # Leased at the head the porcelain read, for both classes: the worktree's
  # own HEAD is deleted with that old value (`update-ref --no-deref -d HEAD
  # <head>`, atomic in git's ref transaction). A seat that committed after the
  # read moved HEAD, the lease refuses, and the worktree stays with its
  # commit; for a detached worktree that HEAD is the only ref holding it. Once
  # HEAD is gone no commit can land there, so the tree is deleted and its
  # admin entry pruned (`git worktree remove` refuses a worktree with no HEAD).
  # Returns 1, the worktree kept, on a refused lease.
  if [ -n "${3:-}" ]; then printf 'remove  %s  %s\n' "$1" "$3"; else printf 'remove  %s\n' "$1"; fi
  if [ "$DRY" -eq 1 ]; then
    printf '%s\n' "$(realpath_of "$1" 2>/dev/null || printf '%s' "$1")" >>"$REMOVED_FILE"
    return 0
  fi
  if [ -z "${2:-}" ] || ! git -C "$1" update-ref --no-deref -d HEAD "$2" 2>/dev/null; then
    printf 'worktree_gc: FAILED to remove worktree %s: its HEAD is no longer %s, kept\n' "$1" "${2:-<unread>}" >&2
    KEPT_N=$((KEPT_N+1)); return 1
  fi
  printf '%s\n' "$(realpath_of "$1" 2>/dev/null || printf '%s' "$1")" >>"$REMOVED_FILE"
  if rm -rf "$1" && git worktree prune; then
    printf 'removed  %s\n' "$1"; REMOVED_N=$((REMOVED_N+1))
  else
    printf 'worktree_gc: FAILED to remove worktree %s\n' "$1" >&2
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
  local real state seat st_out st_rc up onremote topic
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
    topic=0
    case "$state" in
      open) printf 'keep  %s  open-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
      merged) ;;
      none|closed)
        # A seat branch's pull request sits on fix/<topic>; a merged or closed
        # one there frees the seat, on the stricter terms below.
        case "$(topic_pr_state "$branch")" in
          merged|closed) topic=1 ;;
          open) printf 'keep  %s  open-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
          *) printf 'keep  %s  no-merged-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
        esac ;;
      *) printf 'keep  %s  gh-error\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
    esac
    up=$(unpushed_of "$wt")
    if [ "$up" != 0 ]; then
      printf 'keep  %s  unpushed (%s commit(s) on no remote ref)\n' "$wt" "$up"; KEPT_N=$((KEPT_N+1)); return 0
    fi
    st_out=$(git -C "$wt" status --porcelain 2>/dev/null); st_rc=$?
    if [ "$topic" -eq 1 ] && { [ -n "$st_out" ] || [ "$st_rc" -ne 0 ]; }; then
      # Not proved merged by its own branch: uncommitted work is on no remote.
      printf 'keep  %s  dirty-topic-seat\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0
    fi
    cwd_free "$wt" "$real" || return 0
    ELIGIBLE=$((ELIGIBLE+1))
    if [ -n "$st_out" ] || [ "$st_rc" -ne 0 ]; then print_uncommitted "$wt"; fi
    remove_worktree "$wt" "$head" || return 0
    if [ "$DRY" -eq 0 ]; then
      # Leased at the head the porcelain read: a seat that commits after the
      # unpushed read moves the branch, the lease refuses, and the commit stays
      # on its branch. `branch -D` deleted wherever the ref then pointed.
      { [ -n "$head" ] && git update-ref -d "refs/heads/$branch" "$head" 2>/dev/null; } \
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
  onremote=0
  if ! head_is_merged_ancestor "$head"; then
    if head_on_remote "$head"; then onremote=1
    else printf 'keep  %s  unmerged-head\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0; fi
  fi
  if recently_modified "$real" "$MIN_AGE_DETACHED"; then
    printf 'keep  %s  young\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0
  fi
  cwd_free "$wt" "$real" || return 0
  ELIGIBLE=$((ELIGIBLE+1))
  if [ "$onremote" -eq 1 ]; then remove_worktree "$wt" "$head" on-remote || return 0
  else remove_worktree "$wt" "$head" || return 0; fi
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
# Drained, never `grep -q`: under pipefail a SIGPIPE'd writer reads as "not
# handled" and the seat is judged a second time (R9-RCA-prepr-tmp).
handled_seat() { printf '%b' "$HANDLED_SEATS" | grep -x "$1" >/dev/null; }

C_SEATS=""
for SEATS_ONE in ${SEATS_REALS[@]+"${SEATS_REALS[@]}"}; do
  [ -d "$SEATS_ONE" ] || continue
  for seat in "$SEATS_ONE"/*/; do
    [ -d "$seat" ] || continue
    seat="${seat%/}"
    seat_real=$(realpath_of "$seat")
    case "$seat_real" in "$KEEP_REAL"|"$KEEP_REAL"/*) continue ;; esac
    handled_seat "$seat_real" && continue
    [ -d "$seat/wt" ] || { printf 'keep  %s  no-wt\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue; }
    is_registered "$(realpath_of "$seat/wt")" && continue
    if recently_modified "$seat_real" "$ORPHAN_AGE"; then
      printf 'keep  %s  fresh\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue
    fi
    # The orphan's own HEAD, read once: the rm -rf below is leased at it, as
    # remove_worktree's is, because a commit a seat makes after this read is
    # held by that HEAD alone in an unregistered checkout (#3085 class C).
    wt_branch=""; ohead=""
    if wt_branch=$(git -C "$seat_real/wt" rev-parse --abbrev-ref HEAD 2>/dev/null); then
      ohead=$(git -C "$seat_real/wt" rev-parse HEAD 2>/dev/null) || ohead=""
      if [ -z "$ohead" ]; then
        printf 'keep  %s  unreadable-head\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue
      fi
    fi
    if [ -n "$wt_branch" ] && [ "$wt_branch" != "HEAD" ]; then
      state=$(pr_state_of "$wt_branch")
      case "$state" in
        merged) ;;
        *) printf 'keep  %s  unmerged-branch\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue ;;
      esac
      if [ "$(unpushed_of "$seat_real/wt")" != 0 ]; then
        printf 'keep  %s  unpushed\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue
      fi
    elif [ "$wt_branch" = "HEAD" ]; then
      # A detached orphan goes only on a merged head whose sha still resolves.
      if ! head_is_merged_ancestor "$ohead"; then
        printf 'keep  %s  unmerged-head\n' "$seat"; KEPT_N=$((KEPT_N+1)); continue
      fi
    fi
    # The header's keep rule classes A/B enforce via dispose_seat_dir: a seat
    # directory holding another live worktree is kept, or the rm -rf below
    # takes the nested worktree with it in the same run that printed
    # `keep ... open-pr` for it (#1288).
    nested=$(live_under "$seat_real")
    if [ -n "$nested" ]; then
      printf 'keep  %s  live-worktree (%s)\n' "$seat" "$nested"; KEPT_N=$((KEPT_N+1)); continue
    fi
    ELIGIBLE=$((ELIGIBLE+1))
    C_SEATS="$C_SEATS$seat_real\n"
    printf 'remove  %s (orphaned seat)\n' "$seat"
    preserve_evidence "$seat_real"
    if [ "$DRY" -eq 0 ]; then
      # A failed evidence move leaves the directory behind; the seat is kept
      # under dispose_seat_dir's own nondisposable-contents rule rather than
      # rm -rf'd past evidence a verdict can still reach (#1288).
      for e in "$seat_real"/evidence* "$seat_real"/ev-*; do
        [ -d "$e" ] || continue
        printf 'keep  %s  nondisposable-contents (%s)\n' "$seat" "$(basename "$e")"
        KEPT_N=$((KEPT_N+1)); continue 2
      done
      # The lease: HEAD deleted at the value read, atomically; a moved HEAD
      # refuses and the seat stays with its commit. A wt git cannot read has
      # no HEAD to hold a commit, and goes unleased.
      if [ -n "$ohead" ] && ! git -C "$seat_real/wt" update-ref --no-deref -d HEAD "$ohead" 2>/dev/null; then
        printf 'worktree_gc: FAILED to remove %s: its HEAD is no longer %s, kept\n' "$seat" "$ohead" >&2
        KEPT_N=$((KEPT_N+1)); continue
      fi
      rm -rf "$seat_real" && printf 'removed  %s\n' "$seat" && REMOVED_N=$((REMOVED_N+1)) \
        || printf 'worktree_gc: FAILED to remove %s\n' "$seat" >&2
    fi
  done
done

# --- class E: plain repo copies in a seat dir ---------------------------------
# A mutant, null or head tree a seat copied out of the repository carries no
# .git, so classes A-C never see it and a seat directory holding one is kept as
# nondisposable-contents. It goes when the seat's topic (the directory name less
# a leading `seat-`) has a MERGED pull request on `fix/<topic>`, nothing under
# the seat was modified within the orphan age, no live worktree remains beneath
# the seat and no process has its cwd inside the copy.
for SEATS_ONE in ${SEATS_REALS[@]+"${SEATS_REALS[@]}"}; do
  [ -d "$SEATS_ONE" ] || continue
  for seat in "$SEATS_ONE"/*/; do
    [ -d "$seat" ] || continue
    seat_real=$(realpath_of "${seat%/}")
    case "$seat_real" in "$KEEP_REAL"|"$KEEP_REAL"/*) continue ;; esac
    printf '%b' "$C_SEATS" | grep -x "$seat_real" >/dev/null && continue
    copies=()
    for cp in "$seat_real"/*/; do
      cp="${cp%/}"
      [ -d "$cp" ] && [ ! -e "$cp/.git" ] || continue
      case "$(basename "$cp")" in
        wt) continue ;;
        *mutant*|*null*|*head*) copies+=("$cp") ;;
      esac
    done
    [ "${#copies[@]}" -gt 0 ] || continue
    topic=$(basename "$seat_real"); topic=${topic#seat-}
    if [ "$(pr_state_of "fix/$topic")" != merged ]; then
      printf 'keep  %s  copies-unmerged-topic\n' "$seat_real"; KEPT_N=$((KEPT_N+1)); continue
    fi
    if recently_modified "$seat_real" "$ORPHAN_AGE"; then
      printf 'keep  %s  fresh\n' "$seat_real"; KEPT_N=$((KEPT_N+1)); continue
    fi
    nested=$(live_under "$seat_real")
    if [ -n "$nested" ]; then
      printf 'keep  %s  live-worktree (%s)\n' "$seat_real" "$nested"; KEPT_N=$((KEPT_N+1)); continue
    fi
    for cp in ${copies[@]+"${copies[@]}"}; do
      cwd_free "$cp" "$cp" || continue
      ELIGIBLE=$((ELIGIBLE+1))
      printf 'remove  %s (plain copy)\n' "$cp"
      if [ "$DRY" -eq 0 ]; then
        rm -rf "$cp" && printf 'removed  %s\n' "$cp" && REMOVED_N=$((REMOVED_N+1)) \
          || printf 'worktree_gc: FAILED to remove %s\n' "$cp" >&2
      fi
    done
  done
done

# --- class D: stale venvs ----------------------------------------------------
venv_referenced() { # vdir -> 0 when a live worktree symlinks into it (depth <= 2)
  python3 - "$1" "$REMOVED_FILE" "$LIVE_FILE" <<'PY'
import os, sys
vdir = os.path.realpath(sys.argv[1])
def rd(p):
    try: return [l.rstrip("\n") for l in open(p) if l.strip()]
    except OSError: return []
removed = set(rd(sys.argv[2]))
def links_to(dp, names):
    for n in names:
        p = os.path.join(dp, n)
        try:
            # os.walk lists a symlink to a directory under dirnames, so both
            # lists are scanned; a venv link lives at the worktree root and
            # points AT the venv directory, not inside it.
            rp = os.path.realpath(p)
            if os.path.islink(p) and (rp == vdir or rp.startswith(vdir + os.sep)):
                return True
        except OSError: pass
    return False
for wt in rd(sys.argv[3]):
    if wt in removed: continue
    for dp, dns, fns in os.walk(wt):
        if os.path.relpath(dp, wt).count(os.sep) >= 2:
            dns[:] = []
        if links_to(dp, fns) or links_to(dp, dns):
            sys.exit(0)
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
