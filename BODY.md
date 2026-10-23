R10-FLY-RELAY-REVIEW-FF: the relay now retries confirm on every relayed verdict that bus.sh has not posted. Part of #201.

**What failed (P-O).** `cloud_relay.sh` writes the probe to its ledger (`cloud-relayed`) before confirm runs. A confirm that failed or was skipped was therefore never retried: the next pass reads the probe as "already relayed". The confirm's failure text also went to `/dev/null`. Verdicts sat unposted on #2659 and #2632 on 2026-10-23, and on four PRs over two days.

**Which of the three causes.** The orchestrator's relay log (`~/hpo-orch/r10s4/relay/loop.log`) is not in the tree, so this seat could not read it and cannot say which cause fired. The arm is keyed on the outcome instead, a relayed tip that bus.sh has not posted, so it covers all three causes:
- a confirm that failed;
- a stale `cloud_relay.sh` without the confirm;
- a relay by a call without `--confirm`. `tick_loop.sh`'s `relay_start` made exactly that call before this change.

**The change.**
- **Confirm arm (`pass --confirm`).** For each `review/<pr>` tip that `git ls-remote` lists, the arm acts only when the relay pushed that tip: its `bus-nonce:` must match a probe the relay ledgered as `probe/rev-<pr>-<nonce8>`. It also skips any tip whose tree bus.sh already posted, recorded as `<pr> <tree>` in `posted-signed`. For the rest it runs `bus.sh confirm <pr> <tip>`.
  - On success it logs `POSTED`, which clears the PR's earlier OWED event on the tick.
  - On failure it writes `OWED <utc> confirm-owed refs/heads/review/<pr> <tip> tries=<n>/<max>: <confirm's last output line>` to `<log>.level`. The next pass retries it, up to `HPO_RELAY_CONFIRM_TRIES` attempts (default 3). After that the line stays on the level, untried, until the posted record shows the verdict or `dispose` takes the ref.
  - A tip with no dispatch for its PR, head and nonce is owed `undispatched` and never confirmed.
  - A tip the relay did not push waits for the orchestrator's own read of the reviewer's thread.
  - The arm makes no `gh` call; `bus.sh confirm` does the posting.
- **Relay confirm.** The relay's own confirm now logs confirm's last output line in its `OWED` reason, where it used to discard it.
- **Remote tip.** Confirm now takes `review/<pr>`'s remote tip, as `git ls-remote` reports it, not the commit push-verdict built locally. It takes that tip only when the tip's tree is this verdict's tree (`verdict_tree` builds bus.sh's `VERDICT.md` plus `evidence/`). The relay prints `review/<pr> remote tip <sha>`.
- **Non-fast-forward.** A `push-verdict` that the remote refuses as non-fast-forward is run again, at most three times, and never forced; bus.sh re-reads the fresh tip and appends the same verdict on it. If the fresh tip already carries this verdict's tree, the relay skips the push and prints that it did.
- **`tick_loop.sh`.** `relay_start` now runs `cloud_relay.sh pass --confirm` (P15, P-C). `--confirm` replaces the orchestrator's read of the reviewer thread with the relay's nonce, head and dispatch-record checks (decided 2026-10-18).
- **Probe arm.**
  - A relay rc of 2, a refusal of the ref itself, is refused at once as before.
  - Any other failure, such as an HTTP 400 push or a failed fetch, is retried on later passes, `HPO_RELAY_TRIES` attempts in all (default 3), then refused. A failed fetch now returns rc 1 instead of a refusal.
  - Each refusal prints `REFUSED <ref> <sha> <reason>` and is written as `OWED <utc> probe-refused <ref> <sha> <reason>` in `<log>.level` until disposed. A probe refused before this change has no stored reason (`<ledger>.refused-why`) and stays silent.
- **`dispose`.** It now also takes `review/` refs.

**Alternatives considered.**
- *Retry inside `relay()` by dropping the probe from the ledger.* Rejected: a re-relay would push a second review commit.
- *Confirm every `review/*` tip.* Rejected: that would skip the orchestrator's thread read for its local reviewers.
- *Check bus.sh's `posted` record.* Rejected as the key: `posted` holds verdict commits, and a fresh confirm builds a new commit each time. The PR plus tree pair in `posted-signed` is the posted identity.

**Not built in this PR.** These remain in this group's roster carry:
- the stale-checkout restart (P-B and the 07:10Z triage);
- P-E's "SEAT ENDED NO RETURN" detector;
- the `http.postBuffer` push setting and an `ev/` size cap.

The brief's priority list for this seat named only P-O and the brief's items.

## Head

af21edb9e6e6

## Mutation proof

Failing first. The new self-test ran against origin/main 4c31eb16e's production functions, a hybrid file of the base script with the new `self_test`: `cloud_relay self-test: 230 checks, 23 failed`. The red checks included:
- "the next pass confirms it and logs POSTED";
- "a posted review is not confirmed again";
- "a push refused non-fast-forward is re-applied and the relay passes";
- "a transient push failure is not refused";
- "the refusal is owed in the level file, once, with its reason".

Mutants, run with `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-12 cloud_relay-13 cloud_relay-14 cloud_relay-15 cloud_relay-16 cloud_relay-17 cloud_relay-18 cloud_relay-19 cloud_relay-20 cloud_relay-21 tick_loop-3`, gave `RESULT survivors=0`. All 11 were KILLED:
- cloud_relay-12: drop the confirm arm from `pass`.
- cloud_relay-13: drop the posted check.
- cloud_relay-14: drop the tries bound.
- cloud_relay-15: drop the dispatch check.
- cloud_relay-16: no non-fast-forward re-apply.
- cloud_relay-17: no "already carries" skip.
- cloud_relay-18: confirm the printed sha instead of the remote tip.
- cloud_relay-19: refuse every failure at once.
- cloud_relay-20: no `probe-refused` level line.
- cloud_relay-21: drop confirm's last line from the OWED reason.
- tick_loop-3: `relay_start` without `--confirm`.

## Null control

- A review already posted, by the arm or by hand in bus.sh's `posted-signed`, is not confirmed again.
- An undispatched review is owed once after two passes and is never confirmed.
- A `review/<pr>` tip whose nonce the relay did not ledger is left alone and owes nothing.
- `pass` without `--confirm` runs no confirm arm.
- A push failure that is not non-fast-forward is not re-applied: one push, rc 1.
- A refusal of the ref itself (rc 2) is refused at once.
- With the real `bus.sh push-verdict`, no stub, the relay confirms the remote tip as carrying its verdict tree. This pins `verdict_tree` to bus.sh's own tree.
- The 192 checks that ran before this change still pass (a nonce mismatch, a head mismatch, the hold file, the handoff arm, the reap).

## Figures

- cloud_relay self-test, 230 checks, 0 failed: `bash tools/audit/seat/cloud_relay.sh --self-test`
- tick_loop self-test, 12 checks, 0 failed: `bash tools/audit/seat/tick_loop.sh --self-test`
- Seat mutants, survivors 0 of the 11 named above: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-12 cloud_relay-13 cloud_relay-14 cloud_relay-15 cloud_relay-16 cloud_relay-17 cloud_relay-18 cloud_relay-19 cloud_relay-20 cloud_relay-21 tick_loop-3`
- prepr at af21edb9e6e6, every check ok or skipped, exit 0: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`

## Red checks

`none`

## Forward-carry

`none`. The carries not built here are already in this group's roster entry. Carry: dev/programme/rosters/wave-r10-groups.json

## Friction

`none`
