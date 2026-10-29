Fix review: merge 99c755c43357f4c7c5f963dcf9e93c2c377fd979

bus-nonce: b6f4513169a27a13179f054db5dd727a

Round 1 of this PR as seen by this seat. A record PR: the diff against the merge base is two documentation files (dev/programme/triage/s6-batch60.md, dev/programme/delivery/2958.md).

## Findings

- The six roster ops the body holds (append-carry R10-ORCH-ROSTER-SCHEMA, append-carry R10-ORCH-LEDGER, and append-group R10-FLY-TICK-TRAIN-RC, R10-FLY-PACKET-RED-PATHS, R10-FLY-RELAY-TOOLS-LEVEL, R10-FLY-GH-CALL-LOG) are owed after the merge, because roster_edit.py refuses them until this file is on main. Carry: R10-ORCH-ROSTER-SCHEMA
- The review packet could not be rendered here: review_packet.py refused with host-path on s6-batch60.md:130, where the text quotes the string HOME=/root and this host's home is /root. That is the same refusal P280 describes for #2872, and the file text is a quotation rather than a leak. Carry: dismissed: the match depends on this host's HOME and the quoted text is deliberate; checks were re-read live instead.

## Evidence

- Head measured: 99c755c43357f4c7c5f963dcf9e93c2c377fd979 (ev/HEAD.txt); the PR head ref was unchanged when posting.
- git merge-tree --write-tree origin/main (279578074) at the head exits 0 with no conflict and no MERGE-CLAIM line (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched; no claim file is in the diff.
- RESULT ruling_verdict at head: P278 ACCEPT, P279 ACCEPT, P280 REJECT, P281 ACCEPT, P282 ACCEPT, P283 ACCEPT, P284 ACCEPT, P285 ACCEPT, which is what the body says.
- RESULT mutation: changing P278's Verdict line to REJECT makes ruling_verdict return REJECT, so the carry gate would refuse it. The mutant is detected.
- Cited lines re-derived at the head: roster_edit.py PUSH_ATTEMPTS = 3 at :137, the lint-gate refusal returning 3 at :657-660, record_row.py urlopen at :882, review_packet.py policy_lint call at :392. The body's P282 `:331` is the older pin, and the file itself re-pins to :392.
- Not re-derived: the live-log counts (TRAIN_RC 7/16, STALE CHECKOUT 28/13, nine refused PRs), because those logs are on the orchestrator's machine. They are quoted as the body's own measurements.
- CI check-runs on the head: all concluded checks are success or skipped except tests / nightly-status (failure). nightly-status grades main's Nightly, and this diff touches none of what it reads, so by defect-root-cause.md it owes no answer here, and the body says so. A prelude job of a later run (40919497605) was still in progress when read, and pr-contract had not concluded.
- This diff writes no production code line, so there are no mutants for the mutation lane to draw, and no budget, closure, golden or claim number moves.
- Forward-carry: the body states none; the rulings' carries live in the roster ops listed above.
