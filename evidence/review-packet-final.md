# Review packet #3307
head: a379c307830addd67fc1abbcde3a71fdb16b8704
base: d2e4d2d10cfe15b9ec51c36422029718e8367f1c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128617440762 success
arch-score / arch-score id=128622036138 success
arm id=128617309036 skipped
budget-raise-gate / budget-raise-gate id=128622064851 success
cancel-superseded id=128622056178 success
codeql id=128622036258 skipped
codeql / Analyze (actions) id=128617405344 success
codeql / Analyze (javascript-typescript) id=128617405254 success
codeql / Analyze (python) id=128617405480 success
gate id=128622035713 success
governance id=128622036193 skipped
governance / delivery-status id=128617405400 success
governance / delivery-status-publish id=128617406838 skipped
governance / env-matrix id=128617405487 success
governance / instrument-self-tests id=128617405604 success
governance / policy-docs id=128617405370 success
governance / record id=128617406353 skipped
governance / wave-script id=128617405375 success
hassfest id=128622073063 skipped
hassfest / hassfest id=128617405159 success
kernel-points id=128622065536 skipped
pr-contract id=128622036630 skipped
pr-contract / pr-contract id=128621741994 success
prelude id=128622035810 success
refresh id=128622035643 success
tests id=128622036063 skipped
tests / arch-instrument id=128617529053 success
tests / briefs id=128617405392 success
tests / browser id=128617529048 success
tests / ci-ratchet id=128621742626 skipped
tests / claims-autofix id=128618686342 skipped
tests / closure-scope id=128617405383 success
tests / closures id=128617529054 success
tests / closures-autofix id=128621742654 skipped
tests / coverage id=128617529094 success
tests / coverage-ratchet id=128617838243 success
tests / fast (3.14) id=128617529198 success
tests / graders-head-copy id=128617838254 success
tests / lane-proofs id=128618685276 success
tests / mutation id=128617405291 success
tests / mutation-autofix id=128617551379 skipped
tests / mutation-pins id=128617550944 skipped
tests / nightly-ha id=128617530077 skipped
tests / nightly-status id=128617405310 success
tests / replay id=128617529734 skipped
tests / typing id=128617529043 success
validate id=128622059691 skipped
validate / validate-hacs id=128617405318 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PATH=<shim>:$PATH bash .claude/hooks/session-start.sh --self-test | tail -1
             `.claude/hooks/session-start.sh` is in the tree at this head

FIGURES: 1 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/hooks/session-start.sh b/.claude/hooks/session-start.sh
index 79a6e7f16..910b4e3bf 100755
--- a/.claude/hooks/session-start.sh
+++ b/.claude/hooks/session-start.sh
@@ -146,6 +146,14 @@ if [ "${1:-}" = "--self-test" ]; then
   # that it ASKS -- that every one of the seven lines is present and none is
   # empty. A hook that silently prints six lines instead of seven is the failure
   # mode here: nobody reads a missing line.
+  # THE CLOCK IS PINNED. `origin/main at:` is git's relative `%cr`, which moves
+  # with the wall clock; the byte comparisons below call the report in
+  # sequence, and one that straddles a tick of the clock ("2 minutes ago" to
+  # "3 minutes ago") fails two rows at once with no defect in the hook. Main
+  # 48af0864a failed that way minutes after its merge (R10-HOTFIX-MAIN-IST-RED).
+  # `GIT_TEST_DATE_NOW` is git's own pin, inherited by every `bash "$0"` below.
+  # A caller's pin stands, so a test can drive a ticking clock through it.
+  : "${GIT_TEST_DATE_NOW:=$(date +%s)}"; export GIT_TEST_DATE_NOW
   out=$(report)
   pass=0; fail=0
   st() { if printf '%s' "$out" | grep -E "$1" >/dev/null; then pass=$((pass+1)); printf '  ok   %s\n' "$2"
diff --git a/dev/programme/delivery/3307.md b/dev/programme/delivery/3307.md
new file mode 100644
index 000000000..d178fbcc1
--- /dev/null
+++ b/dev/programme/delivery/3307.md
@@ -0,0 +1 @@
+- [#3307](https://github.com/tvofi/heatpump_optimizer/pull/3307) — **open**, R10-HOTFIX-MAIN-IST-RED: pin the clock the session-start hook self-test reads (R10-HOTFIX-MAIN-IST-RED)
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 9f2810884..5c0c03930 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -1923,6 +1923,20 @@ if [ "${1:-}" = "--self-test" ]; then
   r=$?; st "$r" 0 "this repository's own wired hooks pass (null control)"
   [ "$r" -eq 0 ] || printf '%s\n' "$hk" | grep -v '^  ok' | sed 's/^/       | /' | tail -12
 
+  # The session-start hook's self-test under a git whose clock advances 70 s per
+  # call: `origin/main at:` is git's relative `%cr`, so a self-test that
+  # compares two reports byte for byte fails on a clock tick, as main did
+  # minutes after a merge (R10-HOTFIX-MAIN-IST-RED, 22 passed 2 failed). The
+  # shim sets the clock only when the self-test has not pinned one, so the row
+  # passes when the self-test pins its own and fails when it does not.
+  tk=$(mktemp -d); mkdir -p "$tk/bin"; gt=$(command -v git)
+  printf '#!/bin/bash\nf="%s/clk"; n=$(( $(cat "$f" 2>/dev/null || echo 0) + 70 )); echo "$n" > "$f"\nexport GIT_TEST_DATE_NOW="${GIT_TEST_DATE_NOW:-$(( $(date +%%s) + n ))}"\nexec "%s" "$@"\n' "$tk" "$gt" > "$tk/bin/git"
+  chmod +x "$tk/bin/git"
+  hk=$(PATH="$tk/bin:$PATH" bash .claude/hooks/session-start.sh --self-test 2>&1); r=$?
+  st "$r" 0 "the session-start self-test passes while git's clock ticks between its reports (null control)"
+  [ "$r" -eq 0 ] || printf '%s\n' "$hk" | grep -v '^  ok' | sed 's/^/       | /' | tail -12
+  rm -rf "$tk"
+
   # A missing matcher, `""` and `"*"` are Claude Code's own "match every tool"
   # spellings, not a pattern to compile -- `"*"` alone threw out of `RegExp`
   # and read as MATCHER BLIND on a group that in fact fires on every edit

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
