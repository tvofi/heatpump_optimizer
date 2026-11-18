# Proposal triage, session s6, batch 31 (P176-P183)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch30.md` (P168-P175). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). It rules the last eight of the V79-V103 ideas, the quality series. Each extends an instrument the tree already has, and none saves round-10 closure time. Starting new quality gates mid-round would also add reds to every open head. So each is DEFER, naming the round-11 audit dimension that owns its measurement. Facts read at origin/main dfcd8d9be.

Round-1 re-cut (verdict 6402374814, 2026-10-25): every entry is DEFER, with an `Instances:` line and the round-11 dimension that owns its measurement (P176: D11). The owner's acceptance of these ideas can reach R10-ROUND-PLAYBOOK as an owner-sourced carry citing tvofi; P183's carry is dropped.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P176: a versioned review rubric (S6-V94)
Verdict: DEFER -> D11 (governance mechanisms) owns the measurement in round 11: the count of round-10 blocked verdicts whose reason a fixer could have pre-checked against a numbered rubric item, by verdict id. No rubric renumbering in round 10: it would invalidate the citations in open verdicts. (Round-1 re-cut, verdict 6402374814: an unmeasured benefit is DEFER, never ACCEPT.)
- The rubric exists: `fix-review.md` is the reviewer's contract, and its block verdicts are already coded by class (`blocked <sha> mutation-vacuous` at line 12, `class-open` at 28, `carry-missing` at 46, `head-moved` at 88, `architecture-unsound` at 134), which a fixer can pre-check today.
- Missing: a stable item id per rule that findings cite, and a version a brief pins.
- The edit is to a capped policy file with zero headroom (R10-ORCH-REVIEW-PACKET carry 0).

Source: s6 `proposals.md` `## V94` (orchestrator, 2026-10-25, tvofi-accepted F10).
Instances: none measured. The block classes already coded in `fix-review.md` (lines 12, 28, 46, 88, 134) are the population a count would read.
Cost: S in policy, plus `brief_lint.mjs` resolving rubric ids.
Binding: renumbering the contract mid-round would invalidate the citations in open verdicts. Closure saving: 0 h in round 10.

## P177: property-based tests for optimizer invariants (S6-V95)
Verdict: DEFER -> D2/D3 own the measurement in round 11: the count of round-10 optimizer defects that a stated property (energy balance, monotone cost under price scaling, setpoint bounds, no heating outside the plan) would have caught, by issue or PR. (Round-1 re-cut, verdict 6402374814: an unmeasured benefit is DEFER, never ACCEPT.)
Source: s6 `proposals.md` `## V95` (orchestrator, 2026-10-25, tvofi-accepted Q1).
Instances: none measured. No test under `tests/` imports a property-testing library (`git grep -l hypothesis -- 'tests/*.py'` prints nothing).
Cost: M (a new dependency for the CI requirements, and one property per invariant with its null control).
Binding: a new suite added mid-round is a new red class for every open head. Closure saving: 0 h in round 10.

## P178: differential testing against an exact oracle (S6-V96)
Verdict: DEFER -> D0 owns the measurement in round 11: the cost gap between the optimizer and an exact LP or brute-force solution on small horizons, sampled once offline, against the BLAS-noise headroom `tests/optimality.py` already allows. (Round-1 re-cut, verdict 6402374814: an unmeasured benefit is DEFER, never ACCEPT.)
Source: s6 `proposals.md` `## V96` (orchestrator, 2026-10-25, tvofi-accepted Q2).
Instances: none measured. `tests/optimality.py`'s docstring states it is "Not an optimality proof".
Cost: M plus a design step.
Binding: D0's own instrument; a design must state what counts as a gap. Closure saving: 0 h in round 10.

## P179: a per-module mutation-score ratchet (S6-V98)
Verdict: DEFER -> D3 owns the measurement in round 11: per-module survivor rates from the mutation ledger (`tests/mutation_ledger/`) over a full round, which a floor would be recorded from. (Round-1 re-cut, verdict 6402374814: an unmeasured benefit is DEFER, never ACCEPT.)
Source: s6 `proposals.md` `## V98` (orchestrator, 2026-10-25, tvofi-accepted Q5).
Instances: none measured. `tests/mutation_budgets.json` holds one sampled cap (`max_survivor_fraction`) and no per-module figure.
Cost: S (a per-module table from the mutation ledger, plus the ratchet check).
Binding: it needs a full-round measurement to record honest floors. Closure saving: 0 h in round 10.

## P180: Home Assistant contract tests across versions (S6-V99)
Verdict: DEFER -> D10 owns the measurement in round 11: the count of defects that reached a release because an entity or state schema changed against the latest or dev HA release, by issue. (Round-1 re-cut, verdict 6402374814: an unmeasured benefit is DEFER, never ACCEPT.)
- `tests/ha_contract.py`: what the stub owes Home Assistant, measured against both;
- `tests/ha_floor.py`: every HA name production reaches, against the floor release `hacs.json` declares;
- `tests/nightly_ha.py`: real Home Assistant in its container.

What is new: entity and state schema snapshots, run against the latest and dev releases as well as the floor.
Source: s6 `proposals.md` `## V99` (orchestrator, 2026-10-25, tvofi-accepted Q6).
Instances: none measured. The floor, stub and real-container instruments exist (`tests/ha_floor.py`, `tests/ha_contract.py`, `tests/nightly_ha.py`).
Cost: M (snapshots, plus a nightly matrix over three HA versions).
Binding: an extension of D10's instruments, which the round-11 audit sizes. Closure saving: 0 h in round 10.

## P181: a deterministic full-year simulation gate (S6-V100)
Verdict: DEFER -> D2/D0 own the measurement in round 11: the seasonal KPI drift a year simulation would detect that `tests/stress.py`, `tests/backtest.py` and `tests/golden.py` do not, priced against the claim-file rules (CLAUDE.md rule 3). (Round-1 re-cut, verdict 6402374814: an unmeasured benefit is DEFER, never ACCEPT.)
Source: s6 `proposals.md` `## V100` (orchestrator, 2026-10-25, tvofi-accepted Q7).
Instances: none measured.
Cost: L plus a design step.
Binding: it touches the claim-file rules (`claim-files.md`), so it must be designed before any build. Closure saving: 0 h in round 10.

## P182: units as types, and a strict-typing ratchet (S6-V101)
Verdict: DEFER -> D2/D7 own the measurement in round 11: the count of kW/kWh unit-confusion defects in rounds 1-10, by issue. The strict-typing ratchet already exists (`tests/typing_ruler.py`). (Round-1 re-cut, verdict 6402374814: an unmeasured benefit is DEFER, never ACCEPT.)
Source: s6 `proposals.md` `## V101` (orchestrator, 2026-10-25, tvofi-accepted Q8).
Instances: none measured. `tests/typing_ruler.py` ratchets `mypy --strict` errors, errors per code and type-ignores held at 0 (its docstring).
Cost: M (NewType-style units across the thermal and price modules, under the existing ruler).
Binding: a typed-units pass touches most production modules and would collide with every open production group. Closure saving: 0 h in round 10.

## P183: escaped-defect metrics per stamp (S6-V103)
Verdict: DEFER -> D13/D14 own the measurement in round 11: post-release defects and time-to-detect per stamp, by issue citing a released version. `defect-root-cause.md:18` already owes each such defect a root cause. (Round-1 re-cut, verdict 6402374814: an unmeasured benefit is DEFER, never ACCEPT.)
- A defect that reached a released version already owes a root cause (`defect-root-cause.md:18`).
- D14 hunts recurring bug classes.
- What is new is a per-stamp count of post-release defects with time-to-detect, which feeds D14's classes.

Source: s6 `proposals.md` `## V103` (orchestrator, 2026-10-25, tvofi-accepted Q10).
Instances: none measured.
Cost: S (an enumerator over issues that cite a released version, keyed to `tools/release/stamp.py`'s tags).
Binding: a measurement that pays at round 11's audit. Closure saving: 0 h in round 10.

