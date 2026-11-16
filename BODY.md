R11-PRE-PLAN-RENDER (part 2, the rest of the group): a round's plan page and its closure cover that round's groups only; the next round's groups are a second tab on a preliminary Gantt of their own.
Group R11-PRE-PLAN-RENDER, roster lane IN, size M. Part 1 (the phases section, carry 6's first half) is on main.

Owner instructions built here (verbatim in the group's carries 0-2, 6): a round's plan page and closure figure cover that round's groups; the next round's groups move to a second tab with a preliminary Gantt "built from the same duration model, starting at the current round's planned closure and labelled preliminary".

## Head

a03ff5d77e8dc5ca7ccfa460f410c0fc06e5144f, cut from origin/main at 6f422812d5 (2026-11-16T16:47:19Z); `git merge-tree --write-tree origin/main HEAD` reported no conflict.

- A group belongs to the round its id names (`roster_lib.group_round`, `next_round_groups`, `round_roster`): the one rule. A group of a later round is outside the plan's closure, lanes, stamps, strip counts and projected-issues chart.
- `replan.build_round_plan` (the CLI's entry) plans the round's groups with `build_plan`, unchanged, then prices the nearest later round on the same durations and caps from the round's closure (`next_round_preview`): its plan is `plan["next_round"]["plan"]`, a full plan that `check_plan` also checks. An `after` edge from a later-round group to an earlier-round group is dropped (that round is closed by then); a group of this round waiting on a later-round group is refused (`PlanError`). A later round the model cannot plan is `next_round.unavailable`, drawn as an UNAVAILABLE tab, never an absent one. Groups of rounds past the nearest are only counted (`beyond`).
- `plan_page.render` draws the round's groups on the first tab and, when the plan carries `next_round`, a second tab "Round N (preliminary)" with its own swimlanes, group rows and planned stamps (`next_round_pane`, rows through the shared `group_rows`). A plan or roster with no later-round group renders no tab.
- Carry 3: `roster_lib.one_line_brief` reads a markdown heading as its title line and strips an opening list marker, so "1." alone and run-together headings are gone; the strip's part-merged count and the row label share one predicate (an absorbed group a merged PR names is not part merged); the lede's open-group figures are asserted equal to the rows.
- Carry 4: the closure figure no longer counts post-closure R11-PRE groups (they are a later round's); running-as-not-started is the stage word's reading, removed by carry 5's evidence flags; "a serial after-edge prices parallel work as a sum" was not re-measured or changed (see Forward-carry).
- Carry 5: the plan beat hands `replan.py` `--live-refs` and `--in-flight` from the overlay keys `plan_live_refs` and `plan_in_flight` (declared in `sweep_template.md`; absent keys leave the stage word, as before).
- Carry 6, rest: a phase the model prices but has no figure for (finders, verify and judge, plan) prints "duration unmeasured" in its Planned cell; `durations.json` has no `phase_hours`, and I did not add a measurement from round 10's record, so the page prints it as unmeasured, as the carry allows. The page for a round with no roster yet renders (part 1); `replan.py` still refuses a closed round's plan, by design.

Not built: carry 2's prototype `build_tabs.py` is out of tree (scratch of the round-10 orchestrator, not reachable from this container); the tab is built to the carry's text. Carry 5's retirement of the local 150→420 s render-timeout raise in `$HPO_STATE_DIR/s14/beat_extras.sh` is out of tree and not done here.

## Mutation proof

Each mutant applied to the production line, `PYTHONPATH=tests/hastub python3 tools/audit/seat/plan_page.py --self-test` (or `beat_jobs.py --self-test`), restored after:
- `roster = roster_lib.round_roster(roster, round_n) if later else roster` → `roster = roster`: the fixture arms die (`KeyError: 'R10-NEXT-A'`, 129 checks, 1 failed).
- `part = [] if g in done else sorted(...)` → `part = sorted(...)`: FAIL "the strip's part-merged count equals the rows that read part merged".
- `if n not in later and a:` → `if False:` in `build_round_plan`: FAIL "a group of this round waiting on a later round's group is refused".
- `plan_phases._model_duration`'s `isinstance(h, bool) or ... or h <= 0` → `False`: the phases census and the fixture arms fail.
- `beat_jobs.py` `evidence += [flag, ...]` → `pass`: the ledger mutant `plan_evidence_dropped` is killed by "the overlay's ref listing and in-flight PRs reach replan".

## Null control

- "null control: a page whose roster has no next-round group has no tabs".
- "a roster with a next-round group plans the same closure, groups, stamps and waves as the roster without it": `{k: v for k, v in p2.items() if k != "next_round"} == p0`.
- "adding a next-round group changes nothing on the current tab and adds one bar to the other": panes compared byte for byte, 2 bars become 3 on the second tab only, the first tab identical, though a next-round group carries an open issue.
- "the current round's tab is the page without the next round's groups": the first pane equals the groups-only page from `<div class="strip">` to `</main>`.
- `plan_page.py` over a plan recorded without `next_round` draws no later-round row and no tab.

## Figures

- `PYTHONPATH=tests/hastub python3 tools/audit/seat/plan_page.py --self-test`: `plan_page self-test: 149 checks, 0 failed`.
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/beat_jobs.py --self-test`: `beat_jobs self-test: 274 checks, 0 failed` (base: 271, 0 failed).
- `PYTHONPATH=tests/hastub python3 tools/plan/replan.py --self-test`: `self-test: 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/doc_claims.py`: `ALL 410 checks PASSED`.

<!-- figure-block: scope-line mb=6f422812d5d8b918beace0283419c153f6df66ce head=a03ff5d77e8dc5ca7ccfa460f410c0fc06e5144f -->
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
- A measured `phase_hours` for finders, verify and judge, and the plan, from round 10's record. Carry: dismissed: R11-PRE-ROUND-METRICS is carries-open and receives none; the page prints the phases unmeasured until a measurement lands in the durations file

## Friction

none
