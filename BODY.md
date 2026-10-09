Countermeasure for `RCA-1565-mutation-timeouts`, established by a root-cause seat:
the nightly mutation lanes bound each driver's first run below the pool factor the
lanes themselves measure, which reddened four of the six consecutive scheduled runs
from 2026-10-03 to 2026-10-08 (last green `36984959667`, 2026-10-02T08:36:04Z).

The bound was `max(--timeout floor 1200 s, TIMEOUT_SCALE 3 x the driver's *solo-gate*
recording)` while the lane drives the same script in a 3-worker pool at 1.3-3.3x that
recording; `closure.SECONDS_BAND = 2.0` deliberately keeps a committed value up to 2x
below the cost CI last measured, so the surviving headroom was `3 / 2 = 1.5x` against a
pool factor the tree's own comment states reaches 3.4x. Derived from the committed table
with the tree's own `driver_timeout`, `tests/boost_drift_replay.py`'s bound was 1576 s on
10-07 (CI printed `timed out after 1576s`; the sibling lane measured the pool cost at
1573 s -- three seconds of margin) and 2401 s on 10-08 (CI printed `timed out after
2401s`); on 10-03/04/05 it had no recording and fell to the bare 1200 s floor while the
script really costs >= 1573 s in the pool. When it tripped, `baseline_refusal` voided
every mutant verdict and printed "Fix the suite first" while the same head's committed
entry said `{"seconds": 800.2, "rc": 0}` -- the suite was green and the lane was judging
its own bound.

This lands RCA §5 items 1-3 and the record. It does **not** re-tune `SECONDS_BAND`
(tvofi set it 2026-10-08 for merge-text hygiene -- a different concern); it decouples the
*bound* from the *band*. The fourth arm -- honouring `EXCLUSIVE` under `--scope full`, the
null-control "kills" of 10-03/10-04 -- is an unpinned-count raise (`budget-raise-gate`,
decision 0013) and is routed to the owner, not built here.

## Head

`955dd09a3eab730ecaa3f6be55359781c5b4d201` (branch `fix/r9-nightly-mutation-bound`,
merge base `b2b6acd64` = `origin/main` at dispatch). Every figure below was measured at
this head; the CI-evidence figures cite runs at the heads named in each line.

## Mutation proof

The five checks are in `tests/entities.py`, named `RCA-1565 …`, driven as functions
(never a nightly run). `PYTHONPATH=tests/hastub python tests/entities.py`.

**Failing arm -- the whole fix removed** (the merge-base `tests/mutation_table.py` restored
over the fix, my `entities.py` checks in place): `3 of 2239 ENTITY CHECKS FAILED`, exit 1.
The three that go red are exactly the defect checks; the two null controls stay green:

```
FAIL RCA-1565: the baseline bound covers the MEASURED pool cost with the scale's margin, not TIMEOUT_SCALE x a band-stale solo recording
ok   RCA-1565 null control: a healthy driver's bound still covers its pool cost, the seed never lowers a bound, and env_drift stays floor-bound (not scaled)
FAIL RCA-1565: the pool measurement round-trips through pool_seconds.json, and an absent/unreadable/malformed file seeds nothing (fail-soft, never a smaller bound)
FAIL RCA-1565: a baseline that TIMED OUT against a green committed recording names the stale recording and the bound, not 'fix the suite first'
ok   RCA-1565 null control: a real red baseline (a failing check, not a timeout) still says 'fix the suite first' and names the check
```

**Passing arm -- the fix in place**: `ALL 2239 ENTITY CHECKS PASSED`, exit 0 (all five green).

**Surgical mutations** (each isolates one production predicate; the check that keys on it
goes red and the other four stay green -- so no check is vacuous). Both measured with
`PYTHONPATH=tests/hastub python tests/entities.py`, then restored with
`git checkout HEAD -- tests/mutation_table.py` (confirmed `mutation_table.py == HEAD`):

- MUTATION A -- `seed_pool_seconds`'s fold neutered (`out[s] = max(...)` -> `pass`, the pool
  measurement ignored): `1 of 2239 ENTITY CHECKS FAILED`, and the one red is

      FAIL RCA-1565: the baseline bound covers the MEASURED pool cost with the scale's margin, not TIMEOUT_SCALE x a band-stale solo recording

  (the bound falls back to `3 x solo = 2401`, below the `3 x 2401 = 7203` the check needs).
  The round-trip and wording checks stay green -- they do not read the fold.
- MUTATION B -- `baseline_refusal`'s timeout arm neutered (`timeouts = []`, every red treated
  as an ordinary failure): `1 of 2239 ENTITY CHECKS FAILED`, and the one red is

      FAIL RCA-1565: a baseline that TIMED OUT against a green committed recording names the stale recording and the bound, not 'fix the suite first'

  (the verdict reverts to "Fix the suite first" and omits "STALE"). The bound and round-trip
  checks stay green.

The amend that carried these proofs' head (`955dd09a`) is comment-accuracy only in
`mutation_table.py` (the carrier is `actions/cache`, not an artifact download) plus
`continue-on-error` on the cache save in `tests.yml`; no measured logic moved, and the green
arm below was re-taken at `955dd09a`.

## Null control

The unmodified tree, and what the fix leaves alone:

- **The two null-control checks read flat at both ends** (green on the unfixed tree in the
  failing arm above, green with the fix): a healthy driver's bound already covered its pool
  cost, so the fix does not fire on it, and a real red baseline still says "Fix the suite
  first". Nothing is skipped to reach green.
- **Re-taken at this merge base** (`b2b6acd64`), committed solo seconds via the tree's own
  `recorded_seconds()`, pool costs from CI job `113233890923` (2026-10-08): `features.py`
  solo 730.5 / pool 772, `stress.py` 760.6 / 434, `entities.py` 259.6 / 142,
  `harness_headers.py` 199.0 / 211 -- each bound (floor 1200 or the scale) covers its pool
  cost before and after. `env_drift.py`'s solo recording is the declared 0.9 s stub
  (`closure.py` #934) against a 524 s pool cost: it is protected by the **floor** (1200),
  not the scale, and the fix reads flat on it -- the seeded bound rises to 1572 and still
  covers 524. The seed only ever raises a bound (`max(solo, pool) >= solo`, `driver_timeout`
  monotonic), so no driver's protection shrinks.
- **Fail-soft**: `pool_seconds(None)`, a missing file, and a malformed file each read as
  `{}`, so the bound falls back to the solo recording -- today's behaviour, never a smaller
  bound. A cache miss on the first nightly is therefore safe.

## Figures

- Six consecutive red scheduled runs; last green `36984959667`:
  `gh api "repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?event=schedule&per_page=12" --jq '.workflow_runs[] | [.id,.head_sha[0:9],.created_at,.conclusion,.status] | @tsv'`.
- The reproduced bounds 1200 / 1576 / 2401 / 4469 from the committed table with the tree's
  own function: `python -I -c 'import sys; sys.path.insert(0,"tests"); from mutation_table import driver_timeout; ...'` over `git show <head>:tests/closures.json` for heads `2e569748a fb11a0172 a1da8d381 be0cb8213 816547efe b2b6acd64` (`logs/bounds_reproduction.txt`).
- CI's printed timeouts and the 1573 s completed run: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs --allow-escape-sequences` for `112708109605`, `112708109541`, `113233890923` (`logs/job-*.log`, `logs/pool_tables.txt`).
- Voided lane work 63.4 / 64.2 / 72.4 min: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id> --jq '[.started_at,.completed_at] | @tsv'` for the same three jobs.
- Failing arm `3 of 2239 ENTITY CHECKS FAILED` (merge-base `mutation_table.py`), passing arm
  `ALL 2239 ENTITY CHECKS PASSED` at this head: `PYTHONPATH=tests/hastub python tests/entities.py`
  (`logs/entities_FAILINGARM.txt`, `logs/entities_FINAL.txt`; the surgical mutations A/B are
  `logs/entities_MUTA.txt` / `logs/entities_MUTB.txt`).
- `fold_ledger.py check` clean (`101 rca entries`, `0 violation(s)`): `python3 -I tools/audit/fold_ledger.py check`.
- Structural ratchet: `PYTHONPATH=tests/hastub python tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- Scoped-gate selection: `python tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: FULL -- ... .github/workflows/tests.yml changes the gate itself`; `scope.run` names nothing to run locally, so the remainder is CI's.

## Red checks

- **`nightly-status`** (and `delivery-status` if it reads red on this PR): this diff touches
  `.github/workflows/tests.yml`, so `defect-root-cause.md`'s exemption for the main-grading
  reporters does **not** apply and the body owes them an answer. The red is `main`'s
  *stranded* nightly conclusion -- the six-night streak this PR is the countermeasure for
  (the bound arm reddened 10-03/04/07/08) -- not a regression this diff introduces: a
  scheduled run's conclusion attaches to whatever commit was `main`'s head when the cron
  fired, and this branch is not that head. Cheaper detector: `nightly_status.py` itself is
  the detector (it grades `main` and fails closed); there is no cheaper one, and the remedy
  is the orchestrator's on `main` -- fix the lane (this PR) and dispatch Tests on the default
  branch once it merges. Standing cost: none added here.
- No check this diff turned red on its own head is expected: `entities.py` is green at this
  head (all 2239), `structure.py` passes, `fold_ledger.py check` is clean, the `mutation`
  lane's pool is empty (no production file is touched), and the four floor-override jobs and
  every `mutation-ledger`/`mutation-nightly` command pin in `entities.py` are unchanged
  (verified: `--scope full --drain "$out" --max 40`, `--seed`, `--budget-minutes 270` present;
  no `secrets.` or `contents: write` added to the measuring job).

## Forward-carry

`none` owed to a later stage's brief. The one finding that changes a later decision -- the
`EXCLUSIVE`-under-`--scope-full` arm (iv), an unpinned-count raise -- is the owner's
(`budget-raise-gate`, decision 0013) and is already routed to tvofi per the dispatch; it is
recorded as refused-and-routed in `dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` §4/§5 and in
the `bugclasses.json` countermeasure, not carried into a stage brief. The RCA's other
same-shape causes (`record-autofix` has no `if:`; `closures-autofix` is `pull_request`-only
so a schedule-run staleness has no repair lane) are named in the RCA doc and left to their
own items per the dispatch's out-of-scope list.

## Friction

defect-root-cause.md: contradiction: the dispatch scoped item 3's carrier as "an `if: always()` step" on `mutation-ledger-push`, but that job writes through the `hpo-ledger` App whose write-set decision 0011 pins to "new files under `tests/mutation_ledger/killed_by/` and nothing else" (enforced by `drain_write_set_problems` / `drain_push_problems` and an `entities.py` pin), so persisting `pool_seconds.json` to `main` through it would widen a policy grant a fixer does not own. Took the RCA's named alternative ("or the lane's artifact"): `actions/cache`, already pinned in this workflow for the drift baseline, which needs no write grant, no secret (so the measuring job keeps decision 0011's invariant) and adds no job to the four that override the read-only floor; the `if: always()` write rides `mutation-ledger` itself, which runs on the schedule whatever the drive concluded.
