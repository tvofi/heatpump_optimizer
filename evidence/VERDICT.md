Fix review: blocked 3fce22f6a1313e439d6ff880f85bd2fa72731a9f class-open: inputs.problem_messages
bus-nonce: 9eb029b2427576829c2c30de676123d9

Round 1. Measured at `3fce22f6a1313e439d6ff880f85bd2fa72731a9f` (re-read from git
before posting; unchanged), merge base `524c1896b6943b3da03d6cad61420ced31e14c9c`.

## The harness

Reviewer-built and disclosed as mine, not the finder's: #2814 ships no committed
harness (its `Reproduction` is prose over a live download), so `evidence/harness.py`
was written for this review from the issue's own reproduction rule. It drives only
`diagnostics.async_get_config_entry_diagnostics` and the collector's public
`as_dict` / `async_bundle`, so it runs unchanged at both ends. It prints its own
`RESULT` lines: `evidence/base.txt` (merge base) and `evidence/head.txt` (head),
with `evidence/run.txt` holding the exact commands.

Metric: the value the download PUBLISHES under `inputs.input_ages_minutes`,
`inputs.input_problems[].age_minutes`, `inputs.problem_messages`,
`plan.plan_stale`, `plan.plan_age_minutes` and the debug manifest's
`self_tests_at` / `self_tests_age_hours`. Perturbation and null control: the export
clock — exported at the publish instant the ages must not move; exported 14 minutes
later they must.

## 1. The age changes hands — established

Payload published with `indoor` 2.0 min and `outdoor` 5.0 min old; exported 14 min
later:

- base: `input_ages_minutes` `{indoor: 2.0, outdoor: 5.0}`,
  `input_problems[0].age_minutes` 2.0, `input_ages_at` absent.
- head: `{indoor: 16.0, outdoor: 19.0}`, 16.0, `input_ages_at`
  `2026-01-12 08:00:00+00:00`.

Null control (exported at the publish instant): 2.0/5.0 and 2.0 at both ends.
`plan_stale` is re-judged at the export: payload `False`, plan 96 min old at export
— base `False`, head `True`; a 15-minute interval with a 60-minute-old plan is
`False` at both ends, so the floor is not doing the work. `_plan_is_stale` over a
bare config: a `True` interval base `True`, head `False`; `"15"` base raised
`TypeError`, head `False`.

## 2. Every other age in the bundle — one seam is open (the block)

Leaves that move between publish and a 14-minute-late export (R5, head):
`exported_at`, `plan.plan_age_minutes` (1.0 → 15.0, already export-dated at base),
`inputs.input_ages_minutes` (2.0/5.0 → 16.0/19.0, new at head),
`inputs.input_problems[0].age_minutes` (2.0 → 16.0, new at head), and the new
`inputs.input_ages_at`. Unmoved by design: `max_age_minutes` (a threshold),
`coordinator.weather_stale_hours` / `tibber_outage_cycles` (null), and the
manifest's new `self_tests_at` / `self_tests_age_hours` (computed at the export).

**`inputs.problem_messages` does not move, and now contradicts its siblings.**
Same payload, exported 40 min later (R8b):

- head: `problem_messages` `["sensor.indoor: stale (last report 20 min)"]` beside
  `input_problems[0].age_minutes` 60.0 and `input_ages_minutes` `{indoor: 60.0}`;
  `input_health` `ok`, `stale_inputs` `[]` — an age twice its own
  `max_age_minutes` (30.0) reported as healthy.
- base: 20 / 20 / 20, `input_health` `ok` — internally consistent.

`diagnostics._inputs_at` re-bases two of the three age-bearing fields in `inputs`
and leaves the rendered string and the two verdicts at publication time; the change
therefore *creates* the contradiction (it did not exist at base). The body
enumerates three residues and dispositions neither `problem_messages` nor
`input_health` / `stale_inputs`, and the new tests never name them (`grep` finds
only a leak-text fixture at `tests/debug_collect.py:1476`). The body also names no
enumeration rule for the class (#2814 states more than one seam). This is the
`plan_stale` verdict the PR re-judged, left un-re-judged one field away.

## 3. The download time cannot be absent — established

- No `input_ages_at` at all, exported 14 min late: `input_ages_minutes`
  `{indoor: 2.0, outdoor: 5.0}`, problem age 2.0 — as published, never zero.
- `input_ages_at` 5 min ahead of the export clock: same, as published.
- A plan the clock cannot date (`last_optimization` ahead of the export):
  `plan_stale` keeps the payload's `True`.
- A plan never judged (`last_optimization` None, no `plan_stale` key): `None`.

## 4. Mutation pins

The diff adds 12 ledger rows under `tests/mutation_ledger/killed_by/`, not the
eleven `tests/pins/*.json` the brief describes (`tests/pins/` does not exist).
All five anchors name functions that exist at this head. Re-driven each row with
its own `killed_by` driver (`tests/mutation_table.py --anchor … --jobs 1`),
`evidence/pins-summary*.txt`:

| anchor (`tests/mutation_ledger/killed_by/`) | driver | result |
|---|---|---|
| `coordinator.py:plan_stale_limit_minutes CLAMP_DROP 8ee35b1a` | structure.py | reproduced (killed) |
| `coordinator.py:plan_stale_limit_minutes RETURN_DEL 8ee35b1a` | structure.py | reproduced (killed) |
| `coordinator.py:plan_stale_limit_minutes GUARD_OFF 482b8551` | debug_collect.py | reproduced (killed) |
| `coordinator.py:…_plan_is_stale CMP_BOUND 1e075bcb` | debug_collect.py | reproduced (killed) |
| `coordinator.py:…_plan_is_stale RETURN_DEL 1e075bcb` | features.py | not re-verified (timed out) |
| `debugger.py:DebugCollector.as_dict BOOLOP 81d62bfa` | debug_collect.py | reproduced (killed) |
| `debugger.py:DebugCollector.as_dict GUARD_OFF 81d62bfa` | debug_collect.py | reproduced (killed) |
| `diagnostics.py:_inputs_at GUARD_OFF 305ddbe3` | debug_collect.py | reproduced (killed) |
| `diagnostics.py:_inputs_at GUARD_OFF 4a6254b3` | debug_collect.py | reproduced (killed) |
| `diagnostics.py:_inputs_at GUARD_OFF 79397f15` | debug_collect.py | reproduced (killed) |
| `diagnostics.py:_inputs_at RETURN_DEL 02e1c03c` | debug_collect.py | reproduced (killed) |
| `diagnostics.py:_plan_summary CMP_BOUND 7abd2715` | debug_collect.py | reproduced (killed) |

Each printed `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced, 0 not
re-verified`, its driver's baseline `rc=0 failed=0`, and the mutation lane's own
null control `NULL_COMMENT survived`. **Survivors: none among the rows that ran.**
No anchor is re-keyed: none of the five functions carried a ledger row at the
merge base (0 at base, 12 at head), so the silent-revert class does not arise.
The one `features.py` row took 28 minutes in the first pass and was stopped; the
second attempt ran to the 15-minute cap, both stalled inside `features.py`'s own
baseline beside three concurrent `features.py` runs from other seats, so the lane
never reached the mutant. It is **not verified**, not a survivor. A `tests/features.py`
kill is itself weak evidence for this seam: the suite is large and touches the
coordinator broadly, so it can go red for reasons the mutation did not cause.

## 5. `tests/structure_budgets.json` — nothing rises

Three lines change (six in the diffstat): `class_excess_loc` 18067 → 18066 (down), `max_class_loc`
8222 → 8221 (down), `recorded_at` `5261ba84…` → `6fe5170c…` (provenance, not a
metric). No metric rises. `budget-raise-gate` decided exactly that: its log reads
`RESULT budget_raises=0 count` and `PASS: no budget raise; no owner review is
owed` — not a tick, the tool's own verdict. `python3 tests/structure.py` at this
head printed `STRUCTURE RATCHET PASSED`; `tools/audit/archscore/score.py --diff
origin/main` reproduced `dS +0.0012 IMPROVES`, `coord_footprint 2412 -> 2410`.
The two down-movements are earned by deleting `_stale_limit` and the early return.

## 6. Scope

The body accounts for the production plumbing (`InputReader`/`read_at`,
`payload.py`'s `input_ages_at`, `store.py`'s domain row, the coordinator function,
the debugger's two writes) and for four ledger rows. It does not enumerate the
eight rows added by `ci: pin killed mutants` (`e73ff68ca`) — it names the commit
only — and never states the direction of the budget change. Minor, non-blocking,
but it is the same "four rows" account the mutation section leans on.

## Second block: carry-missing

`## Forward-carry` routes the py-spy / BSD `wc -l` finding to
`R10-FLY-SUITE-ENV-FLAKES`. That group's roster entry is `resume.stage:
carries-open` with **zero** carries and its brief contains neither `wc -l` nor
`py-spy`, at this head and at the handoff ref `eb0e5237d2dfe237e0015e8be3745b990e4b7b04`;
`dev/programme/carries/carry-2730.json` does not exist, and `git grep -l
'wc -l < calls'` finds nothing in the tree or at that ref. A PR comment is not
propagation (`finding-propagation.md`): `carry-missing: not carried to
R10-FLY-SUITE-ENV-FLAKES`.

## Not established

- `python3 tests/env_drift.py --all 524c1896b` never completed: the box was
  under 1 GiB free and the run printed nothing before the tool's timeout, so I
  have no drift verdict from it. It is not needed to decide the claim: the diff
  moves no golden fixture (`git diff --name-only 524c1896b...HEAD -- tests/golden
  tests/fixtures` empty) and leaves both claim files byte-identical, so the drift
  set is empty by construction. `--claims-only` passed per the body; I did not
  re-run it.
- The fixer's out-of-tree probe (0/3 base, 3/3 head) is not committed and cannot
  be re-derived; every number in this verdict is my harness's.
- `VERSION`, the manifest version and `RELEASE_NOTES.md` are untouched (diff
  empty); no claim file was re-recorded.

## Observations, non-blocking

- A bool or non-numeric `optimization_interval` now reads as *no limit*: the plan
  can never be stale rather than being caught at the config boundary.
- The two `killed_by: tests/structure.py` rows reproduce, but they kill
  structurally, not behaviourally. `structure.py`'s `dead_top_level_symbols`
  counts a symbol with no load **in the integration** (tests do not count), and
  line 740 is production's only reference to `PLAN_STALE_FLOOR_MINUTES` (and,
  with the return, to `PLAN_STALE_INTERVALS`); dropping either makes them dead.
  Derived from the metric's definition and that grep, not from the run's own
  `FAIL` line, which the lane does not print. The floor's behaviour is pinned by
  the `debug_collect.py GUARD_OFF` row, which drives the 15-minute-interval arm.
