# BLOCKED: r10-outside-first at ed1f1b1d

`python3 -I tools/plan/replan.py --self-test` fails on the merge of this head with origin/main
(and on refs/pull/3304/merge), at the fixture in tools/plan/replan.py whose label begins
"dispatch follows the owner's order (tvofi 2026-11-07, triage P420)" (about line 665):
seq is ['CPA','CPB','CPC','R10-HOTFIX-H','OUT','PROD','HI','LO','NONE'], wanted hotfix, outside, then CP.
Cause: main's build_plan starts a ready critical-path group at once over the slots cap, so with slots=1 the
CP groups share t0 with the hotfix and outside groups and sort first. Head alone and main alone both pass.
Needs a code repair (tier-order the simultaneous starts, or the overflow pick), outside this body-only task.
