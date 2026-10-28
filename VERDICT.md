Fix review: merge 10f85c3ee7065d31230e292d7438e105efb9ff57

bus-nonce: 65d1909f7889510c0745997d27a38aeb

This is round 3, the third review of PR #2528 (R10-PREPR-CLOSURES). I measured head `10f85c3ee7065d31230e292d7438e105efb9ff57` from a detached worktree under /etc/profile.d/hpo-toolchain.sh. It was still the PR head at 22:48:28Z. `dev/governance/roles/` on main is unchanged since the merge base `5a755f53e`. Following the brief, I judged only the items round 2 left open.

## Findings

- **Sibling seams of the orphaned-recorder class are carried, not settled.** These are prepr's foreground heavy steps 3 to 3h. The body now routes them to the programme's live tracking issue #201, which is open. `carry_audit.py check --body` exits 0 with `2 routed, 0 unrouted, 0 bad destination(s)` (ev/carry-body.txt). `dev/programme/carries/carry-201.json` does not hold the entry yet. The body says the orchestrator owes that entry after the merge. I did not re-derive the "18 lines" count at this head. The rule's text is in round 2's evidence, and this round changes none of steps 3 to 3h: the only change to `prepr.sh` outside the self-test is main's 3f4 comment. Carry: #201
- **The body's `## Red checks` cites nightly-status job 119339580088, which ran at the previous head `5332c59f9`.** At this head the run is job 119521063745. It grades the same main scheduled run, 39563978649 at `c77f89d`, with the same reds, `slow` and `mutation-nightly`. So the body's answer holds unchanged, and only the job id is stale. Carry: dismissed: same main run, answer unchanged
- **The policy half still owes the owner's approving review.** That is `gate-scoping.md` and its two generated copies. Giving it is not a reviewer's job. Carry: dismissed: owner approval gate, not a later stage

## Evidence

- **Item 61eab2a5 (M7) is settled.**
  - The sleeper now forks `( sleep 300 ) &` and records its pid. `reap_arm` requires prepr, recorder and lane all gone, and reads each by `ps -o stat=` state, where absent or `Z` counts as gone. It never uses `kill -0`.
  - RESULT M0 (unmutated): `323 passed, 0 failed`, rc 0 (ev/mut-M0.txt).
  - RESULT M7 (`kill -TERM -- -"$rpid"` -> `kill -TERM "$rpid"`, ev/mut-M7.diff): `320 passed, 3 failed`. All three reap arms fail with `got gone:gone:alive` (ev/mut-M7.txt). This matches the body.
- **My own probe agrees with the arms.** ev/probe.sh is my instrument, not the finder's or the fixer's.
  - Its recorder forks a lane, which forks a grandchild `sleep 301`. Liveness is read from `/proc/<pid>/stat`, and the 6b block is copied from the worktree's `prepr.sh`.
  - Head: KILL to prepr, TERM to prepr and TERM to the group all give `prepr=gone recorder=gone lane=gone grandchild=gone`.
  - M7: all three give `lane=alive grandchild=alive` (ev/probe.txt).
- **Item 3fc47a16 (M9) is settled.**
  - The driver now appends step 6b's own `if ... fi` block, cut from `prepr.sh` at its `# --- 6b.` marker by awk. I checked that the awk returns exactly the 6b block, `closures_step "$BASE"` included. It is copied, never `eval`ed.
  - If the marker disappears, the driver runs no recorder and the arm reads `unstarted`, so the test fails rather than passing empty.
  - RESULT M9 (6b's `closures_step "$BASE"` -> `CLOSURES_LINE=$(closures_line "$BASE")`, ev/mut-M9.diff): `321 passed, 2 failed`. The TERM-alone and group arms fail with `got alive:alive:alive` (ev/mut-M9.txt). This matches the body.
  - My probe under M9 gives KILL all gone, and both TERMs all alive.
- **Item 11113f3e.** The carry is re-routed from R10-PREPR-CAP, which this PR closes, to #201, which is open. `carry_audit.py check --body` rc 0 (ev/carry-body.txt).
- **Head lineage (ev/head-lineage.txt).**
  - The head is main `5a755f53e` merged into `b569bfd02`, which merges code head `df97bd446` into `5332c59f9`.
  - The only change to `prepr.sh` between the code head and the head is main's own 5-line 3f4 comment, the same lines as main's diff from `1ebc737e7`, so nothing was resolved by hand.
  - Outside the PR's five files, the head matches main.
- **Figures re-measured at this head (ev/cheap-checks.txt), every rc 0:**
  - `RULES-SYNC ok`
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, with scope.run `tests/entities.py`
  - `ALL 2382 ENTITY CHECKS PASSED`
  - `claims hygiene: 5a755f53e... ok`. The body quotes `1ebc737e7`, the code head's base.
  - `ALL 124 closure shrink pins PASSED`, `layout self-test: ok`, `ALL 109 HARNESS HEADER CHECKS PASSED`
  - `STRUCTURE RATCHET PASSED`, `Architecture score: dS +0.0000 NULL`
  - The `PREPR_RECORD:-` grep returns one production line, prepr.sh:564.
  - The nightly-status path filter prints nothing (rc 1).
  - VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched, and no claim file moved.
- **Body figures I did not re-take.** I did not re-take M1, M2, M3wd, M3setm, M4, M4sub, M5, M6, or the eval probe. Round 2 verified M0 to M6, and the brief excludes them. The "18 lines" sibling count is above.
- **Merge.** `git merge-tree --write-tree origin/main 10f85c3ee7065d31230e292d7438e105efb9ff57` exits 0 with tree `310f1acdb` against main `5a755f53e` (ev/merge-tree.txt).
- **CI at this head (check-runs API, ev/check-runs.tsv).**
  - All 49 runs have concluded.
  - The one red is `nightly-status` (job 119521063745), which grades main's scheduled run 39563978649 (ev/nightly-status-log.txt). It is not a required check and does not block. The diff reaches nothing those lanes read, and the body's `## Red checks` names and answers it.
  - `closures`, `mutation` and `composed-proof` are green.
  - `pr-contract` ran green at 22:47:21Z, after the last other run concluded (composed-proof, 22:47:01Z).
- **Harness (step 9).** The group still has no committed finder's harness. The lane probe is my own instrument, disclosed above and kept in ev/probe.sh.
