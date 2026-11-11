R10-ARCH-DOCS, arm B of triage P261: `docs/architecture.md` and `dev/README.md` verified against the tree, every wiring marker resolved, the machinery figure redrawn and pinned. Closes #2395. Part of #201.

What landed, by brief item:

1. **Verification and marker resolution.** Every `[target:]` and `[retired-by:]` marker on the two pages is now a statement of the tree, or is corrected where the landed shape departs from the planned one. Departures, each with the group that caused it:
   - R10-CI-LAYOUT-P2:
     - The umbrella calls a ninth unit, `kernel-points`, which the planned graph did not draw and the workflow list called "called by nothing".
     - The prelude's outputs are `kind`, `pr`, `base`, `head` and a work set; the figure said `scope`.
     - `ci.yml` is the live umbrella, not the inert stub. Every unit is a `workflow_call` file, so "each unit file starts on its own pull-request event" was false.
     - Both rerun workflows are gone, as marked.
     - The list omitted `marketplace.yml`, `dependabot-automerge.yml` and `dependency-graph.yml`.
     - The owner step (ruleset requires only `gate`) is stated as landed on the authority of `dev/governance/roles/nudge.md` section 4 and `dev/programme/delivery/2673.md`. This seat has no ruleset API read, so it is not read from the live object. `tools/ci/fixtures/ruleset/ruleset_23698884.json` still lists the 17 contexts; it is `ruleset_cutover.py`'s rollback copy.
   - R10-ORCH-MACHINERY:
     - `beatd.py` does not drive the tick, the relay, the train or the heartbeat. `tick_loop.sh` does, and the beat's job table is a disjoint set.
     - The ledger kinds `stage-mismatch` and `absorb-edge-missing` never landed (carry 9). The page now names only keys of `KINDS`.
     - No script opens `train-stop`. The sequence note "a refusal opens train-stop" is removed.
   - R10-FLOW-RELAY-HOLD: the hold list is a state-directory file that only the orchestrator writes. The planned edge drew it acting on the relay.
   - R10-PLAN-ARTIFACT, R10-FLOW-TOOLKIT-MODEL, R10-FLOW-TOOLKIT-MEASURE: the plan model is `tools/plan/replan.py`. The four flow instruments do not import it, so "extended by the flow toolkit's projection" is replaced by what each one reads.
   - R10-PARAMS-OWNER: the coordinator context is not "written once". It is a frozen value replaced whole.
   - R10-ARCH-SHAPES: the hour clock has two owners with two rules (`quiet_windows.wall_clock`, `dhw_schedule.format_clock`), not one.
   - R10-SENSOR-PAYLOAD: one payload-number mixin, not separate value and path mixins.
   - R10-SCORES: reworded to carry 4's landed shape.
   - R10-LIVESTATE, R10-HEAT-METER, R10-COP-GATE, R10-LEARNER-ETA, R10-CONFIGFLOW-PAGES landed as planned; each is now stated with its owning module.
   - Wrong at the base with no landing group behind it (R10-ARCH-DOCS-FIRST's own text):
     - The relay "opens" a pull request. The opener job does; the relay only updates.
     - The merge train's "pitch" and "gap rule". `merge_train.py` has neither; the pitch is `record_row.py`'s, for the record pull request.
     - "`inputs.InputReader` performs every entity read". `pump_arbiter.py`, `early_cutoff.py` and the coordinator read the pump's own controls directly.
     - The learners "never call the glue". Two import `store.py`.
     - The `button.py` row omitted the reset-heat-loss button.
2. **The machinery figure (carries 2, 3, 12).** Redrawn top-down from one entry, actors in one group and stores in another. Every arrow is `runs` or `writes`, from the actor. The table under it cites, per arrow, the file and the quoted text that performs it.
   - Design choice: the citation table lives on the page, not in the test. The owner asked to be able to check each direction, and a list kept in the test would be the second copy `fixer.md` step 11 warns of.
   - Design choice: reads are not drawn. The prose under the table states them.
   - A person's arrow cites the contract or instrument guide that says the person does it. The "file is one the actor's node names" rule applies to script actors only, so a person's arrow is pinned by its quoted text alone.
3. **The pins, in `tests/doc_claims.py`.**
   - `machinery_edge_findings` refuses: an arrow with no row, a row with no arrow (together these refuse a reversed arrow), an arrow starting at a store, a verb other than `runs` or `writes`, `writes` ending at an actor, a quoted text the cited file no longer holds, a script actor citing a file its node does not name, and a second entry.
   - `due_marker_findings` makes "no unresolved target marker on main" a hard check (carry 7). User-doc markers are left to `--markers --user` (carry 11).
   - Two anchors that required a marker to exist are relaxed, because the round's end state has none. The fixtures carry the non-vacuity.
4. **Closure.** The new predicate opens the nine cited files that were INERT. They move to `INERT_EXCEPT`, and the closures of `tests/doc_claims.py` and `tests/entities.py` are re-recorded: `entities.py` reads three of the nine, which the table listed under its inert reads only.

Brief carries, by the dispatch brief's numbers, which count from 0. `review_packet.py` counts the same fifteen from 1, so its Carry 15 is the brief's Carry 14, and each number here is one lower than the packet's. Carry 0 and Carry 12 are item 2. Carry 1, Carry 6, Carry 8 and Carry 10 moved to R10-USER-DOCS-VERIFY and are not touched (Carry 13). Carry 2 and Carry 3 are items 2 and 3. Carry 4 is the R10-SCORES line. Carry 5 and Carry 7: arm A's checker is present and green at this head and was not rebuilt. Carry 9 is the ledger-kind departure. Carry 11: user-doc markers are left. Carry 13: no file outside the two pages' docs is edited among user pages; no departure was looked for or found in `README.md` or a user page. Carry 14: done at this merge base; the re-read after the last product merge is R10-ARCH-DOCS-DELTA's.

Outside the roster group's `files`: `tests/doc_claims.py` (carry 2 item 3 names it), `tests/closure.py` and `tests/closures.json` (item 4), and the mutant harness (`fixer.md` step 18).

Alternatives not taken:
- Deriving each arrow's direction from which script names which. A comment or a log string naming the other script satisfies it in both directions, so a reversed arrow would stay green.
- Keeping the two relay arms as two nodes. `tick_loop.sh` starts one `pass`, and the arms are functions inside it, so two nodes would draw two starts the code does not make.
- Drawing reads as dashed arrows. The owner's convention is one meaning per arrow.

## Head

c4c28b4cef17868052d2018879340e617b2ca119 (base d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a, origin/main at 2026-11-11T00:59Z).

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_arch_docs_mutants.py` at the head. It replaces each predicate's test with one that cannot fire, runs `tests/doc_claims.py` on the mutated source, and prints the checks that fail. Nothing is written to the tree.

- due marker, `if r["due"] and r["scope"] == "wiring"` -> `if False`: FAIL `red fixture: a due wiring marker is refused, and a not-yet-due one is not (null control)`
- verb: FAIL `red fixture: a verb that is not runs or writes is a finding`
- store as actor: FAIL `red fixture: a store drawn as the actor (is read by) is a finding`
- writes ends at a store: FAIL `red fixture: writes ending at an actor is a finding`
- arrow with no row: FAIL `red fixture: one arrow reversed is a finding`
- row with no arrow: FAIL `red fixture: a row with no arrow is a finding`
- quoted text in the cited file: FAIL `red fixture: a cited line the code no longer holds is a finding`
- cited file is the actor's: FAIL `red fixture: an arrow reversed together with its row is a finding`
- one entry: FAIL `red fixture: an actor nothing starts, a second entry is a finding`
- node names unique: FAIL `red fixture: two nodes of one name is a finding`
- cited file tracked, and one arrow per line: the run dies (`TypeError`, `AttributeError`) on the fixture that plants the case. Killed by a crash, not by a named check.

## Null control

- The harness's baseline, the unmutated file, prints no FAIL line.
- `machinery_edge_findings` on the clean fixture returns nothing: `the clean fixture yields no finding (null control)`.
- The owner's control on the page's own figure: `reversing any one arrow of the page's figure is a finding`. The check reverses each arrow in turn and requires a finding every time; it also requires the unreversed page to be clean.
- A marker naming a not-started group, and a due user-doc marker, are not refused: `red fixture: a due wiring marker is refused, and a not-yet-due one is not (null control)` and `a due user-doc marker is left to its own resolver (null control)`.
- The marker resolver at the base, before any edit, with the roster branch's file: `python3 tests/doc_claims.py --markers --roster <handoff/audit-r10-roster's wave-r10-groups.json>` printed `28 of 28 marker(s) due`, two `UNRESOLVED` lines (`stage-mismatch`, `absorb-edge-missing`) and exit 1.

## Figures

- Marker resolver at the head: `python3 tests/doc_claims.py --markers` and the same with `--roster` on the roster branch's file (39a92af760) each print `0 of 0 marker(s) due`, exit 0. The base figure is under `## Null control`.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at the head: `ALL 318 checks PASSED`.
- Mutants: the harness prints `RESULT baseline_fails=0`, `RESULT mutants=12`, `RESULT killed=12`. Rule: one mutant per predicate test of the two new functions; a row whose text is not in the file exactly once is an error.
- Mermaid: `NODE_PATH=$(npm root -g) node dev/audit/harnesses/r10_mermaid_parse.mjs tools/site dev/README.md docs/architecture.md` printed `mermaid 12.3.0 parse+render in Chromium: 5 block(s), 0 failure(s)`. Taken at f043978af8; `git diff --quiet f043978af8 HEAD -- dev/README.md docs/architecture.md && echo UNCHANGED` prints UNCHANGED.
- The machinery figure was rendered in the default and the dark mermaid theme with the pinned mermaid and looked at: one entry at the top, the actors' group above the stores' group. A scratch render, not in the tree.
- Edge anchors: each quoted text was checked with `grep -qF` against its cited file before the table was written; the gate check `every arrow is cited, every citation holds in the tree, and the figure has one entry` repeats it on every run.
- Closure: `./tests/derive_closures.sh --single tests/doc_claims.py` (Linux) first exited 1 naming nine INERT files as read; after `INERT_EXCEPT` it exited 0 and updated one closure. `tools/pr/prepr.sh` at 85b458a18d then refused `ci predict` with three `UNDER-SCOPED tests/entities.py` lines and one `INERT READS tests/harness_headers.py` line, and its `self-test` step with the null control that the same predicted red trips. `./tests/derive_closures.sh --single tests/entities.py` exited 0, and `tools/pr/ci_predict.py --base origin/main --apply-inert` then printed `no closures, fast, governance or instrument red predicted`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`. Before the closure commit it printed `MODE: SCOPED -- 4 script(s) run`, and `tests/doc_claims.py`, `tests/entities.py` and `tests/md_tables.mjs` ran green at f043978af8. `tests/harness_headers.py` failed one check on the new harness (`every inlined walk matches the canonical helper and no depth root remains`: a fixed parent depth for the root); the harness now carries the canonical walk, and at the head the script prints `ALL 112 HARNESS HEADER CHECKS PASSED`. The closure commit edits `tests/closure.py`, which the gate cannot scope.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Seams (`fixer.md` step 8). The class is "a figure arrow whose direction the code contradicts". Enumerator: the `-->` lines of the block under `### Its components`, which the gate check reads. Every one is closed in this diff by its table row. The other three figures in `dev/README.md` and the one in `docs/architecture.md` are not under the convention: their arrows mean "needs" or "data flows to", and `named_element_findings` resolves their nodes. No instrument checks those arrows' directions.

## Red checks

none

## Forward-carry

- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `tests/doc_claims.py` now refuses a bare marker whose groups are all done, so the re-read after the last product merge states the tree and adds no marker for a landed group. The "One owner per concern" bullets in `docs/architecture.md` were written at d08ed31049; re-check each against its module at the delta's merge base. Control: `python3 tests/doc_claims.py --markers --roster <the roster branch's file>` exits 0 with `0 of 0 marker(s) due`. Carry: R10-ARCH-DOCS-DELTA
- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `dev/README.md` states that the ruleset requires only `gate` on `nudge.md` section 4's authority, not from a live read. A seat with the ruleset read confirms it against ruleset 23698884, or corrects the sentence. Carry: R10-ARCH-DOCS-DELTA
- `dev/programme/rosters/wave-r10-groups.json`, R10-USER-DOCS-VERIFY's brief: `check_marker_census`'s anchor no longer requires a marker to exist, so removing the last user-doc marker leaves `tests/doc_claims.py` green. Control: `python3 tests/doc_claims.py --markers --user` ends `0 user-doc marker(s), 0 due`. Carry: R10-USER-DOCS-VERIFY

## Friction

none
