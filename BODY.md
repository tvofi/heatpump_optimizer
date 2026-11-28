R11-HOTFIX-MUTATION-DRIVER-CAP (owner ruling 11-28, an exception to the tooling freeze). At #3897's head the `tests / mutation` drive drew 10 sites. 9 of them were pinned to `tests/features.py`, which costs 1617 s per recorded run. With that driver's lazy baseline and null control, that is 11 features.py runs on 3 workers, and the job hit its 160-minute timeout. Pinning cannot fix this, because `sampled_pool` draws pinned sites too.

The fix: under `--scope changed`, `sampled_pool` now draws at most `COSTLY_PIN_DRAWS` (2) sites whose `killed_by` killer is one of the site's drivers and records over `COSTLY_PIN_SECONDS` (900 s) by `recorded_seconds`. `costly_pin` makes that test. The draw keeps the order of the same shuffled draw: each site that is passed over is replaced by the next site of the draw, and the lane prints a `passed over` line for it.

Only a pinned site is ever passed over:
- A pinned site's kill is a measured ledger row. The nightly's `--scope full --max 40` draw, which is not capped, re-drives it (`pin_reverification`).
- An unpinned site's killer is exactly what the lane exists to find, so it is never passed over.

`--scope full` keeps the uncapped draw. The ratchet path (`unpinned_sites`, `ratchet_refusal`, `added_unpinned`) is not in the diff, so an added unpinned site still refuses.

Alternatives, and why each lost:
- **Running the pinned site's `features_block.py` section instead of the whole features.py.** A `killed_by` row names a script, not a block. That approach needs a ledger format change and a per-block baseline and null control, so it is a larger design than a hotfix.
- **Cost-weighted sampling.** It biases every draw, including one with no costly pin, so it breaks the null control below.
- **`--budget-minutes` on the PR lane.** That is a `.github/` change, and it reports SKIP-BUDGET sites instead of drawing other ones.

## Head

462e051a847207921122f9fdf4438d5874749b4f, on base ac9045c223721608e684c8a2213831aa34c1fa4f (origin/main at 2026-11-28T15:14Z).

## Mutation proof

The check is `tests/entities.py`'s "the PR lane's draw holds at most COSTLY_PIN_DRAWS sites pinned to a driver over COSTLY_PIN_SECONDS ...".

Each mutant below was applied to `tests/mutation_table.py` and driven through that check's block, which is the exact text between its comment and `_mut_ordpool`, run with `mutation_table` imported. Each one read FAIL; the restored tree reads OK:
- `if pin is not None and dear == COSTLY_PIN_DRAWS:` changed to `if False:`
- `> COSTLY_PIN_SECONDS` changed to `>=`
- `dear += pin is not None` deleted
- `if len(drawn) == cap: break` deleted
- the `pin in mut["drivers"]` conjunct dropped
- `if killed_by is None: return pool[:cap], held` deleted (raises AttributeError)

The base program (ac9045c2's `mutation_table.py`) under the new check reads FAIL, `K=None`. That is the failing test first, at commit afd9dcad71.

main()'s wiring, which passes `killed_by` and `seconds` under `--scope changed` only, is killed by the harness below rather than by a check. With that keyword argument removed from the `sampled_pool` call in the after checkout, the after arm read `DRIVER tests/features.py runs=11`, 10 sites drawn, `ESTIMATE 9754 s` (163 min): the before arm's draw.

## Null control

- With a pin at the threshold (900 s, not over it), with no pins, and with a pin to a script that is not one of the site's drivers, the capped draw equals the uncapped `sampled_pool` draw site for site. These are the same check's arms 2, 3 and 5, and arm 4 is the call with no `killed_by`.
- The before arm of the harness reproduces the incident itself: 11 features.py runs, and an estimate over 160 minutes, matching the cancelled job run 46128197569.

## Figures

- `dev/audit/harnesses/mutation_draw_cost.py` (sha1 c49593fa33174ba8c52c7f2799a74138ef5b2541). It runs a checkout's own `mutation_table.main` as tests.yml calls it (`--scope changed --base origin/main --max 10 --jobs 3`). Only `run_script` is stubbed: each run sleeps the driver's `recorded_seconds` / 100 and is red iff the tree carries a drawn mutant whose pin is that driver. The estimate is the first-to-last driver-run span × 100.
- Before, at ebd70acc5e2ba8716813aa07ed1fa9332ab8d045 (#3897's head) with its own program, `cd <ebd70acc checkout> && python3 dev/audit/harnesses/mutation_draw_cost.py --cost tests/env_drift.py=397`: 10 sites drawn, 9 pinned to features.py; `DRIVER tests/features.py runs=11`; `ESTIMATE 9745 s` (162 min).
- After, the same command on a checkout of ebd70acc carrying this head's `tests/mutation_table.py`: 4 sites drawn, 2 of them pinned to features.py; 10 sites passed over, every one pinned to features.py; `DRIVER tests/features.py runs=4`; `ESTIMATE 5376 s` (90 min).
- The after arm and the mutation proof ran on commit 4c16879e8d's `tests/mutation_table.py`. It differs from the head's only in comment and docstring text, from commit 462e051a's comment ratchet repair (`git diff 4c16879e8d HEAD -- tests/mutation_table.py`).
- The `--cost tests/env_drift.py=397` override is the CI log's measured env_drift baseline (job 140928518998). The recording for that ref-driven driver times a stub.
- Both estimates leave out the job's setup and inventory minutes.
- `python3 tools/audit/archscore/score.py --diff ac9045c223721608e684c8a2213831aa34c1fa4f HEAD`: `Architecture score: dS +0.0000 NULL`.
- Scope, by `tests/closure.py select --diff <merge-base>`: `MODE: SCOPED -- 3 script(s) run, 31 scoped out` (doc_claims.py, entities.py, harness_headers.py). All three ran green locally with `PYTHONPATH=tests/hastub`, and so did `python3 tests/structure.py`.
- `tools/pr/ci_predict.py --apply-inert` wrote the harness's INERT READS entry for `tests/harness_headers.py`. A second run predicted no red.

## Red checks

none

## Forward-carry

- The cap prices a pinned site by its pin alone. A PR whose drawn sites are unpinned and killable only by features.py still pays one sweep per site; that is the evidence the lane exists to gather, and pin-killed pins it on the next push. Carry: dismissed: an unpinned site's killer is unmeasured, so capping it would drop the sites the sample exists to check.

## Friction

none
