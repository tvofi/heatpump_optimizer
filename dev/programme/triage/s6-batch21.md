# Proposal triage, session s6, batch 21 (P97-)

Rulings from the s6 `proposals.md`, collected 4 or 5 to a pull request under
tvofi's batching rule of 2026-10-24 (one PR per ruling only when it unblocks
critical-path work). Numbering continues after `s6-batch20.md` (P93-P96, #2782,
unmerged at this base).

## P97: restarting a standing seat leaves its predecessor running (S6-V31)
Verdict: ACCEPT, in two parts.
- (a) No code, effective now: a restart stops the predecessor first. Before starting a replacement standing seat, the orchestrator runs `TaskStop` on the predecessor's task id, which is harmless if that seat has already ended. It then logs one line in the seat ledger: `<role> w<old> <old id> stopped (<TaskStop result>) -> w<new> <new id>`. A notice reading "completed ... waiting on its own background work" never counts as ended.
- (b) Carry into R10-ORCH-BEATD's `--seat-alive` arm (P46, where P93 already deferred the seat-queue reading). Each seat touches an alive entry keyed by its own seat id, and `tools/audit/seat/pulse.py` prints `DUPLICATE seat <role>` when two ids of one role are fresh inside the stale window.
Source: s6 `proposals.md` `## V31`; the orchestrator's seat ledger, 2026-10-25, entries 00:51Z to 01:00Z.
Instances: 4 in one night: tick w14 beside w15, roster w12 beside w13, merge w7 beside w8, and dispatch w22 beside w23. The dispatch pair pushed duplicate reviewer-pool entries for #2765 and #2767, which then had to be removed by hand. This is the third or later instance of a class already known to the orchestrator: a "completed" notice for a seat whose own background job is still live is false. So a barrier is owed, not a note.
Measured on main:
- Each restart rule says only that a seat which is "absent, or finished with ... owed, is restarted on the same queue" (`dev/governance/roles/standing-dispatch.md`, the same wording in the merge, roster and tick contracts). The sweep's step (1b) in `tools/audit/seat/sweep_template.md` restarts a seat "absent from" the ledger or "finished with work still owed". None of these says to stop the predecessor, or what "finished" means when the harness notice is ambiguous.
- `pulse.py` has no seat-identity input: `--seat-queue SEAT=FILE[:MIN]` reads a queue file, and the alive files are per role (for example `dispatch.alive`), so two seats of one role touch the same file and cannot be told apart.
Cost:
- (a) One tool call per restart and one ledger line, with no code. `TaskStop` is a harness tool, which no in-tree script can call, so this is a step for the restarting session, not a script.
- (b) One entry per seat id beside the per-role file, and one count in pulse's seat-alive read, inside an arm R10-ORCH-BEATD already builds. Its test is two fresh ids of one role giving DUPLICATE, with one fresh id as the null control.
- The cost of not doing this: four doubled seats in one night, each polling GitHub twice. One doubled dispatch seat wrote shared state (pool entries), which cost a cleanup pass and could have dispatched two reviewers to one head.
Binding: (a) closes the cause at the one place a seat is started, at the price of one call. (b) is the detector for the case (a) misses, such as a restart by a session that skipped the step, and it costs almost nothing inside an arm already planned. A guard against duplicate pool writes is REJECTED for now: the pool is outside the tree, both duplicates came from one doubled seat, and (a) and (b) remove that source.
What would change the answer: a duplicate seat after (a) is in the briefs, which would make it a skipped step (a review finding on that restart). Or duplicate pool writes from two legitimately distinct seats, which would make the pool guard worth building.
Carry text (b) (for `roster_edit.py append-carry R10-ORCH-BEATD`, citing `triage: dev/programme/triage/s6-batch21.md#P97`): "In the `--seat-alive` arm of tools/audit/seat/pulse.py, read standing-seat liveness from one alive entry per seat id under each role, beside the per-role file, and print 'DUPLICATE seat <role>: <id> <id>' when two ids of one role are fresh inside the stale window. Step (1b) of tools/audit/seat/sweep_template.md then stops the older id before anything else, and logs both ids. Self-test: two fresh ids of one role give DUPLICATE; the null control, one fresh id plus one stale id, gives no DUPLICATE. Mutation proof: deleting the count fails the two-fresh case. Basis: on 2026-10-25 four standing-seat restarts (tick, roster, merge, dispatch) left the predecessor running, and the doubled dispatch seat pushed duplicate reviewer-pool entries for #2765 and #2767."

## P98: carry_audit reads the roster of a stale checkout (S6-V32)
Verdict: ACCEPT NARROWED -> R10-FLOW-ROSTER-FREEZE arm (b2), after arm (b) (P89, #2779). With no `--roster-ref`, when the checkout's HEAD does not contain `origin/main`, `tools/audit/carry_audit.py` reads the roster at `origin/main` instead of the tree, and prints a `NOTE stale tree` line naming both commits. A checkout that contains main, such as CI's pull-request merge checkout, keeps reading its own tree, so a PR's own new group still counts.
- REJECTED: defaulting `--roster-ref` to `origin/main` always. In CI that drops the groups a pull request's own roster edits add.
- REJECTED: having `merge_train.py` pass an explicit ref. It fixes one caller and leaves every seat that runs the check bare.
Source: s6 `proposals.md` `## V32`.
Instances: 2.
- An earlier round-10 occurrence, recorded by the orchestrator.
- 2026-10-25 about 01:45Z: `carry_audit` reported BAD-DEST on #2770 and #2772 for groups that exist on `origin/main`, because the checkout it ran from is a detached tree 387 commits behind `origin/main` when measured. With `--roster-ref origin/main`, #2772 is clean.
Measured on main:
- `load_dests` with no ref reads `roster_lib.load_roster_file` from the checkout's own tree, so the answer depends on which tree runs it.
- Arm (b) is #2779 (branch `fix/r10-roster-freeze-b-r2`), with a merge verdict at 72ee6a18. It adds the round's roster branch (`roster_lib.round_ref`) as a second source.
- The round branch usually carries main's groups, but `roster_lib.default_roster_ref` itself warns when main carries roster changes the branch has not merged. So arm (b) alone does not close the stale-tree case: a group that reached main directly is still missing from a stale tree and from an unmerged round branch.
Cost:
- One `git merge-base --is-ancestor origin/main HEAD` and, when it fails, one `roster_lib.show_roster` at `origin/main`, inside the `load_dests` arm (b) already edits.
- One self-test case: a scratch clone whose tree lags `origin/main`, and a carry to a group only on `origin/main`, which passes with the NOTE. The null control is a group on neither, which is still BAD-DEST.
- The cost of not doing it: each instance costs a seat a re-run with a hand-chosen ref, and one could block a merge or send a body back on a false BAD-DEST.
Binding: two instances with one cause, the tree as the default source of truth for a shared roster. The fix belongs where the default is chosen, at the cost of one ancestry check, in the `load_dests` arm (b) edits.
Routing: arm (b2) of R10-FLOW-ROSTER-FREEZE, cut on main after #2779 merges. #2779 (arm (b)) has a merge verdict at 72ee6a18 and is first in train s26, so its head is not moved. The orchestrator carries this text into the group once this batch merges.
What would change the answer: a stale-tree BAD-DEST from a checkout that contains `origin/main`. That would mean the round branch, not the tree, lags, which is `roster_lib.default_roster_ref`'s warning case and R10-FLOW-ROSTER-FREEZE's to settle.
Carry text (for `roster_edit.py append-carry R10-FLOW-ROSTER-FREEZE`, citing `triage: dev/programme/triage/s6-batch21.md#P98`): "Arm (b2), cut on main after arm (b) (#2779) merges: in tools/audit/carry_audit.py `load_dests`, with no --roster-ref, test whether the checkout's HEAD contains origin/main (`git merge-base --is-ancestor origin/main HEAD`). If it does not, read the roster at origin/main through roster_lib.show_roster instead of the tree, and print 'NOTE stale tree: <HEAD> lacks origin/main <sha>; roster read at origin/main'. A checkout that contains origin/main, such as CI's pull-request merge checkout, keeps its own tree, so a pull request's own new group still counts. Keep the round-ref union that arm (b) adds. Self-test: in a scratch clone built through tests/throwaway_git.py, a tree behind origin/main and a carry to a group only on origin/main passes with the NOTE; the null control, a group on neither, is BAD-DEST. Mutation proof: removing the ancestry test fails the stale-tree case. Basis: on 2026-10-25 carry_audit reported BAD-DEST on #2770 and #2772 for groups that exist on origin/main, read from a detached checkout 387 commits behind; with --roster-ref origin/main, #2772 is clean. This is the second instance."

## P99: a main merge leaves a PR's structure-ratchet gain unrecorded (S6-V33)
Verdict: DEFER. Re-rule when a third pull request is blocked on exit 2 from `tests/structure.py` after a merge of main, with a recorded wall-clock or round cost. Until then the one-command repair stands: the fixer runs `python3 tests/structure.py --record` and says in the commit message which rows moved and why.
Source: s6 `proposals.md` `## V33`.
Instances: 2, one blocked and one held.
- #2753 at bafbef69, blocked by reviewer d641e9fe: `class_excess_loc` 18195 and `max_class_loc` 8435 against recorded budgets 18202 and 8442 after #2698's -7 landed on main.
- #2712 at 0b03e095: the same budget-base move, held. Both are as the orchestrator reported them; the cost figure ("a full fixer+review round per hit") is not measured in any log I read.
Measured on main:
- `tools/merge/ledger_merge.py` documents that when both sides move a count, the result is base plus both deltas, and that a key both sides changed to the same value takes it. Two independent gains that happen to land on the same number therefore collapse into one, and the PR's measured gain reads as unrecorded. That is a coincidence of values, not a defect in the sum rule.
- `tests/structure.py` exits 2 for this state on purpose. The text at its `record_budgets` and improvement branch says a budget is re-recorded "deliberately, on a clean tree, with the reason in the COMMIT". An automatic re-record by `merge_main_bot.py` or `update_pr.sh` would reverse that design. Neither script mentions the structure ratchet today.
- Narrowing the cause to "same value takes it" would let the bot fix only the case where the merged tree measures better than the merged budget. That is the only case exit 2 reports, so the narrowing buys nothing over a plain exit-2 handler.
Cost of the proposal:
- A new autofix job: a structure.py run per merge-main (a full measurement, minutes of CPU and one more runner job, unmeasured here); a bot commit that the reviewer's head-freeze rule treats as a moved head; and policy text in `ci-autofix.md`, the fourth job after the three it names.
- The commit message must carry the per-row reason, so the bot must generate it, which is the part the ratchet deliberately leaves to a human.
Cost of not doing it: one `--record` plus a re-review of one head when it happens, on two instances so far.
Binding: an unmeasured benefit is DEFER, never ACCEPT. Two instances and no timing leave the trade unproven, and the proposal reverses a deliberate design choice of the ratchet. The cheaper alternative is to let `prepr.sh`, which fixers re-run after any merge, print the `--record` command on exit 2; it already does.
What would change the answer: a third instance, or a measurement that the repair costs more than one fixer turn. Then the bot job is worth costing against the `ci-autofix.md` precedent.

## P100: bus.sh dispatch forces seat commits onto Dependabot branches (S6-V34)
Verdict: ACCEPT NARROWED -> R10-FLY-CARRY-DISPOSITION (the group whose carries already edit `bus.sh`: P66, P76). In `bus.sh dispatch`, when every commit in `origin/main..<head>` is authored by `dependabot[bot]`, check the delivery row at `origin/main:dev/programme/delivery/<pr>.md` instead of at the head. All other heads keep the head-carries-its-row test unchanged.
- REJECTED: reading the row from origin/main for every head. It would undo #1990 class E, where a row that lands after the verdict moves the head.
- REJECTED: detecting the author through the GitHub API. The commit authors are in git, and the audit seats spare the API.
Source: s6 `proposals.md` `## V34`.
Instances: 2, both as the orchestrator reported them; I did not open the PRs.
- #2773: dispatch w26 added a merge commit and a delivery row (78672bb, 558fcd6) to the Dependabot branch, and pr-contract and the gate went red.
- #2678: the same trap.
Measured on main:
- `bus.sh dispatch` (line 377) dies unless `git cat-file -e "$h:dev/programme/delivery/<pr>.md"` succeeds. A Dependabot head can never carry that row, so the seat is pushed to write it onto the bot branch.
- `tools/policy/dependabot_contract.mjs` refuses any branch commit not authored by `dependabot[bot]` and committed by `web-flow`. So the one path `dispatch` leaves open is the one the contract forbids. The two checks contradict each other for this class of PR.
- The reason for the head-carries-row rule (a row written after the verdict moves the head) does not apply here: a Dependabot head is never moved by the seat, so a row on main cannot stale it.
Cost:
- About ten lines in the `dispatch` arm: one `git log --format=%an origin/main..$h`, an all-bot test, and a second `git cat-file -e origin/main:$row`.
- Two self-test cases in `bus.sh`'s existing throwaway repo: a bot-only head with the row on main passes; the null control, a bot head with the row nowhere, is still refused, and a mixed head (one human commit) still needs its own row.
- No API calls and no standing CPU.
- The row for a Dependabot PR must still land on main through a record PR. That path exists and is what the V34 text proposes.
- The cost of not doing it: each instance turns two CI checks red on a PR the contract exists to keep green, plus a cleanup of seat commits that the Dependabot branch must lose (a force-reset by the bot's rebase).
Binding: two instances with one cause, a check that contradicts another policy check, fixed in about ten lines with a null control. The narrowing keeps the ordering guarantee for every seat-authored head.
What would change the answer: a Dependabot PR whose row on main still cannot be written before dispatch. That would make the record-PR path the blocker, which is a different item.
Carry text (for `roster_edit.py append-carry R10-FLY-CARRY-DISPOSITION`, citing `triage: dev/programme/triage/s6-batch21.md#P100`): "In tools/audit/seat/bus.sh `dispatch`, before the head-carries-its-delivery-row die, test whether every commit in `origin/main..<head>` has author `dependabot[bot]` (git log --format=%an, no API call). If so, require the row at `origin/main:dev/programme/delivery/<pr>.md` instead of at the head; any other head keeps the existing test. Self-test in the bus.sh throwaway repo: a bot-only head with the row on origin/main passes; the null control, a bot-only head with the row nowhere, is refused; a head with one non-bot commit and the row only on origin/main is refused. Mutation proof: dropping the all-bot test fails the mixed-head case. Basis: on 2026-10-25 dispatch w26 added a merge commit and a delivery row to #2773 (78672bb, 558fcd6), turning pr-contract and the gate red against tools/policy/dependabot_contract.mjs; #2678 is the same trap."
