#!/bin/bash
# policy_check.sh: OK if policy-read.stamp is newer than the last compact_boundary in this session's transcript, else OWED
J=$HOME/.claude/projects/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-audit-round-10-orchestration-eaa727/9d5c75e8-1167-40ab-8487-67826f2ebc1f.jsonl
S=$HOME/hpo-orch/r10s3/orch/policy-read.stamp
last=$(grep '"subtype":"compact_boundary"' "$J" | tail -1 | grep -o '"timestamp":"[^"]*"' | head -1 | cut -d'"' -f4)
read_at=$(cat "$S" 2>/dev/null)
if [ -z "$read_at" ]; then echo "POLICY RE-READ OWED (no stamp; last compaction $last)"; exit 1; fi
if [[ "$read_at" > "${last%%.*}" ]]; then echo "POLICY OK (read $read_at > compaction $last)"; else echo "POLICY RE-READ OWED (read $read_at, compaction $last)"; exit 1; fi
