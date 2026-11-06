Root cause for the v7.1.2 process-worker hang, group R10-RCA-PROCESS-WORKER-HANG (trigger 1, the defect reached a release). The fix is #3232; this branch touches none of #3232's code or test files. Both PRs change `tests/closures.json`, a shared generated ledger with a merge driver: `git merge-tree --write-tree bba5b4d4d HEAD` (#3232's head) exits 0.

- Analysis: `dev/audit/rca/r10-process-worker-hang.md`, cited by the `_rca` entry `R10-RCA-PROCESS-WORKER-HANG` in `dev/audit/config/bugclasses.json`. That entry is also on class `N-reap-lock`'s `rca` list, and the class now carries a `barrier_refusal`, which `fold_ledger.py check` requires once a class has an in-tree RCA.
- **Cause:** `_run_in_process` read the reply with `pickle.load(stdout)` and no deadline while holding `_PROCESS_LOCK`. The read has been unbounded since 8542e51cb (first tag v6.3.15). The worker was computing, not dead: one core stayed busy for about 55 minutes with memory flat. No tool can now say which job it ran, on which inputs, or why it did not finish; the document lists what is known.
- **Why the stop did not free the lock: not reproduced.** At v7.1.2 the kill-first stop path frees the read in 0.00 s, both for a silent job and for a CPU-spinning one.
- **Process state (c).** Round 9's D1 seat read this lock and this read (D1-s2-05), but it measured stop latency against a finite solve. The double in its check ends the read when the worker is killed. D1 step 5 injects exceptions, and a silent peer never raises one. The #511 checks drive only a worker that fails.
- **Countermeasure.** Step 5 of `dev/governance/dimensions/D1.md` becomes "Guards, waits": each peer wait (pipe, child, lock) is driven by a live, silent peer, with the instrument `dev/audit/harnesses/silent_peer_waits.py`, "unless the wait is its own idle state", which admits `run_worker`'s `pickle.load(stdin)` (the idle worker waits for its parent; the parent's close is EOF). The brief was at its line and token caps, so the change is paid for by tightening step 5 and step 6; no cap moved. **This is a policy change: it merges only on the owner's approving review**, and it addresses state (c) by changing the unit that missed the defect.
- **Code-side candidate, not carried.** `ThermalModel._stability_substeps` was raised by D1-s2 and closed by D1-s2-02 in round 9's `leads.json`, as covered by `_FORECAST_FIELD_RANGE`. The substep count stays uncapped (`max(1, ...)` in thermal_model.py). The RCA records it as an unmeasured candidate this seat did not carry.
- **Cost test.** The wait arm costs about 58 s per release against about 475 s per release for the defect. A per-PR static arm costs about 100 s per release and also passes, but only on one instance. It cannot land green before #3232 merges, so it is left to the owner (the document's `## Needs tvofi`).

## Approval

Awaiting the owner's approving review. The diff changes `dev/governance/dimensions/D1.md`, step 5 ("Guards, waits"). That is a change to what a D1 finder must do: drive every wait on a peer with a live, silent peer, unless the wait is its own idle state. It addresses process state (c).

## Head

`f914e1d9c79ffd4e5f1017ab43ee6ffbc0b4230e`, the final code head, pushed to `handoff-wip/r10-rca-process-worker-hang`. It contains origin/main `28482eceeb6b9809e44b12d80fc994282cc21645` (merge `04f41926f`), so the merge base is origin/main and main has not moved since that merge. All figures below were taken at this head on 2026-11-06 22:26Z. Drive and scan rows on other trees were taken from `git archive` checkouts of the tree named.

## Mutation proof

This diff adds no production code, so the proofs break the instrument and the fix it reads:
- **Scan arm.** With the harness's `pickle.load` predicate replaced by `if False:` (a scratch copy), the scan over this head's package drops the defect's site: `pickle.load` lines 2 → 0, `RESULT unbounded_sites=6` → `4`.
- **Drive arm, the fix's deadline removed.** v7.1.2 has no `PROCESS_REPLY_TIMEOUT_S`, and there `--drive --cap 6 --silent 30 --reply-timeout 2` reads `RESULT reply_returned_within_cap=0` with `NOTE this tree has no PROCESS_REPLY_TIMEOUT_S`. #3232's head `0e59de557` under the same arguments reads `RESULT reply_returned_within_cap=1`, `RESULT reply_elapsed_s=2.00`, `OUTCOME raised ProcessWorkerTimeout`.

## Null control

- `--drive --cap 6 --answer` (a job that answers in 0.1 s) reads `RESULT reply_returned_within_cap=1`, `RESULT reply_elapsed_s=0.10` at v7.1.2, at main `9cbd7dd0d` and at #3232's head `0e59de557`. The drive does not fire on a healthy reply and does not go green by skipping.
- At #3232's head with the shipped 1800 s deadline, `--drive --cap 6 --silent 30` reads `reply_returned_within_cap=0`. Only the deadline perturbation turns the arm green.
- The scan's count is `RESULT unbounded_sites=6` at v7.1.2, at `9cbd7dd0d`, at #3232's head and at this head. The count does not move with the fix, which is why the scan is an enumerator for disposition, not a pass/fail check (stated in the document).
- Review findings, answered. The scan's queue arm keys on the receiver's text containing "queue" (the header now says so) and reaches no site in the package. D1 step 5 admitted no by-design wait; it now does (the `unless` clause above).

## Figures

Run from the worktree at head `f914e1d9c`, origin/main `28482eceeb`, 2026-11-06 22:26Z, with `PYTHONPATH=tests/hastub:custom_components`.
- Scan: `python3 dev/audit/harnesses/silent_peer_waits.py --scan custom_components/heatpump_optimizer` prints `RESULT unbounded_sites=6` (coordinator.py x5, process_worker.py:73 `run_worker`). The same scan over `git archive` of v7.1.2, `9cbd7dd0d` and `0e59de557` also prints 6. The harness at head has sha1 `56af5c5ad3c7549d517bfee8d868c3c7b4b9fd40`.
- Drive rows: `python3 dev/audit/harnesses/silent_peer_waits.py --drive --cap 6 --silent 30`, with `--reply-timeout 2` and `--answer` variants, from a checkout of each of v7.1.2, `9cbd7dd0d`, `0e59de557`. Silent: `reply_returned_within_cap=0` on all three. `--reply-timeout 2`: 0 on the first two, 1 at 2.00 s on `0e59de557`. `--answer`: 1 at 0.10 s on all three. `stop_elapsed_s=0.00` and `reply_released_after_stop=1` on every row.
- Tags and merges: `git tag -l 'v*' | wc -l` prints 158. `git log --merges --oneline v6.3.15..v7.1.4 | wc -l` prints 5594, over `git tag -l 'v*' --sort=v:refname | awk '/^v6.3.15$/{f=1} f' | wc -l`, which prints 55.
- First tags: `git tag -l 'v*' --contains 8542e51cb --sort=v:refname | head -1` prints v6.3.15, and the same for `1c4d70fdd` prints v6.7.11.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$(mktemp -d)"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` and names `tests/entities.py`.
- `fold_ledger: 0 violation(s)`: `python3 tools/audit/fold_ledger.py check`.
- `TOTAL: 0 error(s) across 50 policy file(s)`: `node tools/policy/policy_lint.mjs`; `node tools/policy/policy_lint.mjs --budgets` exits 0.
- `STRUCTURE RATCHET PASSED`: `python3 tests/structure.py`.

## Unpinned sites

n/a: no production code changed. The diff adds no `custom_components/` site, and the harness is an audit instrument outside the mutation lane.

## Red checks

none: the head `f914e1d9c` is on `handoff-wip/r10-rca-process-worker-hang` and has no check runs yet (one read of its check-runs, all pages: total_count 0). `gate` is excluded from the reds a body must answer by `pr-contract.yml`.

## Forward-carry

- The wait arm's destination is step 5 of `dev/governance/dimensions/D1.md`, which round 11's D1 finder reads. Carry: dismissed: lands in this PR's diff, in D1.md
- Per-PR static arm over `--scan`, buildable only after #3232 merges. Carry: dismissed: owner decision, recorded under `## Needs tvofi` in dev/audit/rca/r10-process-worker-hang.md
- `ThermalModel._stability_substeps` uncapped substep count: raised by D1-s2, closed by D1-s2-02 as covered by `_FORECAST_FIELD_RANGE`; an unmeasured candidate this seat did not carry. Carry: dismissed: no run shows an input inside the forecast bound that makes the count matter; recorded in dev/audit/rca/r10-process-worker-hang.md
- D1 step 5 condemned `run_worker`'s `pickle.load(stdin)`, which the RCA clears as by design. Carry: R10-RCA-PROCESS-WORKER-HANG
- Scan queue arm keys on the receiver's name containing "queue". Carry: dismissed: reaches no site in the package at v7.1.2, main or #3232's head; the RCA records that the scan reads literal call shapes only
- Body said the branch touches none of #3232's files, but both change `tests/closures.json`. Carry: dismissed: shared generated ledger with a merge driver, clean merge measured against #3232's head bba5b4d4d; none of #3232's code or test files touched

## Friction

- defect-root-cause: unclear: the rule asks for a **Root cause** section on the defect's own issue, but the defect has no issue (#3226 is a pull request), and this seat is told to post no comment. The section's content is the document's `## Result`. Carry: dismissed: posting it is the orchestrator's, on #3232 or #3226
