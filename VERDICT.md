Fix review: merge e1a6bedad8dfa5a2b29c51c40022456ca241da81

bus-nonce: a3dfbc941942c25a01a43561d25a7705

## Summary

Round 1 of review. This PR changes governance and audit tooling only (`.claude/workflows/audit-find.js`, `tools/policy/check-wave-script.mjs`, `finding.schema.json`, `COMMON.md`, `dev/audit/README.md`, a planted harness, one policy budget raise). It does not touch `custom_components/`. Reviewed in a detached worktree at e1a6bedad8dfa5a2b29c51c40022456ca241da81, which merges the authored code head 2c54bbc78547d241f2a45b3fca381a929a77d655 (an ancestor of the head, as the body says). The diff is against merge base 921214bf4246338c1a83fbc5269eaa0bfe91b7d5.

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main e1a6bed` (origin/main 6aa7ddc712) exited 0. The only driver line was `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt, ev/lints-merged.txt).
- Role contracts: main's `fix-review.md` differs from the merge base's copy. I reviewed to main's copy, which `role_pack.py render` read from this checkout of main.
- Version files: the three-dot diff touches none of `VERSION`, the manifest or `RELEASE_NOTES.md`.
- Claim files: the diff touches no golden or claim file, so the `env_drift.py --all` comparison has nothing to compare.
- Grader: `node tools/policy/check-wave-script.mjs` printed `249 passed, 0 failed` at the head and again on the head merged with origin/main (ev/grader.txt, ev/lints-merged.txt). The body's 249 is re-derived.
- Mutation proof (ev/mutants.txt). Each mutant was applied at the head, graded with check-wave-script.mjs, then restored. Every one exited 1:
  - The PR's own three: `CADENCE` re-added in the DISPATCH block failed `the driver declares no cadence`. `denominatorGaps` renamed failed `...and the driver enforces it`. The schema dual edit (`enumerator` dropped from `required`, then `fold_ledger.py sync`) failed `the finder report schema's coverage rows require the denominator`.
  - Seven of mine:
    - intake refusal deleted: 1 failed
    - retry refusal (`reports[s.id] = null`) deleted: 1 failed
    - overdue check deleted: 1 failed
    - `examined > universe` guard dropped: 1 failed
    - `not_reached` closure check dropped: 2 failed
    - `carryOf` always empty: 4 failed
    - `denominatorGaps` returning no gaps: 17 failed. This sed also hit `boxGaps`' `return gaps`, so the count overstates the mutant; the six single-line mutants above isolate each guard.
  - No survivor.
- Planted control: `python3 dev/audit/harnesses/r11_denominator_planted.py` printed `driver_refuses_bare=1`, `driver_passes_full=1`, `reader_rows=2`, `reader_counted=1`, `reader_counts_bare=0`, matching the body (ev/planted.txt). The harness is the fixer's, written in this PR. The finding is a contract change and has no separate finder's harness. The grader arms are the detector.
- Lints at the head (ev/lints-head.txt):
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 52 policy file(s)`
  - COMMON.md row: 114/114 lines, 1697/1697 tokens
  - corpus: `~69824` against `69833`, as the body says
  - `structure.py`: `STRUCTURE RATCHET PASSED`
  - archscore: `dS +0.0000 NULL`
  - `rules_sync --check`: ok
  - `brief_lint`: rc 0
- Lints on the head merged with origin/main 6aa7ddc712: `TOTAL: 0 error(s) across 51 policy file(s)`, corpus `~66293` against `66726`.
- Budget raise (step 14): COMMON.md's caps rise from 108/1598 to 114/1697. The added text is the owner-ordered denominator section. The Budget section, the schema restatement and the motivation clauses are already cut, as the `## Raise justification` lists. I found no cut the body missed that both improves the text and keeps the rule. The raise is not `metric-gamed`. Its approval follows this verdict at `budget-raise-gate`.
- Class (step 6): one seam, the coverage-row contract.
  - The other readers of the old `depth` coverage are the round-10 intake script `dev/audit/rounds/round10/intake/intake.py`, a frozen round artifact, and `carryOf`, which reads round 10's depth words and hands the whole step over. The grader pins that (`carryOf at round 11 reads round 10: the whole step for M1`).
  - `audit-verify.js` reads no depth.
  - Widening the patterns to D16 and D17 without wiring is dispositioned in the body to R11-PRE-NEW-DIMENSIONS.
- Carry 31 removal from `dev/audit/README.md`: `D11.md:86` and `D13.md:51` both name the convergence scorecard, so the carry is spent as the body says.
- Red checks: the body answers `budget-raise-gate`, `policy-docs`, `env-matrix`, `instrument-self-tests`, `graders-head-copy` and `fast (3.14)` from earlier heads, each with one cause and with a detector or none. `merge_train.py owed-reds` was read.
- CI: `merge_train.py classify e1a6bedad8dfa5a2b29c51c40022456ca241da81 --pr 3647` returned rc 4: `APPROVAL-OWED e1a6bedad8dfa5a2b29c51c40022456ca241da81 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.tools/audit/briefs/COMMON.md: 108 -> 114 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request`. The only red is the budget raise's approval, which follows this verdict, so I judge the head GREEN (ev/classify.txt).
- Head re-read before return: the branch `fix/r11-pre-finder-contract-pr` is still at e1a6bedad8dfa5a2b29c51c40022456ca241da81 (ev/head-reread.txt).
