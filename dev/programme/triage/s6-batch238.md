# Proposal triage, session s14, batch 238

Source: owner rulings (tvofi, about 2026-11-12T07:35Z), recorded, not weighed (P714-P716); one
orchestrator request to discharge an idle group (P717). Ruling recorded by triage s14-60.

Owner ruling, verbatim (typos his; "baikanfan"/"bankaifan" is the contributor Bankaifan; "love"
reads "move"): "Implement a mechanism that allow baikanfans PRs to be accepted as is as long as
they follow all our conventions and rules and have a valid merge verdict (the reviewer may also be
run by bankaifan). Merges with main and codeowner approvals remain in our machinery even for such
PRs. The difference from today is that baikanfan may run the fixer-reviewer cycles themselves.
Also, for the rest of the round, non critical outside PRs can be folded into the plan of they do
not love the programme closure eta. If they do, that are planned for round 11. It is critical the
catalog pr and programme closure is ready 15/11 or sooner"

## P714: outside-contributor fixer and review cycle (the mechanism)

Verdict: ACCEPT
Basis: the owner ruling above, first and second sentences. Destination: a new group,
R10-OUTSIDE-CONTRIBUTOR-CYCLE, size L, lane IN, source outside, design first under decision 0014.
Today a fork pull request is rebuilt by our fixer as an hpo-author pull request: pr-contract
refuses any other author (0011), verdicts post only through bus.sh confirm as hpo-approver (0013),
and tools/pr/app_approve.sh takes a verdict only from an allowlisted account. Wanted: an
allowlisted contributor's fork pull request is admitted unchanged when every required check and the
body contract pass at its head and a valid "Fix review: merge <head>" verdict exists for that head,
which the contributor's own reviewer seat may produce; merge of main, code-owner approval, the
train and the record stay ours. The brief lists what the design must decide. No after-edges; it
shares tools/audit/seat/merge_train.py with R10-GATE-DEFER-BARRIER (critical path) and must not
take it ahead of that group. Severity medium. Figure against 20%: not applicable (owner ruling).

## P715: the fold rule for outside work, rest of round 10

Verdict: ACCEPT
Basis: the owner ruling above, third and fourth sentences. Rule: for the rest of round 10 a
non-critical outside request is planned into round 10 only if it does not move the programme
closure ETA; if it does, it is planned for round 11. A critical one (a defect a user is hitting
now) is exempt. Applied against plan-live.json generated 2026-11-12T07:27Z (closure
2026-11-15T05:43Z); a group finishing after about 2026-11-14T12:00Z moves closure. Planned
finishes: SUPPLY-MIN-RUN-PAUSE 11-13T22:29, LEARNER-ROBUSTNESS-P2 11-13T21:51, START-COUNTER-EDGES
and MODE-BEFORE-SUPPLY-ON 11-14T04:49, RESTART-LEARNING-PR-B 11-14T05:53, PLANNER-PRICE
11-14T06:02, DHW-START-HYSTERESIS 11-14T11:04 (round 10); DISINFECTION-STEP-NOTICE 11-14T18:23,
LEARNER-ROBUSTNESS-P3 11-15T00:23, OUTSIDE-CONTRIBUTOR-CYCLE unplanned, L with design (round 11).
None sits on an after-edge path into R10-ROUND-PLAYBOOK-FINAL or closeout; none but P714's group
shares a file with a critical-path group. Stage changes are the orchestrator's to order.
A round-11 group is recorded as P709 did: an append-carry on R10-ROUND-PLAYBOOK-FINAL adding the
item to dev/audit/README.md's round-11 opening plan carries, then set-stage <group> deferred.

## P716: closure and the catalog pull request by 2026-11-15 outrank outside work

Verdict: ACCEPT
Basis: the owner ruling above, last sentence. Programme closure and R10-CATALOG-PR are critical
and must be ready by 2026-11-15; they outrank every non-critical outside group. R10-CATALOG-PR's
after-edges (USER-DOCS-VERIFY, ARCH-DOCS, ROUND-PLAYBOOK-FINAL, CLOSEOUT-CLEANUP, CLOSEOUT-PREP,
ARCH-DOCS-DELTA) hold every closeout predecessor; no edge is missing, so no roster op. The plan
puts it post-closure (start 11-15T07:43Z, finish 11-16T07:27Z), past the date: the orchestrator's.

## P717: R10-HOTFIX-REPLAY-CLASS-CUT discharged by #3477

Verdict: ACCEPT
Its one carry (0-based 0; #3477 body "Carry 1"), the RCA countermeasure, is built at merge
4f3b94fb53: level_shift_offenders in tests/replay.py, the replay_cuts arm in
tools/policy/field_coverage.mjs, dev/audit/rca/R10-RCA-REPLAY-CLASS-RERECORD.md, all on
origin/main. Mark it implemented at the merge and set the group done.
