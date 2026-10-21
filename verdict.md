Fix review: blocked 10f85c3ee7065d31230e292d7438e105efb9ff57 carry-missing: not carried to the sibling-seam stage: the body routes prepr's steps 3 to 3h to #201 but no carry-201.json entry, roster group or issue cites #2528, and the body says the orchestrator still owes it

bus-nonce: a759d6c2b378770c6ff0097c82aa10f8

This is round 3, the third review of this group. I measured head `10f85c3ee7065d31230e292d7438e105efb9ff57`, and it was still the PR head when I wrote this (ev/head-at-write.txt). The head merges code head `df97bd446` and main `5a755f53e`. Its `tools/pr/prepr.sh` differs from the code head only by main's three-line comment at step 3f4 (ev/main-delta-prepr.diff). I worked from detached worktrees of the head, under /etc/profile.d/hpo-toolchain.sh. `dev/governance/roles/` on main is unchanged since the merge base.

## Block

- **The sibling-seam carry has no owner (fix-review.md step 10, finding-propagation.md "Where it goes").** The body's `## Forward-carry` sends prepr's foreground heavy steps 3 to 3h to `#201`, the 18 lines the round-2 rule returns. A KILL orphans them, and a TERM waits behind them. The body adds: "This seat writes no carry file, so the orchestrator owes the entry there, or the group or issue it cuts."
  - `dev/programme/carries/carry-201.json` cites #2528 zero times, on origin/main `5a755f53e` and on roster `5ffe2a933`.
  - No roster group or carry file on the roster ref names #2528. R10-PREPR-CAP is the group this PR closes, so it is no destination.
  - The diff touches no carry or roster file, and no issue was filed (ev/carry-owner.txt).
  - So the finding exists only in this PR's body. That is the step-10 case "one only in this PR's comments", and it fails item (3) of the dispatch brief: a live roster owner that cites #2528.
  - `carry_audit.py check` passes it (`2 routed`) because `#201` is a syntactically valid destination. It does not read whether the carry file holds the entry.
  - To unblock, either one fixes it: the orchestrator writes the entry into `carry-201.json` (or a live roster group's `brief`), citing #2528, with the control (a KILL or TERM to prepr during step 3h leaves the self-test or mutants drive running or deferred) and the fix shape (`closures_step`); or the PR files a new issue for the seam and routes the carry there.
  - No code change is owed. The code and its tests hold (below). Carry: #201 (item 11113f3e)

## Findings

- The sibling seams of the orphaned-recorder class, prepr's steps 3 to 3h, are open and outside this group's scope. This is the block above, carried to the destination the body names, which still has to receive the entry. Carry: #201 (item 11113f3e)
- `carry_audit.py pr 2528` exits 1. Three items of the round-1 verdict (comment 6318683802) were never routed by any later body or verdict. Each is settled at this head, so this verdict routes them:
  - c7585c9b, round 1's block that the reap arm was unpinned: repaired in round 2, and in this round M3wd, M7 and M9 each fail the arms. Carry: dismissed: repaired, the arms are load-bearing at this head (item c7585c9b)
  - b50893bf, the finder's harness: still none committed, so the probe is the reviewers' own instrument. Carry: dismissed: no committed harness exists, disclosed (item b50893bf)
  - 2a8ed562, `PREPR_RECORD_CLOSURES=0` opting in: fixed by `[ "${PREPR_RECORD_CLOSURES:-}" = 1 ]`, which round 2's M6 pins. `closures_records_here` is byte-unchanged since round 2's head `5332c59f9`. Carry: dismissed: fixed and pinned by M6 (item 2a8ed562)
- The body's `## Red checks` is stale in two places. It cites nightly-status job 119339580088 from the previous head, where this head's job is 119521063745. It also says "This code head has not run CI yet", but CI has concluded on this head. The answer itself still holds: the same main run 39563978649 at `c77f89d`, with `slow` and `mutation-nightly` red. Re-word it when the body is next re-cut. Carry: dismissed: stale wording, the answer holds at this head

## Evidence

- **Round 2's block is closed (brief item 1).** Each mutant is a detached worktree at the head with one literal edit, asserted to match exactly once (ev/mut-*.diff). Each run is `bash tools/pr/prepr.sh --self-test` (ev/selftest-*.txt), and all worktrees were restored with an empty `git status` (ev/restore-status.txt).
  - RESULT M0 (null, unmodified): 323 passed, 0 failed.
  - RESULT M7 (`kill -TERM -- -"$rpid"` becomes `kill -TERM "$rpid"`, the leader pid only): 320/3. All three reap arms fail with `got gone:gone:alive`: the lane is orphaned. Round 2 measured 323/0.
  - RESULT M9 (6b's `closures_step "$BASE"` becomes `CLOSURES_LINE=$(closures_line "$BASE")`): 321/2. The TERM-alone and group arms fail with `got alive:alive:alive`. Round 2 measured 323/0.
  - RESULT M3wd (the watchdog body becomes `( : ) & wpid=$!`): 320/3. All three arms fail with `gone:alive:alive`.
  - Every count and every failing arm matches the body's mutation table.
- **How the arms reach production.** The driver copies the 6b block out of prepr.sh by its `# --- 6b.` marker, from the first `^if ` to `^fi$`, into its text. M9 shows that a call-site change reaches the arms. If the marker were lost, the recorder would never start and every arm would read `unstarted`, so the extraction fails closed.
- **Production code is unchanged since round 2.** Between `5332c59f9` and the head, prepr.sh changes only inside the self-test plus main's 3f4 comment. So round 2's M1, M2, M3setm, M4sub, M5, M4 and M6 results still apply to the production lines, and I did not re-run them.
- **Figures re-derived at the head (ev/cheap-checks.txt).**
  - `RULES-SYNC ok`.
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, with scope.run `tests/entities.py`.
  - `ALL 2382 ENTITY CHECKS PASSED`.
  - `claims hygiene: 5a755f53e... ok`. That is this head's own base; the body quotes `1ebc737e7` at the code head.
  - `ALL 124 closure shrink pins PASSED`, `layout self-test: ok`, `ALL 109 HARNESS HEADER CHECKS PASSED`, `STRUCTURE RATCHET PASSED` and `Architecture score: dS +0.0000 NULL`.
  - The `PREPR_RECORD:-` grep gives one production line, prepr.sh:564.
  - The `rc=` lines after the piped commands are the rc of `tail`, so I read each result from its own printed line.
  - I did not re-derive the body's eval-probe figures (`direct: prepr S lane S` and the rest). The M9 result is the measurement those figures support.
- **Release and claim files.** VERSION, manifest.json, RELEASE_NOTES.md and tests/golden are untouched, three-dot from the merge base (rc 0). The nightly-status path filter over the diff prints nothing (rc 1).
- **Merge (brief item 5).** `git merge-tree --write-tree origin/main 10f85c3ee` exits 0 with tree `310f1acdb` against main `5a755f53e`, which is the PR's base, so the merge is clean (ev/merge-tree.txt).
- **CI at this head (brief item 4).** I read the check-runs API for the commit (ev/check-runs.json and ev/check-runs.tsv). All 49 runs have concluded.
  - The one red is `nightly-status` (119521063745). Its log grades main's scheduled run 39563978649 at `c77f89d` (mutation-nightly and slow) (ev/nightly-status-log.txt). The body names and answers it.
  - Per that log, nightly-status is not a required check and does not block.
  - `closures`, `mutation`, `closure-scope` and `instrument-self-tests` are green.
  - `pr-contract` was green at 22:47:55Z, after the last run concluded (composed-proof at 22:47:01Z).
- **Carry audit (brief item 3).** `carry_audit.py check --body` prints `2 routed, 0 unrouted, 0 bad destination(s)` (rc 0). `carry_audit.py pr 2528` prints `10 finding item(s): 7 routed, 3 unrouted` (rc 1); the three are the round-1 items this verdict routes above (ev/carry.txt).
- **Owner approval.** The policy half, gate-scoping.md and its two generated copies, still owes tvofi's approving review, which is not mine to give.
