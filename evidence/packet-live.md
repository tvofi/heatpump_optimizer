# Review packet #3160
head: 4cf5a2e6f0c8eb23031cd89e67b809bbbdcaeeca
base: 8247a1ed10f66baaa173d30be1696907c6bbae32

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125082844455 neutral
arch-score / arch-score id=125082646677 success
arm id=125082565273 skipped
budget-raise-gate / budget-raise-gate id=125082646569 success
cancel-superseded id=125082540712 success
codeql / Analyze (actions) id=125082646603 success
codeql / Analyze (javascript-typescript) id=125082646663 success
codeql / Analyze (python) id=125082646623 in_progress
governance / delivery-status id=125082646737 success
governance / delivery-status-publish id=125082648266 skipped
governance / env-matrix id=125082646671 success
governance / instrument-self-tests id=125082646546 success
governance / policy-docs id=125082646583 success
governance / record id=125082648324 skipped
governance / wave-script id=125082646551 success
hassfest / hassfest id=125082646557 success
kernel-points id=125082647932 skipped
prelude id=125082540643 success
refresh id=125082540371 success
tests / arch-instrument id=125082803996 success
tests / briefs id=125082646768 success
tests / browser id=125082803991 success
tests / ci-ratchet id=125089174121 skipped
tests / claims-autofix id=125085112926 skipped
tests / closure-scope id=125082646646 success
tests / closures id=125082804006 success
tests / closures-autofix id=125088108923 skipped
tests / coverage id=125082803929 success
tests / coverage-ratchet id=125089172212 success
tests / fast (3.14) id=125082803940 success
tests / graders-head-copy id=125089172306 success
tests / lane-proofs id=125089172318 success
tests / mutation id=125082646739 success
tests / mutation-autofix id=125082914395 skipped
tests / mutation-pins id=125082914423 skipped
tests / nightly-ha id=125082805330 skipped
tests / nightly-status id=125082646672 success
tests / replay id=125082805944 skipped
tests / typing id=125082804069 success
validate / validate-hacs id=125082646582 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified python3 -W ignore dev/audit/rounds/round6/D11/fix/codeowners_gap.py --self-test
             `ignore` does not look like a path in this tree
  unverified python3 -W ignore dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check
             `ignore` does not look like a path in this tree
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head

FIGURES: 2 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/rounds/round6/D11/fix/codeowners_gap.py b/dev/audit/rounds/round6/D11/fix/codeowners_gap.py
index 1b3480fc2..34daed098 100644
--- a/dev/audit/rounds/round6/D11/fix/codeowners_gap.py
+++ b/dev/audit/rounds/round6/D11/fix/codeowners_gap.py
@@ -369,6 +369,12 @@ ALLOWED_USES = {
     "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1",
     "actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444",
     "actions/download-artifact@37930b1c2abaa49bbe596cd826c3c89aef350131",
+    # The bumped revisions (R10-DEPS-ACTIONS-BUMP): both generations are
+    # admitted while the workflows move from the first to the second.
+    "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
+    "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0",
+    "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1",
+    "actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333",
 }
 # `diff` and `commit` because pinned jobs on `main` use them; `show` and `log`
 # were dropped in round 4 (`git show --output=` writes a file).
@@ -874,6 +880,17 @@ PROBES = [
     ("a listed restore whose list names another file",
      _LISTED(between="printf 'README.md\\0' > \"$RUNNER_TEMP/pinned.list\"")),
     ("a listed restore whose list is truncated by cat", _LISTED(between='cat /dev/null > "$RUNNER_TEMP/pinned.list"')),
+    # A revision on neither list: each bumped SHA one character off.
+    ("checkout one character off its bumped pin", lambda jt: jt.replace(
+        "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5",
+        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b2 # v7.0.1")),
+    ("setup-python one character off its bumped pin", lambda jt: jt.replace(
+        "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6",
+        "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e1 # v7.1.0")),
+    ("setup-node one character off its bumped pin", "\n      - uses: actions/setup-node@"
+     "949feb2413d6458794dcd2491c4babbbce0c15c2 # v7.1.0\n        with:\n          node-version: \"22\"\n"),
+    ("download-artifact one character off its bumped pin", "\n      - uses: actions/download-artifact@"
+     "9000827ccba6bdab643e8b6fd33ac0654aef8333x # v8.0.2\n        with:\n          name: x\n"),
     ("pip install", _run("pip install -r tests/requirements-ci.txt")),
     ("npm ci", _run("npm ci")),
     ("bare tracked path", _run(T + " fast || true")),
@@ -945,6 +962,17 @@ NULLS = [
                                    'cmp README.md README.md')),
     ("download-artifact at its pin", "\n      - uses: actions/download-artifact@"
      "37930b1c2abaa49bbe596cd826c3c89aef350131 # v7\n        with:\n          name: x\n"),
+    ("download-artifact at its bumped pin", "\n      - uses: actions/download-artifact@"
+     "9000827ccba6bdab643e8b6fd33ac0654aef8333 # v8.0.2\n        with:\n          name: x\n"),
+    ("checkout and setup-python at their bumped pins", lambda jt: jt.replace(
+        "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5",
+        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1").replace(
+        "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6",
+        "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0")),
+    ("setup-node at its current pin", "\n      - uses: actions/setup-node@"
+     "a0853c24544627f65ddf259abe73b1d18a591444 # v5\n        with:\n          node-version: \"22\"\n"),
+    ("setup-node at its bumped pin", "\n      - uses: actions/setup-node@"
+     "949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0\n        with:\n          node-version: \"22\"\n"),
     ("a scratch write", _run('echo x > "$RUNNER_TEMP/x.txt"')),
     # The merge queue's base (round-9 process review item 2): a `merge_group`
     # run has no pull request, so the base it restores from is the queue's.
diff --git a/dev/programme/delivery/3160.md b/dev/programme/delivery/3160.md
new file mode 100644
index 000000000..b67274ee4
--- /dev/null
+++ b/dev/programme/delivery/3160.md
@@ -0,0 +1 @@
+- [#3160](https://github.com/tvofi/heatpump_optimizer/pull/3160) — **open**, R10-DEPS-ACTIONS-BUMP: deps actions bump p1 (allowlist accepts old and new revisions) (R10-DEPS-ACTIONS-BUMP)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
