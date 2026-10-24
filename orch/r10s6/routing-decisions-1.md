# Routing decisions 1 (round 10, 2026-10-24)

Inputs: routing-audit-1.md; roster `origin/handoff/audit-r10-roster` d3c2a27c7; `origin/main` 9586fce08 (fetched 2026-10-24). Item texts re-read with `carry_audit.py`'s own `audit()` over PR bodies and comments cached once by `gh pr view N --json body,comments` (34 source PRs, plus 16 group PRs for section C) into /Users/timmalmstrom/hpo-orch/r10s6/scratch/routing2/; it reproduces audit 1's 70 bad-destination and 25 unrouted rows exactly. Evidence is `git grep`/`git show` at origin/main unless stated. Ops: routing-ops-1.txt. Nothing was written to GitHub, the roster or any branch.

Verdicts: IMPLEMENTED (on main; needs nothing), NO-OBLIGATION (evidence prose, a trailer, a note on a merged body, or a condition that expired; needs nothing), NOT IMPLEMENTED (routed to the live group named; a group marked new is in groups/*.json).

## Counts

| set | IMPLEMENTED | NO-OBLIGATION | NOT IMPLEMENTED | total |
|---|---|---|---|---|
| A. BAD-DEST rows | 24 | 7 | 39 | 70 |
| A. UNROUTED rows | 3 | 18 | 4 | 25 |

B. 32 live groups with no issue: 8 wired to an existing open issue, 1 absorbed (set done), 23 NEED-ISSUE covered by 15 issue bodies (two umbrellas of 7 and 2, one of 2, 12 single). Plus 3 done groups reopened and 1 new group (R10-ROUTING-INVARIANTS) that need issues: 19 bodies in routing-issues-1/.
C. 14 uncovered issues: 7 DELIVERED (close by hand), 7 NOT DELIVERED (wired: 2 to existing live groups, 5 to new groups).

New groups: R10-ADVISOR-RESIDUE (#2257), R10-RESTORE-RACE-PROBE (#2248, #2674), R10-BRIEFS-FOLD-D0 (#2269), R10-REPLAY-REAL-DAY (#2272), R10-ARCHSCORE-SPELLINGS (#2259), R10-ROUTING-INVARIANTS (needs issue). Reopened to carries-open (each already holds its carries): R10-FLY-SUITE-ENV-FLAKES, R10-FLY-GH-READ-RETRY, R10-FLY-NO-FOOTERS.

## A. Carry items (one row per audit-1 row)

| source | where | item | audit 1 | verdict | destination | evidence |
|---|---|---|---|---|---|---|
| #2683 | review 6379079217 | 14f2edf3 | UNROUTED | NO-OBLIGATION | - | review evidence (figure_lint output) |
| #2683 | review 6379079217 | 57e267d2 | UNROUTED | NO-OBLIGATION | - | review evidence (body identity) |
| #2683 | review 6379079217 | 7ca5af57 | UNROUTED | NO-OBLIGATION | - | an evidence path fragment |
| #2683 | review 6379079217 | c571d890 | UNROUTED | NO-OBLIGATION | - | review evidence (policy_lint output) |
| #2675 | body | f61f187d | BAD-DEST #2674 | NOT IMPLEMENTED | R10-RESTORE-RACE-PROBE (new) | #2674 open; dev/programme/carries/carry-2674.json on main only, absent from the roster branch (`git ls-tree origin/handoff/audit-r10-roster dev/programme/carries/`); no live group lists #2674 or #2248 |
| #2673 | review 6375740038 | 6b866e0b | UNROUTED | NO-OBLIGATION | - | review evidence (carries checked) |
| #2643 | body | 1e40d527 | BAD-DEST R10-FLY-NO-FOOTERS | NOT IMPLEMENTED | R10-FLY-NO-FOOTERS (reopen) | tools/policy/field_coverage.mjs:114 adds `attribution` to `ignore` but :122 keeps it in `pending`, so the strictening is half done. Carry already in the group's list; reopen |
| #2643 | body | 771d38c3 | BAD-DEST R10-FLY-NO-FOOTERS | NOT IMPLEMENTED | R10-FLY-NO-FOOTERS (reopen) | same as 1e40d527 |
| #2639 | body | 056ddbd0 | BAD-DEST R10-FLY-GH-READ-RETRY | NOT IMPLEMENTED | R10-FLOW-JIDOKA | `git grep instrument-self-tests origin/main -- tools/pr/ci_predict.py` is empty |
| #2639 | body | 85501172 | BAD-DEST R10-FLY-GH-READ-RETRY | NOT IMPLEMENTED | R10-FLY-GH-READ-RETRY (reopen) | PR 3 never landed (see 84be4901) |
| #2639 | body | bb2965c2 | BAD-DEST R10-FLY-GH-READ-RETRY | NOT IMPLEMENTED | R10-FLY-GH-READ-RETRY (reopen) | no git-transport classifier: `git grep -iE 'fetch.*retry\|retry.*fetch' origin/main -- tools/audit/seat/merge_train.py tools/audit/seat/gh_read.py` is empty |
| #2633 | review 6354675958 | 24441f60 | UNROUTED | NO-OBLIGATION | - | review evidence (CI on the head) |
| #2633 | review 6356059586 | 968d05b6 | BAD-DEST R10-FLOW-ARCH-PLANNER | NO-OBLIGATION | - | wording note; the review itself says nothing binding was lost |
| #2632 | body | 9160e669 | BAD-DEST R10-LIVESTATE | IMPLEMENTED | - | coordinator.py:9686-9708: `_resolve_away` keeps the never-revert-across-await guard after #2675 |
| #2632 | body | d17bc0c8 | BAD-DEST R10-FLY-SUITE-ENV-FLAKES | NOT IMPLEMENTED | R10-FLY-SUITE-ENV-FLAKES (reopen) | #2659 (975fbb8), the group's only PR, changed harness_headers.py and closure.py only; tools/coverage/coverage_tree.sh unchanged since b161681af. Carry already in the group's list; reopen |
| #2632 | review 6354822998 | 325975e1 | BAD-DEST R10-FLY-SUITE-ENV-FLAKES | NOT IMPLEMENTED | R10-FLY-SUITE-ENV-FLAKES (reopen) | #2659 did not touch tests/features.py; HASTUB_TZ failures unaddressed. Carry already in the group's list; reopen |
| #2629 | body | 17086c62 | BAD-DEST R10-RECORD-API-BUDGET | NOT IMPLEMENTED | R10-FLOW-RECORD-PITCH | decision O-1 (M3) not taken: dev/audit/rca/install-ratelimit.md:222-227 still a recommendation; no live group owned the record job |
| #2628 | body | dbae61eb | BAD-DEST R10-FLOW-ARCH-PLANNER | NOT IMPLEMENTED | R10-FLOW-WIP | dev/governance/roles/nudge.md:105 still caps the critical-path lane; orchestrator.md:100 exempts it |
| #2628 | review 6352499018 | 0d645b16 | UNROUTED | NO-OBLIGATION | - | review evidence (cuts checked) |
| #2622 | body | f09dc4ca | BAD-DEST R10-POLICY-LINT-FAMILY | NOT IMPLEMENTED | R10-MERGE-SUBJECT-HARDEN | `git grep -iE 'bootstrap\|deadlock' origin/main -- tools/policy/agreement.mjs` is empty; MERGE-SUBJECT-HARDEN is the live owner of agreement.mjs |
| #2612 | body | 3dda57ce | BAD-DEST R10-BRIEFS-FOLD | NOT IMPLEMENTED | R10-BRIEFS-FOLD-D0 (new) | `git grep _CERT_CELLS origin/main -- dev/governance/dimensions/` is empty; tests/optimality.py:655 still space-only |
| #2612 | body | 631f8640 | BAD-DEST R10-BRIEFS-FOLD | NOT IMPLEMENTED | R10-RCA-FRICTION-RESIDUE | a finding-propagation friction row; that key is #2438, which RCA-FRICTION-RESIDUE lists |
| #2612 | body | eb752e24 | BAD-DEST R10-BRIEFS-FOLD | NOT IMPLEMENTED | R10-BRIEFS-FOLD-D0 (new) | `git grep '#1293' origin/main -- dev/governance/dimensions/D0.md` is empty |
| #2609 | body | a6edee9d | BAD-DEST R10-PLAN-ARTIFACT | NOT IMPLEMENTED | R10-FLOW-TOOLKIT-MODEL | `git grep -iE 'plan.model' origin/main -- docs/architecture.md` is empty; the one plan model is TOOLKIT-MODEL's scope |
| #2606 | body | 5afde258 | BAD-DEST R10-RECORD-API-BUDGET | IMPLEMENTED | - | M0: governance.yml:1259,1368 (RATE_LIMIT before/after); `git grep 'shared App quota' origin/main -- dev/programme/HANDOVER.md` is empty (#2629 97b4fdd) |
| #2606 | body | 61373427 | BAD-DEST R10-FLY-GH-READ-RETRY | IMPLEMENTED | - | tools/audit/seat/gh_read.py:22,108-109 waits for x-ratelimit-reset on a spent bucket |
| #2606 | body | 6635e3d7 | BAD-DEST R10-RECORD-API-BUDGET | NOT IMPLEMENTED | R10-FLOW-RECORD-PITCH | record_api_calls.sh:56 marker list lacks `HTTP <code> from` and `unparseable JSON from`, which policy_lint.mjs:3352,3356 print |
| #2606 | body | b5f92218 | BAD-DEST R10-RECORD-API-BUDGET | IMPLEMENTED | - | dev/audit/harnesses/record_api_calls.sh:63-66 refuses --record reading 0 over a non-empty window |
| #2605 | review 6338592560 | 04edda95 | UNROUTED | IMPLEMENTED | - | tests/entities.py:18111-18124 pins PY_SPY_TIMEOUT_S < 30 and that the real lane's default is that constant |
| #2605 | review 6338592560 | d4f06227 | BAD-DEST R10-NIGHTLY-PYSPY-RETRY | NOT IMPLEMENTED | R10-NIGHTLY-HB-RESPAWN | already owned: the live group's brief cites review/2605 finding 2 as its scope; no op |
| #2605 | review 6340610047 | 98c7c2ed | UNROUTED | NO-OBLIGATION | - | review evidence (check 4) |
| #2595 | body | 6fb50ac5 | BAD-DEST R10-POLICY-LINT-FAMILY | NOT IMPLEMENTED | R10-TRAIN-OVERLAP-GRADE | its brief names merge 6077bf70e, this red, as instance 1 of the barrier it owes; no headroom band or overlap grade on main |
| #2595 | review 6332581437 | 98904e32 | BAD-DEST R10-POLICY-LINT-FAMILY | NOT IMPLEMENTED | R10-TRAIN-OVERLAP-GRADE | restates 6fb50ac5 |
| #2595 | review 6332581437 | d7ca3d75 | UNROUTED | NO-OBLIGATION | - | body null-control nit on merged #2595 |
| #2595 | review 6332581437 | ecd69bc2 | UNROUTED | NO-OBLIGATION | - | body figure nit on merged #2595 |
| #2589 | body | 84be4901 | BAD-DEST R10-FLY-GH-READ-RETRY | NOT IMPLEMENTED | R10-FLY-GH-READ-RETRY (reopen) | PR 3 of the group never landed: `git grep -iE 'classify\|gh_read\|retry' origin/main -- .github/workflows/pr-contract.yml` is empty; the group's carry 1 holds PR 3 |
| #2586 | body | 14c702a5 | BAD-DEST R10-RCA-ORCH-CONTINUITY | NO-OBLIGATION | - | the stale 0012 sentence constrained a seat that finished (R10-RCA-ORCH-CONTINUITY done, 93e6a63); 0012's moratorium ended (dev/governance/decisions/0014-design-seats-and-the-end-of-0012s-moratorium.md) |
| #2586 | review 6326243759 | 3703aa13 | BAD-DEST R10-RCA-ORCH-CONTINUITY | NO-OBLIGATION | - | same as 14c702a5 |
| #2585 | body | 6d4f5c52 | BAD-DEST R10-RCA-FRICTION | NOT IMPLEMENTED | R10-FLY-CLOUD-SETUP-TOOLCHAIN | `git grep RUNNER_TEMP origin/main -- tools/audit/seat/cloud-setup.sh dev/programme/HANDOVER.md` is empty |
| #2585 | body | 78caa42b | BAD-DEST R10-RCA-FRICTION | IMPLEMENTED | - | tools/audit/seat/cloud-setup.sh:67 puts venv-ci first on PATH; HANDOVER.md:505 |
| #2585 | body | b32aecdb | BAD-DEST R10-REPLAY-LANE | NO-OBLIGATION | - | REPLAY-LANE merged 0280e6efd at 2026-10-21T03:34, before #2585 (fae523a, 2026-10-22) created nightly.yml; the instruction addressed a finished fixer |
| #2582 | review 6330613458 | cdd7283c | BAD-DEST R10-FLOW-ANDON | NOT IMPLEMENTED | R10-ORCH-BEATD | #2582 (fea3d3c) landed heartbeat.sh only; heartbeat.sh's 1200 s is heartbeat age, and no instrument alarms on a handoff tip ahead of its PR, a dead lock owner or a 1 h self-test (`git grep` over orchestrator_tick.py, heartbeat.sh) |
| #2577 | review 6327609732 | 8ab071b4 | BAD-DEST R10-FLOW-MAIN-GATE | NOT IMPLEMENTED | R10-ORCH-DISPATCH-REG | `git grep -iE 'conclu\|unboarded\|pr_args' origin/main -- tools/audit/seat/bus.sh` is empty; #2584 (49018a8) touched merge_train.py, merge_pr.sh and the tick, not bus.sh dispatch |
| #2577 | review 6331521421 | 9a2082ce | BAD-DEST R10-FLOW-MAIN-GATE | NOT IMPLEMENTED | R10-ORCH-DISPATCH-REG | the hot-file reviewer-refusal arm; same evidence as 8ab071b4 |
| #2577 | review 6331521421 | fa81793d | UNROUTED | NO-OBLIGATION | - | review evidence (round-4 blocks cleared) |
| #2572 | body | 69e7c431 | BAD-DEST #2257 | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | #2257 open, no live owner; seam (b) untouched after #2572 (no later commit names it: `git log --grep '#2257'` shows only 5e1fdb77b) |
| #2572 | body | 87849118 | BAD-DEST #2257 | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | #2257 open, no live owner; seam (c) was measured only in a scratch probe |
| #2572 | body | a47745dc | BAD-DEST #2257 | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | #2257 is open and no live group lists it; coordinator.py:8809 and :11242 still publish the single-solve `monthly_cost_delta` as the advisor's `cost_delta_sek_month` |
| #2572 | body | d096f0c1 | BAD-DEST R10-LIVESTATE | IMPLEMENTED | - | a statement of fact for LIVESTATE, which merged with price_tiles.py in its files (#2675 94bec97; roster resume.note) |
| #2572 | review 6322344533 | 4468b8a1 | UNROUTED | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | the mixing question was left to the re-cut and not measured |
| #2572 | review 6322344533 | 4b51e0e7 | UNROUTED | NO-OBLIGATION | - | disclosure note on merged #2572's body |
| #2572 | review 6322344533 | 5f30f170 | UNROUTED | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | same as e8626144 |
| #2572 | review 6322344533 | bfe93d15 | UNROUTED | IMPLEMENTED | - | a pre-merge process step; R10-UX-HEALTH's carry list holds the #2572 carry on the roster branch |
| #2572 | review 6322344533 | c2b6a1af | UNROUTED | IMPLEMENTED | - | MX1 closed in #2572 itself: tests/finite_boundary.py:1094 seeds the tile book before every `_async_save_*` flush (5e1fdb77b); the round-2 review 6328189370 no longer names MX1 |
| #2572 | review 6322582323 | 36367bc0 | BAD-DEST R10-ADVISOR | NO-OBLIGATION | - | a disclosure note on merged #2572's body; no later stage |
| #2572 | review 6322582323 | ae0472c3 | BAD-DEST R10-ADVISOR | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | MX4 still survives: tests/features.py:33575-33584 folds exactly two samples into every day, so a pooled mean equals the mean of daily means |
| #2572 | review 6322582323 | e8626144 | BAD-DEST R10-ADVISOR | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | the copy question (per degree held vs per degree of setting) was left to judge/owner; no later commit |
| #2572 | review 6328189370 | 5df8a03b | BAD-DEST #2257 | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | same as e8626144, round 2 |
| #2572 | review 6328189370 | f1c7e1de | BAD-DEST #2257 | NOT IMPLEMENTED | R10-ADVISOR-RESIDUE (new) | same as ae0472c3 (MX4), round 2 |
| #2566 | body | 97d06403 | BAD-DEST R10-HANDOVER-REFRESH | IMPLEMENTED | - | dev/programme/HANDOVER.md:500 (`tests/layout.py --guard`), landed with #2566 302f665 |
| #2566 | body | b94aab94 | BAD-DEST R10-HANDOVER-REFRESH | IMPLEMENTED | - | dev/programme/HANDOVER.md:505 (venv-ci first on PATH), landed with #2566 302f665 |
| #2566 | review 6327140155 | e1ab9994 | UNROUTED | NO-OBLIGATION | - | review evidence (nightly-status not required) |
| #2563 | body | 2e462326 | BAD-DEST R10-BRIEFS-FOLD | IMPLEMENTED | - | dev/governance/dimensions/D2.md:36-39 |
| #2563 | review 6317463517 | 429b992e | BAD-DEST R10-NIGHT-FOLDS | IMPLEMENTED | - | custom_components/heatpump_optimizer/const.py:1038 says 0.245 kW |
| #2563 | review 6317463517 | 4ea2e64e | BAD-DEST R10-NIGHT-FOLDS | IMPLEMENTED | - | dev/audit/harnesses/r10_night_folds_learners.py:23 expects gains.unconverged 0.0000 |
| #2563 | review 6317463517 | b29dfdfd | UNROUTED | NO-OBLIGATION | - | trailer line `Round: ...`, not a finding |
| #2563 | review 6317463517 | f2a90213 | UNROUTED | NO-OBLIGATION | - | bus-nonce trailer; carry_audit's TRAILER regex lacks `bus-nonce:` |
| #2561 | body | 17053579 | BAD-DEST R10-BRIEFS-FOLD | IMPLEMENTED | - | the detector landed in #2561 (tools/policy/check-wave-script.mjs:483); fix-review.md:54 puts the word first (`root-cause-detectable: <check>`) |
| #2561 | body | bad0a70a | BAD-DEST R10-POLICY-LINT-FAMILY | IMPLEMENTED | - | tools/policy/policy_lint.mjs:2799 family members include test-vacuous, vacuous-test, vacuous-check, mutant-survives (75bd9e6b1) |
| #2559 | review 6318137698 | 452d9e05 | BAD-DEST R10-BRIEFS-FOLD | IMPLEMENTED | - | the carry it corrects was consumed: dev/governance/dimensions/D2.md:36-39 states the gains precondition (#2631 b24cfe5) |
| #2559 | review 6318137698 | 653b4a9b | BAD-DEST R10-ROSTER-OPS | NO-OBLIGATION | - | stale figures in merged #2559's own body; no later stage reads them |
| #2559 | review 6318238167 | 7f85b089 | BAD-DEST R10-ROSTER-OPS | NOT IMPLEMENTED | R10-ORCH-ROSTER-SCHEMA | roster_edit.py:10,79: only `set-resume --field note` clears a note; `set-stage` leaves a stale note beside `done` |
| #2558 | body | 5a9cc23e | BAD-DEST R10-PLAN-ARTIFACT | IMPLEMENTED | - | the item says survivors B to E "are closed in this PR": #2558 merged 383bca2 |
| #2557 | body | 6bec0b0a | BAD-DEST R10-RCA-HANDOFF-SLIP | NOT IMPLEMENTED | R10-ORCH-LEDGER | tools/audit/seat/ledger.py:58-65: aging keys on `ct`, the tip's commit time (4 h / 12 h), not on arrivals after the last opening as pulse.py does; the standing backlog still saturates it |
| #2554 | review 6331184193 | 64e8b432 | UNROUTED | NO-OBLIGATION | - | review evidence (figures re-derived) |
| #2549 | review 6319952656 | 01ce8b81 | UNROUTED | NOT IMPLEMENTED | R10-UPDATE-PR-SIGNALS | real residual; `git grep -iE 'setsid\|pgid\|process group' origin/main -- tools/audit/seat/cloud_relay.sh tools/audit/seat/update_pr.sh` is empty |
| #2549 | review 6319965396 | 01ce8b81 | UNROUTED | NOT IMPLEMENTED | R10-UPDATE-PR-SIGNALS | real residual; `git grep -iE 'setsid\|pgid\|process group' origin/main -- tools/audit/seat/cloud_relay.sh tools/audit/seat/update_pr.sh` is empty |
| #2548 | body | 2f4b921e | BAD-DEST R10-REPLAY-LANE | IMPLEMENTED | - | option (b) landed: tests/replay.py:376-391, the loop ratio is normalised by a same-clock pure-Python ruler, "bounded, not invariant, across runners" |
| #2545 | review 6326255132 | dc368e8c | BAD-DEST R10-RCA-HANDOFF-SLIP | IMPLEMENTED | - | dev/audit/rca/N-orphaned-handoff.md:178-179 cites orchestrator.md section 5's soft-cap countermeasure (#2545 f35a5a3) |
| #2545 | review 6331182210 | 4f48ff38 | UNROUTED | NO-OBLIGATION | - | review evidence prose (RCA checklist), not a finding |
| #2545 | review 6331182210 | 6c98ab6e | UNROUTED | NO-OBLIGATION | - | review evidence (check-runs), not a finding |
| #2529 | body | 66a6ad9c | BAD-DEST R10-CI-LAYOUT | IMPLEMENTED | - | .github/workflows/governance.yml:529 runs `agreement_py.py --restore` in the lane |
| #2529 | body | 76e30be3 | BAD-DEST R10-CI-LAYOUT | NOT IMPLEMENTED | R10-RCA-FRICTION-RESIDUE | friction row (bash 3.2 seats vs bash 5 CI); `git grep -iE 'bash 3\.2\|bash 5' origin/main -- dev/programme/HANDOVER.md` is empty; no countermeasure or recorded refusal |
| #2529 | body | 8c6a3e6f | BAD-DEST R10-CI-LAYOUT | NOT IMPLEMENTED | R10-FLOW-JIDOKA | prepr.sh:2996 runs the head's .claude/workflows/field_coverage.mjs, not the base's registry over the head; no other pre-push step does |
| #2529 | body | 8e11263f | BAD-DEST R10-CI-LAYOUT | NO-OBLIGATION | - | conditional ("if a later seat finds ..."); the three INERT_EXCEPT entries only over-select; nothing is owed unless a seat finds the artefact |
| #2529 | body | 9728f4d0 | BAD-DEST R10-CI-LAYOUT | NOT IMPLEMENTED | R10-FLOW-JIDOKA | `git grep selftest_wiring origin/main -- tools/pr/prepr.sh tools/audit/seat/merge_train.py tools/audit/seat/merge_pr.sh` is empty |
| #2529 | body | bd99c893 | BAD-DEST R10-CI-LAYOUT | IMPLEMENTED | - | `gh api repos/tvofi/heatpump_optimizer/rulesets/23698884`: required_status_checks contexts = `gate` only |
| #2529 | body | e6bf0f70 | BAD-DEST R10-CI-LAYOUT,R10-CI-LAYOUT-P1 | NOT IMPLEMENTED | R10-FLOW-JIDOKA | the P1/P2 branch-merge half expired (fae523a, #2673 b927f43 merged); the standing half is open: `git grep selftest_wiring origin/main -- tools/pr/prepr.sh tools/audit/seat/merge_train.py tools/audit/seat/merge_pr.sh` is empty. One carry with 9728f4d0 |
| #2529 | body | ef0d3fec | BAD-DEST R10-CI-LAYOUT | IMPLEMENTED | - | abf4f40b7 (R10-CI-LAYOUT PR 1) re-recorded tests/ci_budgets.json (`critical_path_minutes` 54.825, tests/ci_budgets.json:26) |
| #2521 | body | c1406aa8 | BAD-DEST R10-BRIEFS-FOLD | IMPLEMENTED | - | tests/README.md:274 names `dev/audit/harnesses/k1725_blas_kernel_gap.py` |
| #2521 | body | cec58467 | BAD-DEST R10-CURRENCY | IMPLEMENTED | - | 701448f90 (in #2620, 27b59c9) removed the comment: `git log -S money_currency origin/main -- coordinator.py` newest hit; `git grep money_currency` in coordinator.py is empty |
| #2521 | body | d40928f5 | BAD-DEST R10-BRIEFS-FOLD | IMPLEMENTED | - | `git grep -E 'measures all 24\|record all 51\|cross_seam_edges' origin/main -- dev/governance/dimensions/D7.md dev/governance/dimensions/D9.md` is empty after #2631 (b24cfe5) |
| #2521 | review 6318583190 | 33d0028d | BAD-DEST R10-BRIEFS-FOLD | IMPLEMENTED | - | tests/README.md:274 (same correction as c1406aa8) |
| #2513 | body | 1f866f06 | BAD-DEST R10-ROSTER-OPS | NOT IMPLEMENTED | R10-ORCH-ROSTER-SCHEMA | pointer to review item 3b97e1aa; same disposition |
| #2513 | review 6314156311 | 3b97e1aa | BAD-DEST R10-ROSTER-OPS | NOT IMPLEMENTED | R10-ORCH-ROSTER-SCHEMA | `git grep -E 'fail.closed\|M4\|M5\|M6' origin/main -- tools/audit/seat/r10_roster_ops_mutants.py` is empty: the reviewer's three fail-closed survivors were never tightened; ROSTER-OPS (#2513 929275e) is done |

## A0. The 40 (source PR, destination) pairs

| source | audit-1 destination | items | verdicts -> live destination |
|---|---|---|---|
| #2675 | #2674 | 1 | f61f187d NOT IMPLEMENTED -> R10-RESTORE-RACE-PROBE |
| #2643 | R10-FLY-NO-FOOTERS | 2 | 1e40d527 NOT IMPLEMENTED -> R10-FLY-NO-FOOTERS; 771d38c3 NOT IMPLEMENTED -> R10-FLY-NO-FOOTERS |
| #2639 | R10-FLY-GH-READ-RETRY | 3 | 056ddbd0 NOT IMPLEMENTED -> R10-FLOW-JIDOKA; 85501172 NOT IMPLEMENTED -> R10-FLY-GH-READ-RETRY; bb2965c2 NOT IMPLEMENTED -> R10-FLY-GH-READ-RETRY |
| #2633 | R10-FLOW-ARCH-PLANNER | 1 | 968d05b6 NO-OBLIGATION |
| #2632 | R10-LIVESTATE | 1 | 9160e669 IMPLEMENTED |
| #2632 | R10-FLY-SUITE-ENV-FLAKES | 2 | d17bc0c8 NOT IMPLEMENTED -> R10-FLY-SUITE-ENV-FLAKES; 325975e1 NOT IMPLEMENTED -> R10-FLY-SUITE-ENV-FLAKES |
| #2629 | R10-RECORD-API-BUDGET | 1 | 17086c62 NOT IMPLEMENTED -> R10-FLOW-RECORD-PITCH |
| #2628 | R10-FLOW-ARCH-PLANNER | 1 | dbae61eb NOT IMPLEMENTED -> R10-FLOW-WIP |
| #2622 | R10-POLICY-LINT-FAMILY | 1 | f09dc4ca NOT IMPLEMENTED -> R10-MERGE-SUBJECT-HARDEN |
| #2612 | R10-BRIEFS-FOLD | 3 | 3dda57ce NOT IMPLEMENTED -> R10-BRIEFS-FOLD-D0; 631f8640 NOT IMPLEMENTED -> R10-RCA-FRICTION-RESIDUE; eb752e24 NOT IMPLEMENTED -> R10-BRIEFS-FOLD-D0 |
| #2609 | R10-PLAN-ARTIFACT | 1 | a6edee9d NOT IMPLEMENTED -> R10-FLOW-TOOLKIT-MODEL |
| #2606 | R10-RECORD-API-BUDGET | 3 | 5afde258 IMPLEMENTED; 6635e3d7 NOT IMPLEMENTED -> R10-FLOW-RECORD-PITCH; b5f92218 IMPLEMENTED |
| #2606 | R10-FLY-GH-READ-RETRY | 1 | 61373427 IMPLEMENTED |
| #2605 | R10-NIGHTLY-PYSPY-RETRY | 1 | d4f06227 NOT IMPLEMENTED -> R10-NIGHTLY-HB-RESPAWN |
| #2595 | R10-POLICY-LINT-FAMILY | 2 | 6fb50ac5 NOT IMPLEMENTED -> R10-TRAIN-OVERLAP-GRADE; 98904e32 NOT IMPLEMENTED -> R10-TRAIN-OVERLAP-GRADE |
| #2589 | R10-FLY-GH-READ-RETRY | 1 | 84be4901 NOT IMPLEMENTED -> R10-FLY-GH-READ-RETRY |
| #2586 | R10-RCA-ORCH-CONTINUITY | 2 | 14c702a5 NO-OBLIGATION; 3703aa13 NO-OBLIGATION |
| #2585 | R10-RCA-FRICTION | 2 | 6d4f5c52 NOT IMPLEMENTED -> R10-FLY-CLOUD-SETUP-TOOLCHAIN; 78caa42b IMPLEMENTED |
| #2585 | R10-REPLAY-LANE | 1 | b32aecdb NO-OBLIGATION |
| #2582 | R10-FLOW-ANDON | 1 | cdd7283c NOT IMPLEMENTED -> R10-ORCH-BEATD |
| #2577 | R10-FLOW-MAIN-GATE | 2 | 8ab071b4 NOT IMPLEMENTED -> R10-ORCH-DISPATCH-REG; 9a2082ce NOT IMPLEMENTED -> R10-ORCH-DISPATCH-REG |
| #2572 | #2257 | 5 | 69e7c431 NOT IMPLEMENTED -> R10-ADVISOR-RESIDUE; 87849118 NOT IMPLEMENTED -> R10-ADVISOR-RESIDUE; a47745dc NOT IMPLEMENTED -> R10-ADVISOR-RESIDUE; 5df8a03b NOT IMPLEMENTED -> R10-ADVISOR-RESIDUE; f1c7e1de NOT IMPLEMENTED -> R10-ADVISOR-RESIDUE |
| #2572 | R10-LIVESTATE | 1 | d096f0c1 IMPLEMENTED |
| #2572 | R10-ADVISOR | 3 | 36367bc0 NO-OBLIGATION; ae0472c3 NOT IMPLEMENTED -> R10-ADVISOR-RESIDUE; e8626144 NOT IMPLEMENTED -> R10-ADVISOR-RESIDUE |
| #2566 | R10-HANDOVER-REFRESH | 2 | 97d06403 IMPLEMENTED; b94aab94 IMPLEMENTED |
| #2563 | R10-BRIEFS-FOLD | 1 | 2e462326 IMPLEMENTED |
| #2563 | R10-NIGHT-FOLDS | 2 | 429b992e IMPLEMENTED; 4ea2e64e IMPLEMENTED |
| #2561 | R10-BRIEFS-FOLD | 1 | 17053579 IMPLEMENTED |
| #2561 | R10-POLICY-LINT-FAMILY | 1 | bad0a70a IMPLEMENTED |
| #2559 | R10-BRIEFS-FOLD | 1 | 452d9e05 IMPLEMENTED |
| #2559 | R10-ROSTER-OPS | 2 | 653b4a9b NO-OBLIGATION; 7f85b089 NOT IMPLEMENTED -> R10-ORCH-ROSTER-SCHEMA |
| #2558 | R10-PLAN-ARTIFACT | 1 | 5a9cc23e IMPLEMENTED |
| #2557 | R10-RCA-HANDOFF-SLIP | 1 | 6bec0b0a NOT IMPLEMENTED -> R10-ORCH-LEDGER |
| #2548 | R10-REPLAY-LANE | 1 | 2f4b921e IMPLEMENTED |
| #2545 | R10-RCA-HANDOFF-SLIP | 1 | dc368e8c IMPLEMENTED |
| #2529 | R10-CI-LAYOUT | 8 | 66a6ad9c IMPLEMENTED; 76e30be3 NOT IMPLEMENTED -> R10-RCA-FRICTION-RESIDUE; 8c6a3e6f NOT IMPLEMENTED -> R10-FLOW-JIDOKA; 8e11263f NO-OBLIGATION; 9728f4d0 NOT IMPLEMENTED -> R10-FLOW-JIDOKA; bd99c893 IMPLEMENTED; e6bf0f70 NOT IMPLEMENTED -> R10-FLOW-JIDOKA; ef0d3fec IMPLEMENTED |
| #2529 | R10-CI-LAYOUT-P1 | 1 | e6bf0f70 NOT IMPLEMENTED -> R10-FLOW-JIDOKA |
| #2521 | R10-BRIEFS-FOLD | 3 | c1406aa8 IMPLEMENTED; d40928f5 IMPLEMENTED; 33d0028d IMPLEMENTED |
| #2521 | R10-CURRENCY | 1 | cec58467 IMPLEMENTED |
| #2513 | R10-ROSTER-OPS | 2 | 1f866f06 NOT IMPLEMENTED -> R10-ORCH-ROSTER-SCHEMA; 3b97e1aa NOT IMPLEMENTED -> R10-ORCH-ROSTER-SCHEMA |

## B. The 32 live groups with no issue

Search: the open-issue list cached once by audit 1 (`gh issue list --state open --limit 500 --json number,title,labels`, /private/tmp/claude-501/s/issues.json, 53 issues), matched against each group's brief. A match is wired only where the issue names the group's own defect class or ask.

| group | stage | verdict | issue / body file | evidence |
|---|---|---|---|---|
| R10-FLOW-JIDOKA | in-progress | WIRE #2428 | carry-missing friction | brief: "Of 133 blocked fix reviews in round 10, 25 were carry-missing"; #2428 is `[policy] recurring friction: carry-missing` |
| R10-FLY-CARRY-DISPOSITION | not-started | WIRE #2428 | carry-missing friction | brief: lets the orchestrator add the `Carry:` marker a carry-missing block asks for |
| R10-FLOW-ROSTER-FREEZE | not-started | WIRE #2389 | head-moved rework | brief: the roster PR's review "comes back head-moved or body-stale: #2559 lost five reviewer rounds" |
| R10-FLOW-BODY-ONLY | not-started | WIRE #2389 | head-moved rework | brief: "every body fix moves a clean head" (#2513, #2544, #2548, #2529, #2549) |
| R10-FLY-ROW-HEAD-CARRY | not-started | WIRE #2389 | head-moved rework | brief: carry CI results across a head move that changes only the delivery row |
| R10-FLY-CARRY-DOC-CONTEXT | not-started | WIRE #2389 | head-moved rework | brief: app_approve.sh carries a verdict across a main merge that moves only md context lines |
| R10-STRUCTURE-ALIAS | in-progress | WIRE #2235 | N-structure-blind | brief: seam_cut_total counts occurrences, so a local alias pays; #2235's mechanism is "measures a name or regex proxy instead of the property it gates" |
| R10-DIAG-REDACT | not-started | WIRE #2271 | DIAG-REPLAY sanitise half | #2271 title: "fill the bundle's replay half through the export's allowlist and sanit[ise]"; brief: "R10-DIAG-REPLAY, the group that held it, is done" |
| R10-FLY-CAP-LINE | not-started | ABSORB into R10-FLOW-WIP, set done | - | same seam: orchestrator_tick.py:607-611 is the WIP line FLOW-WIP owns (pr_cap.py, orchestrator_tick.py in its files); the line still names no exception |
| R10-FLOW-BOARD | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Flow board (Lean study K1)"; no open issue tracks the Lean study |
| R10-FLOW-MQ-PROBE | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean study K9" |
| R10-FLOW-POSTMERGE | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean flow study, mechanisation" |
| R10-FLOW-RECORD-PITCH | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean study K6" |
| R10-FLOW-WIP | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean study K4" |
| R10-FLOW-AUTOTRAIN | in-progress | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean flow study, mechanisation" |
| R10-FLOW-TOOLKIT-MODEL | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "the Lean flow study's projection model" |
| R10-FLOW-AUDIT-PLAN | not-started | NEED-ISSUE (umbrella) | round11-readiness.md | brief: "Mechanise P3 for round 11" |
| R10-ROUND-PLAYBOOK | not-started | NEED-ISSUE (umbrella) | round11-readiness.md | brief: "run round 11 onwards from the tree alone"; #2395 is ARCH-DOCS's docs scope, not dev/audit/README.md |
| R10-ORCH-REVIEW-PACKET | not-started | NEED-ISSUE (umbrella) | seat-context-cost.md | brief: owner ruling 2026-10-24, card 8; #2505 is the machinery design, not this |
| R10-POLICY-ROLE-PACK | not-started | NEED-ISSUE (umbrella) | seat-context-cost.md | brief: owner ruling 2026-10-24, token pre-study (b) |
| R10-FLOW-DESIGN-STAGES | not-started | NEED-ISSUE | design-stages.md | no open issue names design stages |
| R10-FLY-OPENPR-ATOMIC | not-started | NEED-ISSUE | openpr-atomic.md | not done: `git grep -iE 'pr close' origin/main -- tools/audit/seat/open_pr.sh` is empty |
| R10-FLY-RELAY-REVIEW-FF | carries-open | NEED-ISSUE | relay-review-ff.md | #2664 merged 811cd01; 9 carries still open; no issue |
| R10-FLY-ORPHANS-REWRITTEN | not-started | NEED-ISSUE | orphans-rewritten.md | no open issue |
| R10-FLY-DEPGRAPH-STALE | in-progress | NEED-ISSUE | depgraph-stale.md | pins patched (tests/requirements-ci.txt:30 aiohttp 3.14.5) but the cause (graph not updating) is the owed work |
| R10-FLY-STAMP-CHECK-NOTES | not-started | NEED-ISSUE | stamp-check-notes.md | not done: `git grep -- --check-notes origin/main -- tools/release/stamp.py` is empty |
| R10-FLY-MANDATE-REVOKE-GUARD | not-started | NEED-ISSUE | mandate-revoke-guard.md | not done: `git grep -iE 'revok|withdraw-mandate' origin/main -- tools/pr/gh_comment.py` is empty |
| R10-TRAIN-OVERLAP-GRADE | queued | NEED-ISSUE | train-overlap-grade.md | a third-instance barrier; no open issue |
| R10-NIGHTLY-HB-RESPAWN | queued | NEED-ISSUE | nightly-hb-respawn.md | residual of #2605; no open issue |
| R10-FLY-PRUNE-REFS | not-started | NEED-ISSUE | prune-refs.md | not done: prune_refs.py last changed 730ac0c14 (a prune family), neither defect |
| R10-CLOSEOUT-CLEANUP | not-started | NEED-ISSUE | closeout-cleanup.md | runs last; no open issue |
| R10-IMMERSION-LATCH | queued | NEED-ISSUE | immersion-latch.md | D15 finding; no open issue |

Also needing an issue: the three reopened groups (suite-env-flakes.md, gh-read-residue.md, no-footers-strict.md) and R10-ROUTING-INVARIANTS (routing-invariants.md). None of the 32 is already done or absorbed apart from R10-FLY-CAP-LINE; R10-FLY-RELAY-REVIEW-FF's PR merged but its carries are the open work.

## C. The 14 open issues listed only by done groups

| issue | verdict | PR / commit | residual and destination |
|---|---|---|---|
| #2235 | NOT DELIVERED (findings delivered) | #2340 8186403 (`Closes #2235`), #2401 07a0940, RCA #2415 f0a4aca | the class is live in R10-STRUCTURE-ALIAS (seam_cut_total counts occurrences); wire #2235 there |
| #2248 | NOT DELIVERED | #2675 94bec97 (`Part of #2248`) | seven unprobed writers filed as #2674; new R10-RESTORE-RACE-PROBE (issues 2248, 2674) |
| #2250 | DELIVERED | #2612 008ad15 | its one finding D9-s1-01 (fused objective, #2612 body section 1); close |
| #2252 | DELIVERED | #2435 05c39d3 | the relative trust region is the issue's whole ask (#2435 body "What changed"); accuracy.py's refit clip was out of scope by the body's own statement; close |
| #2257 | NOT DELIVERED | #2572 f24895c (`Part of #2257`) | seams (a)-(c), MX4, per-degree copy, mixing; new R10-ADVISOR-RESIDUE (fixes 2257) |
| #2258 | DELIVERED | #2647 14405df | owner items 1-3 answered (#2647 body); the body leaves verification to the orchestrator after merge; close |
| #2259 | NOT DELIVERED | #2401 07a0940 (`Part of #2259`) | #2401's table: item 2's "duplicated spellings of a one-statement rule" not delivered; new R10-ARCHSCORE-SPELLINGS (fixes 2259) |
| #2265 | DELIVERED | #2390 a96f4be | findings e, g, h, i landed with the two countermeasures (#2390 body line 3); close |
| #2269 | NOT DELIVERED | #2631 b24cfe5 (`Part of #2269`) | the two D0 carries from #2612; new R10-BRIEFS-FOLD-D0 (fixes 2269) |
| #2271 | NOT DELIVERED | #2399 0dac0bf (`Part of #2271`) | the sanitise half is R10-DIAG-REDACT's scope; wire #2271 there |
| #2272 | NOT DELIVERED | #2514 0280e6e, #2548 290712e (`Part of #2272`) | no real recorded day: tests/replay/ holds only synthetic-dhw-only.json; new R10-REPLAY-REAL-DAY (fixes 2272, after REPLAY-SCOPED and DIAG-REDACT) |
| #2298 | DELIVERED | #2521 92b5bf4 | docs/index.html declares 792 for the 1056x792 PNG, plus a check over every sized `<img>` (#2521 body line 9); close |
| #2410 | DELIVERED | #2669 5c9828f, 75bd9e6b1 | the family arm no longer re-files a member's occasions and its members list is complete (policy_lint.mjs:2799); policy_lint's stats run re-files in place if the live window is still over threshold; close |
| #2496 | DELIVERED | #2513 929275e | roster_edit.py has `set-after` and `drop-carry` (roster_edit.py header); residuals 3b97e1aa and 7f85b089 go to R10-ORCH-ROSTER-SCHEMA; close |

## D. The permanent check: R10-ROUTING-INVARIANTS

Group JSON: /Users/timmalmstrom/hpo-orch/r10s6/groups/R10-ROUTING-INVARIANTS.json (size M, after none, owner_gate "mandated approval under 6329234399", issue to be created from routing-issues-1/routing-invariants.md).

- Invariant 1 in carry_audit.py, with the consumed-versus-pending mark: every group `carry` entry is pending until it ends in `[implemented: <sha>]` (ancestor of origin/main), `[moved: <GROUP>]` or `[dismissed: <reason>]`. roster_edit.py gains `mark-carry`, and `set-stage` to a done stage refuses while a carry is pending, so a group cannot finish holding unimplemented work. `Dests.check` accepts a done group only for an item that group marked implemented or moved, and prints STRANDED otherwise. A new offline `carry_audit.py roster` subcommand checks every group with git alone.
- Invariant 2 in brief_lint.mjs's roster-shape block (the roster linter): a live group with empty `issues` and `fixes` is an error.
- Invariant 3 stays in `carry_audit.py sweep --issues`, except that a carry file no longer counts as an owner. #201 and the Tracking label are exempt.
- One live predicate: `absorbed` is not in roster_lib.DONE_STAGES (roster_lib.py:33). The group settles that in roster_lib.
- Wiring: governance.yml runs the offline check on every pull request and push, and the issue check on push to main. orchestrator_tick.py's default pass runs the offline check every tick and the issue check at most hourly from a cached list. The CARRY section is opt-in today (orchestrator_tick.py:2061).
- Migration: at merge the orchestrator marks the done groups' existing carries `[implemented: <resume.commit>]` with mark-carry, except the ones this file moved. This file's IMPLEMENTED and NO-OBLIGATION rows are the null control.
