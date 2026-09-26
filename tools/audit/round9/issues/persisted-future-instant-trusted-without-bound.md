# [R9-PERSISTED-FUTURE-INSTANT-TRUSTED-WITHOUT-BOUND] persisted future instant trusted without bound

**Class `persisted-future-instant-trusted-without-bound`.** persisted future instant trusted without bound. The mechanism the sweep confirms across 7 instances: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 7 (2 judge-verified findings + 5 sweep-confirmed instances).

RCA: owed.

> Note: the judge's class table (`CLASSES-DRAFT.json`) recorded n=2, rca=False for this class; the class sweep (`S7.json`), run after the judge and enumerating every sibling seam, found N=7, rca=True. The sweep count is the one this issue uses, being the later, complete enumeration.

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s1-04 | `custom_components/heatpump_optimizer/drift.py` | low | A timestamp stored while the clock ran ahead is trusted verbatim and stretches stale timeouts by the clock error |
| D1-s3-05 | `custom_components/heatpump_optimizer/boost.py` | low | Boost 'two-hour maximum' is an absolute instant: a clock step back or a far-future store extends it without bound |
| sweep | `custom_components/heatpump_optimizer/coordinator.py:8007,8023-8024` | (unrated) | sweep-confirmed: fuse-advisor 7-day recompute cooldown |
| sweep | `custom_components/heatpump_optimizer/coordinator.py:2953,6306` | (unrated) | sweep-confirmed: heavy-snow damping window |
| sweep | `custom_components/heatpump_optimizer/coordinator.py:7343,8099-8114` | (unrated) | sweep-confirmed: outage staggered-recovery window |
| sweep | `custom_components/heatpump_optimizer/pump_arbiter.py:629,405-407` | (unrated) | sweep-confirmed: write-echo grace period |
| sweep | `custom_components/heatpump_optimizer/coordinator.py:8381` | (unrated) | immersion-event recency count; same shape, capped by needing >=3 corrupted entries, not separately probed |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D1-s1-04: also `custom_components/heatpump_optimizer/drift.py:148`, `custom_components/heatpump_optimizer/snapshots.py:74`, `custom_components/heatpump_optimizer/curve_learning.py:111`, `custom_components/heatpump_optimizer/comfort_learning.py:256`
- D1-s3-05: also `custom_components/heatpump_optimizer/boost.py:166`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/accuracy.py:78` — not applicable: position-pruned (entry[-512:]), not a now-gated window
- `custom_components/heatpump_optimizer/accuracy.py:406` — not applicable: position-pruned, not a now-gated window
- `custom_components/heatpump_optimizer/away.py:590` — not applicable: different class: tz-naive return_time crash (D1-s3-01)
- `custom_components/heatpump_optimizer/coordinator.py:583` — not applicable: shared tz-coercion helper, not itself a gate
- `custom_components/heatpump_optimizer/coordinator.py:6330` — not applicable: different class: stale 15-min quarter read (D2-s3-01/D8-s1-01)
- `custom_components/heatpump_optimizer/coordinator.py:7554,7566` — not applicable: keyed by calendar-day string, not a now-gated comparison
- `custom_components/heatpump_optimizer/open_meteo.py:206` — not applicable: fresh per-cycle fetch, nothing persisted
- `custom_components/heatpump_optimizer/price_model.py:487` — not applicable: fresh per-cycle fetch, nothing persisted
- `custom_components/heatpump_optimizer/manual_plan.py:82,236,246` — not applicable: belongs to 'service input without an upper-bound clamp' (D1-s2-54), its own class

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s1-04**: `grep -n "fromisoformat" custom_components/heatpump_optimizer/{drift,snapshots,curve_learning,comfort_learning}.py`
- **D1-s3-05**: `rg -n "until" custom_components/heatpump_optimizer/boost.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

AST lint over every fromisoformat call reachable from a persisted-store async_load that flows into a now-restored/restored-now comparison with no intervening min/max clamp at the restore site; sub-second cost

## Fix

Fix: see round-9 fix plan.

