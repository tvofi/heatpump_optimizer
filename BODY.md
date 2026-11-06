Root cause for the v7.1.2 process-worker hang, group R10-RCA-PROCESS-WORKER-HANG (trigger 1, the defect reached a release). The fix is #3232; this branch touches none of its files.

- Analysis: `dev/audit/rca/r10-process-worker-hang.md`, cited by the `_rca` entry `R10-RCA-PROCESS-WORKER-HANG` in `dev/audit/config/bugclasses.json`. That entry is also on class `N-reap-lock`'s `rca` list, and the class now carries a `barrier_refusal`, which `fold_ledger.py check` requires once a class has an in-tree RCA.
- **Cause:** `_run_in_process` read the reply with `pickle.load(stdout)` and no deadline while holding `_PROCESS_LOCK`. The read has been unbounded since 8542e51cb (first tag v6.3.15). The worker was computing, not dead: one core stayed busy for about 55 minutes with memory flat. No tool can now say which job it ran, on which inputs, or why it did not finish; the document lists what is known.
- **Why the stop did not free the lock: not reproduced.** At v7.1.2 the kill-first stop path frees the read in 0.00 s, both for a silent job and for a CPU-spinning one.
- **Process state (c).** Round 9's D1 seat read this lock and this read (D1-s2-05), but it measured stop latency against a finite solve. The double in its check ends the read when the worker is killed. D1 step 5 injects exceptions, and a silent peer never raises one. The #511 checks drive only a worker that fails.
- **Countermeasure.** Step 5 of `dev/governance/dimensions/D1.md` becomes "Guards, waits": every wait on a peer (pipe, child, lock) is now driven by a live, silent peer, with the instrument `dev/audit/harnesses/silent_peer_waits.py`. The brief was at its line and token caps, so the change is paid for by tightening step 5 and step 6's #1090 sentence; no cap moved. **This is a policy change: it merges only on the owner's approving review**, and it addresses state (c) by changing the unit that missed the defect.
- **Cost test.** The wait arm costs about 58 s per release against about 475 s per release for the defect. A per-PR static arm costs about 100 s per release and also passes, but only on one instance. It cannot land green before #3232 merges, so it is left to the owner (the document's `## Needs tvofi`).

## Approval

Awaiting the owner's approving review. The diff changes `dev/governance/dimensions/D1.md`, step 5 ("Guards, waits"). That is a change to what a D1 finder must do: drive every wait on a peer with a live, silent peer. It addresses process state (c).

## Head

`5c246022a` (branch head, three commits on origin/main `9cbd7dd0d`). origin/main had not moved when this body was written, so `prepr.sh` was not rerun after a merge.

## Mutation proof

This diff adds no production code, so the proofs break the instrument and the fix it reads:
- **Scan arm.** With the harness's `pickle.load` predicate replaced by `if False:` (a scratch copy), the scan over v7.1.2's package drops the defect's site: `_run_in_process: pickle.load` 1 → 0 lines, `RESULT unbounded_sites=6` → `4`.
- **Drive arm, the fix's deadline removed.** v7.1.2 has no `PROCESS_REPLY_TIMEOUT_S`, and there `--drive --cap 6 --silent 30 --reply-timeout 2` reads `RESULT reply_returned_within_cap=0` with `NOTE this tree has no PROCESS_REPLY_TIMEOUT_S`. #3232's head `0e59de557` under the same arguments reads `RESULT reply_returned_within_cap=1`, `RESULT reply_elapsed_s=2.00`, `OUTCOME raised ProcessWorkerTimeout`.

## Null control

- `--drive --cap 6 --answer` (a job that answers in 0.1 s) reads `RESULT reply_returned_within_cap=1`, `RESULT reply_elapsed_s=0.10` at v7.1.2, at main `9cbd7dd0d` and at #3232's head. The drive does not fire on a healthy reply and does not go green by skipping.
- At #3232's head with the shipped 1800 s deadline, `--drive --cap 6 --silent 30` reads `reply_returned_within_cap=0`. Only the deadline perturbation turns the arm green.
- The scan's count is `RESULT unbounded_sites=6` at v7.1.2, at main and at #3232's head. The count does not move with the fix, which is why the scan is an enumerator for disposition, not a pass/fail check (stated in the document).

## Figures

- Drive rows (the document's first table): `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/silent_peer_waits.py --drive --cap 6 --silent 30`, with `--reply-timeout 2` and `--answer` variants, from a checkout of each tree (v7.1.2, `9cbd7dd0d`, `0e59de557`). The harness at head has sha1 `7572c722b23431c5a5c4610d0f4eecadbf87b960`.
- Site table: `python3 dev/audit/harnesses/silent_peer_waits.py --scan custom_components/heatpump_optimizer`, from a checkout of each tree. Per tag, the same rule runs over `git archive <tag> custom_components` for every tag in `git tag -l 'v*'`.
- Merge commits per release: `git log --merges --oneline v6.3.15..v7.1.4 | wc -l`, over `git tag -l 'v*' --sort=v:refname | awk '/^v6.3.15$/{f=1} f' | wc -l`.
- First tags: `git tag -l 'v*' --contains 8542e51cb --sort=v:refname | head -1` and the same for `1c4d70fdd`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` and names `tests/entities.py`. The run was `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`: `ALL 2637 ENTITY CHECKS PASSED`, `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN` at `5c246022a`. A disclosed self-correction: the first run, at `a65397f3c`, read `1 of 2637 ENTITY CHECKS FAILED`. The failing check was the policy acceptance (`the template arm turns ... the real template keeps it green`). My first draft of the D1 change, a new step 7, took the brief over its `[budgets]` caps and named the RCA document from a policy file; `5c246022a` folds the change into step 5. `node tools/policy/policy_lint.mjs` now reads `TOTAL: 0 error(s) across 50 policy file(s)`.
- `STRUCTURE RATCHET PASSED`: `python3 tests/structure.py`.
- `fold_ledger: 0 violation(s)`: `python3 tools/audit/fold_ledger.py check`.
- Policy budgets within cap: `node tools/policy/policy_lint.mjs --budgets` (exit 0).
- `CI PREDICT: no closures, fast, governance or instrument red predicted`: `python3 tools/pr/ci_predict.py`, after `--apply-inert` wrote the harness's `INERT READS` entry (commit `a65397f3c`).

## Unpinned sites

n/a: no production code changed. The diff adds no `custom_components/` site, and the harness is an audit instrument outside the mutation lane.

## Red checks

none: CI has not yet run on this head.

## Forward-carry

- The wait arm's destination is step 5 of `dev/governance/dimensions/D1.md`, which round 11's D1 finder reads. Carry: dismissed: lands in this PR's diff, in D1.md
- Per-PR static arm over `--scan`, buildable only after #3232 merges. Carry: dismissed: owner decision, recorded under `## Needs tvofi` in dev/audit/rca/r10-process-worker-hang.md
- Substep-cap lead (`ThermalModel._stability_substeps`, owner D1-s4). It is the remaining code-side candidate for the 55-minute computation, and this seat measured nothing new. Carry: dismissed: already on record in dev/audit/rounds/round9/leads.json

## Friction

- defect-root-cause: unclear: the rule asks for a **Root cause** section on the defect's own issue, but the defect has no issue (#3226 is a pull request), and this seat is told to post no comment. The section's content is the document's `## Result`. Carry: dismissed: posting it is the orchestrator's, on #3232 or #3226