R10-RCA-FLUSH-DISPATCH: the root-cause seat for the owner's ruling of 2026-11-07. The stamp's record flush dispatches all of Nightly to run the one-minute `record-autofix` job. This seat ran beside R10-FLY-STAMP-FLUSH-COST and never inside it, so this diff does not touch `tools/release/stamp.py` or `.github/workflows/nightly.yml`.

What lands:
- `dev/audit/rca/r10-rca-flush-dispatch.md`, the analysis;
- class `N-dispatch-overreach` and `_rca` `R10-RCA-FLUSH-DISPATCH` in `dev/audit/config/bugclasses.json`;
- `dev/audit/harnesses/r10_rca_flush_dispatch.py`, which reproduces every run figure (`fixer.md` step 18);
- its INERT READS entry in `tests/closures.json`;
- the class id registered where the agreement lane reads it: `dev/audit/config/finding.schema.json` and `.claude/workflows/audit-find.js`.

The four results:
- **Cause.** The flush rule took a job as the unit of dispatch, and the API dispatches a workflow.
  - Triage P88 (`dev/programme/triage/s6-batch19.md`) and the R10-FLOW-RECORD-PITCH carry both say "dispatches `record-autofix`".
  - `record-autofix` had lived in `nightly.yml`, beside every heavy lane gated on `github.event_name != 'push'`, since `abf4f40b7` (2026-10-21).
  - `6b1aa629f` (#2836) implemented the carry. It recorded the every-lane fact only as a code comment on `FLUSH_MAX_DISPATCHES`.
- **Process state: (c).** The triage cost gate (`proposal-triage.md`, whose cost list names "CI runners") was obeyed: P88 has a `Cost:` line. But it priced the stamp step under the job unit.
  - The flush self-tests and mutants drive a `dispatch=` double and never read what the dispatch starts.
  - The fix review of #2836 was asked about no runner cost.
  - Why not (a), (b) or (d) is in the document's section 3.
- **Cost test.**
  - Defect: 26 dispatches since #2836 merged, at most 15909 runner-min, 33 of them the wanted job. On 11-07: 7 dispatches, 3557 runner-min, all 7 cancelled, and 916 runner-min of finished ledger shards that never landed.
  - A generic dispatch-scope check is **refused under the bound**. Its reach is 1 of 7 code callers, and the instance is pinned by R10-FLY-STAMP-FLUSH-COST.
  - A one-line `proposal-triage.md` cost rule, pricing a dispatch by the jobs it runs, **passes**: about 27 runner-h per cycle against seconds per proposal.
- **Countermeasure.** That rule is policy, so it is **proposed, not landed**. It is the owner's decision.

**Re-cut over a concurrent step.**
- `handoff-wip/r10-rca-flush-dispatch` already held `50a672627` (12:35Z) when this seat first pushed. It came from another run of this seat, and it recorded state (a) and built `tools/audit/seat/dispatch_scope.py` with a `governance.yml` self-test step.
- This head fast-forwards it, withdraws that check and restores `governance.yml` to main's. The reasons are measured in the document's section 5:
  - its regex enumeration does not find `merge_train.py`'s argv-tuple `ci.yml` dispatch (`merge_train found: False`);
  - its `--check` is red on main until the sibling merges;
  - wired as `--self-test` alone, it reads no call site.
- The three-dot diff against main therefore holds no trace of it.

The defect's issue **Root cause** section is not posted: the brief said to post no comment. The document's section 6 is written to be copied.

## Head

`0f9759f46f0c50938d2f46e1d4587bee22a86266`, measured against `origin/main` `28d46c4918285d36c409c1fb2f72eb77e04e569e` at 2026-11-07T13:09Z.

- Main moved during the work, so `origin/main` was merged (never rebased). The merge resolved one conflict, in the class-id lists of `finding.schema.json` and `audit-find.js`, by keeping main's `N-livehead-operator-cancel` and this branch's `N-dispatch-overreach`.
- The merge commit also carries `N-dispatch-overreach`'s `nearest_existing: N-livehead-operator-cancel` and `mechanism_difference` in `bugclasses.json`, for the class main had just added.
- Steps 2 to 8 were re-run on the merged head, and every figure below is from that run.
- `prepr.sh` passed on this head, and main did not move after it, so no second run was owed.

## Mutation proof

n/a: no production or check code is changed. The diff is an RCA document, a ledger entry, a read-only measuring harness and its closure classification.

The ledger entry's pin is `fold_ledger.py check`.

- **Mutant:** delete `_rca["R10-RCA-FLUSH-DISPATCH"]` from `dev/audit/config/bugclasses.json`. `python3 tools/audit/fold_ledger.py check` printed `UNKNOWN-RCA: N-dispatch-overreach cites R10-RCA-FLUSH-DISPATCH, which _rca does not index` and `fold_ledger: 1 violation(s)`.
- **Restored** (`git checkout`): `fold_ledger: 0 violation(s)`.

The harness's discriminating power is shown under `## Null control`.

## Null control

- `python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py runs 42320317707 42372556020`:
  - the 00:47Z `schedule` run reads `ledger-push=success lost=0`;
  - the 12:27Z `push` run reads `total=0`, because every heavy lane skipped.
  - So `lost` and the lane minutes read zero where nothing was lost or run.
- `since 2026-10-21T00:00:00Z` and `since 2026-10-26T02:31:17Z` both print `runs=26`. So no `nightly.yml` dispatch ran between the file's creation and the flush's merge.

## Figures

- 11-07 dispatches: `python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py runs 42344537787 42346251204 42353878060 42357667261 42364230438 42367391498 42369836867` printed `RESULT runs=7 runner_min=3557 record_autofix_min=6 cancelled=7 lost_ledger_min=916`.
  - The rule: runner-min is the sum over a run's latest-attempt jobs of completed_at minus started_at.
  - lost is the success-shard minutes of `mutation-ledger` where `mutation-ledger-push` did not succeed.
- Since #2836 merged: `python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py since 2026-10-26T02:31:17Z` printed `RESULT runs=26 runner_min=15909 record_autofix_min=33 cancelled=7 lost_ledger_min=916`.
  - It is an upper bound on the flush's share: the API names `tvofi` as the actor on every dispatch, so hand dispatches are included.
- Class reach, 1 of 7 code dispatch callers:
  - the rule is a `git grep` of the tree for `/dispatches`, `gh workflow run`, `createWorkflowDispatch` and `repository_dispatch`, docs, comments and fixtures excluded;
  - then a `yaml.safe_load` of each target's jobs and their `if:` lines;
  - every caller is dispositioned in the document's section 4.
- Withdrawn check's blind spot: `call_sites()` of `50a672627`'s `dispatch_scope.py`, copied into this tree, printed `merge_train found: False`, against `tools/audit/seat/merge_train.py`'s `DISPATCH = (("ci.yml", ("-f", "recheck=true")),)`.
- Ledger: `python3 tools/audit/fold_ledger.py check` printed `fold_ledger: 0 violation(s)`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, naming `tests/entities.py`. That script was run, with `PYTHONPATH=tests/hastub`:
  - `tests/entities.py` printed `ALL 2643 ENTITY CHECKS PASSED`;
  - `env_drift.py --claims-only` printed `claims hygiene: 28d46c4918285d36c409c1fb2f72eb77e04e569e ok`;
  - `closure.py selftest` printed `ALL 118 closure shrink pins PASSED`.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- CI prediction: `python3 tools/pr/ci_predict.py --apply-inert` printed `no closures, fast, governance or instrument red predicted against 28d46c491828`. Before the merge, `--apply-inert` wrote the one INERT READS entry.

## Red checks

none

## Forward-carry

- The instance fix (nightly.yml `inputs.lanes`, a `lanes=beat` payload arm, an entities pin) is already bound by triage P404 into its group; this seat adds no text, analysis in `dev/audit/rca/r10-rca-flush-dispatch.md`. Carry: R10-FLY-STAMP-FLUSH-COST
- The triage cost rule pricing a dispatch by the jobs it runs, drafted in `dev/audit/rca/r10-rca-flush-dispatch.md` section 5 for `dev/governance/roles/proposal-triage.md`, is policy and not landed here. Carry: dismissed: policy change awaits the owner decision

## Friction

concurrent-seat: contradiction: `handoff-wip/r10-rca-flush-dispatch` already held another run's step `50a672627` at 12:35Z when this seat first pushed, so two seats ran one topic; resolved by a fast-forward re-cut. Carry: dismissed: one overlap, reported in this body
