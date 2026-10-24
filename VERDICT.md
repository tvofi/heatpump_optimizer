Fix review: blocked 859b74ba8ab4d0020025895b73a53b3833b5e74c carry-missing: not carried to R10-ORCH-ROSTER-SCHEMA or R10-FLY-CLOUD-SETUP-TOOLCHAIN, the body's two Forward-carry destinations are in no roster at origin/main 9586fce08 or handoff/audit-r10-roster db3e513ec

bus-nonce: ccf3f54a7b7489266de0d1950bcaa46e

Round 1 (no earlier `verdict/2704` ref and no verdict comment on the PR). Measured head `859b74ba8ab4d0020025895b73a53b3833b5e74c`, re-read as the PR head when this was written. Merge base `ac5788f2617755631f14e4d1a31efab0e47aa820`. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract read is current.

## Block

`fix-review.md` step 10 and `finding-propagation.md` Enforcement: "The producing PR does not merge until the carry is in the tree ... The body names the file, the stage and (a roster carry) the branch SHA."

- `## Forward-carry` item 1, the roster's "Identity and flow" boilerplate (64 briefs), routed `Carry: R10-ORCH-ROSTER-SCHEMA`. That group's `carry` and `brief` hold no such entry at origin/main `9586fce08` or at `handoff/audit-r10-roster` `db3e513ec`. The only roster copy is this group's own `R10-POLICY-FIXER-MD` carry[9], and that becomes undispatched once this group merges. The body says "This seat writes no roster ref" and gives no branch SHA.
- `## Forward-carry` item 2, `BASH_ENV` (#2452), routed `Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN`. None of that group's carries names `BASH_ENV`. Its existing entries (#2572, #2554, R10-BRIEFS-FOLD, #2629) are PATH and venv frictions, not this precondition. The only roster copy is again `R10-POLICY-FIXER-MD` carry[4].
- `carry_audit.py check --body` passes (4 routed, 0 bad destination(s)) because both destination groups exist and are `not-started`. It does not read whether the text landed, so it does not settle this.

Repair: a `roster_edit.py append-carry` per destination on `handoff/audit-r10-roster` (standing-roster), with each control and precondition as the body states it, and that branch SHA named in the body. No code change is needed. Everything else below checks out, so a re-review after the carry lands should only need to confirm it.

## Findings

- The body's item 11 figure `median of 98 min` and `6640 min` sum do not re-derive under my rebuild of its stated input. I used commit times via `%cd` in UTC, with each ref's `Fix review:` subjects de-duplicated by line. That gives `SUM class-open 27 entries 6297 min` and a median of 126 min over 25 timed entries (119 min if the 2 untimed entries count as 0). `27`, `18 PRs` and `#2283 = 3` reproduce exactly. The difference is the timestamp source (author time vs commit time), which the body does not state. One more block is spelled `harness: class-open:` with a colon. rounds.py keys it apart (`SUM harness:class-open: 1`), so a 28th class-open block exists under a variant spelling. The disposition (refuse an unconditional step 8) does not turn on either figure. Carry: dismissed: a disclosed one-seat re-measurement of a refusal's supporting figure, whose decision stands on the 27/18 counts that do reproduce
- Mutant 2b's reading differs from the body. Restoring `finding-propagation.md`'s cut "adjective" clause, rewrapped to the same 2 lines and regenerated, gives `TOTAL: 1 error(s)` (tokens 1348 > 1336), not the body's 2 (it adds no line). The body's mutant apparently also added a line. Either way the payment is shown to be needed. Carry: dismissed: mutant shape difference, same conclusion

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 859b74ba8` exits 0 (tree `ff621679c`) against origin/main `9586fce08`. No conflict (`ev/merge-tree.txt`).
- RESULT step 5: the diff touches no `VERSION`, manifest or `RELEASE_NOTES.md`. Files: `fixer.md`, `fix-review.md`, `finding-propagation.md` and its two generated copies, plus `dev/programme/delivery/2704.md`.
- RESULT budgets head: `fixer.md 314/315 5215/5216`, `fix-review.md 140/140 2445/2451`, `finding-propagation.md 101/101 1332/1336`, `TOTAL: 0 error(s) across 50 policy file(s)`. All match the body.
- RESULT budgets merge base `ac5788f26`: `312/315 5169/5216`, `139/140 2420/2451`, `100/101 1335/1336`, `TOTAL: 0`, wave-script `209 passed, 0 failed`. These equal the body's null at `50af6174f` (`ev/mb-checks.txt`).
- RESULT head checks: `rules_sync --check` ok, `check-wave-script 209 passed, 0 failed`, `STRUCTURE RATCHET PASSED`, `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (`ev/head-checks.txt`).
- RESULT mutant 1 (main's `finding-propagation.md` source, copies left as branch): `RULES-SYNC: 2 file(s) out of date`. Killed.
- RESULT mutant 2a (`fixer.md` #386 sentence restored): `fixer.md 315 315 5249 5216`, `TOTAL: 1 error(s)`. Killed, and matches the body.
- RESULT mutant 2b: killed, with 1 error, not 2 (see Findings).
- RESULT mutant 3 (step 6 re-spelled `harness: class-open <seam>`): `209 passed, 1 failed`, `FAIL fix-review.md teaches "class-open" as a reason under another class`. Killed, and matches the body. Worktree restored clean after all mutants (`ev/mutants.txt`).
- RESULT factual claims (`ev/claims.txt`):
  - `tests/mutation_table.py:104 PKG = "custom_components/heatpump_optimizer/"`.
  - `git grep carry_audit tools/pr/prepr.sh` rc=1, and `ci_predict` is found at 436, 446 and 453.
  - `ci_predict.py --apply-inert` exists.
  - `tests/mutation_ledger/survivor_triage/` exists.
  - `nudge.md` section 9 states the DIRTY / merge-tree absorb rule.
  - prepr 6f "Reads the committed tree at HEAD".
  - `handoff_push.sh` opens the PR via `app_push` and writes the row.
  - `tests/structure.py` docstring says "the largest class span".
  - `ci.yml` has the `labeled` trigger, and `kernel-points.yml` has its push arm.
- RESULT roster boilerplate: 64 groups whose brief matches `the seat pushes refs only, through [`]tools/audit/seat/handoff_push.sh`, 18 of them not `done` (15 not-started, 3 in-progress). Matches the body.
- RESULT item 11: 223 `verdict/*` refs now (214 at the fixer's fetch). `SUM class-open 27 entries`, on 18 PRs, with #2283 at 3, #2345 at 3 and #2406 at 2. `harness:class-rule-missing 2` (`ev/item11-rounds.txt`, rounds.py from origin/main run on `ev/item11-tsv/`, my own rebuild of its input from ref commit subjects, disclosed per step 9).
- RESULT carry_audit: `4 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry_audit.txt`).
- Step 6, class: the body's rule is "every line of #2378 plus this group's roster carries". Each issue number #2378 cites appears in the body. I did not independently re-derive the 11-line split from `policy_lint.mjs --stats`.
- Step 14: no metric moves. Budgets are untouched (`policy_budgets.json` is not in the diff), and every added line is paid by a cut in the same file, as shown by mutants 2a and 2b. No `closures.json`, INERT or claim-file change.
- Step 11, CI on the head (`ev/check-runs.txt`, `ev/workflow-runs.txt`): every concluded check is success or skipped, and none is red. Still in progress when read: `tests / closures`, `tests / fast (3.14)`, `tests / coverage`, `governance / instrument-self-tests`, `prelude`, and workflows `CI code` and `CI edit`. No `pr-contract` or `gate` run had concluded. No red check is owed an answer at this reading. The body's `## Red checks: none` predates CI, which is consistent.
- Step 12: the head re-read from the PR API is still `859b74ba8ab4d0020025895b73a53b3833b5e74c`.
