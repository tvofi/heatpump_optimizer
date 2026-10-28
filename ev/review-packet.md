# Review packet #2929
head: 780adaf04bef23261616489810258ce6416a17c8
base: b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=123052339043 skipped
cancel-superseded id=123052343331 queued
prelude id=123052343136 queued
refresh id=123052342740 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 52f69737: dismissed:registered by the held append-group op after merge
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh api 'repos/tvofi/heatpump_optimizer/actions/runs?branch=fix/triage-s7-batch54&per_page=30'
             gh api: every long flag accepted
  ok         tools/pr/cancel_superseded.py
             `tools/pr/cancel_superseded.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2929.md b/dev/programme/delivery/2929.md
new file mode 100644
index 000000000..708b7a9e1
--- /dev/null
+++ b/dev/programme/delivery/2929.md
@@ -0,0 +1 @@
+- [#2929](https://github.com/tvofi/heatpump_optimizer/pull/2929) — **open**, triage s7 batch 55: rule P266 (V180) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch55.md b/dev/programme/triage/s6-batch55.md
new file mode 100644
index 000000000..5cfec14c1
--- /dev/null
+++ b/dev/programme/triage/s6-batch55.md
@@ -0,0 +1,88 @@
+# Proposal triage, session s7, batch 55 (P266)
+
+This batch has one entry, V180, filed 2026-10-28T19:22:17Z and quoted from `proposals.md` as it
+stands. The owner directed it (tvofi: the account's concurrent-job limit is the CI bottleneck, so
+cancel superseded runs). The owner has decided *whether*; this ruling sets the shape and the
+destination. Facts were read at origin/main `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`, at the
+live roster `origin/handoff/audit-r10-roster` `be898eaef54a6ba1f996b4ca9b11c6f93ce94ea4`, and from
+two Actions run listings (`actions/runs?branch=<b>`) for the two branches the manual pass touched.
+
+## P266: the sweep cancels CI runs whose head is no longer their pull request's head
+
+Verdict: ACCEPT, narrowed to a `sweep` subcommand of the existing `tools/pr/cancel_superseded.py`,
+not a new file. The destination is a new fly-in, **R10-FLY-CANCEL-SWEEP**: no group on the live
+roster owns that file (its R10-CI-CONCURRENCY group does not appear on the roster ref above).
+
+Source: `proposals.md` V180 (the orchestrator, owner-directed, 2026-10-28T19:22:17Z). The manual
+pass at 19:20Z cancelled 4 runs and was refused on 3 stale ghosts.
+
+Instances:
+- **An in-run canceller already exists, but the limit it relieves starves it.**
+  - `tools/pr/cancel_superseded.py` (R10-CI-CONCURRENCY, `092861f05`, 2026-10-18) cancels a
+    branch's older-head runs from the newer run. `ci.yml` line 154 is "Cancel this branch's runs
+    at superseded heads".
+  - Its predicate is the pure `candidates()` (line 48): same branch, event `pull_request` or
+    `workflow_dispatch`, status active, a different head SHA, and a lower run id.
+  - It runs *inside the newer run*, so while that run waits for a runner it cancels nothing. The
+    two listings show exactly this:
+    - `fix/triage-s7-batch54` (#2927): runs 40751731241 (code) and 40751736668 (edit) at
+      `dad80f255`, created 19:09:25-27Z, were not cancelled by the in-run job. The run at the new
+      head, 40751761625, was still `queued` at 19:21Z. They were cancelled by the manual pass at
+      19:21:29-30Z.
+    - `fix/triage-s7-batch49` (#2928): runs 40752875163 and 40752880041 at `582d0e694` show the
+      same pattern. The new-head run 40752909198 was still `queued`, and the manual pass cancelled
+      the old runs at 19:21:11-42Z.
+- **Every open supersedes its own first runs.** `tools/audit/seat/open_pr.sh` pushes twice:
+  the code head (line 70), then a row-only head carrying `dev/programme/delivery/<N>.md` (line
+  84). It must, because the PR number names the row file. Each open therefore leaves one code run
+  and one edit run on a head that is superseded about 20 s later. Both pairs above are this
+  shape.
+- **A bot rule must be kept.** The canceller's docstring says a run sent by `github-actions[bot]`
+  must never cancel the older run still running the other autofix jobs (`a98d5a05a`). That rule
+  carries over to the sweep.
+
+Carry (narrowed shape):
+1. Add `cancel_superseded.py sweep --repo R [--dry-run]`, reusing `candidates()`. It makes one
+   open-PR listing (number, head SHA, head repo) and one runs listing per active status
+   (`queued`, `in_progress`, `waiting`). For each open same-repo PR branch it cancels the runs
+   `candidates()` selects against the PR's live head. With no run yet at the live head, every
+   active run at another head on that branch is a candidate.
+2. **Never** cancel:
+   - a run at the live head, including a twin run at the same SHA;
+   - a run on `main`;
+   - any `push`, `workflow_run`, `schedule` or `pull_request_target` event. That leaves
+     train-hold, beat and record pushes untouched by construction, because they are push events
+     or not on an open PR's branch;
+   - a branch whose live-head commit is authored by `github-actions[bot]`. This is the autofix
+     rule above.
+   - A run on a branch with no open PR (a closed or deleted branch: the "ghosts") is reported,
+     never cancelled.
+3. It prints one line per action and a summary line: `CANCEL-SWEEP: cancelled n, kept m (live
+   head), skipped k (bot head / not a PR), ghosts g`. An unreadable answer cancels nothing and
+   exits 0, the same fail-soft as `run`.
+4. The orchestrator's sweep runs it each pass. R10-ORCH-BEATD can adopt it as a job once that
+   group is built. It is not carried onto BEATD, which is in progress.
+5. Controls (in `--self-test`, beside the existing arms):
+   - The #2927 shape: two runs at `dad80f255` and one `queued` at the live head. Both old runs are
+     cancelled, and the live one is kept.
+   - A bot-authored live head cancels nothing.
+   - A `push` run on `main` and a run on a branch with no open PR are never cancelled.
+   - Mutant: dropping the event filter cancels the `push` fixture, and fails.
+   - Null: a branch whose only active runs are at its live head cancels nothing.
+- Policy and ownership: `tools/pr/cancel_superseded.py` is code-owned (`.github/CODEOWNERS:75`),
+  so the PR merges on tvofi's approving review. The file is already classified
+  (`tests/closures.json`, `tests/closure.py:592`).
+
+Not carried: a new file under `tools/audit/seat/`. The predicate and its recorded fixtures
+already exist in one place, and a second copy would be two owners of one rule. Also not carried:
+changing `open_pr.sh` to push once. The row file needs the number that only the first push
+creates, so the sweep is the cheaper fix for that pair.
+
+Cost: about 60 lines and five self-test arms in a 219-line file. The API cost is 1 open-PR
+listing plus up to 3 runs listings per pass, plus one POST per cancel. At the 300 s poll floor
+that is under 50 calls an hour.
+
+Binding: the owner directs the outcome. The shape is the one that keeps the existing predicate
+and its bot rule as the single source, and reaches the case the in-run job cannot: a newer run
+still waiting for a runner. Measured: 4 runs on 2 opens in one 12-minute window, each pair the
+open's own first push.

