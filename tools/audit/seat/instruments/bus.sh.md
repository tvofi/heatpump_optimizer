# `bus.sh`

- `bus.sh` — git refs as the programme's message bus: seats publish verdicts
  on refs, the orchestrator watches. When: a reviewer seat with no other
  channel, or an orchestrator collecting several lanes' verdicts at once.
  `orphans` discharges a handoff by name only when that `fix/<t>` or
  `fix/<t>-pr` head carries the tip; a named head behind it is
  `repair=update`.
  With `HPO_BUS_TRAIN_STATE` set, each merge verdict it posts is added to
  the merge train there (`merge_train.py add --auto`, one `BUS train-add`
  line; the output in `train-add.log`); a refused add never fails the post.
  `dispatch` is the worker registry's one writer (`$HPO_BUS_STATE/dispatched`,
  `<pr> <head> <reviewer> <nonce> <utc> <model|->`): it closes
  `reviewer-fire <pr> <head>` in the ledger (`$HPO_BUS_LEDGER`, else
  `ledger.py`'s default log), `--nonce` re-records a relay-minted nonce for the
  seat fired with it, and from a fourth round it needs the body's `## Re-cut`
  note or `--past-three <reason>` (logged in `past-three`). `confirm` writes
  the record's model as `bus-model:` on `verdict/<pr>`, which
  `review_strength.py --guardrail` reads as a model arm; it refuses a replay of
  a posted tree before it pushes. `dispatch` first renders the review packet
  (`review_packet.py`) and names it as `review-packet:`. A REFUSED packet (the
  head is unfit: rc 1, a named signal) refuses the dispatch and records
  nothing; a packet this seat cannot RENDER (rc 3, `UNAVAILABLE`: no checkout,
  no `gh`, no token, an unwritable path) dispatches anyway, names no packet,
  and says why in `review-packet: unavailable -- <reason>`.
