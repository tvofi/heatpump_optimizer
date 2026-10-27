# Proposal triage, session s7, batch 38 (P206)

One entry. Facts read at origin/main `524c1896b` on 2026-10-27.

## P206: one seat's measurements hold the whole push lane for half an hour (V126)
Verdict: ACCEPT narrowed -> a carry of **R10-PREPR-CAP** (it owns `tools/pr/prepr.sh` and
`tests/gate_lock.py`, `stage` `done` -- the roster command under "Roster" below). The proposal asked for a cost/benefit
ruling on three arms; measured against the tree, the holder-side bound it names in arm 1 is
already the mechanism, and the bound that can still be moved is on the **waiter**. So the
carried arm keeps the proposal's goal -- one seat does not acquire a push lane for half an hour
-- and puts the bound where it can act: past a bound, the waiter takes the exit the rule already
sanctions (`SKIP: <script> ... left to CI, named unrun`) instead of blocking unbounded.
- Arm 1 as proposed (bound the lease and renew it) is REJECTED because it already exists and
  cannot act on the observed wait: `grep -n '^LEASE_SECONDS\|^RENEW_REFUSED_RC\|^def renew' tests/gate_lock.py`
  prints 78/120/568; `renew()` refuses while another label waits (585-586);
  `grep -n 'fcntl.flock' tests/gate_lock.py` prints 291/300; `sed -n '6p' tests/gate_lock.py`
  prints "for the duration of a gate run; the lease covers the window between commands", so an
  expiry cannot preempt the wait below and shortening the lease would not touch it.
- Arm 2 (a scoped gate under a heavy slot instead of the lease) is REJECTED on a measured fact:
  the scripts it covers measure the machine -- `tests/gate_lock.py:44-45` states the lease
  "serialises the commands that must run ALONE -- those that measure the machine";
  `grep -n '^SLOT_MIN_SECONDS\|^MACHINE_MEASURING' tests/gate_lock.py` prints `116:SLOT_MIN_SECONDS = 69`
  and `117:MACHINE_MEASURING = ("tests/stress.py", "tests/harness_headers.py")`. Running them in
  a four-slot pool would measure load, not the tree; the multi-minute non-measuring side is
  already a slot, and neither measuring script takes the lease itself -- the holders are:
    - `tests/run.sh`'s `leased()` (329-353): `flock-wrap` (347) under a seat's label, else
      `auto-lease` (350) -- the grep below prints both -- around each `lease` script; it asks
      `needs-lease` at 335 (`grep -n 'needs-lease' tests/run.sh` prints 317/335).
    - `tests/mutation_table.py`'s `_leased_if_exclusive` (1986) `auto-lease` off CI around
      `tests/stress.py` (`LEASED`, 2342) -- `grep -n '_leased_if_exclusive\|^LEASED' tests/mutation_table.py` prints 1986/2001/2342;
    - `tools/audit/judge_batch.py`'s `Lease` (`gate_lock.take` 185, entered 378), held across a
      batch, renewed per command (196-198, called 268) -- `grep -n 'gate_lock.take\|def renew\|lease.renew\|with Lease' tools/audit/judge_batch.py` prints 185/196/268/378;
    - by hand: `take`/`renew`/`release` (`sed -n '28,33p' dev/governance/rules/gate-scoping.md`);
      audit prompts send a seat down it (`sed -n '192p' .claude/workflows/audit-verify.js`).
  A SLOT, not this lease, and so outside the arm: `tools/pr/prepr.sh`'s whole-run `slot-take`
  (line 3142; line 344 only *asks* `needs-lease` -- `grep -n 'needs-lease' tools/pr/prepr.sh`),
  `tests/run.sh`'s `slot-auto-lease` (line 343), `tests/derive_closures.sh`'s `slot-take`
  (line 128), all printed by the grep below. The `gate_lock.take`/`_gate_lock.take` matches in `tests/gate_lock.py`
  and `tests/entities.py` are self-tests against temporary lock dirs (`lock_dir=d`, `d1`, `d2` and `lock` in `tests/entities.py`; `lock_dir=lock_dir` in `tests/gate_lock.py`'s generated subprocess source); the CLI is not
  one of those matches -- `_cmd_take` (line 1008) calls `take(args.label,
  lock_dir=args.lock_dir, ...)` with `--lock-dir` defaulting to `DEFAULT_LOCK_DIR`
  (lines 1140-1145), and that is the by-hand route named above. Command: the importer grep
  `grep -rn 'gate_lock\.take\|gate_lock import\|from gate_lock' tools/ tests/ .claude/ | grep -v '\.pyc'`
  finds `judge_batch.py` but not the CLI route, so it is completed by
  `grep -rn 'gate_lock\.py.*\(take\|auto-lease\|flock-wrap\|slot-take\|slot-auto-lease\)' --include='*.sh' --include='*.py' tools/ tests/`
  piped to `grep -v '^tests/gate_lock.py:'`, which prints invocations at `prepr.sh` 3142, `run.sh` 343/347/350,
  `derive_closures.sh` 128, plus text mentions at `mutation_table.py` 1987, `prepare_baseline.sh` 322
  (a usage line it prints to a seat), `judge_batch.py` 39/45 and `entities.py` 38636.
- Arm 3 (longer leases) is REJECTED as proposed, and for a second reason: a longer lease also
  lengthens a wedged by-hand holder's window between commands.

Source: orch s7, 2026-10-27, relayed to this seat with its measurement done; the
`proposals.md` entry was not yet appended when this ruling was cut.

Instances: one measured wait, and the tree's recordings account for its length.
- The wait: `update_pr.sh fix/r10-cop-partload` (pid 62391) sat 38 minutes as an fcntl waiter
  while the lease passed from `fix-2854-stress2` (released 11:59:49Z) to
  `r10-train-overlap-grade` (taken 11:59:52Z, `expires_at` 12:29:52Z); the owner file still
  named that label when read at 12:13Z (`cat /tmp/hpo-gate.lock/owner`). The orchestrator's
  measurement, not re-derived here.
- Why 38 minutes: two consecutive legitimate measurement runs. `tests/closures.json`'s
  `recorded` table gives `tests/stress.py` at 936.3 s and `tests/harness_headers.py` at 241.1 s;
  2 x 936.3 s is 31.2 minutes, and the first run's tail plus queueing reaches 38. Command:
  `python3 -c "import json; r=json.load(open('tests/closures.json'))['recorded']; print(r['tests/stress.py']['seconds'], r['tests/harness_headers.py']['seconds'])"`
  prints `936.3 241.1`.
- The lease is bounded and refuses extension: `grep -n '^LEASE_SECONDS\|^RENEW_REFUSED_RC\|^def renew' tests/gate_lock.py` prints 78/120/568, and
  `sed -n '138p' tests/gate_lock.py` prints "measures the machine and must not be extended past a waiter".
- `tests/run.sh` takes the lease per script and only for measuring ones: `leased()` asks
  `needs-lease` about the single script it is about to run (comment at line 317, function
  329-353), and `needs_lease` answers `lease` for exactly four cases: an empty scope argument
  (`MODE: FULL`), an unreadable scope file, a `MACHINE_MEASURING` script, or an unreadable table
  (lines 937-949). Measured: `python3 tests/gate_lock.py needs-lease /nonexistent/scope.scope`
  prints `lease`; with a two-ordinary-script file it prints `slot`, with `tests/stress.py` `lease`.
- The waiter's wait is unbounded: `take()`'s loop is `while True: ... time.sleep(WAIT_POLL_SECS)`
  with no deadline (lines 511-566); `wait=False` raises instead, and only self-tests pass it, in
  `tests/gate_lock.py` and `tests/entities.py` (`grep -rln --include='*.py' --include='*.sh' wait=False tools/ tests/`).
  `grep -n 'timeout\|deadline\|max_wait' tests/gate_lock.py` finds only subprocess-cleanup waits,
  none in the ticket loop. `tests/run.sh`'s comment above `leased()` states the hold: "auto-lease
  and flock-wrap both hold flock for the run, so a crash releases at once (#404)" (lines 325-326).
- Roster: `python3 -c "import json;d=json.load(open('dev/programme/rosters/wave-r10-groups.json'));g=[x for x in d['groups'] if x['group']=='R10-PREPR-CAP'][0];print(len(d['groups']),g['files'],g['resume']['stage'],g['carry'],[x['group'] for x in d['groups'] if 'tests/run.sh' in x.get('files',[])])"`
  prints `208 ['tools/pr/prepr.sh', 'tests/gate_lock.py'] done [] []`, so `R10-PREPR-CAP` owns both
  files, stage `done`, no carry, and `tests/run.sh` is in no group's `files`; the carry names it.

Cost: about 15-20 lines in `tests/gate_lock.py` -- a deadline in `take()`'s wait loop, named
by the caller as the awaited script's recorded duration and left off when the caller names
none, exiting with a distinct code plus one line naming the wait and its bound -- and a
four-line case arm in `tests/run.sh`'s `leased()` mapping that code to the existing skip
line, so the lane's manifest records a named unrun rather than a pass. Two
self-test arms: one waiter past the bound exits with the code and the line, one within it still
runs. Standing cost on the uncontended path, which is the common case, is one clock read per
poll and no new branch: no new file, no CI minutes, no GitHub call.

Binding: the bound must be at least the awaited script's recorded duration (936.3 s for
`stress.py`, 241.1 s for `harness_headers.py`), or the arm skips a measurement the waiter would
have completed and turns a contended-but-legitimate local gate into a skip; the skip must be the
existing named-unrun line, never a silent pass, so no lane reads green without stress.py; it
must apply only to scripts `needs_lease` classifies `lease`, because a `slot` waiter already
shares the four-slot pool and its constraint is CPU, not comparability; an uncontended run must
take no new branch (the null control); neither `LEASE_SECONDS` nor `renew()`'s refusal
changes with this carry, because the lease period is not the defect; and a `judge_batch`
holder must keep waiting -- `sed -n '374p' tools/audit/judge_batch.py` prints "Every finding
measured serially under one lease", and `Lease._take()` (184) passes no `wait=False`
(`sed -n '184,186p' tools/audit/judge_batch.py`), so the opt-in default leaves its wait unbounded; the skip exit is mapped only by
`tests/run.sh`'s `leased()`, and a batch that took it would lose a measurement that no
workflow re-runs (`grep -rn judge_batch .github/` is empty). What would overturn the arm: a
waiter bound already present somewhere this reading did not reach, or a measured `stress.py`
cost far below the 936.3 s recording, which would move the bound figure but not the arm's
shape.
