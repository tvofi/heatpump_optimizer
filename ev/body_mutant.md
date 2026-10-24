Adds `dev/programme/triage/s6-batch18.md`: one ruling, P87 (S6-V22, a dispatch row commit on a triage PR stales its body's Head), under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took.

Verdict: P87 ACCEPT (no code). The fix goes into the orchestrator's triage-seat and dispatch-seat briefs: a PR's own row goes through the existing `tools/audit/seat/update_pr.sh <branch> - <body>`, which commits the row through `delivery_row.sh` and writes the matching `## Head` note in the same `--row-only` push. The three instances (#2755, #2758, #2759) were triage PRs opened by a bare `app_push.sh` whose row was then added without that note. A new tool path (candidate a) is unneeded. Writing the row before the open (candidate b) is REJECTED, because the row needs the PR number.

## Head

`69efb1cbbde94c5a414f60f3d31ae0616f05907a` merges origin/main `0810d5b8f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2763.md`.

`69efb1cbbde94c5a414f60f3d31ae0616f05907a`, on merge base `0810d5b8f`.

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads the one entry (P87 -> ACCEPT).

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P99`) returns None. The ruling carries no roster carry, so there is nothing for brief_lint to check; its destination is the orchestrator's out-of-tree dispatch prompts.

## Figures

- Entries and verdicts: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch18.md | sort | uniq -c` (1 ACCEPT).

## Red checks

none

## Forward-carry

n/a: the destination is two lines in the orchestrator's triage-seat and dispatch-seat briefs, not a roster group.

## Friction

none
