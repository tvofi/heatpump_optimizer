_Requested by **tvofi**_

R9-EG-B1 (#1736, per-solve immutable inputs), round 2. Round 1 was blocked
(comment 5977790144): the branch conflicted with main (#1874's gapped-census
changes in `tests/arch_score_head.py` and `tests/features.py`, so no CI had
ever run at its head), the hub barrier passed a record that shared the live
hubs' containers, and the card what-if's freshness had no pin. This round
merges main, adds the two owed checks, cuts the barrier text to what the
checks refuse, and carries the instrument finding.

What changed (round 2 over round 1's `6b68bca08`):

- **The merge.** `origin/main` merged twice (never rebased): `4efc5b63e`
  (resolving #1874's two content conflicts by keeping both sides: the #1736
  hub-writers checks and the EG-A2 gapped-census checks in
  `tests/arch_score_head.py`; the #1736 block and the EG-A2 helper checks in
  `tests/features.py`) and `1913f0dd7` (the v6.7.16 stamp; clean).
  `tests/structure_budgets.json` resolved through the ledger driver
  (`functions_cc_over_15: 34 + both deltas = 31`); `tests/structure.py`
  re-run at each merged tip: PASSED (after recording `max_method_loc`
  374→373, which main's EG-A2 consolidation moved down; reason in the
  commit).
- **The record shares nothing.** `tests/features.py` walks object identity
  over the record (`record.config`, `record.params`, `record.inputs.state`)
  and the what-if's base (the other `_solve_hubs` arm, `banded=False`)
  against the three live hubs, and refuses any shared MUTABLE object --
  nested containers and shared instances included. Immutable atoms are
  skipped on purpose: `copy.deepcopy` shares an int, a string, a datetime or
  an enum member by identity, and sharing those is harmless. The walk's own
  control plants one shared list and must name exactly it. Killed by MX (the
  three `copy.deepcopy(...)` wrappers removed from `_solve_hubs`): red,
  naming the shared objects; green at the head.
- **The card's what-if is fresh.** `tests/features.py` pins that the card
  prices with this moment's configured peak price and the learner's pooled
  draw pattern, not the last solve's: both move between the solve and the
  card call, and the card must see the moved values. Killed by MC2 (the
  what-if reading the live hubs directly): red on both inputs.
- **The barrier text.** `tools/audit/bugclasses.json`'s N-shared-config
  barrier said `tests/entities.py` "refuses a live hub handed to a thread or
  the process worker"; its key is an argument spelled as a hub attribute, so
  an alias, a lambda capture or `SolveInputs(state=ctx._current_state)`
  passes it. The text now states what each of the three checks refuses,
  including entities' literal spelling and the gap the identity walk covers.
- **The instrument finding carried.** `.claude/workflows/carry-1774.json`
  (see Forward-carry).

Everything else is round 1's, unchanged: one record per solve, the setback
as a value, `optimize(*, inputs: SolveInputs)`, the model corrections
refreshed once per cycle, H1–H4, the `arch_score_head.py` write barrier and
the `entities.py` hand-off barrier, the seam-map and ledger updates, and the
harnesses that follow the signature. See the round-1 body in the PR history
for the full design record (options considered, behaviour changes 1–3, the
H1–H4 decisions and the design choices the checks encode); none of it
changed.

### Behaviour, beyond the refactor

Unchanged from round 1, with one addition:

1–3. As round 1 (H1–H4; corrections refreshed once per cycle after the
learners; the card's what-if takes this moment's tariff threshold, baseline
load, DHW plan inputs and burn/peak flags). Item 3's freshness claim now has
its own pin (the MC2 arm above); round 1's only kill for it came through
sharing, never through tariff freshness.

Design choices the checks encode:

- The identity walk collects MUTABLE objects only, and its walks return ids:
  both roots stay alive while their walks are compared, because the id of a
  garbage-collected object is reused and a temporary walked on both sides
  reads as shared when it is not. Both are stated in the helper's docstring;
  the control pair is held in named module-level objects.
- The freshness arm sets the learner's `hourly_profile` directly, in range:
  `normalize_profile` projects onto `[0.2, 3.5]` mean 1.0, so two spikes
  past the ceiling project to the same profile and move nothing, and with
  day-type evidence `pattern_for` blends the day-type profiles instead.
- The freshness arm compares the peak-price RATIO (90/50 = 1.8), never the
  field: `marginal_price_per_kw` divides by the peaks averaged.

### Options considered

Round 1's options stand. Round 2 additions:

- **Taken: an identity walk in `tests/features.py`.** Runtime identity over
  the real record built by the real coordinator, importing the production
  builders; an AST rule cannot see sharing (the containers are built at
  runtime), which is why `entities.py`'s spelling rule is the backstop, not
  the barrier.
- Freeze the hubs (frozen dataclasses). Rejected: sharing a nested container
  is still possible under a frozen parent, and the hubs are written by the
  loop's own state updates -- freezing them is a coordinator redesign, not
  this fix's lane.
- Check only `record.inputs.state` (what the worker receives). Rejected: the
  worker also receives `optimizer.model.params` and `optimizer.config`,
  built from the record's other two legs.

### Budgets

None raised. `max_method_loc` 374→373 is a recording of an improvement main
already made, reason in the commit message; no row rose at any commit of
this branch.

## Head

`13b1b8f0b05fae3b5549e20e3e955c1ba9f5755b` on `handoff/r9-eg-solve-inputs`,
being round 1's `6b68bca08` plus round 2's commits and two merges of
`origin/main` (never rebased): `4efc5b63e` and `1913f0dd7` (the v6.7.16
stamp, clean). Merge base `4efc5b63e76104561b7f467920772d475a996766`;
`git merge-base --is-ancestor origin/main HEAD` holds at the measured head.
Commit list over the base:

- `152420f0f` test, failing first (round 1).
- `b186ba2c7` the refactor (round 1).
- `6dec26740` structure re-record (round 1).
- `b2c52810c` merge of main `2df2f49d9` (round 1).
- `20a48323b` value checks for the mutation drive's unpinned edges (round 1).
- `a251632a4` `carry-1776.json` (round 1).
- `6b68bca08` D1.md's executor-boundary rename (round 1; the reviewed round-1 head).
- `d206ee884` merge of main `4efc5b63e`, both conflicts resolved keeping both sides.
- `ef72defe7` structure: record `max_method_loc` 374→373 from the merge.
- `a4d640c35` the two round-2 checks.
- `cf3bada36` the barrier text cut and `carry-1774.json`.
- `13b1b8f0b` merge of main `1913f0dd7`.

`closure.py select --diff $(git merge-base origin/main HEAD)` prints
`MODE: SCOPED -- 25 script(s) run, 5 scoped out.` `stress.py` is left to
CI's required mutation check (`fixer.md` step 5), named unrun here.

## Mutation proof

Round 1's M0–M4 stand (measured at the round-1 pre-squash commit whose
`custom_components/` is identical to the head's). Round 2's two arms, each
applied as a scratch edit to `coordinator.py` in this worktree and restored
after (`git checkout --`); both were first run red with the check in the
working tree at the pre-fix tip `ef72defe7`, then green at the committed
head `a4d640c35`:

- **MX**, the three `copy.deepcopy(...)` wrappers in `_solve_hubs` removed
  (`replace()` then shares every nested container -- #240's race):
  `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/features.py`
  → `2 of 3691 FEATURE CHECKS FAILED`; the failing check is `#1736 the
  record (and the what-if's base) shares no mutable object with the three
  hubs, a nested container included`, naming 36 shared objects with their
  paths on both sides (`_thermal_params.dhw_windows<list> ==
  record.params.dhw_windows<list>`, the whole `defrost_derate` tree, ...).
  The other failure is the known Mac-only one. This is the mutant the
  round-1 review planted and every round-1 check passed.
- **MC2**, the what-if's `base is None` arm reading the live hubs directly
  instead of calling `_solve_hubs(..., banded=False)`: same command →
  `3 of 3691 FAILED`; `#1736 the card's what-if prices with this moment's
  tariff and DHW inputs` fails on both inputs (peak card 0.0 against the
  moved 30.0; the hub's original draw pattern against the moved one), and
  the round-1 `#240` deep-copy check fails with it. Round 1's kill of this
  mutant came through sharing alone; the freshness arm is what this round
  adds.
- M0 at the head: `1 of 3691 FEATURE CHECKS FAILED` -- only the known
  Mac-only `R9-F2.1 P3` (Red checks).
- Sites this diff adds, `python3 tests/mutation_table.py --scope changed
  --base 4efc5b63e`: 21 `ADDED UNPINNED` (round 1 measured 22 at base
  `9fed34071`; one site's line was consolidated away by main's EG-A2), each
  killed-by name recorded in round 1's drive; pinning killed ones is
  `mutation-autofix`'s.

## Null control

- The identity walk's control, run inside the check at both arms: a planted
  shared list is named by exactly one id (the control prints `control shared
  1 (want exactly the planted list)` under MX, where the real arm fails).
- MX at the round-1 head (pre-fix tip) with every round-1 check: the
  round-1 review measured `ALL PASSED` on `tests/entities.py`,
  `tests/features.py` and the #1736 block alone (comment 5977790144,
  "Plant MX ... survives"); the killing arm is new in this round.
- Golden: `GOLDEN_MODE=drift GOLDEN_REF=4efc5b63e python3 tests/golden.py`
  → `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`. Both claim
  files are byte-identical to main's (the v6.7.16 stamp's `claims-for:`);
  this branch claims nothing. This Mac's BLAS cannot reproduce the committed
  values, so CI's `golden.py` in drift mode is what proves byte identity
  there.
- The score's null control is a tree against itself, pinned NULL by
  `tests/arch_score_head.py` (run below).

## Figures

All at head `13b1b8f0b`, merge base `4efc5b63e`, this M1 (macOS, the seat
venv), unless named otherwise. Every command was run from the worktree root
with `PATH="$HOME/hpo-seats/bin:$PATH" PYTHONPATH=tests/hastub` (the node
scripts without it). The MX/MC2 mutation runs name their own tips.

- `python3 tools/audit/archscore/score.py --diff 4efc5b63e` →
  `dS +20.5886 IMPROVES`: `hub_solve_writes 40 -> 2  +20.5340`,
  `coord_footprint 2511 -> 2504  +0.0040`, `params_over_10 28 -> 27
  +0.0506`; gate-only tripwires `reflective_writes 16 -> 15`,
  `computed_attr_access 31 -> 29`. No metric rose.
  **The relocation share:** 7.71 of the +20.59 comes from the five
  correction fields round 1 moved into `_refresh_model_corrections`
  (solar_aperture_scale, internal_gains_profile, dhw_inlet_current,
  flow_curve_bias, flow_curve_indoor_target), which runs in
  `_update_current_state` one call before the solve, outside the metric's
  roots. Rule: `hub_solve_writes`'s weight held, the head reading 7 instead
  of 2 (those five sites restored) scores
  `20.5340 x log2(41/8)/log2(41/3) = +12.82`; the difference, 7.71, is the
  relocation's share of dS. The relocation is disclosed and argued (round-1
  behaviour change 2); the metric's blindness to it is carried to #1774
  (Forward-carry).
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED` at every
  pushed tip; after the first merge the ledger driver had resolved
  `functions_cc_over_15` to 31 and the ratchet reported
  `max_method_loc 373 (budget 374)`, recorded down in `ef72defe7`.
- `python3 tests/entities.py` → `ALL 2139 ENTITY CHECKS PASSED` (2132 at
  round 1; the second merge brought main's seven new checks).
- `python3 tests/arch_score_head.py` → `ALL 9 ARCHITECTURE SCORE HEAD
  CHECKS PASSED` (7 at round 1; the 2 gapped-census checks are main's
  #1874, kept in the conflict resolution). `python3 tests/arch_score.py` →
  `ALL 158 ARCHITECTURE SCORE CHECKS PASSED`.
- `python3 tests/features.py` → `1 of 3691 FEATURE CHECKS FAILED` (the
  known Mac-only `R9-F2.1 P3`; 3691 = 3681 at round 1 + 8 from EG-A2 + 2
  added here). Under MX `2 of 3691`, under MC2 `3 of 3691` (Mutation proof).
- `python3 tests/optimality.py` → `ALL 84 OPTIMALITY CHECKS PASSED`;
  `GOLDEN_MODE=drift GOLDEN_REF=4efc5b63e python3 tests/golden.py` →
  `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 4efc5b63e`,
  `NO STALE FIXTURE: 56 committed fixture(s)`.
- `python3 tests/doc_claims.py` → `ALL 159 checks PASSED`;
  `python3 tests/config_flow_steps.py` → `ALL 496 checks PASSED`;
  `python3 tests/harness_headers.py` → `ALL 105 HARNESS HEADER CHECKS
  PASSED` (see Red checks for one non-reproducing run);
  `python3 tests/backtest.py` → `ALL 25`; `python3 tests/manual_plan.py` →
  `ALL 85`; `python3 tests/finite_boundary.py` → `ALL 83`;
  `python3 tests/guard_pins.py` → `ALL 9`; `python3 tests/solar_alignment.py`,
  `python3 tests/wood_advisor.py` (7), `python3 tests/deployment_shape.py`,
  `python3 tests/typing_ruler.py` (11), `python3 tests/env_drift.py`
  (`NO STALE FIXTURE: 5 committed fixture(s)`) pass; `python3 tests/edge.py`,
  `python3 tests/validate.py`, `python3 tests/plan_view.py` exit rc 0.
- `node tests/card.mjs` → `ALL CARD CHECKS PASSED`; `node tests/card_drift.mjs`
  → `identical in all 40 states` (re-run after the second merge; the merge
  touched the card bundle).
- `node .claude/workflows/policy_lint.mjs` → `TOTAL: 0 error(s) across 40
  policy file(s)`; `node .claude/workflows/brief_lint.mjs` → carry-1774 and
  carry-1776 lint with 0 errors; `node .claude/workflows/rules_sync.mjs
  --check` → ok.

## Red checks

- `tests/features.py` `R9-F2.1 P3: the shipped storage plan is no worse on
  its own objective than the half-price floor's plan refined under it`
  fails on this Mac (and `tests/dst_checks.py`'s seven Mac names, unrun
  this round, were the same seven at base and head in round 1). Answer: the
  failure is a BLAS-kernel knife-edge this Mac's Accelerate produces and
  CI's Linux runner does not (round 1 measured it identical at the merge
  base; `tools/audit/harnesses/k1725_blas_kernel_gap.py` is its
  instrument); the cheapest detector that can see it is CI's environment,
  which is the gate that judges it. Disclosed, not chased.
- `tests/harness_headers.py` printed `1 of 105 ... FAILED` once, in the
  first run after the second merge, chained after `tests/entities.py`;
  three standalone re-runs of the same command at the same head print
  `ALL 105 ... PASSED` and leave the tree clean. The failing check's name
  was not captured (the chain kept only each command's last line). This
  branch adds one harness (`solve_inputs_parity.py`, round 1) and touches
  no committed harness output; if CI reproduces the flake it is main's.
- `mutation` will refuse the 21 added unpinned sites until
  `mutation-autofix` pins the killed ones (`ci-autofix.md`); the drive
  names the killer of each (round 1's list, one site consolidated away by
  main). Wait for the bot commit; do not duplicate.
- `nightly-status`/`delivery-status`: this diff touches neither their
  scripts, `tests.yml`, `governance.yml`, the plan, `HANDOVER.md` nor a
  row it did not add (the `.claude/workflows/policy_lint.mjs` exemption),
  so they are owed no answer; main's nightly was not red at `1913f0dd7`'s
  stamp.

## Forward-carry

- **R9-EG-A4 (#1774)** → `.claude/workflows/carry-1774.json`, in this PR:
  the round-1 review planted a hub write after `_refresh_model_corrections()`
  and both `hub_solve_writes` and `arch_score_head.py` stayed green, so a
  required delta-S can be fed by writes the solve-path barrier is blind to;
  the carry names the plant, the widened-engine figures and the
  re-measurement instruction. EG-A4 decides whether delta-S becomes
  required.
- **R9-EG-A3 (#1776)** → `.claude/workflows/carry-1776.json` (round 1,
  unchanged): `params_over_10` is 27 after EG-B1, not "about 22"; the
  roster's own brief still needs the same text and the orchestrator writes
  it.
- **To tvofi, as product decisions** (unchanged from round 1): the card's
  what-if ignores an active away setback (5.0 kW plan difference), and the
  thermal view publishes the configured floor during a setback.
- **`tools/audit/briefs/D1.md`** (round 1, unchanged): item 4's
  executor-boundary rename from the deleted `_solve_snapshot` to
  `_solve_record`/`_solve_hubs`.

## Approval

This PR touches policy: `tools/audit/briefs/D1.md`, one line in item 4
(round 1; unchanged in round 2). tvofi's approving review at the round-2
head is owed; the round-1 approval, if posted at `6b68bca08`, does not
cover a head that moved. The orchestrator gives it under the round-9
mandate. No budget is raised.

## Friction

none
