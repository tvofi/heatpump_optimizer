Fix review: merge 294bf66ffb463faf842f6a0f43c119b27005b558

Round: 2 of R10-SETPOINT-BOOST at this head. Round 1 was blocked `head-moved` at
44ea3af3 and confirmed as bus commit 04d553dc; the move landed on this head, and
this round measures it. Not the fourth round.

Head measured: 294bf66ffb463faf842f6a0f43c119b27005b558. Re-read immediately
before posting: unchanged.

## The eight `killed_by` re-derivations (round 1's gap, now closed)

Round 1's in-tree `--anchor` drive refused with `1 mutant(s) timed out` under a
machine load of 40-80. This round I re-derived each of the nine sites at this
head with the tree as cwd, using the operator the body names: the ledger's `old`
line replaced by the mutant text its table states (CONST values 96 / 1.0 / 0.5,
each comparison bound inverted as listed, the guard taken to `False`, the CLAMP
min dropped). My runner is `rev-2465-r2/run_block_mutant.py`, named as mine: it
executes **the PR's own R10-SETPOINT-BOOST block of `tests/features.py`
unmodified**, in the features.py header namespace, with the four helper names the
block takes from the SETPOINT-POWER block (`_dr`, `_DrCoord`, `_dr_entry`,
`_dr_params`) supplied verbatim; the tree is restored after each run and
`git status` is clean. It is the block, not the whole 4258-check driver, and I
say so: the block reddens the named check, which is the property the `killed_by`
row asserts. The whole-driver runs of the same nine mutants and the baseline are
reported below.

RESULT block at BASE, no mutation: `ALL 26 FEATURES BLOCK PASSED`, rc 0 (ev/block_BASE.txt)
RESULT S1 `draw_range.py:<module> CONST 3b4c559c` `IDLE_WINDOW = 96`: rc 1, 1 of 26 failed -- `FAIL the idle window is one day of readings: 60 at 0.20 then 36 at 0.30 learn the newest 48 (0.30), not the whole 96 (0.20)` (ev/block_S1.txt)
RESULT S2 `draw_range.py:<module> CONST 9b5abfbf` `CEILING_TOLERANCE_K = 1.0`: rc 1 -- `FAIL a set-point 0.9 K under the ceiling is not full-power evidence ...` (ev/block_S2.txt)
RESULT S3 `draw_range.py:<module> CONST 56bfbaa7` `GATE_TOLERANCE_K = 0.5`: rc 1 -- `FAIL a set-point 0.4 K above the gate is not a gate-held interval ...` (ev/block_S3.txt)
RESULT S4 `DrawRange._evidence CMP_BOUND 3a7f8343` `>=` -> `>`: rc 1, 2 of 26 failed -- the sub-ceiling check and `FAIL a set-point exactly CEILING_TOLERANCE_K under the ceiling counts as full (the test is inclusive)` (ev/block_S4.txt)
RESULT S5 `DrawRange._evidence CMP_BOUND 3e86f7a9` `>` -> `>=`: rc 1 -- `FAIL a draw exactly IDLE_MARGIN times the learned idle is the idle draw, not a run (the test is strict)` (ev/block_S5.txt)
RESULT S6 `_stored_idle CMP_BOUND d95cb3ca` `>=` -> `>`: rc 1 -- `FAIL a stored idle reading of 0.0 is a reading: six of twelve, the median is 0.15` (ev/block_S6.txt)
RESULT S7 `inputs.py:_on_step CMP_BOUND 94ce3139` `<` -> `<=`: rc 1 -- `FAIL a set-point exactly one millionth of a step above a multiple is not snapped to it (the snap is strict)` (ev/block_S7.txt)
RESULT S8 `pump_arbiter.py:_flow_command GUARD_OFF ec595179`: rc 1 -- `FAIL the guard: a written set-point that is not a number, or an entity range that does not read, commands nothing` (ev/block_S8.txt)
RESULT S9 `pump_arbiter.py:_flow_target CLAMP_DROP 38a077e7` `lo=floor_c`: `ALL 26 FEATURES BLOCK PASSED`, rc 0 -- the site survives, as its `survivor_triage equivalent` says (ev/block_S9.txt)

The eighth row is a real kill, not a triage: each of S1-S8 reddens the check its
ledger row names, and the baseline is green. The ninth I re-derived as equivalent
analytically as well: `quantise_setpoint_c` applies `max(out, ceil_step(lo))`
then `min(..., floor_step(hi))` with `hi=heat_c`, so for `floor_c > heat_c` the
mutant's higher `lo` is cut back to `floor_step(heat_c)`, the value the original's
`ceil_step(heat_c)` also reaches (`ceil_step(heat_c) >= floor_step(heat_c)`), and
the Fahrenheit path is a monotone affine map of the same comparison. A triage on
a killable mutant would have reddened the block; it does not.

RESULT CI's own mutation lane at this head (`MUTATION TABLE PASSED`, 12:54:13Z) re-drove the same nine sites itself: `PIN RE-VERIFICATION: 9 reproduced, 0 not reproduced, 0 not re-verified`, `1 survivor(s) of 10 evaluated = 0.0% (1 triaged equivalent, raw 10.0%), cap 20.0%` (ev/mutation_log.txt). This is the in-tree re-verification round 1 could not run, and it agrees with the block above.
RESULT CI's `mutation` green is not the `MUTATION TABLE INCONCLUSIVE` kind: its log counts `1 survivor(s) of 10 evaluated`, and the per-driver lines read `LAZY AND NEVER RUN -- every mutant run of it was green, so no verdict read its baseline` (`tests/stress.py`: `DEFERRED AND NEVER RUN`), which is the evaluated pass, not the inconclusive arm (ev/mutation_log.txt).

The whole-driver runs of S1-S9 and the unmutated baseline (`tests/features.py`,
the recorded driver) were started at this head; at the shared machine's load
(80-120 from other seats) they would have needed about another hour, so I
stopped them at posting and do not report their outcome. CI's own unmutated
driver run at this head is green (`ALL 4258 FEATURE CHECKS PASSED`, above), so
the driver baseline is confirmed from CI, and the block below is the driver's own
text for the named checks. Round 1's nine in-tree `--anchor` attempts each ran
the tool's comment-only null control and it survived every driver
(rev-2465/ev/anchor_*.txt), so the null control holds too.

## The carried numbers, re-taken at this head (not assumed)

RESULT `mutation_table.py --pin-killed --base origin/main`: `4147 unpinned site(s) of 6264 candidate sites, 4147 at the ratchet base d99b400a5986a206e3a2bc0c2943967ce27b8adc; the ledger agrees with the deterministic inventory` and `PIN KILLED -- 0 new unpinned site(s)`, `PIN KILLED: nothing to pin`, rc 0 (ev/pin_killed.txt). The absolute number depends on the base read: CI's lane reads the same sentence as `4126 ... 4126 at the ratchet base a2b25bbc5` (main's tip, which carries more pinned rows than the merge base). Every read shows unpinned equal to its base, which is the claim: this diff adds none.
RESULT `carry_audit.py check --body`: `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (ev/carry_audit_body.txt)
RESULT `env_drift.py --claims-only <merge-base d99b400a5>`: `claims hygiene: d99b400a5986a206e3a2bc0c2943967ce27b8adc ok`, rc 0 (ev/env_drift_claims_only.txt)
RESULT `env_drift.py --all` at this head, completed: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`; `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`; rc 0 (ev/env_drift_all.txt). The same run at 44ea3af3 read the same two lines, rc 0.
RESULT `git merge-tree --write-tree origin/main(a2b25bbc5) 294bf66f`: exit 0, tree `012b1f16ad2e80bc36a8b16663e1b8cdb9522699`, the same tree measured at 44ea3af3 before the move; `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.txt)
RESULT harness at this head (`--no-solves`): `floor: cells 155 heating floor at or below the gate 0`; `window plan ... engaged False observed (0.8999999999999999, None) idle 0.3 planned None`; `window probe ... engaged True observed (2.9399999999999995, 3.0)`; `failures 0` (ev/harness_head_nosolves.txt)
RESULT harness at the merge base d99b400a5 (run from that tree's cwd): `floor ... 63`; `window plan ... engaged True observed (0.8999999999999999, 2.034) idle None planned (0.8999999999999999, 2.034)`; `failures 0` (ev/harness_base_nosolves.txt)
RESULT harness with solves, both trees: 32 plan sha1 lines identical; `spread: lower 8 higher 0 identical plan 8`; `flat: lower 0 higher 0 identical plan 16`; `failures 0` at both (ev/harness_head_solves.txt, ev/harness_base_solves.txt)

## CI at this head

RESULT CI at this head, `fast (3.14)` success (11:31:35Z start, 12:00:45Z end): its own log reads `ALL 4258 FEATURE CHECKS PASSED` (`python3 tests/features.py`, 635 s), `STRUCTURE RATCHET PASSED`, `ALL 2359 ENTITY CHECKS PASSED`, `ALL 84 OPTIMALITY CHECKS PASSED` (ev/fast_log.txt). These re-derive the body's local figures at this head, from CI.
RESULT check-runs API at 294bf66f, every context concluded: 32 success, 16 skipped, 1 failure (`nightly-status`, below). `fast (3.14)`, `pr-contract`, `arch-score`, `coverage`, `typing`, `env-matrix`, `instrument-self-tests` success; `closures` success at 12:22:06Z; `mutation` success at 12:54:13Z.
RESULT CI's body check at this head (job log): `record red-history 18 commit(s) between origin/main and this head, every failure conclusion across them: arch-score, mutation`; `PR-BODY: 0 error(s)`; `FIGURES: 11 resolved, 0 not verified, 0 refused`; `no version edit`; `CARRY-AUDIT: 6 ... 6 routed` (ev/pr_contract_log_head.txt). Both range reds are answered under `## Red checks`.
- `mutation` is green at this head (12:54:13Z) and re-verified the nine dispositions itself; its earlier range red is answered under `## Red checks`.
- `nightly-status` is red at this head and is not this PR's: its own log reads `NIGHTLY FAILED: slow failed last night.` and states `This check is NOT one of the required contexts on main-protect`. The diff does not move `tests/nightly_status.py` or what it reads, so `defect-root-cause.md`'s exemption covers it and I do not block on it (ev/nightly_status_log.txt).

## Architecture

Unchanged from round 1 and still sound on added lines: one owner per concept (the
gate in `_gate_c`, the floor rule in `thermal_model` with the gate passed in, the
rounding at the one write in `inputs`), no HA import added to a model module, the
decision in `_flow_command` handed neither the coordinator nor anything reaching
into it, the store reused rather than duplicated, units in names, missing input
returns `None`. `arch-score` succeeds at this head; the group's `architect_note`
is null.

## Notes, non-blocking (carried from round 1, still standing)

- The body's mutation answer still calls `mutation_table.py --scope changed --base
  origin/main` a source-only detector and says `prepr.sh` step 6d runs it. The
  refusal arm is source-only, but the pass arm proceeds into the sampled table,
  and step 6d runs `tools/pr/ci_predict.py`. The trigger is answered either way.
- A hand-set fractional disinfection floor on a whole-degree entity (e.g. 48.05 °C
  on a °F install) is written 0.27 K low and `setpoint_check` re-raises the issue;
  the UI's step-1 selector cannot produce it, so it is not blocking. Rounding a
  floor up would remove the class.

## What I could not verify

- The whole-driver outcomes of S1-S9 and the baseline (`tests/features.py`) were
  stopped at posting after the shared machine made each run an hour long; the
  named checks are re-derived above with the PR's own block, and CI's unmutated
  driver run at this head is green.
- The owner's export aggregates (54 samples, 41 at p_min, 0.33-0.73 kW, 25.0
  written) remain private and not re-derivable; I do not report them as confirmed.
- `mutation`'s conclusion at this head (in progress at posting).

bus-nonce: 5010c2d8fbe8a265203ae66161deec71
