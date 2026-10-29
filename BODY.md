Triage batch 61 rules V189 (the dispatch gate measures the wrong quantity) as P286, V190 (a handoff preflight before a reviewer is owed) as P287, and V191 (a returned handoff shows as held, not owed) as P288. It is the next rolling batch under V182, after batch 60 (#2958, merged as `20c205158`).
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

- **P287 (V190, a handoff preflight should catch paperwork blocks): ACCEPT, narrowed, as a carry on R10-FLY-CARRY-DISPOSITION. The packet run in `handoff_push.sh` and `update_pr.sh` is REJECTED.**
  - `body_push.sh` already runs before every open: `prepr.sh --fill-red`, `--body-check`, the carry audit and `review_packet.py handoff` (P256: `structure`, `hot-file`, `brief-carries`). `handoff_push.sh` is the orchestrator's opener, which runs after the fixer's push, and `update_pr.sh` runs prepr (`:19-20`).
  - 15 `Fix review: blocked` verdicts were committed on 2026-10-29: class-open 3, carry-missing 3, class-rule-missing 2, ci-red 2, mutation 3, merge-conflict 1, ci-unconcluded 1. Of these, 2 are paperwork a static check catches, not half.
  - Those 2 are #2961 and #2946 round 1: a named live group whose roster carry had not landed. `carry_audit.py` routes on the group name alone (`Dests.check`). R10-FLY-CARRY-DISPOSITION's first carry already specifies `carry_audit.py landed`, and its `after` group is done, so it is ready to dispatch. The carry adds the same check to `body_push.sh` at the handoff.
  - The rest of V190's instances: #2925 round 6 is judgement, because no body item names the open jobs. The nightly refusals (#2953, #2954, #2963) were dispatch refusals that R10-FLY-PACKET-RED-PATHS removes. #2962's verdict is `mutation-survivor`, not handoff-not-applied. The SAV-ACTUATION instance has no verdict ref, and prepr step 6d already refuses a missing `## Unpinned sites` (`:615-618`).
  - One held roster op (`append-carry R10-FLY-CARRY-DISPOSITION`), released once this file is on main.

- **P288 (V191, a returned handoff shows as held, not owed): ACCEPT, re-aimed, as a new fly-in R10-FLY-RELAY-FREEZE-REGISTRY plus a carry on R10-FLOW-BODY-ONLY. The tick's commit-time comparison is REJECTED.**
  - #2953 was a false review freeze. `cloud_relay.sh`'s `review_freeze` counts any detached worktree at the head as a review, and the opener's own worktree sits there. The relay printed `HELD-REVIEW #2953` on 44 passes from 17:07Z, and `bus.sh`'s dispatch record holds no #2953 line.
  - Of the 7 PRs the live relay log ever held as REVIEW, 4 had no dispatch record at that head: #2896 (9 passes), #2916 (56), #2933 (6) and #2953 (44). 10 `fix/*` tips on origin have a detached opener or updater worktree at the tip right now.
  - The fly-in holds a handoff only on a dispatch record, which `review_freeze`'s own comment calls the worker registry. Its HELD-REVIEW line names the dispatch nonce and time. The self-test's worktree arm (`:892-895`) is inverted.
  - #2872 was a body-only handoff (`handoff-body` at 17:38:52Z, code equal to the head), which `handoff_arm` skips in silence. The carry on R10-FLOW-BODY-ONLY owes a level line until the body-only update lands.
  - #2962 was applied at 18:49:37Z and dispatched at 18:51:24Z. Its wait was `OWED reviewer-fire`, which was already printed.
  - Two held roster ops (`append-group R10-FLY-RELAY-FREEZE-REGISTRY`, `append-carry R10-FLOW-BODY-ONLY`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`b46e95475dd00459c035fd22ca5fcf4335b88f98`; the file is the whole diff against `ce5940c0d1d8f611a818d53e7fffcafb48b356c1`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P286, P287 and P288 as `ACCEPT`. `triage_refusal` passes the new group's brief and resume note, the R10-FLOW-WIP carry text the R10-FLY-CARRY-DISPOSITION carry text, the R10-FLY-RELAY-FREEZE-REGISTRY brief and note, and the R10-FLOW-BODY-ONLY carry text (it returns None).
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same texts are refused: `dev/programme/triage/s6-batch61.md#P286 is not an ACCEPT ruling (REJECT)`, and likewise `#P287` and `#P288` for their texts.

## Null control

- With the file absent, the same texts return `the triage ruling dev/programme/triage/s6-batch61.md is not on the roster branch or origin/main`. That is what the real dry run of both held ops printed before this push.

## Figures

- The group and the carry were linted by appending them to a copy of the roster at the `handoff/audit-r10-roster` tip. The only error is the group's citation of this not-yet-merged file (`not in the tree`), which clears on merge. There are two warnings, for line-only citations in the tick.
- `git grep -n 'dispatch-gate\|HPO_WIP_CAP'` outside `pr_cap.py` finds `orchestrator.md:97-98,105`, `instruments/pr_cap.py.md:3,6,13`, `instruments/orchestrator_tick.py.md:37` and `orchestrator_tick.py:590,592,3691-3699`. These are the fly-in's files.

- P287: `git fetch origin '+refs/heads/verdict/*:...'`, then `git log --since=2026-10-29T00:00 --format='%cI %s'` over every verdict ref. That gives 50 verdict commits, 15 of them `Fix review: blocked`, classed by the word after the head SHA. #2962's ref holds one verdict, `mutation-survivor`.
- P287's carry was linted on a copy of the roster at the `handoff/audit-r10-roster` tip, with the carry added to R10-FLY-CARRY-DISPOSITION: `TOTAL: 0 error(s)`.
- P288: `grep -oE 'HELD-REVIEW #N <tip> (head <sha>'` over the live relay log, deduplicated, with each (PR, head) looked up in `bus.sh`'s `dispatched` record. Held with no record at that head: #2896, #2916, #2933, #2953. Held with one: #2899, #2932, #2939. `git worktree list --porcelain` detached heads joined with `git ls-remote origin 'refs/heads/fix/*'` give 10 matches, all opener or updater worktrees under a `pr/` state directory.
- P288's group and carry were linted on a copy of the roster at the `handoff/audit-r10-roster` tip: `TOTAL: 0 error(s)`, with two line-only-citation warnings.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
