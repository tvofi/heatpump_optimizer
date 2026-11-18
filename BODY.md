R11-PRE-PLAN-RENDER (part 2, the rest of the group): a round's plan page and its closure cover that round's groups only; the next round's groups are a second tab on a preliminary Gantt of their own.
Group R11-PRE-PLAN-RENDER, roster lane IN, size M. Part 1 (the phases section, carry 6's first half) is on main.

Owner instructions built here (verbatim in the group's carries 0-2, 6): a round's plan page and closure figure cover that round's groups; the next round's groups move to a second tab with a preliminary Gantt "built from the same duration model, starting at the current round's planned closure and labelled preliminary".

## Head

`6804e9c5a29946cbef4722088b1f668de6a246a8` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

11e9a4e9644e9a468dd2522f03a8450fbed23731, one commit on the reviewed head 8daf6df1576494f49f0ac32d790dbedbb6c92d0e (merge base 6f422812d5); `git merge-tree --write-tree origin/main HEAD` against origin/main c82f014a63 reported no conflict, so main was not merged.

Round 2: answers the first review's block (`review/3676` at f34eb2bf, class code-unwired).
- Block 1 (phase_hours unwired): `replan.MODEL_FIELDS` now names `phase_hours`, so `build_plan` copies it from `durations.json` into `generated.model`, which `plan_page.render` hands to `plan_phases.section`. It is not a required field (`model_refusals` lists the required ones), and `_model_duration` already refuses a non-positive, non-numeric or boolean figure as "duration unmeasured". The injected arm is replaced by one that goes durations (+`phase_hours={"finders": 7.5}`), then `replan.build_plan`, then `render`, and reads "7.5 h (plan model)" on the page; the injected arm tested only `section`, which this arm reaches through production. The `MODEL_FIELDS` and `plan_phases.MODEL_TIMED` comments state the wired source. Alternative not taken: a separate validated field in `build_plan`; the renderer's guard already refuses a bad figure, so a second validator would duplicate it.
- Block 2 (M6, M16, M15): three arms in `plan_page.py --self-test`: a next-round plan with its `generated.model` deleted makes `check_plan` return exactly `next round 10: model: the plan records no duration model (generated.model)`; a round-10 group with `savings="lots"` makes the producer's `build_plan` raise `PlanError`, read as `next_round.unavailable` with the round's own plan equal to the plan without it and drawn as `UNAVAILABLE: R10-NEXT-A: savings is not a number`; groups `R11-FAR-A` and `R12-FAR-B` under a round-9 plan give `beyond == 2`, round 10 scheduled alone, and the tab text "2 more group(s) belong to rounds after 10".

- Carry 0 (round filter) and Carry 1 (second tab, preliminary Gantt): a group belongs to the round its id names (`roster_lib.group_round`, `next_round_groups`, `round_roster`): the one rule. A group of a later round is outside the plan's closure, lanes, stamps, strip counts and projected-issues chart.
- `replan.build_round_plan` (the CLI's entry) plans the round's groups with `build_plan`, unchanged, then prices the nearest later round on the same durations and caps from the round's closure (`next_round_preview`): its plan is `plan["next_round"]["plan"]`, a full plan that `check_plan` also checks. An `after` edge from a later-round group to an earlier-round group is dropped (that round is closed by then); a group of this round waiting on a later-round group is refused (`PlanError`). A later round the model cannot plan is `next_round.unavailable`, drawn as an UNAVAILABLE tab, never an absent one. Groups of rounds past the nearest are only counted (`beyond`).
- `plan_page.render` draws the round's groups on the first tab and, when the plan carries `next_round`, a second tab "Round N (preliminary)" with its own swimlanes, group rows and planned stamps (`next_round_pane`, rows through the shared `group_rows`). A plan or roster with no later-round group renders no tab.
- Carry 3 (description, strip, lede): `roster_lib.one_line_brief` reads a markdown heading as its title line and strips an opening list marker, so "1." alone and run-together headings are gone; the strip's part-merged count and the row label share one predicate (an absorbed group a merged PR names is not part merged); the lede's open-group figures are asserted equal to the rows.
- Carry 4: the closure figure no longer counts post-closure R11-PRE groups (they are a later round's); running-as-not-started is the stage word's reading, removed by carry 5's evidence flags; "a serial after-edge prices parallel work as a sum" was not re-measured or changed (see Forward-carry).
- Carry 5: the plan beat hands `replan.py` `--live-refs` and `--in-flight` from the overlay keys `plan_live_refs` and `plan_in_flight` (declared in `sweep_template.md`; absent keys leave the stage word, as before).
- Carry 6, rest: a phase the model prices (finders, verify and judge, plan) prints `durations.json`'s `phase_hours` figure, carried through `generated.model`, or "duration unmeasured" where it has none. `durations.json` has no `phase_hours` yet, and I did not add a measurement from round 10's record, so the page prints those phases unmeasured, as the carry allows. The page for a round with no roster yet renders (part 1); `replan.py` still refuses a closed round's plan, by design.

Carry 2 (the prototype as model): the prototype page script is out of tree (scratch of the round-10 orchestrator, unreachable from this container); the tab is built to the carry's text. Carry: dismissed: no copy is reachable to build against. Carry 5's retirement of the local 150→420 s render-timeout raise in `$HPO_STATE_DIR/s14/beat_extras.sh` is out of tree and not done here.

## Mutation proof

Each mutant applied to the production line, `PYTHONPATH=tests/hastub python3 tools/audit/seat/plan_page.py --self-test` (or `beat_jobs.py --self-test`), restored after:
- `roster = roster_lib.round_roster(roster, round_n) if later else roster` → `roster = roster`: the fixture arms die (`KeyError: 'R10-NEXT-A'`, 129 checks, 1 failed).
- `part = [] if g in done else sorted(...)` → `part = sorted(...)`: FAIL "the strip's part-merged count equals the rows that read part merged".
- `if n not in later and a:` → `if False:` in `build_round_plan`: FAIL "a group of this round waiting on a later round's group is refused".
- `plan_phases._model_duration`'s `isinstance(h, bool) or ... or h <= 0` → `False`: the phases census and the fixture arms fail.
- `beat_jobs.py` `evidence += [flag, ...]` → `pass`: the ledger mutant `plan_evidence_dropped` is killed by "the overlay's ref listing and in-flight PRs reach replan".

Round 2, the reviewer's driver (`review/3676:evidence/mutation_driver.py`) restricted to M6, M15, M16 plus the wiring line's own mutant, each over `plan_page.py` and `replan.py --self-test`, restored after (`git status` clean):
- M6 `check_plan`'s next-round recursion → `pass`: KILLED, FAIL "check_plan checks the next round's plan: a violation in it is the round plan's, named by the next round" (got `[]`).
- M15 `"beyond": len(later) - len(mine)` → `0`: KILLED, FAIL "groups of rounds past the nearest are counted in beyond, not scheduled, and the tab says so".
- M16 `except PlanError` → `except ZeroDivisionError`: KILLED, FAIL "a later round the model refuses is next_round.unavailable, the round's own plan unchanged, drawn as an UNAVAILABLE tab" (got the escaped `R10-NEXT-A: savings is not a number`).
- MW `MODEL_FIELDS` without `"phase_hours"`: KILLED, FAIL "a phase durations.json prices reaches the plan's model and the page prints its figure ...".

Failing case first: this head's `plan_page.py` over 8daf6df's production files (`git apply` of the self-test hunk only): `plan_page self-test: 152 checks, 1 failed`, the failure the phase arm above (got `(2, 2)`: no figure printed). The M6, M15 and M16 arms pass there, because the behaviour they pin is already present at 8daf6df; each fails under its mutant above.

## Null control

- "null control: a page whose roster has no next-round group has no tabs".
- "a roster with a next-round group plans the same closure, groups, stamps and waves as the roster without it": `{k: v for k, v in p2.items() if k != "next_round"} == p0`.
- "adding a next-round group changes nothing on the current tab and adds one bar to the other": panes compared byte for byte, 2 bars become 3 on the second tab only, the first tab identical, though a next-round group carries an open issue.
- "the current round's tab is the page without the next round's groups": the first pane equals the groups-only page from `<div class="strip">` to `</main>`.
- `plan_page.py` over a plan recorded without `next_round` draws no later-round row and no tab.
- Round 2: the phase arm asserts the fixture `plan` (durations without `phase_hours`) carries none and prints no "plan model)"; the M6 arm's control is `check_plan(p2) == []` on the unbroken plan; the M15 arm asserts `beyond == 0` and no "more group(s) belong" on the roster with round 10 only.
- The reviewer's control reproduces: a one-group round-11 roster through `build_plan` over `durations.json` plus `phase_hours={"finders": 7.5}` prints `phase_hours in generated.model: {'finders': 7.5} check_plan: []` at this head and `phase_hours in generated.model: False check_plan: []` at 8daf6df.

## Figures

- `PYTHONPATH=tests/hastub python3 tools/audit/seat/plan_page.py --self-test`: `plan_page self-test: 152 checks, 0 failed` (8daf6df: 149; the injected phase arm replaced, three arms added).
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/beat_jobs.py --self-test`: `beat_jobs self-test: 274 checks, 0 failed` (base: 271, 0 failed).
- `PYTHONPATH=tests/hastub python3 tools/plan/replan.py --self-test`: `self-test: 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/doc_claims.py`: `ALL 410 checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2723 ENTITY CHECKS PASSED`.
- prepr: passed rc=0 at 11e9a4e9644e9a468dd2522f03a8450fbed23731 (`PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`, scoped).

<!-- figure-block: scope-line mb=6f422812d5d8b918beace0283419c153f6df66ce head=6804e9c5a29946cbef4722088b1f668de6a246a8 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

- Destination file: `dev/programme/rosters/wave-r10-groups.json`; the unbuilt items stay on the group's own carries 2, 4 and 5 there, unchanged by this diff. Carry: dismissed: the orchestrator rules whether a further part is dispatched

- "A serial after-edge prices parallel work as a sum" (PC-1113-05) was not measured or changed here. Carry: dismissed: the next round's plan does not exist to measure against until a round-11 roster does, and the claim has no instance in the tree to re-run.
- The out-of-tree timeout raise and the round-10 orchestrator's prototype page script (above). Carry: dismissed: both live in `$HPO_STATE_DIR`, which a cloud seat cannot read or write.
- A measured `phase_hours` for finders, verify and judge, and the plan, from round 10's record. Carry: dismissed: R11-PRE-ROUND-METRICS is carries-open and receives none; a figure written to `durations.json`'s `phase_hours` reaches the page at the next `replan.py` run, through `generated.model`

## Friction

none
