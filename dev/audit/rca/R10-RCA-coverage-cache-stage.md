# RCA: the coverage cache stages the parent's data under the child's marker

Seat: round-10 root-cause, class `N-cache-stage-nests`. The cause was measured
at tree `b254b5b069c2` (`origin/main`, 2026-10-17); the countermeasure lands in
the same pull request as this record.

**Relation to `R10-RCA-coverage-base-reuse.md` (#2349).** That record traced the
same reds to reuse that never consults the floor, landed a floor re-validation
backstop in `tools/coverage/coverage_tree.sh`, and left open "the exact
mechanism by which the reused per-script data fails to reproduce the base's own
green measurement". This record is that mechanism: the base data is not the
base's. The backstop stays and is not superseded — it is the floor-side guard —
but it is blind in two places this fix closes: a stale base that grades
**above** the floor passes the backstop and the ratchet alike, and every stale
base that grades below it now costs a full re-measure of every script instead of
a red.

Instances: #2320 (`8833a1d9a`), #2342 (`e10481396`), #2343/#2348 (`e3f2468c6`,
`0759c90ec`), and `main` at `b254b5b06` (required `coverage-ratchet` red,
job 117357623002, run 39018747004).

## Root cause

### Cause, reproduced

The `coverage` job's push arm saves its per-script data with
`tests.yml`'s `Stage this commit's per-script coverage`:

```
cp -R "$W5P_WORK/out/per" "$RUNNER_TEMP/coverage-base"
```

`cp -R src existing-dir` copies `src` INTO `existing-dir`. Since 2026-10-13
(`a99be2532`, "feat(V1): per-script coverage reuse on the push arm") the push
arm also **restores** the previous push's entry into that same path, and a
trusted restore does not remove it (`rm -rf` runs only when the marker check
fails, `tests.yml:755`). So on every push whose restore hit, the step created
`coverage-base/per/` with this run's files while the parent's files stayed at
the top level; the next lines then overwrote `.measured-by` with this commit.
The saved entry's top level is therefore the **parent's** data and its marker
the **child's**. The next run trusts the marker and reuses the parent's data —
recursively, so the top level freezes at the last cache miss (or discarded
restore), while each entry grows a nested `per/` no consumer reads.

Reproduced at `b254b5b06` with `gh`-fetched job logs and uploaded artifacts:

- The `coverage` job (117356122208) restored
  `coverage-per-v1-Linux-e3f3b312…`, printed `trusted`, planned
  `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, printed
  `SKIP tests/features.py (closure: 134 files, no changed file is in its
  measured closure)` and `reused tests/features.py's coverage from the base`.
  Only `tests/entities.py` was measured (1 measured, 19 reused).
- Its artifact (`coverage-json` 12096042211) reads package **95.61 %**
  (947/21558 missed), `early_cutoff.py` **81.53 %**, `coordinator.py`
  **84.14 %**, `sysid.py` **91.28 %**, `price_model.py` **94.77 %**.
- The **same tree** measured with every script run: `e3f3b312`'s push run
  (38983243676, job 117248717366) printed `MODE: FULL -- every test script
  runs`, `ran tests/features.py exit=0 wall=1028s`, and its artifact
  (12082825478) reads package **98.61 %** (300/21558 missed),
  `early_cutoff.py` **100.00 %**, `coordinator.py` **97.85 %**,
  `sysid.py` **96.70 %**, `price_model.py` **99.45 %**. The nightly at the
  same commit (39011974246, artifact 12093456536) agrees: package 98.60 %,
  `early_cutoff.py` 100.00 %.
- The two trees differ in **six files**, none of them one of the four modules:
  `.github/workflows/pr-contract.yml`,
  `dev/audit/harnesses/closing_keyword_ownership.py`,
  `dev/programme/delivery/2342.md`, `tests/closures.json`,
  `tests/entities.py`, `tools/pr/preflight.sh` (`git diff --stat e3f3b312
  b254b5b06`). A per-file comparison of the two artifacts differs in exactly
  seven of 77 files — the four above plus `dhw_schedule.py`, `freq_control.py`,
  `ledger.py` — and every one of them is in `tests/features.py`'s measured
  closure, which was reused.

The four PR instances carry the same signature (`gh` job logs):

| head | coverage job | plan | reused | ratchet read |
|---|---|---|---|---|
| `8833a1d9a` (#2320) | 8m43s | 3 run / 30 skip | `features.py` | 95.61 %, four modules below floor |
| `e10481396` (#2342) | 5m08s | 2 run / 31 skip | `features.py` | 95.61 %, four modules below floor |
| `e3f2468c6` (#2343) | 44s | 0 run / 33 skip | all 33 | 75.16 % `early_cutoff.py` |
| `0759c90ec` (#2348) | 49s | 0 run / 33 skip | all 33 | 90.67 %, `coordinator.py` 59.14 % |

`e3f2468c6` and `0759c90ec` are the class's clearest shape: **nothing was
measured**, so the whole payload was the frozen top level.

The cache chain is visible in the entry metadata (`gh api
repos/tvofi/heatpump_optimizer/actions/caches`): `81ae048e8` 52 688 B at
15:34Z, `92accb2cf` 51 606 B at 19:36Z, `d7b171229` 59 598 B at 22:26Z,
`e3f3b312` 61 602 B at 00:07Z, `b254b5b06` 53 415 B at 08:56Z, all created
after their run's measured `per/` was written. The e3f3b312 entry was created
by a run that measured every script (job 117248717366) yet the next push that
restored it read 81.53 % on a module that run measured at 100.00 %.

### Class search

`grep -rn 'cp -R\|cp -r' .github/workflows/*.yml` returns one hit:
`tests.yml:890`, this step. The other restore→save pairs do not share the
shape:

- `pool-seed` (mutation-nightly → mutation-ledger): the save writes exactly
  the file its consumer reads (`cp …/pool_seconds.json
  $RUNNER_TEMP/pool-seed/pool_seconds.json`), so a stale sibling cannot be
  read.
- `lane-proof-*`: the saving job (`lane-proofs`) creates each directory with
  `mkdir -p`; the restore lives in `closure-scope`, which never saves.
- `drift-baseline`: a push never restores it (the restore's `if` excludes
  `push`), and `env_drift.py` re-checks the baseline's key inside, so a wrong
  restore is a miss.

The reach beyond this instance: any lane that restores a cache and then saves
a *superset* of it silently freezes the restored part, and the failure is
invisible because the marker/key is rewritten last. The dangerous direction is
not only a false red: a stale base can also read **higher** than the tree, so
a real coverage regression can pass `coverage-ratchet` — the ratchet is
one-sided and this bypasses its floor rather than tripping it.

### Process state: (d) the process was sound and its precondition changed

The stage step is `af2ac7637` (2026-10-01, "save the per-script coverage from
the path the restore names (R9-F10.9b)"). It was written when the restore step
carried `if: github.event_name != 'push'` — quoted from the `a99be2532` diff,
which **removed that line** and added:

```
RESTORE_BASE=$(git rev-parse HEAD^1)
...
key: ${{ steps.covkey.outputs.restore_key }}
```

`a99be2532` (2026-10-13, "feat(V1): per-script coverage reuse on the push
arm") left the stage step untouched. The step's precondition — "on a push,
`$RUNNER_TEMP/coverage-base` does not exist when this runs" — was true under
the 2026-10-01 contract (a push restored under its own key, which never hit)
and false under the 2026-10-13 one (a push restores its parent by `HEAD^1`,
which hits).

This is not (b): every run executed the step; no line was skipped. It is not
(a): the step existed and its test existed. It is not (c) in the sense of a
misapplied unit: the same command string was correct before the V1 change.
The unit was a step whose correctness rested on a precondition that another
pull request removed. The countermeasure for (d) is the one
`dev/governance/roles/root-cause.md` names: make the process notice its own
precondition change. The existing `_cov_marker` fixture in `tests/entities.py`
created `w/out/per` and ran the step with **no** `coverage-base`, so it encoded
the old precondition and could not see the change.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock
per release.

- **Standing cost.** CI: one `rm -rf` of a ~60 KB directory, below the step's
  own ~0.1 s. The test: `_cov_stage_entry` drives the step twice in temp
  directories, measured over 50 runs at 61.5 ms per run → **0.123 s** per
  `tests/entities.py` execution. That script runs in `fast` on every PR and
  push; at 18.5 PRs per release (`git log --merges --first-parent
  v6.7.1..v7.0.0`, the measurement in `R10-N-staleness.md`), that is
  **2.3 s per release**. The `v2` key adds one full re-measure per
  pull request/push once (the current chain is poisoned and would otherwise
  stay so), which is the same coverage lane that would have run.
- **P(recurrence).** Measured: 4 instances in the 32 h from
  `2026-10-16T00:51Z` (#2320) to `2026-10-17T08:57Z` (main) — **3.0 per day**
  of the round-10 fix wave. With the defect in place, every run whose diff
  clears a covering script reuses the frozen data; the trigger is the
  closure's own skip, so it recurs on essentially every such run.
- **cost(defect).** The measured `coverage` lane wall clock per occurrence:
  5m08s (`e10481396`), 8m43s (`8833a1d9a`), 8m27s (`b254b5b06`). The red is
  deterministic — a re-run reproduces it — so clearing it costs a diagnosis
  seat plus the workaround (forcing a re-measure or changing the key) and a
  re-run. Lower bound used: **308 s** per occurrence.
- **Verdict.** At the measured frequency, 308 s × 3.0/day against 2.3 s per
  release: the barrier passes by more than two orders of magnitude. Even at
  `P = 0.01`, 3.1 s against 2.3 s.

### Countermeasure (this seat's pull request)

Addresses (d):

1. **Clear the destination before staging.**
   `rm -rf "$RUNNER_TEMP/coverage-base"` ahead of the `cp -R`, so the entry's
   top level is always this run's `per/` whatever the restore left. This makes
   the step independent of the precondition rather than asking the next seat
   to remember it.
2. **Invalidate the poisoned chain.** The cache key version moves
   `coverage-per-v1` → `coverage-per-v2`. Without it the first post-fix push
   would still reuse its parent's stale scripts through `out/per`. (#2349
   changed `tools/coverage/coverage_tree.sh`, a `hashFiles` input, so its own
   push missed once and re-seeded from a full measurement; the next pushes
   hit and nested again — `33e0ee4a2` (job 117436564587) restored
   `1138a4ef5`'s entry, printed `trusted=true` and
   `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, and `9804c7700`
   (job 117458468301) restored `33e0ee4a2`'s and ran 16 scripts whose fresh
   data its save then nested under `per/`. So the chain since #2349 is again
   frozen at its last miss; it reads green only while the frozen data still
   clears the floor.) A new
   version makes the next push and every pull request miss once, measure every
   script, and re-seed a correct entry; the measured correct values above
   (98.61 %) show the floor is met.
3. **A detector that names the precondition.** `tests/entities.py` gains
   `_cov_stage_entry`, which runs the step's own `run:` with a populated
   `coverage-base` (the trusted-restore shape) and with none (a miss), and
   asserts the top-level file is this run's and no nested copy exists.

Demonstration, both runs:

```
OLD trusted restore top-level='PARENT'   nested=True  -> FAIL
OLD miss            top-level='THIS RUN' nested=False -> PASS
NEW trusted restore top-level='THIS RUN' nested=False -> PASS
NEW miss            top-level='THIS RUN' nested=False -> PASS
```

`OLD` is the step at `b254b5b06`, `NEW` the step with `rm -rf`; the miss arm is
the null control, showing the check fires on the restored-directory
precondition and not on the step in general. The fixture is also the first one
that drives the step in the shape the push arm actually gives it.

## Needs tvofi

No policy change. `tests.yml` and `tests/entities.py` are measured for tokens
under `tools/policy/policy_lint.mjs --budgets`; the added lines sit inside the
five aggregate caps' `_band`, so no cap is raised.
