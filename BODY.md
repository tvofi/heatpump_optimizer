Triage batch 103 rules one queue proposal from the orchestrator s10 (2026-11-01T16:53:15Z): the review packet's hot-file rule reads the merge train's state from `HPO_BUS_TRAIN_STATE`, which cloud seats do not have. It is the rolling batch after batch 102.

- **P360: REJECT as proposed. The residual case is DEFERRED to R10-DISPATCH-AT-HANDOFF.**
  - **The instance.** #3055's round-3 body-only cloud fixer was refused by `body_push.sh`: `hot-file: #3065 holds an unboarded merge verdict and shares tools/audit/seat/cloud_relay.sh`. The body was lost with the container.
  - **The refusal was correct.** The proposal says #3065 was in train 58734's queue. It was not. The train's `train.log` PARKs #3065 on policy approval at batch 2's start and then skips it at verdict `1ac45d875522`. Its `skipped.json` holds #3065, and `queue.pending.json` is `[3054, 3066]`. Run locally with the variable set, `train_boarded()` returns `[3049, 3054, 3066, 3073, 3077, 3084]`, so the local check refuses the same way.
  - **Why both changes are rejected.** A warning when the state is absent saves nothing here, because the next local dispatch refuses the same #3065. It also weakens the P256 handoff gate wherever the variable is unset. A train-written boarded ref adds a standing GitHub write per train event, to fix a false refusal with no measured instance.
  - **What would change the answer.** One cloud handoff refused by `hot-file` over a pull request that `train_boarded()` returned at that time. R10-DISPATCH-AT-HANDOFF owns the item, as the not-started group whose `files` lists `review_packet.py`.

No roster op: a REJECT and a DEFER route nothing. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`901c5b387134d0cb1e292186f68baf3675ccce50`; the file is the whole diff against `d052f80f7`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P360 as `REJECT`.
- A carry citing it is refused: `dev/programme/triage/s6-batch103.md#P360 is not an ACCEPT ruling (REJECT)`. So no roster text can land on this ruling.

## Null control

- With the file absent, a carry citing it is refused: `the triage ruling dev/programme/triage/s6-batch103.md is not on the roster branch or origin/main`.
- `train_boarded()` with `HPO_BUS_TRAIN_STATE` unset returns `[]`. That is the cloud read the proposal describes, against the local read above.

## Figures

- `hot_file_refusals` is at `tools/audit/seat/review_packet.py` line 188, and `train_boarded` at line 574, at `d052f80f7`.
- Hot-file paths in the three-dot diffs:
  - #3065 at `1ac45d875`: `cloud_relay.sh` and `r10_seat_selftests_mutants.py`;
  - #3055 at `757c71eb9`: `cloud_relay.sh` and `pr_args.sh`;
  - #3090 at `3e6bf4230`: `r10_seat_selftests_mutants.py`.
- The lost fixer round: 5617 s, as the proposal line cites it.
- No capped file is touched (`grep -n review_packet tests/*_budgets.json` prints nothing).

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
