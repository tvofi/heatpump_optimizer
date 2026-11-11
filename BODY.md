Triage batch 182 rules queue line 280, 2026-11-11. It holds one ruling.

- **P601, ACCEPT narrowed: RELAY-ARMS-BEFORE-HANDOFF-ARM, as the new group R10-RELAY-ARM-ORDER.**
  - `cloud_relay.sh pass()` runs `handoff_arm`, an inline update_pr and full prepr, before `probe_arm` and `confirm_arm`.
  - Probe-to-POSTED latency over 24 h, n=45: median 6.8, p75 18.1, p90 51.6, max 112.7 min. 11 posts waited more than 20 min, about 510 of 715 PR-minutes.
  - Arm 1 (the relay and confirm arms first, sharing one hoisted open-PR listing) is accepted. Arm 2 (detached updates) is rejected, because update_pr.sh already answers BUSY per branch.

The diff is one file against the merge base: `dev/programme/triage/s6-batch182.md`, the ruling. No product behaviour changes.

## Head

`6dc5299921579df60cc96d2ccdb3552eb91ca86e`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P601 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P601 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P602 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...6dc5299921579df60cc96d2ccdb3552eb91ca86e`: 1 file, 1 commit.
- The figures come from the `POSTED` lines of `cloud-relay.log`, matched to the committer times of the `origin/probe/rev-*` refs, and from `cloud_relay.sh` at `cbd23f1c8b`. Each is cited beside its command in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
