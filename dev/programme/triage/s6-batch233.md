# Proposal triage, session s14, batch 233

Source: the R10-BODY-CONTRACT fixer's stop record (handoff-wip/r10-body-contract 78133e8ac2,
BLOCKED.md) and two proposal candidates from the orchestrator's sweep log (2026-11-12T05:01Z and
05:17Z). Line numbers are at origin/main 2ced371c1a. Rulings are the orchestrator's under mandate
6715477401 (scope all), made by triage s14-41.

## P704: R10-BODY-CONTRACT carry 38 (Card 7 ruling, figure blocks) is already on main

Verdict: NO-OP
Scope: R10-BODY-CONTRACT carry 38, the only carry of the group not yet marked.
Evidence: 8124343607 is an ancestor of origin/main; tools/pr/figure_block.py and
tools/pr/figure_registry.json are in the tree; .github/workflows/pr-contract.yml:370-375 runs
figure_lint.mjs on the body and re-renders generated figure blocks from the base's registry;
tools/policy/figure_lint.mjs and tools/policy/policy_lint.mjs carry the figure checks. The fixer's
stop record names the same files.
Disposition: mark carry 38 implemented at 8124343607cea8683983bf5e1005e4b27f55d502. With it, all 45
carries of R10-BODY-CONTRACT are marked, so the group is set done at that SHA. No new work.

## P705: a cloud fixer cannot read the owed-red text its body is refused on

Verdict: ACCEPT
Scope: tools/audit/seat/cloud_dispatch.py (the fixer and repair text it renders) and
tools/audit/seat/cloud_relay.sh (the arm that relays a stop back to the seat).
Evidence: body_push.sh:128 runs tools/pr/ci_predict.py, which predicts red while a red check is
still owed an answer (ci_predict.py:1409). A cloud seat has no gh, so it cannot read that check's
failure text and cannot write the answer; the body stays refused. Hotfix #3487 stalled 45 minutes
until a local seat repaired the body (sweep log 05:01Z). Carry 0 of the destination already makes a
body_push refusal the same seat's to repair; this one it cannot repair without the text.
Destination and severity: carry on R10-RELAY-NOBODY-STALL (not-started; owns cloud_relay.sh,
cloud_dispatch.py and body_push.sh), normal. Figure against 20%: one occurrence, 45 minutes on a
critical-path hotfix plus a local seat; cloud is the fixer majority, so every owed red on a cloud
PR repeats it. Fix cost is small: the relay, which has gh, fetches the owed check's failure summary
and hands it to the seat in the repair message (or the dispatch embeds it), so the benefit clears.
Fix shape: when the predictor refusal names an owed red, the relay attaches that check run's name,
conclusion and failure excerpt to the seat's next message. Control: a refusal with no owed red adds
no text.

## P706: carry_fold and the roster drain race on the roster push

Verdict: ACCEPT
Scope: the roster branch's write path, tools/audit/seat/roster_edit.py (push loop :1174) as used by
the roster-drain beat job (tools/audit/seat/beat_jobs.py:339) and by tools/audit/seat/carry_fold.py.
Evidence: both write through roster_edit.py --push and share no lock; carry_fold lost the push race
3 times in 3 tries against a 21-op drain, and the hotfix #3487 body stalled 15 minutes until the
drain was SIGSTOPped by hand (sweep log 05:17Z). A stopped drain that is not resumed halts every
roster op, so the workaround carries its own risk.
Destination and severity: carry on R10-TICK-RESIDUE-P3 (not-started; owns beat_jobs.py and the
roster-drain row), normal. Figure against 20%: one occurrence, 15 minutes on a critical-path body
and a manual signal to the drain; it recurs whenever a fold lands during a long drain. Fix cost is
small: the drain takes a lease in HPO_STATE_DIR per op and yields between ops while an out-of-queue
writer holds it (or carry_fold enqueues at the head of the queue and waits for its line), so the
benefit clears. The fixer chooses between the two by which keeps one writer of record; the lease
touches roster_edit.py, which the fixer adds to the group's files.
Control: a drain pass with no fold pending runs unchanged.
