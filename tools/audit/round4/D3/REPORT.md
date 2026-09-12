# D3 — test-suite gaps, round 4

- **Dimension**: D3 — what the suite cannot fail on, and unnecessary suite resource use.
- **Baseline**: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697` (the comparison ref everywhere below; never `HEAD`).
- **Tree**: the isolated worktree `.claude/worktrees/audit-r4-D3`, because this
  dimension's method mutates production.
- **Machine**: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11 on OpenBLAS,
  threads pinned to 1 in every harness.
- **Contention**: nine other finders shared the box throughout. `load1` ran
  **4.2 – 10.9** over the measurement window and is recorded per mutant in
  `prescreen.json`. Every wall number here is therefore **provisional**; the
  kill/survive verdicts are counts and are not.
- **Exposure**: none. No `docs/audit-*.md`, `docs/backlog.md`, `docs/plan-*.md`,
  no `git log`, no `gh`.

## Method

`tools/audit/round4/D3/mutant_pool_r4.py` parses every production module into
single-line **deletion** mutants under three operators — `GUARD_OFF` (an `if`
whose whole block stops happening), `CLAMP_DROP` (a `min`/`max` clamp removed),
`STMT_DEL` (a statement replaced by `pass` at the same indent) — and samples
them at **seed 20260912**.

Weights are consequence classes read off COMMON.md's severity ladder and are
recorded in the harness and in `pool.json`: 5 = a wrong line moves money or
comfort silently (`optimizer`, `thermal_model`, `price_model`, `tariff`,
`grid_fee`); 4 = a safety or health guard, or the loop that publishes every
value; 3 = a user-visible published value, a service, config validation; 2 = a
bounded feature module; 1 = presentation and plumbing. Slots are allocated
**proportional to weight squared** by largest remainder, capped at four per
module: a flat weighted draw gave the five weight-5 modules 1.3 slots each out
of 36, because fifty lower-weight modules outvote them. Within a module the
draw is stratified so half the slots (rounded up) go to the guard/clamp
stratum; unstratified, guards drew 4 of 36 because plain statements outnumber
them about five to one in the candidate list (9069 candidate lines in total).

`const.py` is excluded from the pool and the exclusion is recorded in the
harness: deleting a module-level constant assignment is an `ImportError` in
every driver, which measures the import graph rather than the suite.

`tools/audit/round4/D3/prescreen_r4.py` then drives each mutant against **the
fast scripts of its measured closure** from `tests/closures.json` — the brief
excludes `stress.py`, `edge.py` and `backtest.py` from a pre-screen — **plus
`tests/env_drift.py --all 7dd68dd3…`**, the differential gate CI actually runs.
Two further drivers are excluded, both measured rather than assumed:

* **`tests/card_drift.mjs`** renders the working tree's card and the ref's card
  *against the same plan payload*, so a production-Python mutant moves both
  sides identically and it cannot kill one. It is nonetheless in the closure of
  every production module, because `card.mjs`/`card_drift.mjs` inherit
  `plan_view.py`'s whole closure by rule.
* **`tests/golden.py`**, because `tests/run.sh` skips it outright whenever
  `GOLDEN_MODE=drift`, which is what CI runs — and run standalone it resolves
  the mode to `drift` and execs `tests/env_drift.py --all origin/main`, i.e. the
  same differential run this pre-screen already makes against the baseline SHA.
  Measured: **201.2 s**, against the **0.4 s** `tests/closures.json` records for
  it.

**Kill rule**: a mutant is killed by the first driver whose exit status changes
against the recorded baseline, or whose `N of M … FAILED` count rises above it.
Every gate script here `sys.exit(1)` on failure — `validate.py`, `edge.py` and
`plan_view.py` do it from their own issue lists rather than through
`harness.Results` — so the exit status is a sufficient signal for all of them.
Drivers run **cheapest measured first**, and the run stops at the first kill, so
a killed mutant names the cheapest script in its closure that can see it;
`env_drift.py --all` runs last, only for a mutant nothing cheaper killed.
The baseline was green on all fifteen drivers before a single mutant was
applied (`RESULT baseline_red_scripts=0`).

**Restoration** is checked, not assumed: the harness re-reads the file after
every mutant and asserts its SHA-256 matches the pre-mutation hash.

## Resource use

### 1. `tests/closures.json`'s `recorded` seconds are not the seconds the gate spends

`tests/derive_closures.sh` records a closure by running each script with the
cheapest argument that still touches every file — `golden.py --only
__no_such_scenario__`, `env_drift.py --cache-key <ref> --all` — and
`tests/closure.py` stores the seconds of *that* invocation in
`tests/closures.json`'s `recorded` block. For the two differential guards the
stored number is therefore the seconds of a stub, and it is the only per-script
timing table in the tree.

Measured on this box against the same tree (all wall, all provisional,
`load1` 4.2–6.8, baseline drift cache warm for the second env_drift run):

| script | `recorded` seconds | measured seconds | ratio |
|---|---|---|---|
| `tests/golden.py` | 0.4 | **201.2** | 503× |
| `tests/env_drift.py --all <sha>` | 0.7 | **152.0** (warm cache; 193.2 cold) | 217× |
| `tests/features.py` | 140.4 | 89.8 | 0.64× |
| `tests/entities.py` | 50.8 | 29.3 | 0.58× |
| `tests/optimality.py` | 51.6 | 62.0 | 1.20× |
| `tests/validate.py` | 24.7 | 34.1 | 1.38× |

Nothing in the tree *reads* `recorded[*].seconds` for a decision —
`tests/closure.py` writes it and no other script consumes it — so this is
accounting rather than behaviour. It matters because it is the table a seat
reaches for when sizing a gate run, and it says 0.4 s for the script that
`tests/README.md` documents as `python tests/golden.py` and that costs three
and a half minutes.

### 2. `python3 tests/golden.py` and `tests/env_drift.py --all` are the same measurement

Run standalone with `GOLDEN_MODE` unset, `golden.py` resolves the mode to
`drift` (`resolve_mode`: "Unset means `drift`") and execs
`tests/env_drift.py --all origin/main`. In this worktree `origin/main` resolves
to the baseline SHA, so the two runs compare the same two trees over the same
55 fixtures; measured 201.2 s and 152.0 s respectively. `tests/run.sh` avoids
the duplication by skipping `golden.py` whenever the mode is `drift`, so CI
never pays it twice — but a developer following `tests/README.md`'s "Running one
script at a time" list pays 201 s for `golden.py` and another 152 s for
`env_drift.py`, and gets one answer. Both also `git worktree add` inside the
checkout.

