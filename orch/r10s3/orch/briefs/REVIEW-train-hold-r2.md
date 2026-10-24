# Fix review — R10-TRAIN-HOLD, round 2 (new head after a blocked verdict)

Role: **fix reviewer**, adversarial. Read `dev/governance/roles/fix-review.md` and
`dev/governance/roles/COMMON.md` first. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**

Code head: `ddfbf8ac730f5e9b2c6e5ca1bc142fff4e764cd0` (`handoff/r10-train-hold`); body
`handoff-body/r10-train-hold` = `6f763391e4a2725ac3fe51edac9155f3a97900ba`.
A verdict at the **old** head `17197336f` blocked this branch; that verdict is not a verdict on this head. The
pull request is being opened as the record; find it with `gh pr list --head fix/r10-train-hold --state open`.
**Hold your verdict** until the orchestrator sends a `bus-nonce` at the final post-recarry head — the delivery row
must land before dispatch.

Work in a detached worktree at the head you measure, under `/Users/timmalmstrom/hpo-seats/r10s3/r10-train-hold-review2/`
(scratch and evidence there; absolute paths). `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`.
Long runs detached via `tools/audit/seat/daemonize.py --log`; the gate lease is shared and the box is loaded
(load1 60+): state load1 beside wall-clock figures and prefer counts.

## What changed since the blocked verdict

**F1 — the hold bound now prices a refresh gap, not a wait.** The hold ref is refreshed at four sites in
`tools/audit/seat/merge_train.py`: run start, every queue item, before every recarry, and before every sleep in
`wait_ci()`. `HOLD_MAX_AGE_S` drops 14400 → 3600, above the longest named phase (a 15-min recarry) by >3×. Only a
train/batch arms the ref; a bare `wait-ci` cannot leave one behind (new test + arming mutant).
**F2 — the absent-ref arm is the API's own code**: `GET /commits/train-hold` returns **422**, not 404; the step now
treats 404 and 422 as silent absence and logs anything else. F3–F5 adjust the body, add dismissal-marked carries,
and prove stdin delivery (`printf 'not json' | gh api --input -` → 400).

## What to verify, with your own harness

1. **Reproduce the two blocking findings at the old head** (`17197336f` with the new tests transplanted if needed):
   they must be red there and green at `ddfbf8ac`. The fixer reports `196 checks, 2 failed` at the pre-repair head
   and `197, 0 failed` at this one; re-run both.
2. **Re-run the mutants**: no start publish; release only in `finally`; arming guard widened to `if not self.real`;
   no per-item refresh; no `is_sha` guard; no `wait_ci` refresh; no recarry refresh. Each must redden the named
   check. A mutant that crashes instead of reddening is not a proof.
3. **The live publish path — the fixer names this as the first thing to attack.** `gh api --method POST
   …/git/refs --input -` with `{"ref": "refs/heads/train-hold", "sha": …}`, and `PATCH` on the second refresh: is
   the shape accepted by the API the train will use? A refused publish fails open and silently today — check
   whether the code logs it distinguishably and whether `hold_armed` has any other reader.
4. **`wait_ci`'s refresh cannot starve the wait** — it fires only on the path that sleeps; confirm by reading the
   loop and by the mid-wait test.
5. **The 422 arm**: stub 422 (silence), 500 and unparseable (warn); drop the `!= 422` arm and confirm the
   null-control check reds.
6. **The body**: `prepr.sh BODY.md 2302` at this head (the fixer re-ran figure_lint and carry_audit after a
   one-line Figures edit that prepr did not see — verify the body as pushed); 14 figures resolve; 0 unrouted
   carries; `## Head` names `ddfbf8ac…`; the two dismissal-marked carries are legitimate dismissals, not routed
   work.
7. **Not established** (the fixer says so): the create/refresh/delete has never run against GitHub, the recarry
   phase's 5–15 min is a comment's figure, and the concurrency seam is recorded not fixed. Confirm the body says
   this and does not claim a live publish.

Post the verdict with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` once the nonce
arrives; a head that moved under the review is `blocked`. No host path in the verdict (#2310) — write `~/…`.
Report under 250 words: verdict line, each item confirmed/not, what you could not establish.
