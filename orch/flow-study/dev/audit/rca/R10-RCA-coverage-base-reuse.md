# R10-RCA-coverage-base-reuse: coverage-ratchet reddens on modules a diff does not touch

Root-cause seat for the round-10 `coverage-ratchet` recurrence. It ran beside the
defect (`dev/governance/roles/root-cause.md`), never as the fixer. Instances: #2320,
#2342, #2343/#2348, and main itself.

**Defect.** The `coverage-ratchet` check goes red on four `custom_components/`
modules a diff does not touch — `early_cutoff.py 81.53%`, `coordinator.py 84.14%`,
`sysid.py 91.28%`, `price_model.py 94.77%` — all below the 95.0% `module_percent_floor`,
and the package at 95.61% below its 96.0% floor. The same tree measured fresh reads
green: `early_cutoff.py 100%`, `coordinator.py 97.85%`, `sysid.py 96.7%`,
`price_model.py 99.45%`, package 98.61%, zero modules below floor.

## 1. Cause

The `coverage` job reuses a script's per-script base data whenever the diff changes no
file in that script's measured closure, and the reuse decision never consults the
recorded floor. The chain is two steps, both floor-blind.

**The keying.** `tools/coverage/coverage_tree.sh` decides reuse through
`tests/closure.py coverage-split`, which calls `coverage_split`
(`tests/closure.py:2880`):

```python
if plan.get("mode") != "scoped":
    return list(stage), []
skip = set(plan.get("skip", ())) - set(plan.get("run", ()))
measure = [s for s in stage if s not in skip or s not in reusable]
return measure, [s for s in stage if s not in measure]
```

A script is reused when the plan is SCOPED and skips it ("no changed file is in its
measured closure") and its base file exists. Nothing reads `tests/coverage_budgets.json`
or the base data's per-module percentages. Reproduced:

```
$ printf 'features\nentities\nharness_headers\n' | python3 tests/closure.py coverage-split \
    --plan plan.json --reuse-dir base      # plan skips features.py; base has .coverage.features
reuse	features
measure	entities
measure	harness_headers
```

`features` is emitted `reuse` with a base value that grades below floor, and no step
checks. The copy itself is equally blind: the `reuse` arm of `measure()` in
`coverage_tree.sh:177` is a bare `cp` of `.coverage.$s` from the base.

**The consequence.** `coverage` then combines the reused per-script data with the
freshly-measured scripts, and the pinned `tests/coverage_ratchet.py` grades that
combined JSON. When the reused data does not reproduce the base's own green
measurement, the grader reddens on a head that changed nothing in the module.

**Measured on #2342's push to main** (run `39018747004`, job `117357623002`): the plan
was `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, with
`reused tests/features.py's coverage from the base: no changed file is in its closure`
and `reused tests/boost_drift_replay.py` likewise. The grader printed

```
FAIL package coverage 95.61 % >= 96.0 % (20611/21558 statements, ...)
FAIL every module >= 95.0 %  (4 below)
     early_cutoff.py: 81.53 %
     coordinator.py: 84.14 %
     sysid.py: 91.28 %
     price_model.py: 94.77 %
```

The immediately preceding push #2341 (run `38983243676`) did a FULL fresh measurement
of the identical production tree (`MODE: FULL`, `ran tests/features.py`, zero `reused`
lines) and graded `ok package coverage 98.61 %`, `ok every module >= 95.0 % (0 below)`.
The 2026-10-17 nightly (run `39011974246`, HEAD `e3f3b312f`) measured the same tree
fresh and read the same green numbers. The production statement count is identical in
all four payloads (21558, 77 files), so no production line moved: the 81.53% is a
spurious artefact of the reuse path, not a real regression.

## 2. Process state: (d)

The reuse was sound under the precondition **"the base's per-script data is a faithful,
green measurement of the current tree."** That precondition was a property of the
original design, stated in the round-9 prestudy
`dev/audit/rounds/round9/prestudy/coverage-fast-scoping-prestudy.md`: the push to main
is "both the detector (red within one merge) and the producer of the per-script base
the next PRs reuse," so the base is always a fresh green run.

The V1 lever removed that guarantee. `tests/closure.py:2958` `coverage_summary`, the
instrument's own record of the change, says a reused script's data "is NOT re-measured
by this run or by the pushes after it -- the full re-measure backstop the push arm used
to be is gone." With the push arm now reusing too, a base script can carry data that
was never re-validated against the floor, and the reuse path has no floor check to
notice. The precondition changed underneath the process; nothing made the process
notice.

Not (b): the reuse path ran exactly as written. Not (a): the closure-and-marker
discipline existed and ran. The state is not the design failing from the start; it is a
precondition the design relied on being removed without the reuse path gaining the
check that would make its loss loud.

## 3. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, per release cycle
(the round). Class: `coverage-ratchet` reddens on a head that did not change the module.

- **P(recurrence), measured.** 4 instances in round 10 (#2320, #2342, #2343/#2348,
  main) over the round's ~3-day window. Frequency 4 per cycle.
- **cost(defect) per instance.** A spurious red owes the `defect-root-cause.md` second
  trigger (a named cheaper detector or a recorded none) from the PR's author, plus a
  diagnosis of a check that is not the head's fault, plus a red on main that holds
  `nightly-status` and blocks the record until the orchestrator drains it. Conservatively
  1–2 seat-hours per instance; 4–8 seat-hours per cycle.
- **cost(countermeasure, recurring).** The backstop re-runs the pinned grader on the
  combined JSON (8 s, the prestudy's measured `coverage-ratchet` grade) on every
  coverage run, and re-measures fully only when that JSON reads below floor after reuse.
  A full re-measure is ~50 runner-minutes (prestudy §1.1: 61 m 01 s worst, ~23 m
  fastest). At 4 recurrences per cycle that is ~3.3 runner-hours per cycle, replacing
  the seat-time cost above; on a healthy tree the 8 s check is the whole cost (~50
  coverage runs per cycle ≈ 7 min).

**Verdict: the countermeasure pays for itself.** 3.3 runner-hours of correct
measurement, plus ~7 min of standing check, is cheaper than 4–8 seat-hours of
mis-attributed diagnosis and a red-on-main that blocks the record — runner-minutes are
an order of magnitude cheaper than seat-minutes, and the re-measure is the measurement
the defect was skipping, not new work.

## 4. Countermeasure

A self-healing floor backstop in the instrument, addressing state (d): the reuse path
must notice its own precondition change by re-validating the combined result against the
floor, and re-measure when a reused measurement grades below it.

In `tools/coverage/coverage_tree.sh`, after the final combine and JSON: if the combined
`coverage.json` grades below the floor **and** any script was reused, re-measure every
script (no reuse) and re-combine, so the grader never sees a stale union.

**Failing on the defect** — the #2342 combined JSON reads `early_cutoff.py 81.53%`,
`coordinator.py 84.14%`, `sysid.py 91.28%`, `price_model.py 94.77%`; the pinned grader
prints `FAIL every module >= 95.0 % (4 below)` and the backstop fires.

**Passing once fixed** — the full re-measure the backstop triggers is the same
measurement the three fresh runs produced: `early_cutoff.py 100%`, package 98.61%,
0 below; the grader prints `COVERAGE RATCHET PASSED`.

**Null control** — on a healthy tree the reused JSON grades at/above floor, the backstop
does not fire, and nothing re-runs (8 s standing). It cannot go green by skipping: it
re-measures rather than short-circuits, so a genuine drop (a real module below floor)
still reddens the head that caused it, now attributed correctly.

The exact mechanism by which the reused per-script data fails to reproduce the base's
own green measurement (a line loss across the cache/restore/re-combine, not reproduced
by a minimal local `coverage combine` of a copied file) is a follow-up; the backstop
closes the class regardless, because it guarantees the grader grades a faithful
measurement.

Class: nearest `bugclasses.json` entry is **I3** ("a ... CI check ... runs a stale
ref"); the coverage lane is a new instance of the stale-ref mechanism.

## Reproduce

- Pull the #2342 and #2341 and nightly `coverage-json` artifacts:
  `gh api repos/tvofi/heatpump_optimizer/actions/artifacts/{12096042211,12079121316,12093456536}/zip`.
  Compare `files[".../early_cutoff.py"].summary`: #2341 and nightly read 157/157, #2342
  reads 128/157. The production statement count is 21558 in all three.
- Read the #2342 coverage job log (`gh api .../actions/jobs/117356122208/logs
  --allow-escape-sequences`): `reused tests/features.py's coverage from the base`, then
  the ratchet job `117357623002`'s `FAIL every module >= 95.0 % (4 below)`.
- The keying, locally: a scoped `plan.json` skipping `features.py` and a `base/` with a
  `.coverage.features`, run through `tests/closure.py coverage-split`, emits
  `reuse features` without reading the floor.
