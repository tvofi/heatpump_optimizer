Fix review: blocked 1a7484a36d0e797d73f4c1bca3a619d4bf6b6dfc claim: the arm-2 universal "the only scripts that take the lease" does not reproduce (tools/audit/judge_batch.py holds the exclusive lease across a batch), and s6-batch37.md does not resolve at this head
bus-nonce: 0145ab2347c1dd7bcd13314ee83bd966

Measured head: 1a7484a36d0e797d73f4c1bca3a619d4bf6b6dfc (git ls-remote refs/heads/fix/triage-s6-batch38, re-read immediately before this file was written).
Merge base: 524c1896b6943b3da03d6cad61420ced31e14c9c = origin/main at review time = the batch's stated facts SHA.
Diff: 2 files, +82 (dev/programme/triage/s6-batch38.md +81, dev/programme/delivery/2881.md +1). The dispatch brief's +62/+61 does not match the head; I trust git.

See EVIDENCE.md for every command and RESULT line.

Findings
F1 (blocking). `s6-batch38.md:22-23`: "the only scripts that take the lease are `tests/stress.py` and
`tests/harness_headers.py`". False at this head. `tools/audit/judge_batch.py` (live: referenced by
`.claude/workflows/audit-verify.js`, `tests/closure.py`, `tests/closures.json`) imports `gate_lock` and
calls `gate_lock.take(...)` in `Lease._take` (line 185), holding the exclusive lease across a whole
batch of commands and renewing per command. That is a third holder and it is not a `MACHINE_MEASURING`
script. `tools/pr/prepr.sh:344` is a second route through `needs-lease`. The arrow's conclusion (a
heavy slot would let measuring work share a loaded box) survives because judge_batch's commands are
measurements, but the sentence that carries it is a universal the tree contradicts, and the batch's
own binding ("the bound must be at least the awaited script's recorded duration when the caller names
one") has no answer for a judge_batch holder.

F2 (blocking, smaller). `s6-batch38.md:3` cites `s6-batch37.md`. It does not exist at this head
(`git cat-file -e HEAD:dev/programme/triage/s6-batch37.md` fails; main's triage dir ends at
s6-batch35.md). It exists on `fix/triage-s6-batch37` at a63c6bfd with "batch 37 (P205)", so the
citation is true of an unmerged branch, not of the tree the batch claims. No tag is cited, and
brief-citations.md resolves a path only in the tree or at a cited tag. If #2881 merges ahead of the
sibling, main carries "continues after s6-batch37.md" with no such file.

Everything else holds
- Paths named by the batch: 4 of 5 resolve at the head (tools/pr/prepr.sh, tests/gate_lock.py,
  tests/closures.json, tests/run.sh). `s6-batch37.md` does not (F2). `proposals.md` is an out-of-tree
  s6 source document, named the same way by batches 33-35, and is not a tree path.
- Figures that reproduce exactly at this head: stress.py 936.3 s and harness_headers.py 241.1 s
  (closures.json `recorded`); 2 x 936.3 s = 1872.6 s = 31.21 min; LEASE_SECONDS = 1800 (line 78);
  RENEW_REFUSED_RC = 75 (line 120); renew() at line 568; SLOT_MIN_SECONDS = 69; take() 511-566 with the
  unbounded `while True` + `time.sleep(WAIT_POLL_SECS)` at 562; needs_lease 918-954; the docstring
  sentence at 57-59 verbatim, including "since"; the renew refusal text verbatim; the run.sh comment at
  325-326; leased() asking needs-lease at 335; `needs-lease` returns slot for two ordinary scripts and
  lease for stress.py / harness_headers.py (re-run); 208 roster groups; tests/run.sh in no group's
  `files`; R10-PREPR-CAP owns tools/pr/prepr.sh and tests/gate_lock.py, stage done, carry [].
  `grep -n 'timeout|deadline|max_wait'` does return only subprocess/thread cleanup waits (895, 1867, 1934).
- Figures that do not reproduce: F1's count of lease holders. Cite: 2 -> tree: 3+.
- The 38-minute wait, its pid, and its timestamps are the orchestrator's external measurement; the
  batch says so ("not re-derived here"). The stated accounting reaches 31.2 min from the recordings and
  bridges ~6.8 min with "the first run's tail plus queueing", for which no command is given. Disclosed,
  so recorded as a bounded gap rather than a defect.
- Dispositions: the batch has no closing disposition (fixed / not-a-defect / out-of-scope / deferred).
  Its one row is ACCEPT-narrowed -> a carry; its evidence is in this batch and in the tree (above).
- Delivery row: dev/programme/delivery/2881.md is new, one line, right PR number, names the batch, state
  **open** matching the PR. delivery-status-tracking.md's shape is met.
- P/V numbering: continuous. In tree batch35 = P199-P203 / V119-V123; branch batch36 = P204 / V124;
  branch batch37 = P205 / V125; this = P206 / V126. The orchestrator's triage-STATE.md says next is P207.
- Lint: `node tools/policy/brief_lint.mjs` exits 0. dev/programme/triage/ is not among its inputs
  (wave-*-groups.json briefs, dev/programme/carries/carry-<N>.json), so it does not lint this document;
  its own output is "ROSTER ok ... CARRY ok ...", with the 10 errors printed being its fixtures.
- Body checks: head named in the body is 1a7484a3 and is the head; 51dd6d00 is the authored head and the
  row commit adds only delivery/2881.md (measured). "Red checks: none" holds: all 55 runs on the head are
  success or skipped; the earlier commit's 27 runs contain 6 cancellations and no failure.
  The body's mutation proof and null control re-execute exactly: P206 verdict ACCEPT, refusal None,
  mutant DEFER -> "dev/programme/triage/s6-batch38.md#P206 is not an ACCEPT ruling (DEFER)", P999 -> None.
- Forward-carry: P206 is routed in prose to R10-PREPR-CAP (stage done) and the orchestrator's
  roster-queue-s7.txt carries the append-carry line (b38-P206.txt). It is not yet on the roster branch,
  which matches the P196 precedent (batch 34 landed 10:14, roster append 15:47), so not blocked.
- `git merge-tree --write-tree origin/main <head>` exits 0: no conflict. VERSION, the manifest and
  RELEASE_NOTES.md are untouched (2-file diff). No budget, ledger or golden figure moves.

Could not establish
- Whether any proposal was dropped from the batch: its source register (`proposals.md`, V126) is out of
  tree and the batch says the entry "was not yet appended". Only the P/V continuity above is checkable.
- The 38-minute wait itself: no in-tree harness, no log to a retained path.
