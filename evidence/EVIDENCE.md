# Evidence for the r3 re-review of #2881

Head measured: d606ade6db7775606e3f31f8df45032a183c5e1a
Worktree: /Users/timmalmstrom/hpo-seats/r10s6/rev-2881-wt (detached at the head)
Merge base: 34cd75bf1fe506334611ba6c074c223317370e67 = origin/main at review time
(fetched 2026-10-27; `git rev-parse origin/main` printed it).

All commands below were run from the detached worktree at the head.

## 1. Diff scope

```
$ git log --oneline $(git merge-base origin/main HEAD)..HEAD
d606ade6d Merge remote-tracking branch 'origin/main' into fix/triage-s6-batch38
856608896 Merge commit '8d91422e7...' into fix/triage-s6-batch38
8d91422e7 triage: s6 batch 38 -- narrow the gate_lock take claim to its matches
388b0ab5c Merge commit 'd8e3db265...' into fix/triage-s6-batch38
d8e3db265 triage: enumerate the gate-lease holders in batch 38, not a false universal
1a7484a36 record: the delivery row for #2881
51dd6d00b triage: batch 38 (P206) ruling on the gate-lease wait bound

$ git diff --stat $(git merge-base origin/main HEAD)...HEAD
 dev/programme/delivery/2881.md     |   1 +
 dev/programme/triage/s6-batch38.md | 114 +++++++++++++++++++++++++++++++++++++
 2 files changed, 115 insertions(+)
```

Two files: the batch and the PR's own delivery row (required by
delivery-status-tracking; one row: `- [#2881](...) -- **open**, triage: s6 batch 38 (P206) (R10-TRIAGE-B38)`).
Nothing outside the batch's seam.

## 2. The repaired sentence -- HOLDS

`dev/programme/triage/s6-batch38.md:42-46`:

> The `gate_lock.take`/`_gate_lock.take` matches in `tests/gate_lock.py`
> and `tests/entities.py` are self-tests against a temp `lock_dir=d`; the CLI is not
> one of those matches -- `_cmd_take` (line 1008) calls `take(args.label,
> lock_dir=args.lock_dir, ...)` with `--lock-dir` defaulting to `DEFAULT_LOCK_DIR`
> (lines 1140-1145), and that is the by-hand route named above.

Verified:
- `grep -n 'gate_lock\.take\|_gate_lock\.take' tests/gate_lock.py` -> 1855, 1923, both
  inside `holder_script` strings run as subprocesses against `Path('<temp d3/d6>')`.
- `grep -rn 'gate_lock\.take\|_gate_lock\.take' tests/entities.py` -> 15395..16073, all
  inside `_gl_*` self-test functions under `TemporaryDirectory` (`lock_dir=d/d1/d2/lock`);
  they execute at import (`_gl_ok, _gl_detail = _gl_crash_then_successor()` at 15500).
- `sed -n '1008,1013p' tests/gate_lock.py`: `def _cmd_take(...): owner = take(args.label,
  lock_dir=args.lock_dir, lease_seconds=args.lease_seconds, wait=not args.no_wait, ...)`.
- `sed -n '1139,1145p' tests/gate_lock.py`: `p.add_argument("--lock-dir", type=Path,
  default=DEFAULT_LOCK_DIR, ...)` and `DEFAULT_LOCK_DIR` = `/tmp/hpo-gate.lock`.
- `_cmd_take` does not match either literal pattern; the distinction is true.

RESULT: the sentence that a prior review blocked is now true.

## 3. Findings

### F1 (blocking) -- needs_lease "only" enumeration is one arm short

`dev/programme/triage/s6-batch38.md:76-77`:

> `needs_lease` answers `lease` only for `MACHINE_MEASURING`, an empty scope, or
> an unreadable table (lines 918-954).

`tests/gate_lock.py:918-954` has four lease-returning arms:
- 937-938 `if not scope_run: return "lease"` (empty scope) -- listed;
- 940-942 `except OSError: return "lease"` (unreadable scope file) -- NOT listed;
- 943-944 `if any(name in MACHINE_MEASURING ...): return "lease"` -- listed;
- 946-949 `except (OSError, ValueError): return "lease"` (unreadable closures table) -- listed.

Command (the file's own cited form):
```
$ python3 tests/gate_lock.py needs-lease /nonexistent/scope.scope
lease
$ python3 tests/gate_lock.py needs-lease ''
lease
$ python3 tests/gate_lock.py needs-lease scope-two-big.scope   # entities.py + features.py
slot
$ python3 tests/gate_lock.py needs-lease scope-stress.scope    # tests/stress.py
lease
```
(see needs_lease-perturbation.txt; scope-two-big.scope and scope-stress.scope are in this
directory, and reproduce-needs-lease.sh re-runs the block from the head worktree)

Metric: 1 of 4 lease-returning arms unlisted; the cited line range contains the omitted arm.
Perturbation: point the scope at a path that cannot be read; the answer is `lease`, which
the enumeration does not contain. The file therefore contradicts the very lines it cites.

### F2 (blocking) -- "only gate_lock.py's own self-tests pass it" is location-false

`dev/programme/triage/s6-batch38.md:81-82`:

> `wait=False` raises instead, and only `gate_lock.py`'s own self-tests pass it.

`grep -rn 'wait=False' --include='*.py' --include='*.sh' --include='*.js' --include='*.mjs' .`
gives, as take()/take_slot() arguments, tests/gate_lock.py:1272..1939 AND
tests/entities.py:15395..16073 (46 hits); the only other `wait=False` hits are
`pool.shutdown(wait=False)` in three unrelated harnesses. The gate_lock self-tests in
tests/entities.py execute at import (15500, 15892, 16085). The batch's own repaired
sentence (line 42-43) names `tests/entities.py` as holding gate_lock self-tests, so the
statement contradicts its own file.

Metric: 2 files hold the wait=False take callers, not 1.
Perturbation: run the entities.py gate_lock block; `_gate_lock.take(..., wait=False)`
executes. Substance that holds: no production path passes `wait=False`.

### F3 (blocking) -- the cited supporting grep prints nothing

`dev/programme/triage/s6-batch38.md:49-52`:

> `grep -rn 'gate_lock\.py.*\(take\|auto-lease\|flock-wrap\|slot-take\|slot-auto-lease\)' --include='*.sh' --include='*.py' tools/ tests/`
> piped to `grep -v gate_lock.py`, which adds `mutation_table.py`, `prepr.sh`, `run.sh` and
> `derive_closures.sh`, plus `prepare_baseline.sh`, ...

Exact command (see grep-pipeline.txt):
```
$ grep -rn 'gate_lock\.py.*\(take\|auto-lease\|flock-wrap\|slot-take\|slot-auto-lease\)' \
    --include='*.sh' --include='*.py' tools/ tests/ | grep -v gate_lock.py
(no output; exit 1)
```
Every line the first grep produces contains the literal `gate_lock.py`, so
`grep -v gate_lock.py` removes all of them. Without the pipe the same grep prints
prepr.sh:3142, prepare_baseline.sh:322, judge_batch.py:39/45, mutation_table.py:1987,
derive_closures.sh:128, run.sh:343/347/350, entities.py:38636 -- the substantive set the
sentence lists (plus two docstring mentions it omits). The filter is over-broad: it should
be anchored to the file (`grep -v '^tests/gate_lock.py:'`) or dropped.

Metric: cited pipeline 0 lines vs 5 files claimed; un-piped grep reproduces the 5.
Perturbation: run the sentence's command as written; it cannot produce the output claimed.

### F4 (finding, same class, in the body) -- the body's Figures compress the "only" further

The live PR body (fetched from the API; byte-identical to the state file but for a trailing
newline) `## Figures` line 38:

> ... `needs_lease` (lines 918-954) answers `lease` only for `MACHINE_MEASURING`.

As an answer-set claim this is false: `needs_lease('')`, `needs_lease('/nonexistent')`, and
an unreadable closures table all answer `lease` (three arms beyond MACHINE_MEASURING). It is
true only if silently read as "classifies as `lease` only scripts in MACHINE_MEASURING" -- a
qualifier the sentence does not state and the batch's own fuller enumeration shows was not
the intended meaning. `preflight.sh:109-111` states the rule the body is held to: "Unqualified
quantifiers. Each needs the whole set enumerated, not sampled."

## 4. Body Figures and Red checks -- the rest holds

- closures figures: 936.3 s / 241.1 s --
  `python3 -c "import json; r=json.load(open('tests/closures.json'))['recorded']; print(r['tests/stress.py']['seconds'], r['tests/harness_headers.py']['seconds'])"`
  -> `936.3 241.1`; 2 x 936.3 = 1872.6 s = 31.21 min.
- LEASE_SECONDS = 1800 at 78; RENEW_REFUSED_RC = 75 at 120 and dispatched at 1973-1975;
  renew() at 568; SLOT_MIN_SECONDS = 69 at 116; MACHINE_MEASURING at 117.
- take() at 511-566 (the sed range 511-567 ends at `ticket.unlink` line 565); `while True`
  with `time.sleep(WAIT_POLL_SECS)` and no deadline. `grep -n 'timeout\|deadline\|max_wait'`
  -> 895, 1867, 1934 only, all subprocess waits.
- run.sh: comment 317, leased() 329-353, needs-lease 335, slot-auto-lease 343, flock-wrap 347,
  auto-lease 350, slot-auto-lease/auto-lease are the only lease mechanics in the file.
- mutation_table.py: _leased_if_exclusive 1986-1998, LEASED at 2342 = ("tests/stress.py",).
- judge_batch.py: gate_lock.take at 185, Lease entered at 378 with
  `max(gate_lock.LEASE_SECONDS, timeout + 300)`, renew at 196-198 called from measure() at 268.
- prepr.sh: slot-take 3142; needs-lease asked at 344 (the only such call; 2108 is a self-test
  of it); stress.py is left to CI at 2108.
- derive_closures.sh: slot-take 128.
- gate-scoping.md:28-33 = the take/renew/release block; audit-verify.js:192 = the judge lease line.
- prepare_baseline.sh:322 is a usage line inside the BASELINE.md heredoc (`cat > ... <<MD`),
  not an invocation -- the file's claim holds.
- Roster: 208 groups; R10-PREPR-CAP files [tools/pr/prepr.sh, tests/gate_lock.py],
  resume.stage "done", carry []; no group's `files` names tests/run.sh.
- `grep -rn judge_batch .github/` -> empty (rc 1).
- stress.py / harness_headers.py: `grep -n 'gate_lock\|auto-lease\|flock-wrap\|take('` -> no
  hits (rc 1), so "neither takes the lease itself" holds.
- Mutation proof and null control reproduced at the head (roster_edit.triage_refusal):
  P206 verdict ACCEPT; refusal None; P999 verdict None; mutant DEFER ->
  "dev/programme/triage/s6-batch38.md#P206 is not an ACCEPT ruling (DEFER)"; missing file ->
  "the triage ruling dev/programme/triage/s6-batch38.md is not on the roster branch or origin/main".
- Red checks "none": head check-runs (38) = 26 success, 10 skipped, 3 in_progress/null
  (coverage, governance / instrument-self-tests, prelude), 0 failure/cancelled/timed_out
  (check-runs.txt).

## 5. Could not establish

- The 38-minute wait: `/tmp/hpo-gate.lock/owner` no longer exists at this head, and the
  batch declares it "The orchestrator's measurement, not re-derived here." Its arithmetic
  (2 x 936.3 s = 31.2 min; expires_at = taken + 30 min) is consistent but not re-derivable.
- `dev/programme/triage/s6-batch37.md` (cited line 3) is absent at the head and on origin/main
  (`git cat-file -e` fails); it exists only on unmerged `fix/triage-s6-batch37` (a63c6bfd).
  The r2 fix brief records the orchestrator's disposition -- "which resolves by merge order" --
  so this is noted, not re-raised as a new finding.
- "Every holder above is a measurement context": settled for run.sh, mutation_table and
  judge_batch by enumeration; for the by-hand route it is true by gate-scoping.md's definition
  of the lease (the measuring lock), not by an enumerated runtime instance.
