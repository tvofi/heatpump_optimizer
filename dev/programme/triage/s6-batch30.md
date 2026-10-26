# Proposal triage, session s6, batch 30 (P168-P175)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch29.md` (P158-P167). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). It rules eight of the V79-V103 ideas; none saves round-10 closure time, and after the round-1 re-cut each is DEFER, naming its measurement or its owner. Facts read at origin/main dfcd8d9be.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P168: fail-fast CI ordering (S6-V81)
Verdict: DEFER (ordering) -> D13 owns the measurement: per-script p(red) and runtime inside the serial tests job, from check-run history. The cancel-on-first-red arm is REJECTED on its binding cost: `## Red checks` must name every red, so a cancel shows one red per round and costs a review round per red to save runner minutes. (Round-1 re-cut, applying verdicts 6402369226 and 6402374814 on the sibling batches: an unmeasured benefit is DEFER, never ACCEPT.)
- The cancel half: `## Red checks` must name every red at the head (`prepr.sh:1417`, policy_lint's unnamed-red arm). Cancelling the remaining jobs at the first red would show one red per round, and a fixer would need a round per red. That costs whole review rounds to save runner minutes.
- The ordering half: the CI units run as parallel jobs (each unit job `needs: prelude` only, `ci.yml:169-241`; `gate` needs `prelude` and `pr-contract`, `ci.yml:301-302`), so job order does not change the wall time. Only the serial order of scripts inside a job could. The tests matrix already sets `fail-fast: true` where it applies (`tests.yml:197-203`).
- The measured long pole is CodeQL on batch proofs, which is ruled in P158 (R10-PROOF-CODEQL, an ACCEPT trial on #2829, not yet on main), not reordered.

Source: s6 `proposals.md` `## V81` (orchestrator, 2026-10-25, tvofi-accepted T4), with the orchestrator's CodeQL measurement (2026-10-25).
Instances: no per-script failure probability is recorded in the tree.
Cost: S to measure. The round-11 item is to order the scoped tests job's scripts by measured p(red) / runtime once check-run history supplies the numbers.
Binding: no saving without data, and a real harm in the cancel half. Closure saving: 0 h in round 10 (P158 carries the measured gain).

## P169: live reviewer pairing for large or critical-path groups (S6-V85)
Verdict: DEFER -> D13 owns the measurement: the share of round-10 blocked verdicts a shadow reviewer during implementation would have pre-empted, by verdict id, priced against a second reviewer seat per group and the independence `fix-review.md` requires. (Round-1 re-cut, applying verdicts 6402369226 and 6402374814 on the sibling batches: an unmeasured benefit is DEFER, never ACCEPT.)
- A reviewer who shadows the implementation is anchored on the fixer's approach. The fix reviewer's contract requires a fresh context, a frozen head, and the finder's harness, never the fixer's (`fix-review.md:3-4` for the fresh context and frozen head, step 2 at `fix-review.md:13-14` for the finder's harness, and CLAUDE.md's role table).
- Round 10 already places early adversarial judgement where it is cheapest for L and XL groups: the designer and design review (`designer.md`, `design-review.md`).
- A design must keep the verdicting reviewer independent of any shadow, for example a shadow seat that never posts the verdict.

Source: s6 `proposals.md` `## V85` (orchestrator, 2026-10-25, tvofi-accepted T9).
Instances: none measured. (The plan-opt study's mean of 2.26 rounds per fix PR is out of tree and not re-derived here; it is not used as a figure.)
Cost: M in policy (`fix-review.md`, `fixer.md`) plus a second reviewer seat per group.
Binding: independence is the reviewer's whole value, so a design must settle it before any build. Closure saving: 0 h in round 10.

## P170: keep approved heads current in the background (S6-V86)
Verdict: DEFER -> pairs with P153 (closure cache; itself DEFER on #2828, not on main) and the merge-queue decision. What would change the answer is the train's recarry CI wait per batch from the train logs, against the CI minutes a background refresh of every verdicted head would spend. (Round-1 re-cut, applying verdicts 6402369226 and 6402374814 on the sibling batches: an unmeasured benefit is DEFER, never ACCEPT.)
- Merging main into a clean head is what R10-FLOW-BODY-ONLY's part (a) stops ("merge origin/main into the head only when the pull request is DIRTY or merge-tree reports a conflict"). Its carry 8 holds that part pending the owner's merge-queue decision (tvofi card 4, 2026-10-24).
- Each background merge moves a verdicted head and needs a carried verdict (`app_approve.sh --carry`) and a new CI run. With several verdicted heads in flight, every main move multiplies those runs, and without a closure cache each is a full scoped run.

Source: s6 `proposals.md` `## V86` (orchestrator, 2026-10-25, tvofi-accepted T10).
Instances: the train's own recarry is the step it replaces (`merge_train.py` recarry, `MAIN-MOVED` recovery at `:574-581`).
Cost: M, plus CI minutes that scale with in-flight x main moves.
Binding: it pays only with V74's cache and the merge-queue decision, both round-11. Closure saving: 0 h in round 10.

## P171: runnable Definition of Done, the ten most frequent block reasons in prepr (S6-V88)
Verdict: DEFER -> owned by the carries named below (the mechanical block classes are in prepr or in P135). Ranking a top ten waits on P172's Pareto. (Round-1 re-cut, applying verdicts 6402369226 and 6402374814 on the sibling batches: an unmeasured benefit is DEFER, never ACCEPT.)
Carried already:
- carry-missing: R10-FLOW-JIDOKA carry 11;
- unnamed red: `prepr.sh:1417`;
- host paths: JIDOKA carry 18;
- claims: `prepr.sh:278`;
- head-moved: the reviewer-dispatch refusal, triage P135 -> R10-ORCH-REVIEW-PACKET.

Source: s6 `proposals.md` `## V88` (orchestrator, 2026-10-25, tvofi-accepted F2).
Instances: block classes are coded today in the verdict shape `blocked <sha> <class>: ...` (`fix-review.md`, for example `mutation-vacuous` at line 12, `class-open` at 28, `carry-missing` at 46, `head-moved` at 88, `architecture-unsound` at 134).
Cost: none new in round 10.
Binding: the mechanical classes are covered. The rest are judgements a lint cannot make. Closure saving: 0 h new.

## P172: block-reason taxonomy and Pareto per round (S6-V89)
Verdict: DEFER -> D13 owns the measurement: a per-round Pareto of `blocked <sha> <class>` verdicts. The top cause already routes to the root-cause rule at the third instance. (Round-1 re-cut, applying verdicts 6402369226 and 6402374814 on the sibling batches: an unmeasured benefit is DEFER, never ACCEPT.)
- The taxonomy exists: the verdict shape `blocked <sha> <class>` (`fix-review.md`).
- D13 already measures first-pass yield and rounds per merge from parsed verdicts (`D13.md:19-24`).
- "The top cause gets a mistake-proofing fix" is the existing root-cause rule. At about the third instance a recurring error owes `root-cause.md`: a cause, a process state, and a countermeasure or a recorded refusal (CLAUDE.md, `defect-root-cause.md`).
- The round-11 item is a per-round Pareto by class in D13's report, feeding that rule.

Source: s6 `proposals.md` `## V89` (orchestrator, 2026-10-25, tvofi-accepted F3).
Instances: none counted in the tree. A Pareto by verdict class is not recorded; the plan-opt study's offline counts are out of tree and not used as a figure.
Cost: S (an enumerator beside D13's).
Binding: round 10's top causes are already being fixed (JIDOKA, P135, P140). The Pareto pays from round 11's first wave. Closure saving: 0 h in round 10.

## P173: starter templates per change kind (S6-V90)
Verdict: DEFER. What would change the answer is the count of blocked verdicts whose class is a missing body section, harness or mutant scaffold, by verdict id. (Round-1 re-cut, applying verdicts 6402369226 and 6402374814 on the sibling batches: an unmeasured benefit is DEFER, never ACCEPT.)
Source: s6 `proposals.md` `## V90` (orchestrator, 2026-10-25, tvofi-accepted F4).
Instances: none measured.
Cost: M (four scaffolds, each kept current with the contract).
Binding: a scaffold that drifts from the contract is a new block class. Build it once round 11's contracts are fixed. Closure saving: 0 h in round 10.

## P174: cheap self-review before handoff (S6-V91)
Verdict: DEFER -> needs the rubric (P176, itself DEFER on #2831, not on main) and a scoring harness. What would change the answer is a small model's rubric findings scored against real verdicts on a sample of round-10 handoffs. (Round-1 re-cut, applying verdicts 6402369226 and 6402374814 on the sibling batches: an unmeasured benefit is DEFER, never ACCEPT.)
Source: s6 `proposals.md` `## V91` (orchestrator, 2026-10-25, tvofi-accepted F5).
Instances: none measured.
Cost: M plus a design step.
Binding: unscored, it adds a step of unknown yield. Closure saving: 0 h in round 10.

## P175: first-pass yield per brief source (S6-V92)
Verdict: DEFER -> D13 owns the measurement: first-pass yield split by brief source, read from the brief citations. (Round-1 re-cut, applying verdicts 6402369226 and 6402374814 on the sibling batches: an unmeasured benefit is DEFER, never ACCEPT.)
Source: s6 `proposals.md` `## V92` (orchestrator, 2026-10-25, tvofi-accepted F7).
Instances: round 10's first-pass yield is 117/255 (0.46), from `python3 tools/audit/seat/flow_metrics.py --window 2026-10-15T12:37:57Z..2026-10-25T19:00:00Z --roster origin/main:dev/programme/rosters/wave-r10-groups.json --prefix R10-` (the window opens at the round-10 roster's first commit). It has not been split by source.
Cost: XS inside D13's enumerator.
Binding: it tells round 11 which brief source to repair first. Closure saving: 0 h in round 10.

