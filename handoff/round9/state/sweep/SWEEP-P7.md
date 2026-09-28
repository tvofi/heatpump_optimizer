# Sweep: P7 — "Naive wall-clock datetime arithmetic across a DST transition"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Ledger class (`P7`,
`tools/audit/bugclasses.json`): rounds 2, 3, 5; 4 prior instances (R2 D2-03,
R3 D1-03, R3 D2-02, R5 D1-08); status `open`, detector null, barrier null.
This round's finding: D14-s4-01 (verified, high).

## Enumerator

Reused verbatim from the D14-s4 finder seat (`handoff/audit-r9-evidence`,
`tools/audit/round9/D14/s4/p7_dst_seams.py` + `dst_fixture.py`), which already
does exactly what D14.md steps 3-4 ask: it traces every `homeassistant.util.dt`
call the real coordinator cycle makes across a synthetic spring/autumn DST
transition day and flags every production site where the resulting duration
disagrees with the UTC truth. Copied into this sweep dir with one path-depth
fix (`HERE.parents[4]` -> `parents[5]`, since this wrapper sits one directory
deeper than the original `D14/s4/`); no logic changed.

```
$ PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P7/p7_dst_seams.py
RESULT spring2027_wrong_sites=8 count
RESULT autumn2027_wrong_sites=9 count
RESULT wrong_sites=9 count
```

Reproduces the finding's own number (`wrong_sites=9`) exactly.

## Positive control

Re-finds D14-s4-01 (9 wrong sites, union over the two transition days). The
ledger's pre-fix historical instances (R2 D2-03, R3 D1-03/D2-02, R5 D1-08)
were already checked by the finder seat at their pre-fix commits
(`8454c07d`, `33cedffa`, `c7e2f817`; see `D14/s4/REPORT.md` non-findings:
baseline `tariff` arm 9 without `window_factors` vs pre-#777's 12 including
it; baseline 9 without `defrost._elapsed`/`_update_current_state` vs
pre-#1299's 10 including both) — re-executing those git-archive exports is
not repeated here (no heavy re-runs; the evidence is committed and citable).

## Null control

```
$ PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P7/p7_dst_seams.py --day plain,plain_autumn
RESULT wrong_sites=0 count
```

## Perturbation

```
$ PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P7/p7_dst_seams.py --reintroduce
RESULT wrong_sites=10 count
```

Moves 9 -> 10 under the one-line re-introduction (`coordinator._utc_age_seconds`
made to subtract raw datetimes, #1299's shape), the expected direction.

## Baseline vs main

`git diff 1936d5ca..origin/main -- custom_components/heatpump_optimizer/coordinator.py`
touches only `async_reset_comfort_weight` (unrelated to any DST seam);
`accuracy.py`, `dhw_learning.py`, `external_heat.py`, `tariff.py` are
byte-identical between baseline and `origin/main`. All 9 seams still exist
on `origin/main`.

## Disposition — every returned seam (from the enumerator's own per-site table)

| seam | disposition |
|---|---|
| coordinator.py:6207 `_forecast_arrays` step_offset | instance (high: grid up to 60 min off, 42/48 cycles per transition day) |
| accuracy.py:182 `score_lead_predictions` | instance |
| coordinator.py:9405 `_file_dhw_lead_predictions` | instance |
| coordinator.py:9445 `_file_lead_predictions` | instance |
| coordinator.py:9205 `_record_accuracy` elapsed | instance |
| dhw_learning.py:347 `DhwProfileLearner.async_learn_dynamics` | instance |
| external_heat.py:206 `ExternalHeatDetector._rate` | instance |
| coordinator.py:4684 `_next_optimization` | instance |
| tariff.py:58 `_window_slot` | not applicable — a wall-clock label by definition (the finder's own disposition, re-confirmed: `crossing=492 wrong=492` counts label recomputation, not a duration error) |
| coordinator.py:3169 `close` | guarded — `hits=67 crossing=0 wrong=0`: reached but never crosses a transition boundary in this fixture |

7 instance sites (excluding the one not-applicable and one guarded of the 9
`sites_reached`; the finder's REPORT.md's own count of "9" already nets out
the not-applicable site, i.e. 8 instances + 1 n/a = 9 "wrong" union, and
`close` sits outside the 9 at `wrong=0`).

## Count

N = 1 verified finding (D14-s4-01) + 0 additional sweep-confirmed instances
(the enumerator re-finds the same seams the finder already enumerated
exhaustively; no seam beyond the finder's own list turned up) = **1**.
However this is a ledger class with 4 prior-round instances and status
`open`/barrier `null` — **not** `barriered`, so the "any instance of a
barriered class" trigger does not apply, and per round N=1 keeps
**rca: false**, matching the brief. Recorded for the orchestrator: P7 has
now recurred in 4 of 6 rounds (2, 3, 5, 9) with no barrier ever built: a
plain re-derivation from `defect-root-cause.md`'s per-round rule says
`rca: false` this round, but the cross-round recurrence is worth a look by
whoever owns the ledger's cumulative view, since `defect-root-cause.md`'s
gate is stated as one-round-at-a-time and this class keeps clearing it by
one round's count alone.

## Barrier proposal

The finder's own: a `tests/` lane running the DST tracer over the two
replay days (11.0 s wall, provisional), failing on any wrong site outside
the not-applicable list; extend `tests/dst_checks.py` with a post-transition
clock (10:00). Not built here (N < 3 this round).

## Gate seconds

~40.6s wall per DST-day arm (provisional, this box); ~10s for the plain-day
null control. Two arms run for this sweep: ~91s total.
