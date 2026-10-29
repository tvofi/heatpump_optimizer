# Review packet #2967
head: 2008b0d3c7747610b3d37a5f675a05398311a069
base: e5ddba1fad5e6eccfeceaeaaa249bc459963405b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123734098292 neutral
arch-score / arch-score id=123733837596 success
arm id=123733649173 skipped
budget-raise-gate / budget-raise-gate id=123733837536 success
cancel-superseded id=123733654496 success
codeql / Analyze (actions) id=123733838151 success
codeql / Analyze (javascript-typescript) id=123733837916 success
codeql / Analyze (python) id=123733838154 in_progress
governance / delivery-status id=123733837780 success
governance / delivery-status-publish id=123733841025 skipped
governance / env-matrix id=123733837776 in_progress
governance / instrument-self-tests id=123733837604 in_progress
governance / policy-docs id=123733837555 in_progress
governance / record id=123733840441 skipped
governance / wave-script id=123733837550 success
hassfest / hassfest id=123733837637 success
kernel-points id=123733840024 skipped
prelude id=123733653997 in_progress
refresh id=123733654264 success
tests / arch-instrument id=123734058815 success
tests / briefs id=123733837940 success
tests / browser id=123734058700 in_progress
tests / closure-scope id=123733837711 success
tests / closures id=123734058706 in_progress
tests / coverage id=123734058697 in_progress
tests / fast (3.14) id=123734058789 in_progress
tests / mutation id=123733837698 success
tests / mutation-autofix id=123734233698 skipped
tests / mutation-pins id=123734232508 skipped
tests / nightly-ha id=123734060934 skipped
tests / nightly-status id=123733837632 failure
tests / replay id=123734061241 skipped
tests / typing id=123734058757 success
validate / validate-hacs id=123733837648 success

## Refusals
red-unanswered: concluded red check `tests / nightly-status` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified python3
             python3 with no script argument
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head

FIGURES: 10 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/hassfest.yml b/.github/workflows/hassfest.yml
index 6dc8215aa..919031b38 100644
--- a/.github/workflows/hassfest.yml
+++ b/.github/workflows/hassfest.yml
@@ -1,8 +1,8 @@
 name: Hassfest
 
-# A called workflow of ci.yml's umbrella: the caller owns the triggers, the
-# run-id concurrency group and the grant (`contents: read`). It takes no inputs
-# and no secrets.
+# A called workflow of ci.yml's umbrella and of marketplace.yml's weekly
+# schedule: each caller owns the triggers, the run-id concurrency group and the
+# grant (`contents: read`). It takes no inputs and no secrets.
 on:
   workflow_call:
 
diff --git a/.github/workflows/marketplace.yml b/.github/workflows/marketplace.yml
new file mode 100644
index 000000000..855b2a6b3
--- /dev/null
+++ b/.github/workflows/marketplace.yml
@@ -0,0 +1,33 @@
+name: Marketplace
+
+# The Marketplace's two validators on a clock (#2965 C5). `hassfest` and
+# `validate` are ci.yml's units, run only when the prelude's workset names
+# them, so main could go weeks without a current run for the catalog PR to
+# link. This file calls the same two unit files the way ci.yml does -- caller
+# id == stem, `contents: read`, no inputs, no secrets -- so their job bodies,
+# pinned action SHAs and hassfest's image-pull retry are the ones CI runs,
+# never a copy. A schedule runs main's tree. A red is a failed run: nothing
+# here continues on error. tools/ci/gate.py reads ci.yml's runs alone, so no
+# run of this file is ever a source for `gate`. tests/entities.py pins it.
+
+on:
+  schedule:
+    - cron: "41 3 * * 1"
+  workflow_dispatch:
+
+permissions: {}
+
+# By run id, never cancelled, as ci.yml's.
+concurrency:
+  group: Marketplace-${{ github.run_id }}
+  cancel-in-progress: false
+
+jobs:
+  hassfest:
+    uses: ./.github/workflows/hassfest.yml
+    permissions:
+      contents: read
+  validate:
+    uses: ./.github/workflows/validate.yml
+    permissions:
+      contents: read
diff --git a/.github/workflows/validate.yml b/.github/workflows/validate.yml
index 30b823edb..18407cf8a 100644
--- a/.github/workflows/validate.yml
+++ b/.github/workflows/validate.yml
@@ -1,8 +1,8 @@
 name: Validate
 
-# A called workflow of ci.yml's umbrella: the caller owns the triggers, the
-# run-id concurrency group and the grant (`contents: read`). It takes no inputs
-# and no secrets.
+# A called workflow of ci.yml's umbrella and of marketplace.yml's weekly
+# schedule: each caller owns the triggers, the run-id concurrency group and the
+# grant (`contents: read`). It takes no inputs and no secrets.
 on:
   workflow_call:
 
diff --git a/dev/programme/delivery/2967.md b/dev/programme/delivery/2967.md
new file mode 100644
index 000000000..1eadc8828
--- /dev/null
+++ b/dev/programme/delivery/2967.md
@@ -0,0 +1 @@
+- [#2967](https://github.com/tvofi/heatpump_optimizer/pull/2967) — **open**, R10-MARKETPLACE-EXTRAS: scheduled HACS-action and hassfest runs; D10 Marketplace readiness (R10-MARKETPLACE-EXTRAS)
diff --git a/tests/closures.json b/tests/closures.json
index 8b3f2f339..70e4c6048 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1333,6 +1333,7 @@
    ".github/workflows/governance.yml",
    ".github/workflows/hassfest.yml",
    ".github/workflows/kernel-points.yml",
+   ".github/workflows/marketplace.yml",
    ".github/workflows/merge-main.yml",
    ".github/workflows/nightly.yml",
    ".github/workflows/pages.yml",
@@ -2484,6 +2485,7 @@
    ".github/workflows/governance.yml",
    ".github/workflows/hassfest.yml",
    ".github/workflows/kernel-points.yml",
+   ".github/workflows/marketplace.yml",
    ".github/workflows/merge-main.yml",
    ".github/workflows/nightly.yml",
    ".github/workflows/pages.yml",
diff --git a/tests/entities.py b/tests/entities.py
index 2df47f388..e81a9fbb0 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -19390,6 +19390,9 @@ _NON_GATE_WORKFLOWS = [
     ".github/workflows/pr-contract.yml",
     # Decision 0013 as amended: the budget-raise gate, read for its wiring pins.
     ".github/workflows/budget-raise-gate.yml",
+    # #2965 C5: the weekly caller of hassfest.yml and validate.yml, read for
+    # its wiring pin below.
+    ".github/workflows/marketplace.yml",
 ]
 for _wf in _NON_GATE_WORKFLOWS:
     R.check(
@@ -20096,6 +20099,80 @@ R.check(
          for _wf in [*_NON_GATE_WORKFLOWS, _GOV_WF, _REL_WF]}),
 )
 
+# --- the Marketplace validators on a clock (#2965 C5) -----------------------
+#
+# hassfest.yml and validate.yml run under ci.yml only when the prelude's
+# workset names them, so marketplace.yml calls both on a schedule for the
+# catalog PR to link a current run against main. Read from the parsed file:
+# a cron firing at least weekly (any day-of-month and month, so it fires every
+# week) and `workflow_dispatch`, nothing else; exactly the two callers, each
+# `uses:` its own stem's existing file (ci.yml's naming rule) with
+# `contents: read` alone and no inputs or secrets, so the job bodies, pinned
+# SHAs and hassfest's pull retry are CI's own; no `continue-on-error` at the
+# caller, so a scheduled red is a failed run. The design choice it encodes: a
+# separate caller rather than a `schedule` on ci.yml, whose triggers are pinned
+# above and whose every unit a schedule would run.
+_MP_PATH = Path(".github/workflows/marketplace.yml")
+_MP_TEXT = _MP_PATH.read_text() if _MP_PATH.is_file() else ""
+_MP_UNITS = ("hassfest", "validate")
+
+
+def _mp_defects(text: str) -> "list[str]":
+    doc = _yaml.safe_load(text) or {}
+    on = doc.get(True, doc.get("on"))
+    out = []
+    if not isinstance(on, dict) or set(on) != {"schedule", "workflow_dispatch"}:
+        return [f"triggers {sorted(map(str, on or {}))} (want schedule, workflow_dispatch)"]
+    crons = [str((s or {}).get("cron", "")).split() for s in on.get("schedule") or []]
+    if not crons or any(len(c) != 5 or c[2:4] != ["*", "*"] for c in crons):
+        out.append(f"schedule {crons} does not fire every week")
+    if doc.get("permissions") != {}:
+        out.append(f"top-level permissions {doc.get('permissions')} (want {{}})")
+    jobs = doc.get("jobs") or {}
+    if set(jobs) != set(_MP_UNITS):
+        out.append(f"jobs {sorted(jobs)} (want {list(_MP_UNITS)})")
+    for j in _MP_UNITS:
+        job = jobs.get(j) or {}
+        uses = job.get("uses")
+        if uses != f"./.github/workflows/{j}.yml" or not Path(str(uses)).is_file():
+            out.append(f"{j}: uses {uses}")
+        if job.get("permissions") != {"contents": "read"}:
+            out.append(f"{j}: permissions {job.get('permissions')}")
+        extra = set(job) - {"uses", "permissions"}
+        if extra:
+            out.append(f"{j}: also sets {sorted(extra)}")
+    return out
+
+
+_MP_DEFECTS = _mp_defects(_MP_TEXT)
+# Null controls: each mutation below must be named, so a reader that compares
+# nothing fails.
+_MP_PLANTS = {
+    "a wrong workflow path": _MP_TEXT.replace(
+        "uses: ./.github/workflows/hassfest.yml", "uses: ./.github/workflows/hasfest.yml", 1),
+    "a caller off its stem": _MP_TEXT.replace(
+        "uses: ./.github/workflows/validate.yml", "uses: ./.github/workflows/hassfest.yml", 1),
+    "no schedule": _MP_TEXT.replace("  schedule:\n", "  push:\n", 1),
+    "a monthly cron": _MP_TEXT.replace('* * 1"', '1 * 1"', 1),
+    "a red hidden": _MP_TEXT.replace(
+        "    uses: ./.github/workflows/validate.yml\n",
+        "    uses: ./.github/workflows/validate.yml\n    continue-on-error: true\n", 1),
+    "a widened grant": _MP_TEXT.replace(
+        "      contents: read\n  validate:", "      contents: write\n  validate:", 1),
+    "secrets inherited": _MP_TEXT.replace(
+        "    uses: ./.github/workflows/hassfest.yml\n",
+        "    uses: ./.github/workflows/hassfest.yml\n    secrets: inherit\n", 1),
+}
+_MP_PLANT_MISSED = sorted(k for k, t in _MP_PLANTS.items()
+                          if t == _MP_TEXT or not _mp_defects(t))
+R.check(
+    "marketplace.yml runs CI's own hassfest and validate units weekly and on "
+    "dispatch, read-only, a red never hidden (#2965 C5)",
+    bool(_MP_TEXT) and not _MP_DEFECTS and not _MP_PLANT_MISSED,
+    f"defects={_MP_DEFECTS} plants the reader missed={_MP_PLANT_MISSED}; the "
+    "catalog PR links a current passing run of both against main",
+)
+
 # --- what the closure RECORDER sees: child processes (R9 D14-s5-01) --------
 #
 # The audit hook records this process; a child's reads never reach it, only

