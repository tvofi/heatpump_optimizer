# Proposal triage, session s10, batch 116 (P378)

The rolling batch after batch 115. Facts were read at origin/main `b8e823699`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`efd37113a`), from GitHub's pull-request files,
and in the session's seat ledger and the dispatch seat's fire ledger and handoffs. The owner was
re-read at roster `a62d10eb0`, after the s11 replan folded R10-TICK-PR-BUCKETS.

## P378: the dispatch seat lists already-fired payloads as fire-owed

Verdict: DEFER (LOG, by the owner's 2026-11-01 ~19:50Z rule). The item is already owned: the
FIRE-OWED tick level of R10-TICK-LEVELS (the carry opening "Three owed classes", item 3), with the
payload-file key that the carry citing `s6-batch115.md#P375` applies to it. No carry, no group and
no policy edit. The answer changes if R10-TICK-LEVELS closes without building the FIRE-OWED level
with its payload-file arm, or if a false
fire-owed line holds a pull request that touches `custom_components/`.

Source: the orchestrator s10's message of 2026-11-02, about 20:30Z, a slip from that day's
sweeps. It proposes one line in `dev/governance/roles/standing-dispatch.md`: before reporting a
payload fire-owed, check the dispatch seat's fire ledger (`ledger-standin.txt`) for a FIRED line
naming the payload file.

Instances:
- **Four false fire-owed reports, each already fired** (the orchestrator's report). Each render
  is in the seat ledger and each fire is in the fire ledger, 12 to 17 s later:
  - #3089 r5: rendered 17:29:12Z, `FIRED payload-fix-3089-r5.json` at 17:29:26Z (line 223).
  - #3177 r1: rendered 18:15:52Z, `FIRED payload-3177-r1.json` at 18:16:04Z (line 224).
  - #3085 r2: rendered 20:15:14Z, `FIRED payload-3085-r2.json` at 20:15:31Z (line 229).
  - #3174 r4: rendered 20:24:58Z, `FIRED payload-3174-r4.json` at 20:25:14Z (line 230).
  - An earlier batch at about 16:26Z, for example `FIRED payload-3085-r1.json` at 16:26:08Z
    (line 219).
- **Every one of them is fired by payload filename alone.** Since 2026-11-02T11:10Z the fire
  ledger writes `FIRED payload-<name>.json` with no PR number or topic (lines 201 to 230); the
  earlier lines wrote `#<n> r<k>`.
- **The proposed rule is already in force, and the instances happened under it.** The dispatch
  seat's session handoff has opened with "RULE AT THE TOP: before listing anything fire-owed,
  grep ... ledger-standin.txt for a FIRED line by PR number, topic AND the payload filename" in
  its s10g handoff (written about 16:18Z), its s10h handoff and its current s10i handoff (written
  about 17:30Z). All four instances above are later than 17:29Z.
- **No production pull request is held.** From `gh pr view <n> --json files`: #3089
  (`fix/r10-flow-body-only`, 8 files), #3177 (`fix/triage-s9-batch115`, 3 files), #3085
  (`fix/r10-closeout-cleanup`, 12 files) and #3174 (`fix/r10-replay-cost-budget`, 2 files)
  each have 0 files under `custom_components/`.
- **The mechanised form has a live owner.** On roster `efd37113a` the item sat on
  R10-TICK-PR-BUCKETS. On roster `a62d10eb0` that group's stage is `absorbed`, and R10-TICK-LEVELS
  is `in-progress` with `pr: 3200`. Its FIRE-OWED arm is in #3200 at `d7e67e0d7`
  (`orchestrator_tick.py` line 948), which has not merged.
  - The carry opening "Three owed classes", item 3, specifies a FIRE-OWED level ("a rendered cloud
    payload with no fire recorded") with the null control "a payload with a FIRED line prints
    nothing".
  - The carry citing `s6-batch115.md#P375` keys a fire on "a payload file for it
    (`payload-fix-<n>-r<k>.json` or `payload-<n>-r<k>.json`)" and says "Apply the same definition
    to FIRE-OWED".

Cost:
- One sentence in a role contract, which is policy: it merges only on the owner's approving
  review.
- The sentence would name a session-local file that is not in the tree, so the contract would
  bind a seat to a path a later round may not have.
- No capped file is touched by this ruling.

Binding:
- **Why LOG.** The friction is one extra message round per instance. It holds no pull request
  that touches `custom_components/`, and no measured gain above 10% is offered.
- **The proposed text has a measured null.** The same instruction, in the same words, stood at
  the top of the seat's own handoff while all four instances happened. A second copy of it in the
  contract changes nothing the first did not.
- **The owner is the tick level, not the seat.** R10-TICK-LEVELS's FIRE-OWED level computes what
  is owed from the fire ledger, with the P375 carry's payload-file key and a null control for a
  fired payload.
  Once it is built, the dispatch seat's running fire-owed list is redundant; the seat need report
  only the payload it rendered in that report.
- **Until it is built**, the session-local stand-in is the orchestrator's: read a dispatch seat's
  fire-owed line as a claim to check against the fire ledger, as the stand-in `blind_spots.py`
  FIRE-OWED arm already does. The P375 patch to that stand-in, adding the payload-file key, covers
  this arm too.
