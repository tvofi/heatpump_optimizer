# `ci_probe.py`

- `ci_probe.py` — the writes a CI-layout probe needs, each behind the same
  guards: `push <ref> <sha>` (only `refs/heads/ci-probe/*`), `dispatch`,
  `rerun-job`, `cancel`, `label`, `retarget`, `close`, and the owner-only
  `review --approve --sha` and `dismiss-review`. When: the P2 probe fan-out
  (`plans/ci-layout`). Refusals: a ref outside `ci-probe/`, a missing or other
  `--repo`, `/rate_limit` below 20 % remaining (or unreadable), a token that is
  not `tvofi` on a review, a host path in a ref, message or log line, and a
  commit the push publishes first whose message carries a tool's attribution
  or whose identity names a machine (`ref_privacy.published`). One log
  line per write (`--log`); `--dry-run` writes nothing. Nothing polls (the 60 s
  floor holds vacuously). `--self-test` runs over fakes and a throwaway bare
  remote, including the namespace control: a planted `ci-probe/x` leaves
  `cloud_relay.sh`'s probe arm and `bus.sh orphans` unchanged, a planted
  `probe/foo` is OWED. `prune_refs.py` deletes a `ci-probe/*` ref, untagged,
  unless an open pull request has it as head.
