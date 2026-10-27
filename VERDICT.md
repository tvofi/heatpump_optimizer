Fix review: merge 24702c3756442023ab88524e182fe4333c46ad50
bus-nonce: 68b187d8268df2f8838b8743457ddf98

**Approve — the grade renders the merge tree and reads it with the tree's own checks; two limits and one unpinned claim are recorded below.**

Line 1 is this head's grammar, not the brief's. `tools/audit/seat/bus.sh` (`verdict_sha`) and `tools/audit/seat/proof_watch.py` (`VERDICT_MERGE`) accept only `Fix review: merge <40-hex>` or `Fix review: blocked <40-hex> <label>: <reason>`; a `Verdict: …` first line is refused before anything is pushed, so the substitution is recorded here rather than the verdict lost.

mandate 6329234399

Reviewed head 24702c3756442023ab88524e182fe4333c46ad50, unchanged at publication. Worktree at that head, main checkout untouched. Evidence: `evidence/` beside this file.

## What I measured

- The fixer's harness, at this head: `python3 tools/audit/seat/merge_train.py --self-test` -> `merge_train self-test: 327 checks, 0 failed` (selftest.txt). The batch arms alone are 81 checks, 0 failed.
- The body's reproof: `python3 tests/closure.py selftest` -> `ALL 117 closure shrink pins PASSED`; restoring the pre-fix line gives `FAIL no rename-detecting --name-only diff under RENAME_SITES [tools/audit/seat/merge_train.py:2352: touched = files + self.git("diff", "--name-only", rb, tip).split()]`, `1 of 117 closure shrink pins FAILED` (closure-selftest.txt). So the cheaper detector the body names does fail on the old code and pass on the new.
- `--no-renames` semantics, measured in a throwaway repo: rename-detecting `--name-only` names one side (`b/moved.py`); `--no-renames` names both (`a/old.py`, `b/moved.py`), so the grade's file set is the one the gate's selection needs and a genuine rename is still seen (rename-probe.txt).
- The grade itself, with the real checks, on a real merge tree at this head (grade-arms.txt): a synthetic car that lowers tests/structure_budgets.json `methods_over_200` 9 -> 8 is graded `structure.py RED FAIL methods_over_200 9 > 8 (+1)` with `policy_lint ok`, and `grade_reason` names that red, not the remedy prose; a comment-only change in a measured module is green at both checks (`GRADE: []`). The check moves under its own perturbation.
- Cost (cost.txt): `node tools/policy/policy_lint.mjs` 54.9 s and `python3 tests/structure.py` 32.4 s standalone, 85-108 s each for the same two inside two competing harness runs; about nine cheap git calls plus one or two checks per graded car, and the guard's second pass is a cache hit. An N-car overlap batch pays about N-1 of those. This is not a second train, but it is minutes per car, and a red car also pays a recarry (app_push/prepr) and one CI cycle before the second encounter stops it even though the recarry's tree is the graded tree.
- The red checks, read from GitHub and not the body: `tests / fast (3.14)` job 122212454353 failed on exactly the pin above; `pr-contract` job 122231068361 refused the body for not naming it; `gate` job 122231365540 was that lane's aggregate (red-checks.txt).
- The fixer's M1, re-run here: `grade_merge` returning at its entry leaves exactly the five arms the body names red -- arm 1, the red-arm-read arm, the text-merge arm, arm 2, and the structure.py-selected arm -- with the null control and the worktree-cleanup arm green; `batch arms: 81 checks, 5 failed` (mutation-m1.txt).

## Limits I measured, which I do not read as blocking

- `structure_reaches` predicts the gate's closure-hit rule, not `tests/closure.py select`. Measured (selector.txt): for a GATE_FILE (`.github/workflows/tests.yml`) or an unrecorded path, `select` returns `mode: full` with `tests/structure.py` in `run` while `structure_reaches` returns False; and on the red arm's tree (e8a070d7051d, measured RED at structure.py) `structure_reaches` says False for a touched list that selects nothing. A green grade is therefore a statement about the selected checks, not about the tree. I could not construct a red the merge itself *introduces* that the selector drops: every input structure.py reads (the package's .py files, const.py, tests/structure_budgets.json, tests/seam_map.json, structure.py) is recorded in its closure, and an unrecorded new file makes the gate FULL at the car's own head. It can only propagate a base already red at the ratchet, which --overlap tolerates (main_green is log-only) and which the body scopes out.
- Smaller: the closure's unit mapping is `tests/closure.py`'s in the running checkout, not the merge tree's, so a merge that changes UNIT_DIRS would be mapped by the old rules; and `POLICY_LINT_REL` is chosen from the checkout, so a merge tree that added `.claude/workflows/policy_lint.mjs` would be linted by the tools/policy copy while CI would run the new one.
- Grade and merge are not atomic: the graded tree is built from a fetch of `origin/main` at the guard, and `gh pr merge --match-head-commit` pins the head, not the base, so a foreign merge landing in that window makes the landed tree ungraded. The pre-existing rb-ancestor guard does not see a foreign descendant merge either; this PR narrows the window and cannot close it.

## The one perturbation the fixer did not run

Keying the grade cache on the tree alone -- dropping the `structure` half of the key that the code's comment says keeps a narrower green from being handed to a car that needs the ratchet -- leaves all 81 batch arms green (mutation-cache-key.txt). The code is right; the arm that would prove it is missing, and the body's mutation proof does not claim it. Give the cache a car that meets a graded tree under a narrower selection if this claim is to stay.

## Not established

- No `gate` or `pr-contract` check-run existed at this head when I published: the umbrella's prelude was still running, so I did not read the head's own gate verdict. tests/coverage was also still in progress.
- Whether a `## Unpinned sites` section is owed: `tools/pr/ci_predict.py --base <merge-base>` printed `CI PREDICT: no closures, fast, wave-script or instrument red predicted` and no ADDED UNPINNED line, consistent with the body's absent section; prepr itself was not run here (heavy, and CI's).
