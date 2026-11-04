Fix review: blocked e966fb701366ccee185b0d9d8d315262eb082e03 figures-uncited: the measured arms and the calibration finding are read at 4fff42664, a commit no ref carries

bus-nonce: 047f9a669d19f469f1c35b240c95ac11

Round 1. Head measured: e966fb701366ccee185b0d9d8d315262eb082e03 (ev/HEAD.txt).

## Block
proposal-triage.md requires each `Instances:` figure beside its command or log, "cite, don't carry". The ruling reads its arm table (R 1.03 to 7.70), the `+44 -8` / `+3 -1` / `+14 -2` marker cost and the "metered half the plan gives 50.0 %" finding at fix-seat commit `4fff42664`. That object does not exist on origin (ev/checks.txt: `git cat-file -t 4fff42664` fatal; zero commits match in `git log --all`). The only pushed hotfix ref is `wip/r10-hotfix-sav-estimate` at 88697cf19, which measures ledger.py +51 -9, notifier.py +6 -0, payload.py +3 -1, card +14 -2: not the quoted sizes. The arm figures cite "run files" with no command.

The sharper problem is the hotfix carry. The pushed 88697cf19 `savings_months` already floors calibration at 1.0 when wood is configured ("scaling down by it would cancel wood's heat from the saving"). The carry says calibration cancels the meter on wood houses and tells the hotfix to add a metered-below-plan arm and decide whether calibration stays; at the pushed head that is partly decided. The cancellation still holds without wood, which bears on the floor's design (it reads booked lines either way). The ruling must say which commit its finding is about, and restate the carry against what is pushed.

To clear: re-read the facts at pushed refs (88697cf19, d8eeae8f8), put each command beside its figure, and restate the hotfix carry against the wood floor already there.

## Findings
- Residual: the ACCEPT's benefit is bounded by its own text at about 1.1 h per release, with a floor that catches 1 of 3 measured instances and R 0.63 passing; it rests on the class-barrier duty, not on the "clearly outweighs" bar. Acceptable under defect-root-cause.md only if the barrier claim stands, so the re-cut should state the cost test with both sides as numbers. Carry: dismissed: the ruling itself names the barrier duty and the owner's reading of the bar is the orchestrator's call
- Residual: R10-SAV-METER-FLOOR is introduced by this ruling and exists in no roster yet (wave-r10-groups.json on handoff/audit-r10-roster has R10-HOTFIX-SAV-ESTIMATE and R10-RCA-SAV-ESTIMATE only). It is created by the orchestrator's roster_edit.py after approval, which is the contract's route. Carry: dismissed: ruling's destination is a new group, which proposal-triage.md allows

## Evidence
- Setup RESULT: cloud-setup check OK; roles dir diff against main: empty.
- RESULT: git merge-tree --write-tree origin/main head exits 0 (no conflict).
- RESULT: review packet: carry_audit 0 findings; figure_lint 0 resolved, 1 not verified, 0 refused; no refusals.
- RESULT: diff is two new files (triage record and delivery row 3212); no VERSION, manifest, budget, golden or claim file touched; no production code, so no mutation or both-ends run applies.
- RESULT: R10-RCA-SAV-ESTIMATE.md at d8eeae8f8 prints 0.18 for 2026-11, 6.8 h per release, "about zero"; the ruling's quotes of those match. The export ratios (3.295, 0.719, 0.188) are not re-derivable from the tree.
- RESULT: merge_train classify on this head: WAIT (gate pending, "gate red: none") at last poll; no red seen. Not judged green.
