# STOP: r10-flow-jidoka-p2-body — 5ab48352 does not carry the voluptuous fix

Result body, not a PR body. This seat changed no code. It pushed no `handoff/r10-flow-jidoka-p2-body`, and it did not touch `handoff-body/r10-flow-jidoka-p2` or #2853. The brief says code 5ab4835246614398074616eaaa301593359a1b61 is "the voluptuous import-chain fix". It is not, so no honest `## Red checks` answer can be written for it.

## Evidence

- 5ab4835246614398074616eaaa301593359a1b61 is an ancestor of the failing PR head 819b82fbbf4c0ddb1fcc37d0c3adcd8c96850a4b. `git merge-base --is-ancestor` exits 0. `git diff --name-only 5ab48352 819b82fb -- tools/pr/prepr.sh tests/harness_headers.py tests/harness.py` prints nothing.
- Check run 121432584047 (`governance / instrument-self-tests`, run 40280489428) ran on `refs/pull/2853/merge` with head_sha 819b82fb. So no commit between the failing head and 5ab48352 exists to cite as the fix.
- `claims_reg_line` at 5ab48352 (`tools/pr/prepr.sh` line 306) still runs `import harness_headers as h`. That module imports `harness`, and `harness` imports `tests/hastub/homeassistant/config_entries.py`, which imports `voluptuous`.
- A search of every origin ref (`git log --all -S'import harness_headers as h'`, plus a `--grep` over commits since 06:00Z) finds no commit that removes the import. `handoff/r10-flow-jidoka-p2` and `fix/r10-flow-jidoka-p2` are unchanged, at 5ab48352 and 819b82fb. The code-fixer claim `claim/s6/r10-flow-jidoka-p2` was taken at 07:51Z, and nothing from it has landed.
- `bash tools/pr/prepr.sh --self-test` at 5ab48352 was run twice, in a detached worktree:
  - With `python3` set to a venv-free interpreter (3.13, no voluptuous) and `BASH_ENV` unset: `409 passed, 2 failed`, rc 2. This reproduces CI. The two failing lines are verbatim the 06:39Z ones:
    - `FAIL 6g passes a docs diff whose register the generator rewrites byte-identical (null control) (got 1, wanted 0)`
    - `FAIL and names the stale files and the moved header RESULT (got 1, wanted 0)`
    - Each is preceded by `ModuleNotFoundError: No module named 'voluptuous'`.
  - Under the seat venv, which has voluptuous: `411 passed, 0 failed`. This is the false green a seat sees on its own box.
- Trap for the next seat: the environment's `BASH_ENV` toolchain profile re-prepends the venv to PATH in every `bash` it starts. So `PATH=<sysbin>:$PATH bash tools/pr/prepr.sh --self-test` still runs the venv `python3` and passes. Only `env -u BASH_ENV` reproduces CI's interpreter.

## What is owed

- A code fix first, on `fix/r10-flow-jidoka-p2`, as `dispatch/fixer-r10-flow-jidoka-p2` (08:50+01:00) already asks: make the 6g header comparison independent of `tests/harness`, close the vacuous rc-1 arm, and show the self-test green under `env -u BASH_ENV` with a venv-free `python3`.
- Then a body re-take for that new head. Whoever re-dispatches this body seat should give the fixed head's SHA, not 5ab48352.
- For the record: `python3 -I tools/audit/carry_audit.py check --body` over the current `handoff-body/r10-flow-jidoka-p2` (0d91d96a) prints `CARRY-AUDIT: 7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)` (all `R10-FLOW-JIDOKA`), against the roster it reads from origin/main.
