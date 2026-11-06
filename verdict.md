Fix review: blocked eb7102637619f5aea0368e4d421be57960c35c77 citation-false: the RCA cites round 9 leads.json's ThermalModel._stability_substeps as an unbuilt D1-s4 lead, but the record says raised_by D1-s2, "closed by D1-s2-02"

bus-nonce: ac5ebdb44a950d68775e5e332841bfff

Round 1 (first-round adversarial fix review) of #3261, group R10-RCA-PROCESS-WORKER-HANG, measured at head eb7102637619f5aea0368e4d421be57960c35c77 (merge base 198b8f7ed21fdd10dc3407aa95b92f906b6bb27a). Worktree detached at the head. Role contract current (`git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty).

## Block

- **Claim.** The RCA's "Why the worker went silent" says: "the lead that would bound the substep count whatever the input (`dev/audit/rounds/round9/leads.json`, symbol `ThermalModel._stability_substeps`, owner D1-s4) was not built" (r10-process-worker-hang.md:67). `## Needs tvofi` item 2 (line 211) repeats "(round 9 leads.json, D1-s4)" and calls it "a D1/D2 finding for round 11". The body's forward-carry dismisses it: "already on record in dev/audit/rounds/round9/leads.json".
- **Evidence.** leads.json at the merge base, lines 786-791 (ev/leads_citation.txt): `{"raised_by": "D1-s2", "symbol": "ThermalModel._stability_substeps", "why": "closed by D1-s2-02 (runaway wind-driven substeps)"}`. The lead was raised by D1-s2, not owned by D1-s4. Round 9 closed it as covered by D1-s2-02's forecast bound; it was not recorded as an open lead left unbuilt. The "D1-s4" comes from the next row (`HeatPumpOptimizer.optimize`, "owner-side D1-s4 guard scope").
- **Harness.** `sed -n 786,797p dev/audit/rounds/round9/leads.json` at 198b8f7ed.
- **Metric.** The owner and the disposition the RCA cites, compared with the owner and disposition the record states. The owner reads D1-s4 in the RCA and D1-s2 in the record. The status reads "not built" (open) in the RCA and "closed by D1-s2-02" in the record.
- **Perturbation.** Reading the neighbouring row, line 795, reproduces the RCA's "D1-s4" exactly, so the citation took the owner from the wrong row.
- **Why it blocks.** The brief owes "why the worker went silent if establishable". This candidate is the only code-side one the RCA names, and it hands the owner a decision on it (Needs tvofi 2). As written:
  - A later seat reads an open D1-s4 lead that the record closed.
  - The owner decides on a misstated record.
  - The dismissal "already on record" points at a record that closes the candidate, so no stage holds it. A merged RCA is read as established fact (CLAUDE.md, "Fix it; ... only then file it").
- **The re-cut.**
  - Correct both citations: raised by D1-s2, closed by D1-s2-02 as covered by `_FORECAST_FIELD_RANGE`. The substep count itself stays uncapped (thermal_model.py:3819, `max(1, ...)`, no cap).
  - Either drop "a D1/D2 finding for round 11" or carry it to a named stage with a precondition and a control (finding-propagation.md). Otherwise record it plainly as an unmeasured candidate this seat did not carry.
  - Re-run `fold_ledger.py check`, `policy_lint.mjs` and the scoped gate after the edit.

## Findings

- **The D1.md step 5 wording has no by-design exception.** The new text: "Every wait on a peer (pipe, child, lock): a live, silent peer (`silent_peer_waits.py`) must time it out, freeing its hold". At every tree `--scan` lists `process_worker.py:73 run_worker: pickle.load(stdin)` (ev/drives.txt). The RCA's own site table dispositions that read "by design: the idle worker waits for its parent; the parent's close is EOF". A D1 finder who applies step 5 as written must report that site as a defect, which the RCA itself rules out.
  - Harness: `--scan` at the head.
  - Metric: sites the rule condemns but the RCA clears. That is 1 (run_worker), and it is 0 under a wording that admits a dispositioned by-design wait.
  - Fix in the same re-cut, within the brief's caps: for example "must time it out, freeing its hold, unless the wait is the peer's own idle state".
  - Carry: R10-RCA-PROCESS-WORKER-HANG
- **The scan's queue arm keys on the receiver's name.** `get()` is flagged only when the receiver's text contains "queue". A planted `q.get()` with no timeout reads 0 sites (ev/mut_scan.txt, planted file, function `b`), while the four other unbounded calls there are flagged. The header says "a queue's `get()` with no timeout" and does not mention the name heuristic. At v7.1.2 the package has no `Queue(` and no other `threading` primitive besides `_PROCESS_LOCK` (grep, ev/checks2.txt context). So the blind spot reaches no site on any tree measured. Carry: dismissed: reaches no site in the package at v7.1.2, main or #3232's head; the RCA already records that the scan reads literal call shapes only (Needs tvofi 1)
- **The body says the branch "touches none of its files", but both PRs change `tests/closures.json`.** #3232 at bba5b4d4d adds `tests/worker_deadlines.py` to it; this PR adds the harness to `inert_reads` (ev/overlap_3232.txt). `git merge-tree --write-tree bba5b4d4d eb7102637` exits 0 with `LEDGER-MERGE: resolved tests/closures.json` (ev/vs_3232.txt). Every new tracked file must be classified in that shared ledger, so this overlap cannot be avoided, and it merges clean. Carry: dismissed: shared generated ledger with a merge driver, clean merge measured against #3232's head bba5b4d4d; none of #3232's code or test files touched

## Evidence

Re-derived, all at the trees named:

- **Drive table** (ev/drives.txt; the harness at head is sha1 7572c722b, as the body says). Reproduced row for row:
  - v7.1.2 silent: `reply_returned_within_cap=0`.
  - v7.1.2 `--reply-timeout 2`: `NOTE this tree has no PROCESS_REPLY_TIMEOUT_S`, then 0.
  - v7.1.2 `--answer`: 1 at 0.10 s.
  - main 9cbd7dd0d and merge base 198b8f7ed: the same three rows.
  - #3232 head 0e59de557 silent: 0. With `--reply-timeout 2`: 1, `reply_elapsed_s=2.00`, `OUTCOME raised ProcessWorkerTimeout`. With `--answer`: 1 at 0.10 s.
- **"Stop frees the read in 0.00 s at v7.1.2"** is reproduced: `stop_elapsed_s=0.00`, `reply_released_after_stop=1` on every tree.
  - Null control: the `--answer` arm, with no job in flight, also reads 0.00 s.
  - Perturbation (mine): a v7.1.2 copy with the kill/terminate before `with _PROCESS_LOCK` removed (`if worker.poll() is None:` changed to `if False:`). It reads `stop_returned_within_cap=0`, `stop_elapsed_s=6.00`, `reply_released_after_stop=0`, and its `--answer` control stays at 0.00 s (ev/mut_stop.txt). So the stop figure moves when the kill-first premise is removed, and the figure is not vacuous.
- **Scan.** `RESULT unbounded_sites=6` at v7.1.2, main, the merge base and #3232's head. The sites match the RCA's table (ev/drives.txt).
- **Scan over every tag.** I re-ran it over all 158 `v*` tags with `git archive` (ev/tag_scan.txt). Counting calls only: 0 up to v6.3.14, 2 at v6.3.15, 3 from v6.4.0 and 4 from v7.0.5. This matches the body.
- **Harness mutants (mine)** on v7.1.2 (ev/mut_scan.txt, mutant files in ev/m_*.py). Each drops the count from 6 to 4:
  - the `pickle.load` predicate set to `if False:` (the body's own mutant; it reproduces `6 -> 4` and the defect site disappears);
  - the zero-arg arm off;
  - the `_LOCK` `with` arm off;
  - the timeout-kw test forced.
- **Bounded end of the scan.** A planted file whose function `a` has `wait(timeout=)`, `run(timeout=)`, `get(timeout=)`, a 4-argument `select` and `acquire(timeout=)` reads 0 sites. Its function `b`, with the same calls unbounded, reads 4 (the queue one is missed; see Findings). An awaited `e.wait()` is skipped, as designed.
- **Git figures.**
  - `git tag -l 'v*' | wc -l` = 158 (v2.3.0-beta.1, 2026-08-20, to v7.1.4, 2026-11-06).
  - Merges in v6.3.15..v7.1.4 = 5,594; tags from v6.3.15 = 55.
  - First tag of 8542e51cb (2026-09-05) = v6.3.15; of 1c4d70fdd (2026-09-28) = v6.7.11.
  - First commits under round8 and round9 = 2026-10-07; under round10 = 2026-10-15.
  - `_FORECAST_FIELD_RANGE` was introduced by eab073836 (2026-09-29), with wind (0.0, 100.0) at v7.1.2 coordinator.py:2684.
- **Code citations at v7.1.2,** checked by a read-only locator agent (tool-checked):
  - features.py:41831 "which dies with the worker"; `_f15_reap_under_solve` at :41814; the D1-s2-05 check at :41856.
  - `_G525_STUBBORN` and `_G533_STUBBORN` never call `_run_in_process`.
  - `D9/s1/worker_rss.py` exists.
  - thermal_model.py:3819 has `n_sub` with a floor and no cap.
  - dhw_planner.py:1493 calls `linprog` with no `time_limit`.
  - The L-BFGS-B call passes only `maxiter`.
  - replay.py has `InProcessWorker` (:1688) and `unusable` (:2261).
  - #3232 at 0e59de557 sets `PROCESS_REPLY_TIMEOUT_S = 1800.0`, `_SHUTDOWN_LOCK_TIMEOUT_S = 5.0` and `_REPLY_FRAME_TIMEOUT_S = 60.0`.
- **round9 batch1-findings.json.**
  - D1-s2-05 carries the quoted `pickle.load`, "30-70 s" and "D1-s2-02 runaway" text, and its `phenomenon_property` is the stop-bounded property the RCA quotes.
  - D1-s2-02 carries the 1e12, 3.45 and 60 s figures.
- **#3226's body** confirms 09:02:28, the restart at about 10:11, 14-15 % to 37-39 % CPU at 09:15 and memory about 49 %, and the trace lines 1909/1850.
- **Cost-test arithmetic** re-computed:
  - 75,000/158 = 475 s/release.
  - (0.67 + 21 + 900) x 10/158 is about 58 s/release.
  - 5,594/55 is about 102 merges, and 102 x 0.67 is about 68 s.
  - 3 x 600/55 is about 33 s.
  - These hold. The scan median here is 0.74 s over 5 runs (ev/scan_timing.txt) against 0.67 s claimed: another machine, and immaterial to the 58 < 475 result.
- **Cost-test figures I could not verify.**
  - Not re-derivable: #3232's "last updated 20:03Z" and "38 commits". The PR now reads updated 20:51:10Z with 49 commits, so the snapshot cannot be recovered.
  - Verified: created 2026-11-06T00:16:06Z.
  - The 71,200 s term is therefore unverified to within about 3,000 s. The pass margin survives that.
- **Ledger and policy checks at the head** (ev/checks.txt, ev/checks2.txt):
  - `fold_ledger: 0 violation(s)`. With `barrier_refusal` removed it reads `UNRECORDED-BARRIER: N-reap-lock ...` and `1 violation(s)`, so the entry is both required and accepted.
  - `STRUCTURE RATCHET PASSED`.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`; `--budgets` rc 0.
  - No `*budgets*.json`, VERSION, manifest or RELEASE_NOTES.md in the three-dot diff.
  - The claim files are untouched.
  - `tests/closures.json` classifies the harness under `inert_reads` / `tests/harness_headers.py`.
  - `closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, as the body says.
  - `dev/programme/delivery/3261.md` is in the diff.
- **Merge with main.** `git merge-tree --write-tree origin/main(28482eceeb) eb7102637` exits 0, so it merges clean.
- **`## Head`** names eb7102637619f5aea0368e4d421be57960c35c77, which is the head I measured.
- **CI.** `merge_train.py classify eb7102637 --pr 3261` returned `GREEN eb7102637619f5aea0368e4d421be57960c35c77 pending: none red: none`, rc 0 (ev/ci_classify.txt).
- **Every check-run page** (107 runs, pages 1-2; ev/check_runs_all.txt and ev/check_runs_p2.txt): 3 concluded `failure`, all named `gate`.
  - IDs: 128162705998, 128164588196, 128176687653.
  - Each log reads `FAIL run(s) [...] at this head are still being judged; their gate decides`, a deferral. Attempt 3 (128177123255) is green.
  - `pr-contract.yml:290-311` excludes `gate` from the reds a body must answer ("it is red whenever anything required is red"). So `## Red checks: none` is the correct set, though its reason "CI has not yet run" is now stale.
  - Not a root-cause trigger. `instrument-self-tests` is green, and `nightly-status` is not owed: no workflow file is in the diff.
- **Mutation lane.** The diff writes no production line, so the green `mutation` lane drew no mutant. The mutants above are mine.

## Friction

- The `gh api --paginate` check-run listing breaks at page 2 through the proxy ("Numeric-ID repository paths ... not supported"). I fetched page 2 by an explicit `&page=2`.
