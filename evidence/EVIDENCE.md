# Evidence for the #2881 review at head 8cdfc0ce950393f3709387a98dc94713f389ed5a

All commands run in a detached worktree at `~/hpo-seats/r10s6/review-2881/wt`
checked out at `8cdfc0ce950393f3709387a98dc94713f389ed5a`, with
`PATH=$HOME/.local/state/hpo/venv-ci/bin:$PATH`.

## Head and diff scope

```
$ git ls-remote origin refs/pull/2881/head refs/heads/fix/triage-s6-batch38
8cdfc0ce950393f3709387a98dc94713f389ed5a	refs/heads/fix/triage-s6-batch38
8cdfc0ce950393f3709387a98dc94713f389ed5a	refs/pull/2881/head
$ gh pr view 2881 --json headRefOid,state
{"headRefOid":"8cdfc0ce950393f3709387a98dc94713f389ed5a","state":"OPEN"}
$ git rev-parse HEAD
8cdfc0ce950393f3709387a98dc94713f389ed5a
$ git merge-base origin/main HEAD
67178dc6a589cf95d2ce7cff36d8bbf17343e8dc
$ git diff --numstat $(git merge-base origin/main HEAD)...HEAD
1	0	dev/programme/delivery/2881.md
108	0	dev/programme/triage/s6-batch38.md
$ cat dev/programme/delivery/2881.md
- [#2881](https://github.com/tvofi/heatpump_optimizer/pull/2881) — **open**, triage: s6 batch 38 (P206) (R10-TRIAGE-B38)
$ git cat-file -t 524c1896b ; git log -1 --format='%H %ci %s' 524c1896b
commit
524c1896b6943b3da03d6cad61420ced31e14c9c 2026-10-27 09:50:00 +0100 Merge pull request #2874 ...
$ git merge-base --is-ancestor 524c1896b origin/main && echo YES
YES
```

## The narrowed `lock_dir` sentence (record :38-42)

Enumeration over each file's `gate_lock.take` / `_gate_lock.take` matches,
parsing each call to its matching close paren and reading `lock_dir=<val>`:

```
$ python3 -I -c "<balanced-paren scan of every _?gate_lock\.take\w*\( match>"
tests/gate_lock.py matches= 2 lock_dir values set= ['lock_dir']
  lines: [1855, 1923]
tests/entities.py matches= 36 lock_dir values set= ['d', 'd1', 'd2', 'lock']
  lines: [15395, 15417, 15433, 15444, 15450, 15458, 15466, 15476, 15478, 15521, 15525, 15531, 15535, 15571, 15639, 15661, 15699, 15710, 15716, 15844, 15847, 15852, 15856, 15858, 15874, 15877, 15882, 15885, 15919, 15959, 15988, 15992, 16028, 16050, 16070, 16073]
```

The record's lists are exactly those sets. The gate_lock.py sites are the
generated subprocess sources at 1855 and 1923 (`f"lock_dir = Path('{d3}')"` /
`Path('{d6}')`, each a TemporaryDirectory); every entities.py site is inside a
`_gl_*` self-test under `TemporaryDirectory()` (`d = Path(td) / "lock"`,
`d1 Path(td)/"one"`, `d2 Path(td)/"live"`, `lock Path(tds)/"lock"`).

CLI route: `_cmd_take` at 1008, `take(` at 1009, `lock_dir=args.lock_dir` at
1011; `--lock-dir` block at 1140-1145 with `default=DEFAULT_LOCK_DIR` at 1143.
No `gate_lock.take` string occurs on the CLI path, so "the CLI is not one of
those matches" holds.

## Prior-round findings

Round 1 (verdict commit 6dffb0365, head 1a7484a):
- F1 universal "the only scripts that take the lease": the current record's
  holder enumeration reproduces (see below); the universal is gone.
- F2 `s6-batch37.md` citation: `git ls-tree origin/main dev/programme/triage/`
  has no batch37; the current record says "One entry." and cites none.

Round 2 (verdict/2881 tip 8716d5cd3, head d606ade):
- F1 `needs_lease` arms:
```
$ awk 'NR>=918 && NR<=954 {printf "%d: %s\n", NR, $0}' tests/gate_lock.py   # lease returns at 938, 942, 944, 949
$ python3 tests/gate_lock.py needs-lease /nonexistent/scope.scope
lease
$ python3 tests/gate_lock.py needs-lease <file: tests/entities.py tests/structure.py>
slot
$ python3 tests/gate_lock.py needs-lease <file: tests/stress.py>
lease
$ python3 tests/gate_lock.py needs-lease <file: tests/golden.py tests/env_drift.py>
none
```
- F2 `wait=False`:
```
$ grep -rln --include='*.py' --include='*.sh' wait=False tools/ tests/
tests/gate_lock.py
tests/entities.py
```
  entities.py's sites are the `_gl_*` functions called at import (15487, 15492,
  15497, 15500, 15542, 15740, 15750, 15811, 15823, 15892, 15898, 15971, 16013,
  16085); no production caller passes it.
- F3 anchored pipeline:
```
$ grep -rn 'gate_lock\.py.*\(take\|auto-lease\|flock-wrap\|slot-take\|slot-auto-lease\)' --include='*.sh' --include='*.py' tools/ tests/ | grep -v '^tests/gate_lock.py:'
tools/pr/prepr.sh:3142: ... slot-take ...
tools/audit/judge_batch.py:39: ... (text)
tools/audit/judge_batch.py:45: ... (text)
tools/audit/prepare_baseline.sh:322: ... auto-lease ... (usage line in printed text)
tests/mutation_table.py:1987: ... (docstring text)
tests/derive_closures.sh:128: ... slot-take ...
tests/run.sh:343: ... slot-auto-lease ...
tests/run.sh:347: ... flock-wrap ...
tests/run.sh:350: ... auto-lease ...
tests/entities.py:38636: ... (text)
```
  Exactly the eight lines the record lists.
- F4 body Figures line: the body now reads "needs_lease (lines 937-949) answers
  `lease` for exactly four cases -- an empty scope argument (`MODE: FULL`), an
  unreadable scope file, a `MACHINE_MEASURING` script, or an unreadable table".

## Line and figure citations

```
$ grep -n '^LEASE_SECONDS\|^RENEW_REFUSED_RC\|^def renew' tests/gate_lock.py
78:LEASE_SECONDS = 1800
120:RENEW_REFUSED_RC = 75
568:def renew(
$ awk 'NR>=582 && NR<=586' tests/gate_lock.py
    waiting = [waiter.label for waiter in _queue(lock_dir) if waiter.label != label]
    if waiting:
        raise RenewRefused(
            f"renew refused: {waiting[0]} waits for the lease. Finish the current "
            f"stress.py run, release, and take again: you queue behind it")
$ grep -n 'fcntl.flock' tests/gate_lock.py
291:        fcntl.flock(fd, flags)
300:            fcntl.flock(fd, fcntl.LOCK_UN)
$ sed -n '6p' tests/gate_lock.py
for the duration of a gate run; the lease covers the window between commands
$ sed -n '138p' tests/gate_lock.py
# measures the machine and must not be extended past a waiter.
$ sed -n '44,45p' tests/gate_lock.py
That single lease serialises the commands that must run ALONE -- those that
measure the machine, so their numbers are comparable only with nothing else
$ grep -n '^SLOT_MIN_SECONDS\|^MACHINE_MEASURING' tests/gate_lock.py
116:SLOT_MIN_SECONDS = 69
117:MACHINE_MEASURING = ("tests/stress.py", "tests/harness_headers.py")
$ grep -n gate_lock tests/stress.py tests/harness_headers.py   # no output, exit 1
$ grep -n 'needs-lease' tests/run.sh
317:# The lease `gate_lock.py needs-lease` names decides each run: `lease` for the
335:  [ -z "$s" ] || answer=$("$PYTHON" tests/gate_lock.py needs-lease "$one" 2>&1)
$ sed -n '329,353p' tests/run.sh   # leased(): flock-wrap at 347, auto-lease at 350
$ sed -n '325,326p' tests/run.sh
# otherwise leave it held); auto-lease and flock-wrap both hold flock for the
# run, so a crash releases at once (#404). A `slot` run already inside a slot
$ grep -n '_leased_if_exclusive\|^LEASED' tests/mutation_table.py
1986:def _leased_if_exclusive(fn):
2001:@_leased_if_exclusive
2342:LEASED = ("tests/stress.py",)
$ grep -n 'gate_lock.take\|def renew\|lease.renew\|with Lease' tools/audit/judge_batch.py
185:        gate_lock.take(self.label, lock_dir=self.lock_dir, lease_seconds=self.seconds,
196:    def renew(self) -> None:
268:    lease.renew()
378:    with Lease(label, lock_dir, max(gate_lock.LEASE_SECONDS, timeout + 300)) as lease:
$ sed -n '374p' tools/audit/judge_batch.py
    """Every finding measured serially under one lease, in input order."""
$ sed -n '184,186p' tools/audit/judge_batch.py   # _take; no wait=False
$ grep -n 'needs-lease' tools/pr/prepr.sh
300:...  344:...  345:...  2108:...
$ sed -n '3142p' tools/pr/prepr.sh
  if python3 tests/gate_lock.py slot-take --label "$SLOT_LABEL" --owner-pid $$ >"$slot_stderr" 2>&1; then
$ sed -n '128p' tests/derive_closures.sh
elif MSG=$($PYTHON tests/gate_lock.py slot-take --label "derive-$$" --owner-pid $$ 2>&1); then
$ sed -n '28,33p' dev/governance/rules/gate-scoping.md   # take / renew / release
$ sed -n '192p' .claude/workflows/audit-verify.js
const lease = `python3 tests/gate_lock.py take --label judge-r${round}; renew between commands; release at the end -- never mkdir`
$ sed -n '322p' tools/audit/prepare_baseline.sh
  python3 tests/gate_lock.py auto-lease --label <your-label> -- python3 tests/stress.py
$ grep -n 'while True' tests/gate_lock.py   # 531 is take()'s loop
$ sed -n '562p' tests/gate_lock.py
            time.sleep(WAIT_POLL_SECS)
$ grep -n 'timeout\|deadline\|max_wait' tests/gate_lock.py
895:                proc.wait(timeout=10)
1867:    holder.wait(timeout=5)
1934:    holder.wait(timeout=5)
```

## Closures and arithmetic

```
$ python3 -c "import json; r=json.load(open('tests/closures.json'))['recorded']; print(r['tests/stress.py']['seconds'], r['tests/harness_headers.py']['seconds'])"
936.3 241.1
2 x 936.3 = 1872.6 s = 31.21 min
```

## Roster

```
$ python3 -c "import json;d=json.load(open('dev/programme/rosters/wave-r10-groups.json'));g=[x for x in d['groups'] if x['group']=='R10-PREPR-CAP'][0];print(len(d['groups']),g['files'],g['resume']['stage'],g['carry'],[x['group'] for x in d['groups'] if 'tests/run.sh' in x.get('files',[])])"
208 ['tools/pr/prepr.sh', 'tests/gate_lock.py'] done [] []
$ grep -rn judge_batch .github/    # no output, exit 1
```

## Mutation proof and null control

```
$ python3 -I -c "import sys; sys.path.insert(0,'tools/audit/seat'); import roster_edit as R; src=open('dev/programme/triage/s6-batch38.md').read(); cite=['triage: dev/programme/triage/s6-batch38.md#P206']; ..."
verdict: ACCEPT
refusal on committed file: None
P999 verdict: None
mutant verdict: DEFER
mutant refusal: dev/programme/triage/s6-batch38.md#P206 is not an ACCEPT ruling (DEFER)
missing-file refusal: the triage ruling dev/programme/triage/s6-batch38.md is not on the roster branch or origin/main
```

## Check runs

```
$ gh pr view 2881 --json statusCheckRollup -q '[.statusCheckRollup[].conclusion] | group_by(.) | map({(.[0] // "null"): length}) | add'
{"":7,"SKIPPED":8,"SUCCESS":22}
```
No conclusion is FAILURE or TIMED_OUT, so the body's "Red checks: none" holds.

## History named by the body

```
$ git diff --stat 34cd75bf1 6e9f4273c
 dev/programme/delivery/2881.md     |   1 +
 dev/programme/triage/s6-batch38.md | 108 ++++++
$ git merge-base origin/main 6e9f4273c
34cd75bf1fe506334611ba6c074c223317370e67
$ git log -1 --format='%H %P' 6e9f4273c
6e9f4273cc7f5b2e750c972c6dcd582b0a742e80 d797247fe22e8545b3c83b75012f07c2447804c3
$ git diff d797247fe 6e9f4273c -- dev/programme/triage/s6-batch38.md   # one line: the lock_dir correction
$ git diff --stat 1a7484a^ 1a7484a   # delivery/2881.md only
$ git diff --stat 524c1896b 51dd6d00b   # triage/s6-batch38.md only
```
The Head paragraph is generated by `tools/audit/seat/update_pr.sh:77-81`, which
names the run's final HEAD and the two merges that run performed; each named
sha exists and each merge appears in the branch history (6e9f4273c merged at
ce6531210, main 67178dc6a at 8cdfc0ce, 8d91422e at 856608896, main 34cd75bf1
at d606ade, d8e3db265 at 388b0ab5, and main 524c1896b is the base the branch
sits on).

## What could not be established

- The 38-minute wait: `/tmp/hpo-gate.lock/owner` is gone; the record declares it
  the orchestrator's measurement and does not re-derive it.
- P206/V126's own proposal text: `proposals.md` is not a tree path, and the
  record says the entry was not yet appended when the ruling was cut.
