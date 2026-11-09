HOTFIX R10-HOTFIX-SELFTEST-SCOPE-HANG: `governance / instrument-self-tests` was cancelled at its 60-minute job timeout on main's push runs 42623897209 (job 129183022595, main 631ac4df) and 42606134873.

Cause, from the job log and the code:

- **Step 5 failed in 0 s** with `sudo: The "no new privileges" flag is set, which prevents sudo from running as root.` `tools/ci/selftest_step.sh` traced every step except `launch`, so the install step's `sudo` ran under `strace --seccomp-bpf`, which sets no_new_privs. strace itself was already on the runner (every later step ran traced; the scope self-test printed `skip the recorder end to end: ... this run is itself traced`).
- **`launch` had no `if:`**, so step 5's failure skipped it, and the five `bg_wait` steps each failed on `$RUNNER_TEMP/bg/lib.sh: No such file or directory`.
- **Step 113 (`drift`) never ended.** The wrapper traced it too, so `selftest_scope.py check` folded every step's trace while itself under ptrace. `fold_trace` called `os.path.realpath` once per syscall line, and each of its lstats was a ptrace stop. `fold` also silently skipped a waited-on bg trace that was missing (all five, here) and accepted an empty trace as a whole measurement.
- `record`, the local path that took the "about 34 minutes" figure in the job's comment, skips `strace` and `drift` by its own list. So the traced `drift` path ran for the first time on main.

The fix:
- **`selftest_step.sh`** runs the five ungated steps untraced. Its `UNTRACED` list is held equal to `UNGATED` by the self-test. It traces with `-q` rather than `-qq`, so every process's exit line stays in the trace. With `SELFTEST_TRACE` set and no strace on PATH, it runs the step untraced and says so.
- **`fold`** streams each trace, memoises `realpath`, and returns its refusals. `check` and `record` refuse, by name:
  - `MISSING`: a waited-on bg trace;
  - `EMPTY`: no traced call;
  - `PARTIAL`: the first process's exit line is absent.
- **`launch`** runs under `!cancelled()`.
- **`tools/ci/selftest_scope_mutants.sh`** is wired as step `selftest-scope-mutants`, and its closure is recorded with `selftest_scope.py record --step selftest-scope-mutants`.

Alternatives considered and not taken:
- Gate `drift` on `steps.strace.outcome`: it skips the measurement silently, and leaves the traced fold in place.
- A wall-clock cap inside `check`: it bounds a symptom; the fold untraced is bounded by its input.
- Keep `-qq` and detect partial traces by a missing trailing newline: strace writes whole lines, so a killed tracer can still leave one.

Root cause (defect-root-cause.md, second trigger; `instrument-self-tests` is not in `merge_train.py owed-reds`, answered because the brief owes it). The cheaper detector exists now: the self-test's wrapper checks run the wrapper over stub PATHs, with no strace and no ptrace. They run inside the `selftest-scope` step on every pull request whose diff reaches the wrapper; the wrapper is a GATE_FILE, so every step runs. Standing cost: the `selftest-scope-mutants` step, timed below, on each pull request that selects it and on each push to main. Process state (c): the pre-merge measurement, `record`, was run and passed, but it replays the steps through a different skip list than CI's wrapper, so it never ran the traced `drift` and `strace` steps. The countermeasure is the `UNTRACED == UNGATED` check plus the behavioural stub checks, demonstrated below red on the incident's wrapper and green at the head. The analysis document is the root-cause seat's.

## Head

4f167ab4b1526378e2ce8d28187a3d4964d42a36 (measured head; no code change since the red runs), merge base 7bdc8aa2ec92934b96b77d3fd8d331b1c23d3769.

## Mutation proof

`sh tools/ci/selftest_scope_mutants.sh --self-test` applies one mutant per new rule; the self-test refuses every one. Excerpt, failing check names per mutant:

- a missing bg trace skipped: `check: missing trace bg-slow.trace is refused`
- an empty trace read whole: `record: an empty trace fails the record`, `check: empty trace ... is refused` (x3)
- a partial trace read whole: `check: partial trace bg-slow.trace is refused` (x2)
- a signal death read as partial: `fold: a first process killed by a signal ended its trace (null control: whole)`
- check drops the trace refusals: the six `check: ... trace ... is refused` checks
- record passes over a broken trace: `record: an empty trace fails the record, naming it`
- only launch untraced (the incident's wrapper): `wrapper: the ungated steps [...] run untraced`
- no strace exec'd anyway: `wrapper: no strace on PATH runs the step and the --as command untraced, saying so`
- exit lines suppressed (-qq): `wrapper: a gated step runs under strace -q ...`, `wrapper: --as NAME ...`, and both `record:` checks (real strace: a `-qq` trace reads PARTIAL)
- drift traced again: `wrapper: the ungated steps [...] run untraced`, `wrapper: its UNTRACED list is UNGATED`

It ends `SELFTEST-SCOPE MUTANTS: every mutant refused`. It was also run under `strace -f -q --seccomp-bpf` (CI's traced condition, where the real-strace recorder checks skip), and every mutant was still refused: the record-broken check uses a stub tracer, not ptrace.

## Null control

- The head's own self-test: `selftest_scope self-test: 103 checks, 0 failed`.
- The base wrapper under the head's self-test (`--wrapper` = `git show origin/main:tools/ci/selftest_step.sh`): 7 failed. These are the five wrapper checks plus both real-strace `record` checks, whose `-qq` traces read PARTIAL.
- A trace whose first process was `killed by SIGKILL` folds with no refusal, so the PARTIAL rule does not refuse a step that ended by a signal.

## Figures

- head self-test, 103 checks, 0 failed: `python3 -I tools/ci/selftest_scope.py --self-test`
- base wrapper, 7 of 103 failed: `git show origin/main:tools/ci/selftest_step.sh > $T/s.sh && python3 -I tools/ci/selftest_scope.py --self-test --wrapper $T/s.sh`
- 10 mutants, every one refused: `sh tools/ci/selftest_scope_mutants.sh --self-test`. It ran in 8.2 s wall untraced and 12.9 s under `record`, which is the standing cost above.
- fold timing on one trace: 70504 lines, the self-test's own `%file` trace concatenated 8 times. Head 0.4 s untraced and 0.6 s traced; base 0.7 s untraced and 4.4 s traced. Commands: `strace -f -q -y --seccomp-bpf -e trace=%file -o $T/x.trace python3 -I tools/ci/selftest_scope.py --self-test`, then `fold_trace` of it timed by `python3 -I -c` against the head's and `origin/main`'s `tools/ci/selftest_scope.py`, bare and under `strace -f -q --seccomp-bpf -e trace=%file -o /dev/null`. The rule: the traced/untraced ratio is the per-line ptrace cost the `drift` step paid, and the head removes both the tracer (UNTRACED) and most of the lstats (the realpath memo, identical output).
- class seams, steps of the job with no `if:`: `python3 -I -c 'import sys; sys.path.insert(0,"tools/ci"); import selftest_scope as s; print([x.id or x.name for x in s.workflow_steps() if not x.cond])'`. At head this prints `['', '', 'scope']` (checkout, setup-node, scope: each precedes any step that can fail, so already guarded by position). Over the base workflow it also printed `launch`, which this diff closes.
- class seams, steps traced that no table entry reads: `UNGATED` against the wrapper's `UNTRACED`, held equal by `wrapper: its UNTRACED list is UNGATED`. All five are closed in this diff.
- `selftest_scope static`: 107 gated steps, 0 problems: `python3 -I tools/ci/selftest_scope.py static`
- `selftest_wiring`: 0 unwired: `python3 -I tools/audit/seat/selftest_wiring.py --check`
- STRUCTURE RATCHET PASSED: `python3 tests/structure.py`

## Red checks

- `tests / fast (3.14)`: the one failing check inside `python3 tests/stress.py` was "the probed scenarios' memory peaks stay within their recorded budgets" (typical_slab/shoulder traced peak 3.9 MiB against 1.8 MiB recorded, x1.5 threshold). This diff touches only `tools/ci/`, `.github/workflows/governance.yml` and a delivery row, none of which stress.py's probe imports. Re-run of `PYTHONPATH=tests/hastub python3 tests/stress.py` on this same head, Python 3.14.7: `ALL 114 STRESS CHECKS PASSED`, the same scenario reading traced 2.1 MiB. Same code, 3.9 then 2.1 MiB: a run-to-run spread of the traced peak, not a regression from this diff. Cheaper detector: none; the traced probe inside stress.py is the detector that found it, and the spread is a distinct finding in the stress memory-probe seam, not this PR's group. Carry: dismissed: not caused by this diff, no cheaper detector.
- `pr-contract / pr-contract`: red only because the line above was missing from this section; answered here.

## Forward-carry

none

## Friction

none
