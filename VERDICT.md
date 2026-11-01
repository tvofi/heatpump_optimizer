Fix review: blocked 41790e2b8944e4529a921b27be4b61398e86bef2 merge-semantics: the P312 drain re-sorts a spool that main's add --front ordered, and the --priority wiring from add into the spool has surviving mutants

bus-nonce: e2422e10128694de56e3936c65a9fdfe

## Round

Round 1. Reviewed from a detached worktree at 41790e2b8944e4529a921b27be4b61398e86bef2, which was still the PR head when this verdict was written.

## Block

1. **The merge resolution breaks main's `add --front` (P112).** The textual resolution in `ae3cae823` is correct: main's `--front`/`--remove` block is intact and the item carries `priority`. The semantic resolution is not. Main promises that `--front` puts the entry "FIRST in the next batch" and prints the spool order it read back. This PR's `Train.drain_order` (merge_train.py:3023-3034) re-sorts the whole spool at `queue_take` by `(not priority, not critical)`. A `--front` entry that is not critical therefore drains behind any critical-path entry. My harness `ev/front_vs_drain.py` builds a spool `[#3 critical, #1, #2]` and runs `spool_edit_locked(#1, "front")`. It logs `FRONT #1: spool read back: #1 #3 #2` but drains `[3, 1, 2]`. The null control, with nothing critical, drains `[1, 3, 2]`. So the read-back that `--front` prints does not describe what the train actually runs. Neither the body nor the self-test says how `--front` should rank against `--priority` and the critical path. The fix has two parts. First, decide the rule, for example that a fronted entry keeps first place, or that `--front` sets the same key `--priority` does. Second, pin it with a self-test arm that drives `--front` through `drain_order`.
2. **The `--priority` path is not covered by tests (mutation-vacuous) from the CLI into the spool.** Only `drain_order` is tested, and only on hand-built dicts. The following mutants each leave `merge_train.py --self-test` at 415 checks, 0 failed:
   - R1: drop `**({"priority": True} if a.priority else {})` from the `add` item. SURVIVED.
   - R6: change that line to `if False`. SURVIVED.
   - R4: drop `"priority"` from the spool-entry key list in `train_add` (merge_train.py:1054, added by this PR). SURVIVED.

   R4 matters most. It leaves P312's HOTFIX ordering dead in production: the spool never stores the key, so `drain_order` never sees it, and the suite stays green.

## Findings

- Main's `add --front` ranks below a critical-path entry once this PR's drain sorts the spool, and the read-back it prints no longer matches the drain order (Block 1). Carry: R10-FLY-TRAIN-DEFAULTS
- Surviving mutants R1, R4 and R6 on the `--priority` wiring (Block 2); the fixer owes an arm that drives `add --priority` through `train_add` and the spool into `drain_order`. Carry: R10-FLY-TRAIN-DEFAULTS
- Surviving mutant R2: `front=a.front` changed to `front=False` in `main()`'s add call. This passthrough is main's code (P112), not this diff. Its self-test calls `train_add(front=True)` directly and runs the CLI `--front` only on an already-spooled entry, so the CLI path for a new `--front` entry is untested. The fixer is editing these exact lines for Block 1 and can pin it in the same arm. Carry: R10-FLY-TRAIN-DEFAULTS

## Evidence

- Head: `ev/HEAD.txt` holds 41790e2b8944e4529a921b27be4b61398e86bef2, which is also the worktree's HEAD. The PR's commit list was re-read before writing, and the head had not moved. The body's `## Head` names 41790e2b8944e4529a921b27be4b61398e86bef2.
- Mutants from the body, re-run by me: `r10_seat_selftests_mutants.py postmerge-1 postmerge-2 record_beat-1 record_beat-2 S10` gives RESULT survivors=0 (`ev/body_mutants.txt`). The P312 drain key replaced by `0` is KILLED (2 failed). `merge_pr.sh` CARRIED HEAD comparison made unconditional is KILLED. Deleting `merge_pr.sh`'s postmerge line is KILLED (2 failed) (`ev/merge_pr_mutants.txt`).
- My own mutants (`ev/own_mutants.txt`, `ev/mut.py`): R3 (`--remove` arm turned into front) KILLED. R5 (critical sorted before priority) KILLED. R1, R2, R4 and R6 SURVIVED, as listed under Findings.
- Merge resolution, diffed against both parents. Against main (`fb0a6d5a3`), the conflict hunk differs only by the added `--priority` argument and the `priority` item key. Against `17b38f7d9`, it differs only by main's `--front`/`--remove` block and `front=a.front`. `git merge-tree --write-tree origin/main 41790e2b8944e4529a921b27be4b61398e86bef2` (origin/main `e4c9e2016`) exits 0 with tree `d5a65434a` (`ev/standing.txt`).
- Figures re-measured at the head (`ev/figures.txt`):
  - `merge_train.py --self-test`: 415 checks, 0 failed. The body's 396 was taken at 17b38f7d9, and the body's head note gives 415.
  - `merge_pr.sh --self-test`: 22 checks, 0 failed.
  - `postmerge.py --self-test`: 16 checks, 0 failed.
  - `record_beat.py --self-test`: 16 checks, 0 failed.
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `policy_lint.mjs --budgets`: standing-merge.md at 36 of 37 lines and 504 of 507 words, so within its cap with no raise.
- `tests/entities.py` and `tests/harness_headers.py` could not run in this container: `homeassistant` and `paho` are missing from both venvs, so I did not re-derive these two figures locally. CI's `tests / fast (3.14)` job (124861560572) at this head prints `ALL 2497 ENTITY CHECKS PASSED` (the body's 2493 was taken at 17b38f7d9) and `ALL 112 HARNESS HEADER CHECKS PASSED`. The same job prints `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN` (the scoped gate). The log tail I read did not include the MODE line.
- CI: `merge_train.py classify 41790e2b8944e4529a921b27be4b61398e86bef2` gives GREEN, pending none, red none, rc 0 (`ev/classify.txt`). I read all check runs across every page (`ev/check_runs.txt`): there is no failure, cancelled, timed_out or action_required run. That matches the body's `## Red checks: none`.
- Standing checks: the claim files are byte-identical to origin/main. VERSION, RELEASE_NOTES.md and the manifest are untouched. The delivery row `dev/programme/delivery/3090.md` is in the three-dot diff. The body answers carries 1-5, and its Forward-carry section is `none`. The role contract matches main: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.
- Policy: this PR changes `dev/governance/roles/standing-merge.md` and `dev/governance/roles/nudge.md`. It merges only on tvofi's approving review at its head, or under a mandate in force with scope `all`, and this verdict does not stand in for that review.
- The finder's harness: the packet names none (P-numbered tooling carries). The harnesses I built are my own: `ev/front_vs_drain.py` and `ev/mut.py`.
