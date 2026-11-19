Fix review: merge a94deddd62ca54f9c81bc1a558c398887d67ddf7
bus-nonce: 0e702255ad33108b0cd5a44ac9593a93

Round 2, delta scope (later-rounds ruling): `git diff bdcca2fb9f a94deddd62`, from a detached worktree at the head. Prior verdict: merge at bdcca2fb9f.

## Evidence

- The delta is one commit, a94deddd62 `ci: re-record tests/entities.py's closure`, touching only `tests/closures.json` (`evidence/delta-a94deddd62...txt`).
- Structural diff of the JSON: `closures["tests/entities.py"]` gains `tests/comment_ratchet.py` and `tools/audit/text_ledger.py` and loses nothing; no other closure changes. These are exactly the two files this branch's `tests/closure.py` (unchanged since bdcca2fb9f) moves out of INERT (`NOT_A_TEST` / `INERT_EXCEPT`), so the recording matches the classification the prior round reviewed.
- The other four changes are `recorded[*].seconds` timings (edge, finite_boundary, stress, typing_ruler) from the same Linux recordings artifact. They are measurements only and are not used for scope selection.
- `tests / closures` and `tests / closure-scope` pass at the head; the gate digest in the packet is green (`evidence/packet-a94deddd62.md`, `evidence/checks-a94deddd62.txt`).
- Prior findings: no code, test or harness file changed in the delta, so the round-1 evidence (mutation kills, wiring plant, finder harness at both ends) still holds as-is.

## Notes

- `governance / env-matrix` was cancelled once at its 10-minute timeout on this head after every declared outcome held. A rerun passed. This is not caused by the PR; the proposal is filed locally for round-end triage.
