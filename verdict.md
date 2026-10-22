Fix review: blocked e53fee3670d81481bd25d255f3f27365e287c12e mutation-survivor: two fresh mutants outside the sweep's operator classes (the delivery-path prefix widened to dev/programme/, the first-pass seen-set scoped to the window) pass all 76 self-test checks and move figures the body quotes

bus-nonce: 81dae66295437b957b448f2bf182113d

This is **round 4** of PR #2579 (R10-FLOW-YIELD-PROBE), so the next round is the fifth. From the fourth round on, `fixer.md` owes a re-cut, not a repair. This round's change of method counts as a re-cut: the fixer moved from adding a case per mutant to an `ast` enumerator over operator classes. I measured head e53fee3670d81481bd25d255f3f27365e287c12e from a detached worktree. It holds code head 80b4f2760 plus automatic merges of origin/main 93e6a63d2 and dcf12f490. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so this contract is current. `git ls-remote` showed the head still at e53fee3670d81481bd25d255f3f27365e287c12e at 04:47Z.

## Block

- **mutation-survivor (steps 1, 6 and 14).** Round 3 blocked on a class: one-line mutants of `review_strength.py` that pass the self-test and move figures the body quotes. The body says this round "closes the class by enumeration rather than by instance". The enumerator only covers its own operator classes, though. Those classes empty a string literal; they never change one. They also delete a statement but never move one. Two fresh mutants fall outside them. Each passes `review_strength self-test: 76 checks, 0 failed` (ev/mutants_named_fresh.txt). Each moves quoted figures when the body's own bundle command is re-run over the same fetched bus (ev/bundle_diff_F2.txt, ev/bundle_diff_F7.txt):
  - **F2: the delivery-path exclusion is widened.** In `pr_facts`, `f.startswith("dev/programme/delivery/")` becomes `f.startswith("dev/programme/")`. It is a one-line, one-literal edit. The body's `L>=600` stratum `1.10 (22/20), 0.69 (11/16), 0.08 (1/13)` becomes 22/19, 11/16, 1/12. The size re-weight 0.89, which uses L1's per-stratum PR counts, moves with it, because L1 reads L 12, M 14 and S 13 where it read 13/13/13. No fixture PR touches a `dev/programme/` file outside `delivery/`. Emptying the literal is the sweep's only edit of it, and the sweep kills that one.
  - **F7: first-pass is scoped to the window.** In `tally`, `first = v["pr"] not in seen; seen.add(v["pr"])` moves inside `if a <= v["t"] < b:`. That turns "the PR's first verdict ever" into "its first verdict in this window". The body's fixer first-pass `opus 7/22, 2/14, 5/7` becomes 7/22, 5/18, 7/10. The `all` first-pass of P2, L1 and S moves too: 10/35 → 13/39, 17/36 → 19/39 and 4/10 → 8/14. The fixture does re-review PR 6 across windows. No check reads first-pass for a PR whose first verdict falls before the window, so the move passes.

  Fix: add a fixture PR that changes a `dev/programme/` file outside `delivery/`, with its size and product checked. Add a first-pass check on a window that holds a later verdict of a PR first reviewed before it. Then either widen the enumerator's string rule, for example a prefix literal truncated at its last `/`, and add a statement-move class, or state in the body that the class rule is bounded to its listed operators and that mutants outside them are not covered. The sweep's `RESULT` cannot stand as "closes the class" while seams like these lie outside it.

## Findings

- F2 and F7 above are each a self-test case owed in the round-5 fix. Neither is a later-stage finding. Carry: dismissed: owed by this pull request's own next round, stated under Block
- **F4: the cloud id prefix shortened.** `rid.startswith("cloud")` becomes `rid.startswith("clou")`. The mutant passes the self-test but moves nothing on the real bus: the bundle diff is empty (ev/bundle_diff_F4.txt). Telling the two apart would need a bus-confirmed id that starts `clou` but not `cloud`. No such id exists, and no seat writes one. Carry: dismissed: equivalent on the real bus; no reviewer id begins clou without cloud
- **The sweep skips arguments of `print`.** `_text_ids` exempts every constant under a `print(...)` argument, and `main` calls `print(guardrail(verdicts, wins[-1][2], a.guardrail, a.p0))`. So the indices that choose the guardrail's `until` are never mutated as thresholds. I mutated them by hand: `wins[-1][1]`, `wins[0][2]` and `a.guardrail + 1`. The main golden and the "guardrail to the LAST named's" check kill all three (ev/mutants_print_args_out.txt), so no seam is open there. The body's description of what the rule skips ("human-readable text") is wider than what the code skips. Carry: dismissed: every hand mutant there is killed; the description, not the coverage, is loose

## Evidence

- **Named arms (step 1).** I ran my own runner over exact one-occurrence replacements in a second detached worktree at the head, and the file was restored `restored identical: True` (ev/mutant_runner.py, ev/mutants_named_fresh.txt, ev/mutants_print_args_out.txt). Unmutated: `review_strength self-test: 76 checks, 0 failed` (3.11). Every arm round 3 named is killed at this head, with the failing checks the body's table lists:
  - N1: 2 failed. N2: 2 failed.
  - N3: 4 failed. I also used a second form, `key=lambda p: (p, first[p])`, and it gives 4 failed too.
  - N4: 1 failed. N6: 2 failed. N7: 1 failed. N8: 2 failed. N9: 3 failed.
- **Fresh mutants, my own.** 17 in all:
  - Killed: F1 (`blueprint/`), F3 (`-p` suffix), F5 (a REAL_CATCH word typo), F6 (the merges map keeps the oldest), F8 (a binary counted as 1), F9 (parent index 0), F10 (the unreviewed label), F11 (roster not as of T), F12 (`cloud-` suffix), F13 (tie reversed), F14 (window lower bound open), and P1, P2 and P3 in `print` arguments.
  - Survived: F2, F4 and F7, as above.
- **The sweep (the body's class rule), re-run at this head.** Command: `/opt/hpo/venv-ci/bin/python dev/audit/harnesses/r10_review_strength_mutants.py --jobs 8` (ev/sweep_head.txt). It prints `RESULT mutants=799 killed=787 survived=12 disposed=12 undisposed=0 stale=0`, rc=0, the body's figure re-derived, and its 12 dispositions match the body's table. Neither F2 nor F7 is among the 799, because the rule's classes do not generate them.
- **Finder's harness (step 2).** The baseline is the brief's quoted rates, 0.52 over 112 PRs and 0.15 over 47 (the tool does not exist at the merge base, so this end is the hand count). At the head, `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z` prints `PRs 112 verdicts 257 real 58 (0.52/PR) book 65 (0.58/PR)`, and the bundle's `all L` row prints `PRs 47 verdicts 84 real 7 (0.15/PR) book 30 (0.64/PR)` (ev/figures_extra.txt, ev/bundle_head.txt).
- **Null control (step 3).** The bundle printed by the eb9f7e89 tool and by this head's tool over the same fetched bus is byte-identical, `BUNDLE-IDENTICAL` (ev/null_bundle.txt, ev/bundle_eb9f7e89.txt). The tool changes this round therefore move no figure, as the body claims. M0 passes in the sweep.
- **Figures re-derived at this head** with the body's bundle after `--fetch` (ev/bundle_head.txt, ev/figures_extra.txt). The bundle printed `facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`, with 380 verdicts on the bus and 0 outside the grammar. Every quoted figure re-derives and matches:
  - Baselines: 112 / 0.52 (58) / 0.58 (65); 47 / 0.15 (7) / 0.64 (30); 35 / 0.06 (2).
  - L13: 11 PRs, 16 verdicts, 4 real.
  - `all` rows: 43/48, 14/39, 3/39, 5/14, with incidence 25/48, 10/39, 3/39, 4/14.
  - Strata: finding 40/37, 5/17, 1/13; L>=600 22/20, 11/16, 1/13; product True 17/14, 2/9, 1/7.
  - Re-weights, recomputed from the rows: origin (13·40/37 + 6·0 + 20·3/11)/39 = 0.50; size (13·22/20 + 13·17/13 + 13·4/15)/39 = 0.89; product (7·17/14 + 32·26/34)/39 = 0.85.
  - Reviewer kind: cloud 6/31, 3/24, 5/14; local 43/48, 8/14, 0/20. P2 cloud+finding 3/13, local+finding 2/8.
  - Fixer first-pass: opus 7/22, 2/14, 5/7; sonnet 5/15, 0/3, 3/6.
  - Prior-merge: A gives 22 PRs, 33 verdicts, 0 real.
  - Extended list: P2 19/39, L1 8/39; cloud incidence 8/31, 7/24, 4/14; local L1 0/20; POST 24/85.
  - Back-test: 8, 8, 8, 8, 7, 7, 6, 5, 5, 5 of 30, every line `ok`, the lowest 5/30 at P = 0.116.
  - Self-test: 76 checks, 0 failed.
- **Not re-derived.** I did not re-run the body's local Red-checks figures (2382 entity checks, 109 harness-header checks, 74 wired, the structure ratchet). CI's runs on this head are cited instead (fix-review step 11).
- **Steps 4 and 5.** The PR touches neither VERSION, the manifest version, RELEASE_NOTES.md nor either claim file: the three-dot diff from merge base dcf12f490 lists 7 files, none of them these.
- **Step 7.** The body's `## Head` names e53fee3670d81481bd25d255f3f27365e287c12e, the head I measured. Its structure checks out: 6bd5444d6 merges 80b4f2760 into eb9f7e89d, and e53fee367 merges dcf12f490 into 6bd5444d6. The fixer's own commits are 4a64049e0 (the self-test, two tool fixes and the sweep) and 80b4f2760 (the closures entry).
- **Step 14.** The `tests/closures.json` +1 this round is an `inert_reads` entry for `tests/harness_headers.py`, which reads every file under `dev/audit/harnesses/`. It only widens what runs when the file is touched. No budget, score, ledger or claim file moves.
- **Merge-tree (step 13).** `git merge-tree --write-tree origin/main e53fee3670d81481bd25d255f3f27365e287c12e`, with origin/main at 1602f9342, is clean: exit 0, tree 435b72882308 (ev/merge_tree.txt). No absorb is owed.
- **Carry audit over the body.** `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` prints `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (ev/carry_audit_body.txt). The roster ref is 306a96d5f21f.
- **Roster check for my own carries.** origin/main's roster has no R10-FLOW-YIELD-PROBE group: 108 groups there against 144 on the handoff roster (ev/roster_groups.txt). So none of my carries names that group. Every item above is dismissed with its reason, because each is either owed by this PR's next round or settled as equivalent. R10-ORCH-MACHINERY is present and open on both rosters.
- **Forward-carry (step 10).** At roster 306a96d5f21f, R10-ORCH-MACHINERY's carry holds "From #2579 (item b8b28b28): the yield-probe guardrail (threshold, extended class list, seat-family arm, planted-defect calibration), and the reviewer model is unrecorded in the ledger. Control: a planted defect of each class must trip the guardrail, and a null window must not." The control is stated as a precondition (ev/roster_carry.txt).
- **Red checks (step 11).** I read 41 check-runs at this head at 04:46Z (ev/check_runs.tsv):
  - 23 success, 13 skipped, 1 neutral (CodeQL) and 3 still in progress: `fast (3.14)`, `coverage` and `Analyze (python)`.
  - Both `pr-contract` runs are success, as are instrument-self-tests, closure-scope, mutation, arch-score, budget-raise-gate, delivery-status and wave-script.
  - `nightly-status` is red. It grades main's scheduled run, this diff reaches nothing it reads, and the body answers it. It is not this PR's.
  - The intermediate commits 7f251a783, 4a64049e0, 80b4f2760 and 6bd5444d6 carry no check-runs (ev/check_runs_range.txt).
  - No gate check is red, so no root-cause answer is owed. The block does not rest on CI.

RESULT selftest=76/0 named_mutants=8/8_killed own_mutants=17 own_killed=14 own_survived=3(F2,F4,F7) sweep=799/787/12_disposed survived_moving_body_figures=2(F2,F7) body_figures_reproduced=all_quoted null_bundle=identical carry_audit_body=0_unrouted merge_tree=clean ci=3_in_progress,nightly-status_red(main) round=4
