Triage batch 61 rules V189 (the dispatch gate measures the wrong quantity) as P286. It is the next rolling batch under V182, after batch 60 (#2958, merged as `20c205158`).
- **P286 (V189, `pr_cap.py dispatch-gate` counts groups, while the owner's cap counts open pull requests): ACCEPT, as a new fly-in R10-FLY-PR-CAP-COUNT, with a carry on R10-FLOW-WIP.**
  - On 2026-10-29 the owner restated the rule as a soft cap of 6-10 open pull requests. It gates only a new group's dispatch.
  - The gate's docstring still encodes the 2026-10-20 ruling. `dispatch_gate` refuses on `wip_groups`, the count of roster groups `in-progress` (`WIP_STAGE`, `WIP_CAP_DEFAULT = 6`). The open-PR count (`counted`) is only printed. The tick's line `WIP: N/6 (open PRs M)` (`orchestrator_tick.py:607-608`) and its self-test (`:3688`) pin the same rule. `orchestrator.md` section 5 (`:96-99`) and both instrument notes state it.
  - The fix makes the gate count open PRs with `counted`. The soft cap is `HPO_WIP_CAP` (default 6) and the hard cap is a new env var (default 10).
    - Below the soft cap, the gate passes.
    - From the soft cap to the hard cap, it refuses unless `--over-cap` gives a reason.
    - At or above the hard cap, it refuses unless the reason begins `critical path:`, which keeps section 5's critical-path exemption.
    - An unread PR list refuses. Groups in progress stay on the line as information. Opening is never refused.
  - Section 5 is policy, so it merges on tvofi's approving review or under mandate 6329234399.
  - R10-FLOW-WIP gets a carry: build its lanes on the open-PR quantity, with lane figures as information.
  - Two held roster ops (`append-group R10-FLY-PR-CAP-COUNT`, `append-carry R10-FLOW-WIP`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`1f4d5fd60b7d626f0667e3bac00e668ed398d0d7`; the file is the whole diff against `ce5940c0d1d8f611a818d53e7fffcafb48b356c1`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P286 as `ACCEPT`. `triage_refusal` passes the new group's brief and resume note and the R10-FLOW-WIP carry text (it returns None).
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same texts are refused: `dev/programme/triage/s6-batch61.md#P286 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the same texts return `the triage ruling dev/programme/triage/s6-batch61.md is not on the roster branch or origin/main`. That is what the real dry run of both held ops printed before this push.

## Figures

- The group and the carry were linted by appending them to a copy of the roster at the `handoff/audit-r10-roster` tip. The only error is the group's citation of this not-yet-merged file (`not in the tree`), which clears on merge. There are two warnings, for line-only citations in the tick.
- `git grep -n 'dispatch-gate\|HPO_WIP_CAP'` outside `pr_cap.py` finds `orchestrator.md:97-98,105`, `instruments/pr_cap.py.md:3,6,13`, `instruments/orchestrator_tick.py.md:37` and `orchestrator_tick.py:590,592,3691-3699`. These are the fly-in's files.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
