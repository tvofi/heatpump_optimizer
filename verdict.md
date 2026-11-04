Fix review: merge 9f6d90798e73c858619bf01d78bc2f1a626b92a3

bus-nonce: a975e22c14d7a5537786f3ec2bc4e3cb

## Round

Round 2 (delta) of #3206 (R10-RCA-GATE-STALE / R10-HOTFIX-GATE-STALE-JOBS), measured at head 9f6d90798e73c858619bf01d78bc2f1a626b92a3; the head was still the PR head when this verdict was written. Round 1 blocked a615a76f (root-cause-detectable: tests / closures) on the body alone, with no fault in the code.

## Evidence

- Delta (ev/delta.txt): the commits from a615a76f to the head that are not on main are 79ac5afb (github-actions[bot], "ci: re-record closures", tests/closures.json +5 lines only), cf0a4a8a (hpo-fixer, merges origin/main d4e584ec6) and 9f6d907 (merges cf0a4a8a). Both merge trees equal `git merge-tree --write-tree` of their parents (2d5af384), so the branch adds no change of its own beyond the bot re-record. No production or harness file changed after round 1.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden/ are untouched over the three-dot range.
- Merge (ev/merge-tree.txt): `git merge-tree --write-tree` against origin/main 2a9cd347 gave rc 0, and against ce7a6bac (re-fetched before writing) also rc 0. On the second run the ledger driver printed `LEDGER-MERGE: resolved tests/closures.json`. Neither run touched a claim file.
- Finder's harness, unchanged (ev/harness-head.txt, ev/harness-main.txt): `python3 -I dev/audit/harnesses/r10_gate_stale_jobs/harness.py` printed `mismatches 4 of 9` (rc 1) at the head. Given an origin/main 2a9cd347 worktree as its argument it printed the same, byte-identical. This is as expected: the PR is the RCA harness, not the fix.
- Body checks: the body now names `tests / closures` (UNDER-SCOPED, answered by ci-autofix 79ac5afb) and `pr-contract / pr-contract` and `gate` with their answers. It corrects the INERT sentence (the five .py files are measured closure members) and retracts the "0 script(s) run" line. It also states the rounding for "about 47 min": attempt-1 lags rounded up to the 60 s poll, with the reviewer's 45 min and 39.7 min unrounded quoted.
- Scope re-derived: `python3 tests/closure.py select --diff origin/main` at the head printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, matching the body.
- Class count re-derived: tally.py printed `scanned runs 1000 red gate attempts 383` with only-prelude-None 12, only-PENDING-this-run 6, ABSENT-this-run 1 and PENDING-plus-other 2, matching the body. An offline count over reasons.jsonl, under recover.py's own predicate, gives 19 attempts and 14 false reds, matching the body.
- Not re-derived: "170 min 4 s over 10". recover.py reads the live jobs API, and here it crashed on HTTP 502s and on the proxy's refusal of numeric-ID paginated paths. That is an environment limit, not a script defect, and the delta does not touch this figure.
- CI (ev/classify.txt): `GREEN 9f6d90798e73c858619bf01d78bc2f1a626b92a3 pending: none red: none` (merge_train classify, rc 0).
- Red checks at this head (ev/check-runs.tsv, 55 runs, every page): the only concluded red is `tests / nightly-status` failure. The body names it as inherited from main, and the diff reaches nothing it reads. `tests / closures`, `pr-contract / pr-contract` (twice, completing 20:54:48 and 20:57:17, both after the red's 20:21:36) and `gate` (twice) are success, so that pr-contract run is the evidence that the body check passed.
- Mutation: the diff writes no production line, so no step-1 mutant applies. The harness's own mutants were checked in round 1 and are not touched by the delta.

## Findings

- Residual: the body's `## Red checks` header scopes its list to 79ac5afb, not this head. At this head the only concluded red is `tests / nightly-status`, which the body names, so the list is complete for this head. Carry: dismissed: wording only, the set of reds at this head is fully named
- Residual: "about 47 min" re-derives as 45 min under the rounding the body now states. The body discloses this, and the cost-test verdict (build) does not move. Carry: dismissed: the cost-test verdict does not move
- Follow-up: the handoff-column results (3 of 9) and the `a6305aa29` figures were not re-run in either round, so only the main column is verified. Carry: R10-HOTFIX-GATE-STALE-JOBS
- Follow-up: the two fail-open readers named in the doc, `codescan_wait.py`'s own-run path and `pr-contract.yml`'s red list, are unmeasured and carried; the body's carries resolve on origin/handoff/audit-r10-roster (CARRY-AUDIT: 3 routed). Carry: R10-HOTFIX-GATE-STALE-JOBS

## Friction

- recover.py's live `gh api --paginate` calls fail behind the cloud proxy, on HTTP 502s and numeric-ID pagination, so the recovery-minutes figure cannot be re-derived from a cloud seat.
