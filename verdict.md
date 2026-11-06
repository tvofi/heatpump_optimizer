Fix review: blocked bba5b4d4d7ac37f339850de36b1ca24573f8c821 mutation-vacuous: measure (the frame size cap's running count, coordinator.py:1957 `left_bytes -= size`, deleted) survives all 4902 feature checks

bus-nonce: cc3bfb99f232e5aa4e460ab2399b3ede

## Block

- This is round 5 of #3232, a slim replacement for p-3232-r4, which went idle with no verdict. From the fourth round on, `fixer.md` owes a re-cut.
- **The problem.** `_REPLY_FRAME_MAX_BYTES` is described as "the most the reply frame may carry". The only thing that makes it a bound on the **frame** is `left_bytes -= size` at `custom_components/heatpump_optimizer/coordinator.py:1957`. Without that line it only bounds each single `read()`.
- **The mutant.** I deleted that one line (mutant `measure`, `ev/mutant-m_measure.diff`) and ran `PYTHONPATH=tests/hastub python3 tests/features.py` at the head. Result: `ALL 4902 FEATURE CHECKS PASSED`, rc=0 (`ev/features-m_measure.tail.txt`). It survives.
- **It is not equivalent.** I wrote a direct probe, `ev/probe_measure.py`, which is my own instrument, not the finder's. It shortens the cap to 1,000,000 bytes and feeds the real `_frame_reader` a protocol-5 reply holding two 600 kB byte strings, 1,200,044 bytes in all:
  - at the head: `refused: reply frame exceeds 1000000 bytes`;
  - under the mutant: `frame of 1200044 bytes ACCEPTED over cap 1000000`;
  - at base 9a54629e (null control, which has no cap): ACCEPTED.

  So the mutant really reopens what the owner's SECURITY ruling asked to close, an unbounded total reply, through many reads that each stay under the cap. Not one check sees it.
- **Why CI's mutation lane missed it.** The lane is green, and no ledger row covers line 1957. The 20 `killed_by` rows and 1 `survivor_triage` row this PR adds include none for it. As far as the ledger shows, the mutation operators have no deletion of an augmented assignment, so `tests / mutation` never drew this mutant.
- **Repair, in scope for a re-cut.** Add one check to `tests/worker_deadlines.py`: a frame whose individual reads each fit under a shortened cap, but whose total exceeds it, is refused with `ValueError` and the worker is reaped. Then pin this mutant by hand, as a `killed_by` row for the site or the operator's equivalent.

## Findings

- Instrument gap: `tests/mutation_table.py` draws no mutant that deletes an augmented assignment (`x -= n`), so a running-count bound like `left_bytes` can be unpinned while the mutation lane stays green. The block above repairs this one instance. The operator gap is a class beyond this PR, and only the orchestrator can route it to a roster group, since this seat cannot write the roster. Carry: dismissed: instrument class outside this PR's diff; the orchestrator routes it to the mutation-tooling owner or refuses it

## SECURITY

I read the whole three-dot diff (`git diff $(git merge-base origin/main HEAD)...HEAD`, 34 files) line by line. One line per item:

1. **pickle / deserialisation.** Only the integration's own child writes the pipe. `_ensure_worker` spawns it from the installed package, and the parent picks the job (`fn, args`). The parent already ran `pickle.load` on the worker's reply at base. The diff adds no new deserialisation: `_frame_reader` feeds the same `pickle.load` under a time bound and a size bound, and the descriptor-less branch is the base behaviour. The new error paths raise before or instead of loading, never after a partial load is used. The size bound is checked before `os.read` allocates. Earlier rounds killed `check_after_read`, and I did not re-run it. Its cumulative half is unpinned: see Block. CLEAR apart from the Block.
2. **Subprocess and pipe handling.**
   - `selectors.DefaultSelector` on the raw descriptor fixes the FD_SETSIZE limit; the check at fd 1119 passes at the head.
   - The reply timeout kills the worker and reaps it with `wait(timeout=5)`. An exception there is swallowed so it cannot mask the timeout, and the handle is cleared, so the next job spawns fresh. No zombie can outlive the wait except one stuck in the kernel, which the comment names.
   - The stop path takes `_PROCESS_LOCK.acquire(timeout=5)` inside `try/finally`, so it is released on every path. On a timeout it skips only the handle swap.
   - No signals are installed. CLEAR.
3. **Paths, network, secrets.** None introduced. The only path use is `tests/worker_deadlines.py` inserting the repository root into `sys.path` and opening `os.devnull`, both in a test. CLEAR.
4. **.github, CI, workflow, hook or tool edits.** None. The diff touches `tests/closure.py` (`NOT_A_TEST` += `worker_deadlines.py`), `tests/closures.json` (+2 entries), `tests/run.sh` (two skip-list entries) and `tests/entities.py`. The `entities.py` change is a census exclusion keyed on receiver `os`, and r4 measured its planted defect as refused. No workflow permission change. CLEAR.
5. **Dependencies and imports.** Standard library only: `selectors`, `time` and `types.SimpleNamespace` in `coordinator.py`. `services.py` imports `ProcessWorkerUnavailable` from its own package. No requirement or manifest change. CLEAR.
6. **Code run on the host.**
   - Test code spawns only the integration's own worker, through `_run_in_process`. It raises `RLIMIT_NOFILE` to at most 1200, within the hard limit, and restores it in `finally`. It opens 1100 `/dev/null` fds and closes them in `finally`.
   - `harness.split_reply` writes a fixed pickle and calls `os._exit` in the child.
   - No string reaches a shell. No `eval`, `exec` or `subprocess` with `shell=True` is added. CLEAR.
7. **Translation strings.** `diagnose_interval_failed` and `process_worker_timeout` in strings.json, en.json and sv.json are plain text with `{entry_ids}`, `{error}` and `{minutes}` placeholders only. The `_ET_KEYS` pins in features.py match them. No markup, and no format spec beyond named placeholders. `error` is `str(err)` of the integration's own exception. CLEAR.
8. **CodeQL ground** (injection, traversal, unsafe subprocess/eval/pickle, secrets, workflow permissions). Covered by items 1–7. CodeQL itself concluded success at this head (`codeql / Analyze (python)` id=128172511407, `CodeQL` id=128146651316).
9. **Attribution.**
   - The body's `## Acknowledgements` names @Bankaifan and #3226 as the origin. That suffices without a SECURITY.md entry, because the body is the record a reader of this PR meets.
   - All four contributor commits are in the head with author `Bankaifan`: 61cec72ac, 010534bbc, dd4416f1a and 5088d3688.

## Evidence

- Head: bba5b4d4d7ac37f339850de36b1ca24573f8c821 (`ev/HEAD.txt`).
  - Still the PR head when this verdict was written: the PR read through the GitHub API gives head sha bba5b4d4.
  - The roles directory is unchanged against origin/main, so the contract I applied is current.
- CI: `merge_train.py classify bba5b4d4d7ac37f339850de36b1ca24573f8c821 --pr 3232` exited 0 and printed `GREEN bba5b4d4d7ac37f339850de36b1ca24573f8c821 pending: none red: none` (`ev/classify.log`, `ev/classify.rcs`). With no red check, step 11 owes nothing.
- Merge: `git merge-tree --write-tree origin/main bba5b4d4` against origin/main 28482ecee exited 0, with no conflict (`ev/merge-tree-main.txt`).
- VERSION, the manifest, RELEASE_NOTES.md, `tests/golden` and `.github` are untouched in the three-dot diff.
- RESULT deadline_none at the head. I replaced `_reply_ready(stdout, timeout)` with `_reply_ready(stdout, None)` in `_read_reply` (`ev/mutant-m_deadline_none.diff`). Result: `7 of 4902 FEATURE CHECKS FAILED`, rc=1, **killed**. The failing check texts are in `ev/features-m_deadline_none.fails.txt`, for example "a worker that gives no reply within the deadline raises ProcessWorkerTimeout [raised None after 30.0 s; returned None]" and "a worker pipe at fd >= 1024 answers in time and still times out as a timeout".
- RESULT measure at the head. I deleted `left_bytes -= size`. Result: `ALL 4902 FEATURE CHECKS PASSED`, rc=0, **survives** (see Block). Direct probe: `ev/probe-measure.txt`.
- RESULT r4base null at 9a54629e, unmodified: `ALL 4898 FEATURE CHECKS PASSED`, rc=0.
- RESULT r4base none at 9a54629e, a comment-only edit before `_run_in_process` (`ev/mutant-b_none.diff`): `ALL 4898 FEATURE CHECKS PASSED`, rc=0. The no-op survives, as a null control must.
- The figures checked here match the body: `tests/features.py` has 78361 lines, `tests/worker_deadlines.py` 532.
- I take these as given from p-3232-r4 and did not re-run them, as the brief directs: 4902 checks at the head and 4876 on main; entities 2637 at both ends; the earlier mutants m4, m6, guard_off, frame_time_off, frame_bypass, check_after_read, transl_off and transl_key_off all killed; null_comment survives; CodeQL extraction 1266709 ms for features.py and 642655 ms for entities.py; the largest real reply 22,913 bytes.
- Disclosure: the brief named the mutants `measure` and `deadline_none` but not their edits, and r4's runmut.sh was never pushed. The definitions above are mine (`ev/mutate.py`), and each run wrote its own log, keyed on its own `RESULTLINE`.
