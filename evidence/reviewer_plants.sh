#!/bin/bash
# Reviewer's own plant runner (round 4 of #2697), not the fixer's. Runs the finder's
# harness `python3 -I tools/policy/agreement_py.py --run` with the guard from <ref>
# under one plant at a time, restoring every file.
set -u
REF=$1
T=$(mktemp -d); AG=tools/policy/agreement.mjs; MP=tools/audit/seat/merge_pr.sh; MT=tools/audit/seat/merge_train.py
cp "$AG" "$T/ag"; git show "$REF:$AG" > "$AG"
run() { python3 -I tools/policy/agreement_py.py --run 2>&1 | grep -E 'merge call|REFUSED +merge-subject|RESULT' | sed -e 's/^ *//' -e 's/ seconds=[0-9.]*//' -e 's/^.*first-parent commit(s) past [0-9a-f]*, //' | tr '\n' ' '; echo; }
S='"Merge pull request #1 (x)"'
add() { cp "$MP" "$T/mp"; printf '\nfalse && %s\n' "$2" >> "$MP"; echo "$1: $(run)"; cp "$T/mp" "$MP"; }
mt() { cp "$MT" "$T/mt"; python3 - "$MT" "$2" <<'P'
import sys; p,new=sys.argv[1],sys.argv[2]; s=open(p).read()
old='self.run(["gh", "pr", "merge", n, "--repo", self.repo, "--merge", "--match-head-commit", h])'
assert old in s; open(p,'w').write(s.replace(old,new,1))
P
echo "$1: $(run)"; cp "$T/mt" "$MT"; }
echo "unperturbed: $(run)"
mt 'MT single-quoted argv' "self.run(['gh', 'pr', 'merge', n, '--repo', self.repo, '--merge', '--subject', 'Merge pull request #%s (x)' % n])"
mt 'MT space before comma' 'self.run(["gh" , "pr" , "merge" , n, "--subject", "x"])'
mt 'MT --repo between pr and merge' 'self.run(["gh", "pr", "--repo", self.repo, "merge", n, "--subject", "x"])'
mt 'MT blank line inside argv' 'self.run(["gh", "pr", "merge", n,

                  "--subject", "x"])'
mt 'MT -t in argv' 'self.run(["gh", "pr", "merge", n, "-t", "x"])'
add 'MP gh pr "merge"' "gh pr \"merge\" 1 --merge --subject $S"
add 'MP gh "pr" merge' "gh \"pr\" merge 1 --merge --subject $S"
add 'MP gh pr -R o/r merge' "gh pr -R o/r merge 1 --merge --subject $S"
add 'MP gh --repo o/r pr merge' "gh --repo o/r pr merge 1 --merge --subject $S"
add 'MP gh \\-nl pr merge' "gh \\
  pr merge 1 --merge --subject $S"
add 'MP -mt cluster' "gh pr merge 1 -mt $S"
add 'MP ${GH:-gh} program' "\${GH:-gh} pr merge 1 --merge --subject $S"
add 'MP $(command -v gh) program' "\$(command -v gh) pr merge 1 --merge --subject $S"
add 'MP flag before merge word' "gh pr --subject $S merge 1 --merge"
add 'MP -t"x" attached quoted' "gh pr merge 1 --merge -t\"x\""
add 'MP gh.exe' "gh.exe pr merge 1 --merge --subject $S"
add 'MP null: gh pr view -t' "gh pr view 1 --json title -t x"
cp "$T/ag" "$AG"; rm -rf "$T"; git status --short
