#!/usr/bin/env bash
# R10-RCA-PREPR-HEAD-GRADERS: attribute one red pinned-job run to the grader copy.
#
#   attribute.sh <head-sha> <pinned-sha> <job> <out-dir>
#
# Builds CI's tree for a pull-request run -- a merge of <head> into <pinned>,
# pinned as first parent, the way refs/pull/N/merge is built -- in a shared
# throwaway clone whose origin/main is <pinned> (agreement.mjs's merge-subject
# walk reads `merge-base HEAD origin/main`; a live origin/main that has since
# merged the pull request moves that walk, R10-RCA-2671-WAVE-SCRIPT section 1).
# It then runs <job>'s corpus graders on that tree twice: with the pull
# request's own copy of every pinned program (what prepr.sh steps 3-4 run) and
# with <pinned>'s copy of each pinned program the branch changed (what the
# job's "Restore the check source from the base commit" step runs). The
# pinned pathspecs are read from the merge tree's own governance.yml by
# prepr.sh's own reader (PIN_AWK and pin_read, extracted, never run whole).
#
# An instance of the class is: base copy red, head copy green, on one tree.
# Prints one line: `<job> head=<rc> base=<rc> files=<n> first=<first refusal>`.
# Writes only under <out-dir>; the clone is removed on exit.
set -u
head=$1 pinned=$2 job=$3 out=$4
root=$(git rev-parse --show-toplevel)
. "$root/tests/throwaway_git.sh"
mkdir -p "$out"
tree=$(git merge-tree --write-tree "$pinned" "$head" 2>/dev/null) || { echo "$job merge-conflict"; exit 2; }
tree=${tree%%$'\n'*}
merge=$(git commit-tree "$tree" -p "$pinned" -p "$head" -m "ci-shape merge of $head into $pinned")
wt=$(mktemp -d "$out/wt.XXXXXX")
trap 'rm -rf "$wt"' EXIT
throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" || { echo "$job no-clone"; exit 2; }
cd "$wt/t" || exit 2
throwaway_git_env
git checkout -q --detach "$merge" && git update-ref refs/remotes/origin/main "$pinned" || { echo "$job no-checkout"; exit 2; }

sed -n '/^PIN_AWK=\$(cat <<.AWK.$/,/^pinned_paths()/p' "$root/tools/pr/prepr.sh" > "$wt/pin.sh"
echo 'pinned_paths .github/workflows/governance.yml' >> "$wt/pin.sh"
pins=$(bash "$wt/pin.sh")
[ -n "$pins" ] || { echo "$job no-pins"; exit 2; }
files=()
while IFS= read -r f; do
  hit=1
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    if [[ $f == $p || $f == "$p"/* ]]; then hit=0; break; fi
  done <<<"$pins"
  [ "$hit" -eq 0 ] || continue
  git cat-file -e "$pinned:$f" 2>/dev/null || continue
  files+=("$f")
done < <(git diff --no-renames --name-only "$pinned...$head")

pick() { if test -f ".claude/workflows/$1"; then echo ".claude/workflows/$1"; else echo "tools/policy/$1"; fi; }
grade() { # log -> rc
  case $job in
    policy-docs|env-matrix) node "$(pick policy_lint.mjs)" ;;
    check-wave-script) node "$(pick check-wave-script.mjs)" ;;
    agreement)
      python3 -I "$(pick agreement_py.py)" --out "$1.json" && node "$(pick agreement.mjs)" --py-json "$1.json" ;;
    field-coverage) node "$(pick field_coverage.mjs)" ;;
  esac >"$1" 2>&1
}
grade "$out/head.log"; hrc=$?
if [ "${#files[@]}" -gt 0 ]; then git checkout -q "$pinned" -- "${files[@]}"; fi
grade "$out/base.log"; brc=$?
first=$(grep -E 'ERROR +\[|RESULT divergent=|^  FAIL |BLIND |DEAD |REFUSED ' "$out/base.log" | grep -v 'probe, expected' | head -1 | tr -s ' ' | cut -c1-160)
echo "$job head=$hrc base=$brc files=${#files[@]} first=${first:-none}"
