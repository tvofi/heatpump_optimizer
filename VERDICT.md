Fix review: merge cab2a3b1739530e687afbe135ebd4161903cdcc4

bus-nonce: 1ecdeef2e5a3642636745e08a36fa348

Round 1, re-review of the recarry. Reviewer r10-raise-reviewer. Earlier verdict at 82443a023ac7187e6cc580d0c8b5e752cbd6c583 (review/2211 eaa2bb0f); this judges only the resolution delta to cab2a3b1739530e687afbe135ebd4161903cdcc4 (parents 82443a02 + a77faf30, #2210).

- Delta 82443a02..cab2a3b1739530e687afbe135ebd4161903cdcc4: dev/programme/delivery/2210.md, tests/replay.py, tools/replay/export.py (3 files, +200 -5). This equals main's own diff from the old merge base to a77faf30, byte for byte in --stat.
- Resolution delta: git merge-tree of the two parents gives tree 91f98d77, exit 0; diff from that tree to the head's tree is empty. No hand resolution.
- The PR's own files are blob-identical at 82443a02 and at the head: CLAUDE.md, tools/policy/budget_raise_gate.py, dev/governance/rules/ratchet-budgets.md, the 0013 decision, .claude/rules and .cursor/rules ratchet-budgets, dev/programme/delivery/2211.md.
- RESULT budget_raise_gate self-test at cab2a3b1739530e687afbe135ebd4161903cdcc4: 235 checks, 0 failed. rules_sync --check ok. merge-tree against origin/main exit 0.
- Check-runs at cab2a3b1739530e687afbe135ebd4161903cdcc4 (commits API, every run concluded): 26 success, 18 skipped, 1 failure. The failure is nightly-status ("slow failed last night"), which is not a required context and is not this diff's.
- All earlier findings carry unchanged, since no reviewed file moved: policy text, the gate's refusals of expired, edited and missing mandates and of missing arch_score figures, the mutants, and the delivery row.
