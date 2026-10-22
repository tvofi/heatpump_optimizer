Fix review: merge 2af78ed5959f39dbe1e2bdee2efa0298ee198312

bus-nonce: 97f2e58ff8bdd429fb144e624ed7b08f

Delta re-review, round 5, of head 2af78ed5959f39dbe1e2bdee2efa0298ee198312 (still the PR head when read from the PR API at about 17:15Z). The merge base is origin/main `8a94ffd03` itself, so the head already contains main. `dev/governance/roles/` is unchanged between the merge base and origin/main.

## Findings

- None. The round-4 block was a routing defect in the body, and the body now routes. The sibling-seam finding is already carried to R10-FLOW-JIDOKA, which is now on main's roster, and the PR's own Forward-carry items settle the rest. Carry: dismissed: nothing unsettled by this PR is left in the delta.

## Evidence

- **Item 1, the block is cleared.** `R10-FLOW-JIDOKA` is a group on origin/main's roster. `carry_audit.py check` with no `--roster-ref`, run on the body's Forward-carry section, prints `4 routed, 0 unrouted, 0 bad destination(s)` (ev/carry.txt). The check-runs API read shows `pr-contract` completed success twice on this head (119971084672 and 119971447356).
- **Item 2, `## Red checks`.** It names the four `pr-contract` runs red at `1723d8743` (119585492906, 119585669593, 119587185157 and 119691498245) with their cause. It also names the `nightly-status` reds at `10f85c3ee` and `5332c59f9`. Round 4 counted three `pr-contract` runs; the body counts four, and I did not re-read the older heads' check runs. This head's own `nightly-status` run (119971092321) is red; `nightly-status` is not a required context, grades main, and the diff reaches nothing it reads (the filter prints nothing, rc 1). The other 34 runs on this head are success, skipped or neutral, or were still running at 17:15Z (ev/HEAD.txt holds the head). The heavy runs are CI's and I did not re-run them.
- **Item 3, the diff is the reviewed fix.** The branch's diff against `origin/main` and round 4's three-dot diff at `1723d8743` differ only in `index` lines and hunk offsets, because main moved (ev/branch.diff, ev/prev.diff). The change is the five files from before: gate-scoping.md and its two generated copies, delivery/2528.md and `tools/pr/prepr.sh`. `git merge-tree --write-tree origin/main 2af78ed5959f39dbe1e2bdee2efa0298ee198312` exits 0 with tree `5ae08a8bf` (ev/merge-tree.txt). That is a clean merge, so there is no conflict resolution to judge.
- **Mutation proof at this head**, run as `bash tools/pr/prepr.sh --self-test` under the seat toolchain with PREPR_SKIP_CLOSURES=1 in a detached worktree (ev/selftest-*.txt). The worktree read 0 dirty files after the last restore.
  - RESULT M0 (null): 333 passed, 0 failed.
  - RESULT M7 (watchdog kills the pid rather than the group): 330/3, all three reap arms fail with `got gone:gone:alive`.
  - RESULT M9 (6b calls `closures_line` in the foreground): 331/2, the TERM-alone and group arms fail with `got alive:alive:alive`.
  - RESULT M3wd (watchdog body emptied): 330/3, the three reap arms fail.
  - The body's counts are at `bb53ba321` (323, 320/3, 321/2), and it says so. The same three mutants fail the same arms at this head, with 10 more passing arms from main.
- **Body figures re-derived at this head.** Release files and `tests/golden` are untouched (rc 0). The `PREPR_RECORD:-` grep gives one line. R10-FLOW-JIDOKA is on origin/main's roster. I did not re-derive the entity count (the body says 2397), the scoped-gate line, the structure ratchet, the architecture score, the 18-line sibling rule, the `333 passed` self-test at `20d129b11` as a separate blob, or the 4-routed figure on the full body. The body's `333 passed` matches my M0 at the merged head.
- **Forward-carry (step 10).** The roster brief of R10-FLOW-JIDOKA carries the #2528 sentence; round 4 read it on the roster ref and it is now on main's roster. I did not re-read the brief text on main.
