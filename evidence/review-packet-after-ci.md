# Review packet #3430
head: d581d4e0b2e5fab662a2eb70b47b77b82ee5cc6e
base: 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=130284770921 success
arch-score / arch-score id=130298436447 success
arm id=130284448717 skipped
budget-raise-gate / budget-raise-gate id=130298465817 success
cancel-superseded id=130298478489 success
codeql id=130298473000 skipped
codeql / Analyze (actions) id=130284640592 success
codeql / Analyze (javascript-typescript) id=130284640630 success
codeql / Analyze (python) id=130284640762 success
gate id=130298435582 success
governance id=130298479961 skipped
governance / delivery-status id=130284640697 success
governance / delivery-status-publish id=130284642010 skipped
governance / env-matrix id=130284640598 success
governance / instrument-self-tests id=130284640655 success
governance / policy-docs id=130284640548 success
governance / record id=130284642801 skipped
governance / wave-script id=130284640525 success
hassfest id=130298478938 skipped
hassfest / hassfest id=130284640663 success
kernel-points id=130298478465 skipped
pr-contract id=130298436854 skipped
pr-contract / pr-contract id=130297830353 success
prelude id=130298469657 success
refresh id=130298476449 success
sweep-self id=130298718706 skipped
tests id=130298436393 skipped
tests / arch-instrument id=130285142360 success
tests / briefs id=130284640691 success
tests / browser id=130285142304 success
tests / ci-ratchet id=130295631661 skipped
tests / claims-autofix id=130294563666 skipped
tests / closure-scope id=130284640676 success
tests / closures id=130285142384 success
tests / closures-autofix id=130295632294 skipped
tests / coverage id=130285142328 success
tests / coverage-ratchet id=130295372397 success
tests / fast (3.14) id=130285142271 success
tests / graders-head-copy id=130295372289 success
tests / lane-proofs id=130297787673 success
tests / mutation id=130284640600 success
tests / mutation-autofix id=130285145733 skipped
tests / mutation-pins id=130285146087 skipped
tests / nightly-ha id=130285144309 skipped
tests / nightly-status id=130284640607 success
tests / replay id=130285144105 skipped
tests / typing id=130285142278 success
validate id=130298465710 skipped
validate / validate-hacs id=130284640651 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 6bc4f4e1: R10-ARCH-DOCS-DELTA: R10-ARCH-DOCS-DELTA resolved on origin/handoff/audit-r10-roster
NOTE body item d5ef2398: R10-ARCH-DOCS-DELTA: R10-ARCH-DOCS-DELTA resolved on origin/handoff/audit-r10-roster
NOTE body item a44d0012: R10-USER-DOCS-VERIFY
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/doc_claims.py --markers
             `tests/doc_claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         NODE_PATH=$(npm root -g) node dev/audit/harnesses/r10_mermaid_parse.mjs tools/site dev/README.md docs/architecture.md
             `dev/audit/harnesses/r10_mermaid_parse.mjs` is in the tree at this head
  unverified git diff --quiet f043978af8 HEAD -- dev/README.md docs/architecture.md && echo UNCHANGED
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         ./tests/derive_closures.sh --single tests/doc_claims.py
             `tests/derive_closures.sh` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         ./tests/derive_closures.sh --single tests/entities.py
             `tests/derive_closures.sh` is in the tree at this head
  ok         tools/pr/ci_predict.py --base origin/main --apply-inert
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/md_tables.mjs
             `tests/md_tables.mjs` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 14 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/README.md b/dev/README.md
index 9b72712250..d802c4f4ac 100644
--- a/dev/README.md
+++ b/dev/README.md
@@ -10,14 +10,14 @@ document and the obligation each carries; the named file is the policy, not
 this summary. Where this README and a policy file disagree, the policy file
 wins.
 
-**It describes the shape at the end of the current programme.** What is
-already on `main` is written from the tree. What a roster group has still to
-land carries a marker naming that group: `[target: <group>]` for an element
-that exists once the group merges, `[retired-by: <group>]` for one the group
-removes, and `; owner step` where the change lands only on the owner's own
-action. The groups are the keys of `dev/programme/rosters/wave-r10-groups.json`,
-and `tests/doc_claims.py` refuses a marker naming anything else. Resolving the
-markers once their groups are done is R10-ARCH-DOCS's end-of-round check.
+**It describes `main`.** Everything it names is written from the tree, and
+`tests/doc_claims.py` resolves each path, script argument, workflow job,
+ledger kind and diagram node it names. A page that describes a shape still to
+land marks each such element with the roster group that lands it:
+`[target: <group>]` for an element that exists once the group merges,
+`[retired-by: <group>]` for one the group removes, and `; owner step` where
+the change lands only on the owner's own action. `tests/doc_claims.py` refuses
+a marker naming no roster group, and one whose groups are all done.
 
 ## Reading the figures
 
@@ -30,7 +30,6 @@ theme:
 | rectangle `[ ]` | a script, or a job run detached by `tools/audit/seat/daemonize.py` |
 | rhombus `{ }` | a decision made by a person or an agent |
 | cylinder `[( )]` | a git ref or a store |
-| dashed edge | flow that exists once its marked group lands |
 
 ## The `dev/` layout
 
@@ -155,60 +154,70 @@ train → merge → record → stamp. The order is the orchestrator's contract,
 
 ## The CI shape
 
-### The job graph at programme end
+### The job graph
 
-One umbrella workflow calls every unit and ends in one check, `gate`, which is
-the only context the ruleset requires. The check name of a unit's job is
-`<file stem> / <job>`, for example `tests / fast (3.14)`.
+One umbrella workflow, `.github/workflows/ci.yml`, calls every unit and ends in
+one check, `gate`, which is the only context the ruleset requires. The check
+name of a unit's job is `<file stem> / <job>`, for example `tests / fast (3.14)`.
 
 ```mermaid
 flowchart LR
-    ev(["pull request, review,<br/>push to main, merge group"]) -.-> ci["ci.yml: the umbrella<br/>[target: R10-CI-LAYOUT-P2]"]
-    ci -.-> pre["prelude<br/>kind, pr, base, scope"]
-    pre -.-> tests["tests"]
-    pre -.-> codeql["codeql"]
-    pre -.-> gov["governance"]
-    pre -.-> hass["hassfest"]
-    pre -.-> val["validate"]
-    pre -.-> arch["arch-score"]
-    pre -.-> brg["budget-raise-gate"]
-    tests & codeql & gov & hass & val & arch & brg -.-> prc["pr-contract<br/>waits for code scanning"]
-    prc -.-> gate["gate"]
-    gate -.-> rs[("ruleset main-protect-checks<br/>requires only gate<br/>[target: R10-CI-LAYOUT-P2; owner step]")]
-    cut{"owner PUTs the whole ruleset,<br/>then reads it back"} -.->|"PUT"| rs
-    rs -.->|"read-back differs: roll back, ruleset first"| cut
+    ev(["pull request, review,<br/>push to main, merge group"]) --> ci["ci.yml: the umbrella"]
+    ci --> pre["prelude<br/>kind, pr, base, head, workset"]
+    pre --> tests["tests"]
+    pre --> codeql["codeql"]
+    pre --> gov["governance"]
+    pre --> hass["hassfest"]
+    pre --> val["validate"]
+    pre --> kp["kernel-points"]
+    pre --> arch["arch-score"]
+    pre --> brg["budget-raise-gate"]
+    tests & codeql & gov & hass & val & kp & arch & brg --> prc["pr-contract"]
+    prc --> gate["gate"]
+    gate --> rs[("ruleset main-protect-checks<br/>requires only gate")]
+    cut{"owner PUTs the whole ruleset,<br/>reads it back, rolls back<br/>if the read-back differs"} -->|"PUT"| rs
 ```
 
-The cut-over is the owner's: the ruleset object is written whole, read back
-and diffed, and rolled back ruleset-first if the read-back or the first runs
-fail. The orchestrator boards it at a pitch that keeps the gap rule. Those
-steps are the ORCHESTRATOR-PROMPT checklist the orchestrator runs; this figure
-shows only where they sit.
+An arrow from one job to the next means the second job needs the first. The
+prelude (`tools/ci/prelude.py`) computes once what the run is, and each unit
+runs when the prelude's work set names it. `ci.yml` also carries three
+housekeeping jobs outside this chain: `cancel-superseded`, `refresh` and
+`sweep-self`.
 
-### The workflows on `main` today
+The ruleset is the owner's: `tools/ci/ruleset_cutover.py` writes the object
+whole, reads it back and diffs it, and `--rollback` restores the saved copy.
+`dev/governance/roles/nudge.md` section 4 is the rule for reading it: the live
+ruleset every turn, never a remembered list.
 
-Each unit file below starts on its own pull-request event today, and the
-ruleset requires each of its contexts by name. The umbrella above turns every
-one into a callable unit.
+### The workflow files
 
+- `.github/workflows/ci.yml`: the umbrella, the only file a pull-request event
+  starts
 - `.github/workflows/tests.yml`: the gate scripts, the scoped selection, the
   closures and the autofix jobs
-- `.github/workflows/governance.yml`: policy, record and instrument self-tests
+- `.github/workflows/governance.yml`: policy, record and instrument
+  self-tests; it also runs on a schedule
 - `.github/workflows/codeql.yml`, `.github/workflows/hassfest.yml`,
   `.github/workflows/validate.yml`: code scanning and the two Home Assistant
   validators
 - `.github/workflows/pr-contract.yml`, `.github/workflows/arch-score.yml`,
-  `.github/workflows/budget-raise-gate.yml`: the body contract, the
-  architecture score and the raise gate
-- `.github/workflows/ci.yml`: the inert umbrella stub that phase one landed
-- `.github/workflows/pr-contract-rerun.yml` [retired-by: R10-CI-LAYOUT-P2]
-- `.github/workflows/budget-raise-gate-rerun.yml` [retired-by: R10-CI-LAYOUT-P2]
-- `.github/workflows/gate-sweep.yml`, which re-runs a stale `gate` at a pull request's live head [target: R10-CI-LAYOUT-P2]
+  `.github/workflows/budget-raise-gate.yml`, `.github/workflows/kernel-points.yml`:
+  the body contract, the architecture score, the raise gate and the kernel
+  benchmark
+- `.github/workflows/gate-sweep.yml`: starts when a CI run completes and
+  re-runs a stale `gate` at a pull request's live head
+- `.github/workflows/marketplace.yml`: on a schedule, calls the two Home
+  Assistant validators
 - `.github/workflows/nightly.yml`, `.github/workflows/merge-main.yml`,
-  `.github/workflows/release.yml`, `.github/workflows/pages.yml`,
-  `.github/workflows/kernel-points.yml`: standalone, called by nothing
+  `.github/workflows/dependency-graph.yml`: start on a push to `main`
+- `.github/workflows/release.yml`, `.github/workflows/pages.yml`: start on a
+  version tag
+- `.github/workflows/dependabot-automerge.yml`: starts on a Dependabot pull
+  request
 
-`ls .github/workflows/` is the list; this one is a reading aid.
+Every unit the umbrella calls is a `workflow_call` file, so none of them
+starts on a pull-request event of its own. `ls .github/workflows/` is the
+list; this one is a reading aid.
 
 ### The order a change is refused in
 
@@ -225,9 +234,8 @@ flowchart TD
 ```
 
 Read it as the order a change must survive, not as separate jobs. The required
-check is every context the ruleset names today, and `gate` alone once the
-cut-over lands [target: R10-CI-LAYOUT-P2; owner step]. Two traps hold in both
-shapes: a required context that never reports at a head is absent, not green,
+check is `gate`. Two traps hold: a required context that never reports at a
+head is absent, not green,
 and a `DIRTY` pull request does not go red, it cannot run
 (`dev/governance/rules/claim-files.md`).
 
@@ -235,78 +243,175 @@ and a `DIRTY` pull request does not go red, it cannot run
 
 ### Its components
 
+Start at the top: the orchestrator dispatches a seat. Follow the arrows down
+from the seat's push to the merge on `main`. An arrow runs from the actor to
+its target and its label is the verb, `runs` or `writes`; no arrow means "is
+read by".
+
 ```mermaid
-flowchart LR
-    orch(["orchestrator seat"])
-    seats(["fixer, reviewer and design seats"])
-    owner(["owner"])
-    beat["beatd: one supervised beat,<br/>one job table<br/>[target: R10-ORCH-MACHINERY]"]
-    tick["tick: the read-only board<br/>orchestrator_tick.py"]
-    relayp["relay-probe arm<br/>cloud_relay.sh"]
-    relayh["handoff arm<br/>cloud_relay.sh"]
-    docs["state-docs and plan-page<br/>state_docs.py, plan_page.py"]
-    hb["heartbeat<br/>heartbeat.sh --once"]
-    watch["watcher, off the host<br/>heartbeat.sh --watch"]
-    ledger[("obligations ledger:<br/>dispositions, events, derived fold<br/>[target: R10-ORCH-MACHINERY]")]
-    bus[("bus refs: handoff, handoff-body,<br/>probe, review, verdict")]
-    disp[("dispatch records<br/>dispatch/role-topic")]
-    roster[("roster branch<br/>handoff/audit-r10-roster")]
-    hold[("hold list<br/>[target: R10-FLOW-RELAY-HOLD]")]
-    model[("one plan model<br/>[target: R10-PLAN-ARTIFACT]")]
-    kit["flow toolkit<br/>[target: R10-FLOW-TOOLKIT-MEASURE, R10-FLOW-TOOLKIT-MODEL]"]
-    train["merge train and its pitch<br/>merge_train.py"]
-    main[("main")]
-    pick{"dispatch, board, hold<br/>or stop"}
-
-    beat -.-> tick & relayp & relayh & docs & hb
-    tick --> orch
-    orch --> pick
-    pick -->|"dispatch"| disp
-    disp --> seats
-    seats -->|"push"| bus
-    relayp -->|"grade and post a verdict"| bus
-    relayh -->|"open or update the pull request"| bus
-    hold -.->|"frozen heads stay put"| relayh
-    relayp & relayh -.-> ledger
-    ledger -.-> tick
-    roster --> docs
-    model -.-> docs
-    kit -.-> model
-    hb --> watch
-    watch -->|"stopped beat"| owner
-    pick -->|"board at a pitch"| train
-    train -->|"pitch keeps the gap rule"| main
+flowchart TB
+    orch(["orchestrator<br/>the owner, or the seat holding the mandate"])
+    subgraph actors["actors"]
+        disp["cloud_dispatch.py"]
+        seats(["fixer, reviewer and design seats"])
+        tloop["tick_loop.sh"]
+        relay["cloud_relay.sh pass<br/>probe arm, handoff arm"]
+        busx["bus.sh"]
+        tick["orchestrator_tick.py<br/>the read-only board"]
+        beat["beatd.py, beat_jobs.py<br/>the job table"]
+        plan["replan.py<br/>the plan model"]
+        docs["state_docs.py, roster_sync.py, plan_page.py"]
+        rq["roster_queue.py"]
+        opener["open_driver.py, open_pr.sh"]
+        train["merge_train.py"]
+        hb["heartbeat.sh --once"]
+        watch["heartbeat.sh --watch<br/>off the host"]
+    end
+    subgraph stores["stores"]
+        dref[("dispatch ref<br/>dispatch/role-topic")]
+        drec[("dispatch record<br/>the nonce file")]
+        bus[("bus refs<br/>handoff, handoff-body, probe,<br/>review, verdict, design")]
+        hold[("relay hold list")]
+        ledger[("obligations ledger")]
+        board[("board file")]
+        roster[("roster branch<br/>handoff/audit-r10-roster")]
+        sdoc[("state documents and plan page<br/>handoff/audit-r10-plan")]
+        pr[("pull request")]
+        thold[("train-hold ref")]
+        hbref[("heartbeat ref")]
+        main[("main")]
+    end
+    orch -->|"runs"| disp
+    orch -->|"runs"| seats
+    orch -->|"runs"| tloop
+    orch -->|"runs"| beat
+    orch -->|"runs"| train
+    orch -->|"runs"| watch
+    orch -->|"writes"| hold
+    disp -->|"writes"| dref
+    disp -->|"runs"| busx
+    seats -->|"writes"| bus
+    tloop -->|"runs"| relay
+    tloop -->|"runs"| tick
+    tloop -->|"writes"| board
+    tloop -->|"runs"| train
+    tloop -->|"runs"| hb
+    relay -->|"runs"| busx
+    relay -->|"writes"| pr
+    relay -->|"writes"| ledger
+    busx -->|"writes"| drec
+    busx -->|"writes"| bus
+    busx -->|"writes"| pr
+    beat -->|"runs"| plan
+    beat -->|"runs"| docs
+    beat -->|"runs"| rq
+    beat -->|"runs"| opener
+    docs -->|"writes"| roster
+    docs -->|"writes"| sdoc
+    rq -->|"writes"| roster
+    opener -->|"writes"| pr
+    train -->|"writes"| main
+    train -->|"writes"| thold
+    hb -->|"writes"| hbref
 ```
 
-- **Detached jobs** run under `tools/audit/seat/daemonize.py` today: the tick
-  loop (`tools/audit/seat/tick_loop.sh`), the relay's pass
-  (`tools/audit/seat/cloud_relay.sh pass`), the state documents and the plan
-  page (`tools/audit/seat/state_docs.py`, `tools/audit/seat/plan_page.py`). The
-  heartbeat (`tools/audit/seat/heartbeat.sh`) pushes one liveness ref, which a
-  watcher off the host reads.
-- **One supervised beat** replaces the hand-launched loops: `tools/audit/seat/beatd.py`
-  with its job table `tools/audit/seat/beatd.jobs.json`, one job per arm, where an unreadable table refuses to start [target: R10-ORCH-MACHINERY]
-- **The obligations ledger**, `tools/audit/seat/ledger.py`, keeps two stores and one derived fold, with one writer per fact [target: R10-ORCH-MACHINERY]
-  - derived, recomputed every pass: `handoff-no-pr`, `handoff-update`, `probe-ref`, `stage-mismatch`, `absorb-edge-missing`, `record-owed` [target: R10-ORCH-MACHINERY]
-  - events, opened and closed: `reviewer-fire`, `verdict-unposted`, `train-stop` [target: R10-ORCH-MACHINERY]
+Every arrow is one row here, with the line of code or contract that performs
+it. `tests/doc_claims.py` refuses an arrow with no row, a row with no arrow, a
+row whose quoted text is not in the file it cites, and an arrow that starts at
+a store.
+
+| actor | verb | target | performed at |
+|---|---|---|---|
+| orchestrator | runs | cloud_dispatch.py | `tools/audit/seat/cloud_dispatch.py`: `Render the cloud-runner trigger payload for one seat` |
+| orchestrator | runs | fixer, reviewer and design seats | `tools/audit/seat/cloud_dispatch.py`: `fire the seat with a pointer to it` |
+| orchestrator | runs | tick_loop.sh | `tools/audit/seat/instruments/tick_loop.sh.md`: `in place of a seat looping the tick` |
+| orchestrator | runs | beatd.py, beat_jobs.py | `tools/audit/seat/instruments/beatd.py.md`: `until a supervisor unit is applied it runs under` |
+| orchestrator | runs | merge_train.py | `dev/governance/roles/nudge.md`: `tools/audit/seat/merge_train.py run` |
+| orchestrator | runs | heartbeat.sh --watch | `tools/audit/seat/instruments/heartbeat.sh.md`: `the owner schedules a cloud task` |
+| orchestrator | writes | relay hold list | `tools/audit/seat/cloud_relay.sh`: `only the orchestrator writes or edits it` |
+| cloud_dispatch.py | writes | dispatch ref | `tools/audit/seat/cloud_dispatch.py`: `refs/heads/{ref}` |
+| cloud_dispatch.py | runs | bus.sh | `tools/audit/seat/cloud_dispatch.py`: `str(HERE / "bus.sh"), "dispatch"` |
+| fixer, reviewer and design seats | writes | bus refs | `tools/audit/seat/body_push.sh`: `git push -q origin "$C:refs/heads/$REF"` |
+| tick_loop.sh | runs | cloud_relay.sh pass | `tools/audit/seat/tick_loop.sh`: `bash "$relay" pass --confirm` |
+| tick_loop.sh | runs | orchestrator_tick.py | `tools/audit/seat/tick_loop.sh`: `python3 "$HERE/orchestrator_tick.py"` |
+| tick_loop.sh | writes | board file | `tools/audit/seat/tick_loop.sh`: `mv -f "$tmp" "$out"` |
+| tick_loop.sh | runs | merge_train.py | `tools/audit/seat/tick_loop.sh`: `python3 "$HERE/merge_train.py" sweep` |
+| tick_loop.sh | runs | heartbeat.sh --once | `tools/audit/seat/tick_loop.sh`: `heartbeat.sh}" --once` |
+| cloud_relay.sh pass | runs | bus.sh | `tools/audit/seat/cloud_relay.sh`: `bash "$HERE/bus.sh" push-verdict` |
+| cloud_relay.sh pass | writes | pull request | `tools/audit/seat/cloud_relay.sh`: `upd=(bash "$why/update_pr.sh")` |
+| cloud_relay.sh pass | writes | obligations ledger | `tools/audit/seat/cloud_relay.sh`: `ledger_open verdict-unposted` |
+| bus.sh | writes | dispatch record | `tools/audit/seat/bus.sh`: `>> "$S/dispatched"` |
+| bus.sh | writes | bus refs | `tools/audit/seat/bus.sh`: `append_commit review` |
+| bus.sh | writes | pull request | `tools/audit/seat/bus.sh`: `"$POSTER" "$REPO" "$pr" "$body"` |
+| beatd.py, beat_jobs.py | runs | replan.py | `tools/audit/seat/beat_jobs.py`: `"tools/plan/replan.py", "--out"` |
+| beatd.py, beat_jobs.py | runs | state_docs.py, roster_sync.py, plan_page.py | `tools/audit/seat/beat_jobs.py`: `"tools/audit/seat/state_docs.py", "--push"` |
+| beatd.py, beat_jobs.py | runs | roster_queue.py | `tools/audit/seat/beat_jobs.py`: `"tools/audit/seat/roster_queue.py", "run"` |
+| beatd.py, beat_jobs.py | runs | open_driver.py, open_pr.sh | `tools/audit/seat/beat_jobs.py`: `"tools/audit/seat/open_driver.py", "--board"` |
+| state_docs.py, roster_sync.py, plan_page.py | writes | roster branch | `tools/audit/seat/roster_sync.py`: `roster_edit.write_roster(` |
+| state_docs.py, roster_sync.py, plan_page.py | writes | state documents and plan page | `tools/audit/seat/state_docs.py`: `refs/heads/{state_ref}` |
+| roster_queue.py | writes | roster branch | `tools/audit/seat/roster_queue.py`: `"--push"` |
+| open_driver.py, open_pr.sh | writes | pull request | `tools/audit/seat/open_pr.sh`: `bash "$_push"` |
+| merge_train.py | writes | main | `tools/audit/seat/merge_train.py`: `"--merge", "--match-head-commit"` |
+| merge_train.py | writes | train-hold ref | `tools/audit/seat/merge_train.py`: `git/refs/heads/train-hold` |
+| heartbeat.sh --once | writes | heartbeat ref | `tools/audit/seat/heartbeat.sh`: `"$c:refs/heads/$REF"` |
+
+What the figure leaves out is the reading, because a read moves nothing:
+
+- `tools/audit/seat/orchestrator_tick.py` reads the bus refs, the dispatch
+  refs, the ledger and the pull requests, and prints the board. The
+  orchestrator reads the board file to decide what to dispatch, board or hold.
+- `tools/audit/seat/cloud_relay.sh pass` reads the probe and handoff refs and
+  the hold list. Its probe arm grades a reviewer's `probe/rev-<pr>-<nonce>`
+  ref and posts the verdict through `tools/audit/seat/bus.sh push-verdict`.
+  Its handoff arm updates an open pull request from `handoff/<topic>` and
+  `handoff-body/<topic>`, and leaves a pull request on the hold list alone.
+- `tools/audit/seat/bus.sh` refuses a verdict whose nonce the dispatch record
+  does not hold.
+- `tools/audit/seat/heartbeat.sh --watch` reads the heartbeat ref and prints
+  `HEARTBEAT STALE` when it is old. The owner schedules it off the host; the
+  schedule is not in the tree.
+
+The parts, one by one:
+
+- **Two loops run detached** under `tools/audit/seat/daemonize.py`, and the
+  orchestrator starts both. `tools/audit/seat/tick_loop.sh` runs the relay's
+  pass, the tick, the train's sweep and the heartbeat, in that order.
+  `tools/audit/seat/beatd.py` runs the job table
+  `tools/audit/seat/beatd.jobs.json`, where an unreadable table refuses to
+  start. Its jobs are in `tools/audit/seat/beat_jobs.py`: the figure shows
+  the four that write a store, and the rest report or clean up. No beat job
+  runs the relay, the tick, the train or the heartbeat.
+- **A seat is started by the orchestrator.** `tools/audit/seat/cloud_dispatch.py`
+  publishes the dispatch ref and prints the payload; it starts nothing itself.
 - **The bus refs** are the seats' only channel to the orchestrator: a fixer
-  pushes `handoff/<topic>` and `handoff-body/<topic>`; a cloud reviewer pushes
-  `probe/rev-<pr>-<nonce>`, which `tools/audit/seat/cloud_relay.sh` grades and
-  posts through `tools/audit/seat/bus.sh push-verdict`.
-- **Dispatch records** are written by `tools/audit/seat/cloud_dispatch.py`, one
-  per dispatched seat, and `bus.sh` refuses a verdict whose nonce no record
-  holds.
-- **The merge train**, `tools/audit/seat/merge_train.py`, boards verdicted pull
-  requests at a pitch. The pitch's gap rule keeps a disruptive merge away from
-  a critical-chain pull request about to board; a `train-hold` ref stops the
-  record autofix from merging into a running train.
-- **The relay's hold list** keeps a frozen pull request's head still while its handoff branch moves [target: R10-FLOW-RELAY-HOLD]
+  pushes `handoff/<topic>` and `handoff-body/<topic>`, and a cloud reviewer
+  pushes a probe ref.
+- **A pull request is opened by the opener job**, `tools/audit/seat/open_driver.py`,
+  which launches `tools/audit/seat/open_pr.sh` for a handoff with no pull
+  request. The relay only updates one that is open.
+- **The obligations ledger**, `tools/audit/seat/ledger.py`, keeps two stores,
+  the dispositions and the events, and one derived level file that the relay
+  rewrites every pass. Its `KINDS` table is the list of kinds:
+  - derived, recomputed every pass, among them: `handoff-no-pr`, `handoff-update`, `probe-ref`, `review-owed`, `record-owed`
+  - events, opened and closed: `reviewer-fire`, `verdict-unposted`, `approve-held-runs`, `dispatch`, `train-stop`, `postmerge-owed`
+  - no script opens `train-stop`; the train's sweep reads it and stops while one is open
+- **The merge train**, `tools/audit/seat/merge_train.py`, merges verdicted
+  pull requests one at a time, each at the head SHA its verdict names. A
+  critical-path pull request boards before the record sweep. While a run is
+  live it holds the `train-hold` ref, and the record beat in
+  `.github/workflows/nightly.yml` skips while that ref is fresh.
+- **The relay's hold list** is a file under the state directory, one pull
+  request number per line. Only the orchestrator writes it.
 - **The roster branch**, `handoff/audit-r10-roster`, is written through
-  `tools/audit/seat/roster_edit.py`; `tools/audit/seat/roster_sync.py`, run by
-  the state-documents beat, derives each group's stage from its branch's pull
-  request.
-- **One plan model** feeds the plan page and the plan table, extended by the flow toolkit's projection [target: R10-PLAN-ARTIFACT, R10-FLOW-TOOLKIT-MODEL]
-- **The flow toolkit**'s measuring instruments land under `tools/audit/seat/` for any round [target: R10-FLOW-TOOLKIT-MEASURE]
+  `tools/audit/seat/roster_edit.py`. `tools/audit/seat/roster_queue.py`
+  drains queued edits into it, and `tools/audit/seat/roster_sync.py`, run by
+  the plan beat, derives each group's stage from its branch's pull request.
+- **The plan model** is `tools/plan/replan.py`. The plan beat runs it, then
+  `tools/audit/seat/state_docs.py`, which renders the state documents and
+  calls `tools/audit/seat/plan_page.py` for the plan page.
+- **The flow instruments** measure any round from git and the bus:
+  `tools/audit/seat/flow_metrics.py`, `tools/audit/seat/ci_critpath.py`,
+  `tools/audit/seat/review_strength.py` and `tools/audit/seat/gantt_drift.py`.
 
 ### One handoff's path
 
@@ -317,6 +422,7 @@ sequenceDiagram
     participant DR as design reviewer
     participant F as fixer
     participant B as bus refs
+    participant OP as opener job
     participant RL as relay
     participant RV as fix reviewer
     participant T as merge train
@@ -328,8 +434,8 @@ sequenceDiagram
     O->>B: read the approval back
     O->>F: dispatch the fixer
     F->>B: push handoff/topic and handoff-body/topic
-    Note over B,RL: ledger opens handoff-no-pr
-    RL->>M: open the pull request at the head SHA
+    Note over B,RL: handoff-no-pr opens
+    OP->>M: open the pull request at the head SHA
     Note over RL,M: handoff-no-pr closes, reviewer-fire opens
     O->>RV: dispatch at the reviewable head SHA
     Note over O,RV: reviewer-fire closes
@@ -338,15 +444,17 @@ sequenceDiagram
     RL->>M: post the verdict, then confirm
     Note over RL,M: probe-ref closes, verdict-unposted opens and closes on read-back
     O->>M: read the verdict back
-    O->>T: board at the next pitch
+    O->>T: board the verdicted pull request
     T->>M: merge --match-head-commit
-    Note over T,M: a refusal opens train-stop, record-owed opens on merge
+    Note over T,M: record-owed opens on merge
     O->>M: land the delivery row
     Note over O,M: record-owed closes
     O->>M: stamp the version after the merge
 ```
 
-- The ledger kinds the notes name are `tools/audit/seat/ledger.py`'s [target: R10-ORCH-MACHINERY]
+- The ledger kinds the notes name are keys of `KINDS` in
+  `tools/audit/seat/ledger.py`. A derived kind "opens" when a pass first
+  computes it and "closes" when a pass no longer does.
 - **The reviewable head is a SHA.** A head that moved under a review is a
   blocked verdict, never a re-read: "moved" means the head SHA, not the body
   bytes. `dev/governance/roles/fix-review.md` is the rule.
@@ -361,7 +469,7 @@ sequenceDiagram
 | whether a design is sound | the design reviewer | the orchestrator reads the verdict back before dispatching the fixer |
 | what a fix is and what it proves | the fixer | `tools/pr/prepr.sh` and the scoped gate refuse what is missing |
 | whether a fix merges | the fix reviewer, at one head SHA | `tools/audit/seat/bus.sh` posts it; the relay grades a cloud verdict |
-| when a pull request boards | the orchestrator, at a pitch | `tools/audit/seat/merge_train.py` refuses a head that moved or a red check |
+| when a pull request boards | the orchestrator | `tools/audit/seat/merge_train.py` refuses a head that moved or a red check |
 | a policy change or a budget raise | the owner, by approving review | `budget-raise-gate` and the code-owner rule refuse the merge without it |
 | the ruleset | the owner | read back and diffed after the change |
 | the version | nobody: it is derived | `tools/release/stamp.py`, after the merge |
diff --git a/dev/audit/harnesses/r10_arch_docs_mutants.py b/dev/audit/harnesses/r10_arch_docs_mutants.py
new file mode 100644
index 0000000000..49f8d074b2
--- /dev/null
+++ b/dev/audit/harnesses/r10_arch_docs_mutants.py
@@ -0,0 +1,81 @@
+#!/usr/bin/env python3
+"""R10-ARCH-DOCS (#2395): each predicate line of the machinery-edge and due-marker checks, mutated, against doc_claims.
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_arch_docs_mutants.py
+
+THE RULE. MUTANTS below is one row per predicate of `machinery_edge_findings` and `due_marker_findings` in
+tests/doc_claims.py: the exact source text of the test, and what replaces it so the predicate can never fire. A row
+whose text is not in the file exactly once is an error, not a skip, so a predicate renamed away from its mutant is
+seen. The mutated source is executed in a child with `__file__` set to the real path; nothing is written to the tree.
+A mutant is killed when the child prints a FAIL line or dies. The baseline, unmutated, must print none.
+
+Prints one line per mutant with the checks that failed, then `RESULT baseline_fails=`, `RESULT mutants=` and
+`RESULT killed=`. Exit 1 unless the baseline is clean and every mutant is killed.
+"""
+from __future__ import annotations
+
+import subprocess
+import sys
+from pathlib import Path
+
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+ROOT = repo_root(__file__)
+TARGET = ROOT / "tests" / "doc_claims.py"
+MUTANTS = (
+    ("due marker", 'for r in rows if r["due"] and r["scope"] == "wiring"]', 'for r in rows if False]'),
+    ("verb", "if verb not in MACHINERY_VERBS:", "if False:"),
+    ("store as actor", 'if nodes[a][1] == "store":', "if False:"),
+    ("writes ends at a store", 'elif (verb == "writes") != (nodes[b][1] == "store"):', "elif False:"),
+    ("arrow with no row", "sorted(drawn - cited)]", "()]"),
+    ("row with no arrow", "sorted(cited - drawn)]", "()]"),
+    ("quoted text in the cited file", "elif quote not in src:", "elif False:"),
+    ("cited file tracked", 'if src is None:\n            out.append(f"{a} -{v}-> {b}: cites', 'if False:\n            out.append(f"{a} -{v}-> {b}: cites'),
+    ("cited file is the actor's", 'not in kind[a][1]:', 'not in kind[a][1] and False:'),
+    ("one entry", 'if len(entries) != 1 or kind[entries[0]][0] != "seat":', "if False:"),
+    ("one arrow per line", "if not m or m.group(1) not in nodes or m.group(3) not in nodes:", "if False:"),
+    ("node names unique", "if list(name.values()).count(n) > 1})]", "if False})]"),
+)
+RUNNER = ("import sys; sys.argv = [sys.argv[1]]; sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0]); "
+          "exec(compile(sys.stdin.read(), sys.argv[0], 'exec'), {'__name__': '__main__', '__file__': sys.argv[0]})")
+
+
+def fails(src: str) -> list[str]:
+    r = subprocess.run([sys.executable, "-c", RUNNER, str(TARGET)], input=src, capture_output=True, text=True, cwd=ROOT)
+    out = [line.strip()[5:].split("  [")[0] for line in r.stdout.splitlines() if line.strip().startswith("FAIL ")]
+    return out or ([f"died rc={r.returncode}: {r.stderr.strip().splitlines()[-1][:120]}"] if r.returncode else [])
+
+
+def main() -> int:
+    src = TARGET.read_text()
+    base = fails(src)
+    print(f"baseline: {len(base)} FAIL line(s)")
+    killed = 0
+    for what, old, new in MUTANTS:
+        if src.count(old) != 1:
+            print(f"ERROR {what}: {old!r} is in the file {src.count(old)} time(s), not once")
+            return 2
+        got = fails(src.replace(old, new))
+        killed += bool(got)
+        print(f"{'killed  ' if got else 'SURVIVED'} {what}: {'; '.join(got) or '-'}")
+    print(f"RESULT baseline_fails={len(base)}")
+    print(f"RESULT mutants={len(MUTANTS)}")
+    print(f"RESULT killed={killed}")
+    return 0 if not base and killed == len(MUTANTS) else 1
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/3430.md b/dev/programme/delivery/3430.md
new file mode 100644
index 0000000000..4c4e296d36
--- /dev/null
+++ b/dev/programme/delivery/3430.md
@@ -0,0 +1 @@
+- [#3430](https://github.com/tvofi/heatpump_optimizer/pull/3430) — **open**, R10-ARCH-DOCS: r10 arch docs (R10-ARCH-DOCS)
diff --git a/docs/architecture.md b/docs/architecture.md
index 9dbe1b1a34..3caa1a0187 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -87,7 +87,9 @@ Read the diagram as four regions.
   and the dashboard card. Each is reached through a Home Assistant entity or
   service, never imported.
 - **The Home Assistant boundary** is where side effects live.
-  `inputs.InputReader` performs every entity read;
+  `inputs.InputReader` reads the configured input entities and normalises
+  them, and the coordinator, `pump_arbiter` and `early_cutoff.py` read the
+  pump's own control entities back directly;
   `coordinator.HeatPumpOptimizerCoordinator` is the orchestration seam that
   calls the core and then writes; `pump_arbiter` writes the pump's mode and
   set-points and owns the power switch; `store.QuarantiningStore` is the
@@ -99,7 +101,9 @@ Read the diagram as four regions.
 - **The learners** consume the coordinator's evidence and return corrections.
   Most are pure; three still import `homeassistant` at module level —
   `accuracy` and `defrost` for the clock, `dhw_learning` for the clock and the
-  `HomeAssistant` type — so the glue calls them and they never call the glue.
+  `HomeAssistant` type. The glue calls them and they never call the
+  coordinator; `dhw_learning` and `snapshots` reach persistence through
+  `store.py`.
 
 ## The module map
 
@@ -229,8 +233,9 @@ custom_components/heatpump_optimizer/
 │                         #   Mold Floor Breach, Open Window Detected,
 │                         #   Wood Cheaper Than Heat Pump
 ├── button.py             # Optimize now, run identification, reset comfort
-│                         #   weight, diagnose last interval; finalize the
-│                         #   debug collection while that option is on
+│                         #   weight, reset heat loss, diagnose last interval;
+│                         #   finalize the debug collection while that option
+│                         #   is on
 ├── climate.py            # Virtual climate entity: modes, presets, DHW status
 ├── switch.py             # Away, Block DHW, Block Space Heating,
 │                         #   Boost Space Heating, DHW Boost, Optimizer Active
@@ -368,23 +373,20 @@ These instruments keep this page honest:
   example — reads NULL. It is a review trigger, never a target a seat is
   rewarded for moving, and it is a required check on a pull request.
 
-## The shape at programme end
-
-The page above describes `main`. The round-10 roster still holds groups that
-change the shape of the code, and each change below is marked with the group
-that lands it, so R10-ARCH-DOCS can resolve every line once its group is done.
-No group in the roster adds a module, so the module map above is already the
-module set at programme end.
-
-- **One owner of the thermal parameters**, copied on write, so a service call cannot publish a torn or unclamped set across its await, and the coordinator context is written once [target: R10-PARAMS-OWNER]
-- **The live state published whole**: the thermal state, the away state and the event callbacks publish a copy, and each collaborator owns its own fields [target: R10-LIVESTATE]
-- **One owner per duplicated shape**: a power reader in `inputs` that refuses a non-finite or out-of-range reading, one hour-clock owner and one finite-float owner [target: R10-ARCH-SHAPES]
-- **Payload mixins on the entity base**: the finite scrub, the value and path mixins and the zone set-point attributes, shared by the sensors that each carried their own guard [target: R10-SENSOR-PAYLOAD]
-- **A delivered-heat meter input**: measured COP from heat over electric energy, split into hot water and space by the pump's mode [target: R10-HEAT-METER]
-- **An honest COP state**: "not measurable here" where no meter makes COP observable [target: R10-COP-GATE]
-- **One rule for scores**: no evidence is a dash with a reason, never zero, and one view model behind the scores, Savings, Advisor and Health [target: R10-SCORES]
-- **Learner progress in the payload**: phase, progress and what each learner waits for [target: R10-LEARNER-ETA]
-- **One options page template** driven by the field registry [target: R10-CONFIGFLOW-PAGES]
+## One owner per concern
+
+Each rule below has one owner in the code, so a change to it is made in one
+place.
+
+- **The thermal parameters have one writer.** `coordinator.py` builds a new parameter set and publishes it whole in one assignment, so a service call cannot publish a torn or unclamped set across its await. The coordinator context is a frozen value, replaced whole and never edited.
+- **The live state is published as a copy.** Each cycle owns its own copy of the thermal state, so a restore or an await cannot change the state another reader holds.
+- **One owner per duplicated shape.** The power reader in `inputs.py` converts a reading to kW and refuses a non-finite or out-of-range one. `const.py` owns the finite-float conversion. The hour-of-day conversions are two functions with two rules: `quiet_windows.py` owns the wall clock, where the end of the day is 00:00, and `dhw_schedule.py` owns the window label, where it is 24:00.
+- **One payload read on the entity base.** `entity.py` owns the finite scrub, the payload-number rule and the zone set-point attributes. One mixin in `sensor.py` reads a number at a named path of the payload, for the sensors that each carried their own guard.
+- **A delivered-heat meter input.** An optional heat energy meter gives a measured COP, heat over electric energy. `heat_energy.py` splits a span's heat into hot water and space heating by the pump's mode.
+- **An honest COP state.** `accuracy.py` owns the COP observability state, which reads "not measurable" where no meter makes COP observable.
+- **One rule for scores.** No evidence is a dash with a reason, never zero. One view model in `coordinator.py` is behind the scores and the advisor's restart advice, and it shares one convergence rule with the Health page. No score reads or recomputes a Savings figure.
+- **Learner progress in the payload.** `learner_progress.py` gives each learner's phase, its progress and what it waits for.
+- **One options page template.** `config_flow.py` renders every options page from one field registry.
 
 ## Where to start reading
 
diff --git a/tests/closure.py b/tests/closure.py
index 97e609de19..a7624f1f97 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -746,6 +746,17 @@ INERT_EXCEPT = (
     "tools/audit/seat/bus.sh",
     "tools/audit/seat/cloud_relay.sh",
     "tools/audit/seat/heartbeat.sh",
+    # R10-ARCH-DOCS (#2395): tests/doc_claims.py's machinery_edge_findings opens each file dev/README.md's
+    # machinery table cites, for the quoted text that performs the edge.
+    "tools/audit/seat/beat_jobs.py",
+    "tools/audit/seat/body_push.sh",
+    "tools/audit/seat/cloud_dispatch.py",
+    "tools/audit/seat/instruments/beatd.py.md",
+    "tools/audit/seat/instruments/heartbeat.sh.md",
+    "tools/audit/seat/instruments/tick_loop.sh.md",
+    "tools/audit/seat/open_pr.sh",
+    "tools/audit/seat/roster_queue.py",
+    "tools/audit/seat/tick_loop.sh",
     "DISCLAIMER.md",
     "blueprints/automation/charge_ev_from_grid_headroom.yaml",
     "blueprints/automation/economy_mode_on_price_peak.yaml",
diff --git a/tests/closures.json b/tests/closures.json
index 388f371942..4923a1835e 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1251,6 +1251,7 @@
    "custom_components/heatpump_optimizer/wood_fuel.py",
    "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js",
    "dev/README.md",
+   "dev/governance/roles/nudge.md",
    "dev/programme/rosters/wave-r10-groups.json",
    "docs/architecture.md",
    "docs/automations.md",
@@ -1344,10 +1345,22 @@
    "tools/audit/archscore/metrics/__init__.py",
    "tools/audit/archscore/metrics/card.py",
    "tools/audit/archscore/metrics/common.py",
+   "tools/audit/seat/beat_jobs.py",
+   "tools/audit/seat/body_push.sh",
    "tools/audit/seat/bus.sh",
+   "tools/audit/seat/cloud_dispatch.py",
    "tools/audit/seat/cloud_relay.sh",
    "tools/audit/seat/heartbeat.sh",
+   "tools/audit/seat/instruments/beatd.py.md",
+   "tools/audit/seat/instruments/heartbeat.sh.md",
+   "tools/audit/seat/instruments/tick_loop.sh.md",
    "tools/audit/seat/ledger.py",
+   "tools/audit/seat/merge_train.py",
+   "tools/audit/seat/open_pr.sh",
+   "tools/audit/seat/roster_queue.py",
+   "tools/audit/seat/roster_sync.py",
+   "tools/audit/seat/state_docs.py",
+   "tools/audit/seat/tick_loop.sh",
    "tools/policy/rules_sync.mjs",
    "tools/release/stamp.py",
    "tools/site/build_docs.mjs",
@@ -1890,6 +1903,8 @@
    "tools/audit/round4/D11/d11lib.py",
    "tools/audit/round4/D11/governance_cost.py",
    "tools/audit/seat/bare_array.py",
+   "tools/audit/seat/beat_jobs.py",
+   "tools/audit/seat/cloud_dispatch.py",
    "tools/audit/seat/gh_read.py",
    "tools/audit/seat/handover_prompt.py",
    "tools/audit/seat/ledger.py",
@@ -1905,6 +1920,7 @@
    "tools/audit/seat/resume_doc.py",
    "tools/audit/seat/roster_edit.py",
    "tools/audit/seat/roster_lib.py",
+   "tools/audit/seat/roster_queue.py",
    "tools/audit/seat/roster_sync.py",
    "tools/audit/seat/state_docs.py",
    "tools/audit/seat/tmp_paths.py",
@@ -4064,6 +4080,7 @@
    "dev/audit/harnesses/r10_advisor_residue.py",
    "dev/audit/harnesses/r10_anchor_vacuous.py",
    "dev/audit/harnesses/r10_arch_docs_first_mutants.py",
+   "dev/audit/harnesses/r10_arch_docs_mutants.py",
    "dev/audit/harnesses/r10_archscore_any_spellings.py",
    "dev/audit/harnesses/r10_away_presence_listener.py",
    "dev/audit/harnesses/r10_band_census.py",
@@ -5062,7 +5079,7 @@
    "seconds": 55.0
   },
   "tests/entities.py": {
-   "rc": 1,
+   "rc": 0,
    "seconds": 867.9
   },
   "tests/env_drift.py": {
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 2f0d65cf76..43e72ba828 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -3018,9 +3018,10 @@ def check_image_dimensions() -> None:
 # programme end, so some of what they name is not on main yet. Such an element
 # carries a marker naming the roster group that lands it; the grammar is the
 # approved design note's (dev/programme/designs/R10-ARCH-DOCS-FIRST.md, section 3).
-# Every predicate here holds before and after a named group lands: none reads a
-# group's stage except (c), which only prints. Resolving the markers is
-# R10-ARCH-DOCS's end-of-round check, not this one.
+# The predicates of `doc_wiring_findings` hold before and after a named group
+# lands: none reads a group's stage except (c), which only notes. A marker whose
+# groups are all done is refused by `due_marker_findings` (R10-ARCH-DOCS): the
+# page then states the tree, or is corrected where the landed shape differs.
 
 WIRING_DOCS = ("docs/architecture.md", "README.md", "dev/README.md")
 # The user pages R10-USER-DOCS-FINAL drafts and R10-USER-DOCS-VERIFY re-checks. README.md is in both sets.
@@ -3246,6 +3247,82 @@ def marker_placement_findings(rows: list[dict]) -> list[str]:
     return out
 
 
+def due_marker_findings(rows: list[dict]) -> list[str]:
+    """A wiring marker whose every group is done describes the tree as still to come (R10-ARCH-DOCS, #2395). A
+    user-doc marker is R10-USER-DOCS-VERIFY's (`--markers --user`), and is left to it."""
+    return [f"{r['doc']}:{r['line']}: {r['marker']} names only done groups; state the tree and drop the marker"
+            for r in rows if r["due"] and r["scope"] == "wiring"]
+
+
+# The machinery figure's edges (owner direction, tvofi 2026-10-22). The figure under MACHINERY_HEADING draws one
+# labelled arrow per line, actor to target, and the table under it cites the code performing each. The table is the
+# registry, kept on the page it describes: no edge list lives here.
+MACHINERY_DOC = "dev/README.md"
+MACHINERY_HEADING = "### Its components"
+MACHINERY_VERBS = ("runs", "writes")
+_M_NODE = re.compile(r'^\s*([A-Za-z_]\w*)(\(\[|\[\(|\[)"([^"]*)"', re.M)
+_M_EDGE = re.compile(r'^\s*([A-Za-z_]\w*)\s*-->\|"([^"]*)"\|\s*([A-Za-z_]\w*)\s*$')
+_M_ARROW = re.compile(r"-{2,}>|-\.+->|={2,}>|---|~~~|--[ox]")
+_M_ROW = re.compile(r"^\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|\s*`([^`\n]+)`: `([^`\n]+)`\s*\|\s*$", re.M)
+_M_KIND = {"([": "seat", "[(": "store", "[": "script"}
+
+
+def machinery_edge_findings(text: str, read) -> list[str]:
+    """What the machinery figure draws against the code its table cites. `read(path)` is a tracked file's text or None.
+
+    An arrow means the actor runs or writes its target, so: every arrow is one labelled line with a verb of
+    MACHINERY_VERBS; none starts at a store, `writes` ends at a store and `runs` does not; the arrows and the
+    table's rows are the same set, which is what refuses a reversed arrow; a row's quoted text is in the file it
+    cites, and a script actor's cited file is one its node names, which refuses a row reversed with its arrow; and
+    the figure has one entry, a seat nothing points at. A node is named by its label's first line."""
+    at = text.find(MACHINERY_HEADING + "\n")
+    if at < 0:
+        return [f"no {MACHINERY_HEADING!r} section"]
+    body = text[at + len(MACHINERY_HEADING):]
+    nxt = re.search(r"^#{1,3} ", body, re.M)
+    section = body[:nxt.start()] if nxt else body
+    fig = next((b for i, b in _FENCE.findall(section) if i.strip() == "mermaid"), None)
+    rows = [(a.strip(), v.strip(), b.strip(), f, q) for a, v, b, f, q in _M_ROW.findall(_FENCE.sub("", section))]
+    if fig is None or not rows:
+        return [f"{MACHINERY_HEADING!r} draws no figure" if fig is None else f"{MACHINERY_HEADING!r} cites no code"]
+    nodes = {i: (label.split("<br/>")[0].strip(), _M_KIND[shape], label) for i, shape, label in _M_NODE.findall(fig)}
+    name = {i: n for i, (n, _, _) in nodes.items()}
+    out = [f"two nodes are named {n!r}" for n in sorted({n for n in name.values() if list(name.values()).count(n) > 1})]
+    drawn: set[tuple[str, str, str]] = set()
+    for line in fig.splitlines():
+        if not _M_ARROW.search(re.sub(r'"[^"]*"', '""', line)):  # a label's `--once` is no arrow
+            continue
+        m = _M_EDGE.match(line)
+        if not m or m.group(1) not in nodes or m.group(3) not in nodes:
+            out.append(f"not one labelled arrow between two declared nodes: {line.strip()!r}")
+            continue
+        a, verb, b = m.group(1), m.group(2), m.group(3)
+        edge = f"{name[a]} -{verb}-> {name[b]}"
+        if verb not in MACHINERY_VERBS:
+            out.append(f"{edge}: the verb is not one of {', '.join(MACHINERY_VERBS)}")
+        if nodes[a][1] == "store":
+            out.append(f"{edge}: starts at a store, and a store does nothing")
+        elif (verb == "writes") != (nodes[b][1] == "store"):
+            out.append(f"{edge}: `writes` ends at a store and `runs` at an actor")
+        drawn.add((name[a], verb, name[b]))
+    cited = {(a, v, b) for a, v, b, _, _ in rows}
+    out += [f"{a} -{v}-> {b}: drawn, and no row cites the code that performs it" for a, v, b in sorted(drawn - cited)]
+    out += [f"{a} -{v}-> {b}: cited in the table and not drawn" for a, v, b in sorted(cited - drawn)]
+    kind = {n: (k, label) for n, k, label in nodes.values()}
+    for a, v, b, path, quote in rows:
+        src = read(path)
+        if src is None:
+            out.append(f"{a} -{v}-> {b}: cites `{path}`, which is not a tracked file")
+        elif quote not in src:
+            out.append(f"{a} -{v}-> {b}: `{path}` no longer holds {quote!r}")
+        if kind.get(a, ("", ""))[0] == "script" and path.rsplit("/", 1)[-1] not in kind[a][1]:
+            out.append(f"{a} -{v}-> {b}: cites `{path}`, which is not a file the actor's node names")
+    entries = sorted(n for i, n in name.items() if nodes[i][1] != "store" and all(b != n for _, _, b in drawn))
+    if len(entries) != 1 or kind[entries[0]][0] != "seat":
+        out.append(f"the figure has one entry, a seat nothing points at; it has {entries}")
+    return out
+
+
 # (f)-(i): what the architecture page and the onboarding name beyond a path -- a command's arguments, a module's
 # symbols, a workflow job, a ledger kind, a diagram node -- each resolved in the artifact that defines it (fixer.md
 # step 11), never in a list kept here. Read from these two only: README.md names the user's own files
@@ -3525,8 +3602,7 @@ def check_doc_wiring() -> None:
     errs, notes = doc_wiring_findings(docs, tree, roster_stages, style)
     blocks = sum(1 for t in docs.values() for i, _ in _FENCE.findall(t) if i.strip() == "mermaid")
     marks = sum(len(_MARKER.findall(t)) for t in docs.values())
-    R.check("the marked documents draw mermaid blocks and carry markers (anchor)", blocks > 0 and marks > 0,
-            f"{blocks} block(s), {marks} marker(s)")
+    R.check("the marked documents draw mermaid blocks (anchor)", blocks > 0, f"{blocks} block(s), {marks} marker(s)")
     R.check("every path resolves or is marked, every marker names a roster group, every block is well formed",
             not errs, "; ".join(errs[:4]) + (f" (+{len(errs) - 4})" if len(errs) > 4 else ""))
     for n in notes:
@@ -3645,8 +3721,9 @@ def check_marker_census() -> None:
     docs = marker_docs()
     stages = roster_stages()
     rows = marker_census(docs, stages or {})
+    # no `> 0`: the end state of the round is a tree with no marker, and the fixtures below are the non-vacuity
     R.check("the resolver reads every marker in the wiring documents and the user pages, README.md once (anchor)",
-            len(rows) == sum(len(_MARKER.findall(re.sub(r"`[^`\n]+`", "", t))) for t in docs.values()) > 0
+            len(rows) == sum(len(_MARKER.findall(re.sub(r"`[^`\n]+`", "", t))) for t in docs.values())
             and set(docs) == set(WIRING_DOCS) | set(USER_PAGES), str(len(rows)))
     wiring = [r for r in rows if r["scope"] == "wiring"]
     print(f"       ({sum(r['due'] for r in wiring)} of {len(wiring)} wiring marker(s) name only done groups: "
@@ -3654,6 +3731,9 @@ def check_marker_census() -> None:
           f"{len(rows) - len(wiring)} user-doc marker(s): --markers --user)")
     bad = marker_placement_findings(rows) if stages is not None else []
     R.check("every marker sits on a page of its scope and names a roster group", not bad, "; ".join(bad[:4]))
+    due = due_marker_findings(rows)
+    R.check("no wiring marker names only done groups: each is resolved into a statement of the tree (#2395)",
+            not due, "; ".join(due[:4]) + (f" (+{len(due) - 4})" if len(due) > 4 else ""))
     readme = "# T\n\n- `a.py` lands [target: R10-A]\n\n| Row | Cell <!-- [target: R10-B] --> |\n"
     tagged = marker_census({"README.md": readme}, {"R10-A": "not-started", "R10-B": "done"})
     R.check("null control: a README with one wiring and one wrapped marker gives one row of each scope",
@@ -3671,10 +3751,75 @@ def check_marker_census() -> None:
     R.check("null control: a marker naming a not-started group is listed and not due; a quoted one is not a marker",
             [(r["line"], r["due"]) for r in null] == [(3, False)], repr(null))
     R.check("red fixture: a marker naming a done group is due", [r["due"] for r in red] == [True], repr(red))
+    R.check("red fixture: a due wiring marker is refused, and a not-yet-due one is not (null control)",
+            len(due_marker_findings(red)) == 1 and not due_marker_findings(null) and not due_marker_findings(both),
+            repr((due_marker_findings(red), due_marker_findings(null))))
+    wrapped = marker_census({"README.md": "# T\n\n| Row | Cell <!-- [target: R10-B] --> |\n"}, stub)
+    R.check("a due user-doc marker is left to its own resolver (null control)",
+            [r["due"] for r in wrapped] == [True] and not due_marker_findings(wrapped), repr(wrapped))
     R.check("a marker naming a done and a not-started group is not due until both land", [r["due"] for r in both] == [False],
             repr(both))
 
 
+def check_machinery_edges() -> None:
+    R.section("the machinery figure: every arrow runs from its actor, with the code that performs it (#2395)")
+    tree = _tracked()
+    text = (ROOT / MACHINERY_DOC).read_text()
+    errs = machinery_edge_findings(text, _read_tracked(tree))
+    R.check("every arrow is cited, every citation holds in the tree, and the figure has one entry", not errs,
+            "; ".join(errs[:4]) + (f" (+{len(errs) - 4})" if len(errs) > 4 else ""))
+
+    files = {"t/loop.sh": 'bash "$relay" pass\nmv "$tmp" "$out"\n', "t/relay.sh": "push_verdict\n",
+             "t/role.md": "the orchestrator starts the loop\n"}
+    base = (MACHINERY_HEADING + "\n\n```mermaid\nflowchart TB\n"
+            '    orch(["orchestrator<br/>a person"])\n    subgraph actors["actors"]\n        loop["loop.sh"]\n'
+            '        relay["relay.sh pass<br/>two arms"]\n    end\n    board[("board file")]\n    bus[("bus refs")]\n'
+            '    orch -->|"runs"| loop\n    loop -->|"runs"| relay\n    loop -->|"writes"| board\n'
+            '    relay -->|"writes"| bus\n```\n\n'
+            "| actor | verb | target | performed at |\n|---|---|---|---|\n"
+            "| orchestrator | runs | loop.sh | `t/role.md`: `the orchestrator starts the loop` |\n"
+            '| loop.sh | runs | relay.sh pass | `t/loop.sh`: `bash "$relay" pass` |\n'
+            '| loop.sh | writes | board file | `t/loop.sh`: `mv "$tmp" "$out"` |\n'
+            "| relay.sh pass | writes | bus refs | `t/relay.sh`: `push_verdict` |\n\n### Next\n\n| a | b | c | `x`: `y` |\n")
+    clean = machinery_edge_findings(base, files.get)
+    R.check("the clean fixture yields no finding (null control)", not clean, repr(clean))
+    row = '| loop.sh | runs | relay.sh pass | `t/loop.sh`: `bash "$relay" pass` |'
+    plants = (
+        ("one arrow reversed", ('loop -->|"runs"| relay', 'relay -->|"runs"| loop'), "no row cites"),
+        ("an arrow reversed together with its row",
+         ('loop -->|"runs"| relay', 'relay -->|"runs"| loop', row, row.replace("| loop.sh | runs | relay.sh pass |",
+                                                                              "| relay.sh pass | runs | loop.sh |")),
+         "not a file the actor's node names"),
+        ("a store drawn as the actor (is read by)", ('loop -->|"writes"| board', 'board -->|"writes"| loop'), "starts at a store"),
+        ("a verb that is not runs or writes", ('relay -->|"writes"| bus', 'relay -->|"reads"| bus'), "the verb"),
+        ("writes ending at an actor", ('loop -->|"runs"| relay', 'loop -->|"writes"| relay'), "ends at a store"),
+        ("an unlabelled arrow", ('loop -->|"runs"| relay', "loop --> relay"), "not one labelled arrow"),
+        ("a dashed arrow", ('loop -->|"runs"| relay', 'loop -.->|"runs"| relay'), "not one labelled arrow"),
+        ("a row with no arrow", ('    relay -->|"writes"| bus\n', ""), "not drawn"),
+        ("a cited line the code no longer holds", ("`push_verdict`", "`post_verdict`"), "no longer holds"),
+        ("a cited file that is not tracked", ("`t/relay.sh`", "`t/relax.sh`"), "not a tracked file"),
+        ("an actor nothing starts, a second entry", ('    orch -->|"runs"| loop\n', ""), "one entry"),
+        ("two nodes of one name", ('relay["relay.sh pass<br/>two arms"]', 'relay["loop.sh<br/>two arms"]'), "two nodes"),
+        ("a table whose rows cite nothing", ("`: `", "` `"), "cites no code"),
+        ("no figure", ("```mermaid", "```text"), "draws no figure"),
+        ("no section", (MACHINERY_HEADING, "### Its parts"), "section"),
+    )
+    for what, swaps, key in plants:
+        doc = base
+        for old, new_ in zip(swaps[::2], swaps[1::2]):
+            doc = doc.replace(old, new_)
+        got = machinery_edge_findings(doc, files.get)
+        R.check(f"red fixture: {what} is a finding", doc != base and any(key in g for g in got), repr(got))
+    # the page's own figure: reversing any one of its arrows is refused (the owner's null control, on the real figure)
+    arrows = [m.group(0) for m in re.finditer(r'^    \w+ -->\|"\w+"\| \w+$', text, re.M)]
+    live = 0
+    for a in arrows:
+        s, lab, d = re.match(r'    (\w+) (-->\|"\w+"\|) (\w+)', a).groups()
+        live += bool(machinery_edge_findings(text.replace(a, f"    {d} {lab} {s}", 1), _read_tracked(tree)))
+    R.check("reversing any one arrow of the page's figure is a finding (anchor: the figure has arrows)",
+            not errs and arrows and live == len(arrows), f"{live} of {len(arrows)}")
+
+
 def print_marker_census(argv: list[str]) -> int:
     """`--markers [--roster FILE]`: every wiring marker, its groups' stages, and what each due one still leaves
     unresolved; exit 1 while any is due. `--markers --user`: only the comment-wrapped user-doc markers, ending
@@ -4475,6 +4620,7 @@ def main() -> int:
     check_doc_wiring()
     check_named_elements()
     check_marker_census()
+    check_machinery_edges()
     check_card_figures()
     check_coffee_button()
     check_readme_marketplace()

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
