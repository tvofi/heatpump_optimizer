R10-FLY-RELAY-REVIEW-FF: the relay now retries confirm on every relayed verdict that bus.sh has not posted. Part of #201.

**What failed (P-O).** `cloud_relay.sh` writes the probe to its ledger (`cloud-relayed`) before confirm runs. A confirm that failed or was skipped was therefore never retried: the next pass reads the probe as "already relayed". The confirm's failure text also went to `/dev/null`.

**Which of the three causes.** The orchestrator's relay log (`~/hpo-orch/r10s4/relay/loop.log`) is not in the tree, so this seat could not read it and cannot say which cause fired. The arm is keyed on the outcome instead, a relayed tip that bus.sh has not posted, so it covers all three causes:
- a confirm that failed;
- a stale `cloud_relay.sh` without the confirm;
- a relay by a call without `--confirm`. `tick_loop.sh`'s `relay_start` made exactly that call before this change.

**The change.**
- **Confirm arm (`pass --confirm`).** For each `review/<pr>` tip that `git ls-remote` lists, the arm acts only when the relay pushed that tip: its `bus-nonce:` must match a probe the relay ledgered as `probe/rev-<pr>-<nonce8>`. It also skips any tip whose tree bus.sh already posted, recorded as `<pr> <tree>` in `posted-signed`. For the rest it runs `bus.sh confirm <pr> <tip>`.
  - On success it logs `POSTED`, which clears the PR's earlier OWED event on the tick.
  - On failure it writes `OWED <utc> confirm-owed refs/heads/review/<pr> <tip> tries=<n>/<max>: <confirm's last output line>` to `<log>.level`. The next pass retries it. The arm itself tries at most `HPO_RELAY_CONFIRM_TRIES` times (default 3); those tries are counted apart from the relay's own confirm, so a verdict this relay relayed sees one confirm call more than that bound. After that the line stays on the level, untried, until the posted record shows the verdict or `dispose` takes the ref.
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
- **Self-test stub, no push site.** The self-test's push-verdict stand-in places `review/<pr>` on its temp bare origin with `git -C <origin> fetch`, the idiom `mk()` already uses for probe refs, instead of `git push`. `cloud_relay.sh` therefore holds no push site, and `ref_privacy.py --check` needs no `PUSHERS` entry for it.

**Alternatives considered.**
- *Retry inside `relay()` by dropping the probe from the ledger.* Rejected: a re-relay would push a second review commit.
- *Confirm every `review/*` tip.* Rejected: that would skip the orchestrator's thread read for its local reviewers.
- *Check bus.sh's `posted` record.* Rejected as the key: `posted` holds verdict commits, and a fresh confirm builds a new commit each time. The PR plus tree pair in `posted-signed` is the posted identity.
- *Register `cloud_relay.sh` in `ref_privacy.py`'s `PUSHERS` as a `fixture`* (the review's proposal). Rejected (fixer.md steps 14 and 17): a `PUSHERS` entry is keyed on the file, so it would also pass a later unguarded push in the relay's production code. Measured: with the entry in place, a `git push -q origin "HEAD:refs/heads/x-$USER"` line appended to `cloud_relay.sh` gave `--check` 0 refused, rc 0. Without the entry and with the stub fetching, the same appended line is refused, rc 1. Commit 3ff74e439 added the entry and 989ee1190 reverts it, so the net diff does not touch `ref_privacy.py`.
- *Run the real `bus.sh push-verdict` in the stub's place.* Not taken: push-verdict needs a dispatch binding (`dispatch_binding`) for every verdict, which would re-cut most of the self-test's fixtures. One check already runs the real push-verdict with no stub and pins `verdict_tree` to it.

**Not built in this PR.** These sit in this group's roster `carry` array, which loses its owner when the group's `resume` goes to done at this merge:
- the stale-checkout restart (P-B and the 07:10Z triage);
- P-E's "SEAT ENDED NO RETURN" detector;
- the `http.postBuffer` push setting and an `ev/` size cap.

## Head

`5d5e49e6f29e90dd33dffebe3a07319c4965132f` merges the authored code head `989ee1190ff8a2de00129f1ddb7ef83d488b636d` and then merges origin/main `fd7e289d0` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

989ee1190ff8a2de00129f1ddb7ef83d488b636d. It is a fast-forward of af21edb9e (the head the review measured, less the orchestrator's delivery-row commit 1270ba9b9) by three commits: 9a2f838fd merges origin/main 27b59c9f7 into af21edb9e, 3ff74e439 adds a `PUSHERS` entry, and 989ee1190 makes the stub fetch and reverts that entry. `git merge-tree --write-tree origin/main 989ee1190` was clean at origin/main fd7e289d0 (2026-10-23 ~17:20Z). Steps 2-8 were re-run at this head.

## Mutation proof

Failing first, for the self-test stub. The red check is `instrument-self-tests` step 23, `python3 -I tools/audit/seat/ref_privacy.py --check`:
- at 9a2f838fd (the merged tree before the fix): `REFUSE tools/audit/seat/cloud_relay.sh:434: a push site in a file PUSHERS does not name`, 1 refused, rc 1;
- at 989ee1190: 0 refused, rc 0.

Stub mutant: drop the stub's `git -C "$o" fetch`, so it builds the commit and never places `review/<pr>`. `bash tools/audit/seat/cloud_relay.sh --self-test` gave 230 checks, 21 failed, rc 1, among them:
- "confirm ran with review/7's remote tip";
- "confirm takes review/7's remote tip, not the sha push-verdict printed";
- "a watch pass with --confirm confirms and logs POSTED";
- "a confirm failing every pass is tried HPO_RELAY_CONFIRM_TRIES (3) times, no more".
So the fetch is load-bearing in the fixture.

Failing first, for the relay. The new self-test ran against origin/main 4c31eb16e's production functions, a hybrid file of the base script with the new `self_test`: `cloud_relay self-test: 230 checks, 23 failed`. The red checks included:
- "the next pass confirms it and logs POSTED";
- "a posted review is not confirmed again";
- "a push refused non-fast-forward is re-applied and the relay passes";
- "a transient push failure is not refused";
- "the refusal is owed in the level file, once, with its reason".
That hybrid was measured at af21edb9e and not re-run here; the merge brought no change to `cloud_relay.sh`'s production functions (`git diff af21edb9e 9a2f838fd -- tools/audit/seat/cloud_relay.sh` is empty).

Mutants, re-run at 989ee1190 with `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-12 cloud_relay-13 cloud_relay-14 cloud_relay-15 cloud_relay-16 cloud_relay-17 cloud_relay-18 cloud_relay-19 cloud_relay-20 cloud_relay-21 tick_loop-3`, gave `RESULT survivors=0`. All 11 were KILLED:
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
- `ref_privacy.py --check` still refuses a push in `cloud_relay.sh`: an unguarded `git push` line appended at 989ee1190 gives 1 refused, rc 1. Removing the stub's push did not blind the check to the file.

## Figures

- cloud_relay self-test, 230 checks, 0 failed, at 989ee1190: `bash tools/audit/seat/cloud_relay.sh --self-test`
- tick_loop self-test, 12 checks, 0 failed, at 989ee1190: `bash tools/audit/seat/tick_loop.sh --self-test`
- Seat mutants, survivors 0 of the 11 named above, at 989ee1190: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-12 cloud_relay-13 cloud_relay-14 cloud_relay-15 cloud_relay-16 cloud_relay-17 cloud_relay-18 cloud_relay-19 cloud_relay-20 cloud_relay-21 tick_loop-3`
- Push-site registry, 0 refused at 989ee1190 and 1 refused at 9a2f838fd: `python3 -I tools/audit/seat/ref_privacy.py --check`
- ref_privacy self-test, 84 checks, 0 failed: `python3 -I tools/audit/seat/ref_privacy.py --self-test`
- The rest of `instrument-self-tests` that step 23's failure skipped, run locally where cheap: `python3 -I tools/audit/seat/selftest_wiring.py --check` (0 unwired, rc 0) and `python3 -I tests/throwaway_git.py --check` (0 refused, rc 0). The remaining skipped steps are left to CI at this head.
- Gate scope at merge base 27b59c9f7: `python3 tests/closure.py select --diff 27b59c9f7975d1526529fe5aff21e8243caf19c5 --workdir <dir>` prints `MODE: SCOPED -- 0 script(s) run`.
- Structure ratchet, rc 0: `python3 tests/structure.py`
- prepr at 989ee1190: `bash tools/pr/prepr.sh`

## Red checks

- `instrument-self-tests` (job 120428929767 at 1270ba9b9), step 23 "Refuse a push that names the host, and an unregistered pusher": `ref_privacy.py --check` refused the self-test stub's new `git push` in `cloud_relay.sh`, a file `PUSHERS` does not name. This PR caused it; at origin/main 4c31eb16e the same check refused 0. Fixed above: the stub no longer pushes. Cheaper detector: `python3 -I tools/audit/seat/ref_privacy.py --check` runs locally in about 5 s wall-clock on this seat. Neither `tools/pr/prepr.sh` nor `tools/pr/ci_predict.py` runs it (`rg -n ref_privacy tools/pr/prepr.sh tools/pr/ci_predict.py` matches nothing), so the detector existed and was in no local path. Process state (a): no local step ran it. Adding it to prepr.sh would cost about 5 s per prepr run; the countermeasure decision is the root-cause seat's.
- `pr-contract` (job 120446037835 at 1270ba9b9): the body's `## Red checks` read `none` while `instrument-self-tests` was red (`check instrument-self-tests is red and ## Red checks does not name it`). It is downstream of the red above and is answered by this section. No cheaper detector exists: the check refuses a body against CI's own red list, which does not exist before CI runs. The fixer's control is to read the head's check runs before the handoff.

## Forward-carry

- The `carry` array of this group (P-B and the 07:10Z stale-checkout restart, P-E "SEAT ENDED NO RETURN", the `http.postBuffer` setting and the `ev/` size cap) is not built here and has no owner once the group's `resume` goes to done. The orchestrator re-homes it or keeps the group open at the merge record. Carry: R10-FLY-RELAY-REVIEW-FF
- handoff/r10-orch-ledger edits the same `relay()` and `dispose()` hunks of `cloud_relay.sh`; whichever lands second merges main. The group's roster `resume.note` already says so. Carry: R10-ORCH-LEDGER

## Friction

`none`

