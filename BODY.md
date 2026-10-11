perf(optimizer): two bit-identical cuts to the solve's cost -- the #1935 replay is ~8-10% faster

`tests/boost_drift_replay.py` is 86 % of the `fast` e2e critical lane and
81 % of `coverage`'s, and runs in `closures` too (~2 h of lane time per
push arm; pre-study `handoff/r9-covfast-scoping-prestudy` §1). Profiling
it at the merge base (figures below) put ~89 % of its wall inside the
solver: 68 % in `simulate_trajectory_batch` and 19 % in the batched cost
terms, per fused FD evaluation. Two cuts follow, both **bit-identical by
construction** -- no float, plan, branch or executed behaviour moves:

1. **`_energy_cost_fn`'s batch arms stop walking their rows in Python.**
   `grid_only_cost`/`energy_cost` still held the per-row `np.sum` loop the
   comfort terms left behind in D9-s1-01 and cycling in RC-sw1. Each row's
   sum is now `row_sums` (`batchmath.py`), which reproduces numpy's own
   scalar summation order as explicit column arithmetic -- the in-tree
   bitwise contract -- so a row stays bit-for-bit the scalar price of that
   row on every backend. Measured 97.1 -> 11.9 us per `[50,48]` batch call,
   output asserted bitwise-equal; the loop was ~40 % of the cost half of a
   batched evaluation. The replay's prices have no PV surplus, so the
   `grid_only_cost` arm is the one it pays; the PV arm converts alike and
   is pinned by `features.py`'s #948/#21 closures.

2. **One evaluation memo per `_multi_start_minimize` call.** Candidates
   that share a basin walk L-BFGS-B to points an earlier start or polish
   already evaluated bit-for-bit -- measured 127 of 3350 fused evaluations
   over 8 replay cycles (3.8 %) are exact repeats, sitting *across*
   `_scoped_minimize` invocations where scipy's own per-run cache cannot
   see them. The memo wraps the batched objective, keyed on the
   evaluation's own FD row matrix (deterministic in `x` and the bounds),
   and is shared by every start and polish of the one call; a hit returns
   the array the earlier evaluation computed, to the bit. It dies with the
   call -- no answer crosses a solve, and the two-zone continuation's
   half-priced evaluations run before the wrapper exists, so they can
   never be served to the full-priced loop.

A third change lands with them, in instrumentation only: the round-4
D9 harness `h9_batch_cost_loop.py` pins "exactly one batched call and
~97 rows per gradient evaluation", and the memo serves a repeated point
without re-entering the twins -- the pin reddened at 0.954/92.58.
Re-recording those floats would pin a backend-dependent hit rate and
blind the pin to the scalar fallback it exists to catch, so the harness
instead counts a memo hit as the batched evaluation it stands for (one
call, its rows): the exact pins 1 / 97 / 0 hold again, and a fallback
evaluation still reaches neither counter and reddens as before.

**Payments considered and not taken** (fixer step 17 / the ask):

- A `DefrostDerate.factor` memo (~5 % of a solve measured locally, the
  `factor`/`_decide`/`derate_from_duty` chain): REJECTED as unsound --
  `tests/features.py` mutates the derate grids directly (`_dr.factors[2][1]
  = 0.6` at ~10 sites), so no invalidation the class owns can promise
  freshness; a public dataclass with publicly mutable lists cannot carry a
  memo (#714 class: the entry would blind the pin at the site it watches).
- Hoisting the dead `refused_acc = np.zeros_like(...)` allocation out of
  `simulate_trajectory_batch`'s single-zone step (~1-2 % under cProfile):
  below this box's measurement noise, for a branch added to the most
  parity-pinned function in the tree. Not taken.
- A `threadpoolctl` controller reuse in `_scoped_minimize` (~0.5 % locally,
  the dyld re-scan): unmeasurable here. Not taken.
- Shortening or skipping the two-zone prefix (254 solves, ~24 % of the
  wall, output-checked by nothing in the default invocation): REFUSED --
  it changes what runs, the sibling fixer's short-replay refusal
  (`handoff/r9-heavy-consolidation-prestudy`) is the precedent and the
  boundary this fix was commissioned under.
- Warm starts, tolerance or start-set changes: REFUSED -- every one moves
  floats, and rule 3 makes the fixtures the owner's.

## Head

`23b612e80632222fcd19a2b2ab434a412fd56748` (branch `fix/boost-replay-speed`,
merge base `origin/main` = `102312dece91f04e0591007501b56cb8b3a9e686`;
two commits: the optimizer pair `9a34ca1c0`, the h9 harness
instrumentation `23b612e80`). Every figure below was measured at
`23b612e80` unless a line names another SHA.

## Mutation proof

The failing arm is the wall itself, and each mechanism's mutant restores it:

- **Memo deleted** (mutant: `_memoized_batch_objective = lambda bo, memo: bo`,
  i.e. every scipy call reaches the raw objective): the deterministic
  evaluator-count proof -- over 8 replay cycles the raw batched objective
  runs **3350** times with the memo deleted and **3223** times at the head,
  exactly the 127 duplicate evaluations; each costs ~0.9 ms (the batched
  simulation), so the mutant hands back ~114 ms per 8 cycles of pure
  re-computation. The full-run pair below is the wall-level proof.
- **`row_sums` reverted** = the merge base itself: the isolated bench runs
  the loop at 97.10 us and the `row_sums` form at 11.93 us per call with
  the outputs asserted bitwise-equal (`np.array_equal` on the `uint64`
  view), and the whole-script wall is the base/head pair below.
- **Byte-identity** (the fix's own predicate): `cmp` of the replay's full
  stdout at the merge base and at the head -- identical, 46/46 checks,
  every 4-decimal `hh_scale` figure included.
- **Harness instrumentation** (the third change): with the memo landed and
  the h9 counting absent, `tests/harness_headers.py` fails exactly
  `cost_terms_batch_calls_per_gradient` (0.954407 vs 1),
  `batch_rows_per_gradient` (92.5775 vs 97) and
  `null_control_batched_calls_per_gradient_delta` (-0.00399407 vs 0);
  with the counting, `ALL 109 HARNESS HEADER CHECKS PASSED` and the
  harness itself prints `1 calls/grad`, `97 rows/grad`, `0 calls/grad`.

## Null control

`tests/entities.py` (an unrelated scoped script; imports no solver): user
CPU 71.29 s at the base vs 72.19 s at the head -- unchanged, the whole
effect sits in the solver paths the diff touches.

## Figures

Each with the command that printed it; all on this macOS seat under the
seat venv (`~/.local/state/hpo/venv-ci/bin/python3`), scratch
`/Users/timmalmstrom/hpo-seats/r9fix-vib/prof/`:

- Base replay wall (merge base `102312dece`, in-process driver over
  `main()`, stdout captured):
  `cd /Users/timmalmstrom/hpo-seats/r9fix-vib/base && time env WT=/Users/timmalmstrom/hpo-seats/r9fix-vib/base PYTHONPATH=/Users/timmalmstrom/hpo-seats/r9fix-vib/base/tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 prof/run_phased.py`
  -> `758.55s user 6.82s system 92% cpu 13:48.83 total`, rc 0, `ALL 46
  BOOST DRIFT CHECKS PASSED`, in-process total 828.2 s.
- Head replay wall (head `9a34ca1c0`, same driver, same box):
  `cd /Users/timmalmstrom/hpo-seats/r9fix-vib/wt && time env WT=/Users/timmalmstrom/hpo-seats/r9fix-vib/wt PYTHONPATH=/Users/timmalmstrom/hpo-seats/r9fix-vib/wt/tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 prof/run_phased.py`
  -> `649.60s user 6.30s system 93% cpu 11:41.87 total`, rc 0, in-process
  total 700.8 s. **Speedup 758.55 -> 649.60 s user = 14.4 % less CPU**
  (wall 13:48.8 -> 11:41.9 = 15.4 %). Scaled to the CI walls in the
  pre-study by the same ratio: `fast`'s 2323 s -> ~1990 s, `coverage`'s
  2925 s -> ~2500 s, the `closures` recording likewise; the ratio is the
  rule, the CI walls are what lands.
- Output byte-identity:
  `cmp prof/base_stdout.txt prof/head_stdout.txt` -> identical (68 lines,
  46 checks, every float figure).
- Profile (where the time went), 10 surface-free cycles under cProfile:
  `~/.local/state/hpo/venv-ci/bin/python3 prof/prof_cycles.py 10 none` ->
  `optimize` 99.8 % of `cycle`; wrapper timing
  `~/.local/state/hpo/venv-ci/bin/python3 prof/probe2.py` ->
  `simulate_trajectory_batch` 68.4 % (4491 calls), `_cost_terms_batch`
  18.7 %, `_scoped_minimize` 94.1 %.
- The energy-closure bench (mechanism 1):
  `WT=/Users/timmalmstrom/hpo-seats/r9fix-vib/wt ~/.local/state/hpo/venv-ci/bin/python3 prof/bench_grid.py` ->
  `bitwise identical: True`, loop `97.10 us/call`, `row_sums` `11.93
  us/call` (2000 calls, best of 5).
- The duplicate-evaluation census (mechanism 2's premise):
  `WT=/Users/timmalmstrom/hpo-seats/r9fix-vib/base ~/.local/state/hpo/venv-ci/bin/python3 prof/probe_dupbatch.py`
  -> `grad evals=3350 unique_x0=3223 dup_x0=127` over 8 cycles.
- The memo's mutation proof (counts, not walls):
  `WT=/Users/timmalmstrom/hpo-seats/r9fix-vib/wt .../python3 prof/proof_memo2.py` -> `raw batch evaluations=3223`;
  `WT=/Users/timmalmstrom/hpo-seats/r9fix-vib/wt .../python3 prof/proof_memo2.py mutant` -> `raw batch
  evaluations=3350`.
- Null control:
  `cd /Users/timmalmstrom/hpo-seats/r9fix-vib/base && time env PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 tests/entities.py`
  (and the same at `/Users/timmalmstrom/hpo-seats/r9fix-vib/wt`)
  -> 71.29 s vs 72.19 s user.
- Structure ratchet at the head: `python3 tests/structure.py` ->
  `STRUCTURE RATCHET PASSED` (`_multi_start_minimize` held at 149 lines;
  no budget re-recorded, none raised).
- Bit-identity spot proofs across both cycle families (before the full
  runs): `diff prof/snap_base2.txt prof/snap_head2.txt` (21 single-zone
  cycles) and `diff prof/snap_base2_tz.txt prof/snap_head2_tz.txt` (12
  two-zone cycles) -> identical (house state, plan, objective value,
  learner scale, fold counts).

## Unpinned sites

The eight sites `ci_predict` lists for this diff, each with its
disposition (`pinned by mutation-autofix` unless a standing check already
kills the mutant):

- `custom_components/heatpump_optimizer/optimizer.py:539 GUARD_OFF` --
  pinned by mutation-autofix; the mutant breaks every unbatched solve,
  which the whole suite kills.
- `custom_components/heatpump_optimizer/optimizer.py:545 GUARD_OFF` --
  pinned by mutation-autofix; the mutant is the memo's null (every
  evaluation recomputed), the count-level proof of which is in
  `## Mutation proof`.
- `custom_components/heatpump_optimizer/optimizer.py:549 RETURN_DEL` --
  pinned by mutation-autofix; the mutant returns `None` for every fresh
  evaluation, killing any batched solve.
- `custom_components/heatpump_optimizer/optimizer.py:551 RETURN_DEL` --
  pinned by mutation-autofix; same class, one line up.
- `custom_components/heatpump_optimizer/optimizer.py:783 BOOLOP` --
  pinned by mutation-autofix; the mutant routes batched solves onto the
  scalar jac or crashes them.
- `custom_components/heatpump_optimizer/optimizer.py:783 GUARD_OFF` --
  pinned by mutation-autofix; same site, same kill.
- `custom_components/heatpump_optimizer/optimizer.py:2737 RETURN_DEL` --
  a value check: the mutant returns `None` from the grid arm, and
  `tests/features.py`'s `_energy_cost_fn` pins (`3978`-`3989`) price a
  batch through it on every run.
- `custom_components/heatpump_optimizer/optimizer.py:2752 CLAMP_DROP` --
  a value check: `tests/features.py`'s PV piecewise pins (`55571`+)
  assert the PV arm's exact covered-vs-imported prices, which the
  dropped term moves.

## Red checks

One local red, pre-existing at the merge base and not this diff's:
`tests/features.py` check "R9-F2.1 P3: the shipped storage plan is no
worse on its own objective than the half-price floor's plan refined
under it" fails at the head with `[shipped 110.4366, seeded with the
half-price plan 110.1297]` -- and fails at `origin/main`
(`102312dece`) on this seat with **byte-identical figures** (base
control run in full). This seat's numpy is the Accelerate build; the
float-sensitive storage-plan comparison is of the class the tree
already knows does not reproduce off CI's Linux wheels (the
`fast (3.14)` job is the authority for it, and it is green on main).
Everything else in the scoped gate at the head is green locally:
`optimality`, `backtest`, `validate`, `edge`, `finite_boundary`,
`entities`, `env_drift` (no unclaimed drift against `origin/main`, 5
scenarios), `harness_headers` (109/109), `config_flow_steps`,
`debug_collect`, `deployment_shape`, `doc_claims`, `guard_pins`,
`manual_plan`, `plan_view`, `card.mjs`, `card_drift.mjs`,
`solar_alignment`, `typing_ruler`, `wood_advisor`, `block_duty`,
`arch_score_head`, `structure`. `stress.py` is left to CI's required
mutation check (the contract's rule), as are `golden.py`'s strict-mode
fixtures (drift mode -- which is what CI runs -- substituted
`env_drift.py` above). `UNDER-SCOPED` / `INHERITED CLAIMS`: n/a -- the diff
touches `optimizer.py` only, no claim file is touched, and the branch
claims nothing (both claim files are byte-identical to `main`'s). CI's
`coverage`/`coverage-ratchet` and the mutation check are the remaining
arms this box cannot produce; the executed-line set changes only in the
edited lines themselves (an executed loop replaced by executed
expressions in the same module), every value-level branch proven
unchanged by the byte-identical stdout and the drift suite.

## Forward-carry

none

## Friction

none
