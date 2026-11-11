R10-ARCH-DOCS, arm B of triage P261: `docs/architecture.md` and `dev/README.md` verified against the tree, every wiring marker resolved, the machinery figure redrawn and pinned. Closes #2395. Part of #201.

Round 2, after `Fix review: blocked d581d4e0b2e5fab662a2eb70b47b77b82ee5cc6e doc-claim-false`. Every sentence and every arrow the diff adds to the two pages was re-read against the code; `## Figures` names the line behind each.

The six block items:

1. **The beat does not run `roster_sync.py`.** Confirmed: `beat_jobs.py:424` passes `--plan`, and `state_docs.py:63` enters the roster-sync step only under `beat --apply`. The figure is redrawn from who starts each script: `merge_train.py` runs `postmerge.py`, which runs `roster_sync.py`, which calls `roster_edit.py`, the one node that writes the roster branch. The prose says the same and adds "No beat job runs `roster_sync.py`".
2. **"the only file a pull-request event starts".** Removed. The `ci.yml` bullet lists its five events, and the `dependabot-automerge.yml` bullet names `pull_request_target`.
3. **"three housekeeping jobs outside this chain".** Now: `cancel-superseded` and `refresh` need no other job, and `sweep-self` needs `gate`.
4. **"the four that write a store".** Now three jobs, named: `roster-drain`, `plan-beat`, `opener`. "The rest report or clean up" is deleted; this seat did not establish it for the other eleven.
5. **The entry rule's seat half was unpinned.** New red fixture `a single entry that is a script, not a seat`, and its own mutant row. The reviewer's mutant (`if len(entries) != 1:`) is the harness's `the entry is a seat` row and is killed.
6. **Who reads entity state.** The reviewer's three sites are real, and so are more. The sentence now names each reader by module: `coordinator.py` (price, weather, PV production), `pump_arbiter`, `pump_signals`, `early_cutoff.py` (the pump's own entities), `away.py`, `services.py`, `config_flow.py`.

The reviewer's instrument finding, built here: a script node names one script, and a script's row cites that script's file. `machinery_edge_findings` refuses a node whose first label line names two files, and compares the cited basename with the node's first word, where it used to accept any basename in the label. The grouped nodes are gone: `state_docs.py`, `plan_page.py` and `roster_sync.py` are three nodes, the beat's node is `beat_jobs.py`, and the opener's is `open_pr.sh`.

Class repair, beyond the six. Each was a sentence the tree did not support:

- `dev/README.md`:
  - The job graph omitted two `needs` edges: `prelude` to `pr-contract` and `prelude` to `gate`. Drawn.
  - The event node omitted the manual dispatch.
  - `gate-sweep.yml` "re-runs a stale `gate`": the step re-judges the older gates at the head. Reworded to the step's own name.
  - `marketplace.yml`, `nightly.yml`, `merge-main.yml`, `dependency-graph.yml`, `release.yml`, `pages.yml`: each bullet now gives the whole trigger set. `dependency-graph.yml`'s push is path-filtered.
  - "the orchestrator starts both [loops]": no file says so. Now "each run detached under `daemonize.py` by its instrument guide".
  - The tick loop runs the train's sweep only under `--sweep`. Said.
  - `orchestrator_tick.py` "reads the bus refs, the dispatch refs": not established. Now its docstring's sources and the two reads this seat found.
  - "The flow instruments measure any round from git and the bus": one of the four reads git alone, one the verdict bus, one a workflow run, one the plan. Each now carries its own source.
  - "each at the head SHA its verdict names": the train merges at the head the verdict carries to. Reworded.
  - "the sweep ... stops while one is open": the sweep returns having added nothing. Reworded.
  - The bus-refs store omitted `design-verdict`, and the figure omitted that a seat runs `bus.sh` itself and that `bus.sh` and `postmerge.py` write the ledger. Drawn.
- `docs/architecture.md`, One owner per concern:
  - "publishes it whole in one assignment": `_publish_params` makes two assignments. Now "rebinds the coordinator context and the live model".
  - "Each cycle owns its own copy ... a restore or an await cannot change": not found. Now the three copies the code makes.
  - "refuses a non-finite or out-of-range one": the range half was not found. Now the two functions and what each refuses.
  - "The hour-of-day conversions are two functions": two more inline formatters exist (`quiet_windows.py`, `modbus_prefill.py`). Now only "two functions own what the end of the day reads as".
  - "for the sensors that each carried their own guard": history, deleted.
  - "An optional heat energy meter gives a measured COP, heat over electric energy": neither half located. Replaced by `heat_energy.py`'s own statement of what it owns.
  - "reads "not measurable" where no meter makes COP observable": that state is an electric meter with no measured heat; no electric meter is a different state. Said.
  - "No evidence is a dash with a reason": the code gives no grade and one reason code; the dash is the card's. "One view model": no such symbol. "No score reads or recomputes a Savings figure": not found, deleted.
  - "renders every options page from one field registry": four forms build their own. Named.
  - "each learner's phase": the module says each thermal learner's.

Kept on thinner ground, and said here so the reviewer weighs it: "A seat is started by the orchestrator" rests on `cloud_dispatch.py` starting nothing itself (E9) and on its help text; no contract line this seat read says who fires the trigger.

Step ref: `refs/heads/handoff-wip/r10-arch-docs` still held round 1's `BLOCKED.md` commit (71f460d038), no ancestor of the pull-request head, so a fast-forward step push had nowhere to go. The seat's harness refused retiring the ref, and no step was pushed this round.

Verified true and left as written: the learners' three `homeassistant` imports, "never call the coordinator", the two `store.py` importers, the `button.py` list, the ledger-kind lists, the sequence notes the diff added, the Who-decides row.

What landed in round 1, by brief item, unchanged unless listed above:

1. **Verification and marker resolution.** Every `[target:]` and `[retired-by:]` marker on the two pages is a statement of the tree. The departures from the planned shape, by causing group: R10-CI-LAYOUT-P2 (a ninth unit `kernel-points`; the prelude's outputs; `ci.yml` is the live umbrella; both rerun workflows gone; three workflow files were unlisted), R10-ORCH-MACHINERY (`tick_loop.sh`, not `beatd.py`, drives the tick, the relay, the train and the heartbeat; two ledger kinds never landed; no script opens `train-stop`), R10-FLOW-RELAY-HOLD (the hold list is a file only the orchestrator writes), R10-PLAN-ARTIFACT and the two R10-FLOW-TOOLKIT groups (the plan model is `tools/plan/replan.py`; the flow instruments do not import it), R10-PARAMS-OWNER, R10-ARCH-SHAPES, R10-SENSOR-PAYLOAD, R10-SCORES. The ruleset sentence rests on `dev/governance/roles/nudge.md` section 4, not on a live read: this seat has no ruleset API read.
2. **The machinery figure.** Top-down from one entry, actors in one group and stores in another, every arrow `runs` or `writes` from the actor, one table row per arrow citing the file and quoted text that performs it.
   - Design choice: the citation table lives on the page, not in the test. A list kept in the test would be the second copy `fixer.md` step 11 warns of.
   - Design choice: reads are not drawn. The prose under the table states them.
   - Design choice: a script that writes through a helper it runs is drawn as the writer (`open_pr.sh` through `app_push.sh`, the relay through its updater, `bus.sh` through its poster). The roster branch is the exception, because two drawn paths share `roster_edit.py`. The page says both.
   - Design choice: `beatd.py` and `open_driver.py` are launchers between two drawn scripts and are not nodes. The orchestrator's row to `beat_jobs.py` and the job's row to `open_pr.sh` each cite the line that starts the launcher, and the page names both launchers under the table. The reason is under Alternatives.
   - A person's row cites the contract or guide that says the person does it. The one-script rule binds script actors only.
3. **The pins, in `tests/doc_claims.py`.** `machinery_edge_findings` and `due_marker_findings`; the latter makes "no unresolved target marker on main" a hard check.
4. **Closure.** The predicate opens every cited file. Ten that were INERT are on `INERT_EXCEPT`, one of them added this round (`postmerge.py`), and the closures of `tests/doc_claims.py` and `tests/entities.py` are re-recorded.

Carries, numbered from 1 as `review_packet.py` counts them. Carry 1 and Carry 13 are item 2. Carry 2, Carry 7, Carry 9 and Carry 11 moved to R10-USER-DOCS-VERIFY and are not touched (Carry 14). Carry 3 and Carry 4 are items 2 and 3. Carry 5 is the R10-SCORES line, corrected this round. Carry 6 and Carry 8: arm A's checker is present and green at this head and was not rebuilt. Carry 10 is the ledger-kind departure. Carry 12: user-doc markers are left. Carry 14: no user page is edited. Carry 15: done at this merge base; the re-read after the last product merge is R10-ARCH-DOCS-DELTA's.

Outside the roster group's `files`: `tests/doc_claims.py`, `tests/closure.py`, `tests/closures.json`, and the mutant harness (`fixer.md` step 18).

Alternatives not taken:
- Keeping the grouped nodes and adding a "started by" column. The table would then carry a claim no check reads; splitting the node makes the existing citation carry it.
- Drawing `beatd.py` and `open_driver.py` as nodes with rows citing their own lines. Tried first: a cited file leaves INERT, and `tests/entities.py` then failed `every bash -c / sh -c a check runs carries errexit ... (countermeasure B)` on nine sites in those two files, which that check leaves out only while they are INERT (its message: `beatd.py, INERT, is the excluded arm`). Editing either instrument, or that check's exclusion, to draw two boxes is outside this group.
- Deriving each arrow's direction from which script names which. A comment naming the other script satisfies it in both directions.

## Head

cf8e31978081492d2078b8602339d0c35b263779 (merge base 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444; origin/main dbd1ab5b07 at 2026-11-11T05:08:36Z).

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_arch_docs_mutants.py` at the head. It replaces each predicate's test with one that cannot fire, runs `tests/doc_claims.py` on the mutated source, and prints the checks that fail. Nothing is written to the tree.

- due marker: FAIL `red fixture: a due wiring marker is refused, and a not-yet-due one is not (null control)`
- verb: FAIL `red fixture: a verb that is not runs or writes is a finding`
- store as actor: FAIL `red fixture: a store drawn as the actor (is read by) is a finding`
- writes ends at a store: FAIL `red fixture: writes ending at an actor is a finding`
- arrow with no row: FAIL `red fixture: one arrow reversed is a finding`
- row with no arrow: FAIL `red fixture: a row with no arrow is a finding`
- quoted text in the cited file: FAIL `red fixture: a cited line the code no longer holds is a finding`
- cited file is the actor's: FAIL `red fixture: an arrow reversed together with its row is a finding` and `red fixture: a row citing a file its node names only below the first line is a finding`
- one script per node (new): FAIL `red fixture: a node grouping two scripts is a finding`
- the entry is a seat (new, block item 5): FAIL `red fixture: a single entry that is a script, not a seat is a finding`
- one entry: FAIL `red fixture: an actor nothing starts, a second entry is a finding` and the seat fixture
- node names unique: FAIL `red fixture: two nodes of one name is a finding`
- cited file tracked, and one arrow per line: the run dies (`TypeError`, `AttributeError`) on the fixture that plants the case. Killed by a crash, not by a named check.

## Null control

- The harness's baseline, the unmutated file, prints no FAIL line.
- Block item 1 at both ends. `machinery_edge_findings` as it is at this head, applied to `dev/README.md` as it was at d581d4e0b2 (`git show d581d4e0b2:dev/README.md`), returns findings, among them `state_docs.py, roster_sync.py, plan_page.py -writes-> roster branch: cites tools/audit/seat/roster_sync.py, which is not the script the actor's node names` and one `a script node names one script` line per grouped node. Applied to the page at this head it returns none.
- The evidence check below read `miss=1` on its first run: one row cited `coordinator.py:2746` for a line that is at 2754. The row was corrected, not the checker.
- `machinery_edge_findings` on the clean fixture returns nothing: `the clean fixture yields no finding (null control)`.
- The owner's control on the page's own figure: `reversing any one arrow of the page's figure is a finding`. The check reverses each arrow in turn and requires a finding every time.
- Each "none" the pages state, with the count that would not be zero were it false:
  - No beat job runs the relay, the tick, the train or the heartbeat: `grep -cE 'cloud_relay|orchestrator_tick|merge_train|heartbeat\.sh' tools/audit/seat/beatd.jobs.json` prints 0; the same over `beat_jobs.py` prints one line, a comment naming what `orchestrator_tick.py` prints. Control: `grep -c 'replan.py' tools/audit/seat/beat_jobs.py` is not 0.
  - No beat job runs `roster_sync.py`: `grep -c roster_sync` prints 0 for `beat_jobs.py` and for `beatd.jobs.json`. Control: the same over `postmerge.py` is not 0.
  - Every beat job is a `beat_jobs.py` call: the set of `argv[2]` over the jobs of `beatd.jobs.json` has one member.
  - The relay opens no pull request: `grep -cE 'open_pr|pr create|/pulls' tools/audit/seat/cloud_relay.sh` prints one line, a comment about `open_pr.sh`.
  - No script opens `train-stop`: `git grep -nE 'open.{0,12}train-stop|train-stop.{0,4}open' -- tools .github` returns prose, the sweep's read and self-test fixtures, and no production `open`. Control: the same pattern with `postmerge-owed` returns `postmerge.py`'s `open`.
  - One pull-request trigger outside `ci.yml`: `grep -lE '^  (pull_request|pull_request_target|pull_request_review):' .github/workflows/*.yml` prints `ci.yml` and `dependabot-automerge.yml`.
  - Every workflow file is on the page: a loop over `.github/workflows/*.yml` testing `grep -qF` of each path in `dev/README.md` prints no file.
  - No learner imports the coordinator, three import `homeassistant` at module level, two import `store.py`: `grep -lE` over the nine learner modules of the page's diagram prints no file, then `accuracy.py defrost.py dhw_learning.py`, then `dhw_learning.py snapshots.py`.
  - One writer of the thermal parameters: `git grep -nE '_thermal_params = |_thermal_model\.params = ' -- custom_components/heatpump_optimizer` prints the two lines of `_publish_params` and the facade's class attribute.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at the head: `ALL 321 checks PASSED`. Three more than round 1: the three new red fixtures.
- Mutants: the harness prints `RESULT baseline_fails=0`, `RESULT mutants=14`, `RESULT killed=14`. Rule: one row per predicate test of the two functions, and one per half of the entry rule; a row whose text is not in the file exactly once is an error.
- Marker resolver at the head: `python3 tests/doc_claims.py --markers` prints `0 of 0 marker(s) due`, exit 0.
- Mermaid: `NODE_PATH=$(npm root -g) node dev/audit/harnesses/r10_mermaid_parse.mjs tools/site dev/README.md docs/architecture.md`, after `npm ci` in `tools/site`, printed `mermaid 12.3.0 parse+render in Chromium: 5 block(s), 0 failure(s)`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Closure: `./tests/derive_closures.sh --single tests/doc_claims.py` (Linux) exited 0 and updated one closure once `postmerge.py` was on `INERT_EXCEPT`. `tools/pr/ci_predict.py --base origin/main` then printed one `UNDER-SCOPED tests/entities.py` line; `./tests/derive_closures.sh --single tests/entities.py` exited 0.
- Seams (`fixer.md` step 8). The class is "a sentence or an arrow the tree contradicts", on the two pages. Enumerator for the arrows: the `-->` lines of the block under `### Its components`, which the gate check reads; each is closed by its table row. Enumerator for the sentences: the `+` lines of `git diff $(git merge-base origin/main HEAD)...HEAD -- dev/README.md docs/architecture.md`; each factual one is under an E-number below, or under `## Null control` where it is a "none". No instrument checks a prose sentence against code: the list below was built by reading, and its line citations are machine-checked. The other three figures in `dev/README.md` and the one in `docs/architecture.md` are not under the arrow convention; the job graph's `needs` arrows are E3.
- Evidence. Each row is `path:line` and text that line holds at the head. The check: for every row, the text is a substring of that line of that file. It printed `RESULT rows=218 hold=218 miss=0`. Line numbers are this head's; a later tree is read by the quoted text.

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
- E18. `docs/architecture.md`: who reads entity state:
  - `custom_components/heatpump_optimizer/coordinator.py:3390` `return hass.states.get(entity_id)`
  - `custom_components/heatpump_optimizer/coordinator.py:3387` `.price_entity`
  - `custom_components/heatpump_optimizer/coordinator.py:7047` `self.hass.states.get(weather_entity)`
  - `custom_components/heatpump_optimizer/coordinator.py:9785` `entity_id = config.production_entity`
  - `custom_components/heatpump_optimizer/coordinator.py:9788` `self.hass.states.get(entity_id)`
  - `custom_components/heatpump_optimizer/pump_arbiter.py:1111` `state = inp.hass.states.get(entity) if entity else None`
  - `custom_components/heatpump_optimizer/pump_arbiter.py:1110` `entity = _slot_entity(inp.config, slot)`
  - `custom_components/heatpump_optimizer/pump_arbiter.py:1422` `.heat_pump_switch_entity`
  - `custom_components/heatpump_optimizer/pump_signals.py:456` `.heat_pump_mode_entity`
  - `custom_components/heatpump_optimizer/pump_signals.py:457` `reader.hass.states.get(mode_entity)`
  - `custom_components/heatpump_optimizer/early_cutoff.py:236` `.heat_pump_defrost_entity`
  - `custom_components/heatpump_optimizer/early_cutoff.py:272` `.heat_pump_switch_entity`
  - `custom_components/heatpump_optimizer/away.py:609` `_holiday_days(states.get(entity_id), now)`
  - `custom_components/heatpump_optimizer/services.py:834` `if hass.states.get(raw) is None:`
  - `custom_components/heatpump_optimizer/config_flow.py:2232` `hass.states.get(record.entity_id)`
  - `custom_components/heatpump_optimizer/inputs.py:933` `state = self.hass.states.get(entity_id)`
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

## Red checks

none

## Forward-carry

- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `tests/doc_claims.py` now refuses a bare marker whose groups are all done, so the re-read after the last product merge states the tree and adds no marker for a landed group. The "One owner per concern" bullets in `docs/architecture.md` were written at d08ed31049; re-check each against its module at the delta's merge base. Control: `python3 tests/doc_claims.py --markers --roster <the roster branch's file>` exits 0 with `0 of 0 marker(s) due`. Carry: R10-ARCH-DOCS-DELTA
- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `dev/README.md` states that the ruleset requires only `gate` on `nudge.md` section 4's authority, not from a live read. A seat with the ruleset read confirms it against ruleset 23698884, or corrects the sentence. Carry: R10-ARCH-DOCS-DELTA
- `dev/programme/rosters/wave-r10-groups.json`, R10-USER-DOCS-VERIFY's brief: `check_marker_census`'s anchor no longer requires a marker to exist, so removing the last user-doc marker leaves `tests/doc_claims.py` green. Control: `python3 tests/doc_claims.py --markers --user` ends `0 user-doc marker(s), 0 due`. Carry: R10-USER-DOCS-VERIFY

## Friction

none
