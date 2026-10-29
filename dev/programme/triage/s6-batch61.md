# Proposal triage, session s7, batch 61 (P286)

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
