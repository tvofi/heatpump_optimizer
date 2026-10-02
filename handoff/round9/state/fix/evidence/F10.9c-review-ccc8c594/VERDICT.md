Fix review: merge ccc8c594963435bd8073bb79e47cf9e748cfe701

Round 2, PR #1823 (stage 1). Code head ccc8c594. The transport head e2626874 adds only BODY.md and replay_pairs.py
under tools/audit/handoff/.

RESOLUTION DELTA (aa42c991 = c5102ea7 + main 411368b6)
- The tree equals git merge-tree 411368b6 c5102ea7 except in tools/audit/briefs/orchestrator.md, the one
  conflicting file.
- The orchestrator.md diff against main (resolution_orchestrator.diff) does three things. It keeps PROC-1's
  rule "CI green at a head containing current origin/main" and adds the fast path as its one exception, with
  the orchestrator as the queue's one bypass. It rewords two of main's sentences, the tag-citation one and the
  worktree_gc one, to fit the 4096-token cap. The meaning is unchanged; it is policy text, so tvofi's
  mandate approval covers it. It also drops PR1's earlier "Main moved since its CI" line, which the Except
  line replaces.
- merge-tree origin/main(411368b6) ccc8c594: clean.

FIX (aa42c991..ccc8c594, merge_fastpath.py only)
- My round-1 probe now refuses: decide(pr=[DISCLAIMER.md], main=[tools/audit/README.md]) gives unrecorded.
  The same holds for DISCLAIMER.md vs docs/audit-2026-09.md, docs/setup.md vs DISCLAIMER.md, and main
  changing tests/closure.py.
- The run_always scripts are parsed from run.sh at both ends: closure.py, env_drift.py, harness_headers.py
  and layout.py. Including them in the overlap loop also closes my round-1 env_drift belt note:
  quality_scale.yaml now refuses as overlap.
- Self-test: 25 checks, 0 failed. Targeted mutant (unrecorded class disabled): 2 FAIL, as the fixer reported.
- codeowners_gap --check: uncovered_files=0.
- Cost: the new class refuses on nearly every real pair, because docs/delivery rows are unrecorded. The
  fixer's replay found 0 of 30 recent merges ELIGIBLE. That costs speed, not a barrier, and the PR body says
  so. Making the fast path useful needs a later recorder change.

UNRUN: the gate and the mutation table (cite the head's CI, not yet reported to me), typing, real-HA.
