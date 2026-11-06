Fix review: blocked 481c7750755be454af93ce8bd8b12f336ed23bac ci-red: governance / instrument-self-tests is red because governance.yml:719 still greps handoff_push.sh --self-test for a delivery_row line the diff removed

bus-nonce: 764e7069209377ee4cb760331731d888

Round: first round (opus), cloud reviewer seat. Measured head 481c7750755be454af93ce8bd8b12f336ed23bac (base dc0a170b671814be196a54b1c71e29449f54d6d7 = origin/main at review time, so merge base = main). Roles diff `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so main's fix-review.md is current; I reviewed under it (the head's C5 text binds only after merge).

## Block

- `governance / instrument-self-tests` (check-run 127824863756, run 42197602280) concluded **failure** at this head. Cause, reproduced: the diff removes `handoff_push.sh`'s row push and with it the `delivery_row self-test: N checks, 0 failed` line its `--self-test` printed (base prints it, head does not), but `.github/workflows/governance.yml:719` still requires that line from `handoff-push-self-test.txt`. In the job log, `handoff_push self-test: 6 checks, 0 failed` is followed directly by `##[error]Process completed with exit code 1.`. Local replay of the step's two greps (`ev/instrument-self-tests-repro.txt`): at the base, delivery_row-grep rc=0 and handoff_push-grep rc=0; at the head, delivery_row-grep rc=1 and handoff_push-grep rc=0. This is broken CI wiring in the diff's own code, not paperwork: a code/harness-class block under both main's fix-review.md and the head's C5 text. The minimal fix is to delete line 719 only. `delivery_row.sh`'s own self-test stays pinned at governance.yml:690-691, so no pin is lost.
- Downstream of it: `pr-contract / pr-contract` (127842523264) is red with `PR-BODY: 2 error(s)`. `## Red checks` names neither `governance / instrument-self-tests` nor `budget-raise-gate / budget-raise-gate` by its check-run name. The body names `budget-raise-gate` and states "No other check has concluded at the head", which was stale by 10:12Z. The code run's `gate` (127843169405) is red with `FAIL budget-raise-gate / budget-raise-gate: failure (run 42197603790)` and `pr-contract / pr-contract: failure (this run)`. `merge_train.py classify 481c7750755be454af93ce8bd8b12f336ed23bac --pr 3245` printed `RED 481c7750755be454af93ce8bd8b12f336ed23bac pending: none red: gate` (rc 1) on every run from 09:52Z to 10:33Z, after all runs concluded. Under the PR's own C8 rule, `bus.sh post` would refuse a merge verdict here too.
- Root-cause trigger (defect-root-cause.md, second trigger): the red was detectable before the handoff by a cheaper detector at near-zero standing cost: running the instrument-self-tests step's own greps, or `grep -n delivery_row .github/workflows/*.yml` after removing a self-test's output line. The fixer's figure line "`bash tools/audit/seat/handoff_push.sh --self-test`: 6 checks, 0 failed" is true but omits the vanished second line. The repair body owes this answer under `## Red checks`, with both check names spelled as the check-runs API reports them.

## Owner constraint (checked explicitly, per change)

Planted production defect, kept with its null control: `custom_components/heatpump_optimizer/boost.py:597` `return hour_in_windows(hour, windows)` -> `return not hour_in_windows(hour, windows)`.
- At the head, `PYTHONPATH=tests/hastub python3 tests/block_duty.py` exited rc=1 with `3 of 46 BLOCK DUTY CHECKS FAILED`, and `tests/closure.py select` printed `MODE: SCOPED -- 22 script(s) run`, selecting block_duty, features and golden.
- At the base (null control), the identical plant gave rc=1, `3 of 46 BLOCK DUTY CHECKS FAILED` and the same 22-script selection (`ev/plant-*.log`).
- Production-guard definitions are byte-identical between base and head: `ci.yml`, `codeql.yml`, `pr-contract.yml`, `tools/ci/`, `tests/mutation_table.py`, `tests/features.py`, `tests/golden.py`, `tests/golden/`, `custom_components/` and `required-contexts.json` show an empty diff. `tests.yml` changes only in `graders-head-copy` (not required; `HPO_JOB_GRADES: nothing`): the delivery_status head-copy step is removed (`ev/prod-guards.txt`).
- `gate.py --self-test` at the head gives 57 checks, 0 failed. None of the deleted jobs (`governance / delivery-status`, `delivery-status-publish`, Nightly `record-autofix` and its push trigger) is in `gate_required`, so the gate's required set is unchanged for production-only, machinery-only and mixed diffs. No required job becomes SKIPPED by this diff, because the gate's derivation code and ci.yml are untouched. I did not run CI on synthetic diffs; this is read from the unchanged derivation.

Per change:
- **C4 (verdict carry; bus.sh dispatch, fix-review.md step 12):**
  - Touches no production path.
  - Still guarding production: tests / mutation, golden, features and CodeQL on every head (unchanged above). Opus review re-runs whenever the own diff changes; the carry predicate is `app_approve.sh --carry`, unchanged.
  - Within card C4 as written. The body states why the risk is acceptable: yes.
- **C5 (paperwork notes; record stream deleted):**
  - Touches no production path. fix-review.md keeps "one on `custom_components/` blocks", matching the owner's "fixed before merge when it concerns production code". Real classes (mutation-vacuous, class-open, metric-gamed, architecture-unsound, head-moved) are unchanged.
  - The governance/record refusal becomes `continue-on-error`. The card said "adjust governance/record so main is not graded on them", so this is within the card.
  - "a figure" being a note is in card C5's text ("figures ... become a non-blocking note"). The body states why the risk is acceptable: yes. Carry: dismissed: evidence, not a finding
- **C8 (dispatch after the cheap checks; post refuses a merge verdict at RED):**
  - Touches no production path. A production review waits only for checks under 10 minutes; the C8 gate never waits on tests / fast.
  - Within the card. The body states why the risk is acceptable: yes. One entry is vacuous; see Findings.
- **C6 (a) (triage seat retired):** no production check reads it. Within the card. The body states why the risk is acceptable: yes.
- **Train fixes (`app_approve.sh carry()`, `postmerge.py` docs step, `release_worktrees`):** no production check changes. The body states why the risk is acceptable: yes.

No cut goes beyond the approved cards, and I measured no large unforeseen risk under the addendum. The block above is a defect, not a cut.

## Policy text changed (for the coordinator to surface to tvofi)

- `fix-review.md`:
  - The new "Block only on code, tests and harness (card C5) ... paperwork (a stale body, a carry route, a figure, a root-cause answer) is a `Note: <class>: <text>` line under `merge`; one on `custom_components/` blocks. `bus.sh post` refuses `merge` at a red (C8)."
  - Step 10: carry-missing becomes a Note.
  - Step 11: silence is a Note, never a block; the delivery-status sentence is dropped.
  - Step 12: a merge verdict carries to any later head whose own diff is unchanged (C4); head-moved only when the own diff moved.
- `defect-root-cause.md` Enforcement: an unanswered red is a note resolved at merge (C5); `nightly-status` only (delivery-status dropped).
- `delivery-status-tracking.md` items 1 and 4: the record is the PR list and #201 via `postmerge.py`, no per-PR row. The row-status paragraph is removed. Added: a stale body is a note resolved at merge, and owner asks go to the roster at merge.
- `finding-propagation.md`: "before the PR ... merges" becomes "by the time the PR ... merges"; Enforcement: "The carry is in the tree by the producing PR's merge (card C5)".
- `fixer.md`: "Your PR does not merge until any finding ... is in that stage's own brief" becomes "Put any finding ... in that stage's own brief".
- `orchestrator.md`:
  - Section 5: proposals are ruled directly by the owner or the orchestrator, with no triage seat (C6).
  - Section 9: the record is postmerge.py's #201 line and roster resume, with no per-PR row.
  - Carry bullet: "bar its delivery row" is dropped.
- `standing-dispatch.md`: the delivery-row check is dropped from Dispatch.
- `standing-roster.md`: the proposal-triage reference is reworded.
- `D11.md` item 5: "goes to proposal-triage.md" becomes "goes to the orchestrator".
- `proposal-triage.md`: deleted.
- `policy_budgets.json`: its two caps are removed.
- CLAUDE.md: the role rows for delivery-status-tracking, finding-propagation and fix-review are rewritten; the proposal-triage row is removed; the root-cause enforcement sentence becomes "an unanswered one is a reviewer's note resolved at merge (card C5)".
- The body says `content approved by tvofi in chat 2026-11-05`; the owner's approving review is still owed.

## Findings

- Follow-up: `CHEAP_CHECKS`' `pr-contract / pr-contract` entry in `bus.sh` never gates a dispatch. ci.yml's `pr-contract` job `needs:` every unit (tests, codeql, governance, hassfest, validate, kernel-points, arch-score, budget-raise-gate), so its check run does not exist while the head is WAIT. At this head it was created at 10:28:44Z, after `tests / fast` and the rest. C8's effective wait set is the other three checks. This does not slow production review (it shortens the wait). The body's limit note covers "not yet created" in general but not that this entry is structurally always absent. Drop it, or state it. Carry: R10-PROCESS-SLIM
- Follow-up: the body's opening figure "1,600 lines removed against about 230 added (`git diff --shortstat $(git merge-base origin/main HEAD)...HEAD`)" does not re-derive. The command gives 36 files, 354 insertions(+), 1867 deletions(-) at this head; 353/1867 at the code head 497da8adc; and 334/1864 at c3b057258. Carry: R10-PROCESS-SLIM
- Follow-up: `dev/README.md:121` still describes "the record-autofix job that rows a merge no branch rowed", which this diff deletes (stale doc sentence; outside policy). Carry: R10-PROCESS-SLIM
- Residual: `tests/entities.py`'s errexit-scan check loses its live-workflow plant arm (the unwrapped record-autofix batch gate). Only the synthetic cases and the shell arm remain. Carry: dismissed: the job the plant read is deleted and the synthetic arms still pin the scan; a new live plant would need another errexit-shaped workflow step, which is not this group's scope.

## Evidence

- Self-tests at the head (`ev/selftests-head.txt`; base in `ev/selftests-base.txt`). Each figure matches the body:
  - app_approve: 324 checks, 0 failed (base 316)
  - merge_train: 446 checks, 0 failed (base 443)
  - postmerge: 15 checks, 0 failed (base 16)
  - handoff_push: 6 checks, 0 failed
  - body_push: 35 checks, 0 failed (base 32)
  - bus: 136 checks, 0 failed on a clean re-run (`ev/bus-selftest-head-clean.log`; base 132). The first head run showed 8 failed because my mutation harness was mutating bus.sh in the same worktree at the same time; the clean re-run supersedes it.
  - structure: STRUCTURE RATCHET PASSED
  - policy_lint rc 0
  - rules_sync: ok
  - check-wave-script: 220 passed, 0 failed
  - entities: ALL 2609 ENTITY CHECKS PASSED
- Mutation proof, in-tree harness (`ev/mut-bus.log`): bus-1 KILLED (8 failed), bus-2 KILLED (5 failed), bus-7 KILLED (1 failed); `RESULT survivors=0`.
- Mutation proof, my own mutants (`ev/mymut.log`; driver `/root/rev/mymut.py`, which is mine, not the fixer's):
  - A1, the carry() rc distinction forced: KILLED, 2 failed
  - A2, the carry() fetch removed: KILLED, 3 failed
  - B1, the C8 post gate passes RED: KILLED, 4 failed
  - B2, the C8 post gate passes unreadable: KILLED, 4 failed
  - B3, the C4 derivation off: KILLED, 3 failed (including its null control arm)
- Not re-run by me: the release_worktrees and postmerge docs-step mutants (the self-test arms exist and pass), and the out-of-tree docs-step probe. That probe is the fixer's own one-off reproduction and has no committed harness; noted, not verified.
- No finder's harness is named (process group, no finding id). Card figures (RFT, verdict counts, token and job-minute estimates) are cited from the slip study, not re-taken, as the body says.
- Claim files, `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (empty diff); pr-contract's version-edit step agrees.
- The only `*_budgets.json` change is the two removed `proposal-triage.md` caps, with the file deleted. That is not a raise in substance; budget-raise-gate reads it as `489 -> None` and owes the owner's approving review.
- `git merge-tree --write-tree origin/main 481c7750755be454af93ce8bd8b12f336ed23bac`: rc 0, tree d35e6225d204944ea1c7ca3f7d095e38c3516bb0, no conflict (`ev/merge-tree.txt`).
- Check-runs read across all pages (53 at the last read). Concluded reds:
  - budget-raise-gate / budget-raise-gate ×2: expected; owner approval owed.
  - governance / instrument-self-tests: the block.
  - pr-contract / pr-contract: body errors, downstream of the block.
  - gate ×2: the edit run's deferral red at 09:49Z, and the code run's red.
- C8 limit check: `merge_train.py classify` reads only required/gate contexts, so the post gate refuses at a gate RED rather than at "any concluded red" as the card says. Every production check is in `gate_required`, so production reds are covered; a non-required red such as instrument-self-tests reaches it only through pr-contract and the gate, as it did here.
- Head check: `fix/r10-process-slim` still at 481c7750755be454af93ce8bd8b12f336ed23bac at the last read. The body's `## Head` names 481c7750 and the code head 497da8adc; the only commit between them is the delivery row.
