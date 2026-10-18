#!/bin/bash
# delivery_row.sh -- a pull request's own delivery row, written and committed
# by one function for every instrument that lands one (delivery-status-tracking.md).
#
#   . tools/audit/seat/delivery_row.sh     (open_pr.sh, update_pr.sh, bus.sh)
#   tools/audit/seat/delivery_row.sh --self-test
#
# THE ROW'S HOME (#1990's RCA, round 3). Rows are written to
# dev/programme/delivery/ only, never to the retired delivery directory, and
# the directory is made when a branch predates the lift. `bus.sh dispatch`
# refuses a head without its row, so the writer and that check key on this
# one ROW_DIR.
#
# WHY ensure_row EXISTS (2026-10-18, #2390 and #2391). open_pr.sh commits the
# row only after its first push opened the pull request, then pushes again; when
# that second push's prepr refused, the pull request existed with no row, and
# update_pr.sh, which never wrote one, left it so -- every later dispatch was
# refused. update_pr.sh now calls ensure_row, which adds the row when the head
# lacks it and adds nothing when the head carries it, with open_pr.sh's own
# commit identity and message, because both call commit_row.
# Sourcing defines functions and ROW_DIR only; it runs nothing.
ROW_DIR=dev/programme/delivery
write_row() { # <worktree> <N> <line>; prints the repo-relative path written
  mkdir -p "$1/$ROW_DIR" && printf '%s\n' "$3" > "$1/$ROW_DIR/$2.md" && echo "$ROW_DIR/$2.md"
}
row_line() { # <N> <repo> <title> [group] -> the row's one line
  if [ -n "${4:-}" ]; then printf -- '- [#%s](https://github.com/%s/pull/%s) — **open**, %s (%s)' "$1" "$2" "$1" "$3" "$4"
  else printf -- '- [#%s](https://github.com/%s/pull/%s) — **open**, %s' "$1" "$2" "$1" "$3"; fi
}
commit_row() { # <worktree> <N> <line>: write, add and commit the row as tvofi; prints the path
  local p
  p=$(write_row "$1" "$2" "$3") || return 1
  git -C "$1" add "$p" || return 1
  # The committer through the environment and the author through --author: an
  # exported GIT_COMMITTER_NAME beats `-c user.name`, and GIT_AUTHOR_NAME beats
  # it too, so a seat's identity variables cannot re-sign the row.
  GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com git -C "$1" commit -q \
    --author='tvofi <70032254+tvofi@users.noreply.github.com>' -m "record: the delivery row for #$2

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || return 1
  echo "$p"
}
has_row() { # <worktree> <N>: rc 0 when HEAD carries the row
  git -C "$1" cat-file -e "HEAD:$ROW_DIR/$2.md" 2>/dev/null
}
ensure_row() { # <worktree> <N> <line>: commit_row when HEAD lacks the row; prints the path only when it added one
  has_row "$1" "$2" && return 0
  commit_row "$1" "$2" "$3"
}

delivery_row_self_test() ( # a subshell: the throwaway git environment stays in it
  local t f=0 n=0 p h0 h1
  t=$(mktemp -d) || { echo "delivery_row self-test: no temporary directory"; return 1; }
  ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
  p=$(write_row "$t/w" 7 "- [#7] row"); [ "$p" = "$ROW_DIR/7.md" ] && [ -f "$t/w/$p" ] && [ ! -e "$t/w/docs" ]
  ck "a row lands under dev/programme/delivery/<N>.md, and nothing is written under docs/" $?
  # Hermetic through the shared helper, whose identity variables (t <t@t>) are
  # exactly the ones the row's commit must not inherit.
  . "$(cd "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)/tests/throwaway_git.sh" && throwaway_git_env
  { throwaway_git_init "$t/r" -q && printf 'x\n' > "$t/r/x" && git -C "$t/r" add x \
    && git -C "$t/r" commit -q -m base; } || { echo "  FAIL fixture"; rm -rf "$t"; return 1; }
  h0=$(git -C "$t/r" rev-parse HEAD)
  p=$(ensure_row "$t/r" 9 "$(row_line 9 o/r "a title")")
  h1=$(git -C "$t/r" rev-parse HEAD)
  [ "$p" = "$ROW_DIR/9.md" ] && [ "$(git -C "$t/r" rev-parse HEAD~1)" = "$h0" ] \
    && [ "$(git -C "$t/r" diff --name-only "$h0" "$h1")" = "$ROW_DIR/9.md" ] \
    && [ "$(git -C "$t/r" log -1 --format='%an <%ae>|%cn|%s')" = "tvofi <70032254+tvofi@users.noreply.github.com>|tvofi|record: the delivery row for #9" ] \
    && [ "$(git -C "$t/r" show "$h1:$ROW_DIR/9.md")" = "- [#9](https://github.com/o/r/pull/9) — **open**, a title" ]
  ck "a head without its row gains exactly one commit, adding only that row, as tvofi" $?
  p=$(ensure_row "$t/r" 9 "$(row_line 9 o/r "another")")
  [ -z "$p" ] && [ "$(git -C "$t/r" rev-parse HEAD)" = "$h1" ]
  ck "null control: a head that carries its row gains no commit" $?
  [ "$(row_line 3 o/r T G)" = "- [#3](https://github.com/o/r/pull/3) — **open**, T (G)" ]
  ck "a group, when given, closes the row in parentheses (open_pr.sh's shape)" $?
  rm -rf "$t"
  echo "delivery_row self-test: $n checks, $f failed"
  [ "$f" = 0 ]
)

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  case ${1:-} in
    --self-test) delivery_row_self_test; exit ;;
    *) sed -n '2,6p' "$0" >&2; exit 2 ;;
  esac
fi
