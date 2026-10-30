R10-ARCH-DOCS-WIRING, arm A of triage P261 (dev/programme/triage/s6-batch52.md#P261). Refers to #2395, which stays open for arm B (R10-ARCH-DOCS). Part of #201.

What each brief item landed, and the design choice it encodes:

1. **Wiring test.** `tests/doc_claims.py` `named_element_findings` resolves what `docs/architecture.md` and `dev/README.md` name beyond a path. Each element is read in the artifact that defines it, never from a list kept in the test (fixer.md step 11):
   - a command's arguments: each one is a word of the script, e.g. `bus.sh push-verdict` or `heartbeat.sh --once`;
   - a `module.Symbol`, and a CamelCase class or `Class.method` in a diagram label naming a `.py` file: read through `ast`;
   - a check name `<stem> / <job> (<matrix>)` and the CI figure's job nodes: the job ids of the `.yml` that figure names, plus the job's `strategy.matrix` scalars;
   - a ledger kind, in the list under the ledger item or in a sequence-diagram note: the keys of `tools/audit/seat/ledger.py`'s `KINDS`;
   - a module list `a · b` in a diagram label: the package's modules;
   - a `services:` edge label: `services.yaml`'s keys.

   Arm W's paths, markers and mermaid predicates are unchanged. An element a `[target:]` marker covers (its unit, a heading, its diagram label, or the marked line listing a kind) is *pending*, not a finding. Under `[retired-by:]`, an absent element is what the marker states.

   Design choices:
   - A bare config-format name in prose (`pyproject.toml`) is not resolved, because the page also names Home Assistant's own files.
   - README.md is not read: it names the user's `configuration.yaml`.
   - An argument resolves as a word of the script. A renamed subcommand or flag is caught; a reworded help text is not.

2. **Target-marker resolver.** `marker_census` lists every marker with each named group's roster stage. It is due when every group it names is `done`.
   - `python3 tests/doc_claims.py --markers [--roster FILE]` prints the census, plus every pending element whose groups have all landed. It exits 1 while any marker is due.
   - The gate runs only its fixtures. Arm B makes the census hard.
   - Arm W's report-only note (c) now reads the census, so a marker naming one done and one not-started group is no longer reported as resolvable.

3. **P40.** `tests/card_browser.mjs` page mode records each page figure's PNG size and a digest of the page's visible element structure in `docs/img/card/pages.json` (HPO_PAGES_OUT). Every browser run then compares the live card to that record. `doc_claims.py` `check_card_figures` ties the record to the committed PNG headers and requires each light/dark pair to be one page.
   - Pixels are not compared. The committed plan figures (rendered on another machine) differ from this machine's render in 30-31% of pixels at identical size, so a pixel check would be a cross-machine check.
   - The 14 page figures are regenerated from one run. The advisor, savings and setup figures had changed height. `docs/index.html`'s declared advisor height follows (`check_image_dimensions`). The advisor alt text was checked against the new picture and still holds.
   - Not covered: the README hero (`card-plan-chart.png`, HPO_HERO_OUT) and the two generated SVGs (`make_card_figures.mjs`) are outside this record.

Carries moved here:
- Carry 1 (coffee button): already pinned by `check_coffee_button`, which R10-ARCH-DOCS-FIRST landed with a red case per placement and the light/dark token comparison. It is green at this head, so nothing was rebuilt.
- Carry 2: `resolveCited`'s canon lookup has not landed, so the `dev/README.md` entry stays and `corpus_excluded.json`'s `_comment` now carries its reason.

4. **Handoff repair: one kebab-word grammar.** `tools/pr/prepr.sh`'s agreement lane refused the earlier head 2352b3d28 with `UNREGISTERED "[a-z][a-z0-9-]*" in .claude/workflows/figure_lint.mjs, tests/doc_claims.py`. In doc_claims that shape was the diagram selector that sends a label's first segment to the job resolver. That was a second spelling of a grammar doc_claims already carries: `_ARG`'s bare-word arm, the lower-case kebab word. It is now named once, as `_WORD`, and both `_ARG` and the selector read it. figure_lint's copy is a different concept: a `gh` subcommand word passed to `gh <word...> --help`. Only the doc_claims copy was a duplicate, so nothing was registered in `agreement.mjs`.
   - Design choice: the selector stays lower-case kebab, not the workflow job-id grammar `[A-Za-z][\w-]*` that `agreement.mjs` registers for the jobs-block scan. Under the job-id grammar, `dev/README.md`'s sequence-diagram node `PUT` reaches the job resolver and is a false finding (mutant M8). The selector decides only which label is a job node; `job()` decides whether that job exists.
   - The clean fixture gains a `PUT` node, so the selector's case rule is pinned in the gate and not only by the live page.

5. **Handoff repair: doc_claims.py's closure.** The same prepr run refused `closures` as UNDER-SCOPED once agreement was clean. The doc-wiring arm opens each script the pages pass an argument to, and the workflows. The card-figure arm opens `docs/img/card/pages.json` and every page PNG. `./tests/derive_closures.sh --single tests/doc_claims.py` printed 16 such files as `INERT ... actually read by tests` and exited 1: 13 under `docs/img/card/`, plus `bus.sh`, `cloud_relay.sh` and `heartbeat.sh` under `tools/audit/seat/`. They move to `tests/closure.py`'s `INERT_EXCEPT`, the route #2298 and R10-ARCH-DOCS-FIRST took. The re-record then exited 0 and added 21 paths to `tests/closures.json`: those 16, and 5 that were never INERT (`ledger.py`, `tests/gate_lock.py`, `tools/policy/rules_sync.mjs`, `ci.yml`, `tests.yml`).

Alternatives not taken:
- A new `tests/doc_wiring.py` script would split arm W from the predicates it shares (`_units`, `_MARKER`, `_FENCE`) and add a gate script to classify.
- Extending `brief_lint.mjs` lost too: it lints roster briefs and reads neither page.
- For the handoff repair, registering `[a-z][a-z0-9-]*` as `not-a-concept` would have cleared the lane but left doc_claims spelling its kebab word twice. Reusing `_CHECK_NAME`'s `[\w-]+` job atom, or the job-id grammar, lost to M8: either one turns `PUT` into a false finding.

## Head

fc907699e24dfbb28ae390fa26443c74303eb39e (base cc930cdd1a3cfb005ba7ec557f4451ff5e53e364, origin/main at 2026-10-30T18:26Z). Main was merged into 2352b3d28, then two handoff-repair commits were added: the grammar (389c3baee), the closure record (75b30a4e28e8e5ee8573720043c31f570f1e345f) and the carry-1645 re-anchor (this head, fc907699e24dfbb28ae390fa26443c74303eb39e).

## Mutation proof

Each mutant was applied in turn to `tests/doc_claims.py` at the head, and `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` was run (rc=1 for each), then the file was restored byte-identical. The driver is a scratch probe; the replacements are quoted here.
- M1, argument predicate `None if any(word.search(read(h) or "") for h in hits) else` -> `None if True else`: FAIL `red fixture: a renamed subcommand is a finding`, FAIL `red fixture: a removed flag in a diagram node is a finding`
- M2, prose ledger-kind predicate `None if k in kinds else` -> `None if True else`: FAIL `the clean fixture resolves every class and leaves only the marked kind pending (null control)`, FAIL `red fixture: a removed ledger kind in a list is a finding`
- M3, `"due": all(v == "done" for v in st.values())` -> `"due": False`: FAIL `state tolerance: a marker naming a done group, and an absent retired-by path, yield only notes`, FAIL `red fixture: a marker naming a done group is due`
- M4, `if sizes[n] != want:` -> `if False:`: FAIL `red fixture: a figure regenerated without its record is a finding`
- M5, job predicate `if not block` -> `if False`: FAIL `red fixture: a removed workflow job in a diagram node is a finding`
- M6, `None if ms.group(2) in syms(` -> `None if True or ms.group(2) in syms(`: FAIL `red fixture: a removed class is a finding`
- M7, the diagram job selector `if flows and _WORD.fullmatch(segs[0]):` -> `if flows and False:`: FAIL `red fixture: a removed workflow job in a diagram node is a finding`
- M8, the same selector widened to the job atom: `if flows and re.fullmatch(r"[\w-]+", segs[0]):`. This FAILs three checks:
  - `every named element resolves in the artifact that defines it, or a marker covers it`: ``dev/README.md: job `ci / PUT` names no job of .github/workflows/ci.yml``
  - `the clean fixture resolves every class and leaves only the marked kind pending (null control)`
  - `a marked element that does not resolve is pending, not a finding (null control)`
- M1-M6 were taken at 2352b3d28. The merged delta touches none of their lines, since main's delta changes no path under `tests/doc_claims.py`, `tests/card_browser.mjs`, `docs/img` or the card frontend (`git diff --quiet 2352b3d28 HEAD~1 -- tests/doc_claims.py tests/card_browser.mjs docs/img custom_components/heatpump_optimizer/frontend && echo UNCHANGED` prints UNCHANGED). M7-M8 were run at this head.
- card_browser.mjs P40 is pinned in-run by `P40 red case: a figure one pixel taller than the page is stale; the run's own figures are not (null control)`, which calls the same `figureDrift`.

## Null control

- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` at the head: every check passes. `named_element_findings` returns no finding over the two pages, with every element class read (the anchor check names each class's count).
- The clean fixtures yield no finding. A marked unresolved element is pending, not a finding. A marker naming a not-started group is not due. A record matching its files is clean.
- `node tests/card_browser.mjs` (no HPO_PAGES_OUT), a second run after the writing run: `P40 every committed card page figure has the size and structure of the page this card draws` is ok, so the record reproduces on this machine. Cross-machine stability is CI's browser job's to show. Before regeneration, 8 of 14 committed figures from another machine had this machine's exact size.

## Figures

Each count is printed by `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` at the head unless the line names another command. The class counts and the marker census were re-taken at this head. The perturbation rows and the card-figure rows were taken at 2352b3d28 with the previous seat's scratch drivers, and are carried, not re-taken: main's delta touches none of their inputs (the UNCHANGED command under `## Mutation proof`). The handoff repair leaves the selector's verdict on both pages unchanged: `doc_claims.py`'s full output before and after the repair, at the merged tree, compared by `diff before.txt after.txt && echo IDENTICAL`, printed IDENTICAL.
- Agreement: `node tools/policy/agreement.mjs --only discovery` at 2352b3d28 merged with main and without the repair printed `UNREGISTERED "[a-z][a-z0-9-]*" in .claude/workflows/figure_lint.mjs, tests/doc_claims.py` (the null control). At this head it prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`.
- Named elements checked, by class: the anchor line `every class of named element is read on these pages`. Rule: one count per `judge` call in `named_element_findings`, over the two pages. At this head: file 132, module 19, ledger kind 19, job 11, symbol 9, argument 6, service 3; findings 0, pending 5.
- Markers: the anchor line `the resolver reads every marker arm W reads`, plus `python3 tests/doc_claims.py --markers`. At this head, against the tree's roster copy: 25 of 28 due. Every due marker names a group whose roster stage is `done`. The 3 not due name R10-COP-GATE (in-progress) and R10-FLOW-TOOLKIT-MODEL (not-started).
- Perturbations of the real pages and artifacts, applied in memory, through `named_element_findings` (scratch driver). Null (head): 0 findings.
  - doc edits, each 1 finding:
    - `bus.sh push-verdict`->`push-verdicts`
    - `orchestrator_tick.py`->`orch_tick.py`
    - `heartbeat.sh --once`->`--one`
    - `tests / fast (3.14)`->`(3.13)`
    - CI node `gate`->`gates`
    - note `handoff-no-pr`->`handoff-no-prs`
    - `DhwPlanner`->`DhwPlaner`
    - module `sysid`->`sys_id`
    - service `simulate_plan`->`simulate_plans`
  - artifact edits:
    - ci.yml job `prelude`->`preamble`: 1 finding
    - `class InputReader`->`InputReading`: 2 findings, prose and diagram
    - gate_lock.py `needs-lease`->`needs_lease`: 1 finding
  - Removing `reviewer-fire` from `KINDS` yields 0 findings and moves it to pending, because the kind list is under `[target: R10-ORCH-MACHINERY]`. That is the case arm B makes hard.
- Card figures: a scratch canvas pixel diff, not in the tree, against the base's committed PNGs, after `HPO_PAGES_OUT=<scratch> node tests/card_browser.mjs`. Size mismatched: advisor 1056x616 -> 708, savings 158 -> 164, setup 552 -> 714, each in both themes. Size equal: tile, plan, plan-why, health. Pixels differing at equal size: plan 30-31%, plan-why 30%, tile 10-13%, health 80%.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `python3 tests/entities.py`: ALL ENTITY CHECKS PASSED. `node tests/card_browser.mjs` at 2352b3d28: ALL BROWSER CHECKS PASSED, with both P40 lines ok. Its inputs are UNCHANGED since, by the command under `## Mutation proof`.
- Scope (at this head): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL`, `reason: tests/closure.py changes the gate itself`. Run here: `tests/run.sh`'s four `run_always` lines (`env_drift.py --claims-only <merge base>`, `closure.py selftest`, `layout.py`, `harness_headers.py`), plus tests/doc_claims.py and tests/entities.py, which the diff edits or which pin it. Each exited 0. The rest is CI's. At 389c3baee, before the closure commit, the mode was `MODE: SCOPED -- 2 script(s) run`. `tools/pr/ci_predict.py --base origin/main`, at this head against cc930cdd1a3c: no closures, fast, wave-script or instrument red predicted. It says itself that it does not see a data-file read: doc_claims now reads docs/img/card/pages.json, the card PNGs, ledger.py, the workflows and services.yaml, so prepr.sh's `closures` step measured what ci_predict could not, and item 5 repaired it before the handoff.

## Red checks

`tests / briefs` was red at the previous head (75b30a4e28e8e5ee8573720043c31f570f1e345f): `dev/programme/carries/carry-1645.json` cited `tests/doc_claims.py:476` for `check_initial_setup_menu` and `tests/doc_claims.py:565` for `check_simulate_plan_fields`; this PR's two added imports (`collections`, `itertools`) shifted both, and `brief_lint` refused with "'check_simulate_plan_fields' not found near tests/doc_claims.py:476; found at line 570 instead".

Root-cause trigger (red-check, `defect-root-cause.md`): answered.
- Cause: a diff that moves lines in a file a carry cites by line number. A carry's `path:line` is data the code does not know it is.
- Process state: a check exists (`brief_lint`, CI job `briefs`) but prepr step 3f runs it only when a pinned path changed (`pinned_touched`), and `tests/doc_claims.py` is not pinned, so prepr skipped it ("no pinned path changed, so CI's briefs job reads this head's copy") and the first run reached CI to find it.
- Cheaper detector: a local `node tools/policy/brief_lint.mjs` before handoff (this round's step 2), or prepr step 3f extended to run when the diff touches any file a carry or roster `path:line` cites. Standing cost: one `brief_lint` run, about 2.5 minutes of one core on this machine, per handoff whose diff touches a cited file; the extension would add a carry-and-roster citation scan (seconds) to every prepr.
- Countermeasure decision: not built in this PR. It is a prepr change in a code-owned instrument, outside this group's seam; recorded here for the orchestrator to triage as a proposal (one occurrence so far; not yet a recurring class).
- Fix at this head: both citations re-anchored (476 to 479, 565 to 570); `node tools/policy/brief_lint.mjs` exits 0 and prints `carry-1645.json: 0 error(s), 0 warning(s)`. The ten remaining `ERROR` lines in its output are in wave-1 rosters and fixtures, cite wave-1 groups, not a file this diff touches, and do not fail the run (exit 0). The roster has no `tests/doc_claims.py:<line>` citation (grep of `handoff/audit-r10-roster` and this head's `wave-r10-groups.json`), so no edit-brief is owed.

## Forward-carry

- R10-ARCH-DOCS (arm B): the resolver at this head lists `stage-mismatch`, `absorb-edge-missing` and `record-owed` as pending under `[target: R10-ORCH-MACHINERY]`, which is `done`. None is a key of `tools/audit/seat/ledger.py`'s `KINDS`. They are a departure arm B resolves (redraw, or name the landed kinds). Re-measure with `python3 tests/doc_claims.py --markers --roster <the roster branch's wave-r10-groups.json>` at arm B's merge base. Carry: R10-ARCH-DOCS
- R10-ARCH-DOCS (arm B): `docs/img/card/health-light.png` and `health-dark.png` are now regenerated from the card. What remains of the carry naming them is the text: `docs/dashboard-card.md`'s Health alt text and the section's layout, COP, heat-loss and checklist sentences describe the old page. The regenerated picture also crops the checklist after its first item at the 860 px viewport. Carry: R10-ARCH-DOCS

## Friction

none
