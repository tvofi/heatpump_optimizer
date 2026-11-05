Part 1 of R10-SUITE-HOST-DETERMINISM (issues #2726, #2730): the suite's host-zone, gate-lease-timing and coverage-descendant nondeterminism. This round closes the host-zone class across every script `tests/run.sh` invokes, not only `tests/features.py` and `tests/finite_boundary.py`. The parts named under Forward-carry are not built here.

## Re-cut note

This is round 3's answer to verdict/3170 (round 2, blocked at 0a459e60). The finding was: "class-open: tests/finite_boundary.py still fails host-zone checks at the head under America/New_York (1 of 108) and Asia/Kolkata (2 of 108), and passes under UTC". The body is retaken whole from the template headings, and round history is deleted. Every figure below was re-taken in this pass.

The class is a suite check whose result moves with the host zone (`TZ`) or Home Assistant's configured zone (`HASTUB_TZ`), when it should not. The rule that enumerates the class is `python3 dev/audit/harnesses/host_zone_features.py --suite`. It runs every script `tests/run.sh` invokes (its `run` and `run_always` lines, 38 commands) under seven rows:
- `gate`: `TZ=UTC`, `HASTUB_TZ` unset. This is the null row.
- UTC.
- America/New_York, Asia/Tokyo, Europe/Stockholm and Asia/Kolkata (half-hour).
- Europe/London, a DST zone whose 2026 transitions fall on the EU dates the suite's own instants read (2026-03-29, 2026-10-25). Its winter offset is zero, so a leak there shows only across a transition.

Each zone row sets `TZ` and `HASTUB_TZ` together. Every red row is a seam. The seams the sweep returned at the round-3 tip and at the merge base are below, each with its disposition.

What this round changes on top of the round-3 commits (the finite_boundary instant arm, card.mjs's seam clock, guard_pins' idle-cooling clock):
- **`tests/ha_contract.py`**: four default-case `util.dt` contracts asserted `HASTUB_TZ` unset. So the script read `4 of 96 contracts FAILED` under every configured zone, UTC included. Each contract now evaluates in the zone that a fresh copy of the provider's own `util/dt` module sets with `HASTUB_TZ` absent (`_unconfigured_zone`, `_in_default_case`). The default case is constructed rather than read off the host. The nightly lane copies upstream's module in the same way.
- **`tests/golden.py`**: the `coord_*` payloads move with Home Assistant's configured zone, as a time-of-use grid fee's peak hours and the energy totals' local day rightly do. Under America/New_York, 5 of 56 golden payloads differed from the gate capture (`coord_grid_fee`'s forecast prices took the peak fee five hours early). The configured zone is an input of the installation the scenario describes, so `capture_coordinator` now sets `DEFAULT_TIME_ZONE` to `SCENARIO_ZONE` (UTC, the zone the fixtures were recorded in) at the capture boundary, and restores it after. In that zone the naive `START` freeze is the instant it names, so round 3's aware-freeze workaround is dropped, and one mechanism covers both leaks.
- **`dev/audit/harnesses/host_zone_features.py`**:
  - `--golden-zones` compares every golden payload (`env_drift.py --all`'s 56) per zone with the gate row. golden.py's own drift check compares against a baseline captured in the same zone, so it cannot see a payload that moves with the zone on both sides.
  - Mutants: `golden_scenario_zone` and `ha_contract_default_zone` replace the retired `golden_clock`.
  - A further commit on this topic (3181c947, the faketime `Zone@<wall time>` option) adds an opt-in sweep mode. Nothing below uses it.
- **`.github/workflows/nightly.yml`** (commit 9f5a45ba): a slow-job step runs `tests/features.py` and `tests/finite_boundary.py` under `HASTUB_TZ=TZ=Asia/Kolkata`. This is the cheap one-zone lane that the verdict's second finding asked for, so a reintroduced UTC-literal instant reads red nightly.

No `TZ` or `HASTUB_TZ` is pinned in the suite, the runner or the environment. The only assignments are the harness's own subprocess environment and the nightly step above, which sets a non-UTC zone on purpose. No allowlist entry is added, and `tests/harness_headers.py` is untouched.

Disclosure: a second fixer session ran this topic beside this one. Its commits 9f5a45ba (nightly lane) and 3181c947 (faketime option) and its main merges b68368e2, e581b01c and ab57cc05 are in this head as fast-forwards. No work of either session is dropped.

Carries, each named as built, discharged or next part:

- Carry 1 and Carry 4 (0-based 0, 3; features under a non-UTC zone): BUILT. The class is now the whole suite under every zone the sweep runs (Figures), not only `tests/features.py`.
- Carry 2 (0-based 1; gate-lease one-winner flake): the test-side change is BUILT (a condition wait replaces the 0.15 s hold). The `_free_slot` is_file TOCTOU in `tests/gate_lock.py` is NOT built here and stays open in this carry (Forward-carry).
- Carry 3 (0-based 2; coverage_tree.sh descendants): BUILT. `measure()` waits for processes still carrying the script's own `COVERAGE_PROCESS_START` rcfile path, and refuses, naming the script, after `W5P_DESCENDANT_WAIT`.
- Carry 5 (0-based 4; base-red entities U0c / delivery_status): NEXT PART.
- Carry 6 (0-based 5; scan("HEAD") vs working tree): NEXT PART.
- Carry 7 and Carry 8 (0-based 6, 7; stdlib sampler macOS platform rule, six wrappers): NEXT PART.
- Carry 9 (0-based 8; nightly respawn): NEXT PART.

No new finding is carried forward. The open parts above are this group's own carries, already in its brief, and the verdict's second finding (no CI lane runs a non-UTC zone) is built here as the nightly Kolkata step.

## Head

`04dc60576c344f702b11084d43e9a653d2fe198c` merges origin/main `6777ec33337b256d29ea145d98da413dbf076a2a` (fetched 2026-11-05 before 06:20 UTC) into `cb323c1f8635ec5cd94e80ddfdf3c0ae5adea741`. That merges origin/main `6125b263d94e` into `dc32ec6feb50`, which merges origin/main `8364e62460f6` into `3181c9470`, a fast-forward of the round-4 WIP 1a148834, which contains the PR head 0a459e60. Merge base: `6777ec33337b`. Main's delta from 8364e624 to 6777ec33 is 18 files of seat tooling (`tools/audit/seat/closeout.py`, `prune_refs.py`, `orchestrator_tick.py`, `ledger.py`, `tools/audit/worktree_gc.sh`, `tools/pr/ci_predict.py`), a governance workflow step, a role contract, harnesses, delivery rows and a closures entry. It touches no suite script and no `custom_components/` file, so no suite figure below moved; `prepr.sh` was re-run on each merge. The claim files, `VERSION`, the manifest and `RELEASE_NOTES.md` are byte-identical to origin/main, and the three-dot diff holds no `*_budgets.json`.

Where each figure was taken:
- **The full sweep, the mutants, the golden null and the scratch-baseline drift**: at `e581b01c5371bfc0324e65fd6d6b2cc55f29930d`, whose main parent is `c0b082bc48777199cb9b4998514b20b88ec805a1`.
- **The before sweep**: at `1a148834384e3f81bbaed41809853a06ac902bda`, the round-3 tip.
- **Merge-base controls**: at `d7582ed404a87603bd02fefda610d7ebbe4181e1`.

The branch's own delta from e581b01c to the head is the faketime option in the harness (3181c947, opt-in, unused by the default sweep). The rest is origin/main's. So the PR's touched scripts and the golden null were re-run at the head (Figures).

## Mutation proof

Run by `python3 dev/audit/harnesses/host_zone_features.py --mutant all --zones UTC,America/New_York,Asia/Tokyo,Europe/Stockholm,Asia/Kolkata,Europe/London` at e581b01c. Each mutant is a detached worktree with one fixed site restored to its host-zone read, and it is KILLED when at least one zone reads red. All nine were KILLED, and the command exited 0. Every mutant passes in its UTC row.

- `finite_boundary_leaf_zone` (naive leaves read as UTC): New_York 2 of 108 ("an honest payload comes back byte-identical (null control)", "an instant inside its store's lead survives the load"). Tokyo, Stockholm, Kolkata and London 1 of 108 each ("no stored instant reaches a loader beyond the clock plus its store's lead"). UTC all 108 passed. **KILLED.**
- `golden_scenario_zone` (the capture inherits `HASTUB_TZ` again): `--golden-zones` reads `fail:5/56 coord_all_features,coord_dhw,coord_grid_fee,coord_minimal,coord_two_zone` under New_York, Tokyo, Stockholm and Kolkata. UTC and London (winter instant, offset 0) read 56 equal. **KILLED.**
- `ha_contract_default_zone` (`_dt_default_zone` reads its precondition off the environment again): 1 of 96 contracts failed in every row that sets `HASTUB_TZ`, UTC included. Control: the same mutant in the `gate` row (`--zones gate`) reads `ALL 96`, and the harness prints `SURVIVED`. So the mutant is red only where a zone is configured. **KILLED.**
- `card_seam_clock`: New_York and Tokyo 1 card check failed. **KILLED.**
- `guard_idle_cooling`: Tokyo, Stockholm and Kolkata 1 of 61 failed. **KILLED.**
- `nometer_month`: New_York, Tokyo and Kolkata 1 of 4784 failed. **KILLED.**
- `sysid_night_t0`: Tokyo and Kolkata 1 of 4784 failed. **KILLED.**
- `outage_naive_tick`: New_York 1 of 4784 failed. **KILLED.**
- `humidity_now`: New_York, Tokyo and Kolkata 1 of 4784 failed. **KILLED.**

## Null control

- **The unmutated suite at e581b01c**: `--suite` reads the per-zone counts in Figures. Every script passes in the gate, UTC and London rows. In the four offset zones every script passes except `golden.py` and `env_drift.py --all origin/main`.
- **Those two reds are origin/main's capture, not this tree's.** Both compare this tree's capture with a baseline captured from origin/main's own `tests/golden.py` in the same zone, and origin/main still lets the coordinator scenarios inherit `HASTUB_TZ`. Against a local scratch baseline, `8814fa88dfdb` (c0b082bc with only this diff's `tests/golden.py`, never pushed), `HASTUB_TZ=TZ=<zone> PYTHONPATH=tests/hastub GOLDEN_MODE=drift python3 tests/env_drift.py --all 8814fa88dfdb` read `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE` under New_York, Tokyo, Stockholm and Kolkata, rc=0 each.
- **Zone invariance itself**: `--golden-zones` at e581b01c reads `pass:56 payloads equal to gate` in all six zones. At the merge base d7582ed4 the same comparison read `fail:5/56` (the five `coord_*` payloads) under New_York, Tokyo, Stockholm and Kolkata. So once this merges, origin/main's baseline carries the fix and those two rows go green.

## Unpinned sites

none: the diff adds no production line. The only `custom_components/` change is the `_comparable_ts` docstring in `coordinator.py`; its AST is identical at base and head with docstrings blanked (verdict/3170 evidence/coordinator_ast.txt). `prepr.sh` step 6d is re-read at the head.

## Figures

Class rule: `python3 dev/audit/harnesses/host_zone_features.py --suite` (every `tests/run.sh` `run`/`run_always` command, under the seven rows above, both `TZ` and `HASTUB_TZ` set per zone). Its `RESULT zone.<zone>=<passed>/<total>` lines:

| row | before, 1a148834 | after, e581b01c |
|---|---|---|
| gate | 38/38 | 38/38 |
| UTC | 37/38 | 38/38 |
| America/New_York | 35/38 | 36/38 |
| Asia/Tokyo | 35/38 | 36/38 |
| Europe/Stockholm | 35/38 | 36/38 |
| Asia/Kolkata | 35/38 | 36/38 |
| Europe/London (DST) | 37/38 | 38/38 |

Every seam the rule returned, with its disposition:
- `tests/ha_contract.py`, red in every configured row before, 4 of 96 each: **closed in this diff** (`_unconfigured_zone`). Green in every row after.
- `tests/golden.py` and `tests/env_drift.py --all origin/main`, red in the four offset rows before and after: **closed in this diff** for this tree (`SCENARIO_ZONE`; `--golden-zones` 56 equal in every zone). The residual red is origin/main's baseline capture (Null control: NO UNCLAIMED DRIFT against the scratch baseline in all four zones). It clears when this merges.
- `tests/finite_boundary.py`: green in every row at 1a148834 and e581b01c. At the merge base d7582ed4, `HASTUB_TZ=TZ=<zone> PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` read UTC `ALL 108`, New_York `1 of 108`, Tokyo `2 of 108`, Stockholm `2 of 108`, Kolkata `2 of 108` and London `1 of 108`: **closed in this diff** (round 3's instant arm, the verdict's block).
- `tests/features.py`, `tests/card.mjs` and `tests/guard_pins.py`: green in every row: **closed in this diff** (rounds 1-3, each pinned by its mutant above).
- No other script was red in any row.

Other figures:
- `HASTUB_TZ=TZ=<zone> PYTHONPATH=tests/hastub python3 tests/ha_contract.py` at d7582ed4: `4 of 96 contracts FAILED` in each of UTC, New_York, Tokyo, Stockholm, Kolkata and London.
- `--golden-zones` at the base (the harness's `golden_zones` driven on a d7582ed4 worktree): UTC and London 56 equal; the four offset zones `fail:5/56`.
- At the head dc32ec6f, `python3 dev/audit/harnesses/host_zone_features.py --script <s> --zones gate,UTC,America/New_York,Asia/Tokyo,Europe/Stockholm,Asia/Kolkata,Europe/London` for `tests/finite_boundary.py`, `tests/ha_contract.py`, `tests/guard_pins.py`, `tests/card.mjs` and `tests/features.py`, and `--golden-zones`: every script passed in every row (finite_boundary `ALL 108`, ha_contract `ALL 96 contracts`, guard_pins `ALL 61`, card `ALL CARD CHECKS PASSED`, features `pass:4800` per zone and `pass:4807` in the gate row, which also runs the checks that need `HASTUB_TZ` unset). Golden read `pass:56 payloads equal to gate` in all six zones. Each exited 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL -- every test script runs, nothing is scoped out` (the diff touches `.github/workflows/nightly.yml`). The full gate's script set is the sweep's `gate` row, 38/38 at e581b01c.
- `bash tools/pr/prepr.sh` with this body, on the committed head dc32ec6f: `PRE-PR: dc32ec6feb503e4236d8fd351ee7298f8176bcfa ... rc=0` (its `closures` step printed its own skip, "the diff cannot be scoped, so CI re-records every closure"; `carry` read `0 bad destination(s)`). origin/main then moved to 6125b263, so it was merged and `prepr.sh` re-run on cb323c1f: `PRE-PR: cb323c1f8635ec5cd94e80ddfdf3c0ae5adea741 ... rc=0`. origin/main then moved to 6777ec33 (it changes `tools/pr/ci_predict.py`, a prepr step), so it was merged and `prepr.sh` re-run on 04dc6057: `PRE-PR: 04dc60576c344f702b11084d43e9a653d2fe198c ... rc=0`, with the same `closures` self-skip and `carry` `0 bad destination(s)`.

## Red checks

The whole check-run set at 0a459e60 (55 runs, one page of 100): one concluded red.
- `tests / replay` (job 125268597357): `1 of 176 replay checks FAILED`, `synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 2.385 over its budget 2.173]`. The diff writes no runtime code, and `cpu_ratio` is a CPU-time ratio on a shared runner, so this is the runner class the budget did not key, not a defect of this diff. #3174 (merged 2026-11-04 21:03 UTC, in this head through origin/main) keys that budget by runner class on the run's own BLAS ruler. Cheaper detector: none exists. A runner's SKU is assigned at job start, and the keyed refusal in `tests/replay.py` is the detector.

The head 04dc6057 has no CI yet; its check runs start at the handoff.

## Forward-carry

none

## Friction

none
