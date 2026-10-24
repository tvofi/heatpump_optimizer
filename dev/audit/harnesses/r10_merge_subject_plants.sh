#!/bin/bash
# R10-MERGE-SUBJECT-HARDEN (#2697): the finder's harness at both ends, under one
# plant per spelling the round-3 review found unseen.
#
#   bash dev/audit/harnesses/r10_merge_subject_plants.sh [<ref>]   (from the repository root)
#
# Runs `python3 -I tools/policy/agreement_py.py --run` unperturbed and under each
# plant, with tools/policy/agreement.mjs taken from <ref> (default: the working
# tree), and restores every file it touched. A plant the guard reads prints a
# `REFUSED merge-subject-pr writer` line and refused=1; a miss prints refused=0.
set -u
REF=${1:-}
PY=${PYTHON:-python3}
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
AG=tools/policy/agreement.mjs; MP=tools/audit/seat/merge_pr.sh; MT=tools/audit/seat/merge_train.py
cp "$AG" "$T/agreement.mjs"
[ -n "$REF" ] && git show "$REF:$AG" > "$AG"
run() { "$PY" -I tools/policy/agreement_py.py --run 2>&1 | grep -E 'merge call|REFUSED +merge-subject|RESULT' | sed -e 's/^ *//' -e 's/ seconds=[0-9.]*//' | tr '\n' ' '; echo; }
plant() { local name=$1 f=$2; shift 2; cp "$f" "$T/plant"; "$@"; echo "$name: $(run)"; cp "$T/plant" "$f"; }
add() { printf '\n%s\n' "$1" >> "$2"; }
S='"Merge pull request #1 (x)"'
echo "unperturbed: $(run)"
line=$(grep -n 'self.run(\["gh", "pr", "merge", n, "--repo"' "$MT" | head -1 | cut -d: -f1)
plant "single-quoted argv rewrite of $MT:$line" "$MT" sed -i.bak "${line}s/self.run(\[\"gh\", \"pr\", \"merge\", n,/self.run(['gh', 'pr', 'merge', n, '--subject', 'Merge pull request #%s (x)' % n,/" "$MT"
rm -f "$MT.bak"
plant 'gh pr "merge"' "$MP" add "false && gh pr \"merge\" 1 --merge --subject $S" "$MP"
plant 'gh pr -R o/r merge' "$MP" add "false && gh pr -R o/r merge 1 --merge --subject $S" "$MP"
plant 'gh \-newline pr merge' "$MP" add "false && gh \\
  pr merge 1 --merge --subject $S" "$MP"
plant 'a -mt cluster' "$MP" add "false && gh pr merge 1 -mt $S" "$MP"
cp "$T/agreement.mjs" "$AG"
git status --short -- "$AG" "$MP" "$MT"
