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
  and says why in `review-packet: unavailable -- <reason>`. A head is
  dispatched only when `merge_train.py classify` reads it reviewable: RED (a
  required context's latest run concluded failure) or an unreadable answer
  refuses and records nothing; GREEN and WAIT dispatch, and so does
  APPROVAL-OWED (`classify --pr`, rc 4: the red is only a budget raise's
  approval, which follows the review; its line is printed) (`$HPO_BUS_CLASSIFY`
  replaces the command in self-tests). With `--reviewed-head <rh>`, a range
  `review_carry.py` answers CARRY refuses only when the latest verdict naming
  `rh` on `verdict/<pr>` is merge; a blocked one, or none, dispatches and prints
  `review-carry: <rh> was blocked|has no verdict, so a fresh review is owed`,
  and an unreadable `verdict/<pr>` refuses (P348).

The design steps (decision 0014) write the same append-only way:
`bus.sh push-design <topic> <design.md>` adds `design.md` to `design/<topic>`;
`bus.sh push-design-verdict <topic> <verdict.md>` adds `verdict.md` to
`design-verdict/<topic>`. The topic is the roster group id. The verdict's first
line is `Design review: approve <sha>` or `Design review: revise <sha> <class>`,
and `<sha>` must be the current tip of `design/<topic>`: a design that moved
under the review is refused, and so is a topic with no design ref.
  `push-verdict` refuses, before `review/<pr>` moves, a verdict with a line
  its post would refuse (`ref_privacy.py body-lines`, naming the line) and
  one whose finding items name no valid `Carry:` (`carry_audit.py check` at
  origin/main and the round's roster branch, as the train's pre-flight reads
  them); its push carries a 500 MB `http.postBuffer` (#2563's HTTP 400).
  `dispatch` reads a head's own delivery row, except a head whose every
  commit over origin/main is `dependabot[bot]`'s: its row is read on
  origin/main (a row commit on the bot's head reddens `pr-contract`).
  `watch` holds `<state>/watch.lock` (a directory naming its pid): a second
  watcher refuses naming the holder; a dead pid's lock is taken over.
