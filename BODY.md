Policy and one instrument arm: the countermeasure of `dev/audit/rca/R11-RCA-3729-OPEN-AXIS.md`. A class claim that quantifies over a set no rule enumerates lets review find one new member per round: #3729 was blocked `class-open` six times on `_r11_logger_aliases`, rounds 6 and 7 on dependency entry points (asyncio handlers, `frame.report_usage`) that no enumerator reads. **Process state (c)**: `fixer.md` step 8, `fix-review.md` step 6 and the re-cut rule all existed and were obeyed; their unit checked that *a rule exists*, not that *every set the claim quantifies over is a rule's output or a stated residue category*, and the re-cut escalation's text named `claims` only. Approved by the owner on 2026-11-21 under mandate 6893738184 (scope all): "You can approve the permanent fix under the mandate. Fix it locally immediately". The interim rule has bound cloud fixers and reviewers since `dispatch/comms-r11` 6c17b87e62 (ADDENDUM items 8-10); this pull request is its permanent form.

## Summary

- **`fixer.md` step 8.** Every set the claim quantifies over is a named rule's output, or wholly residue by a category the claim states; a set named by examples (a list, "such as", a census of one) is neither. It replaces "If no such instrument exists, say so and what you did instead", which the new clause answers (state the category or narrow the claim).
- **`fix-review.md` step 6.** A seam of such a set blocks the set once: `class-open: axis <set> unenumerated (e.g. <seam>)`, the set's words repeated verbatim so a later block on it is comparable.
- **`fixer.md` "Past three rounds".** A re-cut body blocked again (the text said "on `claims`"; `bus.sh dispatch` already refused a re-cut blocked again on any judgement class), or a second block on one `class-open` axis at any round, goes to the orchestrator to narrow, split or close.
- **`bus.sh` `axis_repeat`.** `dispatch` refuses when verdict/<pr>'s latest block is an axis block and an earlier head was blocked on the same set, unless `--past-three <reason>`; a `## Re-cut` note does not lift it. Five self-test arms (one refusal, one escape, three null controls) and mutant marker `mut:axisrepeat`.
- **Record.** `dev/audit/rca/R11-RCA-3729-OPEN-AXIS.md` and its `_rca` entry in `dev/audit/config/bugclasses.json` (class `null`: no bug class covers repeated review blocks, so no class `rca` cite).
- **Paid, not raised.** Both role files fit their `files_tokens` caps by cutting duplicated or implied prose (list under Figures); no budget moves.

## Cost test

From the RCA, unit wall-clock hours per programme day. Over all 1129 `verdict/*` and `archive/verdict/*` refs (2026-10-06 to 2026-11-21, about 46 days), 8 PRs are static guards over an open reach or spelling set with three or more blocked heads: 31 blocks, 23 repeat rounds. At `R11-RCA-CLASS-OPEN.md`'s median 6.2 h from block to next verdict that is 142.6 h, 3.1 h/day. An axis block caps each open axis at two blocks: 31 become 18, 13 rounds x 6.2 h = 80.6 h, about 1.75 h/day recoverable (estimate, retrospective classification). Standing cost: about 5 min per `class-open` block at about 3.4 a day, 0.28 h/day, at most 0.56 h/day with the fixer side. Passes down to a removal rate of about 16-32% of the estimate. Shadow measure: PRs with three or more distinct `class-open` heads over round 12 (this window: 8); if it does not fall, withdraw the clauses.

## Approval

Policy (`fixer.md`, `fix-review.md`), so `main-protect-checks`' code-owner rule applies. The owner approved this countermeasure on 2026-11-21 under mandate 6893738184 (scope all, to 2026-12-15T12:00Z, on #3394): "You can approve the permanent fix under the mandate. Fix it locally immediately". The approving review at the head is owed by the mandate holder, declared with the mandate id. State addressed: (c). No budget raise, so `budget-raise-gate` does not apply.

## Head

`aadfc314a5484363f2c09e4b6c92000c8a927845`, two commits on `origin/main` `63c6d1cff9` (measured 2026-11-21T21:56Z). Read the diff three-dot.

## Mutation proof

`python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'bash axis_check.sh' --in-place` (spec and checker in the seat's scratch; the checker runs `bus.sh --self-test` and passes only when all five `axis_repeat` arms print `ok`):

```
SURVIVED NULL
KILLED axisrepeat     (the dispatch guard becomes `if false; then`)
KILLED samehead       (drops the head inequality: a re-post at one head counts twice)
KILLED sameset        (drops the set equality: any two axis blocks refuse)
KILLED latestonly     (reads the latest AXIS block instead of the latest block)
rc=0
```

## Null control

- The self-test's own null controls: two blocks on two different axes dispatch; an axis block re-posted at one head is one block and dispatches; two blocks on one axis followed by a later block of another class dispatch.
- `bus.sh --self-test` at the merge base `63c6d1cff9` on this macOS host: `240 checks, 28 failed`; at this head `245 checks, 28 failed` with the same 28 failing names (`diff` of the sorted `FAIL` lines empty). The five added checks pass; the 28 are host-environment failures present at the base and are CI's to grade on Linux.
- The first head of this branch cut "Instrument, test, policy and body deltas never widen it." from step 12 and the `root-cause-detectable` example from step 11; `review_packet.py --self-test` (1 failed) and `check-wave-script.mjs` pin those, so both are back in shorter forms and both now pass (133/0, 296/0).

## Figures

<!-- figure-block: scope-line mb=63c6d1cff9a29ec0c99bcbd5e12c229b61e7c184 head=aadfc314a5484363f2c09e4b6c92000c8a927845 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->
- Per-file caps: `node tools/policy/policy_lint.mjs --budgets` prints `dev/governance/roles/fixer.md 313 315 5215 5216` and `dev/governance/roles/fix-review.md 137 140 2774 2775`, exit 0; no `*_budgets.json` edited.
- Prose paid for the clauses: `fixer.md` drops "The owner's rule." and "If no such instrument exists, say so and what you did instead" (the new clause answers it), and restates step 8's instance sentence and the #592 reason shorter; `fix-review.md` drops "not one per round" (implied by "every one found") and shortens its preamble line 9, steps 4, 6, 11, 12 and 13 and the closing round line, removing no rule.
- Lints: `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s) across 58 policy file(s)`; `node tools/policy/brief_lint.mjs` exit 0; `node tools/policy/rules_sync.mjs --check` printed `RULES-SYNC ok`; `node tools/policy/check-wave-script.mjs` printed `296 passed, 0 failed`; `python3 -I tools/audit/seat/review_packet.py --self-test` printed `133 checks, 0 failed`; `python3 tools/audit/fold_ledger.py check` printed `0 violation(s)`.
- `bash tools/audit/seat/bus.sh --self-test`: `245 checks, 28 failed` at the head, `240 checks, 28 failed` at the merge base, sorted `FAIL` lines identical.
- Scoped gate: `python3 tests/closure.py select --diff 63c6d1cff9 --workdir $D` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/doc_claims.py`, `tests/entities.py`); `tests/doc_claims.py` rc 0; `tests/entities.py` still running past 70 min on this loaded macOS host at handoff, with the same 35 `FAIL` names at the head and at the merge base after 1546 `ok` lines each (host-environment failures; CI's Linux run is the authority); run_always `tests/env_drift.py --claims-only 63c6d1cff9`, `tests/closure.py selftest`, `tests/layout.py`, `tests/harness_headers.py` and `tests/structure.py` each rc 0.

## Red checks

none known at this head; the orchestrator reads the check-runs.

## Forward-carry

none: the clauses bind every fixer and fix reviewer through their role contracts (`finding-propagation.md`, "Constrains every seat"); the interim copy is ADDENDUM items 8-10 on `dispatch/comms-r11`. #3729's own restatement (axis 2 closed by category) is the RCA's section "For #3729", the orchestrator's to put in that group's next brief. Carry: dismissed: the orchestrator holds #3729's brief and has the RCA path

## Friction

none
