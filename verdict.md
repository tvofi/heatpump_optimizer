Fix review: blocked fe138c567b915546e95e8e963fffc527633bfb95 test-red: tests/entities.py countermeasure-B errexit check refuses the bare sh -c this diff adds at tools/pr/figure_block.py:314

bus-nonce: 439909be1ef6fa1301ac0078bf7340b1

Round 1 (first review of this pull request; review scope full).

## Block

- Required check `tests / fast (3.14)` (in `merge_train.py owed-reds`) is red at this head, and the diff causes it. `python3 tests/entities.py` reads `1 of 2723 ENTITY CHECKS FAILED`. The failing check is `every bash -c / sh -c a check runs carries errexit, as GitHub's step shell does, unless it runs no workflow step (countermeasure B)`, with `sites=18 without errexit=['tools/pr/figure_block.py:_self_test']`. The repair the check names is `_GHA_RUN`. The site is the null-control fixture this diff adds at `tools/pr/figure_block.py:314` (`"argv": ["sh", "-c", "echo x > f; " + seen.strip()]`). The merge base `030a4d377f`'s `figure_block.py` has no `sh -c` or `bash -c` call. `classify` at this head prints `RED fe138c567b915546e95e8e963fffc527633bfb95 pending: none red: gate`. Because the head is red, it takes no merge verdict (C8).
- The head is red, so the repair round must also re-run the mutants. These mutants survive the head's own checks: the self-tests of `tools/ci/selftest_scope.py`, `tools/pr/ci_predict.py` and `tools/pr/figure_block.py` all stay at 0 failed. None of them is in the body's `## Unpinned sites`. Each one is either pinned in the repair, or argued as equivalent there with the argument stated:
  - `tools/ci/selftest_scope.py:1066`: `absorb_cli`'s `gone = _ignored(root, probes) | ...` with `_ignored(...)` replaced by `set()` survives (M5a). The same line's retired half also survives when `retired = []` replaces `tools/ci/selftest_scope.py:1065` (M5b). The body says "A read naming nothing at this head (... an ignored or retired probe) is not carried". Only `absorb_entries` with a `gone` the test supplies is pinned. Nothing pins the CLI that computes `gone` from `.gitignore` and the retired manifest, so the real `absorb` would carry an ignored or retired probe from main's artifact into the table.
  - `tools/ci/selftest_scope.py:891`: `step_commands`'s launcher regex survives with `bg_(?:start|run)` replaced by `bg_(?:start)` (M7b). A waiter whose launcher line uses `bg_run` would then not be touched by a diff to its script. The body's mutant "touched_steps forgets what a waiter launcher starts" is killed, but the fixture only exercises the `bg_start` spelling.
  - `tools/ci/selftest_scope.py:807`: `scratch_clone`'s fetch survives when `"+refs/tags/*:refs/tags/*"` is dropped (M6). The body lists `check=False` on that line as unpinned, but not the tag refspec. A traced step that names a tag would then run against a clone with no tags.
  - `tools/ci/selftest_scope.py:955`: `precheck`'s `or _traced()` survives when it is removed (M4b). Under main's traced run of this very step, `precheck` would then attempt a nested strace instead of skipping with rc 3.
  - `tools/ci/selftest_scope.py:926`: `base_drift`'s `or mb == (git("rev-parse", "HEAD") or "").strip()` survives when it is removed (M3). This is reachable only when HEAD is the merge base and main already carries the drift. Without the clause, base_drift traces the same commit a second time and excuses every refusal as main's (rc 0 instead of 1). Pin the clause, or record the equivalence argument.

## Evidence

- Head: `fe138c567b915546e95e8e963fffc527633bfb95`. `refs/pull/3666/head` and `fix/r11-pre-shared-files` both read this SHA at the end of the review, and the PR body's `## Head` names it. File `ev/HEAD.txt`.
- Roles are current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` prints nothing.
- Merge with main: `git merge-tree --write-tree origin/main fe138c567b` rc 0, tree `d036157e47`, no conflict (`ev/merge_tree.txt`).
- CI (`ev/classify.log`): `classify` printed WAIT six times, then `RED ... red: gate`.
  - `tests / fast (3.14)` failed on `tests/entities.py` as described under Block. The log section is in `ev/ci_fast_entities_section.txt`, line 2627.
  - `pr-contract / pr-contract` is red because the body's `## Red checks` does not name `tests / fast (3.14)`. That follows from the red above. pr-contract is not in the owed-reds set.
  - `tests / nightly-status` is red, and is not in the owed-reds set.
  - Every other required context is green. That includes `tests / mutation`, `tests / typing`, `tests / coverage-ratchet`, `governance / instrument-self-tests` and `validate / validate-hacs`.
- Mutation proof (the PR's own harness): `sh tools/ci/selftest_scope_mutants.sh` at the head ends `SELFTEST-SCOPE MUTANTS: every mutant refused`, rc 0, in 76 s wall on 4 processors. There are 56 `^== ` mutant lines and no `NOT REFUSED`, `MUTANT NOT APPLIED` or `BASELINE RED` line. This matches the body's 56 mutants and 72 to 75 s (`ev/selftest_scope_mutants.log`).
- Reviewer's own mutants (`ev/reviewer_mutants.txt`, `ev/reviewer_mutants2.txt`; drivers in `ev/reviewer_mutant_driver*.py`):
  - Killed: M1 (absorb's `git` reads), M2 (absorb's flag-added line), M8 (`drift`'s `only` filter), M9 and M10 (`ci_predict.selftest_scope_preds` rc 3 and rc 0 arms), M11 to M14 (`overlay_program`'s skip-worktree, index reset, base-only exclude and returned env), M15 (origin URL), M16 (`BASH_ENV` pop).
  - Survived: M3, M4b, M5a, M5b, M6, M7b, as listed under Block.
- Self-tests and other checks at the head:
  - `python3 -I tools/ci/selftest_scope.py --self-test`: `162 checks, 0 failed`.
  - `python3 tools/pr/figure_block.py --self-test`: `13 checks, 0 failed`.
  - `python3 tools/pr/ci_predict.py --self-test`: `0 failed`.
  - `python3 -I tools/ci/selftest_scope.py static`: `120 gated step(s), 0 problem(s)`.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `python3 -I tools/audit/fold_ledger.py check`: `0 violation(s)`.
  - Output is in `ev/cheap_checks.txt`.
- Claims: `python3 tests/env_drift.py --all` prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`. No claim file or golden is in the diff.
- Versions: the three-dot diff touches neither `VERSION`, the manifest nor `RELEASE_NOTES.md`.
- Carry 3 figure, re-derived with my own probe (`ev/carry3_scope_line.txt`). The body's probe `a0b2d441ee` is in no ref, so I rebuilt it to the same definition: one edit of `dev/programme/delivery/1059.md` on `9b7d8d3682^` (`a720d3ed63`), giving probe `72ade22524`.
  - The head's `figure_block.py render scope-line --base e0ad8b2bd32b...` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
  - The renderer from `e0ad8b2bd3` prints `MODE: FULL -- every test script runs, nothing is scoped out.`
  - Both match the body. The SHA differs from the body's because the probe is my rebuild.
- Figures I did not re-derive:
  - the `precheck --base origin/main` wall times: 2600 s for 17 steps, and about 20 min per `prepr` trace;
  - the `record --step selftest-scope --step selftest-scope-mutants` re-record, including its byte-identical second run;
  - the no-strace reproduction at `01d4ea83bb`;
  - `ci_predict.py --base origin/main` at the head.

  Each of these is a strace-traced run of tens of minutes, or a host condition. CI's `governance / instrument-self-tests` is green at this head. I added no rerun of the gate or of the mutation table, as `fix-review.md` step 11 requires.
- Finder's harness: none is named. This PR answers design-note carries, not a finder's finding. The brief's demonstration of countermeasure A is the self-test's `the bot:` checks, which pass at the head.
- Table movement, step 14: `tools/ci/selftest_closures.json` changes only the `selftest-scope` and `selftest-scope-mutants` entries. Those are probes of the scratch-clone fixture (`config`, `objects`, `refs`, `l.txt`, `m.txt`, `<unknown>`), which these steps' new code creates, so the movement follows from the change. No budget, closure, INERT or golden moves.
- Forward-carry: the body's two Forward-carry lines and the 8 carry_audit items are routed (`CARRY-AUDIT: 8 routed, 0 unrouted`). I did not open the roster branch for them, because the block above decides this round.
