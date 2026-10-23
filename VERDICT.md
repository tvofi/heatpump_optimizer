Fix review: merge a487ee67b5c310276f5652c4180033893b9ce217

bus-nonce: 4d4fea90c317f3379e6cc1c822c4721a

Round 1. Measured head a487ee67b5c310276f5652c4180033893b9ce217 (the brief's head). Base: origin/main 4c31eb16, which is also the merge base; main has not moved.

## Evidence

- Roles drift: `git diff MB...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- (1) Three-dot diff `MB...HEAD` names exactly two files: dev/programme/rosters/wave-r10-groups.json (+20/-9) and dev/programme/delivery/2663.md (+1, new). VERSION is untouched. The 13 commits carry no Co-Authored-By, Claude or session text (grep count 0).
- (2) Structural diff of base vs head with Python json over the roster. Top-level keys other than groups are unchanged. Each of the 9 changed groups gains only appended `carry` entries and no other field changed (stage, brief, after, resume, files). The groups are LIVESTATE +1, MUTATION-ANCHOR +1, POLICY-LINT-FAMILY +2, FLOW-DESIGN-STAGES +1, FLOW-JIDOKA +1, FLOW-WIP +1, FLY-RELAY-REVIEW-FF +1, FLOW-TOOLKIT-MODEL +1, FLY-SUITE-ENV-FLAKES +1. That is 10 appended carries, one per roster_edit commit, and each prefix is a prefix-identical list.
- Commit messages name the same groups and sources as the carry text (2632 review, triage batches 5/6/7 pf/pm/pl/pk/pi/P-N/P-O, RCA raise-gate grammar). The two merge commits only bring in handoff/audit-r10-roster. The 17-line merge b60070396 is the two POLICY-LINT-FAMILY carries merged in from the handoff branch.
- Cited objects exist. SHAs 2fe11ffbc, a6620c30, fd9914851, c6c8fee16, 84e2aaf66, f2b98c1df, 8f564875d and 2eadf9061 all resolve, and 2eadf9061 is on origin/handoff-body/r10-rca-raise-gate-grammar. 6329234399 is a mandate number, not a SHA, and is not claimed to be one.
- Cited code facts at origin/main: pr_cap.py:52 WIP_STAGE; budget_raise_gate.py lines 137, 138, 410 (the line-410 `justification()`); mutation_table.py:1190 `pin_entry` with the "Recorded by `mutation_table.py ...` against" reason; .gitattributes has 4 ledgermerge lines; 2108 files under tests/mutation_ledger/killed_by/; `git grep handoff-wip` is empty; durations.json sizes_hours holds exactly S 13.1, M 11.4, L 20.1, XL 30.2; replan.py embedded default {"S": 2.0, "M": 4.0, "L": 6.0, "XL": 8.0} at line 814; cloud_dispatch.py fixer prompt "Push nothing else". The #2632 review items resolve on refs/pull/2632/head: coordinator.py:9693 `_expire_away_override`, the `return active, ret` pin, tests/features.py check text "an unexpired away override is not re-persisted each cycle; a lapsed one ...".
- (3) Null control: group count is 169 at base and 169 at head, with an empty set difference both ways. Base roster is byte-equal to origin/main's, so nothing main wrote since the merge base can be lost.
- (4) `node tools/policy/brief_lint.mjs` on the head roster, in a detached worktree at the head: 0 errors, 0 warnings. `git merge-tree --write-tree origin/main HEAD` exits 0 (clean).
- Scoped gate MODE line: not run locally. The diff is data only (roster plus delivery row); CI's closure-scope and closures jobs carry that line, so the cited heavy runs are CI's, not re-run here (PREPR_SKIP_CLOSURES=1).
- CI on this head, one bulk check-runs call: 37 runs. No red. Completed success: pr-contract (x2), budget-raise-gate (x2), arch-score (x2), briefs, mutation, nightly-status, closure-scope, policy-docs, wave-script, delivery-status, graders-head-copy, hassfest, validate-hacs, CodeQL analyses. Neutral: CodeQL. Skipped: the rest, which are scoped out. Still in progress when read: instrument-self-tests, env-matrix, closures, fast (3.14). The verdict's `merge` therefore holds only if those four conclude green, and I was not able to wait on them.
- No red check owes a root-cause answer (rule 11) at this read.
- Rule 6 class enumeration, rule 14 metric movement and the mutation and golden rules (1, 4, 5 of the role) do not apply: no production line, budget, closure or claim file is in the diff.

## Findings

- Carry text for R10-FLOW-TOOLKIT-MODEL cites replan.py "line 335" for the `size_hours[...]` lookup, but at origin/main it is line 325 (line 814 is right). The fixer is told to re-measure, and the claim (no fallback for XS) holds. Carry: dismissed: ten-line citation drift in a roster carry, claim re-verified at main, and the fixer re-measures at its own base
- Carry text for R10-MUTATION-ANCHOR says the 2108 pins are "under killed_by/survivor_triage at main", but 2108 is the count under tests/mutation_ledger/killed_by/ in total and survivor_triage is only a part. My looser pattern counted 1340 files with the "Recorded by" sentence against the carry's 1324, which I could not reproduce exactly because the carry's matching rule is not stated. Carry: dismissed: the carry tells the fixer to measure first, so the figures are not load-bearing, and the fix route is unaffected
