#!/usr/bin/env bash
# Mirror the round-9 shared folder and the orchestrator's working scripts to
# branch handoff/audit-r9-plan, so any local or cloud session can resume from git.
# Usage: sync_state.sh [message]. Run after every milestone.
set -euo pipefail
S=/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad
WT=${WT:-$S/plan-wt}
MSG=${1:-"round9: sync state"}
cd "$WT"
git fetch -q origin handoff/audit-r9-plan
git checkout -q -B plan-mirror origin/handoff/audit-r9-plan
mkdir -p handoff/round9/state handoff/round9/scratch
rm -rf handoff/round9/state && mkdir -p handoff/round9/state && cp -a /mnt/project-files/audit-r9/. handoff/round9/state/ && find handoff/round9/state -name __pycache__ -prune -exec rm -rf {} +
cp handoff/round9/state/RESUME.md handoff/round9/RESUME.md
if [ -d "$S" ]; then
  find "$S" -maxdepth 1 -type f \( -name '*.py' -o -name '*.js' -o -name '*.sh' -o -name '*.md' -o -name '*.json' \) -size -2M \
    -exec cp {} handoff/round9/scratch/ \;
fi
git add -A handoff/round9
if git diff --cached --quiet; then echo "no change"; exit 0; fi
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WgT4h2uvK9kbxQbWc5MJis"
for d in 2 4 8 16; do git push -q origin HEAD:handoff/audit-r9-plan && break || sleep $d; done
git ls-remote origin handoff/audit-r9-plan
