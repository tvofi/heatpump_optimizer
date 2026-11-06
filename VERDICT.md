Fix review: merge e17fadc1795ebbaaf0f01ed067fbb59aeba90dee

bus-nonce: db4cb0f7de565298f717ca2008c60b51

Round 2 of the adversarial fix review of #3261 (group R10-RCA-PROCESS-WORKER-HANG). I measured it at head e17fadc1795ebbaaf0f01ed067fbb59aeba90dee from a worktree detached at that head. The merge base is 28482eceeb6b9809e44b12d80fc994282cc21645, which is origin/main. The repair is commit f914e1d9c, merged in at e17fadc17.

## Round-1 findings, re-measured

- **Block, citation-false: settled.**
  - Record: leads.json at the merge base, lines 787-790, reads `"raised_by": "D1-s2"`, `"symbol": "ThermalModel._stability_substeps"`, `"why": "closed by D1-s2-02 (runaway wind-driven substeps)"` (ev/citation.txt).
  - RCA now: line 65 and Needs tvofi item 2 (line 215) state exactly that record. "D1-s4", "was not built" and "a D1/D2 finding for round 11" are gone. The candidate is now recorded plainly as unmeasured and assigned to no stage.
  - The RCA's "uncapped" claim holds: v7.1.2 thermal_model.py has `n_sub = max(1, int(np.ceil(...)))` with no upper bound (ev/citation.txt).
  - The body's forward-carry agrees with the RCA.
- **D1 step 5 had no by-design exception: settled.** Step 5 now ends "unless the wait is its own idle state", which admits `run_worker`'s `pickle.load(stdin)`. The scan still lists it (process_worker.py:73, ev/drives.txt), and the rule now clears it.
- **Scan header and the queue heuristic: settled.** The header now states the name heuristic ("`q.get()` is not seen; the package has no queue"). The repair's harness change is docstring only, so the scan's logic is unchanged.
- **Overlap with #3232 in closures.json: settled.** The body now states it and quotes the clean merge-tree run against #3232's head bba5b4d4d.

## Findings

- **The repair's tightening of step 5 drops "next cycle" from the swallowed-exception arm.** "recover next cycle" became "recovers".
  - Harness: `node tools/policy/policy_lint.mjs` on D1.md with "next cycle" put back.
  - Metric: TOTAL error count, 0 to 1. The new error is `[budgets] ... about 820 tokens ... exceeds its cap of 819 tokens` (ev/d1_perturb.txt).
  - Null control: the same lint on the unedited file reads `TOTAL: 0 error(s)` (ev/checks.txt).
  - The brief is at its cap, so the cut was forced. "Recovers" still requires recovery.
  - Carry: dismissed: forced by the D1 brief's 819-token cap (measured), recovery still required; the owner approves the D1.md wording at merge
- **`## Red checks` gives the right set but a stale reason.** It says "head f914e1d9c ... has no check runs yet", but the head e17fadc1 has run CI.
  - I read every check-run page with `filter=all` (ev/check_runs_filter_all.txt). The only concluded failures are 4 `gate` runs (128213733037, 128213724460, 128202148031, 128201061248). The later `gate` runs 128213388457, 128215102848 and 128215425787 are success.
  - `gate` is excluded from the reds a body must answer by pr-contract.yml, so "none" is the correct set.
  - Carry: dismissed: the named set is correct at this head; only the stated reason is stale, and pr-contract is green

## Evidence

- **Head.** ev/HEAD.txt holds e17fadc1795ebbaaf0f01ed067fbb59aeba90dee. The body's `## Head` names the same SHA.
- **Merge with main.** `git merge-tree --write-tree origin/main HEAD` exits 0. It prints `LEDGER-MERGE: resolved tests/closures.json`, so it merges clean.
- **Three-dot diff.**
  - The 6 files are bugclasses.json, silent_peer_waits.py, the RCA document, D1.md, delivery/3261.md and closures.json.
  - It holds no VERSION, manifest, RELEASE_NOTES.md, `*budgets*.json` or claim file.
  - closures.json adds the harness to the inert list.
- **Drive, finder's harness at the head**, run against `git archive` trees (ev/drives.txt):
  - v7.1.2, silent: `reply_returned_within_cap=0`.
  - v7.1.2, `--reply-timeout 2`: `NOTE this tree has no PROCESS_REPLY_TIMEOUT_S`, then 0.
  - v7.1.2, `--answer` (null control): 1, at 0.10 s.
  - #3232 head bba5b4d4d, silent (shipped 1800 s deadline): 0.
  - #3232 head, `--reply-timeout 2`: 1, at 2.00 s, `OUTCOME raised ProcessWorkerTimeout`.
  - #3232 head, `--answer`: 1, at 0.10 s.
  - So the harness fails on the unbounded read and passes on the bounded one. Every row reads `stop_elapsed_s=0.00` and `reply_released_after_stop=1`, which reproduces "stop frees the read in 0.00 s at v7.1.2". Round 1's kill-removed perturbation of that figure (6.00 s) still applies, because the repair leaves the drive code unchanged.
- **Scan.** `RESULT unbounded_sites=6` at v7.1.2 and at bba5b4d4d.
- **Harness mutant.** With the `pickle.load` predicate set to `if False:` (ev/m/m_pickle.py), v7.1.2 reads `unbounded_sites=4` (ev/mut_scan.txt). The scan catches the mutant, so it is not vacuous.
- **Harness hash.** `sha1sum` of the harness at the head is 56af5c5ad3c7549d517bfee8d868c3c7b4b9fd40, which matches the body (ev/harness_sha.txt).
- **Checks at the head** (ev/checks.txt):
  - `fold_ledger: 0 violation(s)`.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`; `--budgets` rc 0.
  - `STRUCTURE RATCHET PASSED`.
  - `closure.py select`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, which matches the body.
- **Delivery row.** dev/programme/delivery/3261.md is in the diff and reads open.
- **CI.** `merge_train.py classify e17fadc1795ebbaaf0f01ed067fbb59aeba90dee --pr 3261` reads `GREEN e17fadc1795ebbaaf0f01ed067fbb59aeba90dee pending: none red: none`, rc=0 (ev/classify.txt).
  - instrument-self-tests is green.
  - nightly-status is not owed, because no workflow file is in the diff.
- **Carried from round 1, not re-taken by my own command in this round.**
  - These figures: the tag-scan series, the git counts (158 tags; 5,594 merges over 55 tags), and the cost-test arithmetic (58 s against 475 s per release).
  - They are unaffected by the repair. Its diff touches only the RCA's two citation paragraphs, the D1.md wording and the harness docstring.
