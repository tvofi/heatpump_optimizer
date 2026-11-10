# R10-ARCH-DOCS design note (arm B, after the 2026-11-10 split)

Base: origin/main 96346fdec3ad64ddb2f2c66c87bafa250b40fac4; there is no predecessor handoff head, so the code is read at the base. Roster: origin/handoff/audit-r10-roster d7d5ba411. Inputs: the study (handoff-body/r10-arch-docs-study 14c47bcee, BODY.md, measured at 28d46c49), re-anchored at the base by this seat. The R10-ARCH-DOCS-FIRST note is at f122a1cb5 on design/r10-arch-docs-first. It is not on main, so `dev/programme/designs/` resolves only on design refs.

## 1. Owning seam, and a dispatch precondition

- **Prose and figures:** owned by docs/architecture.md and dev/README.md, this group's `files`.
- **The pins (edge direction and the marker ban):** owned by tests/doc_claims.py, beside `doc_wiring_findings` and `named_element_findings`. tests/seam_map.json maps coordinator methods only, so it names no owner here.
- **One owner, but outside this group's `files`.** tests/doc_claims.py belongs to R10-USER-DOCS-VERIFY, which is not started and now runs beside this group (carry 13). This is a single concern, so it is not a two-owner stop.
- **Precondition, before the fixer dispatches** (orchestrator, `roster_edit.py`):
  - `set-files` adds tests/doc_claims.py to R10-ARCH-DOCS;
  - R10-USER-DOCS-VERIFY gains an `after` edge on R10-ARCH-DOCS, so the two never edit the file at once.
- **Without that op the pins cannot land.** The fixer then reports and stops; it does not fall back to alternative A1.

## 2. Shape

**(a) Marker resolution.**
- Measure: `python3 tests/doc_claims.py --markers --roster <roster json>` reports 28 of 28 markers due at the base, 9 in docs/architecture.md and 19 in dev/README.md.
- Every marker's group is done on the roster branch. Main's roster copy is stale and shows two as not due.
- Each `target` marker becomes a plain statement of the tree. Each `retired-by` line is deleted, because its file is gone (`*-rerun.yml`, removed by R10-CI-LAYOUT-P2).

**(b) The hard check, a marker ban.** After (a), item (c) of `doc_wiring_findings` changes from a note to a finding: *any* `[target:]` or `[retired-by:]` marker in a wiring doc is red.
- **Wiring docs only.** Comment-wrapped user-doc markers stay R10-USER-DOCS-VERIFY's (carry 11).
- **No roster read.** The check depends on no roster state, so it holds the f122a1cb5 section 3 state-tolerance invariant trivially.
- **Effect on DELTA.** R10-ARCH-DOCS-DELTA writes plain text and never a marker.

**(c) The "Its components" figure, redrawn** (dev/README.md, under "## The orchestration machinery").
- Draw from the study's draft, as corrected at the base (section 3 below).
- Layout is `flowchart TB`, with one entrypoint: the owner or orchestrator dispatching a seat.
- Actors and stores sit in separate subgraphs.
- Every solid arrow is "writes" or "triggers", drawn from the actor to the target. A one-line legend states this convention.
- **Reads are not drawn.** The prose names them.
- **beatd's launcher is stated as plain fact.** Nothing in the tree runs `beatd.py run`:
  - `governance.yml` runs only `--self-test`;
  - `liveness.py` runs only `status`.

**(d) Edge-direction pin.**
- **Evidence table.** Under the figure, the fixer adds one row per drawn edge: actor, verb, target, actor file, and a quoted phrase.
- **New predicate** in tests/doc_claims.py, placed after `check_named_elements`. For that figure only, it:
  1. parses each `A -->|"verb"| B` edge, splitting `&` on both ends;
  2. requires a table row with the same actor, verb and target;
  3. requires the row's phrase to occur in the actor's file at HEAD.
- **Why reversals go red:**
  - An arrow reversed in the figure alone fails step 2.
  - An arrow reversed in both figure and table fails step 3, because the phrase is now looked up in the target's file.
- **Phrases, not line numbers.** Across 28d46c49..base, 142 commits touched the cited files.

**(e) Prose corrections.** Each row of the table below.

## 3. Departures found at the base (each named with its cause)

| where | departure | caused by |
|---|---|---|
| dev/README.md CI section, umbrella figure, workflow list | `ci.yml` is described as an inert stub and units as starting on their own events. In fact every unit is `workflow_call`; `ci.yml` is live, has `prelude`, `kernel-points`, `pr-contract` and `gate`, and the ruleset requires `gate` alone. `kernel-points.yml` is called by `ci.yml`, not standalone | R10-CI-LAYOUT-P2 (#2737) |
| components figure and beat prose | beatd is drawn driving the tick, the relay and the heartbeat. Its job table runs `beat_jobs.py` rows instead: roster-drain, plan-beat (replan, state_docs, plan_page), opener (open_driver), and others. tick_loop.sh drives the relay (:131), the tick (:169), the train sweep (:149) and `heartbeat.sh --once` (:175) | R10-FLY-STANDING-CONTRACTS (#3197), on R10-ORCH-BEATD |
| components figure | the study's own errors, corrected here: (1) the relay handoff arm *writes* the ledger (cloud_relay.sh:633-638), so it is not reversed; (2) relay and opener edges target the PR branch, not main; (3) the roster is written by postmerge.py→roster_sync, because `state_docs.py beat --apply` has no launcher; (4) the bus nonce file is written by `bus.sh dispatch`. Missing from the study: relay→`bus.sh confirm`→train add, and the carry-fold arm (67a823c2e) | study snapshot; 67a823c2e |
| dev/README.md ledger kinds | `stage-mismatch` and `absorb-edge-missing` are not keys of `KINDS` in tools/audit/seat/ledger.py, so they are deleted. The events list gains `approve-held-runs`, `dispatch` and `postmerge-owed` | never built; text from R10-ARCH-DOCS-FIRST (#2609); carry 9 |
| dev/README.md sequence note "a refusal opens train-stop" | no production writer of `train-stop` exists; the only reader is merge_train.py sweep. Reword as "the train halts on an open train-stop event" | R10-ORCH-LEDGER |
| dev/README.md layout | the designs path lives on design refs, not main; the roles list is missing the planner and standing contracts; ADRs 0015 and 0016 are not named | R10-ARCH-DOCS-FIRST authoring, decision 0015 |
| docs/architecture.md `[target: R10-SCORES]` line | rewrite as what landed (carry 4): one rule; `model_restart_advice` feeding both the scores and the advisor; `house_loss_converged` shared with Health. No view model behind Savings and Health exists. State that the Driving grade keeps its own day book apart from the savings settlement | R10-SCORES (#2647) |
| docs/architecture.md button row; "no group adds a module" | the reset-heat-loss button is missing from the row. heat_energy.py, driving_grade.py and slot_drivers.py were added (the map already lists them), so the sentence goes | R10-HOTFIX-LEARNER-INPUTS (#3022); R10-HEAT-METER, R10-GRADE-DRIVERS, R10-WHY-NOW-WIDGET |

README.md and the user pages: no departure found beyond the four comment-wrapped markers, which are R10-USER-DOCS-VERIFY's. Nothing to stop on.

## 4. Alternatives

- **A1, a new tests/doc_edges.py.** Lost: it needs a `run` line in tests/run.sh and a closure in tests/closures.json, both gate files, so it forces FULL. It also adds a script run against `tests/ci_budgets.json`, and that raise is the owner's.
- **A2, line numbers in edge labels.** Lost: the 142 commits across the window would break the figure without changing any edge.
- **A3, a hard check of "no marker names a done group", read from the roster.** Lost:
  - it breaks the state-tolerance invariant;
  - its red would land on the stamp push of unrelated work;
  - main's roster copy is stale (it reads TOOLKIT-MODEL as not started).
- **A4, the evidence table as a dict in tests/doc_claims.py.** Lost: it gives the reader no citations, and it is a second source the figure must stay in sync with. The doc table is the predicate's only input.

## 5. Sibling sites

- `grep -n '^```mermaid' docs/architecture.md dev/README.md` finds 5 blocks. Only "Its components" takes the edge pin (carry 2).
- The CI umbrella figure takes (a): its dashed "lands later" edges become solid.
- The sequence diagram takes the train-stop wording.
- `grep -nE '\[(target|retired-by): ' docs/architecture.md dev/README.md` lists every row for (a).

## 6. Evidence plan

1. **Failing first.** At the base:
   - the new edge predicate is red on the current figure (for example `tick --> orch`, and beat→relay has no row);
   - the marker ban is red, with 28 markers.
2. **Fixer null controls** (inline fixtures, as `check_named_elements` does):
   - the redrawn figure is green;
   - reversing one arrow is red;
   - reversing it in figure and table is red;
   - deleting the phrase from the code fixture is red;
   - a user-doc marker under the ban is green, because it is out of scope.
3. **Finder's harnesses at both ends:**
   - `python3 tests/doc_claims.py`;
   - `--markers --roster <roster json>` prints 0 due;
   - `NODE_PATH=$(npm root -g) node dev/audit/harnesses/r10_mermaid_parse.mjs <tools/site> dev/README.md docs/architecture.md` reports 0 failures (`npm ci` in tools/site first);
   - `PYTHONPATH=tests/hastub python3 tests/entities.py`.
4. **Mutation proof targets:** the new predicate's actor/target match, its phrase lookup, and the ban's marker regex.
5. **Goldens and claims:** no golden moves, so both claim files stay byte-identical.

## Notes for the fixer

- Put the new code after `check_named_elements`. dev/programme/carries/carry-1645.json cites tests/doc_claims.py:479 and :570; an insertion above them broke #3011 (d31683a71). Carry: R10-ARCH-DOCS (item ad-insert-below)
- Before pinning, re-open every edge phrase at your own merge base. The study's lines are a snapshot; this seat's re-anchors are listed per row in section 3. Carry: R10-ARCH-DOCS (item ad-reanchor)
- The marker ban changes how DELTA works: it writes no marker. The fixer's PR carries this into DELTA's roster brief before merging. Carry: R10-ARCH-DOCS-DELTA (item ad-marker-ban)
- tests/doc_claims.py is shared; R10-USER-DOCS-VERIFY rebases onto this group's merge. Carry: R10-USER-DOCS-VERIFY (item ad-doc-claims-shared)
- The Driving grade's separate day book is stated in the doc, not judged here; no finder harness measures it. Carry: dismissed: unmeasured observation, no harness (item ad-driving-daybook)
- Carries received and answered here: 0, 2, 3, 4, 7, 9, 11, 12, 13, 14. Carries 1, 6, 8 and 10 moved away.
- Hot files: docs/architecture.md, which R10-ARCH-DOCS-DELTA edits after this group, and tests/doc_claims.py (section 1). Serial position: after every non-product `after` group. Seven are not done at the base: DISPATCH-AT-HANDOFF, BODY-CONTRACT, FLY-GH-READ-RETRY, OUTSIDE-INTAKE and FRICTION-OTHER-FAMILY are carries-open, PROCESS-SLIM is in progress, and HOTFIX-GATE-BUSY-DEFER is refuted. Re-read their merged diffs before dispatching (designer step 9).
