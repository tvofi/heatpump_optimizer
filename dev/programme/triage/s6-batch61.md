# Proposal triage, session s7, batch 61 (P286-P287)

The rolling batch (V182) after batch 60 (#2958, merged as
`20c205158ec465bd37e65ed1b847f4589b173a73`). Facts were read at origin/main
`ce5940c0d1d8f611a818d53e7fffcafb48b356c1`.

## P286: the dispatch gate counts groups, while the owner's cap counts open pull requests

Verdict: ACCEPT, as a new fly-in, R10-FLY-PR-CAP-COUNT. R10-FLOW-WIP, which owns this seam's
lane design, gets a carry so that it builds on the new quantity rather than the old one.

Source: `proposals.md` V189 (orchestrator, 2026-10-29). The owner restated the rule on
2026-10-29: a soft cap of 6-10 open pull requests, which gates only the dispatch of a new group
and never refuses work already in flight. The gate printed "WIP 11/6" while 12 pull requests
were open. The orchestrator reported that figure to the owner as the cap, and the owner
corrected it.

Instances:
- **The gate counts the wrong thing.** `tools/audit/seat/pr_cap.py` encodes the 2026-10-20
  ruling in its docstring, "moving 2026-10-18's open-PR cap". `wip_groups` counts roster groups
  whose `resume.stage` is `in-progress` (`WIP_STAGE`, `WIP_CAP_DEFAULT = 6`). `dispatch_gate`
  refuses on that count. The open-PR count from `counted` is only printed by `info`.
- **The tick reports the same figure.** `orchestrator_tick.py` prints `WIP: N/6 (open PRs M)`
  (`:607-608`), with N taken from `wip_groups`. Its self-test pins the old rule: "A board far
  over the old open cap, and a roster at 5: WIP does not move" (`:3688`).
- **Policy states the old rule.** `dev/governance/roles/orchestrator.md` section 5 (`:96-99`)
  says the gate "counts roster `in-progress` groups and refuses at `HPO_WIP_CAP`". The
  instrument notes `tools/audit/seat/instruments/pr_cap.py.md` and `orchestrator_tick.py.md`
  repeat it.
- **The two counts diverge in both directions.** A group left `in-progress` after its pull
  request merged is a phantom slot (R10-FLOW-WIP's STALE-SLOT carry). A fly-in or record pull
  request that no group owns is invisible to the group count.

Cost and benefit: the cost is one S-sized instrument change plus one policy paragraph. The
benefit is that every dispatch decision and every cap figure reported to the owner uses the
quantity the owner named. Today, each wrong figure either refuses a dispatch the rule allows or
allows one it would refuse.

Accepted: `dispatch-gate` counts open pull requests with `counted`, the rule `info` already
uses. The soft cap is `HPO_WIP_CAP` (default 6) and the hard cap is a new env var (default 10).
The gate behaves by band:
- Below the soft cap, it passes.
- From the soft cap up to the hard cap, it refuses unless `--over-cap "<reason>"` is given.
- At or above the hard cap, it refuses unless the reason begins `critical path:`. That keeps
  section 5's standing exemption, under which a ready critical-path group starts regardless of
  every cap.

An open-PR list that cannot be read is a refusal, never a clean zero. The in-progress group
count stays on the line as information. The gate applies only to dispatching a new group;
opening or updating a pull request is never refused, as now.

The tick's line becomes `CAP: open PRs M/6 soft, 10 hard (WIP groups N)`. Section 5's first
bullet and both instrument notes are rewritten to the new rule. Section 5 is policy, so it
merges on the owner's approving review or under mandate 6329234399.

Controls:
- 11 groups in progress with 5 open PRs passes.
- 11 open PRs without `--over-cap` refuses.
- 7 open PRs with a non-critical-path reason passes.
- 11 open PRs with that same reason refuses.
- 11 open PRs with `critical path: G` passes.
- An unread PR list refuses.
- Mutation: replacing the open-PR count with `wip_groups` fails the first two arms.
- Null control: `open_pr` with 20 open PRs is still not refused (`pr_cap.py:290-291`).

The tick's self-test arm at `:3688` is inverted, not deleted.

Not built: lane caps, orphan-handoff counting and the ranked `next` list. Those stay with
R10-FLOW-WIP, which lands after this fly-in on the same two files.

## P287: a handoff preflight should catch paperwork blocks before a reviewer is owed

Verdict: ACCEPT, narrowed to one check, as a carry on R10-FLY-CARRY-DISPOSITION: `body_push.sh`
runs that group's accepted `carry_audit.py landed` check at the handoff. The proposed packet run
in `handoff_push.sh` and `update_pr.sh` is REJECTED, because the handoff-time packet already
exists, and the measured blocks it would catch are mostly not paperwork.

Source: `proposals.md` V190 (orchestrator, 2026-10-29). It says about half of today's review
rounds blocked on paperwork the packet could have caught at handoff: a carry not landed (#2961,
#2925), a body not answering a red (#2953, #2954, #2963 nightly), `## Unpinned sites` missing
(SAV-ACTUATION), and a handoff ref not an ancestor of the head (#2962).

Instances:
- **The handoff-time packet exists.** `tools/audit/seat/body_push.sh` already runs before the
  body is pushed, so before any open:
  - `prepr.sh --fill-red` and `prepr.sh --body-check`, the pr-body lint;
  - the carry audit;
  - `review_packet.py handoff` (P256), with refusals `structure`, `hot-file` and
    `brief-carries`.
  `handoff_push.sh` is the orchestrator's opener, which runs after the fixer's push.
  `update_pr.sh` already runs prepr unless the push is exactly the PR's row (its header,
  `:19-20`). A second packet run in either place re-runs checks the fixer's own push already ran.
- **The blocks, counted.** The `verdict/*` refs hold 15 `Fix review: blocked` verdicts
  committed on 2026-10-29 local time. By class: class-open 3, carry-missing 3,
  class-rule-missing 2, ci-red 2, mutation 3 (survivor, survivors, vacuous), merge-conflict 1,
  ci-unconcluded 1. Paperwork a static check could catch is 2 of them, not half.
- **Two carry-missing blocks are mechanical.** #2961 (`carry-missing: not carried to
  R10-FLY-LEDGER-SAMPLE`) and #2946 round 1 (`not carried to R10-ROUND-PLAYBOOK or
  R10-ARCH-SHAPES-CLASSIFIER`) each named a live group whose roster carry was not there.
  `tools/audit/carry_audit.py` routes an item that names an open group (`Dests.check`) and never
  reads whether the text landed. That is exactly R10-FLY-CARRY-DISPOSITION's first carry
  (`carry_audit.py landed`, CARRY-MISSING lines, rc 1, `bus.sh dispatch` refuses). P66 measured
  24 of 33 carry-family blocks in that shape. The group is `not-started`, and its one `after`
  group, R10-FLY-ORPHANS-REWRITTEN, is `done`. So it is ready to dispatch.
- **The third carry-missing block is judgement.** #2925 round 6 blocked on three restoring jobs
  that the record names as open and the body routes nowhere. No body item names them, so no
  marker check sees them.
- **The nightly refusals were dispatch refusals, not review rounds.** #2953, #2954 and #2963 are
  the packet's main-graded `nightly-status` refusal (P282, P285). R10-FLY-PACKET-RED-PATHS
  (`in-progress`) removes them by passing the diff's paths. At the handoff no PR exists, so no PR
  red can be read.
- **The remaining two instances are not what V190 says.** #2962's verdict is `blocked
  mutation-survivor: dropping --existing-file from unanswered_reds passes the self-test`, not
  handoff-not-applied, and its ref holds no other verdict. The SAV-ACTUATION instance has no
  verdict ref to read. `prepr.sh`'s step 6d already refuses a missing `## Unpinned sites`
  (`:615-618`), and body_push's `--body-check` runs that step.

Cost and benefit: the accepted check is one subcommand call in `body_push.sh`, beside the packet
call, once the group builds `landed`. It moves 2 of today's 15 blocks to before the open, about
one review round each. The rejected mechanism would add a packet run to the opener and to every
update for a measured gain of zero beyond that.

Accepted, as a carry on R10-FLY-CARRY-DISPOSITION: `body_push.sh` runs `carry_audit.py landed` on
the body at the round roster's branch, beside `review_packet.py handoff`, and refuses on rc 1 with
the CARRY-MISSING lines. Like the packet call, an unreadable roster (rc 3) is reported and not
treated as a refusal. Control: the #2961 body against roster `e9e3f93d2` refuses with
R10-FLY-LEDGER-SAMPLE named. The same body, against a roster copy holding that carry, passes.
Mutation: routing on the group name alone (today's check) passes the #2961 body. Null control:
a body whose only routes are `dismissed:` passes unchanged.

Priority, for the orchestrator: R10-FLY-CARRY-DISPOSITION is ready to dispatch now. This ruling
does not ask to open the batch early. The carry is held with the batch, and the group's own first
carry already specifies the check.
