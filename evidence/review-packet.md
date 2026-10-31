# Review packet #3030
head: 12d32a204c923e768f6146a510445374c23f548c
base: 861f949ae85884801bee7cd94e9307bf546c9046

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=124422959868 success
arch-score / arch-score id=124429817715 success
arm id=124422819545 skipped
budget-raise-gate / budget-raise-gate id=124429817699 success
cancel-superseded id=124422819576 success
codeql id=124429819183 skipped
codeql / Analyze (actions) id=124422921977 success
codeql / Analyze (javascript-typescript) id=124422921940 success
codeql / Analyze (python) id=124422921923 success
gate id=124431833775 success
governance id=124429818910 skipped
governance / delivery-status id=124422922031 success
governance / delivery-status-publish id=124422923476 skipped
governance / env-matrix id=124422921986 success
governance / instrument-self-tests id=124422921979 success
governance / policy-docs id=124422922030 success
governance / record id=124422923184 skipped
governance / wave-script id=124422921966 success
hassfest id=124429819175 skipped
hassfest / hassfest id=124422921905 success
kernel-points id=124429819109 skipped
pr-contract / pr-contract id=124430704489 success
prelude id=124422819571 success
refresh id=124422819501 success
tests id=124429819047 skipped
tests / arch-instrument id=124423070688 success
tests / briefs id=124422922008 success
tests / browser id=124423070684 success
tests / ci-ratchet id=124424262715 skipped
tests / claims-autofix id=124424112356 skipped
tests / closure-scope id=124422922051 success
tests / closures id=124423070687 success
tests / closures-autofix id=124424263186 skipped
tests / coverage id=124423070683 success
tests / coverage-ratchet id=124423214191 success
tests / fast (3.14) id=124423070746 success
tests / graders-head-copy id=124423214124 success
tests / lane-proofs id=124424110644 success
tests / mutation id=124422921955 success
tests / mutation-autofix id=124423073612 skipped
tests / mutation-pins id=124423073787 skipped
tests / nightly-ha id=124423072028 skipped
tests / nightly-status id=124422921959 success
tests / replay id=124423071432 skipped
tests / typing id=124423070706 success
validate id=124429818629 skipped
validate / validate-hacs id=124422921957 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git grep -n 'Code:' 861f949ae -- tools/audit/seat/body_push.sh tools/audit/seat/cloud_relay.sh
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log --diff-filter=A --format=%cI -- dev/programme/triage/s6-batch46.md
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git show origin/main:tools/audit/seat/update_pr.sh
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 1 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3030.md b/dev/programme/delivery/3030.md
new file mode 100644
index 000000000..35346a79c
--- /dev/null
+++ b/dev/programme/delivery/3030.md
@@ -0,0 +1 @@
+- [#3030](https://github.com/tvofi/heatpump_optimizer/pull/3030) — **open**, triage: s8 batch 84 (P321 ruling) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch84.md b/dev/programme/triage/s6-batch84.md
new file mode 100644
index 000000000..c3dde1558
--- /dev/null
+++ b/dev/programme/triage/s6-batch84.md
@@ -0,0 +1,70 @@
+# Proposal triage, session s8, batch 84 (P321)
+
+The rolling batch (V182) after batch 83 (handoff `triage-s8-batch83`). Facts were read at
+origin/main `861f949ae` and on the roster branch.
+
+## P321: the relay updates a pull request from the previous round's body
+
+Verdict: ACCEPT as already carried, with a priority flag; narrowed against the filing's timestamp
+form. **R10-FLOW-BODY-ONLY** (`not-started`, S) has held this exact fix since 2026-10-28 as P233
+(`s6-batch46.md#P233`, V147, "A handoff updates only with the body pushed for it"):
+- `body_push.sh` writes a `Code: <40-hex>` trailer naming the handoff tip the body was written
+  for;
+- `cloud_relay.sh`'s `handoff_arm` does not update when the body tip's `Code:` names another sha,
+  writing `level_line handoff-body-stale ... body names <sha12>` and retrying on its next pass;
+- a failed update's level line carries the `REFUSE` reason.
+
+It is unbuilt. The group's `next_step` has read "DISPATCH NOW: every `after` group is done" since
+2026-10-27.
+
+- **Priority.** The roster op raises R10-FLOW-BODY-ONLY to be dispatched next. This is the
+  recurrence its brief was written for.
+- **REJECTED: the filing's form, "refuse when the body ref's newest commit is older than the
+  code ref's head commit".** A timestamp order is not an identity. A body re-pushed for an
+  unchanged head (P233's #2890, #2891 re-bodies) is newer than the code yet correct. A stale body
+  committed after a quick code push can also be newer, under clock skew between a cloud runner and
+  this host. P233's `Code:` trailer names the head exactly and needs no clock.
+- **Residual, not carried: "BUSY on a dead lock, no retry for 4 minutes".** `update_pr.sh` exits
+  75 (BUSY) while `$WT.lock` is held, and the relay retries on its next pass (`update_pr.sh:12-16`).
+  The group's carry 7 (exit 75 for a branch held elsewhere) covers that path. A lock held by a dead
+  process that is never reclaimed would be a separate defect. This instance gives no evidence of it
+  beyond "did not retry for at least 4 minutes", which may be the pass interval. DEFER: one
+  instance with its cause unmeasured. A second relay BUSY on a lock whose holder pid is dead
+  (`ps -p` empty), lasting more than two passes, re-opens it on this group.
+
+Source: the orchestrator s8's message of 2026-10-31 (slip, 02:42Z, #3016).
+
+Instances:
+- **#3016, by the orchestrator's account.** The relay ran `update_pr` at `460e4b76` against the
+  round-1 body `af5caa138` (`FIGURES: 9 resolved`, `CARRY-AUDIT: 1 finding item`). Prepr refused
+  it on 11 unpinned sites and 5 unanswered reds, while the round-2 body (`1858b19a2`/`5dcf18b8`,
+  `PR-BODY: 0 error(s)`, `18 resolved`) had not yet landed. About 15 minutes of orchestrator time
+  and a fixer turn went into the diagnosis.
+- **Earlier instances**, in P233's ruling: #2890 and #2891 were re-bodied stale (2026-10-27), and
+  #2894 likewise. So this is the fourth or later, an audit class whose barrier is carried and not
+  built.
+- **The fix is not on main.** `git grep -n 'Code:' origin/main -- tools/audit/seat/body_push.sh
+  tools/audit/seat/cloud_relay.sh` prints nothing at `861f949ae`.
+
+Cost: as carried in P233, about 20 lines across `body_push.sh` and `cloud_relay.sh` with their
+self-tests, in a group sized S whose after-edges are all done. This ruling adds only the priority
+and the residual's re-open condition.
+
+Binding: a carried, sized, unblocked fix for a recurring defect, still undispatched three days and
+at least one more incident later. Raising its priority costs nothing beyond the dispatch it was
+already owed. The timestamp variant would add a second, weaker check beside it.
+
+Carry text (for `roster_edit.py append-carry R10-FLOW-BODY-ONLY`, citing
+`triage: dev/programme/triage/s6-batch84.md#P321`): "P321 (orchestrator 2026-10-31, slip, #3016).
+PRIORITY: dispatch this group next. Its P233 carry (the `Code:` trailer in `body_push.sh`, and
+`cloud_relay.sh` `handoff_arm` not updating on a body naming another head) is the fix for this
+recurrence.
+- Observed 2026-10-31 02:42Z: the relay ran `update_pr` at `460e4b76` against #3016's round-1
+  body `af5caa138` before the round-2 body landed. Prepr refused on 11 unpinned sites and 5
+  unanswered reds the new body answered. About 15 orchestrator minutes and a fixer turn were lost.
+  At 861f949ae neither file has a `Code:` line.
+- Do not add a commit-time comparison (body newer than code): re-bodies of an unchanged head are
+  newer and correct, and clocks skew between runner and host.
+- Add one fixture row: the relay given a body tip whose `Code:` names the previous head writes
+  `handoff-body-stale` and runs no `update_pr.sh`. Null: a `Code:` naming the current head
+  updates."

