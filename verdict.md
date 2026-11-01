Fix review: merge 9070029ac258bc819e486d57b00b84a89e559936

bus-nonce: f744c2a0a14038e64389e8e3e59811e1

Round: 3. This is a delta repair over round 2's 361be3cd6, not a re-cut.

Measured head: 9070029ac258bc819e486d57b00b84a89e559936. Branch-only code since round 2 is 75d19ea93 alone: test code in roster_sync.py's self-test, plus plants Y5 and Y6 in r10_roster_ops_mutants.py. The two later commits are merges. 0fa7be8f8 merges 75d19ea93. 9070029ac merges origin/main b5df066e7. `git diff 75d19ea93 9070029ac` touches only files that came from main.

Contract: dev/governance/roles/fix-review.md at origin/main. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. I judged the head from detached worktrees at that SHA.

Head re-read before return: refs/heads/fix/r10-roster-schema-pr = 9070029ac258bc819e486d57b00b84a89e559936 (ev/head-reread.txt).

## Findings

- PR body: the `## Round-2 findings, all answered` section is spliced into the middle of the intro bullet on `roster_sync.py`'s merge transition. The splice point is after "(round 2: before it, `--apply` wrote `carries-open` where the dry run printed `done`; `". The intro bullet therefore ends in a stray heading. A second, truncated `## Round-1 findings, all answered` heading opens inside a code span before the real one. The content is all present; the body's structure is broken. This is a body edit and does not block. Carry: R10-ORCH-ROSTER-SCHEMA
- `r10_roster_sync_mutants.py` M9_carry_dedupe_dropped still survives at this head (rc=0 fails=0, ev/sync-mutants-head.txt). It predates the diff, and the body already forwards it. Carry: #2505
- The body's figure is not at this head. `## Figures` gives prepr at 75d19ea93, the authored handoff, with the closures step skipped (non-Linux). The live head adds a main merge. My own run at this head settles it (Evidence), so the figure only needs restating. Carry: R10-ORCH-ROSTER-SCHEMA

## Evidence

- **A4 and A5, the round-2 survivors.** I used the round-2 reviewer's ev/mut2.py, unchanged except for the head argument and the worktree paths (ev/mut3.py). Each plant ran in its own detached worktree under `env -u BASH_ENV python3 -I <file> --self-test` and was restored clean (ev/mutants-r3-head.txt).
  - A4 (dry-run projection without legacy): rc=1 KILLED. roster_sync reported 86 checks, 1 failed: `the dry run's projection reads the cut-over: a same-pass Carry: to a legacy-only group it closes is refused, not planned`.
  - A5 (write-path projection without legacy): rc=1 KILLED, 86/1: `the write path's projection reads the cut-over: the group is written done, the carry not appended, nothing stranded`. The plant's write was `('done', ['legacy one', 'the oth finding ...'])`, the stranded write from round 2's probe.
- **The same plants at the round-2 head 361be3cd6** (ev/mutants-r3-r2head.txt): A4 and A5 rc=0 SURVIVED, 82/0. The null there (no plant) is also 82/0. The kill is earned by 75d19ea93's tests.
- **Every other finder plant at this head:** X1, X2, X6, X7, X8, A1, A2, A3 and A6 are all rc=1 KILLED with named FAILs. The no-plant null N0 is rc=0, 86/0.
- **Y5 and Y6, the in-tree plants of the same replacement.** Y5 is A4's replacement and Y6 is A5's; neither existed in the round-2 driver. Reproduced at round 2: the identical replacements survive at 361be3cd6 (above). Closed at this head: `r10_roster_ops_mutants.py Y5 Y6` printed Y5 `rc=1 fails=1`, Y6 `rc=1 fails=1` and `plants: 2, without a FAIL line: none`. `--null` printed rc=0 fails=0 for all four targets (ev/self-tests.txt). The omission planted by hand (A4/A5 above) is killed too.
- **Null control, the guards still accept legitimate input.** The unplanted self-tests at this head are roster_lib 60/0, roster_edit 153/0, roster_sync 86/0, carry_audit 214/0, r10_roster_ops_mutants 186/0 and brief_lint `TOTAL: 0 error(s) across 48 file(s)`, `ISSUELESS ok`. They hold these nulls green:
  - an open-group move lands and a plain value lands;
  - a readable cut-over proceeds, with a legacy carry leaving set-stage `done` as `done`;
  - `sync --apply writes done over a group whose only carry is legacy`;
  - with no cut-over the same carry writes carries-open;
  - the new post-cut-over null: the dry run plans `carry R9-LEG +=` and the write appends and writes carries-open.
- **The nulls bite.** These are my own plants, not the finder's (ev/nullplants.py, ev/nullplants.txt).
  - N3 forces the dry-run projection to `done`: rc=1, FAIL `a destination holding a post-cut-over carry projects carries-open: the dry run plans the append (null control)`.
  - N4 forces the write-path projection to `done`: rc=1, FAIL `and the write appends it and writes carries-open (null control)`.
  - N1 and N2 widen only the projection's legacy set to every carry. They survive as equivalent mutants: `closing_stage` only rewrites `done`, never downgrades `carries-open` (L5), and derive() has already judged with the real set.
- **Replay at this head.** The round-2 reviewer's ev/replay2.py ran unchanged, with its worktree at 9070029ac (ev/replay3.py, ev/replay-r3.txt).
  - `legacy at cut-over: 498 carries over 206 groups`.
  - `done-flips today: 21; would now be carries-open: 6`.
  - The RESULT lines are identical to round 2's replay-r2.txt (`diff` empty). The 15 zero-pending flips stay done and the 6 pending-carry flips stay carries-open.
  - On all 10 derive-replayed sync flips, derived equals written: AGREE=True 10, AGREE=False 0.
  - The two round-1 slips are R10-WOOD-NOTIFY (a3553d6d5) and R10-ORCH-ROSTER-SCHEMA (52aea59b1). Both are among the 6 and write carries-open, not done. As in round 2, I read the brief's "must not write carries-open" as "must not write done", because the same brief requires the 6 to stay carries-open.
- **Round-2 findings, re-checked.**
  - A4/A5 pins: fixed, as verified above.
  - The prepr figure: the body now names the full prepr at the authored handoff 75d19ea93, not this head (Findings).
  - The round-1 findings are still routed and none is claimed fixed. The body says "Unchanged", which is true.
- **prepr at this head.** I ran `bash tools/pr/prepr.sh` on Linux in the head worktree, with no body passed and the closures step included (ev/prepr-head.txt). It printed `PRE-PR: 9070029ac258bc819e486d57b00b84a89e559936 ... rc=0`, including:
  - `self-test 431 passed, 0 failed`;
  - `CI PREDICT: no closures, fast, governance or instrument red predicted against b5df066e7a23`;
  - `closures: scoped recordings are covered; left to CI: tests/harness_headers.py`;
  - `claim files: byte-identical to origin/main`.

  Its body step was skipped because I passed no body. CI's pr-contract covers the body, and the review packet reads `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted` and `FIGURES: 10 resolved`.
- **Mutation driver at this head.** `r10_roster_sync_mutants.py`: 23 of 24 rc=1, M9 rc=0, `restored`, the tree clean afterwards. This matches the body.
- **Merge, claim files and version.** `git merge-tree --write-tree origin/main 9070029ac`, with origin/main at 92588d581, exits 0 with tree a21a1f071 and no MERGE-CLAIM line (ev/merge-tree.txt). tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to origin/main. VERSION, the manifest and RELEASE_NOTES.md are untouched.
- **Delivery row.** dev/programme/delivery/3054.md is in the three-dot diff (`**open**`).
- **Structure, scope and score** (ev/structure-scope.txt). `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget file is touched. `tests/closure.py select --diff b5df066e7` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, RUN tests/entities.py. `archscore score.py --diff b5df066e7 HEAD` prints `Architecture score: dS +0.0000 NULL`.
- **CI on this head.** `merge_train.py classify 9070029ac...` was polled from 07:52Z at least 75 s apart (ev/ci-classify.txt). It exited 0 with `GREEN 9070029ac258bc819e486d57b00b84a89e559936 pending: none red: none`. No check on the head concluded red, so step 11 owes no answer, and `## Red checks: none` stands.
- **Review packet** rendered here (ev/review-packet.md). It reports no refusals and no advisories. Its finder's-harness section says "none named". The finder's harness I used is the round-1 reviewer's mut.py/replay.py as reworked by the round-2 reviewer (mut2.py, replay2.py), named in the brief. nullplants.py is my own.
