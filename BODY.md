Owner rulings tvofi 2026-11-07 and 2026-11-09 ("No pr merge should be blocked on a non-required red"): only a red in the set `merge_train.py owed-reds` prints is owed a `## Red checks` answer or may block. `defect-root-cause.md` states it; this PR closes the three places that did not carry it. Policy files change: under mandate 6715477401.

- `dev/governance/roles/fixer.md` and `fix-review.md`: one sentence each citing `defect-root-cause.md`, not restating it. fix-review.md's narrower nightly-status/delivery-status sentence is replaced by the general one; fixer.md folds it into the existing trigger sentence, so both files stay inside their `policy_lint.mjs --budgets` per-file caps (fixer.md sits at its line cap; the cut is the restated "You are naming the trigger, not analysing it", which the kept clause "the analysis is `root-cause.md`'s seat" still carries).
- `tools/audit/seat/cloud_dispatch.py`: `OWED_REDS_LINE` appended to the reviewer and fixer prompts (`OWED_REDS_ROLES`), naming `python3 tools/audit/seat/merge_train.py owed-reds`.
- `tools/audit/seat/orchestrator_tick.py`: the `RED unanswered in ## Red checks` line now reads only reds in `merge_train.judged(merge_train.gating_names(req))`, `req` the PR-head ruleset as the NOT REVIEWABLE arm reads it; an unreadable set (`required is None`) keeps every red. A head whose reds are all outside the set no longer costs a body read.

Alternatives: filtering in the tick through `review_packet.unanswered_reds` (which shells out to `policy_lint`) was not taken: the tick only needs set membership and already imports `merge_train`, the set's one owner; one owner, no subprocess per PR.

## Head

790e98bde8d7a162b5be137af83317ea4c8bc098 (base 7bdc8aa2ec92934b96b77d3fd8d331b1c23d3769, origin/main's tip at the cut).

## Mutation proof

In-tree harness `dev/audit/harnesses/r10_seat_selftests_mutants.py`, new mutants (each one-occurrence replacement, the named self-test step run, file restored):
- `cloud_dispatch-21 cloud_dispatch.py`: KILLED rc=1 | cloud_dispatch self-test: 133 checks, 1 failed
- `cloud_dispatch-22 cloud_dispatch.py`: KILLED rc=1 | cloud_dispatch self-test: 133 checks, 1 failed
- `orchestrator_tick-6 orchestrator_tick.py`: KILLED rc=1 | orchestrator_tick self-test: 296 checks, 3 failed
- `orchestrator_tick-7 orchestrator_tick.py`: KILLED rc=1 | orchestrator_tick self-test: 296 checks, 1 failed
- `orchestrator_tick-8 orchestrator_tick.py`: KILLED rc=1 | orchestrator_tick self-test: 296 checks, 1 failed
- `orchestrator_tick-9 orchestrator_tick.py`: KILLED rc=1 | orchestrator_tick self-test: 296 checks, 1 failed

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 cloud_dispatch-21 cloud_dispatch-22 orchestrator_tick-6 orchestrator_tick-7 orchestrator_tick-8 orchestrator_tick-9`: `RESULT survivors=0` (run at 4439321c385f5937682da6068e99e86b4631737c; the later head changes only fixer.md prose). -21 drops the prompt line, -22 the fixer from `OWED_REDS_ROLES`, -6 the tick's filter, -7 `gating_names`, -8 `judged`, -9 the unreadable-set fallback.

## Null control

- The tick arm `PRS owed reds: unreadable set: every red (null control)` (required None: `tests` and `codeql` both named) passes at base and head; with only the test added, the other three arms failed at the base production code (`orchestrator_tick self-test: 296 checks, 3 failed`: required set read, NOT_GATING in the ruleset, a gate unit under GATE).
- cloud_dispatch arm `and no other role is (null control: a seat that never meets a check run)`: probe, designer and design-reviewer prompts carry no `owed-reds`; with only the test added, the reviewer/fixer arm failed (`cloud_dispatch self-test: 133 checks, 1 failed`).
- M0 (unmutated) of the mutant harness: every seat step exits 0.

## Figures

- `python3 -I tools/audit/seat/orchestrator_tick.py --self-test` at head: 296 checks, 0 failed.
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` at head: 133 checks, 0 failed.
- Generator run (fixer.md step 10): `python3 -I tools/audit/seat/cloud_dispatch.py --role fixer --head 7bdc8aa2ec92934b96b77d3fd8d331b1c23d3769 --topic t --env-id e --model m --repo o/r | grep -c owed-reds` prints 1 at head, 0 from a `git archive` of the base (control: the same command with `CLOUD FIXER\|owed-reds` prints 1 there, so the base rendered). Reviewer: 1 at head; probe: 0 at head.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run`, `tests/entities.py`, run with `PYTHONPATH=tests/hastub`: `ALL 2672 ENTITY CHECKS PASSED` at 790e98bde8d7a162b5be137af83317ea4c8bc098 (the run at 4439321c3 failed one, the template-arm acceptance, on a 12-word fixer.md run duplicating `.github/PULL_REQUEST_TEMPLATE.md`; repaired in 790e98bde, `node tools/policy/policy_lint.mjs` then `TOTAL: 0 error(s)`).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/policy_lint.mjs --budgets`: rc 0; per-file rows for fixer.md and fix-review.md within their caps.
- Class enumeration (fixer.md step 8): `git grep -l "Red checks" -- 'tools/audit/seat/*.py' 'tools/policy/*.mjs'` returns nine files. Dispositions: `orchestrator_tick.py` closed in this diff; `cloud_dispatch.py` closed in this diff (its existing hit is the reviewer's Evidence heading list); `merge_train.py`, `review_packet.py`, `policy_lint.mjs` already guarded (`owed-reds`, `unanswered_reds`, `--required-file`); `beat_jobs_selftest.py` (a fixture copy of the tick's line), `record_row.py` (writes record bodies; naming a red it is not owed blocks nothing) and `figure_lint.mjs` (section parsing) decide no obligation; `dependabot_contract.mjs` refuses any red at a Dependabot head, unfiltered by `required`, a distinct seam (Forward-carry).

## Approval

Policy change (`dev/governance/roles/fixer.md`, `dev/governance/roles/fix-review.md`) under mandate 6715477401, as the dispatch brief records it; nothing here is approved by this seat. It merges on the approval `main-protect-checks`' code-owner rule requires (decision 0009 step 6) or under that mandate's scope.

## Red checks

none

## Forward-carry

- `tools/policy/dependabot_contract.mjs`'s clause 4 (`dependencyBumpProblems`, reached from `checkPrBody`'s Dependabot arm) refuses a Dependabot head on any red, `required` not consulted, so a non-required red keeps a bump unmerged. Its header records that as a design choice (no one answers `## Red checks` for a bot); whether the 2026-11-09 ruling reaches it is the owner's call, and changing it is outside this brief's three gaps. Carry: dismissed: a recorded design choice of the Dependabot contract, surfaced here for the orchestrator to put to the owner; no stage brief owns it.

## Friction

none
