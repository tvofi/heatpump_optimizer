Fix review: merge b15157fb5b98e2011fdd9765672fda20f9952b63

bus-nonce: 9bfe9f70cae37b74dd5edc965b505c52

Round 1. Head measured: b15157fb5b98e2011fdd9765672fda20f9952b63 (diff vs merge base: only dev/programme/triage/s6-batch124.md and dev/programme/delivery/3214.md).

## Findings

## Evidence
- RESULT: ruling shape matches proposal-triage.md: Verdict, Source, Instances, Cost, Binding present; REJECT names its binding cost (losing P296's guard); no ACCEPT, so no destination owed.
- RESULT: the cited delivery exists. s6-batch65.md#P296 line 55 gives the grammar "Carry: <dest> (item <id>, supersedes <old>)" and tools/audit/carry_audit.py:163-164,517-524 implements it, including refusing a supersede of a valid destination.
- RESULT: the figure re-derives. `python3 -I tools/audit/carry_audit.py pr 3185` prints "#2259 superseded by R10-FLY-ARCHSCORE-STMT-PACKING (item a2e21972)" and "CARRY-AUDIT #3185: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)" (ev/carry_audit_3185.txt).
- RESULT: merge-tree with origin/main is clean (no conflict). VERSION, manifest and notes untouched. No budgets, closures or claim files moved. carry_audit at the head: 0 findings, 0 bad.
- Not verified: the Source (an orchestrator queue line of 2026-11-04T21:43:27Z) is not in the tree; I took it as stated. figure_lint reports 1 not-verified figure from the packet (a git diff --stat in the packet's own context, not in this PR's files).
- CI state: UNREADABLE as a verdict on the content. merge_train classify prints RED (gate), but every run on this head (41926047087, 41926047267, 41927640479) concluded cancelled after sitting queued for ~35 min, and the gate check is a cancelled one; no job executed (ev/runs.txt). It is not a failing check, so no red answer is owed. The orchestrator must get a real green run (re-run CI) before merging.
