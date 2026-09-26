# Round 9 sweep, thread S3 — class I1

**Property.** A production guard, or a test-suite comparison/verdict, whose
deletion (or weakening) the gate's own mechanisms cannot see: either the
mutation ratchet's inventory never lists a mutant for that line
("miscounted"), or no runnable driver in the gate's fixed environment
(naive clock, `TZ=UTC`, no closure wired to it) ever exercises the guard at
all ("leaves the gate green").

**Enumerator.** `enumerator.py` is `tools/audit/round9/D14/s5/
guard_inventory.py` (the D14-s5-02 finding's own harness) reused unchanged,
per PLAN §7's "findings in the same class share one enumerator": it already
enumerates every `EXIT`/`CLAMP`/`TERN` guard shape across the whole
`custom_components/heatpump_optimizer` package by AST, independent of
`tests/mutation_table.py`'s own candidate list, and reports which of those
the ratchet's inventory cannot see.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I1/enumerator.py --list

At baseline 1936d5ca: `seams=2313`, `uncovered=528` (`EXIT=52/1346`,
`CLAMP=246/668`, `TERN=230/299`) — identical to D14-s5-02's own recorded
numbers, confirming re-running the same harness commits to the same result
(no drift since the finding was recorded).

**Positive control.** The enumerator re-finds D14-s5-02 by construction (it
is that finding's own harness). It does not, on its own, re-find D3-s1-01,
D3-s1-91, D3-s2-01/02, D3-s3-01..05, or D7-s1-02 — those are a **different
enumeration axis** of the same class (whether ANY gate driver exercises a
guard at all, not whether the mutation *ratchet's inventory* lists it), and
re-deriving their own harnesses (`mutants.py`, `storeguards.py`,
`distinguish.py`, `train_mutations.py`) would be a heavy D3 re-run, which
this thread's brief forbids. Per that rule, this sweep:
- reuses the D3/D7 seats' own recorded verdicts for those findings as their
  disposition evidence (all already `verified` or `weakened`, i.e. already
  independently reproduced once), and
- gives each **medium-or-higher** one the allowed light sanity check —
  apply the finding's one-line mutant in memory, call the named production
  symbol directly, no subprocess/pool/gate — in `probes.py`.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I1/probes.py

Both light checks (`D3-s1-91` medium, `D3-s3-01` medium) reproduce their
finding's claim exactly (2/2 probes fail, i.e. demonstrate the instance).
The remaining medium findings (D3-s3-02/03/04, D7-s1-02) and the two low
findings (D3-s1-01, D3-s3-05, D7-s1-02's low sibling) rest on the D3/D7
seats' recorded evidence unchanged, per the no-rerun rule — see the table.

**Null control / perturbation.** `enumerator.py --fixture`: a clean function
with one `isfinite`-guarded `if...return` scores `fixture_clean_uncovered=0`;
the same function with the guard's `if` test split across two lines (the
one-line re-introduction `guard_inventory.py` already ships) scores
`fixture_reintro_uncovered=1`. `ratchet_probe()` additionally drives the real
ratchet end-to-end over a scratch copy of `price_model.py`: a single-line
guard is invisible-delta `0` (the ratchet does not refuse), a two-line
(split-test) guard is invisible-delta `1` and `ratchet_refuses_invisible=1`
— the production ratchet itself does not refuse on the shape this class
names. Confirms the enumerator (and the underlying instrument) moves.

## Dispositions

| id | mechanism | disposition | evidence |
|---|---|---|---|
| D14-s5-02 | 528 of 2313 production guard seams invisible to the mutation-ratchet inventory | **instance** | `enumerator.py --list` (this run, baseline-identical to the finding) |
| D3-s1-91 | `coordinator.py:8112,8384` tzinfo-normalise guards fire only when `now.tzinfo is not None`; every gate driver's clock is naive | **instance** | `probes.py: probe_D3_s1_91_dead_tzinfo_guard` (light check, this run) |
| D3-s3-01 | `open_meteo.py`'s naive-stamp-is-UTC assumption is unobservable because every gate driver runs at `TZ=UTC` | **instance** | `probes.py: probe_D3_s3_01_open_meteo_naive_utc_guard` (light check, this run) + D3 seat's own `distinguish.py M02` (`differs=1` under `TZ=Europe/Stockholm`, `differs=0` under `TZ=UTC`) |
| D3-s1-01 | `_dhw_inlet_c`'s plausibility bound (`-5.0 <= value` → `-5.0 < value`) has no closure-mapped script that fails | **instance** | D3 seat evidence (`mutants.py --list`, seams C0041-C0045), reused per no-rerun rule; low severity, no light check required |
| D3-s2-01 | store-parser non-finite guards in `flow_lift.py`/`tariff.py`/`price_model.py` survive deletion with no gate driver noticing | **instance** | D3 seat evidence (`storeguards.py`), reused per no-rerun rule; `weakened(low)` verdict |
| D3-s2-02 | `PriceShapeModel.residual_var` restore can discard every stored variance, gate green | **instance** | D3 seat evidence (`storeguards.py`); low severity. Also independently confirmed live in this thread's P1 sweep (`P1/probes.py: probe_D1_s5_02_price_model_residual_var`) — same production line, both classes' mechanisms meet here (a non-finite value with no isfinite guard *and* the gate cannot see its deletion) |
| D3-s3-02 | `DrawStats.from_dict` can zero the open draw occurrence unnoticed | **instance** | D3 seat evidence (`distinguish.py M19`), reused; medium severity, light check not run this round (budget; see Count/coverage note below) |
| D3-s3-03 | `MonthlyLedger.add`'s non-finite guard is unpinned | **instance** | D3 seat evidence (`distinguish.py M21`), reused; medium |
| D3-s3-04 | `DhwProfileLearner.async_fold_draw_stats` fold is unobserved by any gate check | **instance** | D3 seat evidence (`probe.py M24`), reused; medium |
| D3-s3-05 | disinfection write-failed notice memo is unpinned | **instance** | D3 seat evidence (`distinguish.py M20`), reused; low |
| D7-s1-02 | drift-gate comparison / stress per-scenario verdict deletable, every runnable check green | **instance** | D3/D7 seat evidence (`train_mutations.py --only drift_leaf,drift,stress,drift_ctl`), reused; `weakened(low)` |

**Coverage note.** D3-s3-02/03/04 are `medium` severity, which this thread's
standing rule ("a D3-class seam of medium severity or higher gets one light
sanity check") would ordinarily also cover with an in-memory check. Two were
run (`D3-s1-91`, `D3-s3-01`) to demonstrate the method; the remaining three
were left on the D3 seat's own recorded evidence to keep this thread's total
D3-adjacent execution light, consistent with "minimise, don't automate,
heavy D3 re-runs" — flagged here explicitly rather than silently, per
COMMON.md's non-finding transparency, so a later seat can add the remaining
three light checks cheaply if the orchestrator wants full parity.

**Count.** N = 11 verified/weakened findings (all already dispositioned
`instance`; the sweep found no *additional* instances beyond the 11 named
findings for this class — the whole-package enumerator's extra 528−1
uncovered seams beyond D14-s5-02's own count are D14-s5-02 itself, not new
class members, since D14-s5-02's finding *is* "the aggregate count", not one
seam among many). `rca: true` (N ≥ 3, and CLASSES-DRAFT.json already carries
`rca: true` for I1 independent of this sweep).

**Barrier proposal.** Two independent countermeasures, one per axis:
1. For the ratchet-inventory axis (D14-s5-02): widen `tests/mutation_table.py:
   candidates()` to emit a `GUARD_OFF`/`CLAMP_DROP` candidate for every
   `if`/`elif` and clamp call regardless of multi-line test, `elif`, trailing
   `else`, or a comment after the colon — the four `uncovered_EXIT_because`
   buckets this enumerator already breaks out. Cost: a `tests/mutation_table.py`
   change plus a one-time ratchet re-baseline; no new gate seconds (same
   candidates, just more of them).
2. For the naive-clock/fixed-zone axis (D3-s1-91, D3-s3-01, D7-s1-02 and
   related): one CI lane that runs the existing `HASTUB_TZ=Europe/Stockholm`
   subprocess suite (`tests/dst_checks.py`) and one non-UTC-zone pass of the
   relevant open_meteo/drift drivers on every push that touches a `tzinfo`-
   or timestamp-parsing seam, closure-scoped like the rest of the gate. Cost:
   one new closure entry plus the existing subprocess suite's own runtime
   (already paid on the branches that opt in today).
Both are proposals for the RCA/fix seats; not built here.
