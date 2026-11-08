# Review packet #3343
head: 0c3138c5f35760a738cf78694f91cb65af4c3726
base: 996ded2a6dc52816bd4c7dd873c048d85fc6adad

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128822963275 success
arch-score / arch-score id=128822939597 success
arm id=128822807154 skipped
budget-raise-gate / budget-raise-gate id=128822939677 success
cancel-superseded id=128822809333 success
codeql id=128822940425 skipped
codeql / Analyze (actions) id=128822917537 success
codeql / Analyze (javascript-typescript) id=128822917643 success
codeql / Analyze (python) id=128822917671 success
gate id=128823275143 failure
governance id=128822941345 skipped
governance / delivery-status id=128822917455 success
governance / delivery-status-publish id=128822919116 skipped
governance / env-matrix id=128822917474 in_progress
governance / instrument-self-tests id=128822917459 in_progress
governance / policy-docs id=128822917478 success
governance / record id=128822918972 skipped
governance / wave-script id=128822917405 success
hassfest id=128822940722 skipped
hassfest / hassfest id=128822917380 success
kernel-points id=128822940582 skipped
pr-contract id=128823276470 skipped
prelude id=128822809526 success
refresh id=128822809453 success
tests id=128822941630 skipped
tests / arch-instrument id=128823072057 success
tests / briefs id=128822917532 success
tests / browser id=128823072148 in_progress
tests / claims-autofix id=128823805957 skipped
tests / closure-scope id=128822917641 success
tests / closures id=128823072139 in_progress
tests / coverage id=128823072090 success
tests / coverage-ratchet id=128823327398 success
tests / fast (3.14) id=128823072080 success
tests / graders-head-copy id=128823327299 success
tests / mutation id=128822917528 success
tests / mutation-autofix id=128823126450 skipped
tests / mutation-pins id=128823126554 skipped
tests / nightly-ha id=128823073588 skipped
tests / nightly-status id=128822917549 success
tests / replay id=128823073214 skipped
tests / typing id=128823072104 success
validate id=128822941336 skipped
validate / validate-hacs id=128822917453 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at 0c3138c5f35760a738cf78694f91cb65af4c3726

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3343.md b/dev/programme/delivery/3343.md
new file mode 100644
index 000000000..123642227
--- /dev/null
+++ b/dev/programme/delivery/3343.md
@@ -0,0 +1 @@
+- [#3343](https://github.com/tvofi/heatpump_optimizer/pull/3343) — **open**, R10-HOTFIX-PREPR-SELFTEST-DARWIN: prepr selftest darwin (R10-HOTFIX-PREPR-SELFTEST-DARWIN)
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 5c0c03930..19d2621d3 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -3880,10 +3880,13 @@ EOF
   pfh="/$(echo Users)/exampleuser"
   printf 'evidence: %s/proj/log\n' "$pfh" >"$WB/priv-bad.md"
   printf 'evidence: dev/audit/x.md and ~/proj/log\n' >"$WB/priv-ok.md"
-  got=$(HOME=$pfh USER=exampleuser body_privacy_line "$WB/priv-bad.md"); r=$?
+  # python3 may be a seat shim that resolves its venv under $HOME (macOS), so
+  # under the planted HOME it exits 127; the real interpreter's dir goes first.
+  pfp=$(dirname "$(python3 -I -c 'import sys; print(sys.executable)')"):$PATH
+  got=$(HOME=$pfh USER=exampleuser PATH=$pfp body_privacy_line "$WB/priv-bad.md"); r=$?
   st "$r" 1 "a body naming the host home directory is refused by body_privacy_line"
   st "$(printf 'REFUSE ref_privacy (body): %s' "$got" | cut -c1-26)" "REFUSE ref_privacy (body):" "and the line reads REFUSE ref_privacy (body)"
-  HOME=$pfh USER=exampleuser body_privacy_line "$WB/priv-ok.md" >/dev/null
+  HOME=$pfh USER=exampleuser PATH=$pfp body_privacy_line "$WB/priv-ok.md" >/dev/null
   st $? 0 "a body naming only repository-relative paths and ~/ text passes (null control)"
   case "$flow" in *'PRIVACY_LINE=$(privacy_line)
 step "ref privacy" $? "$PRIVACY_LINE"'*) r=0 ;; *) r=1 ;; esac

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
