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

Alternatives not taken:
- A new `tests/doc_wiring.py` script would split arm W from the predicates it shares (`_units`, `_MARKER`, `_FENCE`) and add a gate script to classify.
- Extending `brief_lint.mjs` lost too: it lints roster briefs and reads neither page.

## Head

2352b3d28983880c90f6a7620bf55ab98189ede0 (base cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7, origin/main at 2026-10-30)

## Mutation proof

Each mutant was applied in turn to `tests/doc_claims.py` at the head, and `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` was run (rc=1 for each), then the file was restored byte-identical. The driver is a scratch probe; the replacements are quoted here.
- M1, argument predicate `None if any(word.search(read(h) or "") for h in hits) else` -> `None if True else`: FAIL `red fixture: a renamed subcommand is a finding`, FAIL `red fixture: a removed flag in a diagram node is a finding`
- M2, prose ledger-kind predicate `None if k in kinds else` -> `None if True else`: FAIL `the clean fixture resolves every class and leaves only the marked kind pending (null control)`, FAIL `red fixture: a removed ledger kind in a list is a finding`
- M3, `"due": all(v == "done" for v in st.values())` -> `"due": False`: FAIL `state tolerance: a marker naming a done group, and an absent retired-by path, yield only notes`, FAIL `red fixture: a marker naming a done group is due`
- M4, `if sizes[n] != want:` -> `if False:`: FAIL `red fixture: a figure regenerated without its record is a finding`
- M5, job predicate `if not block` -> `if False`: FAIL `red fixture: a removed workflow job in a diagram node is a finding`
- M6, `None if ms.group(2) in syms(` -> `None if True or ms.group(2) in syms(`: FAIL `red fixture: a removed class is a finding`
- card_browser.mjs P40 is pinned in-run by `P40 red case: a figure one pixel taller than the page is stale; the run's own figures are not (null control)`, which calls the same `figureDrift`.

## Null control

- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` at the head: every check passes. `named_element_findings` returns no finding over the two pages, with every element class read (the anchor check names each class's count).
- The clean fixtures yield no finding. A marked unresolved element is pending, not a finding. A marker naming a not-started group is not due. A record matching its files is clean.
- `node tests/card_browser.mjs` (no HPO_PAGES_OUT), a second run after the writing run: `P40 every committed card page figure has the size and structure of the page this card draws` is ok, so the record reproduces on this machine. Cross-machine stability is CI's browser job's to show. Before regeneration, 8 of 14 committed figures from another machine had this machine's exact size.

## Figures

Each count is printed by `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` at the head unless the line names another command.
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
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `python3 tests/entities.py`: ALL ENTITY CHECKS PASSED. `node tests/card_browser.mjs`: ALL BROWSER CHECKS PASSED, with both P40 lines ok.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run`, naming tests/doc_claims.py and tests/entities.py; both were run. `tools/pr/ci_predict.py --base origin/main`: no closures, fast, wave-script or instrument red predicted. It says itself that it does not see a data-file read: doc_claims now reads docs/img/card/pages.json, the card PNGs, ledger.py, the workflows and services.yaml, so an `UNDER-SCOPED` repair by closures-autofix is possible.

## Red checks

none

## Forward-carry

- R10-ARCH-DOCS (arm B): the resolver at this head lists `stage-mismatch`, `absorb-edge-missing` and `record-owed` as pending under `[target: R10-ORCH-MACHINERY]`, which is `done`. None is a key of `tools/audit/seat/ledger.py`'s `KINDS`. They are a departure arm B resolves (redraw, or name the landed kinds). Re-measure with `python3 tests/doc_claims.py --markers --roster <the roster branch's wave-r10-groups.json>` at arm B's merge base. Carry: R10-ARCH-DOCS
- R10-ARCH-DOCS (arm B): `docs/img/card/health-light.png` and `health-dark.png` are now regenerated from the card. What remains of the carry naming them is the text: `docs/dashboard-card.md`'s Health alt text and the section's layout, COP, heat-loss and checklist sentences describe the old page. The regenerated picture also crops the checklist after its first item at the 860 px viewport. Carry: R10-ARCH-DOCS

## Friction

none
