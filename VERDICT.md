Fix review: blocked f41e5a5f4a674977970d63400b38cac3f6f321cf mutation-vacuous: supply_tick's new-step guard (pump_arbiter.py:1243) survives GUARD_OFF under features.py and harness_headers.py, and its ledger pin killed_by tests/harness_headers.py does not reproduce

bus-nonce: f8445e5ab6e6df0783bd3d7c60a5fcef

## Block

This is review round 4 of PR #2968. The earlier blocks were `d26a00aa2` (mutation-vacuous), `ddf75aaf8` (ci-red) and `9fe3c4cf8` (mutation-vacuous, R3). From this round, `fixer.md` ("Past three rounds, re-cut rather than repair") owes a re-cut under a `## Re-cut` note, not another repair. `bus.sh` refuses a later dispatch at 4 blocked rounds unless the orchestrator splits the PR, closes it, or passes `--past-three <reason>`.

What this round was asked to clear is cleared. Commit `343f2abcf` adds two gate cases and their null controls. Mutant R3 is the tick wired around `_write_supply`. At this head it goes red on both new checks: `2 of 4622`, on `the step tick inside MIN_OFF of an early cut-off writes no turn_on ...` and `the step tick writes nothing at a step the plan turns off while the pump's mode blocks both channels`.

The block is a different site that this PR adds. Its own CI run on this head flags it:

- **The site.** The guard is `pump_arbiter.py:1243`, in `supply_tick`: `if held.supply is None or held.supply[0] == step: return`. It is the design note's "a tick that finds a new step". Without it, the tick rebuilds `wiring.inputs()` and re-derives the step's command every minute inside a step. It would also act mid-step whenever `step_supply`'s answer changes inside a step, for example when a boost ends.
- **The mutant.** `if False:`, applied as one `str.replace` asserted to match exactly once, in a fresh worktree of this head.
  - `tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED` with rc=0.
  - The whole `tests/features.py` prints `ALL 4622 FEATURE CHECKS PASSED` with rc=0.
  - Files: `ev/mutant_S1243_*.res`, `ev/S1243_summary.txt`, `ev/driver2.py`.
- **The false ledger row.** `tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.dcaaed0d.json` (`ev/`) says `killed_by: tests/harness_headers.py` with `rc=1 failed=1`. The CI bot pinned it at `4a049adf0`. At this head that kill does not reproduce.
- **What CI said.** The `tests / mutation` lane on this head (check run 124107634626) printed `PIN NOT REPRODUCED ... supply_tick GUARD_OFF dcaaed0d: pinned to tests/harness_headers.py, LIVES -- a human re-pins, triages or adds the test` and `1 survivor(s) of 8 evaluated = 12.5%, cap 20.0%` (`ev/ci_mutation_log_excerpt.txt`). The lane is green only because the survivor is under the cap, not because the site is killed.
- **The body.** The body counts this site among the pins ("`supply_tick` GUARD_OFF (two sites)") and does not disposition it.

What clears it is one of two things:

- a check, through the real coordinator, that this mutant turns red, such as a tick inside the same step that writes nothing and does not rebuild the inputs, or a boost ending mid-step that writes nothing before the boundary; or
- a proposed `equivalent` survivor triage in the body for a reviewer to judge, replacing the false pin. `ci-autofix.md` forbids automating that triage.

## Findings

- The supply_tick:1243 guard is unkilled behind a false ledger pin. This is the block above, owed by the fixer before the next handoff, inside the re-cut that round 4 requires. Carry: R10-SAV-ACTUATION
- The body does not describe this head's own change. `## Head` names `343f2abcf` as the code head, but no section gives its mutation proof (R3 red) or re-takes the figures. "Review round 3" still quotes `4598` checks, and this head runs 4622. `fixer.md` step 7 requires every executed number in the body, and the round-4 re-cut replaces the body anyway. Carry: R10-SAV-ACTUATION
- The pin-killed bot wrote a row that no longer reproduces at the head of the same branch. It was recorded by `ci: pin killed mutants` at `4a049adf0` and lives here, under the same driver and under `features.py`. I did not establish why it was killed there; it could be a flaky driver or a later change. Whether the bot should re-verify a pin before writing it is the instrument's question, not this fix's. Carry: dismissed: the mutation lane's own pin re-verification already catches it (PIN NOT REPRODUCED on this head), so the defect surfaces without a new detector
- The duty ledger still books the first reading of an OFF step after an ON step from the previous step's tail. Both phases book such a step `space-instead`; see `ev/harness_head.txt`. The body routes this to #2492, which the PR leaves open with `Refs`. Carry: #2492

## Evidence

- RESULT head-measured `f41e5a5f4a674977970d63400b38cac3f6f321cf` (`ev/HEAD.txt`). `git ls-remote` printed it as the branch head at 14:17 UTC, and nothing moved it during the review.
- Roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current. The merge base is `e77418f9b` (origin/main).
- RESULT delta. Against the last reviewed head `9fe3c4cf8`, the branch's own production diff (`custom_components/`, three-dot against each merge base) is byte-identical. The code delta is `343f2abcf` alone: `tests/features.py` +74 (`ev/cheap_checks.txt`).
- Mutants, each one exact-once `str.replace` in a fresh worktree, running the whole `tests/features.py` (`ev/driver.py`, `ev/mutant_*.res`, `ev/features_*.summary.txt`):
  - RESULT NULL: `ALL 4622 FEATURE CHECKS PASSED`, rc=0.
  - RESULT R3: tick wired around `_write_supply` to `switch_supply`. `2 of 4622`, on the two new gate checks. Cleared.
  - RESULT R1: `allow_on` dropped in `_write_supply`. `2 of 4622`, on the cycle MIN_OFF check and the new tick MIN_OFF check.
  - RESULT R4: `supply_write`'s OFF skip forced off. `3 of 4622`, on the two cooling checks and the new tick blocked-mode check.
  - RESULT S1243: `supply_tick`'s new-step guard set to `if False:`. Survives `features.py` (4622 passed) and `harness_headers.py` (112 passed). This is the block.
- The new checks' null controls, `_sa_open["06:15"] == ["turn_on"]` and `_sa_open["06:00"] == ["turn_off"]`, pass in the unmutated run. So the empty or no-`turn_on` write lists are the gate's doing, not a tick that never fired.
- RESULT harness: `dev/audit/harnesses/r10_sav_actuation_phase.py` (sha1 `d8871c1b96466f7d0d16df9ecc15454512d6adc5`, the fixer's own build, disclosed as such) prints `AGREE: yes` at this head (`ev/harness_head.txt`). I did not re-run the base end this round, because production code is unchanged since round 3, whose reviewer took `AGREE: no` at the base.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` exits 0 with tree `bdc9dd55fe06`. There is no conflict and no MERGE-CLAIM line.
- RESULT version and claims: `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and both claim files are untouched three-dot.
- RESULT structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. The budgets only go down: `class_excess_loc` 17672->17659 and `max_class_loc` 8065->8063, earned as round 3 verified. `tests/closures.json` adds the harness to `INERT`.
- RESULT archscore: `score.py --diff e77418f9b HEAD` prints `Architecture score: dS +0.0000 NULL`.
- RESULT CI at this head, read from the check-runs API at 14:49 and 15:04 UTC: every gate check concluded success or skipped, and none is red. That covers fast (3.14), closures, coverage, coverage-ratchet, arch-instrument, instrument-self-tests, env-matrix, policy-docs, typing, replay, browser, lane-proofs, briefs, closure-scope, arch-score, budget-raise-gate, delivery-status, nightly-status, hassfest, validate-hacs, codeql (all three) and mutation. The mutation lane's success carries the PIN NOT REPRODUCED line above. A second workflow run's `prelude` (run 41068863394) was still `in_progress`. No red check is owed an answer at this head.
- Not re-derived: the body's figures for earlier heads (the 484 s timing, the `ci_predict` counts, the X1–X6 and Y1–Y2 counts at 4578 and 4598). Round 3's reviewer re-took Y1, Y2, M3 and M4 on the same production code.
