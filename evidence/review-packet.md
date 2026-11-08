# Review packet #3333
head: 7e9b464acd5289660b0d5a4ef10c7d609dd50c45
base: bb7dfb9bd6c68548d1a956adc411be91e02965e0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128749058510 success
arch-score / arch-score id=128832354679 success
arm id=128747883084 skipped
budget-raise-gate / budget-raise-gate id=128832344153 success
cancel-superseded id=128832314249 success
codeql id=128832349967 skipped
codeql / Analyze (actions) id=128748879135 success
codeql / Analyze (javascript-typescript) id=128748879132 success
codeql / Analyze (python) id=128748879187 success
gate id=128832313815 success
governance id=128832344024 skipped
governance / delivery-status id=128748879160 success
governance / delivery-status-publish id=128748880175 skipped
governance / env-matrix id=128748879116 success
governance / instrument-self-tests id=128748879208 success
governance / policy-docs id=128748879229 success
governance / record id=128748880193 skipped
governance / wave-script id=128748879143 success
hassfest id=128832340191 skipped
hassfest / hassfest id=128748879140 success
kernel-points id=128832345475 skipped
pr-contract id=128832314864 skipped
pr-contract / pr-contract id=128754318221 success
prelude id=128832336930 success
refresh id=128832314027 success
tests id=128832355651 skipped
tests / arch-instrument id=128749612772 success
tests / briefs id=128748879147 success
tests / browser id=128749612862 success
tests / ci-ratchet id=128754318567 skipped
tests / claims-autofix id=128750547843 skipped
tests / closure-scope id=128748879206 success
tests / closures id=128749612791 success
tests / closures-autofix id=128754319118 skipped
tests / coverage id=128749612814 success
tests / coverage-ratchet id=128750123938 success
tests / fast (3.14) id=128749612825 success
tests / graders-head-copy id=128750123953 success
tests / lane-proofs id=128750792738 success
tests / mutation id=128748879311 success
tests / mutation-autofix id=128749660640 skipped
tests / mutation-pins id=128749660449 skipped
tests / nightly-ha id=128749614055 skipped
tests / nightly-status id=128748879171 success
tests / replay id=128749613519 skipped
tests / typing id=128749612779 success
validate id=128832314862 skipped
validate / validate-hacs id=128748879122 success

## Refusals
none

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
diff --git a/dev/programme/delivery/3333.md b/dev/programme/delivery/3333.md
new file mode 100644
index 000000000..67985347c
--- /dev/null
+++ b/dev/programme/delivery/3333.md
@@ -0,0 +1 @@
+- [#3333](https://github.com/tvofi/heatpump_optimizer/pull/3333) — **open**, R10-POLICY-ROLE-PACK: policy role pack, part 2 (R10-POLICY-ROLE-PACK)
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index bd83906aa..6e8a6939d 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -133,6 +133,20 @@ SETUP_CHECK = "bash tools/audit/seat/cloud-setup.sh --check"
 WAIT_LINE = "Never wait in one tool call longer than 240 s; poll again instead."
 
 
+#: The owner's frugal-routing directive (tvofi 2026-11-06, triage s6-batch127 P398),
+#: stated to every role in one line, verbatim.
+FRUGAL_LINE = ("Discovery reads (search, list, read across files) go through Agent subagents, as the "
+               "frugal routing guard requires; at most 5 inline search operations per prompt; never "
+               "set FRUGAL_ALLOW_INLINE.")
+
+#: The policy pack (tools/policy/role_pack.py) a role reads once in place of its
+#: contract and INSTRUMENTS.md. The payload schema has no per-seat environment, so
+#: the seat renders it itself, with the same renderer the SessionStart hook runs;
+#: the probe has no contract and so no pack.
+PACK_ROLE = {"reviewer": "fix-review", "fixer": "fixer", "designer": "designer",
+             "design-reviewer": "design-review"}
+
+
 class Refusal(Exception):
     pass
 
@@ -193,6 +207,10 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
              f"`{SETUP_CHECK}`, and on REFUSE stop: report its line as your result and start no work. "
              "Run anything heavy in "
              "the background with Monitor and no timeout. " + WAIT_LINE)
+    if role in PACK_ROLE:
+        setup += (f" Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render "
+                  f"{PACK_ROLE[role]} --out $HOME/role-pack.md`, then that file in place of your role "
+                  "contract and INSTRUMENTS.md; on REFUSE read those files as before.")
     if role == "reviewer":
         body = (
             "Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them "
@@ -284,7 +302,7 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
     refs = f"your return refs and refs/heads/{WIP_NS}/{topic} and refs/heads/{WIP_NS}/{topic}-body" if role == "fixer" else "your return refs"
     tail = (f"Never write to any branch except {refs}. Never work around a hook or a refusal; "
             "report it in your result instead.")
-    text = "\n".join([first, setup, body, tail]) + "\n"
+    text = "\n".join([first, setup, body, tail, FRUGAL_LINE]) + "\n"
     if brief:
         text += "\nBrief (snapshotted when this payload was rendered):\n" + brief.rstrip("\n") + "\n"
     return text
@@ -1028,6 +1046,12 @@ def self_test() -> int:
           all(ref_privacy.attribution(t) == [] for t in prompts.values()))
     check("every role's prompt caps one tool call's wait under the 5-minute prompt-cache TTL (R10-FLY-CACHE-PROMPTS)",
           all(WAIT_LINE in t and "240 s" in WAIT_LINE for t in prompts.values()))
+    check("every role's prompt carries the frugal-routing line once, verbatim (P398)",
+          all(sum(line == FRUGAL_LINE for line in t.splitlines()) == 1 for t in prompts.values())
+          and FRUGAL_LINE.startswith("Discovery reads (search, list, read across files) go through Agent subagents"))
+    check("every role with a contract is told to render its pack, the probe is not",
+          all(f"role_pack.py render {PACK_ROLE[r]} " in prompts[r] for r in PACK_ROLE)
+          and "role_pack.py" not in prompts["probe"])
     check("the fixer reads its role file, not CLAUDE.md, which the harness already loaded",
           "dev/governance/roles/fixer.md" in prompts["fixer"] and "CLAUDE.md" not in prompts["fixer"])
     check("every role's setup line runs the toolchain check and stops on its REFUSE (#2709)",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
