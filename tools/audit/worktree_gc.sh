#!/bin/bash
# Collect leftover detached worktrees. Dry-run by default.
#
# WHY THIS EXISTS. Review seats check out a detached worktree at a head SHA,
# fixers use a branch worktree, and the orchestrator adds throwaways to read
# main. Nothing removes them. `git worktree list` then stops answering "what
# is live", and the standing rule — do not delete other sessions' uncommitted
# work — is a judgement a script can replace, if it is conservative enough
# that a collector which can delete another session's work is worse than none.
#
# A worktree is listed for delete only when ALL of these hold:
#
#   1. detached (`git worktree list --porcelain` shows `detached`, no `branch`)
#   2. clean — `git status --porcelain` empty, including untracked
#   3. its HEAD is not the head of any open pull request
#   4. older than 60 minutes by the worktree directory's mtime
#
# A branch worktree is never touched, whatever its state. The main checkout
# is never touched either: `git worktree remove` cannot take it, and it is
# a session's claim even when detached.
#
#   tools/audit/worktree_gc.sh            # report; delete nothing
#   tools/audit/worktree_gc.sh --apply    # delete the listed ones
#   tools/audit/worktree_gc.sh --self-test
#
# Criterion 3's listing of open heads is injected via WORKTREE_GC_OPEN_HEADS
# (newline-separated full SHAs) when a test or a seat already has the set.
# Otherwise the script asks GitHub. The invocation lives here so a policy
# file is not the place that names it.
#
set -uo pipefail

MIN_AGE="${WORKTREE_GC_MIN_AGE:-3600}"

# --- self-test ---------------------------------------------------------------
# The issue's acceptance is a property, not a live-repo walk: a detached,
# clean worktree whose HEAD is an open pull request's head is kept with
# criterion 3, before and after --apply. The other three keep criteria and
# the one delete path are driven the same way, in a throwaway repo, so this
# file never needs a gate hook and never walks the caller's worktrees.
if [ "${1:-}" = "--self-test" ]; then
  SCRIPT=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
  TMP=$(mktemp -d)
  # The collector itself must not see GIT_DIR from this process. The trap
  # removes the fixture repo; `git worktree prune` is unnecessary because
  # the common dir dies with TMP.
  cleanup() { rm -rf "$TMP"; }
  trap cleanup EXIT
  st_pass=0; st_fail=0
  st() { if [ "$1" = 0 ]; then st_pass=$((st_pass+1)); printf '  ok   %s\n' "$2";
         else st_fail=$((st_fail+1)); printf '  FAIL %s\n' "$2"; fi; }

  repo="$TMP/repo"
  mkdir -p "$repo"
  git init -b main "$repo" >/dev/null
  git -C "$repo" config user.email test@test
  git -C "$repo" config user.name test
  printf 'a\n' > "$repo/f"
  git -C "$repo" add f
  git -C "$repo" commit -q -m init
  sha_pr=$(git -C "$repo" rev-parse HEAD)
  printf 'b\n' >> "$repo/f"
  git -C "$repo" add f
  git -C "$repo" commit -q -m two
  sha_other=$(git -C "$repo" rev-parse HEAD)

  git -C "$repo" worktree add -b other "$TMP/branch" "$sha_other" >/dev/null 2>&1
  printf 'dirty\n' > "$TMP/branch/extra"

  git -C "$repo" worktree add --detach "$TMP/dirty" "$sha_other" >/dev/null 2>&1
  printf 'dirty\n' > "$TMP/dirty/extra"

  git -C "$repo" worktree add --detach "$TMP/untracked" "$sha_other" >/dev/null 2>&1
  printf 'u\n' > "$TMP/untracked/u"

  git -C "$repo" worktree add --detach "$TMP/prhead" "$sha_pr" >/dev/null 2>&1
  git -C "$repo" worktree add --detach "$TMP/gone" "$sha_other" >/dev/null 2>&1
  git -C "$repo" worktree add --detach "$TMP/young" "$sha_other" >/dev/null 2>&1

  # Age is a property of the directory mtime. Set the "old" ones two hours
  # back; leave young at "now" so criterion 4 is the only thing that keeps it.
  python3 - "$TMP/branch" "$TMP/dirty" "$TMP/untracked" "$TMP/prhead" "$TMP/gone" <<'PY'
import os, sys, time
t = time.time() - 7200
for d in sys.argv[1:]:
    os.utime(d, (t, t))
PY

  run_gc() {
    # Isolation: run from the fixture repo so --apply cannot see the
    # caller's worktrees. The open-head list is the test's, not GitHub's.
    ( cd "$repo" && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_COMMON_DIR \
        WORKTREE_GC_OPEN_HEADS="$1" \
        bash "$SCRIPT" ${2:-} ) 2>"$TMP/err"
  }

  out=$(run_gc "$sha_pr") || true
  printf '%s\n' "$out" > "$TMP/dry.txt"

  printf '%s\n' "$out" | grep -qE "keep[[:space:]]+$TMP/branch[[:space:]]+1$" \
    || printf '%s\n' "$out" | grep -qE "keep[[:space:]].*/branch[[:space:]]+1$"
  st $? "a branch worktree is kept with criterion 1, even when dirty and old"

  printf '%s\n' "$out" | grep -qE "keep[[:space:]].*/dirty[[:space:]]+2$"
  st $? "a dirty detached worktree is kept with criterion 2"

  printf '%s\n' "$out" | grep -qE "keep[[:space:]].*/untracked[[:space:]]+2$"
  st $? "untracked files count as dirty (criterion 2)"

  printf '%s\n' "$out" | grep -qE "keep[[:space:]].*/prhead[[:space:]]+3$"
  st $? "detached, clean, open-PR head is kept with criterion 3 (null control)"

  printf '%s\n' "$out" | grep -qE "keep[[:space:]].*/young[[:space:]]+4$"
  st $? "a young detached clean worktree is kept with criterion 4"

  printf '%s\n' "$out" | grep -qE "delete[[:space:]].*/gone$"
  st $? "detached, clean, old, not an open-PR head is listed for delete"

  printf '%s\n' "$out" | grep -qE "keep[[:space:]].*/repo[[:space:]]+(1|main)$"
  st $? "the main checkout is never listed for delete"

  [ -d "$TMP/gone" ]
  st $? "dry-run does not delete (gone still on disk)"

  # Mutation of criterion 3: an empty open-head list must flip the null
  # control from keep-3 to delete. That is the break the body names.
  mut=$(run_gc "") || true
  printf '%s\n' "$mut" | grep -qE "delete[[:space:]].*/prhead$"
  st $? "clearing the open-head list flips the null control to delete (mutation)"

  # --apply must remove only `gone`, and must leave the null control in place.
  apply=$(run_gc "$sha_pr" --apply) || true
  printf '%s\n' "$apply" > "$TMP/apply.txt"
  [ ! -d "$TMP/gone" ]
  st $? "--apply deletes the one listed worktree"
  [ -d "$TMP/prhead" ]
  st $? "--apply leaves the open-PR-head worktree on disk (null control)"
  [ -d "$TMP/branch" ] && [ -d "$TMP/dirty" ] && [ -d "$TMP/untracked" ] && [ -d "$TMP/young" ]
  st $? "--apply does not touch a worktree a criterion kept"

  after=$(run_gc "$sha_pr") || true
  printf '%s\n' "$after" | grep -qE "keep[[:space:]].*/prhead[[:space:]]+3$"
  st $? "after --apply, the null control is still kept with criterion 3"
  if printf '%s\n' "$after" | grep -qE "delete[[:space:]].*/gone$"; then
    st 1 "after --apply, the deleted worktree is no longer listed"
  else
    st 0 "after --apply, the deleted worktree is no longer listed"
  fi

  # Refuse to delete when open heads cannot be listed: fail closed.
  if ( cd "$repo" && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_COMMON_DIR \
         -u WORKTREE_GC_OPEN_HEADS \
         WORKTREE_GC_OPEN_HEADS_CMD="false" \
         bash "$SCRIPT" --apply >"$TMP/failclosed.txt" 2>"$TMP/failclosed.err" ); then
    st 1 "cannot-list-heads refuses --apply"
  else
    st 0 "cannot-list-heads refuses --apply"
  fi
  [ -d "$TMP/prhead" ] && [ -d "$TMP/young" ]
  st $? "cannot-list-heads deletes nothing"

  printf '\n%s passed, %s failed\n' "$st_pass" "$st_fail"
  [ "$st_fail" -eq 0 ] || exit 2
  exit 0
fi

# --- production --------------------------------------------------------------
APPLY=0
case "${1:-}" in
  "") ;;
  --apply) APPLY=1 ;;
  *) printf 'usage: %s [--apply|--self-test]\n' "$0" >&2; exit 2 ;;
esac

# Do not inherit a caller's GIT_DIR: that would make `git worktree list`
# describe the wrong repository, or none.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR

cd "$(git rev-parse --show-toplevel)" || exit 2

here=$(python3 -c "import os; print(os.path.realpath(os.getcwd()))")

mtime_of() {
  python3 -c "import os,sys; print(int(os.stat(sys.argv[1]).st_mtime))" "$1"
}

realpath_of() {
  python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$1"
}

now="${WORKTREE_GC_NOW:-$(date +%s)}"

list_open_heads() {
  if [ -n "${WORKTREE_GC_OPEN_HEADS+x}" ]; then
    printf '%s\n' "$WORKTREE_GC_OPEN_HEADS"
    return 0
  fi
  if [ -n "${WORKTREE_GC_OPEN_HEADS_CMD:-}" ]; then
    sh -c "$WORKTREE_GC_OPEN_HEADS_CMD"
    return $?
  fi
  # Production listing. Named here, not in a brief or a contract.
  gh pr list --state open --limit 1000 --json headRefOid --jq '.[].headRefOid'
}

heads_file=$(mktemp)
apply_rc=0
trap 'rm -f "$heads_file"' EXIT
if ! list_open_heads >"$heads_file"; then
  printf 'cannot list open pull-request heads; refusing to delete\n' >&2
  exit 2
fi

is_open_head() {
  awk -v h="$1" 'BEGIN{n=0} $0==h {n=1} END{exit n?0:1}' "$heads_file"
}

# First porcelain record is the main checkout. Never delete it.
main_wt=""
wt=""
head=""
has_branch=0
detached=0
locked=0

flush() {
  [ -n "$wt" ] || return 0
  classify
  wt=""; head=""; has_branch=0; detached=0; locked=0
}

classify() {
  local status age mt real
  real=$(realpath_of "$wt" 2>/dev/null || printf '%s' "$wt")

  if [ -z "$main_wt" ]; then
    main_wt="$real"
  fi

  if [ "$real" = "$main_wt" ]; then
    if [ "$has_branch" -eq 1 ]; then
      printf 'keep  %s  1\n' "$wt"
    else
      printf 'keep  %s  main\n' "$wt"
    fi
    return 0
  fi
  if [ "$real" = "$here" ]; then
    # Running from inside a worktree does not make it collectable.
    if [ "$has_branch" -eq 1 ] || [ "$detached" -eq 0 ]; then
      printf 'keep  %s  1\n' "$wt"
    else
      printf 'keep  %s  current\n' "$wt"
    fi
    return 0
  fi
  if [ "$locked" -eq 1 ]; then
    printf 'keep  %s  locked\n' "$wt"
    return 0
  fi
  if [ ! -d "$wt" ]; then
    printf 'keep  %s  missing\n' "$wt"
    return 0
  fi

  # 1. A branch worktree is never touched, whatever its state.
  if [ "$has_branch" -eq 1 ] || [ "$detached" -eq 0 ]; then
    printf 'keep  %s  1\n' "$wt"
    return 0
  fi

  # 2. Dirty, including untracked. A status we cannot run is dirty: we
  # cannot prove the other session left nothing behind.
  if ! status=$(git -C "$wt" status --porcelain 2>/dev/null); then
    printf 'keep  %s  2\n' "$wt"
    return 0
  fi
  if [ -n "$status" ]; then
    printf 'keep  %s  2\n' "$wt"
    return 0
  fi

  # 3. HEAD is an open pull request's head — a review checkout.
  if [ -n "$head" ] && is_open_head "$head"; then
    printf 'keep  %s  3\n' "$wt"
    return 0
  fi

  # 4. Younger than an hour by the directory mtime.
  if ! mt=$(mtime_of "$wt" 2>/dev/null); then
    printf 'keep  %s  4\n' "$wt"
    return 0
  fi
  age=$((now - mt))
  if [ "$age" -lt "$MIN_AGE" ]; then
    printf 'keep  %s  4\n' "$wt"
    return 0
  fi

  printf 'delete  %s\n' "$wt"
  if [ "$APPLY" -eq 1 ]; then
    if git worktree remove -- "$wt"; then
      printf 'removed  %s\n' "$wt"
    else
      printf 'failed  %s\n' "$wt" >&2
      apply_rc=1
    fi
  fi
}

while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in
    worktree\ *)
      flush
      wt="${line#worktree }"
      ;;
    HEAD\ *)
      head="${line#HEAD }"
      ;;
    branch\ *)
      has_branch=1
      ;;
    detached)
      detached=1
      ;;
    locked*)
      locked=1
      ;;
    "")
      flush
      ;;
  esac
done < <(git worktree list --porcelain)
flush
exit "$apply_rc"
