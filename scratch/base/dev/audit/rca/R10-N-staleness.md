# RCA: staleness limit shorter than a report-on-change source's quiet interval

Seat: round-10 root-cause, class `N-staleness` (#2234). The class met the per-round and
cross-round triggers: R9 has 1 instance and R10 has 6 (1 judged, 5 beyond the finding).
Tree: `handoff/audit-r10-register` at `2c3272eb7`. This seat fixes nothing.

## Root cause

### Cause, reproduced

`InputReader` measures a reading's age as the time since Home Assistant last wrote the
entity (`last_reported`, else `last_updated`). It compares that age with
`const.INPUT_MAX_AGE_MINUTES[key]`. A source that reports only on change writes nothing
while its value holds. For that source, age measures how still the value is, not whether
the source is alive. So any limit below the source's legitimate quiet interval declares a
valid reading stale. Each limit in the table was chosen per key, from a comment about how
fast the signal *usually* moves. Nothing in the tree records the quiet interval the limit
has to clear.

Reproduced at `2c3272eb7`:

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-staleness/probe.py CONF_POWER_ENTITY`
  prints `limit=30.0 held 31 min -> problem=stale FAIL`, rc=1.
- `dev/audit/rounds/round10/D14/sweep-N-staleness/enumerate.py` reports
  `RESULT seams=29 flagged=20` in 0.27 s. With `--controls` it reports
  `RESULT controls_ok=True`: the positive control re-finds D14-s3-02, the clean fixture
  flags 0, and one perturbed line flags 1.
- The judge row for D14-s3-02 reads *"power 39 stale of 48 cycles, 78 newly-unavailable
  entity-cycles; mode 47; polling 0"*. Its unbounded-max-age arm gives 0 and 0.

### Class search

The R10 sweep (`dev/audit/rounds/round10/sweep-N-staleness.md`) gave every flagged seam a
disposition. 7 are instances: power and mode (the finding), plus energy, supply temperature,
return temperature, flow meter and `HUMIDITY_MAX_AGE_MINUTES`. 10 are guarded: the six pump
signals demote to silence, and the four free-heat probes fail safe. Solar radiation is
guarded by the Open-Meteo fallback. PV production is not applicable, because no read site
applies its limit (that missing check is class P6).

When each instance seam arrived (first commit by `git log -S`):

| seam | first commit | relative to `v4.0.0` (2026-08-26) |
|---|---|---|
| power, energy | `df7db8215` 2026-08-22 | before |
| humidity | `8e7656d1e` 2026-08-26 | same day |
| mode | `64a54195b` 2026-08-28 | after |
| supply, return | `9f525ccc2` 2026-09-16 (#1067) | after |
| flow meter | `5ea502bc8` 2026-10-07 (R9-UX-9) | after |

### Process state: (c) followed and did not produce the intended result

The round-9 sweep ran and gave the R10 instances a disposition. It did so by reading
comments, not by running a probe. In round 9, class S6
(its `SWEEP.md` and `enumerate.sh`, committed in `6b65c9c4a` under the round-9 D14 sweep
directory `staleness-limit-shorter-than-quiet-interval`) did the following:

- It marked energy and mode **"not applicable"**, because *"each carries its own
  deliberate, generous-horizon justification in `const.py`'s comments"*.
- It marked power, supply and return **"not applicable"**, because *"`const.py`'s comments
  justify these limits as fast-moving signals"*.
- It proposed no barrier, at *"N=1"*.

Its enumerator was `grep` over the limit table plus the finder's indoor harness. That
harness can probe only the indoor key, so no seam other than indoor was ever driven. The
round-9 fix (F4.1, #1718, `3e9f1878b`) then did what its brief asked. It raised the five
slow-store temperatures to `QUIET_STORE_MAX_AGE_MINUTES = 360` and wrote the class's whole
argument into a `const.py` comment: *"its age measures how still the room is, not whether
the probe is alive"*. That argument was never applied to the other keys, because the sweep
had already filed them as out of class.

The step (D14 step 4, a disposition for every seam) was obeyed. Its unit was wrong: a
comment about the usual change rate stood in for the quiet interval. Two of the R10
instances (mode, energy) were in the round-9 sweep's own table and marked "not
applicable". This is not (b), because the step was carried out. It is not (a), because a
sweep existed and listed the seams.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per release.

- **Standing cost.** The static check is the R10 enumerator with its `QUIET` table moved
  into `const.py`. It runs in 0.27 s (measured above). Releases from `v6.7.1` to `v7.0.0`
  merged 314 PRs in 17 intervals, about 18.5 PRs per release
  (`git log --merges --first-parent v6.7.1..v7.0.0`). Charging one run to every PR, the
  upper bound is 0.27 x 18.5 = 5 s per release.
- **P(recurrence).** 4 instance seams (mode, supply, return, flow) arrived after `v4.0.0`,
  across 122 release intervals to `v7.0.0`. That is 0.033 per release.
- **cost(defect).** The lower bound is the round-9 fix PR for this class's first instance.
  #1718 ran 21.75 h from its first commit (2026-09-26T18:14Z) to the merge
  (`fab176199`, 2026-09-27T15:59Z) and carried 5 findings, so 4.35 h per finding. That
  excludes finder, verify, judge and sweep seats. Field impact: measured_power and
  compressor_starts are unavailable on 39 of 48 cycles.
- **Verdict.** 4/122 x 4.35 h = 0.143 h = 513 s per release, against 5 s. The barrier
  passes by two orders of magnitude.

### Countermeasure (a class barrier, proposed; not built by this seat)

It addresses (c): the disposition must rest on a declared quantity that a check can
compare, not on a comment.

1. Declare the quiet interval next to the limit. Add `INPUT_QUIET_MINUTES` in `const.py`,
   keyed exactly like `INPUT_MAX_AGE_MINUTES`, with `inf` for a value that can hold
   indefinitely. This takes the R10 enumerator's `QUIET` table out of the harness, where it
   was the judgement input.
2. Add a static `tests/` arm that refuses three things:
   - a key whose limit is below its quiet interval, unless it is on a reasoned
     guarded-by-design list (pump-signal silence demotion, the fail-safe free-heat probes);
   - a key missing from the quiet table;
   - a list entry that names no key.

   The arm must show:
   - red on this tree: the 7 instance seams are flagged;
   - green once they are fixed;
   - null control: the R10 clean fixture flags 0;
   - non-vacuity: the number of seams read equals `len(INPUT_MAX_AGE_MINUTES)` plus the
     module `*_MAX_AGE_MINUTES` constants.
3. The class's fix PR owns the demonstration and the budget check. For power and mode, the
   D14-s3 replay `on_change` arm is the dynamic complement, as the sweep proposed.

## Needs tvofi

No policy change is proposed. If the fix PR finds that the `const.py` table costs a
structure-budget raise, that raise is tvofi's decision, asked before the push.
