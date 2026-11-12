#!/usr/bin/env bash
# R10-FIXER-MD-SPELLING-CORPUS carries 0 and 1: the measure-first behind
# fixer.md step 2's "killing the diff's survivors is yours". Reproduces every
# figure the pull request's body states from git alone (the bus refs) and
# tools/audit/seat/mutant_run.py:
#
#   fetch                         the review/* and verdict/* bus refs, under refs/bus/
#   blocks FROM UNTIL CLASS_RE    one line per (pr, head) blocked with a class
#                                 matching CLASS_RE, verdict commit date in [FROM, UNTIL]:
#                                 "<pr> <head> <first verdict time>"
#   base HEAD TIME                main's first-parent tip at TIME, merged-based with HEAD:
#                                 the diff base the fixer's prepr saw
#   rank BASE HEAD FILE LINE..    the 1-based rank of the first listed mutant on each
#                                 FILE:LINE in `mutant_run.py --diff --list` (cap 40 = rank <= 40),
#                                 "none" when diff mode draws no mutant there
#   repair PR HEAD                hours from the first block at HEAD to the next verdict
#                                 at a different head (a same-head re-post is not a round)
#   run BASE REV CMD [in-place]   wall seconds and SURVIVED lines of the capped report-only
#                                 diff run at REV (in place: in a detached worktree at REV)
#
# RESULT window=168h — the coverage window is the 7 days before the merge base.
# Null control: `run` at a head merged first pass (#3384, c620ebba^1...c620ebba^2)
# reports survivors only inside orchestrator_tick.py's self_test(), none a
# reviewer would name.
set -u
TOP=$(git rev-parse --show-toplevel) || exit 2
cd "$TOP" || exit 2
MR=tools/audit/seat/mutant_run.py
case "${1:-}" in
  fetch)
    git fetch -q origin '+refs/heads/review/*:refs/bus/review/*' '+refs/heads/verdict/*:refs/bus/verdict/*' ;;
  blocks)
    from=$2; until=$3; cls=$4
    for r in $(git for-each-ref --format='%(refname)' refs/bus/review refs/bus/verdict); do
      git log --format='%H %cI' --since="$from" --until="$until" "$r" | while read -r c d; do
        l=$(git show "$c:VERDICT.md" 2>/dev/null | head -1)
        if grep -Eq "^Fix review: blocked [0-9a-f]{40} ($cls):" <<<"$l"; then
          echo "${r##*/} $(cut -d' ' -f4 <<<"$l") $d"
        fi
      done
    done | sort -k1,1n -k2,2 -k3,3 | awk '!seen[$1" "$2]++' ;;
  base)
    git merge-base "$(git rev-list -1 --first-parent --before="$3" origin/main)" "$2" ;;
  rank)
    b=$2; h=$3; f=$4; shift 4
    list=$(python3 -I "$MR" --diff "$b...$h" --cmd true --list --max-mutants 0 2>&1 | grep '^MUTANT ')
    for l in "$@"; do
      r=$(grep -n "^MUTANT $f:$l " <<<"$list" | head -1 | cut -d: -f1)
      echo "$f:$l rank=${r:-none} of $(grep -c . <<<"$list")"
    done ;;
  repair)
    pr=$2; h=$3; bt=""
    while read -r t c; do
      l=$(git show "$c:VERDICT.md" | head -1)
      if [ -z "$bt" ]; then case "$l" in "Fix review: blocked $h "*) bt=$t ;; esac; continue; fi
      case "$l" in *" $h"*) continue ;; esac
      echo "$pr ${h:0:8} block=$(date -u -d "@$bt" +%FT%TZ) next=$(date -u -d "@$t" +%FT%TZ) hours=$(awk -v a="$bt" -v b="$t" 'BEGIN{printf "%.2f", (b-a)/3600}')"
      exit 0
    done < <(git log --reverse --format='%ct %H' "refs/bus/verdict/$pr")
    echo "$pr ${h:0:8} block=${bt:+$(date -u -d "@$bt" +%FT%TZ)} next=none" ;;
  run)
    b=$2; rev=$3; cmd=$4; mode=${5:-}; W=""
    if [ "$mode" = in-place ]; then
      W=$(mktemp -d "${TMPDIR:-/tmp}/mutcov.XXXXXX"); rmdir "$W"
      git worktree add -q --detach "$W" "$rev" || exit 2
      cd "$W" || exit 2; rev=HEAD; flag=--in-place
    else flag=""; fi
    s=$(date +%s.%N)
    out=$(python3 -I "$MR" --diff "$b...$rev" --cmd "$cmd" --max-mutants 40 --report-only ${flag:+"$flag"} 2>&1); rc=$?
    e=$(date +%s.%N)
    grep -E '^(SURVIVED|BASELINE)' <<<"$out"
    echo "rc=$rc wall_s=$(awk -v a="$s" -v b="$e" 'BEGIN{printf "%.1f", b-a}') survivors=$(grep -c '^SURVIVED' <<<"$out")"
    if [ -n "$W" ]; then cd / && git -C "$TOP" worktree remove --force "$W" 2>/dev/null; fi ;;
  *)
    sed -n '2,24p' "$0"; exit 2 ;;
esac
