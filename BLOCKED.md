# BLOCKED: r11-pre-shared-files, dispatch 1b9856450e (part 1, carries 0-4), base 78d3b40221

Question: the part line reads "Part 1 of 3: build carries 0-4", and those five carries merged as #3708 (`6d7d52709f`, an ancestor of the base). Which is meant: (a) mark carries 0-4 in the roster and re-dispatch `--part` over the carries that remain, or (b) a named residue of carries 0-4 that this seat is to build? Nothing is built here; no code was pushed.

## Why the dispatch names merged work

`tools/audit/seat/cloud_dispatch.py` `part_line` splits `roster_lib.pending_carries`, the carries with no mark. At `handoff/audit-r10-roster` `3a1a252c2e`, `dev/programme/rosters/wave-r11-groups.json`, group R11-PRE-SHARED-FILES: `resume.stage` is `carries-open`, `resume.commit` is `6d7d52709f803516e65be8d3fd101e26772c7e85`, `resume.pr` is 3708, and `roster_lib.carry_mark` returns `None` for every one of the 16 carries, 0 to 4 included. So the split is still 0-4, 5-9, 10-15, and part 1 is the merged part. A seat may not write the roster.

## Measured at 78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f (detached at origin/main, 2026-11-21 UTC)

- `git merge-base --is-ancestor 6d7d52709f HEAD` exits 0; `git log 6d7d52709f..HEAD -- tools/ci/selftest_scope.py tools/pr/figure_block.py tools/ci/selftest_closures.json .github/workflows/governance.yml tools/pr/ci_predict.py` prints nothing, so the part's files are as #3708 left them.
- Carry 0 and carry 4: `absorb_entries` and `union_record` in `tools/ci/selftest_scope.py`; step `id: absorb` of `instrument-self-tests` in `.github/workflows/governance.yml`, `if: steps.drift.outcome == 'failure'`, artifact `selftest-absorbed`. `dev/audit/config/bugclasses.json` cites `dev/audit/rca/R10-RCA-SELFTEST-SCOPE-DRIFT.md` and `dev/audit/rca/R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md`, both in the tree.
- Carry 1: `precheck`, `touched_steps`, `base_drift` in `tools/ci/selftest_scope.py`; the `selftest-scope` arm in `tools/pr/ci_predict.py`.
- Carry 2: `scratch_clone` in `tools/ci/selftest_scope.py`.
- Carry 3: `overlay_program` in `tools/pr/figure_block.py`.
- `python3 -I tools/ci/selftest_scope.py --self-test`: `165 checks, 0 failed`, rc 0 (strace present).
- `python3 tools/pr/figure_block.py --self-test`: `13 checks, 0 failed`, rc 0, with `ok` on `a program main changed or added after the fork runs as the base's and is not the head's diff` and on its null `a file the instrument's run leaves changed in the head's tree is still listed`.

## What #3708 left open of carries 0-4, and where it already sits

The automated commit of the absorbed table (no write route exists without widening a write set the owner pinned; ruling "Do b. Mandate applies", `refs/heads/inbox/r11-pre-shared-files` line 1) is roster carry 13, and the wider `precheck` selection and its cost are carries 14 and 15: all three are part 3's by the current split, and the part line forbids answering them here.

## This ref

This commit's parents are the two `DEMO ONLY (scratch, not for merge)` commits of 2026-11-18 (`964901436f`, `c96dac8741`), which the #3708 handoff left on the step ref; the push is fast-forward only, so BLOCKED.md sits on top of them. Nothing under it is for merge.
