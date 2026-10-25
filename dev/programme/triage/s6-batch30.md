# Proposal triage, session s6, batch 30 (P168-P175)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch29.md` (P158-P167). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). It rules eight of the V79-V103 ideas; none saves round-10 closure time, so each is a round-11 design item recorded in R10-ROUND-PLAYBOOK (one carry, under P175), or is narrowed to what round 10 already carries. Facts read at origin/main dfcd8d9be.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P168: fail-fast CI ordering (S6-V81)
Verdict: ACCEPT narrowed -> round-11 measurement item; the cancel-on-first-red half is REJECTED.
- The cancel half: `## Red checks` must name every red at the head (`prepr.sh:1417`, policy_lint's unnamed-red arm). Cancelling the remaining jobs at the first red would show one red per round, and a fixer would need a round per red. That costs whole review rounds (median 1.45 h to 2.35 h) to save runner minutes.
- The ordering half: the CI units run as parallel jobs (`ci.yml:254`, `gate` needs the units), so job order does not change the wall time. Only the serial order of scripts inside a job could. The tests matrix already sets `fail-fast: true` where it applies (`tests.yml:197-203`).
- The measured long pole is CodeQL on batch proofs, which is ruled in P158 (R10-PROOF-CODEQL), not reordered.

Source: s6 `proposals.md` `## V81` (orchestrator, 2026-10-25, tvofi-accepted T4), with the orchestrator's CodeQL measurement (2026-10-25).
Instances: no per-script failure probability is recorded in the tree.
Cost: S to measure. The round-11 item is to order the scoped tests job's scripts by measured p(red) / runtime once check-run history supplies the numbers.
Binding: no saving without data, and a real harm in the cancel half. Closure saving: 0 h in round 10 (P158 carries the measured gain).

## P169: live reviewer pairing for large or critical-path groups (S6-V85)
Verdict: ACCEPT -> round-11 design item.
- A reviewer who shadows the implementation is anchored on the fixer's approach. The fix reviewer's contract requires a fresh context, a frozen head, and the finder's harness, never the fixer's (`fix-review.md:3-4`, and CLAUDE.md's role table).
- Round 10 already places early adversarial judgement where it is cheapest for L and XL groups: the designer and design review (`designer.md`, `design-review.md`).
- A design must keep the verdicting reviewer independent of any shadow, for example a shadow seat that never posts the verdict.

Source: s6 `proposals.md` `## V85` (orchestrator, 2026-10-25, tvofi-accepted T9).
Instances: none measured. Mean rounds per fix PR 2.26 (plan-opt, n=110).
Cost: M in policy (`fix-review.md`, `fixer.md`) plus a second reviewer seat per group.
Binding: independence is the reviewer's whole value, so a design must settle it before any build. Closure saving: 0 h in round 10.

## P170: keep approved heads current in the background (S6-V86)
Verdict: ACCEPT -> round-11 design item, paired with P153 (closure-keyed CI cache), as the filing says.
- Merging main into a clean head is what R10-FLOW-BODY-ONLY's part (a) stops ("merge origin/main into the head only when the pull request is DIRTY or merge-tree reports a conflict"). Its carry 8 holds that part pending the owner's merge-queue decision (tvofi card 4, 2026-10-24).
- Each background merge moves a verdicted head and needs a carried verdict (`app_approve.sh --carry`) and a new CI run, PR run wall median 920 s. With mean in-flight 10.4, every main move multiplies those runs, and without a closure cache each is a full scoped run.

Source: s6 `proposals.md` `## V86` (orchestrator, 2026-10-25, tvofi-accepted T10).
Instances: the train's own recarry is the step it replaces (`merge_train.py` recarry, `MAIN-MOVED` recovery at `:574-581`).
Cost: M, plus CI minutes that scale with in-flight x main moves.
Binding: it pays only with V74's cache and the merge-queue decision, both round-11. Closure saving: 0 h in round 10.

## P171: runnable Definition of Done, the ten most frequent block reasons in prepr (S6-V88)
Verdict: ACCEPT narrowed. The mechanical block reasons are already carried into prepr and into the pre-review gate, so no new round-10 carry. Ranking the top ten needs P172's Pareto, so that half is a round-11 item.
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
Verdict: ACCEPT -> round-11 item under D13.
- The taxonomy exists: the verdict shape `blocked <sha> <class>` (`fix-review.md`).
- D13 already measures first-pass yield and rounds per merge from parsed verdicts (`D13.md:19-24`).
- "The top cause gets a mistake-proofing fix" is the existing root-cause rule. At about the third instance a recurring error owes `root-cause.md`: a cause, a process state, and a countermeasure or a recorded refusal (CLAUDE.md, `defect-root-cause.md`).
- The round-11 item is a per-round Pareto by class in D13's report, feeding that rule.

Source: s6 `proposals.md` `## V89` (orchestrator, 2026-10-25, tvofi-accepted F3).
Instances: round 10's Pareto was taken offline by plan-opt, at window C: 63 blocks; 16 real, at least 14 mechanical, 14 carry-missing.
Cost: S (an enumerator beside D13's).
Binding: round 10's top causes are already being fixed (JIDOKA, P135, P140). The Pareto pays from round 11's first wave. Closure saving: 0 h in round 10.

## P173: starter templates per change kind (S6-V90)
Verdict: ACCEPT -> round-11 design item. The PR body template and contract already exist (`.github/PULL_REQUEST_TEMPLATE.md`, the headings `checkPrBody` requires). Per-kind harness and mutant skeletons are new and need the kinds settled first: the roster's `kind` values today are mostly `instrument` (101 groups), then `defect` (29), `owner` (16) and `policy` (10).
Source: s6 `proposals.md` `## V90` (orchestrator, 2026-10-25, tvofi-accepted F4).
Instances: none measured.
Cost: M (four scaffolds, each kept current with the contract).
Binding: a scaffold that drifts from the contract is a new block class. Build it once round 11's contracts are fixed. Closure saving: 0 h in round 10.

## P174: cheap self-review before handoff (S6-V91)
Verdict: ACCEPT -> round-11 design item (the filing marks it "design seat"). A small-model rubric pass before the handoff needs a rubric (V94, ruled in batch 31) and a scoring harness against real verdicts. Both are design questions.
Source: s6 `proposals.md` `## V91` (orchestrator, 2026-10-25, tvofi-accepted F5).
Instances: none measured.
Cost: M plus a design step.
Binding: unscored, it adds a step of unknown yield. Closure saving: 0 h in round 10.

## P175: first-pass yield per brief source (S6-V92)
Verdict: ACCEPT -> round-11 item under D13. D13's yield population (`D13.md:19-24`) gains one split, by the source of the group's brief (triage, design, orchestrator), read from the brief's citations (`triage: ...#P<n>`, design refs).
Source: s6 `proposals.md` `## V92` (orchestrator, 2026-10-25, tvofi-accepted F7).
Instances: round 10's overall first-pass yield is 38/71 = 0.54 (plan-opt flow_metrics). It has not been split by source.
Cost: XS inside D13's enumerator.
Binding: it tells round 11 which brief source to repair first. Closure saving: 0 h in round 10.

Carry text (for `roster_edit.py append-carry R10-ROUND-PLAYBOOK`, citing `triage: dev/programme/triage/s6-batch30.md#P175`): "Round-11 design backlog, batch 30 (tvofi-accepted, triage s6 batch 30 P168-P175). (1) V81: order the scoped tests job's serial scripts by measured p(red) / runtime from check-run history. Cancel-on-first-red is rejected, because `## Red checks` must name every red. (2) V85: live reviewer pairing for L, XL and critical-path groups, designed so the verdicting reviewer stays independent of any shadow (`fix-review.md`). (3) V86: keep verdicted heads current in the background; only with the closure cache (V74) and the merge-queue decision, and against R10-FLOW-BODY-ONLY's clean-head rule. (4) V88: rank the ten most frequent block classes from (5) and add the mechanical ones not yet in prepr. (5) V89: a per-round Pareto of `blocked <sha> <class>` verdicts in D13's report, feeding the root-cause rule at the third instance. (6) V90: per-kind starter scaffolds (product defect, instrument, policy, roster) generated from the contract. (7) V91: small-model self-review before handoff against the rubric (V94), scored against real verdicts; needs a designer. (8) V92: D13's first-pass yield split by brief source. Each item states its round-11 owner seat."
