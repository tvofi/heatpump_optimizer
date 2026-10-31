`tools/audit/seat/daemonize.py` ran its own self-test whenever `--self-test` appeared anywhere in argv (`if "--self-test" in sys.argv[1:]`), so a wrapped command that takes that flag (`daemonize.py --log L -- tool --self-test`) was silently replaced by this script's own test and never launched (carry from #2524; issue #2505). Fix: `wants_self_test(argv)` returns `argv[:1] == ["--self-test"]`, and `main()` calls it, so the flag selects the self-test only as the first argument. The usage line in the module docstring now says "first argument only". Pinned by four self-test arms (argv[1] selects it; after `--` is the wrapped command's; as a later option is not ours; no arguments do not select it) and by a harness mutant. Group R10-FLY-DAEMONIZE-ARGV. Carry 1 (the group's only carry, "From #2524 ... restrict it to `argv[1]` and pin it with a self-test arm"): done as above, restricted and pinned by the four arms and the `daemonize-1` mutant.

## Head

f25b5d6a2e308f99469dcda4fb898165fb5886a7 (the fix is a8d94e03b; 187fd9b70 only classifies `daemonize.py` in `tests/closures.json` as read by `tests/entities.py`, the output of `ci_predict.py --apply-inert`; f25b5d6a2 merges origin/main).

## Mutation proof

Mutant `daemonize-1` in `dev/audit/harnesses/r10_seat_selftests_mutants.py` replaces the predicate `return argv[:1] == ["--self-test"]` with `return "--self-test" in argv` (the defect), run on the real source in place with its bytes restored. Run at this head: `env -u BASH_ENV python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 S04 daemonize-1` printed

    == S04 daemonize.py: KILLED rc=1 | daemonize.py: error: usage: daemonize.py --log LOG [--cwd DIR] [--env K=V]... [--path-prepend DIR] -- CMD [ARG]...
    == daemonize-1 daemonize.py: KILLED rc=1 | daemonize.py: error: usage: daemonize.py --log LOG [--cwd DIR] [--env K=V]... [--path-prepend DIR] -- CMD [ARG]...

The killing arms are the self-test's "--self-test after `--` is the wrapped command's, not ours" and "--self-test as a later option is not ours". The usage line is printed by the self-test's own refusal arms and is not the failure. Caveat: the same invocation's M0 arm (every seat step as CI runs it) printed `M0 rc=1 ... ci_probe self-test: 55 checks, 2 failed` and `M0: 6 seat step(s) red` on this host (macOS, load high), steps that do not read `daemonize.py`; the harness therefore ends `RESULT survivors=6`, all six being M0 steps, none a mutant. `git status --short` was empty in the worktree before and after, so the harness restored the file.

## Null control

Unmodified tree (the parent of a8d94e03b, `git show a8d94e03b^:tools/audit/seat/daemonize.py`) given a wrapped command that carries the flag: `python3 -I daemonize.py --log LOG -- sh -c 'echo ran-wrapped "$@"' x --self-test` returned rc 0 and wrote NO log file (the command was never launched; the script ran its own self-test instead). The same line at this head wrote a log whose output line is `ran-wrapped --self-test`. Control for the unchanged path: `python3 -I tools/audit/seat/daemonize.py --self-test` at this head prints `SELF-TEST PASS`, rc 0, with the four new `ok` arms and the six existing launch arms (banner, pid, unflushed output, `-u`, ordering, append mode).

## Figures

- Self-test at this head: `env -u BASH_ENV python3 -I tools/audit/seat/daemonize.py --self-test` prints `SELF-TEST PASS` with the arms named under Null control.
- Mutant: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 S04 daemonize-1` (output above). `daemonize.py` sha1 at this head e3ed6132625fccbb36ef3dcd099d72e6c1659327 (`sha1sum tools/audit/seat/daemonize.py`).
- Diff vs the merge base: `git diff --stat origin/main...HEAD` lists three files, `dev/audit/harnesses/r10_seat_selftests_mutants.py` (+2), `tests/closures.json` (+1), `tools/audit/seat/daemonize.py` (+19 -2).
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

none

## Friction

none
