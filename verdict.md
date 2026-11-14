Fix review: merge df1512502349af541505b73a81a86beb4dd6f930

bus-nonce: 6870f579a89302886464e24414f54c7a
pending-ci: gate

Round 4, a delta review over the reviewed head 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf, which was blocked `root-cause-unrecorded` only on main's Saturday-clock red in `tests / fast (3.14)`. From this round on, `fixer.md` owes a re-cut. Review scope: `delta`. I measured in a detached worktree at df1512502349af541505b73a81a86beb4dd6f930.

## Evidence

- The delta is one automatic merge of origin/main 513a07dfdc into 0f191f49a8, with no resolution. Re-running `git merge-tree --write-tree 0f191f49 513a07dfdc` gives tree 5d6bcbe630, which is identical to the head's tree. `git range-diff` shows all 10 PR commits as `=`, unchanged (ev/delta.txt).
- `review_carry.py 0f191f49a8 df15125023` prints `CARRY`: 0 of 1 branch-only commits are non-merge (ev/review_carry.txt).
- `git diff 0f191f49 df151250` has 14 files, all main's. The PR's own paths (tools/ci/, dev/audit/config, .claude/workflows/audit-find.js) are byte-identical to the reviewed head. Its custom_components/ lines are main's version stamp only (manifest.json and the card's version string). Under step 12, nothing there puts reviewed code at risk, so the scope is not widened.
- The round-3 block is resolved by main. The delta brings c987209c (#3578), which anchors `_chg_seq` in tests/features.py:62334 to Monday 2026-11-09 instead of `dt_util.now()`. `git merge-base --is-ancestor c987209c df15125023` holds. This also settles the round-3 finding on that fixture, so nothing is carried.
- The round-2 findings stay resolved at this head. Run today, a Saturday, with RESULT:
  - `selftest_scope.py --self-test`, both unset and with `GITHUB_BASE_REF=main`: `148 checks, 0 failed`.
  - `SELFTEST_BASE=origin/main selftest_scope.py static`: `114 gated step(s), 0 problem(s)`, rc 0 (ev/selftest_static.txt).
  - `sh tools/ci/selftest_scope_mutants.sh`: 35 `== ` lines, 0 `NOT REFUSED` or `MUTANT NOT APPLIED`, `SELFTEST-SCOPE MUTANTS: every mutant refused`, rc 0 (ev/selftest_scope_mutants.txt).
  - These all match the body's figures.
- `git merge-tree --write-tree origin/main df15125023`: rc 0, so it merges cleanly. The head's base 513a07dfdc is origin/main (ev/mergetree.txt).
- Step 5/14: the PR's own three-dot diff (8 files) touches no VERSION, manifest, notes heading, golden, claim file or budget.
- Step 7: the body's `## Head` names df1512502349af541505b73a81a86beb4dd6f930 and describes this merge as automatic. `refs/pull/3551/head` reads df15125023 at 04:14Z.
- CI: `merge_train.py classify df15125023 --pr 3551` printed `WAIT ... pending: gate red: none` on every poll from 03:43Z to 04:14Z, about 30 minutes (ev/classify.log, ev/classify_last.txt). The live runs at 04:13Z are in ev/checks_at_0413Z.txt:
  - `tests / fast (3.14)` is queued, and `governance / instrument-self-tests` is in progress.
  - `tests / mutation` and `validate / validate-hacs` are success.
  - Two runs concluded failure: `gate` (job 132323694215, the companion run whose pr-contract skipped) and `tests / nightly-status`. Neither is in the `owed-reds` set (ev/owed_reds.txt), and classify reads `red: none`. So no red at this head is owed or this PR's own, and the relay re-checks it once CI concludes.
- Whether the previously red `tests / fast (3.14)` is now green is pending CI. I did not re-run it locally, because it is a heavy check (step 11) and the fix is main's c987209c.
- Self-audit: `carry_audit.py check` over this verdict printed `0 finding item(s)`, rc 0. That run used an empty body file, because this seat reads the PR body only through the API. The packet's `carry_audit at the head` over the body printed `1 finding item(s): 1 routed, 0 unrouted` (R10-NUDGE-RETIRE), and the body's forward-carry is unchanged since the reviewed head.
