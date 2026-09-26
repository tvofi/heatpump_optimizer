# Class sweep — P4: "The optimizer seed set or stop tolerance does not bracket the optimum"

Ledger: `tools/audit/bugclasses.json`#P4, status `open`, 7 historical rounds, 14 instances
(R1-R7), detector never recorded — the most-recurring class in the ledger.

Round-9 finding: **D0-s2-02** (verified, low — the call-0 `ladder` gap on the 24 h grid, 4
`summer_warm` cells excluded, is 1.2012 % max / 0.3909 % mean on `shoulder` prices against a
0.3247 % max / 0.0918 % mean `flat`-price null control; 8 of 16 shoulder cells exceed 0.1 %, none
claimed in `tests/optimality.py`'s `_CERT_CLAIMS`). D0-s2-01 (the ftol=1e-12 stop-tolerance
finding, same class) was **refuted** by the judge (excluded per `CLASSES-DRAFT.json`'s `_note`)
and is not counted here.

## Enumerator

Heavy solver races are **not re-run**: `race.py`'s grid (80/64/32 cells per horizon) is the same
cost class as the D3 mutation pools tvofi asked to minimise, and this is a small (N=1) class per
the sweep brief. `tools/audit/round9/D14/sweep/P4/enumerate.sh` gives the structural half of the
seam rule — every production call site that assembles a seed set and hands it to
`_multi_start_minimize` — and this SWEEP.md reuses the finder's own `REPORT.md` grid (already
executed, already judged) as the positive control and disposition evidence instead of
re-executing it.

Positive control: the finder's `REPORT.md` table (quoted above) is the executed number; re-derive
it with `PYTHONPATH=tests/hastub python3 tools/audit/round9/D0/s2/race.py --cells shoulder,flat
--horizon 24 --perturb none` if a from-scratch re-run is ever wanted (expensive: full grid, BLAS
solver, see the harness header for machine/thread pinning).
Null control: the `flat` price profile, already in the finding's own table (0.3247 % max vs.
1.2012 % on `shoulder`).
Perturbation: `--perturb add_emax_ladder` (documented in the harness) widens the seed ladder and
must move the gap toward 0 — this is the judge's perturbation for the family, not re-run here.

## Disposition

| seam | disposition | note |
|---|---|---|
| `optimizer.py:3484` `_multi_start_minimize` call (with-DHW path, seeds include `headroom*0.5` and a `_price_ranked_start` low-energy anchor) | **instance** | Covered by D0-s2-02's grid, which includes `dhw` cells (`one\|dhw\|shoulder\|shoulder`: 1.17 %). |
| `optimizer.py:4019` `_multi_start_minimize` call (no-DHW / two-zone path, seeds include the deep low-energy anchor and `h.extra_starts`) | **instance** | Covered by D0-s2-02's grid, which includes `nodhw` cells (`one\|nodhw\|shoulder\|shoulder`: 1.20 %). |

Both production seams feed the same seed-construction pattern (a small fixed ladder of
price-ranked/energy-fraction anchors, no bracket-guaranteeing multi-start) into one shared
`_multi_start_minimize`, so they are one mechanism with two call sites, not two mechanisms.

## Count

N = 1 verified finding (D0-s2-02) + 0 additional sweep-confirmed instances (no new seed-assembly
call site beyond the finding's own two, both already in its grid). **rca = false** (N=1 < 3; the
class is `open` in the ledger but not `barriered`, so the historical 14 instances across rounds
1–7 do not themselves trigger RCA this round — only this round's own count does, per PLAN §7.5).

## Barrier proposal

Not proposed here at N=1: a barrier for a seed/stop-tolerance class this well-established (14
prior instances, `detector_idea` already recorded in the ledger: "Per fixture cell, production
multi-start against a dense seed grid on the identical objective") is a P4-class RCA decision, not
a small-N sweep disposition — flagging it to the orchestrator as a candidate for an RCA seat
regardless of this round's N, given the ledger's own recurrence count, per
`defect-root-cause.md`'s recurring-class trigger.
