# `queue_pre_flight.py`

- `queue_pre_flight.py` — runs a merge queue's admission reads offline, before
  the train launches: per entry PASS, PARK (the train's own Stop wording — a
  carry that fails, a missing or stale delivery row, a GITHUB_TOKEN bot tip, a
  branch another worktree holds, a policy or budget head without the owner's
  in-force mandate) or FAIL (a verdict that is not 40-hex, a closed pull
  request). When: before any `merge_train.py run`/`batch` — an admission-time
  refusal parks the entry here instead of stopping a live queue mid-run.
  Refusal: exit 1 unless every entry passed; the checks are the train's own
  methods (`bot_tip`, `policy_gate`, `app_approve.sh --carry`), never new ones.
  `merge_train.py --pre-flight` runs it inside the train, passing the two
  shapes the train now cures itself: a bot tip, and under `--free-holders` a
  holder `Train.freeable` clears.
