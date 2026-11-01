Hotfix, main red: `governance / instrument-self-tests` fails `pr_args self-test: 158 checks, 2 failed` when `runs-on: ubuntu-latest` lands on ubuntu-26.04 (red at 6421fe135, job 124813746788; green at 92588d581, job 124783717352 on 24.04). There `/bin/sleep` is the uutils multicall binary, which refuses a renamed argv[0] ("Security violation: Requested utility `unrelated-sleep` does not match executable name"). `pr_args.sh`'s reap fixture started its bystander as `ln -s /bin/sleep "$REAP_DIR/unrelated-sleep"`, so the bystander died at once and both null controls that require it alive failed.

The fix makes the bystander a two-line wrapper, `exec sleep "$1"`: the exec keeps `$UNREL` the sleeper's own pid, and the sleep is invoked under its own name on either coreutils. Alternatives: pinning the workflow to `ubuntu-24.04` (rejected by the brief: it hides the class); `exec -a` (bash-only and still a renamed argv[0], which uutils refuses); dropping the bystander's distinct name (it is a path name only; the comm is `sleep` either way, so nothing keys on it).

`dev/audit/harnesses/r10_uutils_sleep.sh` lands the reproducer (fixer step 18): it binds an argv[0]-checking `sleep` over `/usr/bin/sleep` in a private mount namespace and runs the self-test in a detached worktree at `<rev>`, with a `gnu` null control and a `symlink` mutant. Classified inert for `tests/harness_headers.py` by `tools/pr/ci_predict.py --apply-inert` (the `tests/closures.json` line).

Carry 1 (the roster's brief for this group) is discharged as written, with one departure: the failing test is not a fake `sleep` earlier on PATH, because the fixture named `/bin/sleep` by absolute path, so a PATH entry never reaches the line that broke. The harness binds the emulation over `/usr/bin/sleep` in a private mount namespace instead; PATH lookups of `sleep` (the fixed wrapper's, and every other `sleep` in the self-test) reach it too. The class grep, the mutation proof and the null control the carry names are below.

## Head

783e189f312a1eb574882123732cfdd8f5c15e91, merge base 6421fe135d9f (origin/main tip 6421fe135d9f at 2026-11-01T10:34Z; main unmoved since the prepr run, so no second run).

## Mutation proof

The fix's production line restored to the symlink form, at the head, under the uutils emulation:

`bash dev/audit/harnesses/r10_uutils_sleep.sh 783e189f3 emu symlink` printed

    FAIL open_pr: the null control -- an unrelated sleeper survives
    FAIL null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start
    pr_args self-test: 158 checks, 2 failed

the same two arms, and the same tally, that job 124813746788 printed.

## Null control

- The unmodified tree under the emulation reproduces CI's red: `bash dev/audit/harnesses/r10_uutils_sleep.sh 6421fe135 emu` printed the two FAIL lines above and `pr_args self-test: 158 checks, 2 failed`.
- The fixed tree on the host's GNU sleep stays green: `bash dev/audit/harnesses/r10_uutils_sleep.sh 783e189f3 gnu` printed `pr_args self-test: 158 checks, 0 failed`.
- The fixed fixture still kills nothing it did not start: the two bystander arms (`open_pr: the null control -- an unrelated sleeper survives` and `null control: a normal successful update_pr ... stops nothing it did not start`) pass under the emulation, and `$UNREL` is the sleeper itself: under the emulation `ps -o pid=,args= -p $UNREL` on a wrapper started the fixture's way printed the real sleep binary's argv at that pid, not `sh`.
- The emulation itself refuses as uutils does: invoked through a link named `unrelated-sleep` it printed "Security violation: Requested utility `unrelated-sleep` does not match executable name `sleep`" and exited 1, and as `/bin/sleep` it exited 0.

## Figures

- `bash dev/audit/harnesses/r10_uutils_sleep.sh 6421fe135 emu`: `pr_args self-test: 158 checks, 2 failed` (baseline under uutils emulation).
- `bash dev/audit/harnesses/r10_uutils_sleep.sh 783e189f3 emu`: `pr_args self-test: 158 checks, 0 failed` (head under uutils emulation).
- `bash dev/audit/harnesses/r10_uutils_sleep.sh 783e189f3 emu symlink`: `pr_args self-test: 158 checks, 2 failed` (mutant).
- `bash dev/audit/harnesses/r10_uutils_sleep.sh 783e189f3 gnu`: `pr_args self-test: 158 checks, 0 failed` (null control, host GNU coreutils 9.4).
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run`; `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Class sweep (fixer step 8), rule: `git grep -nE '\bln +-[a-zA-Z]*s' -- ':!*.md' ':!*.mdc'` and `git grep -nE 'os\.symlink\(|symlink_to\(|hardlink_to\(|os\.link\(' -- '*.py' '*.mjs' '*.js'` and `git grep -nE 'exec -a' -- '*.sh' '*.py'`, at the merge base. Every seam returned, against its disposition:
  - `tools/audit/seat/pr_args.sh` bystander `ln -s /bin/sleep .../unrelated-sleep`: closed in this diff.
  - `tools/audit/seat/pr_args.sh` `nops` PATH (`ln -s "$k" "$t/nops/${k##*/}"`): keeps each basename, so a multicall binary dispatches correctly; not the class.
  - `tools/audit/seat/train.sh` `ln -s "$(command -v python3)" .../venv-ci/bin/python3` (two sites): same basename, and CPython does not dispatch on argv[0]; not the class.
  - `dev/audit/harnesses/r10_seat_selftests_mutants.py` and `tools/audit/seat/offline_spy.py` (`python3`/`python` to `sys.executable`), `tests/entities.py` (`python` to `sys.executable`): CPython is not multicall; not the class.
  - `dev/audit/harnesses/r10_fly_nightly_hb.py` `py-spy` link: same basename; not the class.
  - `tools/audit/worktree_gc.sh` (a venv directory), `tools/pr/prepr.sh` (markdown files, the `tests` directory), `tools/pr/gh_comment.py` (markdown files), `tests/arch_score.py` (a text file), `tests/gate_lock.py` (`os.link` of lock files): links to data, not executables; not the class.
  - `exec -a`: no site.

## Red checks

- `governance / instrument-self-tests` (on main at 6421fe135, job 124813746788): the cause is the runner-image change, `ubuntu-latest` moving to ubuntu-26.04 whose `/bin/sleep` is uutils' multicall binary refusing a renamed argv[0]. Cheaper detector: none exists; a seat's macOS or Ubuntu 24.04 host runs GNU coreutils, and macOS cannot run uutils' check at all, so no earlier check could have seen it. `dev/audit/harnesses/r10_uutils_sleep.sh` now reproduces it on any Linux seat.

## Forward-carry

none

## Friction

none
