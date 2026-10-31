Two reds `prepr.sh` step 6d's CI predictor (`tools/pr/ci_predict.py`) should have predicted and did not: (1) `wiring_preds` kept only `UNWIRED` lines of `selftest_wiring.py --check`, so #3004 round 3's MISMATCH on the instrument page it added went red on `instrument-self-tests` unpredicted; (2) `prepr` predicted the `mutation` ratchet but not the null-control refusal (#2997 rounds 1 and 2). `wiring_preds` now returns every gap kind (UNWIRED, MISMATCH, UNINDEXED, DUPLICATE, MISSING) that names a changed file; the `mutation` arm adds `NO NULL CONTROL` (via `mutation_table.null_for`) as a real red (rc 1, counted in the jobs/reds summary). No autofix job repairs it. Round 2 (review of 86501f71, blocked): the self-test now drives the refusal through `predict(only="mutation")` (B1), and `ci-autofix.md` is back to main byte for byte (O1).

## Head

ff2958bd2a07f8c150e4def2c46869d98937e1d6 (the reviewed head 86501f71 plus a merge of `origin/main` 14ed1355 and two commits: the self-test arm; `ci-autofix.md` restored). `git diff origin/main...HEAD --stat` touches `tools/pr/ci_predict.py` and `dev/programme/delivery/3042.md` only.

## Mutation proof

Run `env -u BASH_ENV`, on the new arms (`null_control_self_test`):
- Wiring predicate (round 1, unchanged): `kinds = (...)` -> `("UNWIRED",)`; self-test prints `FAIL a planted MISMATCH on a changed instrument page is predicted red`, 1 failed.
- M3 (the review's): in `unpinned()`, `nonull = null_control_preds(...)` -> `nonull = []`. Now prints `FAIL an unpinned site in a comment-free file is refused, rc=1`, 1 failed (round 1: survived, 0 failed).
- M4 (the review's): in `is_red`, drop `or line.startswith("NO NULL CONTROL")`. Now prints the same FAIL, 1 failed (round 1: survived).
- Each restored: 0 failed. The two mutants were run through the arm's function alone (about 2 s) because the whole `--self-test` takes about 25 min at load 58; the unmutated whole run is under Figures.

## Null control

The new arm calls `predict(root, "HEAD", only="mutation")` with site discovery stubbed to one added unpinned site and the real `null_for` reading the real file: in `flow_meter.py` (no whole-line comment) it asserts rc=1 and a `NO NULL CONTROL` line; the same site in `button.py` (has a comment) asserts rc=0 and no such line. Round 1's direct `null_control_preds` arms and the MISMATCH null control (a page the diff leaves alone predicts nothing) still pass.

## Figures

- `env -u BASH_ENV python3 tools/pr/ci_predict.py --self-test | tail -1` -> `ci_predict self-test: 0 failed` (control: M3 or M4 or the filter mutation -> `1 failed`).
- `python3 tests/structure.py | tail -1` -> `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs | grep TOTAL` -> `TOTAL: 0 error(s)`; `node tools/policy/rules_sync.mjs --check` -> ok.
- `git diff origin/main -- dev/governance .claude/rules .cursor/rules` -> empty.
- `bash tools/pr/prepr.sh body.md` (no closures skip beyond its own non-Linux default) -> `PRE-PR: ff2958bd2a07f8c150e4def2c46869d98937e1d6 ... rc=0`, MODE: SCOPED, `ci predict` ok with 0 reds, `self-test` 429 passed 0 failed, `unpinned sites` skipped (diff adds none).

Alternatives: filtering gap lines in `selftest_wiring.py` itself was rejected (the check's CI output must stay whole; the predictor owns the diff scoping). The `ci-autofix.md` table row naming the refusal is dropped: restored to main it overruns the file's token cap by 21 tokens (1490 against 1469), and the fix does not need it.

## Red checks

`none` on this branch. Answer for the two reds that motivated it: cheaper detector = this change (`ci_predict` wiring and mutation arms); standing cost = one `selftest_wiring.py --check` run (already run) and one `null_for` file scan per added site.

## Forward-carry

`none`

## Friction

`none`

## Approval

Not needed: no policy file changes. `dev/governance/rules/ci-autofix.md` and its two generated copies are byte-identical to `origin/main`.
