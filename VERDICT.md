Fix review: blocked feacede17c5e1eb6b7e399bf87a2efea3ea79cc7 gate-red: tests / mutation still refuses at this head on the null-control arm, which only a change to the code-owned tests/mutation_table.py can clear, and the body routes that fix to a roster that does not hold it

bus-nonce: d451491dae5ebba811d19c1650d604fa

## Block

- `tests / mutation` (job 124161424410) concluded failure at feacede17c5e1eb6b7e399bf87a2efea3ea79cc7. Its log reads `3620 unpinned site(s) of 6579 candidate sites, 3620 at the ratchet base ca0a6cfbc`, so the round-1 ratchet block is cleared. It then stops at `MUTATION TABLE REFUSED -- no full-line comment in any file in the pool, so the run has no null control`. The required `gate` check needs every unit through `pr-contract`, and `tools/ci/gate.py` exempts no `mutation` unit, so this head cannot go green.
- The body says so itself under `## Red checks`: "It is still red ... Not repaired in this head". Under `## Forward-carry` it says "this PR needs that fix merged first, or the orchestrator's call".
- Cause confirmed at the head: `null_control` (tests/mutation_table.py:2136-2165) takes only a whole-line comment whose full line, indentation included, is under 60 characters. No such line exists in `button.py`. Line 43 is 66 characters. Line 109 is short only once stripped, and with its 12-space indent it is over 60. The diff does not touch tests/mutation_table.py, and neither does main since the merge base.
- The forward-carry is not where the body says it is. The body routes the null-control gap to "dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster". At that ref (a7393655c, 2026-10-30 16:49 +0100) the roster carries the P9 localStorage leak and the "driving scale" widget, but nothing on the `null_control` 60-character cap, `--pin-killed` refusing this pool, or #2997 (step 10).
- What clears this:
  - (a) an instrument fix to `null_control` merged to main first (code-owned; the orchestrator assigns it), then this PR merged with main and `tests / mutation` green; or
  - (b) the orchestrator's recorded call on merging over this unit.
  - In either case, the gap has to be on the roster first. Writing a `button.py` comment to fit the tool is what the body rightly declined to do.

## Findings

- Instrument gap: `null_control` in tests/mutation_table.py accepts only a whole-line comment whose line is under 60 characters, with no recorded reason for the cap. Any pull request whose changed pool holds no such line fails `tests / mutation` and `--pin-killed`/`mutation-autofix` whatever it pins. `ci-autofix.md`'s table omits this case. It is not on the roster yet. Carry: R10-UX-HEALTH
- The cheaper detector the body names is not built: a `null_for` pre-check over the pool in `prepr.sh` step 6d / `tools/pr/ci_predict.py`. Without it the refusal first shows in CI (defect-root-cause.md, second trigger). Carry: R10-UX-HEALTH
- The three ledger rows were made with an out-of-tree scratch script, `python3 hand_pin.py`. `figure_lint` reads it as `unverified ... does not look like a path in this tree`. Decision 0013 says reusable instruments land in tree, never only in /tmp. The fix to `null_control` should make it unnecessary. Until then, a pool-specific null-control override for `--pin-killed` would be the instrument. Carry: R10-UX-HEALTH
- P9 grid state leak (carry 17) and the 375-px chart collision it hides: withheld by the body. It is present on the roster. Carry: R10-UX-HEALTH
- The "driving scale" widget is not built and waits on orchestrator confirmation. It is present on the roster. Carry: R10-UX-HEALTH
- #2499 no-meter over-booking (body: plan/deliv 1.908) is not met. I did not re-derive that figure. Carry: #2499

## Evidence

- Round 2 of #2997. Round 1 (probe/rev-2997-b8365800, f7452d867) blocked 7c43d8fb1 as `mutation-unpinned`.
- `review_carry.py 7c43d8fb1 feacede17` prints FRESH-REVIEW. Of the three branch-only commits, one carries code: 7fed51072, three `killed_by` rows only. The other two are merges.
- Dispatch note: PROMPT.md at dispatch/reviewer-rev-2997 (d551c6dbd) still names head 7c43d8fb1 and nonce b8365800. The scheduled task names head feacede17c5e1eb6b7e399bf87a2efea3ea79cc7 and nonce d451491d, and feacede17c5e1eb6b7e399bf87a2efea3ea79cc7 is refs/pull/2997/head. So this review is of feacede17c5e1eb6b7e399bf87a2efea3ea79cc7, under that nonce, by the brief's procedure.
- Head measured: feacede17c5e1eb6b7e399bf87a2efea3ea79cc7, the PR head when read. The packet's base is d99cadb12. origin/main is ca0a6cfbc, which is also the merge base. `dev/governance/roles/` does not differ between the merge base and main.
- `git merge-tree --write-tree origin/main feacede17c5e1eb6b7e399bf87a2efea3ea79cc7`: rc=0, tree a661b9dfd, no conflicts (ev/merge_tree.txt).
- VERSION, the manifest, RELEASE_NOTES and both claim files are untouched (three-dot).
- Pins re-killed by hand in a worktree at feacede17c5e1eb6b7e399bf87a2efea3ea79cc7 through `tests/debug_collect.py`, with PYTHONPATH=tests/hastub (ev/mut-pins.txt):
  - Baseline: ALL 159 PASSED, rc=0.
  - 226 GUARD_OFF: AttributeError, rc=1.
  - 228 GUARD_OFF: 1 of 159 FAILED, rc=1.
  - 230 RETURN_DEL: 2 of 159 FAILED, rc=1.
  - Null control button.py:43 + " (null control)": ALL 159 PASSED, rc=0.
  - All match the body and the three rows' `reason` fields.
- The behavioural mutants (openSetupSlot render, cfgPage fallback, healthModelTitle, button final branch) were verified in round 1 at 7c43d8fb1. No production or test line moved since; only ledger rows and main merges.
- `tests / mutation-autofix` at this head is green: `skip-not-unpinned -- nothing owed to a human`. `mutation-pins (1)` is green.
- CI at review time: red `tests / mutation`. Green: browser, typing, arch-instrument, arch-score, budget-raise-gate, delivery-status, policy-docs, env-matrix, wave-script, hassfest, validate-hacs, briefs, closure-scope, nightly-status, mutation-autofix and mutation-pins. In progress: `tests / fast (3.14)`, closures, coverage, `governance / instrument-self-tests` and `codeql / Analyze (python)`. No `pr-contract` or `gate` run is listed yet. The red above is read from the check-runs API.
- `## Red checks` names and answers both round-1 reds. It names a cheaper detector, which is not built (see Findings).
- Not re-derived: the scoped-gate count (16 run, 17 scoped out), the #2499 harness figures and the P9 grid counts (850/1190 pairs, 30 entries). I have not verified them.
- No finder's harness is named (the packet says "none named"). I built no instrument.
- carry_audit.py check was not run on this verdict: the session's frugal-routing hook (guard_inline.py) refused the call, and I did not work around it.
