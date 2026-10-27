Fix review: merge 8cdfc0ce950393f3709387a98dc94713f389ed5a
bus-nonce: fb1d0ff38912b58a083d3eabd74c5e94

Verdict: approve — every figure in s6-batch38.md re-derives at 8cdfc0ce, the narrowed `lock_dir` sentence is exactly true with both sets enumerated, all prior findings are answered, and the ACCEPT-narrowed carry ruling is sound.

Measured head: 8cdfc0ce950393f3709387a98dc94713f389ed5a (`git ls-remote origin refs/pull/2881/head refs/heads/fix/triage-s6-batch38` answered it on both refs; the detached worktree is at it).
Merge base: 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc = origin/main.
Diff: 2 files, +109 — `dev/programme/triage/s6-batch38.md` +108 and `dev/programme/delivery/2881.md` +1. Nothing outside the seam; no production code.
Every command and result: EVIDENCE.md.

Prior rounds, answered at this head
- Round 1 F1 (the "only scripts that take the lease" universal): gone. The record enumerates run.sh's `leased()`, mutation_table.py's `_leased_if_exclusive`, judge_batch.py's `Lease`, and the by-hand route, each with a grep that reproduces (1986/2001/2342; 185/196/268/378).
- Round 1 F2 (cites `s6-batch37.md`, absent from the tree): gone. The record now says "One entry." with no sibling citation.
- Round 2 F1 (`needs_lease` omitted the unreadable-scope arm): fixed. "exactly four cases ... (lines 937-949)" names all four `lease` returns at 938/942/944/949, and `needs-lease /nonexistent/scope.scope` prints `lease`.
- Round 2 F2 (`wait=False` claimed only in test/gate_lock.py's self-tests): fixed. The record now says "in `tests/gate_lock.py` and `tests/entities.py`", and the cited `grep -rln ... wait=False tools/ tests/` prints exactly those two files.
- Round 2 F3 (`grep -v gate_lock.py` printed nothing): fixed. The anchored `grep -v '^tests/gate_lock.py:'` prints exactly the eight lines the record lists.
- Round 2 F4 (the body's Figures line said "only for MACHINE_MEASURING"): fixed. The body now states the same four cases with lines 937-949.

The narrowed sentence (record :38-42) is exactly true
- I enumerated the calls and compared sets, not totals. `tests/gate_lock.py` has 2 matches (1855, 1923), lock_dir value set `{lock_dir}`, both generated subprocess source over `Path('{d3}')` / `Path('{d6}')`. `tests/entities.py` has 36 matches, lock_dir value set `{d, d1, d2, lock}`, every one inside a `_gl_*` self-test under a `TemporaryDirectory`. Those are precisely the two lists the sentence gives.
- The CLI is not one of those matches: `_cmd_take` is at 1008, `take(args.label, lock_dir=args.lock_dir, ...)` at 1009-1014, and `--lock-dir` defaults to `DEFAULT_LOCK_DIR` in the block at 1140-1145. No `gate_lock.take` match occurs on the CLI path.

Everything else re-derives (outputs in EVIDENCE.md)
- 78/120/568; renew refuses a waiting label at 582-586; fcntl.flock 291/300; lines 6 and 138 verbatim; gate_lock.py:44-45 quote.
- SLOT_MIN_SECONDS 116, MACHINE_MEASURING 117; neither measuring script references gate_lock.
- run.sh 317/325-326/329-353/335/343/347/350; mutation_table.py 1986/2001/2342; judge_batch.py 185/196/268/378, line 374 quote, `_take` 184-186 with no `wait=False`.
- prepr.sh slot-take 3142 (comment: the WHOLE run), needs-lease ask 344; derive_closures.sh 128; gate-scoping.md 28-33; audit-verify.js 192; prepare_baseline.sh 322 is a usage line it prints, not an invocation.
- take() 511-566: `while True:` at 531, `time.sleep(WAIT_POLL_SECS)` at 562, no deadline; `grep timeout|deadline|max_wait` returns only 895/1867/1934, all subprocess waits.
- closures 936.3 / 241.1; 2 x 936.3 = 1872.6 s = 31.2 min.
- roster command prints `208 ['tools/pr/prepr.sh', 'tests/gate_lock.py'] done [] []`; `grep -rn judge_batch .github/` prints nothing.
- Mutation proof and null control reproduce: ACCEPT / None / P999 None / DEFER refused / missing-file refused.

Ruling
The disposition is right and the record is honest. Arm 1 is already the mechanism — a bounded lease that refuses extension past a waiter, with flock held for the run — so no expiry can preempt an fcntl wait; arm 3 only lengthens a wedged holder's window; arm 2 would move measuring scripts into a loaded pool. The carried arm puts the bound on the waiter, where the unbounded path is (`take()`'s while-True loop), and exits through the named-unrun CI line. R10-PREPR-CAP owns `tests/gate_lock.py` and `tools/pr/prepr.sh`, stage `done`, carry `[]`; `tests/run.sh` is in no group, and the carry names it.

Could not establish
- The 38-minute wait and its timestamps: `/tmp/hpo-gate.lock/owner` is gone. The record declares it the orchestrator's measurement, not re-derived; `tools/audit/seat/update_pr.sh` exists, and 2 x 936.3 s plus tail/queueing is consistent, but that is arithmetic, not a second measurement.
- The proposal's own text (P206/V126): `proposals.md` is not a tree path (batches 33-35 cite it the same way); the record says the entry was not yet appended when the ruling was cut.
- "with a two-ordinary-script file it prints `slot`": the record names no file. It reproduces for a file whose scripts are multi-minute (entities.py + structure.py -> `slot`); two sub-69 s scripts answer `none`. Read existentially it holds; it is not a claim about every two-script file.

## Routing of the round-1 disposition item

The round-1 verdict (comment 6444053622) recorded a bullet on the batch's dispositions. At
this head the batch's one row carries its closing disposition as its `Verdict:` line
(`Verdict: ACCEPT narrowed -> a carry of R10-PREPR-CAP`, s6-batch38.md:6-7), and
`dev/governance/roles/proposal-triage.md` makes the row's Verdict the record's disposition;
no other disposition vocabulary exists in the tree.

Carry: dismissed: the record's ACCEPT verdict is its closing disposition (item ac7bb763)
