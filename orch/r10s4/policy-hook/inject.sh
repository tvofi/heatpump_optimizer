#!/bin/bash
# Policy index for the orchestrator main session: path + blob sha at origin/main,
# with each file marked CHANGED against the manifest of the last full re-read.
W=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt
MAN=/Users/timmalmstrom/hpo-orch/r10s4/policy-hook/last-read.manifest
git -C "$W" fetch -q origin main 2>/dev/null
R=$(git -C "$W" rev-parse origin/main)
echo "BINDING POLICY INDEX (origin/main ${R:0:10}). Re-read each CHANGED file with: git -C $W show origin/main:<path>. Then run policy_reread_check.py --write-stamp and refresh the manifest with: bash $0 --record"
FILES="CLAUDE.md .claude/skills/steward/SKILL.md .github/PULL_REQUEST_TEMPLATE.md $(git -C "$W" ls-tree --name-only origin/main dev/governance/rules/ | grep '\.md$') dev/governance/roles/orchestrator.md dev/governance/roles/fixer.md dev/governance/roles/fix-review.md dev/governance/roles/root-cause.md dev/governance/roles/judge.md dev/governance/roles/verifier.md tools/audit/seat/INSTRUMENTS.md tools/audit/seat/sweep_template.md"
CUR=$(for f in $FILES; do echo "$(git -C "$W" rev-parse "origin/main:$f") $f"; done)
if [ "$1" = "--record" ]; then echo "$CUR" > "$MAN"; echo "recorded $(echo "$CUR" | wc -l) files"; exit 0; fi
echo "$CUR" | while read -r sha f; do
  if grep -qx "$sha $f" "$MAN" 2>/dev/null; then echo "  same    $f"; else echo "  CHANGED $f"; fi
done
