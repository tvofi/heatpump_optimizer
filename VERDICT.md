Fix review: merge 1ac45d875522d5ab8040f8d89d1f05a7aeadda6d

bus-nonce: 0b0cb173c9cb41f0613c5c6aa69ea2c9

Round 1. Reviewed from a detached worktree at 1ac45d875522d5ab8040f8d89d1f05a7aeadda6d.

## Summary

The instrument changes hold under my own plants, and the legitimate paths still work. CI on this head was still pending (classify WAIT, no red check) when this was written; it is not a verified GREEN, and the orchestrator should re-run classify before merging.

## Findings

- carry_audit now reads Evidence by shape (P308 as designed): a prose nit in Evidence that is neither a lead-opened bullet nor carries Carry: is not flagged. At origin/main a line like "a nit remains: baz is residual." was flagged; at this head it is not (my probe). The design is intended and stated in the body, but a seat that buries a finding mid-sentence in Evidence now passes the audit. Carry: dismissed: the shape reading is the owner's P308 ruling, and the reviewer prompt states it
- standing-dispatch.md is code-owned policy and the body records the owner's approval as owed. Carry: dismissed: merge needs the owner's approving review under the code-owner rule, which main-protect-checks enforces

## Evidence

- Merge: git merge-tree --write-tree origin/main head exits 0, with no claim-file conflict (inert_reads merged as a set).
- Self-tests re-run here: tick_loop 26/0, cloud_relay 316/0, bus 123/0, carry_audit 292/0 (ev/*.log). tests/structure.py: STRUCTURE RATCHET PASSED.
- Three-dot diff has dev/programme/delivery/3065.md, touches no golden or claim file, no VERSION or manifest.
- The restart (tick_loop.sh fresh_check) never fast-forwards in place and never exits: it takes the relay flock (non-blocking), refuses a branch checkout, a dirty tree (tracked files) and a failing bash -n of origin/main's copy, then checks out detached and execs with the saved argv, once per pass (HPO_TICK_RESTARTED). Otherwise it prints TICK-STALE and skips the relay and sweep arms. My plants (each removed one guard): dirty, bash -n, lock, detached, relay skip: all killed (1, 2, 6, 4 and 3 failing rows), with the null rows (behind 0 silent, within-bound relays) passing.
- cloud_relay.sh review_freeze: the dispatch-record columns (pr head ref nonce at model) match bus.sh's writer. My plants, dropping the head match and dropping the at time, are killed (1 and 2 failing rows); the null rows pass. My dirty-tools-tree plant ran past my time budget and I stopped it without a result; that guard is covered by the author's cloud_relay-42 mutant, which I did not re-run.
- bus.sh: planting out the carry_gate call fails the two push-verdict refusal rows. I did not plant the body-lines, postBuffer or dependabot arms myself.
- Claims about main (P15 --confirm in relay_start, the confirm arm, the retry with REFUSED) I checked only through the PR's own self-test rows, not by reading origin/main line by line.
- I did not re-run the carry-parser or seat-selftests mutant harnesses, the field-figures harness, prepr, or the scoped gate: the first four are in CI's governance and tests jobs.
- Red checks: none concluded red at the time of writing, so the ## Red checks section's earlier fast(3.14) red (run on 054e5a25f) is a prior head's, repaired in c5ded0de1.
- The review packet reports FIGURES 21 resolved, 0 not verified; carry_audit at head routes 1 item (the friction one, dismissed).
- CI at this head: classify returned WAIT (tests / fast (3.14), closures, graders-head-copy, instrument-self-tests, codeql python still in progress), no red.
