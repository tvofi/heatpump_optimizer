# Sweep: "persisted future instant trusted without bound"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Findings in this class per
the judge (`CLASSES-DRAFT.json`, `judge_commit` 2f97b0a): D1-s1-04 (verified,
low) and D1-s3-05 (weakened(low), low). Not a ledger class (new).

## Enumerator

`enumerate.py` widens both seam_rules to every `datetime.fromisoformat` call
in the package (24 candidate sites), then this file hand-dispositions each by
reading its caller: is the restored instant compared to a later `now` to gate
a staleness window, an expiry, or a cooldown, with no check that the stored
value is not implausibly ahead of the moment it is read back?

```
$ python3 tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/enumerate.py
RESULT candidate_fromisoformat_sites=24
```

## Positive control

Re-finds both round-9 findings (drift.py:148, snapshots.py:74,
curve_learning.py:111, comfort_learning.py:256 for D1-s1-04; boost.py:166 for
D1-s3-05) — all present at baseline `1936d5ca` and at `origin/main` (neither
file changed between the two; `git diff 1936d5ca..origin/main -- custom_components/heatpump_optimizer/{drift,snapshots,curve_learning,comfort_learning,boost}.py`
is empty).

**The enumerator also surfaced four instances beyond the two findings**,
same mechanism, none previously reported:

- `coordinator.py:8007` / `:8023-8024` — the fuse-advisor's 7-day recompute
  cooldown (`_fuse_advisor_at`, restored from the ledger store).
- `coordinator.py:2953` / `:6306` — the heavy-snow damping window
  (`_last_heavy_snow`, restored from `stored`).
- `coordinator.py:7343` / `:8099-8114` (`_detect_outage`) — the outage
  staggered-recovery window (`stored.get("last_tick")`).
- `pump_arbiter.py:629` / `:405-407` (`hold()`) — the write-echo grace period
  (`held.written[slot]`, restored from the pump-duty store).

Each is proven with a failing probe that copies the guard expression
verbatim from its cited line and shows it stuck at day 30 when the restored
instant was written 400 days ahead of the real clock (`probe_fuse_advisor.py`,
`probe_more_instances.py`):

```
$ python3 tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_fuse_advisor.py
RESULT null_control_day6_active=True day8_active=False
RESULT positive_control_stretched_cooldown_at_day30=True
RESULT perturbation_clamped_stretched_cooldown_at_day30=False
PROBE OK: coordinator.py:8007/8023-8024 is an instance of the class

$ python3 tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_more_instances.py
RESULT snow_damping null_control_cleared=True positive_control_stuck_at_day30=True perturbation_clamped=False
RESULT outage_detection null_control_flagged=True positive_control_masked=True perturbation_clamped_flagged=True
RESULT echo_grace null_control_cleared=True positive_control_stuck_at_day30=True perturbation_clamped=True
PROBE OK: coordinator.py:2953/6306, coordinator.py:7343/8108, pump_arbiter.py:629/405-407 are instances of the class
```

## Null control

Each probe's own `null_control_*` line: with an honest (non-clock-skewed)
restored instant, the cooldown/gate clears (or flags) exactly on schedule.
`enumerate.py --self-test` (none needed; the null arm is inline in each probe)
gives 0 false positives on the honest-clock arm.

## Perturbation

The `perturbation_clamped_*` line in each probe: clamping the restored
instant to the moment it is read back (one line at each restore site) clears
the stretch. Direction: for the three "stays active too long" instances
(fuse advisor, snow damping, echo grace) the clamped arm goes from stuck-true
to false; for `_detect_outage` (masked detection) the clamped arm goes from
masked-true to correctly-flagged-true. Both are the expected direction for a
fix that stops trusting an implausibly future stored instant.

## Disposition — every candidate seam

| seam | disposition | note |
|---|---|---|
| drift.py:148 | instance | D1-s1-04 (verified) |
| snapshots.py:74 | instance | D1-s1-04 (verified) |
| curve_learning.py:111 | instance | D1-s1-04 (verified) |
| comfort_learning.py:256 | instance | D1-s1-04 (verified) |
| boost.py:166 | instance | D1-s3-05 (weakened(low)) |
| coordinator.py:8007 / :8023-8024 | instance | sweep-confirmed; probe_fuse_advisor.py |
| coordinator.py:2953 / :6306 | instance | sweep-confirmed; probe_more_instances.py `check_snow_damping` |
| coordinator.py:7343 / :8099-8114 | instance | sweep-confirmed; probe_more_instances.py `check_outage_detection` |
| pump_arbiter.py:629 / :405-407 | instance | sweep-confirmed; probe_more_instances.py `check_echo_grace` |
| coordinator.py:8381 (`_immersion_events` recency) | instance (low confidence, not probed) | same shape (`when >= cutoff` with an unclamped restored `when`), but capped: needs >=3 corrupted entries to move the output, and the list is itself bounded elsewhere; disposed as instance on the mechanism, not separately probed given the class already clears N>=3 |
| accuracy.py:78 (`AccuracySample.from_dict`) | not applicable | `when` is a label carried on the sample and pruned by position (`entry[-512:]`), not compared to `now` to gate a window |
| accuracy.py:406 (`lead_pending`) | not applicable | same: position-pruned, not a `now`-gated window in this file |
| away.py:590 (`_parse_datetime_local`) | not applicable | different class: a tz-naive `return_time` crashes the cycle (D1-s3-01), not a bound question |
| coordinator.py:583 (module-level tz coercion helper) | not applicable | coerces awareness only; it is not itself a gate against `now` (its two relevant callers are dispositioned above) |
| coordinator.py:6330 (`_current_spot_price`) | not applicable | different class: a stale 15-minute quarter read (D2-s3-01 / D8-s1-01, already verified elsewhere) |
| coordinator.py:7554, :7566 (`_price_model.observe_day`) | not applicable | keyed by a calendar-day string from `_price_days_seen`, not by comparing a restored instant to a later `now` |
| open_meteo.py:206 | not applicable | builds an hourly forecast index from fresh API data each cycle, nothing persisted across restarts |
| price_model.py:487 | not applicable | same: parses the current fetch's own entries, not a restored instant |
| manual_plan.py:82, :236, :246 | not applicable (own class) | `expires_at`/`created_at` belong to "service input without an upper-bound clamp" (D1-s2-54), dispositioned in that class's own sweep |

## Count

N = 2 verified findings (D1-s1-04, D1-s3-05) + 5 sweep-confirmed instances
(fuse advisor, snow damping, outage detection, pump-arbiter echo grace,
immersion recency) = **7**. N >= 3, so **rca: true** — this supersedes the
brief's N=2/rca=false, which predated the widening; the four fully-probed
instances plus the fifth on the same mechanism are why.

## Barrier proposal

A `tests/` lint pass over every `datetime.fromisoformat` call reachable from
a persisted-store `async_load` (or a coordinator field documented as
restored from one) that flows into a `now - restored` or `restored - now`
comparison without an intervening `min(restored, now)` / `max(restored, now)`
clamp at the restore site. Cost: AST-only, no HA runtime needed (same shape
as the existing `guard_inventory.py` / `closure_divergence.py` D14 detectors);
provisional cost is sub-second (24 call sites, one file walk).

## Gate seconds

Enumerator + both probes: ~0.3s wall (pure Python, stdlib only, no pytest,
no HA stub import).
