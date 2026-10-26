# STOP: r10-flow-jidoka-p2-body — the red is a live code defect at the PR head

Result body, not a PR body. No code was changed or pushed, no `handoff/r10-flow-jidoka-p2-body` exists, and the body of #2853 was not patched. Brief step 2 says to stop and tell the orchestrator before touching code. No orchestrator session could be reached by message, so this ref carries the report.

## Failing head

- Check run 121432584047, `governance / instrument-self-tests`, run 40280489428. Failed 06:39:09Z with `409 passed, 2 failed` and exit 2, in step `bash tools/pr/prepr.sh --self-test`.
- It checked out `refs/remotes/pull/2853/merge` = 9e15c5dec, "Merge 819b82fbbf4c0ddb1fcc37d0c3adcd8c96850a4b into 11b7a9d739db46a5a62e9f9cf01a8f527a974137". So the failing head is the current PR head, 819b82fbbf4c0ddb1fcc37d0c3adcd8c96850a4b, and no later commit exists that could have fixed it.
- The two failing lines, verbatim:
  - `FAIL 6g passes a docs diff whose register the generator rewrites byte-identical (null control) (got 1, wanted 0)`
  - `FAIL and names the stale files and the moved header RESULT (got 1, wanted 0)`
- Each one is preceded by `ModuleNotFoundError: No module named 'voluptuous'`, raised from the chain `tests/harness_headers.py:21 from harness import Results` -> `tests/harness.py:25` -> `tests/hastub/homeassistant/config_entries.py:47 import voluptuous`.

## Cause

- Step 6g and its self-test arms are new in this PR, added by 002a963a8 (`claims_reg_line`). `origin/main`'s `tools/pr/prepr.sh` has no `claims_reg_line`, so this red does not happen on main and is this PR's own.
- `claims_reg_line` does its header comparison by running `python3 -I -c '... import harness_headers as h'`. At module top, `harness_headers` imports `harness`, which needs `voluptuous`. The governance job's `python3` does not have it.
- So the header-comparison subshell always fails there. The function then prints "the header comparison did not run" and returns 1, which flips the rc-0 null control and the message arm.
- The third arm, `6g refuses a README link added without re-recording`, passes vacuously: it wants rc 1, and the import failure returns rc 1 too.
- Reproduced here: a system `python3 -I` with `tests` and `tests/hastub` on `sys.path` fails `import harness_headers` with the same `ModuleNotFoundError`.
- 5ab483524 and 8580797b5 / 819b82fb do not touch `tools/pr/prepr.sh`, `tests/harness_headers.py` or `tests/harness.py`, so the defect is unchanged at the head.

## Proposed fix (not applied: owed to a code fixer on fix/r10-flow-jidoka-p2)

- Make the header comparison independent of `harness`. Options:
  - (a) Move `expected_from` / `printed_from` into a module that imports nothing from `harness`.
  - (b) Defer `from harness import Results` and `R = Results(...)` in `tests/harness_headers.py` into `main()`, if that file's own pins allow it.
  - (c) Run the snippet under the interpreter that has the venv, the same one the real `claims.py` needs.
- Whichever is chosen, the self-test should also:
  - check the "names the stale files" arm's text, so an import failure cannot pass the rc-1 arm vacuously;
  - run in an interpreter without `voluptuous`, to prove the fix holds where CI runs it.
- Then re-take the head figures and re-body under `## Red checks`. The cheaper detector for the PR's body: run `prepr.sh --self-test` under the governance job's interpreter (system python, no venv) before handoff. Its standing cost is the ~4 min the self-test takes.

## Other reds at the head

The 07:03Z `pr-contract` refusal is the same issue: `## Red checks` does not name `governance / instrument-self-tests`. The right answer is the fix above, not a body line that names this red while leaving it in place.
