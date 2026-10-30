Fix review: merge 3fbbb46f67f3905a804f458068fb3cf8a266e9e3

bus-nonce: c502181048e664dcf028247916a56588

Round 1 of this head (supersedes the 87e5c30f dispatch). Record PR: two markdown files, no production code, so no mutation proof of its own and no claim, VERSION or budget movement.

## Findings

- P294's APPROVAL-OWED condition (BLOCKED + REVIEW_REQUIRED + a merge at the head) also holds while a required check is still running or red, and the catch-all's UNKNOWN row is a transient GitHub value right after a push. The ruling's null controls (DIRTY, stale head, APPROVED+CLEAN) name no row for BLOCKED/REVIEW_REQUIRED with a pending or red required check, nor for a one-pass UNKNOWN, so the fixer may ship a level that flags before approval is actually the missing step. The fixer should add those two null-control rows. Carry: R10-FLY-TICK-APPROVAL-OWED

## Evidence

- Rulings vs proposal-triage.md: each is one `## P<n>` entry with Verdict, Source, Instances, Cost and Binding; ACCEPT names a destination. P293 lands on R10-FLY-CARRY-DISPOSITION, which exists on the roster. P294 names a new group; its roster op is the orchestrator's (held, per the body). Roles are unchanged on main (empty three-dot diff over dev/governance/roles/).
- P293 sample re-run: I fetched verdict/2936..2974 and ran the 30 merge verdicts through carry_audit.items(text, True) from 043b111d0. 9 flagged (7 evidence, 2 non-blocking), 7 evidence items in 5 verdicts (#2937, #2939, #2955, #2959, #2969): matches the body. The #2955 item (158ad202) is in that PR's earlier verdict commit c8ff9d8a6; the ref's tip 077584681 no longer holds it, so a re-run on today's refs reads 6 in 4. Item texts for the other six match the ruling's classes (4 does-not-block, 1 code-span minor, 2 advisory).
- Null controls named in the ruling exist: the #2465-shape and deferral rows at carry_audit.py self-test lines 1021 and 1034; NOT_REQUIRED, NONBLOCK and CODE_SPAN exist as cited.
- P294 code facts at origin/main 1148ee635: prs() --json lacks reviewDecision (lines 552-554); verdict_levels at 653, MERGE-READY at 689, BLOCKED-UNFIXED at 691; owed_unactioned.py FAMILY at line 53 lists MERGE-READY and BLOCKED-UNFIXED only. verdict/2962, 2976 and 2977 commit times (20:56+01, 03:02+01, 02:18+01) and merge heads match the body.
- Merge with origin/main: git merge-tree --write-tree exits 0 (ev/merge-tree.txt).
- Delivery row dev/programme/delivery/2980.md is present, one line, open.
- carry_audit at the head: 0 findings in the packet; the body's Forward-carry is none, correct for a record PR. figure_lint: 1 resolved, 1 unverified (git log flags), 0 refused. The body says the diff is one markdown file; it is two (the delivery row is the other).
- CI at the head (check-runs API, read live): no red run. Completed ones are success or skipped; closures, browser, fast, coverage, env-matrix and instrument-self-tests were still in progress, so the gate is not concluded. Not re-run.
- VERSION, manifest version and RELEASE_NOTES heading untouched (diff touches two files only).
