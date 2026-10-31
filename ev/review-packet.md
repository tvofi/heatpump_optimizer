# Review packet #3027
head: 66c8fa12c1b16193470181ab747d641656d84a62
base: fbc73128371ba2daf9696b851528819c6bf5070e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=124409635806 success
arch-score / arch-score id=124418396128 success
arm id=124409501136 skipped
budget-raise-gate / budget-raise-gate id=124418396114 success
cancel-superseded id=124409500404 success
codeql id=124418397496 skipped
codeql / Analyze (actions) id=124409593372 success
codeql / Analyze (javascript-typescript) id=124409593332 success
codeql / Analyze (python) id=124409593386 success
gate id=124418868644 success
governance id=124418397339 skipped
governance / delivery-status id=124409593326 success
governance / delivery-status-publish id=124409594680 skipped
governance / env-matrix id=124409593280 success
governance / instrument-self-tests id=124409593276 success
governance / policy-docs id=124409593214 success
governance / record id=124409594214 skipped
governance / wave-script id=124409593153 success
hassfest id=124418397114 skipped
hassfest / hassfest id=124409593345 success
kernel-points id=124418396789 skipped
pr-contract / pr-contract id=124418747323 success
prelude id=124409500318 success
refresh id=124409500427 success
tests id=124418397417 skipped
tests / arch-instrument id=124409682948 success
tests / briefs id=124409593156 success
tests / browser id=124409682885 success
tests / ci-ratchet id=124416863599 skipped
tests / claims-autofix id=124410343005 skipped
tests / closure-scope id=124409593114 success
tests / closures id=124409683155 success
tests / closures-autofix id=124410423589 skipped
tests / coverage id=124409682975 success
tests / coverage-ratchet id=124416862131 success
tests / fast (3.14) id=124409682983 success
tests / graders-head-copy id=124416862226 success
tests / lane-proofs id=124416862173 success
tests / mutation id=124409593394 success
tests / mutation-autofix id=124409863433 skipped
tests / mutation-pins id=124409863571 skipped
tests / nightly-ha id=124409683912 skipped
tests / nightly-status id=124409593366 success
tests / replay id=124409684446 skipped
tests / typing id=124409682883 success
validate id=124418397090 skipped
validate / validate-hacs id=124409593106 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 66c8fa12c1b16193470181ab747d641656d84a62 lacks origin/main cabfaadc3a13f61eaf0303918c7b1d5beda9c07c; roster read at origin/main
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git show origin/main:tools/audit/carry_audit.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git show origin/main:tools/audit/seat/queue_pre_flight.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 1 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3027.md b/dev/programme/delivery/3027.md
new file mode 100644
index 000000000..6ce0f52cc
--- /dev/null
+++ b/dev/programme/delivery/3027.md
@@ -0,0 +1 @@
+- [#3027](https://github.com/tvofi/heatpump_optimizer/pull/3027) — **open**, triage: s8 batch 82 (P319 ruling) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch82.md b/dev/programme/triage/s6-batch82.md
new file mode 100644
index 000000000..4b05a22c5
--- /dev/null
+++ b/dev/programme/triage/s6-batch82.md
@@ -0,0 +1,66 @@
+# Proposal triage, session s8, batch 82 (P319)
+
+The rolling batch (V182) after batch 81 (handoff `triage-s8-batch81`). Facts were read at
+origin/main `fbc731283`, on the roster branch `origin/handoff/audit-r10-roster`, and in the
+orchestrator's live merge-train log (`merge_train/train.log`).
+
+## P319: the train's pre-flight refuses a carry to a group that exists only on the round's roster branch
+
+Verdict: ACCEPT, a carry on **R10-FLY-RELAY-REVIEW-FF** (`carries-open`). It owns `carry_audit.py`'s
+disposition, where the fix lives (`load_dests`). The carry may be dispatched alone, ahead of the
+group's other carries.
+- **The rule.** `carry_audit.load_dests` adds the round roster (`roster_lib.round_ref`) as a second
+  destination source whenever it reads a roster, including when a caller names `ref`. Today it does
+  that only on the no-ref path.
+- **Pre-flight changes nothing itself.** `queue_pre_flight.py:197` keeps calling
+  `load_dests(self.checkout, "origin/main", ...)` and inherits the fix.
+- **The premise the orchestrator asked to check holds.** carry_audit already has the round-branch
+  path (`Dests.round_ref`/`round_groups`, and `load_dests` lines 370-374, "The tree's roster lags the
+  round's branch (finding-propagation.md)"). Pre-flight never reaches it, because that branch sits
+  under `else:`: the explicit-ref path at lines 347-352 sets no `round_roster`.
+
+Source: the orchestrator s8's message of 2026-10-31 (a slip; a third pre-flight false-park class,
+beside P308 and P314's verdict-prose class).
+
+Instances (train log, `grep 'is not a group of the roster'`):
+- `PARK #3004` item `b42363f1`: "R10-FLY-CANCEL-SWEEP is not a group of the roster". The group is on
+  the roster branch (in-progress) and absent from main's roster at this read (count 1 on the
+  branch, 0 on main). Waived by hand under the mandate.
+- `PARK #2925` body item `162aa32f`: "R10-FLY-CIPREDICT-RESTORING is not a group of the roster". It
+  is the same shape. The group has since reached main at a stamp, so it reads on both now.
+- **Why it recurs.** Round-10 roster changes reach main only at the stamp (finding-propagation.md,
+  tvofi 2026-10-18). Any carry to a group appended this round reads as a bad destination at
+  pre-flight until the next stamp, while `carry_audit check` with no ref (prepr, body_push) accepts
+  it.
+  - `body_patch.sh` printed the matching `NOTE stale tree ... roster read at origin/main` (the
+    orchestrator's account).
+  - Two parks so far. Every fly-in appended this round is exposed.
+
+Cost:
+- About 3 lines in `load_dests`: compute `round_roster` on the explicit-ref path too, from the
+  same `roster_lib.round_ref` read. Add two fixture rows.
+- No new file, check or API call. `carry_audit.py` is not a capped file.
+
+Binding: two train parks, each needing a by-name waiver, from the one destination source the rest of
+carry_audit already honours. A two-path disagreement inside one function, against about 3 lines,
+is clearly positive. It removes the third pre-flight false-park class at its source, not per
+instance.
+
+Carry text (for `roster_edit.py append-carry R10-FLY-RELAY-REVIEW-FF`, citing
+`triage: dev/programme/triage/s6-batch82.md#P319`): "P319 (orchestrator 2026-10-31, slip:
+pre-flight roster source). May be dispatched alone, ahead of this group's other carries.
+- `tools/audit/carry_audit.py` `load_dests` (line 342 at fbc731283) sets `round_roster` from
+  `roster_lib.round_ref` on the explicit-`ref` path too (lines 347-352). Today only the no-ref
+  `else:` branch does (lines 370-374).
+- A carry to a group that is open on the round's roster branch is then valid at every caller,
+  including `queue_pre_flight.py:197`'s `load_dests(self.checkout, "origin/main", ...)`, as
+  finding-propagation.md counts it.
+- Observed: train `PARK #3004` item b42363f1 ("R10-FLY-CANCEL-SWEEP is not a group of the roster";
+  on the roster branch, not on main) and `PARK #2925` item 162aa32f (R10-FLY-CIPREDICT-RESTORING,
+  same shape before its stamp). Both were waived by hand.
+- Fixture rows:
+  - `load_dests(repo, 'origin/main')` with a group present only on the round ref routes a `Carry:`
+    to it.
+  - Null: a group on neither is still BAD-DEST.
+  - Null: a group `done` on the round ref is still refused.
+- One mutant: skip `round_roster` on the ref path, and the first row is BAD-DEST again."

