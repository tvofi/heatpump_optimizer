# R11-INTAKE-R10-RESIDUE: the carries, triaged (revision 4)

`architect-planner.md` step 3, owed since design `af8f7048ad` stopped and its verdict `89755fd4a7`
sent the group here. The carries are the open ones of the group's row on
`handoff/audit-r10-roster` at `c7e683a6d4`, by 0-based index: a carry is open when it ends in
neither a `[moved` nor a `[dismissed` tag. `INTAKE-TRIAGE.json` is the same table for a script.

41 open carries: 6 kept and re-homed in round 11, 5 merged into a carry of the same root,
26 deferred to round 12, 2 refused as group work, 2 dismissed.

Rules applied:

- An instrument carry is deferred under card P11's freeze, into the deferred `R11-CARRY-*` group
  that owns its file. One owes an in-round overlay (carry 157).
- A product carry goes to the seam group that owns its file when that group is not started. A
  group with an open pull request takes no new scope, so such a carry is deferred.
- A carry deferred to round 12 with no deferred owner stays on this group, which becomes
  `deferred`: it is round 12's architect input and holds no round-11 work.
- A decision or act the carry itself gives the orchestrator or the owner is not a group's work.

| carry | verdict | to | reason |
|---|---|---|---|
| 0 | defer | `R11-CARRY-MERGE-TRAIN` | instrument, under the freeze of card P11; the cancel path and the bounded pause are the merge train's seam |
| 19 | defer | `R11-INTAKE-R10-RESIDUE` | the control needs a recorded full price day, which the tree does not hold and no seat can fetch; round 12, D0's harness input |
| 27 | merge | `R11-CARRY-MERGE-TRAIN` | same root as carry 0: enabling priority_cancel waits on that carry's after measure |
| 29 | defer | `R11-INTAKE-R10-RESIDUE` | states the precondition a future settling-tail formula must meet and owes no change now; round 12, D2's input (boost.py is R11-SEAM-store's file, and that group's findings do not touch the tail) |
| 30 | defer | `R11-CARRY-PREDICT` | instrument, under the freeze of card P11; prepr.sh, policy_lint.mjs and ci_predict are that group's files |
| 64 | defer | `R11-CARRY-LOOP-POLICY` | an owner's choice between two barriers (root-cause record section 6), not a seat's build; round-end proposal triage |
| 69 | defer | `R11-CARRY-MERGE-TRAIN` | instrument, under the freeze of card P11; a count owed by the seat holding the train logs |
| 71 | defer | `R11-CARRY-LOOP-POLICY` | issue 3369 owes a keying change, a vocabulary ruling or a recorded refusal: root-cause.md's decision at round-end triage |
| 91 | keep | `R11-SEAM-docs` | docs/img/ is that group's seam and it is not started; the re-take is owed by the host that recorded the figures, so its fixer raises it and does not re-record |
| 94 | dismiss | none | records a control that is built (the nightly faketime step) and a refusal already measured; it owes nothing |
| 110 | defer | `R11-INTAKE-R10-RESIDUE` | a recount design (route (b) of a blocked question) across the coordinator's split, heat_energy and dhw_planner, with no finding in the round-11 register; round 12, D2's input |
| 118 | keep | `R11-SEAM-tests` | the owner's ruling of 2026-11-14 puts these test gaps in round 11; they are pins, with no shape to design, so they ride the fixer's brief and not the design |
| 124 | defer | `R11-CARRY-FIXER-CONTRACT` | role-contract friction (designer.md: unenforced); round-end proposal triage |
| 128 | defer | `R11-CARRY-PREDICT` | instrument, under the freeze of card P11; tools/policy linter seam (brief_lint.mjs joins that group's files) |
| 133 | defer | `R11-CARRY-PREDICT` | instrument, under the freeze of card P11; brief_lint.mjs resolves no group id; same seam as carry 128 |
| 153 | defer | `R11-CARRY-FIXER-CONTRACT` | fixer.md friction line whose own instance is answered; round-end proposal triage |
| 154 | defer | `R11-CARRY-LOOP-POLICY` | design-review.md friction line whose own instance is answered; round-end proposal triage |
| 155 | defer | `R11-CARRY-LOOP-POLICY` | finding-propagation.md friction line; round-end proposal triage |
| 156 | defer | `R11-CARRY-MACHINERY-CHECK` | instrument, under the freeze of card P11; review_packet.py is that group's file |
| 157 | defer | `R11-CARRY-FIXER-CONTRACT` | instrument, under the freeze of card P11; mutant_run.py is that group's file. It owes the in-round overlay now: a mutation proof run with `python3 -I` adds `-B` to its command, because `-I` drops PYTHONDONTWRITEBYTECODE and two equal-length mutants inside one second share a .pyc |
| 159 | defer | `R11-CARRY-BEAT-RECORD` | instrument, under the freeze of card P11; the record-autofix automerge path against the ruling of 2026-11-15 |
| 163 | defer | `R11-CARRY-TICK-OWED` | instrument, under the freeze of card P11; two more parsers of the stamp owed_watch.fired owns |
| 165 | keep | `R11-SEAM-learners` | the inferred defrost derate folds accuracy.delivered_ratio, that group's file, and learns 0.684 against a control of 1.000 on a pump that sets its own power; the group is not started and already follows R11-SEAM-plant-model, which owns defrost.py |
| 166 | defer | `R11-CARRY-PREDICT` | instrument, under the freeze of card P11; prepr's cold-run reads |
| 167 | merge | `R11-SEAM-learners` | same finding as carry 165: it reports that the control carry 165 asks for now exists |
| 168 | dismiss | none | overtaken: `python3 -I tools/audit/product_reads.py --self-test` exits 0 at main 8751943e17 (86 arms) |
| 169 | keep | `R11-READS-RESIDUE` | the population levels of both axes, a read objective.json records as owed; card E11-N-INTAKE-BUILDER |
| 170 | keep | `R11-READS-RESIDUE` | the committed operation seed ledger is refused by its own reader; card E11-N-INTAKE-BUILDER |
| 171 | keep | `R11-OUTSIDE-HONEST-DHW-RUNS` | runs.py is that group's seam; a later part of it, never its open pull request 3709 |
| 172 | refuse | none | an orchestrator act (three live checks on a test fork with an App key), not a group's work; it goes to the orchestrator's own list in the handover |
| 173 | defer | `R11-CARRY-LOOP-LEDGER` | instrument, under the freeze of card P11; loop_ledger.gate_reds |
| 174 | merge | `R11-CARRY-LOOP-LEDGER` | a pointer to carry 173's four departures, which await the orchestrator's ruling |
| 175 | defer | `R11-CARRY-LOOP-LEDGER` | instrument, under the freeze of card P11; a stated limit of the same instrument |
| 176 | defer | `R11-INTAKE-R10-RESIDUE` | 86 cell-only declarations each owe a reason or a loader; tests/finite_boundary.py has no in-round owner whose design is still open; round 12, D3's input |
| 177 | defer | `R11-INTAKE-R10-RESIDUE` | a decision the carry gives the orchestrator, cost measured first; optimizer.py's two groups have open pull requests (3736, 3738), so it does not join them; round 12, D0's input unless that decision lands sooner |
| 178 | merge | none | same three live checks as carry 172 |
| 179 | refuse | none | an orchestrator decision (how a merge result reaches pull request 3529), not a group's work; the orchestrator's own list |
| 180 | defer | `R11-CARRY-LOOP-POLICY` | finding-propagation.md friction line; round-end proposal triage |
| 181 | merge | `R11-INTAKE-R10-RESIDUE` | measured residue of the same unbuilt part as carry 182 |
| 182 | defer | `R11-INTAKE-R10-RESIDUE` | the heat-ask dither and the closed-loop harness are a new design group by the orchestrator's ruling; its round and priority are the owner's, and this plan cuts no outside-contributor group |
| 183 | defer | `R11-CARRY-TOOLCHAIN` | instrument, under the freeze of card P11; replay_draws.py against gh 2.104; a round-end proposal |

The controls each receiving seat re-runs are in the carry's own text, re-measured at its merge base.
Verdict notes of `89755fd4a7`: `dr1-dup-163-164` is already tagged on the roster at `c7e683a6d4`;
`dr1-files-tick` is carry 159, the one open carry naming `orchestrator_tick.py`, which goes to
`R11-CARRY-BEAT-RECORD` with the automerge path it reports. After this table the group's `files`
name no carry it holds; the orchestrator empties them with the re-homing.
