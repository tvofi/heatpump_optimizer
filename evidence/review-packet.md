# Review packet #3046
head: 79bed84a1aae96391d9d492922cf8c6e70d27446
base: 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124594659972 neutral
arch-score / arch-score id=124594625010 success
arm id=124594545102 skipped
budget-raise-gate / budget-raise-gate id=124594625024 success
cancel-superseded id=124594547875 success
codeql / Analyze (actions) id=124594624919 success
codeql / Analyze (javascript-typescript) id=124594624870 success
codeql / Analyze (python) id=124594624881 success
governance / delivery-status id=124594625089 success
governance / delivery-status-publish id=124594626053 skipped
governance / env-matrix id=124594625040 in_progress
governance / instrument-self-tests id=124594625039 in_progress
governance / policy-docs id=124594624924 success
governance / record id=124594626214 skipped
governance / wave-script id=124594625029 success
hassfest / hassfest id=124594624950 success
kernel-points id=124594625698 skipped
prelude id=124594547895 in_progress
refresh id=124594547719 success
tests / arch-instrument id=124594716503 success
tests / briefs id=124594625008 success
tests / browser id=124594716405 in_progress
tests / closure-scope id=124594625041 success
tests / closures id=124594716958 in_progress
tests / coverage id=124594716472 success
tests / coverage-ratchet id=124594940312 success
tests / fast (3.14) id=124594716397 in_progress
tests / graders-head-copy id=124594940296 success
tests / mutation id=124594625081 success
tests / mutation-autofix id=124594805654 skipped
tests / mutation-pins id=124594804947 skipped
tests / nightly-ha id=124594717313 skipped
tests / nightly-status id=124594625025 success
tests / replay id=124594717777 skipped
tests / typing id=124594716483 success
validate / validate-hacs id=124594624937 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3046.md b/dev/programme/delivery/3046.md
new file mode 100644
index 000000000..90b5192dd
--- /dev/null
+++ b/dev/programme/delivery/3046.md
@@ -0,0 +1 @@
+- [#3046](https://github.com/tvofi/heatpump_optimizer/pull/3046) — **open**, triage: s9 batch 92 (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch92.md b/dev/programme/triage/s6-batch92.md
new file mode 100644
index 000000000..11f69eecc
--- /dev/null
+++ b/dev/programme/triage/s6-batch92.md
@@ -0,0 +1,179 @@
+# Proposal triage, session s9, batch 92 (P331, P332)
+
+The rolling batch after batch 91 (#3043). Facts were read at origin/main `811112b78`.
+
+## P331: the train SKIPs an approved pull request while the approval's review run is still settling
+
+Verdict: ACCEPT, reframed, as one carry on R10-FLY-TRAIN-DEFAULTS (`carries-open`, size S; its
+`files` name `tools/audit/seat/merge_train.py`).
+- **The proposed mechanism is already built.** After the approval, the train already waits for
+  something before the first merge attempt. `review_settle` (P86, `s6-batch17.md`) runs before
+  attempt 1 and polls the head's `pull_request_review` runs (`merge_train.py` lines 2095-2110 at
+  `811112b78`).
+- **The two defects are its bound and the classifier after it.**
+  - **The bound fits the 70-s runs P86 measured, not today's.** It is `polls` = 24 grains of
+    `REVIEW_POLL_SECONDS` = 5 (lines 601 and 1026), about two minutes of sleep. The last 59
+    completed `CI review pr=<n>` runs read at 2026-10-31T14:5xZ took 91 s at p50, 2388 s at p90,
+    5549 s at p95 and 10626 s at most. 22 of the 59 ran over 150 s, which is the CI concurrency
+    queue. The train log holds 13 `review run(s) ... (24/24)` lines, so the wait ran out with the
+    run still open.
+  - **The classifier reads the settling state as a missing review.** `policy_refusal` (lines
+    2058-2093) returns "every required context is green, so the missing requirement is a review",
+    with `wait` False, for `mergeStateStatus BLOCKED` and `reviewDecision APPROVED`. `land` then
+    stops the entry as `[BRANCH-POLICY]` on that attempt, even though the approval at the head is
+    the train's own. That holds both while the review run is open and in the seconds after it
+    concludes, before GitHub recomputes mergeability.
+- **Field instances, from `train/current.log`.** In each one a `review run(s)` wait comes before
+  the SKIP:
+
+  | PR | review-run wait | merge attempts | outcome |
+  |---|---|---|---|
+  | #3031 | ran out at `(24/24)`; run 41211188623, 14:40:04Z to 14:46:10Z | 6 | merged later at the same head, `811112b78` |
+  | #3039 | ended at `(14/24)`; run 41196240353, 11:17:29Z to 11:18:48Z | 1, refused right after the run concluded | re-added unchanged at 49c16053, merged later at `ecca12ceb` |
+  | #3013 | ran out at `(24/24)` | 2 | — |
+  | #3000 | ended at `(19/24)` | 1 | — |
+
+  #3013 touches a code-owned file (`away.py`), so part of its block may have been the owner's
+  review. It is not counted as clean evidence. The other two BRANCH-POLICY SKIPs that day, #2989
+  and #2968, read "no owner APPROVED review citing one mandate" and had no review-run wait. They
+  are a different cause and stay untouched.
+- **Proposed form, narrowed.** "Wait for the gate check-run" is replaced by the run the policy
+  actually waits on, the head's `pull_request_review` run. That is what `review_settle` already
+  lists. The policy refused #3031 and #3039 while `policy_refusal` read "every required context is
+  green", so a poll of the `gate` rollup alone would have seen nothing to wait for.
+
+Source: the orchestrator s9's triage-queue line of 2026-10-31T14:50:00Z (slip, recurring, two
+instances today).
+
+Instances: as tabled above. The run durations come from
+`gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>` (2 calls), and the distribution from one
+`gh api 'repos/tvofi/heatpump_optimizer/actions/runs?event=pull_request_review&per_page=60'` read:
+59 completed, p50 91 s, p90 2388 s, p95 5549 s, max 10626 s, 22 over 150 s and 15 over 420 s.
+`grep -c 'review run.*(24/24)' train/current.log` gives 13.
+
+Cost: S inside `merge_train.py`. That is `review_settle`'s bound and one arm of `policy_refusal`,
+about 20 lines, plus three self-test rows and one mutant. `merge_train.py` has no
+`policy_lint.mjs --budgets` row and no `tests/structure_budgets.json` key; the `--budgets` output at
+`811112b78` names it 0 times. No policy file changes. It adds no GitHub write. The extra reads are
+the same `actions/runs?event=pull_request_review&head_sha=` listing `review_settle` already makes,
+at `POLL_SECONDS` grain once the fast grain is spent.
+
+Binding:
+- Each SKIP costs a manual re-add by the orchestrator and the entry's batch slot. The re-add starts
+  a fresh train, and a solo train in this log runs 48 to 67 minutes (P330).
+- Two of the four instances today, #3031 and #3039, later merged at an unchanged head, so those
+  stops were wrong.
+- The fix is about 20 lines on a seam the train already owns, and no rule changes. Waiting on a
+  settling review run costs at most the CI wait the train already accepts for a pending context.
+- A wait is not a merge, so the existing gates are unchanged.
+
+The carry:
+1. **Bound `review_settle` by time, not by a 2-minute count.** Keep the 5-s grain for the first 24
+   polls. Then poll at `POLL_SECONDS` while a `pull_request_review` run at the head is unfinished,
+   up to the train's existing CI-wait budget (`polls` x `POLL_SECONDS`).
+   - Log `review run ... still running` at most once per `POLL_SECONDS`.
+   - When the budget runs out, the merge attempt proceeds as today.
+2. **Treat a settling review run as a wait in `policy_refusal`.** In the branch that returns "the
+   missing requirement is a review", return `wait` True instead when both of these hold:
+   - a `pull_request_review` run at the head is unfinished, or concluded fewer than 120 s ago (one
+     read of the same listing);
+   - an approver APPROVED review sits at exactly that head.
+
+   `land`'s existing `merge_tries` x 30-s loop bounds this. Every other branch is unchanged: a red
+   context, CHANGES_REQUESTED, and a missing owner review with no review run open still park at
+   once.
+3. **Fixtures.**
+   - #3031's shape: an approval at t0, the review run open past 24 fast polls, and the merge
+     attempted only after the run concludes. It lands, with no SKIP.
+   - #3039's shape: the run concludes, and the first merge is refused BLOCKED/APPROVED within
+     120 s. That is a wait, and attempt 2 lands.
+   - Null, still a park: BLOCKED/APPROVED with no review run at the head in the last 120 s
+     (#2968's shape, the missing owner review).
+   - Null, still a park: a required context red.
+4. **One mutant.** Drop arm 2's run check, and the #3039 row SKIPs.
+
+Rejected: polling the `gate` check-run as filed. In both clean instances the rollup already read
+every required context green when the policy refused, so that poll would not have waited.
+
+## P332: the relay and the review-ref writer act on pull requests that are already closed
+
+Verdict: ACCEPT, narrowed to part (2) of the proposal, as one carry on R10-FLY-RELAY-REVIEW-FF.
+That group is `carries-open`, and its `files` name `tools/audit/seat/cloud_relay.sh`. It is the
+confirm-arm skip. Part (1), a state skip in "the review-ref writer", is DEFERRED to a root-cause
+seat, because nobody has yet named the writer.
+- **(2) The confirm arm owes what can never be posted.**
+  - `confirm_arm` in `cloud_relay.sh` (lines 304-339 at `811112b78`) walks every `review/*` tip
+    that the relay delivered. It owes `confirm-owed` until a confirm succeeds or the orchestrator
+    runs `dispose`. It never reads the pull request's state.
+  - A verdict posts only on an open pull request: `tools/pr/app_comment.sh` line 67 dies with "a
+    verdict posts only on an open one". So a confirm-owed line on a merged or closed PR is a false
+    OWED. It spends its 3 tries and then stays on the level, and on every sweep board, until
+    someone disposes it by hand.
+  - **Instance.** `s9/sweep-latest.txt` holds 11 such lines, at #2589 to #2741, `tries=3/3`
+    (15:58Z). Their tips date from 2026-10-28 (`review/2589` d3c9dfb41, `review/2591` 9165b5193,
+    `review/2600` 41c59d4cc), so this part does not depend on part (1).
+  - **Mechanism.** `handoff_arm` already lists the open pull requests on every pass (line 399,
+    `gh pr list --state open`, written to `cloud-prs.$$`). The confirm arm can read the same
+    pass's list, so the check adds no API call.
+- **(1) The review-ref rewrite has no named writer, so a writer-side skip pins nothing.**
+  - 56 `review/<n>` tips have committer times between 14:10Z and 14:56Z today.
+    - 53 of them are on PRs that are not open (`gh pr list --state open`: 3 open).
+    - 36 are tree-identical to their parent.
+    - The rest re-append a PR's whole verdict history. `review/3011` is `8767123ac` (blocked),
+      `942caaa0d` (merge), then `d31683a71` (blocked, 14:30:42Z) and `79b941694` (merge,
+      14:31:03Z), each a restatement.
+  - The subjects are `bus.sh push-verdict`'s `append_commit review` format (`bus.sh` line 242), and
+    the author is the session's ambient `tvofi`. No log on this host names the process: the relay
+    log has no timestamps, and the bus state files hold no review writes at that time.
+  - A state skip in `push-verdict` would be cheap, but it is aimed at a writer that may not be
+    `push-verdict`. 56 rewrites of shared refs by an unidentified process is a root-cause matter
+    (`defect-root-cause.md`), not a proposal.
+  - **What would change this answer:** the process that made the 14:10Z-14:56Z commits, named from
+    a seat transcript or a log.
+  - **What would follow from that:** the countermeasure belongs to that writer. If it is
+    `push-verdict`, its closed-PR refusal is the fix.
+
+Source: the orchestrator s9's triage-queue line of 2026-10-31T16:10:00Z (slip, recurring today).
+
+Instances:
+- **(2)** The 11 `confirm-owed` lines in `s9/sweep-latest.txt` cover #2589, #2591, #2600 and so on
+  to #2741 (`grep -o 'confirm-owed refs/heads/review/[0-9]* [0-9a-f]*' | sort -u | wc -l` gives 11).
+  The relay level at 16:10:44Z holds none of them, so they had been disposed by then.
+- **(1)** The figures come from `git ls-remote origin 'refs/heads/review/*'` (344 refs) and
+  `git log -1 --format=%cI <tip>` on each. Of the 56 tips with committer times between 14:10Z and
+  14:56Z:
+  - 35 are closed and tree-identical to their parent;
+  - 18 are closed and differ from their parent;
+  - 1 is open and identical;
+  - 2 are open and differ.
+
+  They span #2968 to #3043.
+
+Cost:
+- About 10 lines in `cloud_relay.sh`'s `confirm_arm`, plus two self-test rows. The file has no
+  `policy_lint.mjs --budgets` row, and the `--budgets` output at `811112b78` names it 0 times.
+- No new API call, because the arm reuses the pass's open-PR list.
+- No policy changes.
+
+Binding:
+- A predicate that owes an action no instrument can perform is a false positive at its source.
+  Each such line is read on every sweep until a hand `dispose`.
+- The fix is a state check on a list the pass already holds.
+- The writer-side half waits for its cause.
+
+The carry:
+1. **Read the state of the pass's listing.** In `confirm_arm`, read the open-PR list that the same
+   pass's `handoff_arm` fetched (`cloud-prs.$$`), or list it once when `handoff_arm` did not run.
+2. **Skip a PR that is not open.** A `review/<n>` whose PR is not in that list is skipped. Log
+   `cloud_relay: confirm skip #<n>: not open` once per `(pr, sha)`, record it in
+   `confirm-done`, and owe no level line for it.
+3. **Unknown is not closed.** When the listing failed, keep today's behaviour: the line stays
+   owed.
+4. **Fixtures.**
+   - A relayed review on a closed PR (the `HPO_RELAY_PRS` stub omits it) produces no
+     `confirm-owed` and logs one skip line.
+   - Null, still owed: an open PR's undispatched review (the existing row).
+   - Null, still owed: a failed PR listing.
+5. **One mutant.** Drop the skip, and the closed-PR row owes.
+
+Rejected for now: a state skip in the review-ref writer, until the 14:10Z-14:56Z writer is named.

