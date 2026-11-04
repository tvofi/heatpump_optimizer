R10-PREPR-CAP slot arm: `tools/pr/prepr.sh` takes its heavy slot lazily, just before its first heavy step that is not skipped, instead of for the whole run (carries 25 and 26). It also refuses a body whose `## Head` names another sha before any heavy step (carry 23) and pins the interpreter-spawn cost of step 6g (carry 24). Carry 6 was already built at the merge base. Roster carries 7, 12, 15, 16, 19 and 20 of this part are not built here and stay open on the roster. Round 2 repair of verdict/3191 round 1 (blocked: step 3f3 unleased, `closures_owes_slot` undriven). Closes #2267.

## Head

1584530f3a83f01bf1e96dc02a29a1dd50841d5b (code head: the PR head 5640ad9d0 merged with origin/main 8e90d8144, plus the repair commits; origin/main had not moved when the final prepr ran).

## Mutation proof

Each mutant is a detached worktree of the head with one production edit, run as `PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test` in place (not a /tmp copy). Unmutated head: `486 passed, 0 failed`. Failing rows:
- A, `return 1` as the first line of `closures_owes_slot` (the recorder never takes a slot): red `closures_owes_slot: a scoped diff with scripts, on a machine that records, owes the slot`.
- B, `[ "$k" = scoped ]` changed to `[ "$k" = full ]` in `closures_owes_slot`: red the same row and `and a full diff owes none (CI re-records every closure)`.
- C, delete `SLOT_TAKEN=1` in `take_slot` (the reviewer's follow-up mutant): red `a failing slot-take is attempted once across two take_slot calls (no re-queue on the WARN path)` (got 2) and `and the unleased marker is written once`.
- D, delete the `take_slot` call in step 3f3's else-arm: red `the main flow calls take_slot at the mutants, field coverage, self-test, closures and diff-mutants steps ...` (got 4, wanted 5) and `a plan where the mutants skip and field coverage runs takes the slot before 3f3's recorder`.
- Round 1's mutants (unconditional take at 1b, per-target interpreter in 6g, `if false` in 1a3) are not re-run: their rows are unchanged by this repair.

## Null control

- `closures_owes_slot` rows drive the production function over a throwaway repository whose `tests/closure.py` stub writes the case and scripts it is told: scoped with scripts and records-here gives 0; skip, full, records-here false, and scoped with empty `affected.scripts` each give 1 (the last is the null control for the scoped arm).
- Step 3f3: the production 3a and 3f3 blocks evaluated with `heavy_skip` answering mutants skip and field coverage run log `skip mutants, take, run field_coverage.mjs`; a plan skipping both logs no take (null control).
- 3f5 (register check, `fold_ledger.py`) stays unleased on purpose, stated in the code beside the step: it is light (about 0.5 s per call, the reviewer's own figure), so a queue wait would cost more than the work. 3f3 measured 234 s idle by the reviewer (`ev/step-timings.txt`, not re-measured here).
- Unmutated tree: the idempotence and inherited-slot rows from round 1 pass unchanged.

## Figures

- Self-test: `PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test` prints `486 passed, 0 failed` at the head (round 1: 477; the nine new rows are the 3f3 take, its null, five `closures_owes_slot` rows and two mutant-C rows; the call-site count row changed 4 to 5 in place).
- Call-site rule: `grep -cE '^ *take_slot( |$)|&& take_slot$'` over the main flow equals 5 (mutants, field coverage, self-test, closures, diff mutants); the self-test row computes it.
- Heavy_skip-gated steps enumerated by `grep -n 'heavy_skip "' tools/pr/prepr.sh`: mutants (leased), field coverage (leased in this diff), register check (light, unleased by decision above).
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2602 ENTITY CHECKS PASSED`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`, run above).
- Not measured: slot-wait minutes per prepr over a day, owed after merge (the reviewer's follow-up, Carry: R10-PREPR-CAP).

## Approval

Policy files `dev/governance/rules/gate-scoping.md` and `dev/governance/roles/nudge.md` change (and their generated copies): both state that prepr takes a slot at its first heavy step. They are unchanged by this repair. Needs the owner's approving review (tvofi).

## Red checks

`tests / nightly-status` is red and inherited: the diff does not reach what it reads, and it is not a required check. No other concluded check is red at the previous head 5640ad9d0 (the checks at the final head are rerun after the push).

## Forward-carry

none

## Friction

none
