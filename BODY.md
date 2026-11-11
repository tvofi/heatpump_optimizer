Triage batch 202 rules P628-P630 (queue lines 306-308), 2026-11-11. It holds three rulings.

- **P628, ACCEPT narrowed: the merge train approves queued entries when the batch starts.**
  - Today the train approves at merge time, so each entry then waits on the `CI review` run its own approval started. The fix is a new group, R10-TRAIN-REVIEW-PRESETTLE (S, sonnet), after R10-TRAIN-RESIDUE-P2.
  - Measured from train.log: 11 of 22 merges today waited, a total of 2800-6100 s (6-12% of the day). Under today's runner saturation the waits were 23-28% of the train's time over 11:13Z-14:05Z, and 63-96% of each waiting entry.
  - Null control: no review run of the 50 that completed today turned a green head red. All 7 `gate` failures cite an earlier code run's red.
- **P629, REJECT: replan exempting the binding chain from the coordinator cap.**
  - The modelled saving is 9.8 h of a 94.8 h horizon (10.3%), under the bar.
  - `orchestrator.md` section 5 keys its exemption on the plan's `critical_path`, which replan already exempts.
  - The same 9.8 h is available now as an over-cap dispatch of R10-ECL110-MQTT-OFF-NEUTRAL once #3404 merges.
- **P630, ACCEPT as a carry check on R10-RELAY-ARM-ORDER (#3465), which already reorders the relay arms.**
  - The residual is a verdict that arrives during an update. It is deferred to a post-merge latency measure.
  - The `topic` single-post form is rejected.
  - The hold-file lever is already tracked in `cloud_relay.sh` and `bus.sh`.

The diff is one file against the merge base: `dev/programme/triage/s6-batch202.md`, the rulings. No product behaviour changes.

## Head

`ca76b1d0cf6e1e0e56cd7bdc75de30008aa1ce73`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P628 and P630 as ACCEPT, and a citation of either passes (`None`).
- A citation of P629 is refused as "not an ACCEPT ruling (REJECT)".
- With P628's verdict text flipped, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P631 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ceb3070ccb...ca76b1d0cf6e1e0e56cd7bdc75de30008aa1ce73`: 1 file, 215 insertions, 1 commit. `ref_privacy.py guard`: no output.
- The figures come from:
  - the roster at `003806b637`;
  - `~/.local/state/hpo/merge_train/train.log` from line 19380 (start 2026-11-11T00:28:34Z);
  - the 53 `pull_request_review` runs created since 2026-11-11, and the gate-job logs of the failed ones;
  - `git log --first-parent` on origin/main;
  - the s14-20 replan scenarios at the 13:58Z snapshot;
  - `cloud-relay.log`.

## Red checks

none

## Forward-carry

none

## Friction

none
