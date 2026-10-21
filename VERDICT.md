Fix review: blocked 6684dee65832c7b8e822f8ee0b33fd3f627b54ed harness: design-trace-missing reviewer dispatch refusal at a head with a required context concluded failure

Round 1 (first review). Measured at head 6684dee65832c7b8e822f8ee0b33fd3f627b54ed (detached worktree), merge base 49c222280; roles/ unchanged between the base and origin/main 57f0c9c77. Spec: the pack file dev/programme/flow-study/roster/groups/R10-FLOW-DISPATCH.json at 30c57744a plus STUDY.md K16/K17. The group is on neither roster (origin/main nor origin/handoff/audit-r10-roster 23ef06dc6), so the pack is the whole spec.

## Findings

- Blocking: the group brief (revision 7) requires "the dispatcher refuses a reviewer dispatch for a head where a required context's latest run has concluded failure ... reading R10-FLOW-MAIN-GATE's classifier". The diff implements no such refusal, no self-test covers it, and the PR body neither builds nor dispositions it (no waiver by tvofi found). `dispatch_group("reviewer", ...)` renders for any head. If the classifier is not on main yet (#2570, merged at the base, adds only the tick's superseded-cancel rule; R10-FLOW-MAIN-GATE is not landed), the body must say so and defer the arm explicitly, or build the arm against the check-runs API. Evidence: ev/spec.txt, ev/diff_grep.txt. Carry: dismissed: returned to the fixer in this blocked verdict (item b87aa9e4)
- Wrong default roster ref: `dispatch_group` and `--roster-ref` default to `roster_lib.MAIN_REF` (origin/main). roster_lib's own O17 note (tvofi 2026-10-18) says the default reader is `default_roster_ref`, the round's roster branch, because origin/main is stale. Measured now: 12 of 108 groups have a different brief on origin/main than on origin/handoff/audit-r10-roster (R10-NIGHT-FOLDS, R10-RATIO-ANCHOR, R10-INPUT-STALENESS, ...), so a default group dispatch publishes a stale brief for them. Because the head defaults to the tip of the roster ref, the fix is not just to switch the default: a fixer head taken from the roster branch would fork from the wrong commit. The roster ref and the head have to come from separate sources. Evidence: ev/roster_ref.txt. Carry: dismissed: returned to the fixer in this blocked verdict (item 69e4db4b)
- Unpinned: the reviewer path's explicit `head` is untested. With the mutant `head or _git(...)` -> `_git(...)`, the reviewer is dispatched at the roster tip and not the PR head, and all 42 checks still pass. The reviewer test passes no `--head`. Evidence: ev/mutants.txt (head-ignored). Carry: dismissed: returned to the fixer in this blocked verdict (item 1360f922)
- Unpinned: the `ref_privacy.refusal` guard in `_publish`, which the body cites to justify the GUARDED entry in PUSHERS, has no test that fails without it. With the mutant `if why:` -> `if False:`, all 42 checks pass. The host-path check that does fail goes through `render`, not this guard. Evidence: ev/mutants.txt (privacy-off). Carry: dismissed: returned to the fixer in this blocked verdict (item f71fbc59)
- Body figure off by one: the body says the brief-drop mutant fails 3 checks. At this head it fails 4, because the host-path roster check also fails once the brief is dropped. The other mutants reproduce as stated: tree-skip 2, topic-to-id 2, parent-drop dies with a non-fast-forward push. Evidence: ev/mutants.txt. Carry: dismissed: returned to the fixer in this blocked verdict (item 91a475aa)
- Non-blocking, seam not built: the K17 carry also asks for the seat to be added to workers.json. The body carries only the bus.sh dispatch / reviewer-fire seam to R10-ORCH-MACHINERY and never names workers.json. Carry: R10-ORCH-MACHINERY (item 92bca45d)

## Confirmed

- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`: 42 checks, 0 failed (the null control in the body holds). ref_privacy --check, tmp_paths --check and throwaway_git --check each report 0 refused. `structure.py`: STRUCTURE RATCHET PASSED. VERSION, the manifest, RELEASE_NOTES.md and the golden files are untouched (ev/checks.txt).
- `git merge-tree --write-tree origin/main <head>` exits 0 (tree 4ea9398b7). CI at this head: 48 check-runs. The only red is nightly-status, which grades main, and the body's Red checks answers it. pr-contract succeeded at 16:59:55Z, after the last run concluded.
- Not re-derived: entities 2375, archscore dS +0.0000. Both are CI heavy runs, cited green, not re-run.

RESULT mutants: 8 planted, 6 killed, 2 survived (head-ignored, privacy-off)
RESULT spec: 1 brief requirement neither built nor dispositioned (revision 7 reviewer refusal)
RESULT merge-tree: clean
RESULT ci: 1 red (nightly-status, main's), answered

bus-nonce: afe25a7048b52c8696e889a066b877aa
