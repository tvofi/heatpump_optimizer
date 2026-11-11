R10-ARCH-DOCS, arm B of triage P261: `docs/architecture.md` and `dev/README.md` verified against the tree, every wiring marker resolved, the machinery figure redrawn and pinned. Closes #2395. Part of #201.

Round 3, after `Fix review: blocked ba0ed526cc3b0a4b62a4e05b165710237e3bd123 doc-claim-false`. The method changed, because reading had missed a false sentence twice: a sentence about a whole set (all, each, no, only, a count) is now set beside a command that lists the set, and both that command and the citation checker are in the tree (`dev/audit/harnesses/r10_arch_docs_enumerate.py`, `dev/audit/harnesses/r10_arch_docs_evidence.py`).

The three block items:

1. **`docs/architecture.md`, who reads entity state.** The paragraph no longer offers a list. It says `inputs.InputReader` is not the only reader and gives four examples, marked as examples, each read at its line (E18): `coordinator.py` (price, weather, PV production), `pump_arbiter` (the slot's entity before a write, the power switch), `away.py` (the holiday calendar), `services.py` (refuses an entity with no state). `config_flow.py`, `pump_signals`, `early_cutoff.py` and `setpoint_check.py` are not named and the sentence claims nothing about them; N1 lists every module that names the state machine. Completing the list was the alternative; it lost because a reader that is handed the getter (`quiet_windows`, `modbus_prefill`) appears in no grep for `hass.states`, so a "complete" list would again be a claim no command supports.
2. **`dev/README.md`, `gate-sweep.yml`.** Now what `tools/ci/sweep.py` does (E23): once the completed run's `gate` is green at the live head, the red `gate` of every other CI run at that head is re-run; where no green `gate` covers the newest event, each red `gate` that judged before another run's jobs finished. The second arm is `settle`, which re-runs the triggering run's own gate too, so "the other red `gate` runs" alone would have been a second half-truth.
3. **The two unpinned halves.** `red fixture: a script node that names no script` fails under `!= 1` mutated to `> 1` and under nothing else in the harness's N1 row; `red fixture: a row citing a file whose name is only a part of its node's script name` (`relay.sh` cited under a node named `cloud_relay.sh pass`) fails under `!= a.split()[0]` mutated to `not in a`. Each mutant changes the one comparison. Both killed, by the fixer's harness and by the reviewer's own `ev/rev_mutants_r2.py`, unedited (`## Mutation proof`).

The reviewer's named survivors P3, P7, P8:

- **P3, killed.** A null control now pins the design choice the clause encodes: an entry is an actor, and a store no drawn arrow writes is not one, because reads are not drawn. `a store no arrow reaches is not an entry: the clean fixture with one yields no finding (null control)` fails under P3.
- **P7 and P8, survive, and no honest test in `tests/doc_claims.py` can tell them from the baseline.** Each replaces the call a check makes on the page itself with an empty list. On a clean page the call returns an empty list, so the mutated and unmutated runs are the same run; a fixture cannot reach the call, because the call's input is the page. What can be shown is that the call is the thing that fires, and the harness shows it three ways per call, with the defect planted in the child's source and never in the tree: the mutant alone reads as the baseline; the defect with the call kept fails the live check by name; the defect with the call dropped does not (`## Null control`).

Class repair. Every sentence and arrow the diff adds to the two pages was re-read against the code, the set-claims against N1 to N19. Corrected this round:

- `dev/README.md`:
  - The machinery figure omitted two runs between scripts it draws. N18 lists every executable reference from one drawn script to another; two were actions with no arrow. The relay's carry-fold arm starts `carry_fold.py`, which calls `roster_edit.py` with `--push` (a third writer of the roster branch), and `bus.sh` runs `merge_train.py add` when it posts a merge verdict. Both drawn, each with its row. The page now says the figure is the runs and writes of a normal pass and names what it leaves out: a run that only reads, and the one write on a refusal path.
  - "`tools/ci/ruleset_cutover.py` writes the object whole, reads it back and diffs it": it PUTs the six writable keys and refuses with the difference where a read-back half fails. The figure's node said the owner "rolls back if the read-back differs": the instrument refuses there, and its rollback triggers are three others. Both reworded.
  - "`tests/doc_claims.py` refuses ... [a marker] whose groups are all done": only a marker outside an HTML comment. Said.
  - "A critical-path pull request boards before the record sweep": it skips the sweep before it, and the sweep runs after its merge. Reworded.
  - "skips while that ref is fresh": now the rule, the ref's commit under an hour old, and that the train creates, refreshes and deletes the ref.
  - "Only the orchestrator writes it" (the hold list): what the tree supports is that no script writes it (N9) and that the relay's header says who does. Reworded to those two.
  - "it starts nothing itself" (`cloud_dispatch.py`): it starts git and `bus.sh`. Now "it fires no seat".
  - "Four flow instruments measure a round": no artifact defines the set. Now four are named as four of them.
  - "the other `runs` arrows start a process": re-checked arrow by arrow (E26) and reworded for the new carry-fold arrow.
  - The list of what `tests/doc_claims.py` refuses now includes a script node that names no script.
- `docs/architecture.md`:
  - "`const.py` owns the finite-float conversion": three other functions have "finite" in their name. Now what `finite_float` does, with no ownership claim.
  - "One mixin in `sensor.py`": `sensor.py` defines four mixins. Now "A mixin".
  - "The restart advice is taken once per cycle for the advisor sensor and the envelope grade": N15 shows two call sites, one of them the refit adoption. Now what the insight payload does: takes it once and hands the same advice to the scores.
  - "the one convergence rule the envelope grade and the Health tab's "learned" both read": the two readers are `envelope_score` and the learning view (N15). "The one" and "the Health tab" are gone.

Re-read and left as written, with the row or block behind each: the job graph and trigger list (N2 to N6, N17), the beat sentences (N7, N8), the ledger's kinds (N10, N11), the tick's reads (E27), the opener (E26), the learners' imports (N13), `heat_energy.py` (N14, E28), the parameter writer (N12, E28), the snapshot copies, power, clock, payload, COP and score bullets (E20 to E22, E28), the options pages (N16: in the options flow, three forms take `_page_schema` and four build their own).

Kept on thinner ground: "A seat is started by the orchestrator" rests on `cloud_dispatch.py` firing no seat (it starts only git, `bus.sh`, `ledger.py` and `ref_privacy.py`) and on its help text, E9. "The ruleset requires only `gate`" rests on `dev/governance/roles/nudge.md` section 4, not on a live read; it is carried below. `button.py`'s "while that option is on" is the class docstring's statement (E28); the availability property reads the collector, and the option check behind it was not read.

What landed in earlier rounds, by brief item:

1. **Verification and marker resolution.** Every `[target:]` and `[retired-by:]` marker on the two pages is a statement of the tree. Departures from the planned shape, by causing group: R10-CI-LAYOUT-P2 (a ninth unit `kernel-points`; the prelude's outputs; `ci.yml` is the live umbrella; both rerun workflows gone), R10-ORCH-MACHINERY (`tick_loop.sh`, not `beatd.py`, drives the tick, the relay, the train and the heartbeat; two ledger kinds never landed; no script opens `train-stop`), R10-FLOW-RELAY-HOLD (the hold list is a file no script writes), R10-PLAN-ARTIFACT and the two R10-FLOW-TOOLKIT groups (the plan model is `tools/plan/replan.py`), R10-PARAMS-OWNER, R10-ARCH-SHAPES, R10-SENSOR-PAYLOAD, R10-SCORES.
2. **The machinery figure.** Top-down from one entry, actors in one group and stores in another, every arrow `runs` or `writes` from the actor, one table row per arrow citing the file and quoted text that performs it.
   - Design choice: the citation table lives on the page, not in the test (`fixer.md` step 11: no second copy).
   - Design choice: reads are not drawn, and neither is a run that only reads. The page states both.
   - Design choice: a script that writes through a helper it runs is drawn as the writer. The roster branch is the exception, because three drawn paths share `roster_edit.py`.
   - Design choice: `beatd.py`, `open_driver.py` and `carry_fold.py` stand between two drawn scripts and are not nodes; each row cites the line that starts the helper.
   - Design choice: an entry is an actor; an unwritten store is tolerated (P3 above).
3. **The pins, in `tests/doc_claims.py`.** `machinery_edge_findings` and `due_marker_findings`.
4. **Closure.** The predicate opens every cited file; ten that were INERT are on `INERT_EXCEPT`. This round cites no new file: `cloud_relay.sh` and `bus.sh` were cited already.

Carries, numbered from 1 as `review_packet.py` counts them. Carry 1 and Carry 13 are item 2. Carry 2, Carry 7, Carry 9 and Carry 11 moved to R10-USER-DOCS-VERIFY and are not touched (Carry 14). Carry 3 and Carry 4 are items 2 and 3. Carry 5 is the R10-SCORES line, corrected again this round. Carry 6 and Carry 8: arm A's checker is present and green at this head and was not rebuilt. Carry 10 is the ledger-kind departure. Carry 12: user-doc markers are left. Carry 14: no user page is edited. Carry 15: done at this merge base; the re-read after the last product merge is R10-ARCH-DOCS-DELTA's.

Outside the roster group's `files`: `tests/doc_claims.py`, `tests/closure.py`, `tests/closures.json`, and three harnesses under `dev/audit/harnesses/` (`fixer.md` step 18).

Alternatives not taken:
- Restructuring the two live checks so a dropped call fails. Any shape that does it moves the call into a helper, and the same mutant then applies to the helper's one call: the survivor moves, it does not die.
- Drawing every read-only run. The tick alone imports `merge_train.py` for its classifier and runs `bus.sh` for a listing; the figure would stop showing what moves.
- Keeping the grouped nodes and adding a "started by" column; drawing the launchers as nodes; deriving an arrow's direction from which script names which. Each as in round 2: the first carries a claim no check reads, the second pulls two instruments out of INERT into a check this group does not own, the third is satisfied by a comment in either direction.

## Head

bb2bb6307109f4da387aba7cd3e4b910f801c769 (merge base 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444; origin/main a7628041dc at 2026-11-11T07:25:48Z; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in).

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_arch_docs_mutants.py` at the head. It replaces one predicate's text, runs `tests/doc_claims.py` on the mutated source in a child, and prints the checks that fail. Nothing is written to the tree.

The rows this round adds, each mutating one comparison:

- N1, `len(_FILE.findall(n)) != 1]` to `> 1]`: FAIL `red fixture: a script node that names no script is a finding`
- its other half, `!= 1]` to `< 1]`: FAIL `red fixture: a node grouping two scripts is a finding`
- N4, `!= a.split()[0]:` to `not in a:`: FAIL `red fixture: a row citing a file whose name is only a part of its node's script name is a finding`
- P3, the `nodes[i][1] != "store" and` clause removed: FAIL `a store no arrow reaches is not an entry: the clean fixture with one yields no finding (null control)`

Failing test first: at ba0ed526cc the reviewer's `ev/rev_mutants_r2.txt` reads `SURVIVED N1` and `SURVIVED N4`, and its `ev/rev_mutants_r1_at_head.txt` reads `SURVIVED P3`; the three fixtures are the only change to `tests/doc_claims.py` since.

The rows of earlier rounds, re-run at this head:

- due marker: FAIL `red fixture: a due wiring marker is refused, and a not-yet-due one is not (null control)`
- verb: FAIL `red fixture: a verb that is not runs or writes is a finding`
- store as actor: FAIL `red fixture: a store drawn as the actor (is read by) is a finding`
- writes ends at a store: FAIL `red fixture: writes ending at an actor is a finding`
- arrow with no row: FAIL `red fixture: one arrow reversed is a finding`
- row with no arrow: FAIL `red fixture: a row with no arrow is a finding`
- quoted text in the cited file: FAIL `red fixture: a cited line the code no longer holds is a finding`
- cited file is the actor's (the whole test off): FAIL the two round-2 fixtures and the N4 fixture
- one script per node (the whole test off): FAIL the grouping fixture and the N1 fixture
- the entry is a seat: FAIL `red fixture: a single entry that is a script, not a seat is a finding`
- one entry: FAIL `red fixture: an actor nothing starts, a second entry is a finding` and the seat fixture
- node names unique: FAIL `red fixture: two nodes of one name is a finding`
- cited file tracked, and one arrow per line: the run dies (`TypeError`, `AttributeError`) on the fixture that plants the case. Killed by a crash, not by a named check.

The reviewer's own harnesses, fetched from `refs/heads/probe/rev-3430-6a421a63` and run unedited against a detached worktree of this head (`python3 ev/rev_mutants_r1.py <worktree>`, `python3 ev/rev_mutants_r2.py <worktree>`):

- `ev/rev_mutants_r1.py`: `baseline: 0 FAIL line(s) []`, `RESULT rev_mutants=21`, `RESULT rev_survivors=2`. The two survivors:
  - `SURVIVED P7 due check call dropped: -`
  - `SURVIVED P8 live machinery check dropped: -`
  - and the two named mutants it now kills:
  - `killed   P3 entry excludes stores: a store no arrow reaches is not an entry: the clean fixture with one yields no finding (null control)`
  - `killed   P4 entry must be a seat: red fixture: a single entry that is a script, not a seat is a finding`
- `ev/rev_mutants_r2.py`: `null (baseline): 0 FAIL line(s) []`, `RESULT rev2_mutants=10`, `RESULT rev2_survivors=0`. Its N1 and N4:
  - `killed   N1 one-script rule accepts a script node naming no file: red fixture: a script node that names no script is a finding`
  - `killed   N4 actor-file rule: substring of the first line: red fixture: a row citing a file whose name is only a part of its node's script name is a finding`
  - `killed   N10 page: seats node made a script shape (entry stays, a seat row then owes the one-script rule): every arrow is cited, every citation holds in the tree, and the figure has one entry ;; reversing any one arrow of the page`

## Null control

- The fixer's harness on the unmutated file prints `baseline: 0 FAIL line(s)`; the reviewer's two print `baseline: 0 FAIL line(s) []` and `null (baseline): 0 FAIL line(s) []`.
- P7 and P8, the harness's `LIVE` rows. Quoted from its output at this head:

  - `shown    the due-marker call on the pages (reviewer's P7): alone 0 FAIL line(s); planted defect, call kept: no wiring marker names only done groups: each is resolved into a statement of the tree (#2395); planted defect, call dropped: -`
  - `shown    the machinery call on the page (reviewer's P8): alone 0 FAIL line(s); planted defect, call kept: every arrow is cited, every citation holds in the tree, and the figure has one entry; reversing any one arrow of the page's figure is a finding (anchor: the figure has arrows); planted defect, call dropped: reversing any one arrow of the page's figure is a finding (anchor: the figure has arrows)`

  Read: alone, each mutant prints what the baseline prints. With a due marker appended to the text the census reads, or one arrow of the figure reversed in the text the machinery check reads, the kept call fails the live check by name. With the same defect and the call dropped, that name is absent. For P8 the reversal anchor still fails with the call dropped, because it calls the predicate itself; it cannot fail on a clean page either.
- The evidence checker's own control: a body of one row, `VERSION:1` with a text the line does not hold, prints `MISS VERSION:1 ...`, `RESULT miss=1` and exits 1. On its first run over this round's new rows it read `miss=5`: four `config_flow.py` rows were two lines off and one `merge_train.py` row quoted a comment loosely. The rows were corrected, not the checker.
- `machinery_edge_findings` on the clean fixture returns nothing, and on the clean fixture with an unwritten store returns nothing.
- The owner's control on the page's own figure: `reversing any one arrow of the page's figure is a finding`, over all 42 arrows (N19 reads 42 arrows and 42 rows; the gate check requires the two sets equal, not the counts).
- Every zero among N1 to N19 carries a control that is not zero, named in its block: `replan.py` for the beat greps (N8), `postmerge-owed` for the `train-stop` opener (N11), `accuracy.py` for the `homeassistant` import count (N14).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at the head: `ALL 324 checks PASSED`. Three more than round 2: the N1 and N4 fixtures and the P3 control.
- Mutants: the fixer's harness prints `RESULT baseline_fails=0`, `RESULT mutants=18`, `RESULT killed=18`, `RESULT live_calls=2`, `RESULT live_calls_shown=2`. Rule: one row per predicate test of the two functions, one per half of a two-sided comparison, and one per call a check makes on the page itself; a row whose text is not in the file exactly once is an error.
- Marker resolver: `python3 tests/doc_claims.py --markers` prints `0 of 0 marker(s) due`, exit 0.
- Mermaid: `NODE_PATH=$(npm root -g) node dev/audit/harnesses/r10_mermaid_parse.mjs tools/site dev/README.md docs/architecture.md`, after `npm ci` in `tools/site`, printed `mermaid 12.3.0 parse+render in Chromium: 5 block(s), 0 failure(s)`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL`, reason `tests/closure.py changes the gate itself`. Run locally: `tests/doc_claims.py`, `tests/entities.py` (`ALL 2707 ENTITY CHECKS PASSED`), `tests/harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`), `tests/structure.py`. The rest is CI's.
- Closure: `python3 tools/pr/ci_predict.py --base origin/main --apply-inert` printed two `APPLIED inert_reads tests/harness_headers.py` lines, one per new harness, and at the head `CI PREDICT: no closures, fast, governance or instrument red predicted against 63bcdcaad827 (a data-file read is not seen)`. No closure was re-derived this round: the two rows added to the page cite files already on `INERT_EXCEPT`.
- Seams (`fixer.md` step 8). The class is "a sentence or an arrow the tree contradicts", on the two pages.
  - Arrows. Enumerator: N18, every executable reference (a path, an import, a module call; comment lines dropped) from one of the fifteen drawn script files to another or to a helper. A pair the figure draws is closed by its row: `cloud_dispatch.py` to `bus.sh`; `tick_loop.sh` to the relay, the tick, the train and the heartbeat; the relay to `bus.sh` and, new, to `carry_fold.py` (830); `bus.sh` to `merge_train.py` (482, new); `beat_jobs.py` to its four; `state_docs.py` to `plan_page.py`; `roster_queue.py` and `roster_sync.py` to `roster_edit.py`; `merge_train.py` to `postmerge.py`. Every line of a pair the figure does not draw, by disposition:
    - a run or import that only reads, which the page names as left out: the relay to `merge_train.py classify` (269); `bus.sh` to `merge_train.py classify` (610) and to `cloud_relay.sh held` (479); the tick's import of `merge_train.py` for its classifier (249) and its `bus.sh` listing (336); `plan_page.py`'s import of `replan.py` (76) for `check_plan` and `stale_reason` (750, 751);
    - text a script prints or writes into a prompt, no run: `cloud_dispatch.py` to `merge_train.py` (253); `bus.sh` to `roster_edit.py` (242); the tick to `state_docs.py` (2075); `roster_edit.py` to `roster_queue.py` (1417); `plan_page.py` to `replan.py` (4, 12, 692); `state_docs.py` to `replan.py` (39);
    - inside the script's self-test (`cloud_dispatch.py` from 1075 and its `_group_checks`, `bus.sh` from 1011, `plan_page.py` from 770, the tick from 2720, `state_docs.py`'s `plan_page_arms`): `cloud_dispatch.py` 928, 1146; `bus.sh` 2096; the tick 4052, 4073, 4304, 4305; `state_docs.py` 672, 688, 689; `plan_page.py` 889 and every later line;
    - not a reference: `plan_page.py` 208 and 231 are a variable named `open_pr`;
    - the roster-sync step no caller enters: `state_docs.py` 93, 376 (N8, and the page's "No beat job runs `tools/audit/seat/roster_sync.py`").
    - Outside N18, the one ledger write on a refusal path, named on the page: `cloud_dispatch.py` 585.
    - The enumerator's limit: it matches a script by name, so a run through a variable holding another script's path is not seen. `open_driver.py` and `carry_fold.py` are among its targets for that reason.
  - Sentences. Enumerator: the `+` lines of `git diff $(git merge-base origin/main HEAD)...HEAD -- dev/README.md docs/architecture.md`. A sentence about a whole set is under its N block below; any other factual sentence is under an E number. No instrument checks a prose sentence against code: the E rows are citations, machine-checked for position only, and the reading behind them is this seat's.
- Set claims. `python3 dev/audit/harnesses/r10_arch_docs_enumerate.py` prints blocks N1 to N19; each sentence, its block, and what the block holds:
  - "It is not the only reader of entity state": N1 lists eleven module files naming the state machine in code, `inputs.py` one of them. Would be one file were it false.
  - "starts on a pull request, a review, a push to `main`, a merge group or a manual dispatch": N2 `events: ['merge_group', 'pull_request', 'pull_request_review', 'push', 'workflow_dispatch']`.
  - "each unit runs when the prelude's work set names it": N2, `workset-gated True` on each of the eight units and on `pr-contract`.
  - "`ci.yml` carries three more jobs: `cancel-superseded` and `refresh` need no other job, and `sweep-self` needs `gate`": N2, fourteen jobs: `prelude`, eight units, `pr-contract`, `gate`, and those three with `needs None`, `needs None`, `needs gate`.
  - "the figure names five of the prelude's outputs": N2 lists ten, the five among them.
  - Each trigger bullet of the workflow list, and "one of its three path filters": N3, one line per file, and N17.
  - "Every unit the umbrella calls is a `workflow_call` file, so none of them starts on a pull-request event of its own": N4 prints no file and `units called: 9`. "the one pull-request trigger outside the umbrella": N5 prints `ci.yml` and `dependabot-automerge.yml`.
  - `ls .github/workflows/` against the page: N6 prints no file.
  - "every job there is a `tools/audit/seat/beat_jobs.py` call" and "three of its jobs ... `roster-drain`, `plan-beat` and `opener`": N7, one script in the set, fourteen job names, the three among them.
  - "No beat job runs the relay, the tick, the train or the heartbeat" and "No beat job runs `roster_sync.py`": N8, 0 in the table for both patterns; in `beat_jobs.py` one line for the first, a comment (line 139), and 0 for the second. Control `replan.py`: 2.
  - "No script writes it" (the hold list): N9, every redirect into the file is at `bus.sh` 1362 to 1370 or `cloud_relay.sh` 1252 and after, inside each script's self-test (`bus.sh`'s and the relay's production code end before those lines; the reads are at `cloud_relay.sh` 481 to 610 and `bus.sh` 479).
  - "events, opened and closed" followed by six kinds: N10 prints exactly those six as `event`. "derived ... among them": N10, 25 derived kinds, the five named among them.
  - "no script opens `train-stop`": N11, 0; control `postmerge-owed`, 1.
  - "The thermal parameters have one writer": N12, the two lines of `_publish_params` and the facade's class attribute.
  - "three still import `homeassistant`", "never call the coordinator", "`dhw_learning` and `snapshots` reach persistence through `store.py`": N13, over the nine modules of the page's learners node.
  - "It imports nothing from Home Assistant; the coordinator reads the entities and calls in": N14, 0 lines of `heat_energy.py` name `homeassistant` (control `accuracy.py`: 1), and `coordinator.py` is its one importer.
  - "takes the restart advice once" and the two readers of `house_loss_converged`: N15, four lines: 1416 the refit adoption, 10711 the insight payload, 3265 `envelope_score`, 7940 the learning view.
  - "The setup overview, the factory reset, quick setup and the pre-fill preview build their own forms": N16. The options flow's class starts at 3225; the forms after it are 3366, 3382, 3806 (`_page_schema`), 3457, 3547, 3945, and the overview's form at 2510, which the options flow shows from 3449.
- Evidence. Each row is `path:line` and text that line holds at the head. `python3 dev/audit/harnesses/r10_arch_docs_evidence.py <this body>` printed `RESULT rows=296`, `RESULT hold=296`, `RESULT miss=0`. Line numbers are this head's; a later tree is read by the quoted text.

- E1. The umbrella's events (figure node `ev`, the `ci.yml` bullet):
  - `.github/workflows/ci.yml:35` `pull_request:`
  - `.github/workflows/ci.yml:38` `pull_request_review:`
  - `.github/workflows/ci.yml:41` `branches: [main]`
  - `.github/workflows/ci.yml:43` `merge_group:`
  - `.github/workflows/ci.yml:45` `workflow_dispatch:`
- E2. The prelude's five named outputs (figure node `pre`):
  - `.github/workflows/ci.yml:83` `kind: ${{ steps.derive.outputs.kind }}`
  - `.github/workflows/ci.yml:84` `pr: ${{ steps.derive.outputs.pr }}`
  - `.github/workflows/ci.yml:85` `base: ${{ steps.derive.outputs.base }}`
  - `.github/workflows/ci.yml:86` `head: ${{ steps.derive.outputs.head }}`
  - `.github/workflows/ci.yml:89` `workset: ${{ steps.derive.outputs.workset }}`
- E3. Job-graph arrows: each unit needs the prelude and runs on its work set; `pr-contract` needs the prelude and the eight; `gate` needs the prelude and `pr-contract`; `sweep-self` needs `gate`; nine `uses:` lines:
  - `.github/workflows/ci.yml:182` `needs: prelude`
  - `.github/workflows/ci.yml:183` `if: contains(format(' {0} ', needs.prelude.outputs.workset), ' tests ')`
  - `.github/workflows/ci.yml:184` `uses: ./.github/workflows/tests.yml`
  - `.github/workflows/ci.yml:204` `needs: prelude`
  - `.github/workflows/ci.yml:206` `uses: ./.github/workflows/codeql.yml`
  - `.github/workflows/ci.yml:213` `needs: prelude`
  - `.github/workflows/ci.yml:215` `uses: ./.github/workflows/governance.yml`
  - `.github/workflows/ci.yml:225` `needs: prelude`
  - `.github/workflows/ci.yml:227` `uses: ./.github/workflows/hassfest.yml`
  - `.github/workflows/ci.yml:231` `needs: prelude`
  - `.github/workflows/ci.yml:233` `uses: ./.github/workflows/validate.yml`
  - `.github/workflows/ci.yml:237` `needs: prelude`
  - `.github/workflows/ci.yml:239` `uses: ./.github/workflows/kernel-points.yml`
  - `.github/workflows/ci.yml:247` `needs: prelude`
  - `.github/workflows/ci.yml:249` `uses: ./.github/workflows/arch-score.yml`
  - `.github/workflows/ci.yml:258` `needs: prelude`
  - `.github/workflows/ci.yml:260` `uses: ./.github/workflows/budget-raise-gate.yml`
  - `.github/workflows/ci.yml:271` `needs: [prelude, tests, codeql, governance, hassfest, validate, kernel-points, arch-score, budget-raise-gate]`
  - `.github/workflows/ci.yml:273` `uses: ./.github/workflows/pr-contract.yml`
  - `.github/workflows/ci.yml:319` `needs: [prelude, pr-contract]`
  - `.github/workflows/ci.yml:366` `needs: gate`
- E4. The prelude script, the ruleset tool, the ruleset rule, the two traps:
  - `tools/ci/prelude.py:360` `out = {"kind": kind, "pr": pr, "base": base, "head": ctx["head"],`
  - `tools/ci/ruleset_cutover.py:286` `rc, out = gh(["-X", "PUT", RULESET, "--input", "-"], json.dumps(want))`
  - `tools/ci/ruleset_cutover.py:298` `READBACK half 1 FAILED`
  - `tools/ci/ruleset_cutover.py:309` `def rollback(gh, path: str) -> int:`
  - `dev/governance/roles/nudge.md:57` `Read that ruleset every turn.`
  - `dev/governance/roles/nudge.md:57` `` `gate` is the one required check ``
  - `dev/governance/roles/orchestrator.md:228` `Absent is not green.`
  - `dev/governance/rules/claim-files.md:24` `` a `DIRTY` one does not go ``
- E5. Each workflow file's trigger, as the list states it:
  - `.github/workflows/dependabot-automerge.yml:39` `pull_request_target:`
  - `.github/workflows/dependency-graph.yml:26` `push:`
  - `.github/workflows/dependency-graph.yml:29` `paths:`
  - `.github/workflows/dependency-graph.yml:33` `workflow_dispatch:`
  - `.github/workflows/dependency-graph.yml:34` `schedule:`
  - `.github/workflows/gate-sweep.yml:17` `workflow_run:`
  - `.github/workflows/gate-sweep.yml:18` `workflows: ["CI"]`
  - `.github/workflows/gate-sweep.yml:42` `Re-judge the older gates at this head`
  - `.github/workflows/gate-sweep.yml:49` `tools/ci/gate.py --sweep`
  - `.github/workflows/governance.yml:33` `workflow_call:`
  - `.github/workflows/governance.yml:54` `schedule:`
  - `.github/workflows/kernel-points.yml:30` `workflow_call:`
  - `.github/workflows/kernel-points.yml:41` `workflow_dispatch:`
  - `.github/workflows/marketplace.yml:14` `schedule:`
  - `.github/workflows/marketplace.yml:16` `workflow_dispatch:`
  - `.github/workflows/marketplace.yml:27` `uses: ./.github/workflows/hassfest.yml`
  - `.github/workflows/marketplace.yml:31` `uses: ./.github/workflows/validate.yml`
  - `.github/workflows/merge-main.yml:31` `branches: [main]`
  - `.github/workflows/merge-main.yml:32` `workflow_dispatch:`
  - `.github/workflows/nightly.yml:30` `- main`
  - `.github/workflows/nightly.yml:31` `workflow_dispatch:`
  - `.github/workflows/nightly.yml:41` `schedule:`
  - `.github/workflows/nightly.yml:1119` `say skip-train-hold; exit 0`
  - `.github/workflows/pages.yml:41` `- "v*"`
  - `.github/workflows/pages.yml:42` `workflow_dispatch:`
  - `.github/workflows/release.yml:15` `- "v*"`
  - `.github/workflows/release.yml:16` `workflow_dispatch:`
  - `.github/workflows/arch-score.yml:26` `workflow_call:`
  - `.github/workflows/budget-raise-gate.yml:32` `workflow_call:`
  - `.github/workflows/codeql.yml:87` `workflow_call:`
  - `.github/workflows/hassfest.yml:7` `workflow_call:`
  - `.github/workflows/pr-contract.yml:19` `workflow_call:`
  - `.github/workflows/tests.yml:108` `workflow_call:`
  - `.github/workflows/validate.yml:7` `workflow_call:`
- E6. Ledger kinds: the derived five and the six events are keys of `KINDS`; a derived kind is computed, an event is opened and closed:
  - `tools/audit/seat/ledger.py:106` `"handoff-no-pr": "derived", "handoff-update": "derived", "probe-ref": "derived",`
  - `tools/audit/seat/ledger.py:108` `"review-owed": "derived", "record-owed": "derived",`
  - `tools/audit/seat/ledger.py:113` `"reviewer-fire": "event", "verdict-unposted": "event", "approve-held-runs": "event",`
  - `tools/audit/seat/ledger.py:114` `"dispatch": "event", "train-stop": "event", "postmerge-owed": "event",`
  - `tools/audit/seat/ledger.py:538` `handoff-no-pr`
  - `tools/audit/seat/ledger.py:712` `def record_owed(`
  - `tools/audit/seat/bus.sh:706` `close reviewer-fire "$pr" "$h"`
- E7. `bus.sh`: nonce refusal, the four ref families it writes, the poster, the dispatch record:
  - `tools/audit/seat/bus.sh:199` `unknown nonce %s: no dispatch in %s minted it`
  - `tools/audit/seat/bus.sh:316` `append_commit review "$pr" "$tree"`
  - `tools/audit/seat/bus.sh:811` `append_commit verdict "$pr" "$tree"`
  - `tools/audit/seat/bus.sh:2138` `append_commit design "$topic" "$tree"`
  - `tools/audit/seat/bus.sh:2152` `append_commit design-verdict "$topic" "$tree"`
  - `tools/audit/seat/bus.sh:363` `"$c:refs/heads/$fam/$pr"`
  - `tools/audit/seat/bus.sh:454` `"$POSTER" "$REPO" "$pr" "$body"`
  - `tools/audit/seat/bus.sh:701` `>> "$S/dispatched"`
  - `tools/audit/seat/bus.sh:158` `POSTER=$ROOT/tools/pr/app_comment.sh`
- E8. The relay: hold list, verdict relay, updater, ledger opens, probe refs, the level file, arm order:
  - `tools/audit/seat/cloud_relay.sh:115` `only the orchestrator writes or edits it`
  - `tools/audit/seat/cloud_relay.sh:114` `lists PR numbers, one per line`
  - `tools/audit/seat/cloud_relay.sh:481` `cloud-handoff-hold`
  - `tools/audit/seat/cloud_relay.sh:610` `cloud_relay: HELD #$pr $hs`
  - `tools/audit/seat/cloud_relay.sh:199` `bash "$HERE/bus.sh" push-verdict`
  - `tools/audit/seat/cloud_relay.sh:305` `ledger_open verdict-unposted "$pr" "$head" "$first"`
  - `tools/audit/seat/cloud_relay.sh:670` `upd=(bash "$why/update_pr.sh")`
  - `tools/audit/seat/cloud_relay.sh:705` `ledger_open reviewer-fire "$pr" "$nh" "nonce=$nonce"`
  - `tools/audit/seat/cloud_relay.sh:340` `refs/heads/probe/rev-*`
  - `tools/audit/seat/cloud_relay.sh:569` `level_set handoff-no-pr`
  - `tools/audit/seat/cloud_relay.sh:860` `handoff_arm; carry_fold_arm; probe_arm;`
- E9. Dispatch and the seats' pushes:
  - `tools/audit/seat/cloud_dispatch.py:2` `Render the cloud-runner trigger payload for one seat`
  - `tools/audit/seat/cloud_dispatch.py:1291` `fire the seat with a pointer to it`
  - `tools/audit/seat/cloud_dispatch.py:457` `_git(repo_dir, "push", "-q", "origin", f"{commit}:refs/heads/{ref}")`
  - `tools/audit/seat/cloud_dispatch.py:604` `str(HERE / "bus.sh"), "dispatch"`
  - `tools/audit/seat/cloud_dispatch.py:294` `refs/heads/probe/{ref_key}-{nonce.strip()[:8]}`
  - `tools/audit/seat/cloud_dispatch.py:322` `tools/audit/seat/bus.sh push-design {topic} <design.md>`
  - `tools/audit/seat/cloud_dispatch.py:1332` `print(out)`
  - `tools/audit/seat/body_push.sh:238` `git push -q origin "$C:refs/heads/$REF"`
  - `dev/governance/roles/fix-review.md:7` `tools/audit/seat/bus.sh push-verdict`
- E10. The orchestrator's rows (contract and guide citations):
  - `tools/audit/seat/instruments/tick_loop.sh.md:18` `in place of a seat looping the tick`
  - `tools/audit/seat/instruments/beatd.py.md:18` `until a supervisor unit is applied it runs under`
  - `tools/audit/seat/instruments/beatd.py.md:19` `` `daemonize.py` ``
  - `dev/governance/roles/nudge.md:52` `tools/audit/seat/merge_train.py run`
  - `tools/audit/seat/instruments/heartbeat.sh.md:12` `the owner schedules a cloud task`
  - `tools/audit/seat/instruments/heartbeat.sh.md:14` `schedule is owner-side, not in the tree`
- E11. `tick_loop.sh`: relay pass, tick, board file, sweep under `--sweep`, heartbeat, in file order:
  - `tools/audit/seat/tick_loop.sh:131` `bash "$relay" pass --confirm`
  - `tools/audit/seat/tick_loop.sh:161` `relay_start "$out.relay" "$relay"`
  - `tools/audit/seat/tick_loop.sh:169` `python3 "$HERE/orchestrator_tick.py"`
  - `tools/audit/seat/tick_loop.sh:170` `mv -f "$tmp" "$out"`
  - `tools/audit/seat/tick_loop.sh:173` `[ -z "$sweep" ] || [ -n "$stale" ] || sweep_pass "$out"`
  - `tools/audit/seat/tick_loop.sh:149` `python3 "$HERE/merge_train.py" sweep`
  - `tools/audit/seat/tick_loop.sh:175` `heartbeat.sh}" --once`
- E12. The beat: table refusal, job start, the four drawn job commands:
  - `tools/audit/seat/beatd.py:124` `raise Refuse(f"job table {path} unreadable: {e}")`
  - `tools/audit/seat/beatd.py:336` `subprocess.Popen(self.argv(job)`
  - `tools/audit/seat/beatd.py:527` `beatd.jobs.json`
  - `tools/audit/seat/beat_jobs.py:387` `"tools/audit/seat/roster_queue.py", "run"`
  - `tools/audit/seat/beat_jobs.py:418` `"tools/plan/replan.py", "--out"`
  - `tools/audit/seat/beat_jobs.py:424` `"tools/audit/seat/state_docs.py", "--push", "--mirror", mirror, "--plan", plan`
  - `tools/audit/seat/beat_jobs.py:542` `"tools/audit/seat/open_driver.py", "--board"`
- E13. State documents, plan page, the two ref names, and the roster-sync step the beat's command line never enters:
  - `tools/audit/seat/state_docs.py:495` `str(SEAT / "plan_page.py")`
  - `tools/audit/seat/state_docs.py:279` `f"{commit}:refs/heads/{state_ref}"`
  - `tools/audit/seat/state_docs.py:118` `f"handoff/audit-r{round_n}-plan"`
  - `tools/audit/seat/state_docs.py:40` `` commit as `PLAN-TABLE.md` ``
  - `tools/audit/seat/state_docs.py:63` `` `beat --apply` runs the roster-sync step (`roster_sync.py`) ``
  - `tools/audit/seat/roster_lib.py:266` `f"handoff/audit-r{roster_round(path)}-roster"`
- E14. The roster branch's writers:
  - `tools/audit/seat/roster_queue.py:390` `"--lint-cwd", a.lint_clone, "--push"]`
  - `tools/audit/seat/roster_queue.py:388` `cmd = [py, editor, op, g]`
  - `tools/audit/seat/roster_edit.py:1192` `refspec = f"{head}:refs/heads/{branch}"`
  - `tools/audit/seat/roster_sync.py:713` `roster_edit.write_roster(`
- E15. The opener:
  - `tools/audit/seat/open_driver.py:155` `self.opener = HERE / "open_pr.sh"`
  - `tools/audit/seat/open_pr.sh:125` `bash "$_push"`
  - `tools/audit/seat/open_pr.sh:121` `_push=tools/pr/app_push.sh`
  - `tools/pr/app_push.sh:632` `-X POST`
- E16. The train, its hold ref, postmerge, the critical path, the sweep and `train-stop`:
  - `tools/audit/seat/merge_train.py:1766` `"--merge", "--match-head-commit", h`
  - `tools/audit/seat/merge_train.py:2923` `git/refs/heads/train-hold`
  - `tools/audit/seat/merge_train.py:2769` `tool("postmerge"), str(pr), "--repo"`
  - `tools/audit/seat/merge_train.py:1839` `does not carry to head`
  - `tools/audit/seat/merge_train.py:2484` `critical-path entries jump the record`
  - `tools/audit/seat/merge_train.py:4188` `if ob[0] == "train-stop"`
  - `tools/audit/seat/merge_train.py:4194` `SWEEP HELD: the ledger holds an open train-stop`
  - `tools/audit/seat/merge_pr.sh:304` `python3 -I tools/audit/seat/postmerge.py`
  - `tools/audit/seat/postmerge.py:47` `/roster_sync.py", "--repo", repo, "--apply"`
  - `tools/audit/seat/postmerge.py:48` `/state_docs.py", "--repo", repo, "--push"`
  - `tools/audit/seat/postmerge.py:95` `"open", "postmerge-owed"`
- E17. Heartbeat, the tick's ledger read, the four flow instruments:
  - `tools/audit/seat/heartbeat.sh:35` `"$c:refs/heads/$REF"`
  - `tools/audit/seat/heartbeat.sh:46` `HEARTBEAT STALE:`
  - `tools/audit/seat/orchestrator_tick.py:761` `lg.record_owed(prs, now)`
  - `tools/audit/seat/flow_metrics.py:2` `A round's flow, from git alone`
  - `tools/audit/seat/ci_critpath.py:2` `One workflow run's critical path`
  - `tools/audit/seat/review_strength.py:2` `Review strength from the verdict bus`
  - `tools/audit/seat/gantt_drift.py:2` `Compare the plan's gantt against the real state`
- E19. `docs/architecture.md`: the learners' imports, and the reset-heat-loss button:
  - `custom_components/heatpump_optimizer/accuracy.py:32` `from homeassistant.util import dt as dt_util`
  - `custom_components/heatpump_optimizer/defrost.py:71` `from homeassistant.util import dt as dt_util`
  - `custom_components/heatpump_optimizer/dhw_learning.py:27` `from homeassistant.core import HomeAssistant`
  - `custom_components/heatpump_optimizer/dhw_learning.py:28` `from .store import QuarantiningStore, load_mapping`
  - `custom_components/heatpump_optimizer/snapshots.py:41` `from .store import admitted`
  - `custom_components/heatpump_optimizer/button.py:178` `class ResetHeatLossButton(_OptimizerButtonBase):`
- E20. `docs/architecture.md`, One owner per concern: parameters and snapshots:
  - `custom_components/heatpump_optimizer/coordinator.py:2606` `@dataclass(frozen=True)`
  - `custom_components/heatpump_optimizer/coordinator.py:2607` `class CoordinatorContext:`
  - `custom_components/heatpump_optimizer/coordinator.py:2754` `params = replace(coord._thermal_params, **fields)`
  - `custom_components/heatpump_optimizer/coordinator.py:2755` `coord._thermal_params = params`
  - `custom_components/heatpump_optimizer/coordinator.py:2756` `coord._thermal_model.params = params`
  - `custom_components/heatpump_optimizer/thermal_model.py:253` `self.clamp()`
  - `custom_components/heatpump_optimizer/coordinator.py:6216` `copy.deepcopy(ctx._thermal_params),`
  - `custom_components/heatpump_optimizer/coordinator.py:6223` `copy.deepcopy(ctx._current_state),`
  - `custom_components/heatpump_optimizer/coordinator.py:6199` `copy.deepcopy(ctx._opt_config),`
  - `custom_components/heatpump_optimizer/coordinator.py:2190` `house = replace(live)`
  - `custom_components/heatpump_optimizer/coordinator.py:10634` `state = replace(ctx._current_state)`
- E21. One owner per concern: shapes, payload, heat counter, COP state:
  - `custom_components/heatpump_optimizer/inputs.py:326` `def normalize_power_kw(value: float, unit: Any) -> float | None:`
  - `custom_components/heatpump_optimizer/inputs.py:391` `def state_power_kw(`
  - `custom_components/heatpump_optimizer/const.py:1393` `def finite_float(`
  - `custom_components/heatpump_optimizer/quiet_windows.py:294` `def wall_clock(hour: float) -> tuple[int, int]:`
  - `custom_components/heatpump_optimizer/dhw_schedule.py:451` `def format_clock(hour: float) -> str:`
  - `custom_components/heatpump_optimizer/entity.py:105` `def zone_setpoint_attributes(`
  - `custom_components/heatpump_optimizer/entity.py:125` `def payload_number(`
  - `custom_components/heatpump_optimizer/entity.py:147` `def _finite(value: Any) -> Any:`
  - `custom_components/heatpump_optimizer/sensor.py:346` `class _PayloadNumberMixin(_SensorMixinBase):`
  - `custom_components/heatpump_optimizer/heat_energy.py:222` `def attribution(`
  - `custom_components/heatpump_optimizer/heat_energy.py:1` `The heat a delivered-heat counter measured, and which duty it served`
  - `custom_components/heatpump_optimizer/accuracy.py:829` `COP_NOT_MEASURABLE = "not_measurable"`
  - `custom_components/heatpump_optimizer/accuracy.py:833` `def cop_observability(`
- E22. One owner per concern: scores, learner progress, options pages:
  - `custom_components/heatpump_optimizer/coordinator.py:3323` `def compose_scores(`
  - `custom_components/heatpump_optimizer/coordinator.py:1694` `def house_loss_converged(samples: int) -> bool:`
  - `custom_components/heatpump_optimizer/coordinator.py:3265` `if not house_loss_converged(samples):`
  - `custom_components/heatpump_optimizer/coordinator.py:7940` `"house_heat_loss_learned": house_loss_converged(`
  - `custom_components/heatpump_optimizer/coordinator.py:10711` `advice = model_restart_advice(self)`
  - `custom_components/heatpump_optimizer/coordinator.py:10714` `"scores": self._scores_view(advice),`
  - `custom_components/heatpump_optimizer/learner_progress.py:1` `How far each thermal learner has come`
  - `custom_components/heatpump_optimizer/config_flow.py:1643` `_OPTION_FIELDS: Final[tuple[_F, ...]] = (`
  - `custom_components/heatpump_optimizer/config_flow.py:2048` `def _page_schema(`
  - `custom_components/heatpump_optimizer/config_flow.py:3457` `data_schema=_FACTORY_RESET_SCHEMA`
  - `custom_components/heatpump_optimizer/config_flow.py:3449` `_setup_overview_form(self, self._current)`
- E18. `docs/architecture.md`: readers of entity state, the four examples, sentence by sentence (`inputs.InputReader` reads; `coordinator.py` reads price, weather, PV production; `pump_arbiter` reads the slot's entity before it writes and the power switch; `away.py` the holiday calendar; `services.py` refuses an entity with no state):
  - `custom_components/heatpump_optimizer/inputs.py:933` `state = self.hass.states.get(entity_id)`
  - `custom_components/heatpump_optimizer/coordinator.py:3387` `.price_entity`
  - `custom_components/heatpump_optimizer/coordinator.py:3390` `return hass.states.get(entity_id)`
  - `custom_components/heatpump_optimizer/coordinator.py:7047` `self.hass.states.get(weather_entity)`
  - `custom_components/heatpump_optimizer/coordinator.py:9785` `entity_id = config.production_entity`
  - `custom_components/heatpump_optimizer/coordinator.py:9788` `self.hass.states.get(entity_id)`
  - `custom_components/heatpump_optimizer/pump_arbiter.py:1108` `async def _write(`
  - `custom_components/heatpump_optimizer/pump_arbiter.py:1110` `entity = _slot_entity(inp.config, slot)`
  - `custom_components/heatpump_optimizer/pump_arbiter.py:1111` `state = inp.hass.states.get(entity) if entity else None`
  - `custom_components/heatpump_optimizer/pump_arbiter.py:1422` `.heat_pump_switch_entity`
  - `custom_components/heatpump_optimizer/pump_arbiter.py:1423` `power = inp.hass.states.get(entity) if entity else None`
  - `custom_components/heatpump_optimizer/away.py:609` `_holiday_days(states.get(entity_id), now)`
  - `custom_components/heatpump_optimizer/services.py:834` `if hass.states.get(raw) is None:`
  - `custom_components/heatpump_optimizer/services.py:835` `raise ServiceValidationError(`
  - `custom_components/heatpump_optimizer/services.py:838` `translation_key="assign_entity_missing"`
- E23. `gate-sweep.yml` and `tools/ci/sweep.py` (block item 2): the sweep skips off the live head, re-runs the red `gate` of every other run once this run's is green and newest-covering, and otherwise settles:
  - `tools/ci/gate.py:348` `import sweep`
  - `tools/ci/sweep.py:9` `completed and not`
  - `tools/ci/sweep.py:9` `-> re-run that`
  - `tools/ci/sweep.py:222` `if gate.get("conclusion") == "success" or run["id"] in self.rerun_ids:`
  - `tools/ci/sweep.py:231` `self.post(f"repos/{self.repo}/actions/jobs/{gate['id']}/rerun")`
  - `tools/ci/sweep.py:239` `if not prs or not self.live(prs[0]["number"], head):`
  - `tools/ci/sweep.py:245` `if not covers_newest(vg, runs):`
  - `tools/ci/sweep.py:246` `return self.settle(run_id, pr, head)`
  - `tools/ci/sweep.py:249` `for r in sorted((r for r in runs if r["id"] != v["id"]), key=lambda r: r["id"]):`
  - `tools/ci/sweep.py:277` `No green gate covers the newest event: once every gate at the head has concluded,`
  - `tools/ci/sweep.py:278` `re-run each red one that judged before another run's sources finished`
- E24. The ruleset instrument and the marker rule:
  - `tools/ci/ruleset_cutover.py:2` `required contexts over from the 17 to`
  - `tools/ci/ruleset_cutover.py:31` `are tvofi's, as the repository owner`
  - `tools/ci/ruleset_cutover.py:44` `THE PAYLOAD is the rollback copy's six writable keys with one change:`
  - `tools/ci/ruleset_cutover.py:228` `def save_rollback(gh, path: str) -> dict:`
  - `tools/ci/ruleset_cutover.py:298` `READBACK half 1 FAILED`
  - `tools/ci/ruleset_cutover.py:302` `READBACK half 2 FAILED`
  - `tools/ci/ruleset_cutover.py:311` `rc, out = gh(["-X", "PUT", RULESET, "--input", "-"], json.dumps(want))`
  - `tests/doc_claims.py:3228` `"scope": "user" if _in_comment(bare, m.start()) else "wiring"})`
- E25. The two arrows added, and what the figure leaves out:
  - `tools/audit/seat/cloud_relay.sh:830` `python3 -I "$HERE/carry_fold.py"`
  - `tools/audit/seat/carry_fold.py:63` `import roster_edit`
  - `tools/audit/seat/carry_fold.py:87` `return roster_edit.main(parts + ["--worktree", a.worktree, "--checkout", a.checkout,`
  - `tools/audit/seat/carry_fold.py:88` `"--branch", branch, "--push"])`
  - `tools/audit/seat/bus.sh:460` `train_add "$pr" "$first"`
  - `tools/audit/seat/bus.sh:475` `[ -n "${HPO_BUS_TRAIN_STATE:-}" ] || return 0`
  - `tools/audit/seat/bus.sh:476` `"Fix review: merge "*`
  - `tools/audit/seat/bus.sh:482` `merge_train.py"} add "$1" "$sha"`
  - `tools/audit/seat/bus.sh:479` `cloud_relay.sh" held "$1"`
  - `tools/audit/seat/bus.sh:610` `classify "$h"`
  - `tools/audit/seat/cloud_relay.sh:269` `"$HERE/merge_train.py" classify`
  - `tools/audit/seat/cloud_dispatch.py:584` `if role == "reviewer":`
  - `tools/audit/seat/cloud_dispatch.py:586` `"reviewer-fire", pr, head, f"nonce={nonce} the dispatch ref was not published"`
- E26. "Each other `runs` arrow from a script starts its target as a process", arrow by arrow (the tick loop's four and the relay's `bus.sh` are E11 and E8, the dispatch's is E9, the train's is E16):
  - `tools/audit/seat/beat_jobs.py:164` `p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=3000)`
  - `tools/audit/seat/beat_jobs.py:202` `return self.run([sys.executable, "-I", str(self.repo / tool), *args], self.repo, self.env)`
  - `tools/audit/seat/state_docs.py:503` `r = subprocess.run(cmd, cwd=a.checkout, capture_output=True, text=True)`
  - `tools/audit/seat/roster_queue.py:234` `return subprocess.run(c, capture_output=True, text=True, env=env, cwd=a.edit_checkout)`
  - `tools/audit/seat/roster_queue.py:398` `r = sh(*cmd)`
  - `tools/audit/seat/postmerge.py:81` `code, o = run(argv)`
  - `tools/audit/seat/open_driver.py:185` `return subprocess.Popen(argv, cwd=self.repo, start_new_session=True`
  - `tools/audit/seat/open_driver.py:76` `handoff-no-pr refs/heads/handoff/`
- E27. The train's critical path and hold ref, the tick's reads, the watcher, the ledger's stores:
  - `tools/audit/seat/merge_train.py:2486` `item["sweep_after"] = True`
  - `tools/audit/seat/merge_train.py:837` `HOLD_REF = "refs/heads/train-hold"`
  - `tools/audit/seat/merge_train.py:2948` `"--method", "DELETE"`
  - `.github/workflows/nightly.yml:1099` `HOLD_MAX_AGE_S=3600`
  - `tools/audit/seat/orchestrator_tick.py:15` `GitHub API for PR/CI/mergeability state, the tree for rows/carries/pins, the`
  - `tools/audit/seat/orchestrator_tick.py:16` `It does NOT act: no pushes, no merges, no closes.`
  - `tools/audit/seat/orchestrator_tick.py:756` `lg.review_owed(`
  - `tools/audit/seat/orchestrator_tick.py:1610` `"refs/heads/design/*"`
  - `tools/audit/seat/heartbeat.sh:41` `"+refs/heads/$REF:refs/hb/watch"`
  - `tools/audit/seat/ledger.py:22` `dispositions.tsv`
  - `tools/audit/seat/ledger.py:27` `events.tsv`
  - `tools/audit/seat/instruments/tick_loop.sh.md:18` `When: run detached (`
- E28. `docs/architecture.md`, One owner per concern, the claims the round-2 review did not list as read:
  - `custom_components/heatpump_optimizer/coordinator.py:2748` `re-runs the divisor floor`
  - `custom_components/heatpump_optimizer/coordinator.py:2787` `self.__dict__["_ctx"] = replace(ctx, **{n: value})`
  - `custom_components/heatpump_optimizer/thermal_model.py:248` `def __post_init__(self) -> None:`
  - `custom_components/heatpump_optimizer/thermal_model.py:256` `Enforce the physical floor on every thermal-mass divisor.`
  - `custom_components/heatpump_optimizer/coordinator.py:6166` `def _solve_hubs(`
  - `custom_components/heatpump_optimizer/inputs.py:338` `if factor is None:`
  - `custom_components/heatpump_optimizer/inputs.py:410` `if value is None:`
  - `custom_components/heatpump_optimizer/inputs.py:413` `if kw is None or not math.isfinite(kw):`
  - `custom_components/heatpump_optimizer/const.py:1394` `as a finite float; anything else is`
  - `custom_components/heatpump_optimizer/quiet_windows.py:301` `minutes = int(round(hour * 60.0)) % (24 * 60)`
  - `custom_components/heatpump_optimizer/dhw_schedule.py:458` `if total_minutes != 24 * 60:`
  - `custom_components/heatpump_optimizer/sensor.py:347` `A sensor whose state is the number at one path of the coordinator payload.`
  - `custom_components/heatpump_optimizer/heat_energy.py:8` `Pure, with no Home Assistant import: the coordinator reads`
  - `custom_components/heatpump_optimizer/heat_energy.py:223` `The dwell's shares when observed, else the plan's split: the one owner of the choice.`
  - `custom_components/heatpump_optimizer/coordinator.py:228` `from . import heat_energy`
  - `custom_components/heatpump_optimizer/accuracy.py:841` `if not electric:`
  - `custom_components/heatpump_optimizer/accuracy.py:843` `if not measured_heat:`
  - `custom_components/heatpump_optimizer/accuracy.py:845` `return COP_ESTIMATED if estimated else COP_HEAT_METERED`
  - `custom_components/heatpump_optimizer/coordinator.py:3342` `if not available:`
  - `custom_components/heatpump_optimizer/coordinator.py:10715` `"model_restart": advice,`
  - `custom_components/heatpump_optimizer/coordinator.py:7940` `"house_heat_loss_learned": house_loss_converged(`
  - `custom_components/heatpump_optimizer/config_flow.py:3370` `_page_schema(`
  - `custom_components/heatpump_optimizer/config_flow.py:3808` `_page_schema(`
  - `custom_components/heatpump_optimizer/config_flow.py:3549` `_options_schema(`
  - `custom_components/heatpump_optimizer/config_flow.py:2512` `vol.Schema({})`
  - `custom_components/heatpump_optimizer/button.py:60` `ResetHeatLossButton(coordinator, entry),`
  - `custom_components/heatpump_optimizer/button.py:223` `Unavailable unless the learning page's debug-collection option is on and`

## Red checks

none. At ba0ed526cc `python3 tools/audit/seat/merge_train.py classify ba0ed526cc3b0a4b62a4e05b165710237e3bd123 --pr 3430` printed `WAIT ... pending: gate red: none`; this head has no run yet.

## Forward-carry

- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `tests/doc_claims.py` now refuses a bare marker whose groups are all done, so the re-read after the last product merge states the tree and adds no marker for a landed group. The "One owner per concern" bullets in `docs/architecture.md` were written at d08ed31049; re-check each against its module at the delta's merge base. Control: `python3 tests/doc_claims.py --markers --roster <the roster branch's file>` exits 0 with `0 of 0 marker(s) due`. Carry: R10-ARCH-DOCS-DELTA
- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `dev/README.md` states that the ruleset requires only `gate` on `nudge.md` section 4's authority, not from a live read. A seat with the ruleset read confirms it against ruleset 23698884, or corrects the sentence. Carry: R10-ARCH-DOCS-DELTA
- `dev/programme/rosters/wave-r10-groups.json`, R10-USER-DOCS-VERIFY's brief: `check_marker_census`'s anchor no longer requires a marker to exist, so removing the last user-doc marker leaves `tests/doc_claims.py` green. Control: `python3 tests/doc_claims.py --markers --user` ends `0 user-doc marker(s), 0 due`. Carry: R10-USER-DOCS-VERIFY

## Friction

none
