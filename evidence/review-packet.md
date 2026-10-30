# Review packet #3011
head: 079fb16467219f6a46a8981ecf28c477c6d52ba3
base: 437f1ba9b521199b360d84effe6a621573d34663

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124337530137 neutral
arch-score / arch-score id=124337217519 success
arm id=124337040743 skipped
budget-raise-gate / budget-raise-gate id=124337217658 success
cancel-superseded id=124337046634 success
codeql / Analyze (actions) id=124337217677 success
codeql / Analyze (javascript-typescript) id=124337217745 success
codeql / Analyze (python) id=124337217777 in_progress
governance / delivery-status id=124337217615 success
governance / delivery-status-publish id=124337219675 skipped
governance / env-matrix id=124337217643 success
governance / instrument-self-tests id=124337217684 in_progress
governance / policy-docs id=124337217750 success
governance / record id=124337219269 skipped
governance / wave-script id=124337217764 success
hassfest / hassfest id=124337217634 success
kernel-points id=124337219817 skipped
prelude id=124337047211 success
refresh id=124337047121 success
tests / arch-instrument id=124337390142 in_progress
tests / briefs id=124337217432 success
tests / browser id=124337390128 success
tests / closure-scope id=124337217707 success
tests / closures id=124337390154 in_progress
tests / coverage id=124337390076 in_progress
tests / fast (3.14) id=124337390180 in_progress
tests / mutation id=124337217489 success
tests / mutation-autofix id=124337435744 skipped
tests / mutation-pins id=124337434514 skipped
tests / nightly-ha id=124337391453 skipped
tests / nightly-status id=124337217528 success
tests / replay id=124337392396 skipped
tests / typing id=124337390030 success
validate / validate-hacs id=124337217791 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 079fb16467219f6a46a8981ecf28c477c6d52ba3 lacks origin/main a6e4a5afe37b5371bb4eb7bfc6c67032b70222be; roster read at origin/main
NOTE body item 86621037: R10-ARCH-DOCS
NOTE body item 152c80d3: R10-ARCH-DOCS
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified - `bus.sh push-verdict`->`push-verdicts`
             no segment of this names a program this check knows
  unverified - `orchestrator_tick.py`->`orch_tick.py`
             no segment of this names a program this check knows
  unverified - `heartbeat.sh --once`->`--one`
             no segment of this names a program this check knows
  unverified - `tests / fast (3.14)`->`(3.13)`
             no segment of this names a program this check knows
  unverified - CI node `gate`->`gates`
             no segment of this names a program this check knows
  unverified - note `handoff-no-pr`->`handoff-no-prs`
             no segment of this names a program this check knows
  unverified - `DhwPlanner`->`DhwPlaner`
             no segment of this names a program this check knows
  unverified - module `sysid`->`sys_id`
             no segment of this names a program this check knows
  unverified - service `simulate_plan`->`simulate_plans`
             no segment of this names a program this check knows
  unverified - ci.yml job `prelude`->`preamble`: 1 finding
             no segment of this names a program this check knows
  unverified - `class InputReader`->`InputReading`: 2 findings, prose and diagram
             no segment of this names a program this check knows
  unverified - gate_lock.py `needs-lease`->`needs_lease`: 1 finding
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         node tools/policy/agreement.mjs --only discovery
             `tools/policy/agreement.mjs` is in the tree at this head
  ok         python3 tests/doc_claims.py --markers
             `tests/doc_claims.py` is in the tree at this head
  ok         HPO_PAGES_OUT=<scratch> node tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         node tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 10 resolved, 12 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/governance/config/corpus_excluded.json b/dev/governance/config/corpus_excluded.json
index 2e9034d52..39fdc77d2 100644
--- a/dev/governance/config/corpus_excluded.json
+++ b/dev/governance/config/corpus_excluded.json
@@ -1,5 +1,5 @@
 {
- "_comment": "Round-evidence exclusions for the named-docs check, in the shape .claude/workflows/cfr_exclusions.json takes (a top-level object of keyed entries beside a _comment). policy_lint.mjs merges `excluded` into its CORPUS_EXCLUDED set at load, so each entry here is a named document the corpus cites -- COMMON.md's report-shape line names REPORT.md, fixer.md's baseline line names BASELINE.md -- that holds a finder report, a round baseline or other data a later seat reads rather than policy prose -- or, for `docs/index.html` (the product page D6.md names), a user-facing page, on the ground policy_lint.mjs's own CORPUS_EXCLUDED holds README.md and DISCLAIMER.md as `user-facing`. A `.md` is never excused by location, so they are excluded one by one rather than by prefix. Or, for `tools/audit/seat/beatd_shims/git`, an executable and not a document: the beat jobs' git shim, which must be named `git` to be found on PATH, so the bare-name pass resolves every policy sentence's word `git` to it.",
+ "_comment": "Round-evidence exclusions for the named-docs check, in the shape .claude/workflows/cfr_exclusions.json takes (a top-level object of keyed entries beside a _comment). policy_lint.mjs merges `excluded` into its CORPUS_EXCLUDED set at load, so each entry here is a named document the corpus cites -- COMMON.md's report-shape line names REPORT.md, fixer.md's baseline line names BASELINE.md -- that holds a finder report, a round baseline or other data a later seat reads rather than policy prose -- or, for `docs/index.html` (the product page D6.md names), a user-facing page, on the ground policy_lint.mjs's own CORPUS_EXCLUDED holds README.md and DISCLAIMER.md as `user-facing`. A `.md` is never excused by location, so they are excluded one by one rather than by prefix. Or, for `tools/audit/seat/beatd_shims/git`, an executable and not a document: the beat jobs' git shim, which must be named `git` to be found on PATH, so the bare-name pass resolves every policy sentence's word `git` to it. Or, for `dev/README.md`, the developer onboarding: it states no policy and binds the reader to CLAUDE.md, while it names the tree's tools and contracts by bare name throughout; excluded by 7ae69419e (R10-ARCH-DOCS-FIRST), and dropped when policy_lint.mjs's resolveCited canon lookup lands.",
  "_why_data_not_source": "These entries must be DATA and not a hardcoded block inside .claude/workflows/policy_lint.mjs. The `policy-docs` job's 'Restore the check source from the base commit' step (#1403) rewrites `.claude/workflows/*.mjs` and `*.py` from the base commit before grading, so a round that ships its evidence files and their exclusions in one branch would have the exclusions erased on CI and fail named-docs; pre-registering them first is refused as FIXTURE VACUOUS, because an exclusion that names no tracked file yet is a destination waiting to be used. This file is outside that pathspec, so it arrives with the branch that adds the evidence it excludes -- the same shape the #1403 fix's own comment names for policy_budgets.json, policy_known_bad.json and cfr_exclusions.json: a grader's criteria are data, and a fixture's expected outcome has to be the data under test.",
  "_fail_closed": "A missing or unparseable file, or a non-array `excluded`, makes policy_lint.mjs merge nothing, and the cited-but-unexcluded evidence files then re-arm named-docs on the production run -- so this list cannot silently drop an entry; the check that consumes it notices.",
  "excluded": [
diff --git a/dev/programme/carries/carry-1645.json b/dev/programme/carries/carry-1645.json
index c5e052ac1..f4eaff84e 100644
--- a/dev/programme/carries/carry-1645.json
+++ b/dev/programme/carries/carry-1645.json
@@ -16,7 +16,7 @@
       "effect": "narrows",
       "control": "Established by measurement with its null control. check_simulate_plan_fields's own null control (tests/doc_claims.py:605-619) re-runs the field-extraction regex on a text copy with one documented field's backtick literal deleted, and asserts the deletion is caught -- but it assumes the anchor regex (`r\"\\*\\*`simulate_plan`\\*\\*.*?Fields,\\s*\\n?all optional:\\s*(.*?)\\.\\s*An empty\"`) still matches the mutated text. Perturbing the anchor itself (renaming its lead-in phrase from \"Fields,\" to \"Fields:\" in a copy of docs/configuration.md, leaving the schema and every documented field untouched) makes `re.search` return None; `_mutated_span.group(1)` at tests/doc_claims.py:612 then raises `AttributeError: 'NoneType' object has no attribute 'group'` instead of a clean `R.check(..., False, ...)` FAIL -- confirmed by running the same regex pair against the perturbed text outside the harness. check_initial_setup_menu has the same shape one line earlier: `section = text.split(\"## Initial setup\", 1)[1]...` (tests/doc_claims.py:487) raises `IndexError: list index out of range` if that heading is ever renamed, before its first `R.check` anchor runs -- confirmed the same way, renaming the heading to \"## Initial configuration\" in a text copy. The null control for each check demonstrates it fires on the CONTENT mutation it was written for (a dropped field, the pre-v6.6.5 wizard shape); neither demonstrates what happens when the anchor the extraction depends on stops matching, which is the actual perturbation a doc rewrite is most likely to make.",
       "remeasure": "Do not trust this paragraph's line numbers: they are measured at this PR's head (docs/configuration.md, tests/doc_claims.py) and a later stage is judged against its own merge base. Re-open tests/doc_claims.py's check_initial_setup_menu and check_simulate_plan_fields, re-locate the anchor regex/split call each depends on, and re-run the same two perturbations (rename the \"## Initial setup\" heading; rename \"Fields,\" to \"Fields:\" in the simulate_plan sentence) against a copy of docs/configuration.md at your merge base to confirm each still raises rather than reporting a clean FAIL. If either barrier already wraps its anchor lookups (an `if m is None: R.check(anchor, False, ...); return` guard, or the equivalent), the finding is void there and only applies to the arm that still crashes.",
-      "brief": "Before folding tests/doc_claims.py's check_initial_setup_menu (tests/doc_claims.py:476) and check_simulate_plan_fields (tests/doc_claims.py:565) into the I5 barrier -- or writing new barrier arms in the same style -- guard every anchor lookup (a `re.search` result used before a None check, a `str.split(...)[1]` on a heading that might move) so a doc rewrite that breaks the anchor produces a named `R.check` FAIL (\"the anchor this check depends on no longer matches\") rather than an uncaught exception that aborts the whole doc_claims.py run and hides every other arm's result behind a traceback. Demonstrate the guard by reproducing both crashes above against the unguarded code first, then showing the guarded version reports a clean FAIL under the same perturbation."
+      "brief": "Before folding tests/doc_claims.py's check_initial_setup_menu (tests/doc_claims.py:479) and check_simulate_plan_fields (tests/doc_claims.py:570) into the I5 barrier -- or writing new barrier arms in the same style -- guard every anchor lookup (a `re.search` result used before a None check, a `str.split(...)[1]` on a heading that might move) so a doc rewrite that breaks the anchor produces a named `R.check` FAIL (\"the anchor this check depends on no longer matches\") rather than an uncaught exception that aborts the whole doc_claims.py run and hides every other arm's result behind a traceback. Demonstrate the guard by reproducing both crashes above against the unguarded code first, then showing the guarded version reports a clean FAIL under the same perturbation."
     },
     {
       "from": "R9-F8.3 (handoff/r9-f8-docs-3): the doc-claims lane's PR, which lands five more code-fact arms in tests/doc_claims.py before the barrier does -- check_quick_setup_promises (thermal_model facts from config_flow.py), check_card_version_tracks_stamp (VERSION + tools/release/stamp.py's rewrite_card_version against the bundled card JS), check_curve_bias_no_weekly_bound (learner observation facts), check_readme_currency_claim (resolve_currency facts), and check_service_fields (the live services registry vs the Services paragraphs, the I5 leaf this barrier was written for)",
diff --git a/dev/programme/delivery/3011.md b/dev/programme/delivery/3011.md
new file mode 100644
index 000000000..65e6d4d13
--- /dev/null
+++ b/dev/programme/delivery/3011.md
@@ -0,0 +1 @@
+- [#3011](https://github.com/tvofi/heatpump_optimizer/pull/3011) — **open**, R10-ARCH-DOCS-WIRING: architecture-doc wiring test and its carries (R10-ARCH-DOCS-WIRING)
diff --git a/docs/img/card/advisor-dark.png b/docs/img/card/advisor-dark.png
index 1479a35eb..f2b75f9a0 100644
Binary files a/docs/img/card/advisor-dark.png and b/docs/img/card/advisor-dark.png differ
diff --git a/docs/img/card/advisor-light.png b/docs/img/card/advisor-light.png
index 924405cfa..b18909276 100644
Binary files a/docs/img/card/advisor-light.png and b/docs/img/card/advisor-light.png differ
diff --git a/docs/img/card/health-dark.png b/docs/img/card/health-dark.png
index 78ce2ca5d..963c62997 100644
Binary files a/docs/img/card/health-dark.png and b/docs/img/card/health-dark.png differ
diff --git a/docs/img/card/health-light.png b/docs/img/card/health-light.png
index 7f206420c..3e705efcb 100644
Binary files a/docs/img/card/health-light.png and b/docs/img/card/health-light.png differ
diff --git a/docs/img/card/pages.json b/docs/img/card/pages.json
new file mode 100644
index 000000000..615d43cca
--- /dev/null
+++ b/docs/img/card/pages.json
@@ -0,0 +1,75 @@
+{
+  "_comment": "Written by HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs beside the pictures it takes; tests/card_browser.mjs compares the live card to it (P40) and tests/doc_claims.py compares each PNG to it. Never edit by hand.",
+  "figures": {
+    "tile-light.png": {
+      "width": 900,
+      "height": 866,
+      "structure": "41632c2c073d954f"
+    },
+    "plan-light.png": {
+      "width": 1056,
+      "height": 792,
+      "structure": "f55c665ed0d6f3c7"
+    },
+    "plan-why-light.png": {
+      "width": 1056,
+      "height": 792,
+      "structure": "c595d50cf91af7f6"
+    },
+    "setup-light.png": {
+      "width": 1056,
+      "height": 714,
+      "structure": "5d1eaaf120c1d002"
+    },
+    "savings-light.png": {
+      "width": 1056,
+      "height": 164,
+      "structure": "07e4bcc9dd8c2456"
+    },
+    "advisor-light.png": {
+      "width": 1056,
+      "height": 708,
+      "structure": "f6e80bdb46caba23"
+    },
+    "health-light.png": {
+      "width": 1056,
+      "height": 792,
+      "structure": "1c76c65ce6e7146e"
+    },
+    "tile-dark.png": {
+      "width": 900,
+      "height": 866,
+      "structure": "41632c2c073d954f"
+    },
+    "plan-dark.png": {
+      "width": 1056,
+      "height": 792,
+      "structure": "f55c665ed0d6f3c7"
+    },
+    "plan-why-dark.png": {
+      "width": 1056,
+      "height": 792,
+      "structure": "c595d50cf91af7f6"
+    },
+    "setup-dark.png": {
+      "width": 1056,
+      "height": 714,
+      "structure": "5d1eaaf120c1d002"
+    },
+    "savings-dark.png": {
+      "width": 1056,
+      "height": 164,
+      "structure": "07e4bcc9dd8c2456"
+    },
+    "advisor-dark.png": {
+      "width": 1056,
+      "height": 708,
+      "structure": "f6e80bdb46caba23"
+    },
+    "health-dark.png": {
+      "width": 1056,
+      "height": 792,
+      "structure": "1c76c65ce6e7146e"
+    }
+  }
+}
diff --git a/docs/img/card/plan-dark.png b/docs/img/card/plan-dark.png
index 41ee5e112..c9e18f72a 100644
Binary files a/docs/img/card/plan-dark.png and b/docs/img/card/plan-dark.png differ
diff --git a/docs/img/card/plan-light.png b/docs/img/card/plan-light.png
index a121bda93..d037f4f16 100644
Binary files a/docs/img/card/plan-light.png and b/docs/img/card/plan-light.png differ
diff --git a/docs/img/card/plan-why-dark.png b/docs/img/card/plan-why-dark.png
index af398d381..71e4b7f85 100644
Binary files a/docs/img/card/plan-why-dark.png and b/docs/img/card/plan-why-dark.png differ
diff --git a/docs/img/card/plan-why-light.png b/docs/img/card/plan-why-light.png
index 28ee78588..d2b62b017 100644
Binary files a/docs/img/card/plan-why-light.png and b/docs/img/card/plan-why-light.png differ
diff --git a/docs/img/card/savings-dark.png b/docs/img/card/savings-dark.png
index 9755ab781..d36170a83 100644
Binary files a/docs/img/card/savings-dark.png and b/docs/img/card/savings-dark.png differ
diff --git a/docs/img/card/savings-light.png b/docs/img/card/savings-light.png
index 5e99777a3..9d4dc1aca 100644
Binary files a/docs/img/card/savings-light.png and b/docs/img/card/savings-light.png differ
diff --git a/docs/img/card/setup-dark.png b/docs/img/card/setup-dark.png
index 03d8671ab..4ed00ba8c 100644
Binary files a/docs/img/card/setup-dark.png and b/docs/img/card/setup-dark.png differ
diff --git a/docs/img/card/setup-light.png b/docs/img/card/setup-light.png
index b32168b54..70f9600a9 100644
Binary files a/docs/img/card/setup-light.png and b/docs/img/card/setup-light.png differ
diff --git a/docs/img/card/tile-dark.png b/docs/img/card/tile-dark.png
index b47f36e31..2a57fa858 100644
Binary files a/docs/img/card/tile-dark.png and b/docs/img/card/tile-dark.png differ
diff --git a/docs/img/card/tile-light.png b/docs/img/card/tile-light.png
index f2b4a3b34..b3a22ec23 100644
Binary files a/docs/img/card/tile-light.png and b/docs/img/card/tile-light.png differ
diff --git a/docs/index.html b/docs/index.html
index e07066520..e8c0c22a4 100644
--- a/docs/index.html
+++ b/docs/index.html
@@ -306,7 +306,7 @@ footer .brand { font-size: 1rem }
     <figure role="tabpanel" id="p-adv" aria-labelledby="t-adv" hidden style="margin:0">
       <div class="stage"><picture>
         <source media="(prefers-color-scheme: dark)" srcset="img/card/advisor-dark.png" data-theme-src="dark" data-repo="docs/img/card/advisor-dark.png">
-        <img src="img/card/advisor-light.png" data-repo="docs/img/card/advisor-light.png" width="1056" height="616" loading="lazy" alt="The card's Advisor tab: a Worth doing section of ranked rows, each with one button, a More advice section of advisors that are off by default, then the ranking of sensors that would tighten the model">
+        <img src="img/card/advisor-light.png" data-repo="docs/img/card/advisor-light.png" width="1056" height="708" loading="lazy" alt="The card's Advisor tab: a Worth doing section of ranked rows, each with one button, a More advice section of advisors that are off by default, then the ranking of sensors that would tighten the model">
       </picture></div>
       <figcaption data-src="docs/dashboard-card.md#the-advisor-page">The Advisor tab is an inbox: what the integration would change to make your plan cheaper, ranked by what each change is worth per month.</figcaption>
     </figure>
diff --git a/tests/card_browser.mjs b/tests/card_browser.mjs
index 958876ccb..50c6ef82b 100644
--- a/tests/card_browser.mjs
+++ b/tests/card_browser.mjs
@@ -651,7 +651,8 @@ async function cardPages({ browser, check, plan, out }) {
           : page.locator("heatpump-optimizer-card dialog[open]");
         const shot = await target.screenshot({ type: "png" });
         const name = `${view}-${theme}.png`;
-        shots.push({ name, ok: shot[0] === 0x89 && shot[1] === 0x50 && shot.length > 10_000, bytes: shot.length });
+        shots.push({ name, ok: shot[0] === 0x89 && shot[1] === 0x50 && shot.length > 10_000, bytes: shot.length,
+          figure: { width: shot.readUInt32BE(16), height: shot.readUInt32BE(20), structure: await pageStructure(page, view) } });
         if (out) {
           writeFileSync(path.join(out, name), shot);
           console.log(`  wrote page ${name} ${shot.length} bytes -> ${out}`);
@@ -665,6 +666,67 @@ async function cardPages({ browser, check, plan, out }) {
   check("U5 page-screenshot mode takes the tile, all five pages and the idle-step hover in both themes",
     pics.length === 14 && shots.every((s) => s.ok),
     shots.filter((s) => !s.ok).map((s) => `${s.name} ${s.bytes} bytes`).join(", "));
+  const taken = Object.fromEntries(pics.map((s) => [s.name, s.figure]));
+  if (out) {
+    writeFileSync(path.join(out, FIGURES_MANIFEST), JSON.stringify({ _comment: FIGURES_COMMENT, figures: taken }, null, 2) + "\n");
+    console.log(`  wrote ${FIGURES_MANIFEST} -> ${out}`);
+    return;
+  }
+  // P40: the committed pictures are of the card this tree ships. Each one's
+  // size and the shape of the page it shows are recorded beside it; the
+  // pixels are not compared, because Chromium's raster differs across
+  // machines while layout and structure do not.
+  const recorded = JSON.parse(readFileSync(path.join(repo, "docs/img/card", FIGURES_MANIFEST), "utf8")).figures;
+  const stale = figureDrift(taken, recorded);
+  check("P40 every committed card page figure has the size and structure of the page this card draws",
+    !stale.length, stale.join("; ") + " -- regenerate: HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs");
+  const one = Object.keys(taken)[0];
+  const moved = { ...taken, [one]: { ...taken[one], height: taken[one].height + 1 } };
+  check("P40 red case: a figure one pixel taller than the page is stale; the run's own figures are not (null control)",
+    figureDrift(moved, taken).length === 1 && !figureDrift(taken, taken).length);
+}
+
+const FIGURES_MANIFEST = "pages.json";
+const FIGURES_COMMENT = "Written by HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs beside the pictures it takes; "
+  + "tests/card_browser.mjs compares the live card to it (P40) and tests/doc_claims.py compares each PNG to it. "
+  + "Never edit by hand.";
+
+/** The visible element tree of the page a figure shows, as a digest: tag and
+ * sorted classes in document order, not descending into an svg, whose path
+ * count follows the plan rather than the page's shape. */
+async function pageStructure(page, view) {
+  const shape = await page.evaluate((tile) => {
+    const root = window.__card.shadowRoot;
+    const out = [];
+    const walk = (el) => {
+      for (const c of el.children) {
+        const cs = getComputedStyle(c);
+        if (cs.display === "none" || cs.visibility === "hidden" || c.tagName === "STYLE") continue;
+        out.push(c.tagName.toLowerCase() + [...c.classList].sort().map((k) => "." + k).join(""));
+        if (c.tagName.toLowerCase() !== "svg") walk(c);
+      }
+    };
+    walk(tile ? root : root.querySelector("dialog[open]"));
+    return out.join(" ");
+  }, view === "tile");
+  return createHash("sha256").update(shape).digest("hex").slice(0, 16);
+}
+
+/** Stale or missing figures: `taken` (this run) against `recorded` (the
+ * committed manifest), both name -> {width, height, structure}. */
+function figureDrift(taken, recorded) {
+  const out = [];
+  for (const name of Object.keys({ ...taken, ...recorded }).sort()) {
+    const a = taken[name], b = recorded[name];
+    if (!b) out.push(`${name}: the card draws it and no committed figure records it`);
+    else if (!a) out.push(`${name}: recorded, and the card no longer draws it`);
+    else {
+      for (const k of ["width", "height", "structure"]) {
+        if (a[k] !== b[k]) out.push(`${name}: ${k} ${b[k]} committed, ${a[k]} drawn`);
+      }
+    }
+  }
+  return out;
 }
 
 // ---- the in-page instrument (serialised into the page) ---------------------
diff --git a/tests/closure.py b/tests/closure.py
index bba004d32..96360dac4 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -687,6 +687,28 @@ INERT_EXCEPT = (
     # doc_claims.py's recorded closure.
     "docs/img/brand/coffee.svg",
     "dev/programme/rosters/wave-r10-groups.json",
+    # R10-ARCH-DOCS-WIRING: the card-figure arm opens the page-figure record and
+    # every page PNG it lists, to read the IHDR against it (the two light PNGs
+    # the image-size arm already opens are above), and the doc-wiring arm opens
+    # each script the two pages pass an argument to, to find that argument as a
+    # word of it. Same route: the prefixes stay INERT, the files move to
+    # doc_claims.py's recorded closure.
+    "docs/img/card/pages.json",
+    "docs/img/card/advisor-dark.png",
+    "docs/img/card/health-dark.png",
+    "docs/img/card/health-light.png",
+    "docs/img/card/plan-dark.png",
+    "docs/img/card/plan-light.png",
+    "docs/img/card/plan-why-dark.png",
+    "docs/img/card/savings-dark.png",
+    "docs/img/card/savings-light.png",
+    "docs/img/card/setup-dark.png",
+    "docs/img/card/setup-light.png",
+    "docs/img/card/tile-dark.png",
+    "docs/img/card/tile-light.png",
+    "tools/audit/seat/bus.sh",
+    "tools/audit/seat/cloud_relay.sh",
+    "tools/audit/seat/heartbeat.sh",
     "DISCLAIMER.md",
     "blueprints/automation/charge_ev_from_grid_headroom.yaml",
     "blueprints/automation/economy_mode_on_price_peak.yaml",
diff --git a/tests/closures.json b/tests/closures.json
index ceb95f3f0..c05c31d2b 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1096,6 +1096,8 @@
    "tests/hastub/homeassistant/util/dt.py"
   ],
   "tests/doc_claims.py": [
+   ".github/workflows/ci.yml",
+   ".github/workflows/tests.yml",
    "DISCLAIMER.md",
    "README.md",
    "VERSION",
@@ -1204,10 +1206,23 @@
    "docs/ecl110.md",
    "docs/how-it-works.md",
    "docs/img/brand/coffee.svg",
+   "docs/img/card/advisor-dark.png",
    "docs/img/card/advisor-light.png",
    "docs/img/card/card-plan-chart.png",
+   "docs/img/card/health-dark.png",
+   "docs/img/card/health-light.png",
    "docs/img/card/options-hot-water-by-day.png",
+   "docs/img/card/pages.json",
+   "docs/img/card/plan-dark.png",
+   "docs/img/card/plan-light.png",
+   "docs/img/card/plan-why-dark.png",
    "docs/img/card/plan-why-light.png",
+   "docs/img/card/savings-dark.png",
+   "docs/img/card/savings-light.png",
+   "docs/img/card/setup-dark.png",
+   "docs/img/card/setup-light.png",
+   "docs/img/card/tile-dark.png",
+   "docs/img/card/tile-light.png",
    "docs/img/model/card-dhw-band-weekly.png",
    "docs/img/model/dhw-demand-windows.svg",
    "docs/img/model/dhw-store-decay.svg",
@@ -1222,6 +1237,7 @@
    "docs/setup.md",
    "docs/site/docs.css",
    "tests/doc_claims.py",
+   "tests/gate_lock.py",
    "tests/harness.py",
    "tests/hastub/homeassistant/__init__.py",
    "tests/hastub/homeassistant/components/__init__.py",
@@ -1267,6 +1283,11 @@
    "tools/audit/archscore/metrics/__init__.py",
    "tools/audit/archscore/metrics/card.py",
    "tools/audit/archscore/metrics/common.py",
+   "tools/audit/seat/bus.sh",
+   "tools/audit/seat/cloud_relay.sh",
+   "tools/audit/seat/heartbeat.sh",
+   "tools/audit/seat/ledger.py",
+   "tools/policy/rules_sync.mjs",
    "tools/release/stamp.py",
    "tools/site/build_docs.mjs",
    "tools/site/package-lock.json",
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 91dc8acb2..51138864f 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -50,6 +50,8 @@ from __future__ import annotations
 
 import ast
 import importlib.util
+import collections
+import itertools
 import json
 import os
 import pathlib
@@ -3036,23 +3038,29 @@ def roster_stages(path: pathlib.Path = ROSTER) -> dict[str, str] | None:
     return {g["group"]: (g.get("resume") or {}).get("stage", "") for g in json.loads(path.read_text())["groups"]}
 
 
-def _units(text: str) -> list[tuple[str, bool]]:
-    """(unit, under a marked heading) for prose outside fences: a list item, a table row, a heading or a paragraph."""
-    out: list[tuple[str, bool]] = []
-    heads: list[tuple[int, bool]] = []
+def _groups(text: str, kind: str = "target") -> list[str]:
+    """The roster groups every well-formed marker of `kind` in `text` names."""
+    return [g for m in _MARKER.finditer(text) if m.group(1) == kind for g in m.group(2).split(", ")]
+
+
+def _units(text: str) -> list[tuple[str, list[str]]]:
+    """(unit, groups of the marked headings above it) for prose outside fences: a list item, a table row, a heading
+    or a paragraph."""
+    out: list[tuple[str, list[str]]] = []
+    heads: list[tuple[int, list[str]]] = []
     cur: list[str] = []
 
     def flush() -> None:
         if cur:
-            out.append(("\n".join(cur), any(m for _, m in heads)))
+            out.append(("\n".join(cur), [g for _, gs in heads for g in gs]))
             cur.clear()
 
     for line in _FENCE.sub("", text).splitlines():
         h = re.match(r"(#+)\s", line)
         if h:
             flush()
-            heads[:] = [x for x in heads if x[0] < len(h.group(1))] + [(len(h.group(1)), bool(_MARKER.search(line)))]
-            out.append((line, any(m for _, m in heads)))
+            heads[:] = [x for x in heads if x[0] < len(h.group(1))] + [(len(h.group(1)), _groups(line))]
+            out.append((line, [g for _, gs in heads for g in gs]))
         elif not line.strip():
             flush()
         elif line.lstrip().startswith("|") or re.match(r"\s*(?:[-*+]|\d+\.)\s", line):
@@ -3169,12 +3177,10 @@ def doc_wiring_findings(docs: dict[str, str], tree: set[str], roster, style_docs
         if stages is None:
             out.append(f"{len(groups)} marker(s) present and no roster to resolve them against")
         else:
-            for name, kind, g in groups:
-                if g not in stages:
-                    out.append(f"{name}: [{kind}: {g}] names no group in the roster")
-                elif stages[g] == "done":
-                    # (c) report-only: resolving is R10-ARCH-DOCS's end-of-round predicate
-                    notes.append(f"{name}: [{kind}: {g}] names a done group; R10-ARCH-DOCS resolves it")
+            out += [f"{name}: [{kind}: {g}] names no group in the roster" for name, kind, g in groups if g not in stages]
+            # (c) report-only: resolving is R10-ARCH-DOCS's end-of-round predicate
+            notes += [f"{r['doc']}:{r['line']}: {r['marker']} names only done groups; R10-ARCH-DOCS resolves it"
+                      for r in marker_census(docs, stages) if r["due"]]
     # (e) no hex colour and no init directive inside a mermaid block
     for name, text in {**(style_docs or {}), **docs}.items():
         for info, body in _FENCE.findall(text):
@@ -3186,6 +3192,228 @@ def doc_wiring_findings(docs: dict[str, str], tree: set[str], roster, style_docs
     return out, notes
 
 
+def marker_census(docs: dict[str, str], stages: dict[str, str]) -> list[dict]:
+    """Every marker in the documents, in order, with each named group's roster stage (`absent` when the roster has
+    no such group). `due`: every group it names is done, so the marker is unresolved (R10-ARCH-DOCS-WIRING item 2).
+    A marker quoted in inline code is the grammar being described, not a marker."""
+    rows = []
+    for name, text in docs.items():
+        bare = re.sub(r"`[^`\n]+`", lambda m: " " * len(m.group(0)), text)
+        for m in _MARKER.finditer(bare):
+            st = {g: stages.get(g, "absent") for g in m.group(2).split(", ")}
+            rows.append({"doc": name, "line": bare.count("\n", 0, m.start()) + 1, "marker": m.group(0),
+                         "stages": st, "due": all(v == "done" for v in st.values())})
+    return rows
+
+
+# (f)-(i): what the architecture page and the onboarding name beyond a path -- a command's arguments, a module's
+# symbols, a workflow job, a ledger kind, a diagram node -- each resolved in the artifact that defines it (fixer.md
+# step 11), never in a list kept here. Read from these two only: README.md names the user's own files
+# (`configuration.yaml`), which no tree resolves.
+NAMED_DOCS = ("docs/architecture.md", "dev/README.md")
+PKG_REL = "custom_components/heatpump_optimizer"
+LEDGER = "tools/audit/seat/ledger.py"
+_FILE = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)*[\w-]+\.(?:py|sh|mjs|js|json|ya?ml|md|toml))(?![\w/-])")
+# the lower-case kebab word: an argument after a script, and the diagram node that names a job; the job resolver,
+# not this shape, decides whether that job exists
+_WORD = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
+_ARG = re.compile(r"--[a-z][\w-]*|" + _WORD.pattern)
+_CAMEL = re.compile(r"(?<![\w.])([A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+)(?:\.([a-z_]\w*))?")
+_CHECK_NAME = re.compile(r"([\w-]+) / ([\w-]+)(?: \(([^)]+)\))?")
+_KIND = re.compile(r"[a-z]+(?:-[a-z]+)+")
+_KIND_NOTE = re.compile(r"\b([a-z]+(?:-[a-z]+)+) (?:opens|closes)\b|\bopens ([a-z]+(?:-[a-z]+)+)")
+_LABEL = re.compile(r"\b[A-Za-z_]\w*\s*(?:\(\[|\[\(|\(\(|\{\{|\[\[|\[|\(|\{)\"([^\"]*)\"|--\s*\"([^\"]*)\"\s*-+>|\|\"([^\"]*)\"\|")
+
+
+def _symbols(src: str) -> dict[str, set[str]]:
+    """Top-level name -> its method names (empty for a function or an assignment)."""
+    out: dict[str, set[str]] = {}
+    for n in ast.parse(src).body:
+        if isinstance(n, ast.ClassDef):
+            out[n.name] = {m.name for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
+        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
+            out[n.name] = set()
+        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
+            for t in n.targets if isinstance(n, ast.Assign) else [n.target]:
+                if isinstance(t, ast.Name):
+                    out[t.id] = set()
+    return out
+
+
+def _matrix_values(job: str) -> set[str]:
+    """Every scalar under a job's `strategy.matrix`, comments dropped: what a check name's `(...)` suffix can carry."""
+    m = re.search(r"^( *)matrix:[ \t]*$", job, re.M)
+    out: set[str] = set()
+    for line in job[m.end():].splitlines()[1:] if m else []:
+        if line.strip() and len(line) - len(line.lstrip()) <= len(m.group(1)):
+            break
+        item = line.split("#", 1)[0].strip().removeprefix("-").strip()
+        rhs = item.split(":", 1)[1] if ":" in item else item
+        out |= {v.strip(" \"'") for v in re.split(r"[\[\],]", rhs)} - {""}
+    return out
+
+
+def _ledger_kinds(src: str | None) -> set[str]:
+    """The keys of ledger.py's KINDS table, the one registry of obligation kinds; empty when it cannot be read."""
+    for n in ast.parse(src or "").body:
+        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "KINDS" for t in n.targets):
+            return set(ast.literal_eval(n.value))
+    return set()
+
+
+def named_element_findings(docs: dict[str, str], tree: set[str], read
+                           ) -> tuple[list[str], list[tuple], collections.Counter]:
+    """(findings, pending, checked) for every element the documents name; `checked` counts them by class. `read(path)` is a tracked file's text or None.
+
+    An element that does not resolve is a finding, unless a marker covers it -- its unit, a heading above it, its
+    diagram label, or (a kind a diagram note names) the marked line that lists it -- when it is `pending`
+    (doc, groups, element), the delta R10-ARCH-DOCS resolves once those groups land. A command's argument resolves
+    when the script's text holds it as a word: a renamed subcommand or flag is caught, a reworded help text is not.
+    """
+    out: list[str] = []
+    pending: list[tuple] = []
+    checked: collections.Counter = collections.Counter()
+    bases: dict[str, list[str]] = {}
+    for p in tree:
+        bases.setdefault(p.rsplit("/", 1)[-1], []).append(p)
+    sym_cache: dict[str, dict[str, set[str]]] = {}
+
+    def files(tok: str) -> list[str]:
+        if tok in tree:
+            return [tok]
+        if "/" not in tok:
+            return sorted(bases.get(tok, []))
+        return sorted(p for p in tree if p.endswith("/" + tok))
+
+    def syms(path: str) -> dict[str, set[str]]:
+        if path not in sym_cache:
+            sym_cache[path] = _symbols(read(path) or "")
+        return sym_cache[path]
+
+    def judge(doc: str, groups: list[str] | None, element: str, problem: str | None) -> None:
+        checked[_element_class(element)] += 1
+        # None: under a retired-by marker, where an absent element is what the marker states
+        if problem is None or groups is None:
+            return
+        if groups:
+            pending.append((doc, tuple(dict.fromkeys(groups)), element))
+        else:
+            out.append(f"{doc}: {element} {problem}")
+
+    def file_and_args(doc: str, groups: list[str] | None, text: str, prose: bool) -> list[str]:
+        """Resolve each file token in `text` and the arguments that follow it; returns the resolved files.
+
+        In prose a bare config-format name (`pyproject.toml`) is not resolved: the page also names other projects'
+        files. A token closed by punctuation takes no arguments."""
+        found: list[str] = []
+        toks = text.split()
+        for i, raw in enumerate(toks):
+            tok = re.sub(r":\d+(?:-\d+)?$|[:,;.]$", "", raw)
+            if not _FILE.fullmatch(tok) or (prose and "/" not in tok and not re.search(r"\.(?:py|sh|mjs|js|md)$", tok)):
+                continue
+            hits = files(tok)
+            judge(doc, groups, f"`{tok}`", None if hits else "names no tracked file")
+            found += hits
+            for arg in itertools.takewhile(_ARG.fullmatch, toks[i + 1:] if raw == tok else []):
+                word = re.compile(r"(?<![\w-])" + re.escape(arg) + r"(?![\w-])")
+                judge(doc, groups, f"`{tok} {arg}`",
+                      None if any(word.search(read(h) or "") for h in hits) else "is an argument the script never reads")
+        return found
+
+    def job(doc: str, groups: list[str], stem: str, name: str, matrix: str | None) -> None:
+        text = read(f".github/workflows/{stem}.yml")
+        block = re.search(r"^  " + re.escape(name) + r":\s*\n(.*?)(?=^  [\w-]+:\s*$|\Z)", text or "", re.M | re.S)
+        problem = (f"names no workflow .github/workflows/{stem}.yml" if text is None
+                   else f"names no job of .github/workflows/{stem}.yml" if not block
+                   else "names a matrix value the job does not carry" if matrix and matrix not in _matrix_values(block.group(1))
+                   else None)
+        judge(doc, groups, f"job `{stem} / {name}" + (f" ({matrix})" if matrix else "") + "`", problem)
+
+    kinds = _ledger_kinds(read(LEDGER))
+    for doc in NAMED_DOCS:
+        text = docs.get(doc)
+        if text is None:
+            continue
+        # prose: a check name, a command, a module's symbol
+        for unit, heads in _units(text):
+            groups = None if _groups(unit, "retired-by") else heads + _groups(unit)
+            for span in re.findall(r"`([^`\n]+)`", unit):
+                cn = _CHECK_NAME.fullmatch(span)
+                if cn:
+                    job(doc, groups, *cn.groups())
+                    continue
+                file_and_args(doc, groups, span, True)
+                ms = re.fullmatch(r"([a-z_]\w*)\.([A-Za-z_]\w*)", span)
+                if ms and not _FILE.fullmatch(span) and f"{PKG_REL}/{ms.group(1)}.py" in tree:
+                    judge(doc, groups, f"`{span}`", None if ms.group(2) in syms(f"{PKG_REL}/{ms.group(1)}.py")
+                          else f"is not defined in {PKG_REL}/{ms.group(1)}.py")
+        # prose: the kinds listed under a list item naming the ledger
+        declared: dict[str, list[str]] = {}
+        stack: list[tuple[int, str]] = []
+        heads: list[tuple[int, list[str]]] = []
+        for line in _FENCE.sub("", text).splitlines():
+            h = re.match(r"(#+)\s", line)
+            if h:
+                heads[:] = [x for x in heads if x[0] < len(h.group(1))] + [(len(h.group(1)), _groups(line))]
+                stack.clear()
+                continue
+            li = re.match(r"(\s*)(?:[-*+]|\d+\.)\s", line)
+            if not li:
+                continue
+            ind = len(li.group(1))
+            stack[:] = [x for x in stack if x[0] < ind]
+            if any("ledger.py" in t for _, t in stack):
+                groups = [g for _, gs in heads for g in gs] + _groups(line + "".join(t for _, t in stack))
+                for k in re.findall(r"`([^`\n]+)`", line):
+                    if _KIND.fullmatch(k):
+                        declared[k] = groups
+                        judge(doc, groups, f"ledger kind `{k}`", None if k in kinds else f"is not a key of {LEDGER}'s KINDS")
+            stack.append((ind, line))
+        # diagrams: node and edge labels, sequence notes
+        for info, body in _FENCE.findall(text):
+            if info.strip() != "mermaid":
+                continue
+            labels = [next(x for x in m if x) for m in _LABEL.findall(body) if any(m)]
+            named = [f for lab in labels for seg in re.split(r"<br/?>", lab) for f in file_and_args(doc, _groups(lab), seg, False)]
+            flows = [f for f in named if re.fullmatch(r"\.github/workflows/[\w-]+\.yml", f)]
+            for lab in labels:
+                groups = _groups(lab)
+                segs = [x.strip() for x in re.split(r"<br/?>", lab)]
+                pys = [h for f in _FILE.findall(lab) for h in files(f) if h.startswith(PKG_REL + "/") and h.endswith(".py")]
+                for cm in _CAMEL.finditer(lab) if pys else ():
+                    owner = next((syms(f)[cm.group(1)] for f in pys if cm.group(1) in syms(f)), None)
+                    judge(doc, groups, f"`{cm.group(0)}`",
+                          f"is not defined in {', '.join(pys)}" if owner is None
+                          else f"is no method of {cm.group(1)}" if cm.group(2) and cm.group(2) not in owner else None)
+                for seg in segs:
+                    if re.fullmatch(r"[a-z_]\w*(?: · [a-z_]\w*)+", seg):
+                        for mod in seg.split(" · "):
+                            judge(doc, groups, f"module `{mod}`", None if f"{PKG_REL}/{mod}.py" in tree
+                                  or any(p.startswith(f"{PKG_REL}/{mod}/") for p in tree) else f"is no module of {PKG_REL}")
+                if lab.startswith("services:"):
+                    have = set(re.findall(r"^([a-z_]\w*):", read(f"{PKG_REL}/services.yaml") or "", re.M))
+                    for svc in re.findall(r"[a-z_]+", lab[len("services:"):].replace("<br/>", " ")):
+                        judge(doc, groups, f"service `{svc}`", None if svc in have else f"is not in {PKG_REL}/services.yaml")
+                if flows and _WORD.fullmatch(segs[0]):
+                    stem = flows[0].rsplit("/", 1)[-1][:-4]
+                    job(doc, groups, stem, segs[0], None)
+            for line in body.splitlines():
+                if re.match(r"\s*[Nn]ote\b", line):
+                    for k in (a or b for a, b in _KIND_NOTE.findall(line)):
+                        judge(doc, declared.get(k, []), f"ledger kind `{k}` in a diagram note",
+                              None if k in kinds else f"is not a key of {LEDGER}'s KINDS")
+    return out, pending, checked
+
+
+def _element_class(element: str) -> str:
+    """`a.py` file, `a.py --x` argument, `m.Sym` symbol, or the leading word: job, ledger kind, module, service."""
+    if not element.startswith("`"):
+        return element.split(" `", 1)[0]
+    body = element.strip("`")
+    return "argument" if " " in body else "file" if _FILE.fullmatch(body) else "symbol"
+
+
+
 COFFEE = "https://buymeacoffee.com/rpgshcwb2tp"
 COFFEE_SVG = "docs/img/brand/coffee.svg"
 # inline, or by reference: the image stays inline and its line carries no '://', which HACS's README image rewriter
@@ -3305,6 +3533,151 @@ def check_doc_wiring() -> None:
     R.check("a marker with no roster file to resolve it is a finding", any("no roster" in g for g in got), repr(got))
 
 
+def _read_tracked(tree: set[str]):
+    return lambda path: (ROOT / path).read_text() if path in tree and (ROOT / path).is_file() else None
+
+
+def check_named_elements() -> None:
+    R.section("doc wiring: every instrument, job, kind, symbol and diagram node the two pages name (R10-ARCH-DOCS-WIRING)")
+    tree = _tracked()
+    docs = {p: (ROOT / p).read_text() for p in NAMED_DOCS if (ROOT / p).is_file()}
+    errs, pending, checked = named_element_findings(docs, tree, _read_tracked(tree))
+    want = ("file", "argument", "symbol", "job", "ledger kind", "module", "service")
+    R.check("every class of named element is read on these pages (anchor)", all(checked[k] for k in want),
+            ", ".join(f"{k} {checked[k]}" for k in want))
+    R.check("every named element resolves in the artifact that defines it, or a marker covers it", not errs,
+            "; ".join(errs[:4]) + (f" (+{len(errs) - 4})" if len(errs) > 4 else ""))
+    for doc, groups, element in pending:
+        print(f"       pending: {doc}: {element} [target: {', '.join(groups)}]")
+
+    t = {".github/workflows/ci.yml", ".github/workflows/tests.yml", "tools/x.sh", f"{PKG_REL}/mod.py",
+         f"{PKG_REL}/services.yaml", LEDGER}
+    files = {".github/workflows/ci.yml": "jobs:\n  prelude:\n    runs-on: x\n  gate:\n    needs: [prelude]\n",
+             ".github/workflows/tests.yml": 'jobs:\n  fast:\n    strategy:\n      matrix:\n        python-version: ["3.14"]\n',
+             "tools/x.sh": "case $1 in\n  pass) ;;\n  --once) ;;\nesac\n",
+             f"{PKG_REL}/mod.py": "class ThingOne:\n    def run(self):\n        pass\n",
+             f"{PKG_REL}/services.yaml": "do_it:\n  name: x\n",
+             LEDGER: 'KINDS = {"handoff-no-pr": "derived", "train-stop": "event"}\n'}
+    base = ("# D\n\n- `tools/x.sh pass` runs it, under `tests / fast (3.14)`; it calls `mod.ThingOne`.\n"
+            "- The ledger, `tools/audit/seat/ledger.py`:\n  - kinds: `handoff-no-pr`, `train-stop`\n"
+            "  - later: `record-owed` [target: R10-A]\n\n"
+            "```mermaid\nflowchart LR\n    w[\"ci.yml: the umbrella\"] --> p[\"prelude<br/>kind\"]\n    p --> g[\"gate\"]\n"
+            "    g --> q[\"PUT\"]\n"
+            "    m[\"mod.py<br/>ThingOne.run\"] -- \"services: do_it\" --> x[\"x.sh --once\"]\n    l[\"mod · mod\"] --> m\n```\n\n"
+            "```mermaid\nsequenceDiagram\n    participant A as a\n    Note over A: handoff-no-pr closes, record-owed opens\n```\n")
+    clean, pend, n = named_element_findings({"dev/README.md": base}, t, files.get)
+    R.check("the clean fixture resolves every class and leaves only the marked kind pending (null control)",
+            not clean and all(n[k] for k in want) and {e for _, _, e in pend} ==
+            {"ledger kind `record-owed`", "ledger kind `record-owed` in a diagram note"}, repr((clean, pend, n)))
+    plants = (
+        ("a renamed script", "`tools/x.sh pass`", "`tools/y.sh pass`", "names no tracked file"),
+        ("a renamed subcommand", "`tools/x.sh pass`", "`tools/x.sh push`", "never reads"),
+        ("a removed flag in a diagram node", "x.sh --once", "x.sh --twice", "never reads"),
+        ("a renamed workflow in a diagram node", "ci.yml: the", "cx.yml: the", "names no tracked file"),
+        ("a removed workflow job in a diagram node", 'g["gate"]', 'g["gat"]', "names no job"),
+        ("a check name's matrix value", "(3.14)", "(3.15)", "matrix value"),
+        ("a removed class", "`mod.ThingOne`", "`mod.ThingTwo`", "not defined"),
+        ("a removed method in a diagram node", "ThingOne.run", "ThingOne.walk", "no method"),
+        ("a removed module in a module list", "mod · mod", "mod · gone", "no module"),
+        ("a removed service on an edge", "services: do_it", "services: undo_it", "services.yaml"),
+        ("a removed ledger kind in a list", "`train-stop`", "`train-halt`", "KINDS"),
+        ("a removed ledger kind in a diagram note", "handoff-no-pr closes", "handoff-gone closes", "KINDS"),
+    )
+    for what, old, new_, key in plants:
+        doc = base.replace(old, new_)
+        got, _, _ = named_element_findings({"dev/README.md": doc}, t, files.get)
+        R.check(f"red fixture: {what} is a finding", doc != base and any(key in g for g in got), repr(got))
+    got, pend, _ = named_element_findings({"dev/README.md": base.replace("`tools/x.sh pass` runs it",
+                                           "`tools/y.sh pass` runs it [target: R10-A]")}, t, files.get)
+    R.check("a marked element that does not resolve is pending, not a finding (null control)",
+            not got and any(e == "`tools/y.sh`" for _, _, e in pend), repr((got, pend)))
+
+
+def check_marker_census() -> None:
+    R.section("target-marker resolver: every marker with its group's roster stage (R10-ARCH-DOCS-WIRING item 2)")
+    docs = {p: (ROOT / p).read_text() for p in WIRING_DOCS if (ROOT / p).is_file()}
+    stages = roster_stages()
+    rows = marker_census(docs, stages or {})
+    R.check("the resolver reads every marker arm W reads (anchor)",
+            len(rows) == sum(len(_MARKER.findall(re.sub(r"`[^`\n]+`", "", t))) for t in docs.values()) > 0, str(len(rows)))
+    print(f"       ({sum(r['due'] for r in rows)} of {len(rows)} marker(s) name only done groups: "
+          "python3 tests/doc_claims.py --markers lists them)")
+    stub = {"R10-A": "not-started", "R10-B": "done"}
+    doc = "# T\n\n- `a.py` lands [target: R10-A]\n- quoted: `[target: R10-B]`\n"
+    null = marker_census({"d.md": doc}, stub)
+    red = marker_census({"d.md": doc.replace("[target: R10-A]\n", "[target: R10-B]\n")}, stub)
+    both = marker_census({"d.md": doc.replace("[target: R10-A]\n", "[target: R10-B, R10-A]\n")}, stub)
+    R.check("null control: a marker naming a not-started group is listed and not due; a quoted one is not a marker",
+            [(r["line"], r["due"]) for r in null] == [(3, False)], repr(null))
+    R.check("red fixture: a marker naming a done group is due", [r["due"] for r in red] == [True], repr(red))
+    R.check("a marker naming a done and a not-started group is not due until both land", [r["due"] for r in both] == [False],
+            repr(both))
+
+
+def print_marker_census(argv: list[str]) -> int:
+    """`--markers [--roster FILE]`: every marker, its groups' stages, and what each due one still leaves unresolved.
+    Exit 1 while any marker is due. FILE defaults to this tree's roster; the live one is on handoff/audit-r10-roster."""
+    roster = pathlib.Path(argv[argv.index("--roster") + 1]) if "--roster" in argv else ROSTER
+    stages = roster_stages(roster)
+    if stages is None:
+        print(f"no roster at {roster}")
+        return 2
+    docs = {p: (ROOT / p).read_text() for p in WIRING_DOCS if (ROOT / p).is_file()}
+    tree = _tracked()
+    _, pending, _ = named_element_findings(docs, tree, _read_tracked(tree))
+    rows = marker_census(docs, stages)
+    for r in rows:
+        print(f"{'DUE ' if r['due'] else '    '}{r['doc']}:{r['line']} {r['marker']} "
+              + ", ".join(f"{g}={v}" for g, v in r["stages"].items()))
+    for doc, groups, element in pending:
+        if all(stages.get(g) == "done" for g in groups):
+            print(f"UNRESOLVED {doc}: {element}, though {', '.join(groups)} landed")
+    due = sum(r["due"] for r in rows)
+    print(f"{due} of {len(rows)} marker(s) due")
+    return 1 if due else 0
+
+
+# P40: the committed pictures of the card's pages are of the card this tree ships. tests/card_browser.mjs takes the
+# pages and compares each one's size and element structure to docs/img/card/pages.json, which it writes beside the
+# pictures (HPO_PAGES_OUT); this arm ties that record to the committed files, so neither moves without the other.
+CARD_FIGURES = ROOT / "docs" / "img" / "card"
+
+
+def card_figure_findings(recorded: dict[str, dict], sizes: dict[str, tuple[int, int] | None]) -> list[str]:
+    """`recorded`: pages.json's figures; `sizes`: each committed `<page>-<light|dark>.png` -> its PNG header size."""
+    out = [f"{n}: committed and not in pages.json" for n in sorted(set(sizes) - set(recorded))]
+    out += [f"{n}: in pages.json and not committed" for n in sorted(set(recorded) - set(sizes))]
+    for n in sorted(set(sizes) & set(recorded)):
+        want = (recorded[n].get("width"), recorded[n].get("height"))
+        if sizes[n] != want:
+            out.append(f"{n}: the PNG is {sizes[n]}, pages.json records {want}")
+    for n in sorted(recorded):
+        twin = n.replace("-light.png", "-dark.png")
+        if twin != n and twin in recorded and recorded[n].get("structure") != recorded[twin].get("structure"):
+            out.append(f"{n}: its dark twin records another page structure")
+    return out
+
+
+def check_card_figures() -> None:
+    R.section("P40: the committed card page figures are the pages tests/card_browser.mjs recorded")
+    man = CARD_FIGURES / "pages.json"
+    recorded = json.loads(man.read_text())["figures"] if man.is_file() else {}
+    sizes = {p.name: png_size(p) for p in sorted(CARD_FIGURES.glob("*.png")) if re.search(r"-(?:light|dark)\.png$", p.name)}
+    R.check("pages.json records the tile and every page in both themes (anchor)", len(recorded) >= 14, str(len(recorded)))
+    bad = card_figure_findings(recorded, sizes)
+    R.check("every committed page figure is recorded at its own size, and each theme pair is one page", not bad,
+            "; ".join(bad[:4]))
+    rec = {"a-light.png": {"width": 10, "height": 20, "structure": "s"}, "a-dark.png": {"width": 10, "height": 20, "structure": "s"}}
+    ok = {"a-light.png": (10, 20), "a-dark.png": (10, 20)}
+    R.check("null control: a record matching its files is clean", not card_figure_findings(rec, ok))
+    for what, r, z, key in (
+            ("a figure regenerated without its record", rec, {**ok, "a-dark.png": (10, 24)}, "pages.json records"),
+            ("a figure with no record", rec, {**ok, "b-light.png": (1, 1)}, "not in pages.json"),
+            ("a record with no figure", rec, {"a-light.png": (10, 20)}, "not committed"),
+            ("a theme pair of two pages", {**rec, "a-dark.png": {**rec["a-dark.png"], "structure": "t"}}, ok, "dark twin")):
+        R.check(f"red fixture: {what} is a finding", any(key in g for g in card_figure_findings(r, z)))
+
+
 def check_coffee_button() -> None:
     R.section("Buy Me a Coffee button in its three places (owner, 2026-10-22)")
     built = docs_build()["html"]
@@ -3366,9 +3739,12 @@ def main() -> int:
     check_service_count_comments()
     check_image_dimensions()
     check_doc_wiring()
+    check_named_elements()
+    check_marker_census()
+    check_card_figures()
     check_coffee_button()
     return R.close("checks")
 
 
 if __name__ == "__main__":
-    raise SystemExit(main())
+    raise SystemExit(print_marker_census(sys.argv) if "--markers" in sys.argv else main())

