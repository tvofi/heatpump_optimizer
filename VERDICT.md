Fix review: merge 04117e2e7d285855bd7864a29dce431072017720

bus-nonce: 7ec67e921cb8080ab661474a610d0113

## Evidence

Delta round (fix-review.md 12). Reviewed head a05a8b00d90f3df7dec07e787abae4dcef35ec71 (dispatch --reviewed-head); the prior merge verdict (verdict/3731 c5f3640f, review/3731 4fbaf9a1) covered every commit through 8f77851df5, which it could not post under C8 because that head carried the predicted `tests / mutation` red. No verdict at #3731 was ever posted, so no blocked head exists; a05a8b00 (the clean main merge the prior reviewer read) is the base of this delta, a superset of the true delta 8f77851d..04117e2e. Head reviewed: 04117e2e7d285855bd7864a29dce431072017720 (`ev/HEAD.txt`), detached worktree at that sha.

- Delta: `git diff --stat a05a8b00d9 04117e2e7d` (`ev/delta-stat.txt`): the delivery row `dev/programme/delivery/3731.md` (one line, the PR's own row) and 11 new `tests/mutation_ledger/killed_by/` pins from `github-actions[bot]` "ci: pin killed mutants". No production, test-script, policy or instrument line moved.
- review_carry 8f77851d -> 04117e2e: CARRY, one bot commit inside its paths (`ev/review-carry-8f77851d.txt`).
- Pins: each of the 11 anchors' `old` line occurs exactly once in its file at the head (`ev/pin-anchors.txt`), and the 11 map one to one to the body's `## Unpinned sites` list (2 config_flow, 3 optimizer, 1 sensor, 2 services, 3 thermal_model) (`ev/body-unpinned.txt`).
- Pin re-derived (null control first): `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` at the head `ALL 599 checks PASSED` (`ev/null-cfs.txt`); with `_single_zone`'s `return not two_zone_from_config(config)` -> `pass`, `2 of 599 checks FAILED` (`ev/mut-single_zone.txt`), the pin's own figure (failed=2). File restored, worktree clean.
- Merge with main: `git merge-tree --write-tree origin/main HEAD` rc=0 (`ev/merge-tree.txt`).
- CI at the head: `tests / mutation` success (the prior verdict's one red, now answered by the bot pins); `tests / fast (3.14)` success; `codeql / Analyze (python)` re-run 135265659834 success; `governance / instrument-self-tests` re-run 135303429217 success; `pr-contract` 135320917433 success; `gate` 135321681409 success. Non-required reds outside the gate's owed set: `tests / nightly-status`, and `tests / replay` 135303432054 (`owner-2026-10-30-away.json: cycle_cost` cpu_ratio 444.8 over 332.8, 1 of 198). Replay was cancelled at 8f77851d and skipped at the base ae0ed64a, so it has no paired reading; production is byte-identical from 8f77851d, so it is outside this delta. A local base/head A/B was aborted under machine load (`ev/replay-ab.txt`).
- Prior findings: the one Note (stale-body `## Head` wording) was paperwork, dismissed by the prior reviewer; nothing to resolve.
- Finder harnesses: the delta moves no production line, so the prior verdict's finder-harness measurements at 8f77851d hold at this head (production byte-identical: `git diff --quiet 8f77851df5 04117e2e7d -- custom_components` rc=0).

## Findings

- Note: stale-body: the code-scanning re-run surfaced main's alerts 57/58 (py/overly-permissive-file, `tools/audit/seat/postmerge.py`, `tools/audit/seat/roster_lib.py`, neither touched here); `## Red checks` now names them (body_patch, head unmoved). Carry: dismissed: paperwork on this PR's own body, no later stage reads it
- Note: unanswered-red: `tests / replay` cycle_cost on owner-2026-10-30-away (cpu_ratio 444.8 over its budget 332.8) is red at this head and `## Red checks` does not name it; non-required, and replay.py's own header says the ratio tracks the runner class, so whether this is runner or code is unmeasured here. Carry: dismissed: a non-required check the gate does not owe, no production line in this delta
