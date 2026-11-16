# Review packet #3641
head: 36eb8805ec1eada0b267a5925116a9179bbdf759
base: 030a4d377f9f26f5b8befe5721d86aea454f29e0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133280914783 success
arch-score / arch-score id=133281515511 success
arm id=133280424343 skipped
budget-raise-gate / budget-raise-gate id=133281515258 failure
cancel-superseded id=133281215008 success
codeql id=133281518502 skipped
codeql / Analyze (actions) id=133280834644 success
codeql / Analyze (javascript-typescript) id=133280834695 success
codeql / Analyze (python) id=133280834668 success
gate id=133282149119 failure
governance id=133281517051 skipped
governance / env-matrix id=133280834753 success
governance / instrument-self-tests id=133280834719 success
governance / policy-docs id=133280834879 success
governance / record id=133280837127 skipped
governance / wave-script id=133280835052 success
hassfest id=133281517195 skipped
hassfest / hassfest id=133280834781 success
kernel-points id=133281517148 skipped
pr-contract id=133282150429 skipped
prelude id=133281215149 success
refresh id=133281214753 success
sweep-self id=133282578118 skipped
tests id=133281517978 skipped
tests / arch-instrument id=133281182339 in_progress
tests / briefs id=133280834565 success
tests / browser id=133281182442 success
tests / claims-autofix id=133297452330 skipped
tests / closure-scope id=133280834788 success
tests / closures id=133281182372 in_progress
tests / coverage id=133281182348 in_progress
tests / fast (3.14) id=133281182273 success
tests / mutation id=133280834659 success
tests / mutation-autofix id=133281371745 skipped
tests / mutation-pins id=133281371639 skipped
tests / nightly-ha id=133281184299 skipped
tests / nightly-status id=133280836023 failure
tests / replay id=133281184644 skipped
tests / typing id=133281182311 success
validate id=133281517089 skipped
validate / validate-hacs id=133280834576 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 36eb8805ec1eada0b267a5925116a9179bbdf759 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tools/audit/check_scopes.py --repo . --self-test
             `tools/audit/check_scopes.py` is in the tree at this head
  ok         python3 tools/audit/check_scopes.py --repo . --population
             `tools/audit/check_scopes.py` is in the tree at this head
  ok         python3 tools/audit/check_scopes.py --repo . --ref <ref> --round 11 | grep -c 'still leaves unset'
             `tools/audit/check_scopes.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_owner_criteria.py plants
             `dev/audit/harnesses/r11_owner_criteria.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  unverified git diff origin/main -- dev/governance/config/policy_budgets.json
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 12 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head 5023cde196c43c5bdd4b11789a45780f1c70790a, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/CLAUDE.md b/CLAUDE.md
index cecc4a22f7..c51d09f375 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -154,6 +154,9 @@ individually, because a range reads as complete while covering a fraction:
 | `D14.md` | recurring bug classes |
 | `D15.md` | debugging run from a live diagnostics bundle |
 
+Finder criteria (`owner_criteria`): `D4-criteria.md`,
+`D5-criteria.md`, `D9-criteria.md`, `D10-criteria.md`.
+
 ### Instruments
 
 `tools/audit/seat/` is the instrument inventory, listed in its
diff --git a/dev/audit/config/objective.json b/dev/audit/config/objective.json
index e99b4fa126..1e83a403bd 100644
--- a/dev/audit/config/objective.json
+++ b/dev/audit/config/objective.json
@@ -1,5 +1,5 @@
 {
- "_rule": "The objective function's machine-read half: dev/governance/decisions/0018-objective-function.md defines every key here, and tools/audit/check_scopes.py reads this file (--round at the baseline, --population for the install population). terms are in decision order, layer 1 first. thresholds and owner_criteria hold the owner's values: a null value is unset, makes every comparison or result that needs it undecided, and owes a card (0018 sections 1 and 2); proposed is the orchestrator's proposal and is read by nothing. population lists the axes of the supported install population, each with the tracked source its levels are read from; an axis with kind null is NO-READ and names what would read it. objects maps an object class to the globs whose tracked files are its objects. Only the owner changes this file (CODEOWNERS).",
+ "_rule": "The objective function's machine-read half: dev/governance/decisions/0018-objective-function.md defines every key here, and tools/audit/check_scopes.py reads this file (--round at the baseline, --population for the install population). terms are in decision order, layer 1 first. thresholds and owner_criteria hold the owner's values: a null value is unset, makes every comparison or result that needs it undecided, and owes a card (0018 sections 1 and 2); proposed is the orchestrator's proposal and is read by nothing. population lists the axes of the supported install population, each with the tracked source its levels are read from; an axis with kind null is NO-READ and names what would read it; levels and basis on one are the owner's declared levels and the tracked rows they were taken from, which nothing reads yet. objects maps an object class to the globs whose tracked files are its objects. Only the owner changes this file (CODEOWNERS).",
  "terms": [
   "regret",
   "operation",
@@ -32,7 +32,7 @@
  },
  "thresholds": {
   "product_green_floor": {
-   "value": null,
+   "value": 0.9,
    "proposed": 0.9,
    "unit": "share of concluded runs"
   },
@@ -62,15 +62,15 @@
   }
  },
  "owner_criteria": {
-  "D4": null,
-  "D5": null,
+  "D4": "dev/governance/dimensions/criteria/D4-criteria.md",
+  "D5": "dev/governance/dimensions/criteria/D5-criteria.md",
   "D7": "dev/governance/decisions/0015-the-architects-plan-seam-grouping-and-standing-seats.md",
-  "D9": null,
-  "D10": null
+  "D9": "dev/governance/dimensions/criteria/D9-criteria.md",
+  "D10": "dev/governance/dimensions/criteria/D10-criteria.md"
  },
  "seats": {
-  "evaluator_model": null,
-  "reviewer_model": null
+  "evaluator_model": "claude-fable-5-2",
+  "reviewer_model": "claude-fable-5-2"
  },
  "population": [
   {
@@ -252,13 +252,35 @@
   {
    "axis": "tank_volume",
    "kind": null,
-   "no_read": "a continuous option with no tracked levels: its flow row's minimum, default and maximum, once D12's brief declares them as the levels",
+   "levels": {
+    "min": 50,
+    "default": 200,
+    "max": 1500
+   },
+   "unit": "L",
+   "basis": "the hot-water tank row of the options flow: config_flow.py's CONF_DHW_TANK_VOLUME field, _number(50, 1500, 10, 'L'), its default const.py's DEFAULT_DHW_TANK_VOLUME (200.0). The buffer and wood tank rows are other options, not this axis.",
+   "no_read": "the levels are declared here and nothing reads them: no reader compares them with the flow row they were taken from, so a moved row leaves them stale",
    "builder": "R11-INTAKE-R10-RESIDUE"
   },
   {
    "axis": "house_size",
    "kind": null,
-   "no_read": "a continuous option with no tracked levels: the heated area and heat-loss rows' minimum, default and maximum, once D12's brief declares them as the levels",
+   "levels": {
+    "min": {
+     "heated_area_m2": 20,
+     "heat_loss_kw_per_c": 0.01
+    },
+    "default": {
+     "heated_area_m2": 140,
+     "heat_loss_kw_per_c": 0.15
+    },
+    "max": {
+     "heated_area_m2": 1000,
+     "heat_loss_kw_per_c": 1.0
+    }
+   },
+   "basis": "the heated-area row of the building questionnaire (config_flow.py's CONF_HEATED_AREA field, _number(20, 1000, 5, 'm²'), default const.py's DEFAULT_HEATED_AREA 140.0) and the heat-loss row (CONF_HOUSE_HEAT_LOSS_COEFFICIENT over RANGE_HOUSE_HEAT_LOSS (0.01, 1.0) kW/°C, default DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT 0.15; a two-zone install splits it over the upper and lower rows, defaults 0.08 + 0.07). Each level pairs the two rows' minimum, default or maximum: a declaration, since the flow lets them vary apart.",
+   "no_read": "the levels are declared here and nothing reads them: no reader compares them with the flow rows they were taken from, so a moved row leaves them stale",
    "builder": "R11-INTAKE-R10-RESIDUE"
   }
  ],
diff --git a/dev/audit/config/scopes.json b/dev/audit/config/scopes.json
index 57970e69a5..6aa17cb651 100644
--- a/dev/audit/config/scopes.json
+++ b/dev/audit/config/scopes.json
@@ -498,7 +498,7 @@
    "AGENTS.md",
    "SECURITY.md",
    "dev/README.md",
-   "dev/governance/{dimensions,roles,rules}/*.md",
+   "dev/governance/{dimensions,dimensions/criteria,roles,rules}/*.md",
    "dev/programme/HANDOVER.md",
    "dev/programme/RULINGS.md",
    "dev/programme/plan-*.md",
@@ -559,7 +559,7 @@
       "hacs.json",
       "blueprints/**",
       "docs/img/**",
-      "dev/governance/{dimensions,roles}/*.md"
+      "dev/governance/{dimensions,dimensions/criteria,roles}/*.md"
      ],
      "steps": [
       "M1",
diff --git a/dev/audit/harnesses/r11_owner_criteria.py b/dev/audit/harnesses/r11_owner_criteria.py
new file mode 100644
index 0000000000..da8048d25a
--- /dev/null
+++ b/dev/audit/harnesses/r11_owner_criteria.py
@@ -0,0 +1,134 @@
+#!/usr/bin/env python3
+"""R11-PRE-OWNER-CRITERIA: the round-11 unset gaps, and each criteria file
+applied to one planted finding that meets it and one that does not.
+
+Written by the R11-PRE-OWNER-CRITERIA fixer. Run from a worktree root:
+
+    python3 dev/audit/harnesses/r11_owner_criteria.py gaps <eval-ref> <head-ref>
+    python3 dev/audit/harnesses/r11_owner_criteria.py plants
+
+``gaps``: for each ref, a scratch commit (never a branch) whose
+``dev/audit/yardstick/round11/EVALUATION.json`` marks every ``E11-T-*`` and
+``E11-K-*`` card accepted, then ``tools/audit/check_scopes.py --round 11``
+at it; prints each "still leaves unset" and "unset and no card" gap. Pass
+``<eval-ref>`` as eval/r11's tip and ``<head-ref>`` as a merge of the head
+with it: the eval ref is the null control, printing the gaps the head's
+``objective.json`` must close.
+
+``plants``: one met and one unmet plant per criteria file under
+``dev/governance/dimensions/criteria/``, each applying the statement's own
+rule (D10 Q1's command over a planted copy of ``quality_scale.yaml``, D4
+P2's WCAG ratio, D5 C5's word count, D9 B1's 60 s budget times F = 5).
+Each line prints the plant, the measured value and FAILS or PASSES; a met
+plant must print FAILS and an unmet one PASSES, else the run exits 1.
+"""
+from __future__ import annotations
+
+import json
+import os
+import re
+import subprocess
+import sys
+import tempfile
+
+EVAL = "dev/audit/yardstick/round11/EVALUATION.json"
+YAML = "custom_components/heatpump_optimizer/quality_scale.yaml"
+CRIT = "dev/governance/dimensions/criteria/"
+
+
+def git(*args, **kw):
+    return subprocess.check_output(["git", *args], text=True, **kw).strip()
+
+
+def overlay(ref):
+    ev = json.loads(git("show", f"{ref}:{EVAL}"))
+    n = 0
+    for cid, card in ev["cards"].items():
+        if cid.startswith(("E11-T-", "E11-K-")):
+            card.update(decision="accepted", ruling="scratch overlay")
+            n += 1
+    blob = git("hash-object", "-w", "--stdin", input=json.dumps(ev, indent=1))
+    fd, index = tempfile.mkstemp()
+    os.close(fd)
+    env = dict(os.environ, GIT_INDEX_FILE=index)
+    try:
+        subprocess.check_call(["git", "read-tree", ref], env=env)
+        subprocess.check_call(["git", "update-index", "--cacheinfo", f"100644,{blob},{EVAL}"], env=env)
+        tree = git("write-tree", env=env)
+    finally:
+        os.unlink(index)
+    return git("commit-tree", tree, "-p", ref, "-m", "scratch overlay"), n
+
+
+def gaps(refs):
+    for ref in refs:
+        sha, n = overlay(ref)
+        out = subprocess.run([sys.executable, "tools/audit/check_scopes.py", "--repo", ".", "--ref", sha, "--round", "11"],
+                             capture_output=True, text=True).stdout.splitlines()
+        hit = [ln.strip() for ln in out if "still leaves unset" in ln or "is unset and no card" in ln]
+        print(f"== {ref} (overlay {sha[:10]}, {n} cards accepted): {len(hit)} unset gap(s)")
+        for ln in hit:
+            print("  " + ln.split(" card ", 1)[-1])
+
+
+def q1_rows(text):
+    import yaml
+    rules = yaml.safe_load(text)["rules"]
+    st = lambda v: v if isinstance(v, str) else v["status"]
+    return [k for k, v in rules.items() if st(v) not in ("done", "exempt")
+            or (st(v) == "exempt" and (isinstance(v, str) or not str(v.get("comment", "")).strip()))]
+
+
+def luminance(hexrgb):
+    def lin(c):
+        c /= 255
+        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
+    r, g, b = (int(hexrgb[i:i + 2], 16) for i in (1, 3, 5))
+    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
+
+
+def contrast(fg, bg):
+    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
+    return (a + 0.05) / (b + 0.05)
+
+
+def plants():
+    for f in ("D4", "D5", "D9", "D10"):
+        if not os.path.isfile(f"{CRIT}{f}-criteria.md"):
+            sys.exit(f"{CRIT}{f}-criteria.md is not in this tree")
+    live = open(YAML).read()
+    rows = []
+    todo = live.replace("\n  has-entity-name: done\n", "\n  has-entity-name: todo\n", 1)
+    bare = live.replace("\n  async-dependency: done\n", "\n  async-dependency: exempt\n", 1)
+    assert todo != live and bare != live, "a plant matched nothing"
+    rows += [("D10 Q1", "met: has-entity-name: todo", q1_rows(todo), True),
+             ("D10 Q1", "met: async-dependency exempt, no comment", q1_rows(bare), True),
+             ("D10 Q1", "unmet: the live register", q1_rows(live), False)]
+    for fg, met in (("#777777", True), ("#767676", False)):
+        r = contrast(fg, "#ffffff")
+        rows.append(("D4 P2", f"{'met' if met else 'unmet'}: body text {fg} on #ffffff", round(r, 3), r < 4.5))
+    long = " ".join(["word"] * 41) + "."
+    short = "The cap keeps a slow plan from starving the event loop."
+    for txt, met in ((long, True), (short, False)):
+        n = max(len(s.split()) for s in re.split(r"(?<=[.!?])\s+", txt) if s)
+        rows.append(("D5 C5", f"{'met' if met else 'unmet'}: a comment's longest sentence", n, n > 40))
+    for host_s, met in ((13.0, True), (3.6, False)):
+        pi = host_s * 5
+        rows.append(("D9 B1", f"{'met' if met else 'unmet'}: {host_s} s host solver CPU per cycle, x F=5", pi, pi > 60))
+    bad = 0
+    for crit, plant, value, fails in rows:
+        verdict = bool(value) if isinstance(value, list) else fails
+        want = plant.startswith("met")
+        bad += verdict != want
+        print(f"{crit}\t{plant}\t{value}\t{'FAILS' if verdict else 'PASSES'}{'' if verdict == want else '  <-- WRONG'}")
+    print(f"plants: {len(rows)}, wrong: {bad}")
+    sys.exit(1 if bad else 0)
+
+
+if __name__ == "__main__":
+    if sys.argv[1:2] == ["gaps"] and len(sys.argv) == 4:
+        gaps(sys.argv[2:])
+    elif sys.argv[1:] == ["plants"]:
+        plants()
+    else:
+        sys.exit(__doc__)
diff --git a/dev/governance/config/policy_budgets.json b/dev/governance/config/policy_budgets.json
index a100e9d5b3..c3eab18fc4 100644
--- a/dev/governance/config/policy_budgets.json
+++ b/dev/governance/config/policy_budgets.json
@@ -6,7 +6,7 @@
   "_floor_is_not_the_cost": "always_loaded_tokens measures a session that opens nothing. Moving prose out of CLAUDE.md into a paths:-scoped rule lowers it without deleting a line: across the index split the floor fell by more than half while corpus_tokens moved a fraction of a percent. The two caps below are what stop that drop being recorded as headroom -- corpus_tokens does not move when prose moves, and roles charge a seat for what it loads once it opens a file. Policy: .claude/rules/ratchet-budgets.md.",
   "_band": 500,
   "_band_note": "Applies to the five aggregate caps only -- always_loaded_tokens, corpus_tokens and the three roles caps -- which are compared against cap+_band. Per-file caps below are compared exactly and keep zero headroom deliberately. A cap re-recorded to the measured value every time leaves the NEXT pull request refused by the previous seat's arithmetic rather than by its own prose: measured over 2026-09-08..17, twenty consecutive commits sat at exactly zero corpus headroom, 24 of 39 capped files sit there now, and the corpus still rose across a window where the cap was pinned at measured every commit. The recorded cap is the last measurement; the band is the room a seat works in without touching it. Re-record down when the measurement falls more than _band below the cap, and on any reclassification -- .claude/rules/ratchet-budgets.md.",
-  "corpus_tokens": 67155,
+  "corpus_tokens": 69244,
   "roles": {
     "fixer": {
       "opens": [
@@ -55,7 +55,7 @@
     "tools/audit/briefs/COMMON.md": 114,
     "tools/audit/briefs/D0.md": 76,
     "tools/audit/briefs/D1.md": 72,
-    "tools/audit/briefs/D10.md": 46,
+    "tools/audit/briefs/D10.md": 32,
     "tools/audit/briefs/D11.md": 126,
     "tools/audit/briefs/D12.md": 74,
     "tools/audit/briefs/D13.md": 84,
@@ -85,7 +85,11 @@
     "dev/governance/roles/proposal-triage.md": 40,
     "dev/governance/roles/standing-roster.md": 7,
     "dev/governance/roles/standing-tick.md": 6,
-    "dev/governance/roles/plan-review.md": 24
+    "dev/governance/roles/plan-review.md": 24,
+    "dev/governance/dimensions/criteria/D4-criteria.md": 52,
+    "dev/governance/dimensions/criteria/D9-criteria.md": 49,
+    "dev/governance/dimensions/criteria/D5-criteria.md": 43,
+    "dev/governance/dimensions/criteria/D10-criteria.md": 30
   },
   "files_tokens": {
     ".claude/rules/brief-citations.md": 893,
@@ -109,7 +113,7 @@
     "tools/audit/briefs/COMMON.md": 1697,
     "tools/audit/briefs/D0.md": 1112,
     "tools/audit/briefs/D1.md": 989,
-    "tools/audit/briefs/D10.md": 624,
+    "tools/audit/briefs/D10.md": 410,
     "tools/audit/briefs/D11.md": 1939,
     "tools/audit/briefs/D12.md": 997,
     "tools/audit/briefs/D13.md": 1217,
@@ -141,7 +145,11 @@
     "dev/governance/roles/proposal-triage.md": 563,
     "dev/governance/roles/standing-roster.md": 92,
     "dev/governance/roles/standing-tick.md": 83,
-    "dev/governance/roles/plan-review.md": 304
+    "dev/governance/roles/plan-review.md": 304,
+    "dev/governance/dimensions/criteria/D4-criteria.md": 656,
+    "dev/governance/dimensions/criteria/D9-criteria.md": 641,
+    "dev/governance/dimensions/criteria/D5-criteria.md": 546,
+    "dev/governance/dimensions/criteria/D10-criteria.md": 425
   },
   "_acceptance": "fixtures/policy-rot/budgets.md is capped at 1 line and 1 token on purpose: it is how the budgets check is shown refusing, on both per-file caps. The rest of that directory is deliberately uncapped, which is the check's other half.",
   "_generated": "`.cursor/rules/*.mdc` carries no cap: it is generated from `.claude/rules/` and byte-compared by rules_sync --check, so its size is its source's."
diff --git a/dev/governance/dimensions/D10.md b/dev/governance/dimensions/D10.md
index 45abc0d0e8..b9d0ba2bc6 100644
--- a/dev/governance/dimensions/D10.md
+++ b/dev/governance/dimensions/D10.md
@@ -3,8 +3,9 @@
 Owner's brief: *"Adherence to home assistant integration platinum quality
 requirements."*
 
-Read `COMMON.md` first. Your criterion is the tier
-`dev/audit/config/objective.json` names under `owner_criteria` for D10.
+Read `COMMON.md` first. Your criterion is `criteria/D10-criteria.md`, the
+file `dev/audit/config/objective.json` names under `owner_criteria` for D10:
+a finding names the statement it fails.
 
 ## Method
 
@@ -14,25 +15,10 @@ and the per-rule pages under `rules/`) and execute **one check per rule** —
 an AST or grep over the integration, a stub-driven test, or a documentation
 lookup — recording the command and the result. `diagnostics` is driven with
 every option that can hold a location, the solar location among them.
-Rules, by tier:
-
-- Bronze: action-setup, appropriate-polling, brands, common-modules,
-  config-flow, config-flow-test-coverage, dependency-transparency,
-  docs-actions, docs-triggers, docs-conditions, docs-high-level-description,
-  docs-installation-instructions, docs-removal-instructions,
-  entity-event-setup, entity-unique-id, has-entity-name, runtime-data,
-  test-before-configure, test-before-setup, unique-config-entry.
-- Silver: action-exceptions, config-entry-unloading,
-  docs-configuration-parameters, docs-installation-parameters,
-  entity-unavailable, integration-owner, log-when-unavailable,
-  parallel-updates, reauthentication-flow, test-coverage.
-- Gold: devices, diagnostics, discovery, discovery-update-info,
-  docs-data-update, docs-examples, docs-known-limitations,
-  docs-supported-devices, docs-supported-functions, docs-troubleshooting,
-  docs-use-cases, dynamic-devices, entity-category, entity-device-class,
-  entity-disabled-by-default, entity-translations, exception-translations,
-  icon-translations, reconfiguration-flow, repair-issues, stale-devices.
-- Platinum: async-dependency, inject-websession, strict-typing.
+The rules, by tier, are the rows of
+`custom_components/heatpump_optimizer/quality_scale.yaml` under its
+`# Bronze` to `# Platinum` comments; a checklist rule with no row there is
+itself a finding (`D10-criteria.md`, Q1).
 
 2. Output a tier table (rule, tier, status `done`/`exempt`/`todo`, evidence
 command, result), a draft `quality_scale.yaml` in your report directory,
diff --git a/dev/governance/dimensions/D4.md b/dev/governance/dimensions/D4.md
index 3af07cee19..45ad392303 100644
--- a/dev/governance/dimensions/D4.md
+++ b/dev/governance/dimensions/D4.md
@@ -3,8 +3,9 @@
 Owner's brief: *"UI/UX — the card and the config flow, including grouping and
 setup ergonomics. It should be intuitive, user friendly and look professional."*
 
-Read `COMMON.md` first. Past rendering, your criterion is the one
-`dev/audit/config/objective.json` names under `owner_criteria` for D4.
+Read `COMMON.md` first. Past rendering, your criterion is
+`criteria/D4-criteria.md`, the file `dev/audit/config/objective.json` names
+under `owner_criteria` for D4: a finding names the statement it fails.
 
 ## Method
 
@@ -26,10 +27,9 @@ Read `COMMON.md` first. Past rendering, your criterion is the one
    defaults, selector ranges, validation error keys and their translations,
    help text, and a value of the wrong physical kind typed into each numeric
    option. Score each page, and each `blueprints/` file's inputs, against
-   a written rubric (one theme per page, related fields adjacent, sensible
-   defaults, errors that say what to change, no jargon without help text,
-   field count). Count the steps from install to the first plan and what a
-   new user must know at each.
+   `D4-criteria.md`'s F3, F4, I1 to I3, and count its fields. Count the
+   steps from install to the first plan and what a new user must know at
+   each.
 3. **Professional look.** Consistency of typography, spacing and colour
    tokens across card states; legend and series colours across light/dark;
    alignment of headline numbers; empty and error states.
diff --git a/dev/governance/dimensions/D5.md b/dev/governance/dimensions/D5.md
index 58959d2d46..aa6d83b255 100644
--- a/dev/governance/dimensions/D5.md
+++ b/dev/governance/dimensions/D5.md
@@ -33,8 +33,8 @@ Steps 1 to 3 take their universe from `tools/audit/text_ledger.py` run with
    --dim D5` lists for your cells, true or false of the code it sits on by an
    executed check of that code, never of another comment;
    `text_ledger.py check --plant` refuses a skipped unit; one finding per
-   file, as `D6.md` step 3. Judge concision and
-   precision; list comments that explain *what* the next line obviously does.
+   file, as `D6.md` step 3. Judge each unit by
+   `criteria/D5-criteria.md`, whose statement a finding names.
 
 ## Numbers
 
diff --git a/dev/governance/dimensions/D9.md b/dev/governance/dimensions/D9.md
index e3f6f40e3b..95b3dd9d28 100644
--- a/dev/governance/dimensions/D9.md
+++ b/dev/governance/dimensions/D9.md
@@ -14,7 +14,8 @@ payload size versus the recorder exclusion set; and whether the stress budget
 should become a real gate — CI sets no `STRESS_*` variable, the ms budget is
 retired, and `rss_peak_mb`/`traced_peak_mb` record [every] scenario."*
 
-Read `COMMON.md` first. You have an isolated worktree for instrumentation.
+Read `COMMON.md`, then `criteria/D9-criteria.md`, which budgets each
+cost. You have an isolated worktree for instrumentation.
 
 ## Metric definitions (fixed, so two agents cannot score different things)
 
@@ -53,8 +54,7 @@ Each row reports examined over its metric's universe.
 
 ## Extrapolation
 
-Every Pi statement carries the factor and its source (state it as an
-assumption if it is one) and the M1 number it scales from.
+Every Pi statement scales its M1 number by `D9-criteria.md`'s F.
 
 ## Traps
 
diff --git a/dev/governance/dimensions/criteria/D10-criteria.md b/dev/governance/dimensions/criteria/D10-criteria.md
new file mode 100644
index 0000000000..a9b6387baf
--- /dev/null
+++ b/dev/governance/dimensions/criteria/D10-criteria.md
@@ -0,0 +1,30 @@
+# D10 acceptance criteria: platinum, rule by rule
+
+> Adherence to home assistant integration platinum quality requirements.
+
+— the owner, `D10.md`. The tier is the owner's and `manifest.json` already
+declares it; the register is `quality_scale.yaml` in the integration.
+
+Drafted by a fixer seat under mandate 6893738184 (scope all);
+binding as the owner's words until the owner rewrites them.
+A finding names the statement it fails.
+
+- **Q1 the register.** Every rule of bronze, silver, gold and platinum on
+  Home Assistant's current checklist (`D10.md` step 1) has a row, and every
+  row reads `done` or `exempt`; every `exempt` row carries a `comment`
+  stating why the rule cannot apply. Command, printing each row that fails:
+
+      python3 -c "import yaml,sys;r=yaml.safe_load(open(sys.argv[1]))['rules'];\
+      [print(k,v) for k,v in r.items() if (v if isinstance(v,str) else v['status']) not in ('done','exempt')\
+      or (not isinstance(v,str) and v['status']=='exempt' and not str(v.get('comment','')).strip())\
+      or (v=='exempt')]" custom_components/heatpump_optimizer/quality_scale.yaml
+
+  Pass: no line, and no checklist rule missing a row. Fail: either.
+- **Q2 every site.** A `done` row holds at every site the rule reaches, not
+  at one: every entity, platform, service, flow step, raise and log site the
+  rule's page names. Procedure: `D10.md` step 1's check per rule, run over
+  the enumeration of those sites. Fail: one site that breaks the rule, which
+  makes its row's `done` false.
+- **Q3 exemptions stay true.** An `exempt` row's reason is still true of the
+  code. Fail: the reason contradicted (an exempt discovery row beside a
+  discovery mechanism, for example).
diff --git a/dev/governance/dimensions/criteria/D4-criteria.md b/dev/governance/dimensions/criteria/D4-criteria.md
new file mode 100644
index 0000000000..47e7d7eb6c
--- /dev/null
+++ b/dev/governance/dimensions/criteria/D4-criteria.md
@@ -0,0 +1,52 @@
+# D4 acceptance criteria: the card and the config flow
+
+> UI/UX — the card and the config flow, including grouping and setup
+> ergonomics. It should be intuitive, user friendly and look professional.
+
+— the owner, `D4.md`. Each statement below quotes the words it tests.
+
+Drafted by a fixer seat under mandate 6893738184 (scope all);
+binding as the owner's words until the owner rewrites them.
+A finding names the statement it fails.
+
+Surfaces: every state `node tests/card_drift.mjs --list` prints, at the
+viewports, themes, languages and input modes `D4.md` step 1 names; every
+config-flow and options page; every input of every `blueprints/` file.
+
+## "look professional"
+
+- **P1 no collision.** Overlap of two text boxes, and text past its own box,
+  measured with `getBoundingClientRect`. Pass: 0 px in every surface. Fail:
+  more than 0.5 px anywhere.
+- **P2 contrast.** WCAG 2.2 AA from `getComputedStyle` colours: 4.5:1 for
+  body text, 3:1 for text at 24 px or 18.66 px bold and for chart marks.
+  Fail: one pair below its ratio.
+- **P3 one look.** A series keeps one colour across states within a theme;
+  headline numbers in one row share font size and baseline (±0.5 px). Fail:
+  either differs between two states or two cells.
+- **P4 clean console.** Fail: any console error or uncaught exception.
+
+## "user friendly"
+
+- **F1 hit targets.** Every interactive element is at least 24×24 px, 44×44
+  px under the coarse pointer. Fail: one smaller.
+- **F2 keyboard.** Tab reaches every focusable in visual order with a
+  visible focus ring. Fail: one unreachable, out of order or unmarked.
+- **F3 errors say what to change.** Every validation error key has a string
+  in every `translations/*.json`, naming the field and an accepted value or
+  range. Fail: a missing key, or a string that names neither.
+- **F4 help for every term.** Every field whose label holds a unit, an
+  acronym or a physics term carries a `data_description` in every language.
+  Fail: one without.
+
+## "intuitive"
+
+- **I1 one theme per page.** A page's fields answer the question its title
+  asks; related fields sit adjacent or in one section. Fail: a field another
+  page's title claims, or a related pair split by an unrelated field.
+- **I2 answerable defaults.** On the shortest path from adding the
+  integration to the first plan, every required field has a default or is an
+  entity or area picker. Fail: a required free value with neither. The
+  finding states the path's page count as a measurement.
+- **I3 blueprint inputs.** Every input has a name and a description, and a
+  default where one is safe. Fail: one without.
diff --git a/dev/governance/dimensions/criteria/D5-criteria.md b/dev/governance/dimensions/criteria/D5-criteria.md
new file mode 100644
index 0000000000..1d41d8813f
--- /dev/null
+++ b/dev/governance/dimensions/criteria/D5-criteria.md
@@ -0,0 +1,43 @@
+# D5 acceptance criteria: docs structure and code comments
+
+> Docs structure, flow and content. Verify claims in docs.
+> Comments in code should be concise but precise and easy to understand.
+
+— the owner, `D5.md`. Claims in docs are D6's (`D6.md`).
+
+Drafted by a fixer seat under mandate 6893738184 (scope all);
+binding as the owner's words until the owner rewrites them.
+A finding names the statement it fails.
+
+Comment units: what `python3 tools/audit/text_ledger.py units --dim D5`
+lists for the seat's cells.
+
+## Comments: "concise but precise and easy to understand"
+
+- **C1 precise: true.** Every unit is true of the code it sits on, shown by
+  an executed check of that code (`D5.md` step 4). Fail: a unit the check
+  contradicts.
+- **C2 precise: resolvable.** Every identifier, path and issue a unit names
+  exists (`git grep -n` at the ref, `git ls-files`), and every quantity
+  carries its unit or names a dimensionless quantity. Fail: one that does not.
+- **C3 concise: no restatement.** Delete the unit; if every fact it stated
+  is readable from the identifiers and literals of the statement it sits on,
+  it restated that statement. Fail: such a unit.
+- **C4 concise: why over history.** Split a unit's sentences into those
+  stating a reason, constraint or unit and those recounting history (who
+  measured, which round, what the code used to do). Fail: history sentences
+  are more than half of the unit and deleting them loses no reason or
+  constraint.
+- **C5 easy to understand.** No sentence over 40 words; a term the unit
+  needs is defined in it, in the code it sits on, or in a document it names.
+  Fail: a longer sentence, or an undefined term a reader of the code alone
+  cannot resolve.
+
+## "Docs structure, flow and content"
+
+- **S1 reader paths.** The three paths of `D5.md` step 1 reach their goal.
+  Fail: a dead end, a forward reference, or a needed fact found nowhere.
+- **S2 links.** Every internal link and anchor resolves; every external link
+  answers below HTTP 400. Fail: one that does not.
+- **S3 one home per fact.** No paragraph appears twice across `README.md` and
+  `docs/*.md` (hash of its whitespace-normalised text). Fail: a repeat.
diff --git a/dev/governance/dimensions/criteria/D9-criteria.md b/dev/governance/dimensions/criteria/D9-criteria.md
new file mode 100644
index 0000000000..21975b4678
--- /dev/null
+++ b/dev/governance/dimensions/criteria/D9-criteria.md
@@ -0,0 +1,49 @@
+# D9 acceptance criteria: the Pi-class budget per cost centre
+
+> CPU and memory resource efficiency — target hardware is
+> Raspberry-Pi-class running all of Home Assistant. Measure, don't assert
+> [...] and whether the stress budget should become a real gate
+
+— the owner, `D9.md`. Each cost centre is a metric `D9.md` defines, measured
+by its harness there.
+
+Drafted by a fixer seat under mandate 6893738184 (scope all);
+binding as the owner's words until the owner rewrites them.
+A finding names the statement it fails.
+
+`tests/stress_budgets.json` records the code's own peaks per scenario so
+that `tests/stress.py` can see a regression against them; it is no budget.
+A cost under its recorded row and over a budget here fails; a cost over its
+row and inside every budget here is a regression, not a D9 finding.
+
+## The Pi extrapolation
+
+CPU is measured on the seat's host, pinned to one core with BLAS threads at
+one (`D9.md`, Traps), and multiplied by **F**, the time of
+`tests/stress.py`'s `reference_solve` on one Raspberry Pi 4 core over its
+time on the host. Until a seat measures F on Pi-class hardware, F = 5,
+an assumption (Cortex-A72 at 1.5 GHz against a current desktop core) the
+finding states as one. Bytes are not scaled.
+
+## Budgets (CPU figures are Pi seconds, after F)
+
+- **B1 solver CPU per cycle**: the sum over a cycle's full solves of their
+  process CPU, at most 60 s: a tenth of one core over the shortest
+  optimisation interval the options flow accepts (10 min). Fail: above.
+- **B2 longest GIL hold** on the event loop thread: at most 100 ms, the
+  interval asyncio reports as a slow callback. Fail: above.
+- **B3 loop-thread work per cycle**: at most 0.5 s. Fail: above.
+- **B4 retained growth**: the retained-bytes slope after 200 warm-up cycles,
+  times the 52,560 cycles of a year at the shortest interval, at most 10 MiB
+  (199 bytes per cycle). Fail: above.
+- **B5 memory peak**: per solve, `rss_attrib_mb` as `tests/stress.py`
+  measures it at most 32 MB and the solving process's `rss_peak_mb` at most
+  128 MB. Fail: either above.
+- **B6 payload**: each entity's recorded attributes at most 16,384 bytes of
+  JSON (the recorder's own limit), and all recorded attribute bytes at most
+  5 MB per day at the shortest interval. Fail: either above.
+- **B7 gradient cost**: simulate-step-equivalents per gradient evaluation
+  at most the horizon's step count per simulated trajectory (the owner's
+  "96 ... not ~9,300" at the default horizon). Fail: above.
+
+Full solves per cycle carry no budget of their own: B1 prices them.
diff --git a/dev/programme/delivery/3641.md b/dev/programme/delivery/3641.md
new file mode 100644
index 0000000000..bbb9f3a3a0
--- /dev/null
+++ b/dev/programme/delivery/3641.md
@@ -0,0 +1 @@
+- [#3641](https://github.com/tvofi/heatpump_optimizer/pull/3641) — **open**, R11-PRE-OWNER-CRITERIA: r11 pre owner criteria (R11-PRE-OWNER-CRITERIA)
diff --git a/tests/closure.py b/tests/closure.py
index 232f50e428..8eeaaadb0e 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -1131,6 +1131,7 @@ _CITATION_POLICY = (
     r"\.claude/rules/[a-z0-9-]+\.md",
     r"dev/governance/roles/[A-Za-z0-9_.-]+\.md",
     r"dev/governance/dimensions/[A-Za-z0-9_.-]+\.md",
+    r"dev/governance/dimensions/criteria/[A-Za-z0-9_.-]+\.md",
 )
 
 
diff --git a/tests/closures.json b/tests/closures.json
index 3b9e5c3b5a..e29b8ded09 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1696,6 +1696,10 @@
    "dev/governance/dimensions/D7.md",
    "dev/governance/dimensions/D8.md",
    "dev/governance/dimensions/D9.md",
+   "dev/governance/dimensions/criteria/D10-criteria.md",
+   "dev/governance/dimensions/criteria/D4-criteria.md",
+   "dev/governance/dimensions/criteria/D5-criteria.md",
+   "dev/governance/dimensions/criteria/D9-criteria.md",
    "dev/governance/roles/COMMON.md",
    "dev/governance/roles/architect-planner.md",
    "dev/governance/roles/design-review.md",
@@ -4512,6 +4516,7 @@
    "dev/audit/harnesses/r10_water_setpoint_feedback.py",
    "dev/audit/harnesses/r10_weekday_range_twins.py",
    "dev/audit/harnesses/r11_denominator_planted.py",
+   "dev/audit/harnesses/r11_owner_criteria.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r11_relay_3358_skip.py",
    "dev/audit/harnesses/r9_ci2b_closures_merge.py",
diff --git a/tests/layout.json b/tests/layout.json
index 09758eb01e..0746b077df 100644
--- a/tests/layout.json
+++ b/tests/layout.json
@@ -61,6 +61,7 @@
     "dev/governance/rules/*.md",
     "dev/governance/roles/*.md",
     "dev/governance/dimensions/*.md",
+    "dev/governance/dimensions/criteria/*.md",
     "dev/governance/decisions/*.md",
     "dev/governance/config/*.json"
    ]

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
