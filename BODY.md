The user-docs draft stage of the N2 split (R10-USER-DOCS-FINAL, size L; re-scope by tvofi, 2026-10-31). Design: `dev/programme/designs/R10-USER-DOCS-FINAL.md` on design/R10-USER-DOCS-FINAL 576654cce6e4fc0c643a2184e65d030a7fe0decf, approved by design-verdict/R10-USER-DOCS-FINAL 5b54eb18c1dc93418b881ce9f3e256553ccd8fd9. Brief and carries read at handoff/audit-r10-roster 315cd0441dd89059a1714c4f2e20ad9055063b3b. Carry 1 (the re-scope, tvofi 2026-10-31, "split USER-DOCS-FINAL"): answered by this diff. Brief items (1)-(6) are done against origin/main at the fork, not the true merge base: the enumeration (`--surfaces`), the pages, the correctness pass (claim table below), the removals (no feature the pages describe is absent from the tree: every `--surfaces` row homed, and the history text that described older forms is rewritten), and both arms, coverage with its reasoned exemption list and stateless, each red on its fixture and green on its null control. The check at the true merge base is R10-USER-DOCS-VERIFY's, which reuses these arms. Contract step 9: `git log --first-parent 14ed13551..origin/main` at the fork lists only #3037 (tools/audit/seat, tools/pr), so no in-flight group from the note's list landed since the note's base and there was no merged diff to re-read.

What it adds, all in `tests/doc_claims.py`:
- `surface_sources()` / `surface_rows()`: every user-facing surface in eleven classes, each from the tree (`PLATFORM_LIST` through `entity_census`, `services.yaml`, `config.step` in `translations/en.json` with the defaults each config-flow step renders, `_OPTION_PAGES`, `_OPTION_FIELDS`, `blueprints/automation/*.yaml`, `notifier.py` `EVENT_*`, the card's `tab("<id>"` calls plus the compact card, the card's `DEFAULTS` and `config.<key>` reads, `issues` in `strings.json`), and its home: the page, section and shape of the design's page map. `home-found` is the home shape present and, for `option`, `setup_field` and `card_option`, its Default cell agreeing with the shipped default (`default_agrees`); an option's row must sit under its own page's heading, a setup field's under a heading naming its screen.
- `python3 tests/doc_claims.py --surfaces` (one sorted tab-separated line per surface, `class id label home-page home-found default`; exit 1 while a non-exempt surface has no home) and `--surfaces --against FILE` (the keyed `LANDED` / `REMOVED` / `CHANGED` delta, `surface_delta`; exit 1 while a section is non-empty). `check_surface_coverage` calls the same `surface_rows()`, so the CLI and the gate cannot differ. `SURFACE_EXEMPT` holds one entry, the blank `_OPTION_FIELDS` key on `building_preset` (carry udf-blank-option-key), keyed `building_preset[questionnaire]`.
- `check_stateless`: the history lexicon over the seven pages after fences, code spans, HTML comments, tags and link targets are blanked; every phrase word-bounded (carry udf-used-to-boundary); a purpose-sense `used to` (sentence or table-cell start, after `,`, `is`, `are`, `only`, `also`) passes; `STATELESS_EXEMPT` is empty and each entry would have to match exactly once.
- The marker census tag: `_in_comment` sets `scope` (`user` inside `<!-- -->`, else `wiring`); `marker_census` reads `marker_docs()`, the wiring documents and the user pages in one dict keyed by path (README.md read once); `doc_wiring_findings`' due note and the default `--markers` skip user rows; `--markers --user` prints `N user-doc marker(s), M due`, exit 1 while N > 0; `marker_placement_findings` refuses a bare marker on a user-only page, a wrapped one on `docs/architecture.md` or `dev/README.md`, and a user marker naming no roster group. Verdict note udf-user-marker-path-mask: path check (a) and `_groups` now count only wiring markers (`_wiring`), so a user marker excuses no missing path.
- `entity_census` read `getattr(e, "entity_registry_enabled_default", True)`; the stub has no such property, so the eleven entities declaring only `_attr_entity_registry_enabled_default = False` read as enabled (stub vacuity, fixer.md step 13). It now reads that attribute second, the rule `tests/entities.py` `registry_default` already uses. Measured: 9 disabled before, 20 after, which is the README's "Twenty entities".

The pages: every surface now has its home, and the change history is gone from all seven. Main rewrites: `docs/configuration.md` `## Initial setup` headings carry the screen titles the user sees, with new sections for the Quick setup screen, the pre-fill screen, the review screen and Reauthenticate Tibber, and rows for every field; the options pages tabulate the fields they previously deferred to setup ("See setup step 1") under their own headings; README `## Entities` gains a switch, climate and datetime table, `## Troubleshooting` a `### Repair notices` list of all 26 repair titles; `docs/how-it-works.md` `### The house heat loss coefficient` states the learner's inputs, what an estimated power reading does to it, and the reset (brief item: the heat-loss learner's inputs, from R10-HOTFIX-LEARNER-INPUTS' merged diff 0cae227c3 and its harness, whose basis row reads `power = the pump's own estimate  metered`). User-doc markers, comment-wrapped, own line above the heading: R10-COP-GATE and R10-COP-PARTLOAD (`### COP, and the tracking-error gate`), R10-CEILING-PROBE (`### Active system identification`), R10-UX-HEALTH (`## The health page`), R10-ARCH-SHAPES-CLASSIFIER (`### Why a step is idle`).

Departure from the note, raised: no R10-WOOD-NOTIFY marker on the Wood Cheaper Than Heat Pump row. The tree's roster (`dev/programme/rosters/wave-r10-groups.json` at the fork, 236 groups) has no R10-WOOD-NOTIFY, so the marker is red under `doc_wiring_findings` (b) and under `marker_placement_findings` ("names no group in the roster"), placed exactly as section 3 says. The WOOD-NOTIFY carry udf-wood-homes already tells that group to document the window attributes; its "resolve the marker" clause finds none to resolve. The orchestrator can restore the marker once a roster record carrying R10-WOOD-NOTIFY is on main.

The strings.json history wording (design carry udf-strings-history) stays out of this diff: the stateless item covers the docs only, and the rewrite is already on R10-UX-HEALTH's carries.

Closes: none (owner request; roster group R10-USER-DOCS-FINAL, no issue).

## Head

191ed6b74b444351c07ac94238837c4b78bac7c8

## Mutation proof

Each production line in `tests/doc_claims.py` mutated in place, `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py`, restored from the committed file after each (driver: scratch, not in the tree), run from a `git archive` export of the branch with the head's `tests/doc_claims.py` (191ed6b74) in it: the unmutated export reads `2 of 277 checks FAILED`, both export artifacts (`every path resolves or is marked, ...` and `every named element resolves ...`, on `dev/governance/config/policy_budgets.json`, which the archive's export-ignore drops); every mutant below is red beyond those two, on the checks named.
- home-found predicate (`surface_rows`, `"home": int(found)` to `1`): 4 of 277, FAIL `red fixture: a service planted in services.yaml with no home is the one finding`, `red fixture: a Default cell that disagrees with the shipped default (away_dhw_min_temperature) is a finding`.
- default comparison (`default_agrees`, numeric arm reduced to `return m is not None`): 3 of 277, FAIL `red fixture: a Default cell that disagrees with the shipped default (away_dhw_min_temperature) is a finding`.
- `used to` purpose guard (`stateless_findings`, every `used to` skipped): 3 of 277, FAIL `red fixture: a history-sense "used to" is a finding`.
- stale exemption check (`surface_findings`, `if k not in set(keys)` to `if False`): 3 of 277, FAIL `red fixture: an exemption naming a surface no longer enumerated is a finding`.
- CHANGED field comparison (`surface_delta`, `a[k][f] != b[k][f]` to `False`): 3 of 277, FAIL `red fixture: a changed default is exactly one CHANGED line, nothing LANDED or REMOVED`.
- inside-a-comment predicate (`_in_comment` returns `False`): 6 of 277, FAIL `red fixture: a user-doc marker beside a missing path leaves the path a finding, and adds no due note`, `every marker sits on a page of its scope and names a roster group`, `null control: a README with one wiring and one wrapped marker gives one row of each scope`, `red fixture: a wrapped marker in docs/architecture.md is misplaced`.
- path mask (`doc_wiring_findings` (a), `_wiring(unit)` back to `_MARKER.search(unit)`): 3 of 277, FAIL `red fixture: a user-doc marker beside a missing path leaves the path a finding, and adds no due note`.
- stateless exemption matches once (`len(at) != 1` to `False`): 3 of 277, FAIL `red fixture: an exemption that matches no fragment is a finding`.
- bare marker on a user page (`marker_placement_findings`, first arm `if False`): 3 of 277, FAIL `red fixture: a bare marker in docs/setup.md is misplaced`.

Failing first: the arms committed in f1243b2bc, before any page edit, ran `2 of 277 checks FAILED`, the two being the coverage check (181 surfaces without a home) and the stateless check (51 hits); every fixture check passed.

## Claim table

Prose claims this diff writes that no arm reads (design section 4, item 3), each resolved in the tree at the head:

| page:anchor | claim | tree symbol | verdict |
|---|---|---|---|
| how-it-works.md `### The house heat loss coefficient` | a heat energy or thermal power meter makes the replayed heat measured | `thermal_model.heat_loss_basis`, `probe_install(...).measured_heat` | true |
| same | gaining better evidence discards the evidence gathered on the weaker basis | `heat_loss_basis_voids` in `_reanchor_house_heat_loss_scale` | true |
| same | a pump-estimated power figure is read as a meter | `probe_install(...).measured_power = bool(cfg.get(CONF_POWER_ENTITY))`; `dev/audit/harnesses/learner_inputs_swap.py` prints `power = the pump's own estimate  metered` | true |
| same | the button and `reset_heat_loss_learners` return both to 1.0 | `_void_heat_loss_learners`, `async_reset_heat_loss_learners` | true |
| same | changing the indoor or lower floor sensor resets the learner fitted on it | `HEAT_LOSS_ZONE_ENTITIES`, `heat_loss_entity_voids` | true |
| configuration.md `### The Quick setup screen` | a buffer-tank yes records 500 L | `quick_setup.QUICK_SETUP_BUFFER_VOLUME` | true |
| configuration.md `### The Pre-fill from a heat pump device screen` | After saving shows, default Menu, and setup continues to the finish menu | `_options_schema` (`CONF_AFTER_SAVE`, `AFTER_SAVE_MENU`), `async_step_device_prefill` returning `async_step_finish_setup` | true |
| configuration.md `### Reauthenticate Tibber` | a refused token leads to this screen | `async_step_reauth` to `async_step_reauth_confirm` | true |
| configuration.md `#### Two-Zone & Solar Configuration` | an untouched screen answers no | `async_step_zones` (`TWO_ZONE_MODE_OFF` on an unticked box) | true |
| README.md `### Repair notices` | each line's cause and remedy | `strings.json` `issues.<key>.description`, condensed | true |
| how-it-works.md `## The objective, term by term` | twice the chosen target pull costs 28.55 SEK against 23.28 | the paragraph's own measurement, restated without its version | unchanged figure |

## Null control

- The tree at the head: `--surfaces` exits 0 with every row `home-found 1`; `check_stateless` finds nothing; `--markers --user` lists the four wrapped markers above (five groups) and ends `4 user-doc marker(s), 0 due`.
- The same head checker over the merge base's pages (`git archive 460d7754f` of README.md, docs, blueprints, custom_components, tests/hastub, tests/harness.py, tests/throwaway_git.py, tools; head `tests/doc_claims.py` copied in; run from that export's root): `--surfaces` exits 1 with 181 of 492 surfaces unhomed (card_option 3, entity 8, option 44, option_page 1, repair 26, setup_field 88, setup_step 11); `stateless_findings` returns 51.
- Fixture controls in the arms: the delta of a list against itself is three empty sections; a README with one wiring and one wrapped marker gives one row of each scope; "previous day", a purpose-sense "is used to", "Refused together", a code span and a link anchor are not stateless findings; the unit with a bare wiring marker excuses its missing path.

## Figures

- Surfaces by class at the head: `python3 tests/doc_claims.py --surfaces | awk -F'\t' 'NF==6{print $1}' | sort | uniq -c` prints blueprint 4, card_option 10, card_view 6, entity 82, event 5, option 205, option_page 23, repair 26, service 14, setup_field 102, setup_step 15 (492). The note's counts paragraph names no command (carry udf-count-commands); these are that command's, and they agree with it except card_view (the note's 5 tabs plus the compact card the page map adds) and setup_field (the note gives none).
- Homes: `python3 tests/doc_claims.py --surfaces >/dev/null; echo $?` prints 0 at the head and 1 on the base export, where the stderr `#` lines number 181. The rule is `home-found 0` and not in `SURFACE_EXEMPT` (one entry). The design's 8 unhomed option labels are a first-cell census anywhere in the corpus; this rule also requires the row under the option's own page heading with an agreeing Default cell, which is why the base reads 44.
- Disabled-by-default entities: `awk -F'\t' '$1=="entity" && $6=="disabled"'` over the `--surfaces` output prints 20 rows; with the `entity_census` read as at the fork, 9.
- Stateless hits: `stateless_findings(_user_pages())` returns 51 on the base export and 0 at the head. Lexicon and guard are `_HISTORY` and `_PURPOSE` in the diff.
- Tables: `node tests/md_tables.mjs` prints `doc_orphaned_table_rows=0`, `doc_misrendered_lines=0`, `doc_swallowed_prose_lines=0` at the head.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 6 script(s) run, 27 scoped out` at the head (doc_claims.py, entities.py, harness_headers.py, md_tables.mjs, plan_view.py, card_drift.mjs; the last two joined with the D6 register commit). `tests/plan_view.py` and `node tests/card_drift.mjs` exit 0. Run locally with `PYTHONPATH=tests/hastub` against merge base 460d7754f48630a9fa0d84c31be78bc78d71c02b: `tests/doc_claims.py` ALL 277 checks PASSED; `node tests/md_tables.mjs` as above; `tests/harness_headers.py` red at 68dfc752a on `dev/audit/rounds/round4/D6/claims.py` (`config_defaults_compared` header 89, printed 92; `config_ranges_compared` 92, printed 101) and on the register files it rewrote, repaired in 94685087d (header counts with their reason, `claims.json` and `claims.md` regenerated: 92 defaults and 101 ranges compared, mismatches=[], 85 links, broken=[]); the re-run passes the D6 checks and leaves the tree clean, and its only reds are `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` (12 checks, `rc=124 ... wall limit 900s exceeded` at cpu 198.8 s under a load average near 100; it passed in the first run and reads none of the changed files); run_always `tests/layout.py`, `tests/closure.py selftest`, `tests/env_drift.py --claims-only <merge base>` exit 0; `tests/entities.py` under Red checks.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (no budget file touched).

## Red checks

none yet at this head (CI not run). Local only: `tests/entities.py` stops at its line 18440 on `PermissionError: Cannot get task port` (psutil under this seat's macOS sandbox, in `_hb_stdlib_reads`), a file this diff does not touch; its reads of the changed pages (lines 561 to 7591) precede that line, and none of the `FAIL` lines it printed before stopping names a documentation check: they are a3 to a10 lines, each following its own lane's "passes when" control, and hb (heartbeat) lines; I did not establish that every hb line is a planted fixture. CI runs it whole.

## Unpinned sites

none: the diff adds no site under `custom_components/` or `tools/` (`tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted`); its new predicates in `tests/doc_claims.py` are each pinned by a value check in the same script (Mutation proof).

## Forward-carry

- The keyed delta, `--markers --user`, the claim table and drift attribution for the true merge base: already on R10-USER-DOCS-VERIFY's carry udf-method (roster 315cd0441); the commands named there exist at this head as written. Carry: R10-USER-DOCS-VERIFY in `dev/programme/rosters/wave-r10-groups.json` (landed at handoff/audit-r10-roster 315cd0441, carry udf-method).

## Friction

none.
