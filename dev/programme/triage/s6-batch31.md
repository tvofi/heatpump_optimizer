# Proposal triage, session s6, batch 31 (P176-P183)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch30.md` (P168-P175). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). It rules the last eight of the V79-V103 ideas, the quality series. Each extends an instrument the tree already has, and none saves round-10 closure time. Starting new quality gates mid-round would also add reds to every open head. So each is a round-11 item, owned by the audit dimension that measures it, and recorded in R10-ROUND-PLAYBOOK (one carry, under P183). Facts read at origin/main dfcd8d9be.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P176: a versioned review rubric (S6-V94)
Verdict: ACCEPT -> round-11 policy design item.
- The rubric exists: `fix-review.md` is the reviewer's contract, and its block verdicts are already coded by class (`blocked <sha> mutation-vacuous` at line 12, `class-open` at 28, `carry-missing` at 46, `head-moved` at 88, `architecture-unsound` at 134), which a fixer can pre-check today.
- Missing: a stable item id per rule that findings cite, and a version a brief pins.
- The edit is to a capped policy file with zero headroom (R10-ORCH-REVIEW-PACKET carry 0).

Source: s6 `proposals.md` `## V94` (orchestrator, 2026-10-25, tvofi-accepted F10).
Cost: S in policy, plus `brief_lint.mjs` resolving rubric ids.
Binding: renumbering the contract mid-round would invalidate the citations in open verdicts. Closure saving: 0 h in round 10.

## P177: property-based tests for optimizer invariants (S6-V95)
Verdict: ACCEPT -> round-11 item under D2 (mathematical and physical sanity) and D3 (test-suite gaps). `tests/stress.py` already samples across houses, seasons, tariffs and feature combinations (its docstring), and `tests/optimality.py` asserts that the plan satisfies comfort. Neither states the filing's invariants as properties with shrinking: energy balance, monotone cost under price scaling, setpoint bounds, and no heating outside the plan. No test in `tests/` uses a property-testing library.
Source: s6 `proposals.md` `## V95` (orchestrator, 2026-10-25, tvofi-accepted Q1).
Cost: M (a new dependency for the CI requirements, and one property per invariant with its null control).
Binding: a new suite added mid-round is a new red class for every open head. Closure saving: 0 h in round 10.

## P178: differential testing against an exact oracle (S6-V96)
Verdict: ACCEPT -> round-11 design item under D0 (price optimality); the filing marks it "design seat". `tests/optimality.py` is explicitly "not an optimality proof". It is a floor against trivial challengers, priced on energy cost only, with headroom for BLAS-to-BLAS solver noise (its docstring). An LP or brute-force oracle on small horizons is new. Its gap tolerance must be designed against that same noise (CLAUDE.md rule 3).
Source: s6 `proposals.md` `## V96` (orchestrator, 2026-10-25, tvofi-accepted Q2).
Cost: M plus a design step.
Binding: D0's own instrument; a design must state what counts as a gap. Closure saving: 0 h in round 10.

## P179: a per-module mutation-score ratchet (S6-V98)
Verdict: ACCEPT -> round-11 item under D3. `tests/mutation_budgets.json` holds one sampled cap (`max_survivor_fraction`) plus the derived unpinned-site count ratchet (its `_comment`). Neither is per module. A per-module floor that may only rise fits the structural-ratchet rule (CLAUDE.md rule 2), and a first recording is a deliberate one with its reason.
Source: s6 `proposals.md` `## V98` (orchestrator, 2026-10-25, tvofi-accepted Q5).
Cost: S (a per-module table from the mutation ledger, plus the ratchet check).
Binding: it needs a full-round measurement to record honest floors. Closure saving: 0 h in round 10.

## P180: Home Assistant contract tests across versions (S6-V99)
Verdict: ACCEPT -> round-11 item under D10 (the Home Assistant quality scale). Three instruments exist:
- `tests/ha_contract.py`: what the stub owes Home Assistant, measured against both;
- `tests/ha_floor.py`: every HA name production reaches, against the floor release `hacs.json` declares;
- `tests/nightly_ha.py`: real Home Assistant in its container.

What is new: entity and state schema snapshots, run against the latest and dev releases as well as the floor.
Source: s6 `proposals.md` `## V99` (orchestrator, 2026-10-25, tvofi-accepted Q6).
Cost: M (snapshots, plus a nightly matrix over three HA versions).
Binding: an extension of D10's instruments, which the round-11 audit sizes. Closure saving: 0 h in round 10.

## P181: a deterministic full-year simulation gate (S6-V100)
Verdict: ACCEPT -> round-11 design item under D2 and D0; the filing marks it "design seat". `tests/stress.py`, `tests/backtest.py` and `tests/golden.py` each cover part of it. "BLAS-independent" collides with CLAUDE.md rule 3, which says solver floats do not reproduce across BLAS builds and golden values are claimed, not re-recorded. So the design must say which KPIs are tolerance-graded and how a claim works for them.
Source: s6 `proposals.md` `## V100` (orchestrator, 2026-10-25, tvofi-accepted Q7).
Cost: L plus a design step.
Binding: it touches the claim-file rules (`claim-files.md`), so it must be designed before any build. Closure saving: 0 h in round 10.

## P182: units as types, and a strict-typing ratchet (S6-V101)
Verdict: ACCEPT narrowed -> round-11 item under D2 and D7. The strict-typing ratchet exists: `tests/typing_ruler.py` ratchets three numbers under a pinned `mypy --strict`: total errors, errors per code, and type-ignores held at 0. Its budgets are in `tests/typing_budgets.json`, and the `typing` job runs it (`tests.yml:709`). What is new is distinct kW and kWh types.
Source: s6 `proposals.md` `## V101` (orchestrator, 2026-10-25, tvofi-accepted Q8).
Cost: M (NewType-style units across the thermal and price modules, under the existing ruler).
Binding: a typed-units pass touches most production modules and would collide with every open production group. Closure saving: 0 h in round 10.

## P183: escaped-defect metrics per stamp (S6-V103)
Verdict: ACCEPT -> round-11 item under D13 and D14.
- A defect that reached a released version already owes a root cause (`defect-root-cause.md:18`).
- D14 hunts recurring bug classes.
- What is new is a per-stamp count of post-release defects with time-to-detect, which feeds D14's classes.

Source: s6 `proposals.md` `## V103` (orchestrator, 2026-10-25, tvofi-accepted Q10).
Cost: S (an enumerator over issues that cite a released version, keyed to `tools/release/stamp.py`'s tags).
Binding: a measurement that pays at round 11's audit. Closure saving: 0 h in round 10.

Carry text (for `roster_edit.py append-carry R10-ROUND-PLAYBOOK`, citing `triage: dev/programme/triage/s6-batch31.md#P183`): "Round-11 quality backlog, batch 31 (tvofi-accepted, triage s6 batch 31 P176-P183), each owned by the dimension that measures it. (1) V94: a versioned review rubric, with item ids in `fix-review.md` that findings and briefs cite, resolved by `brief_lint.mjs`. (2) V95, under D2/D3: property-based tests for energy balance, monotone cost under price scaling, setpoint bounds and no heating outside the plan. (3) V96, under D0: an exact LP or brute-force oracle on small horizons beside `tests/optimality.py`, with a gap tolerance designed against BLAS noise; needs a designer. (4) V98, under D3: per-module mutation-score floors that may only rise, recorded from a full-round measurement. (5) V99, under D10: entity and state schema snapshots against the floor, latest and dev HA releases, extending `ha_contract.py`, `ha_floor.py` and `nightly_ha.py`. (6) V100, under D2/D0: a full-year simulation gate with tolerance-graded KPIs, reconciled with the claim-file rules; needs a designer. (7) V101, under D2/D7: kW and kWh unit types under the existing `typing_ruler.py` ratchet. (8) V103, under D13/D14: escaped defects and time-to-detect per stamp, feeding D14's classes. Each item states its round-11 owner seat."
