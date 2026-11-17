Fix review: merge 813a9e9e8dca4583a89f4ec46354cf2a8b389d91

bus-nonce: f1652e7c3653b3fd69ed30a09a135dce

## Round

Second round. This is a delta review over the reviewed head abe961e6e56432e27cd2ea56ac22fd8e37338b50, whose verdict was `blocked ci-red` on `tests / mutation`. `review_carry.py abe961e6e5 813a9e9e8d` prints FRESH-REVIEW because 5dbf429011 is a `ci:` commit that touches files outside the merge-driver files, so the scope is the delta. The delta has three commits:
- 5dbf429011 adds the four `killed_by` ledger rows.
- 3ab8342d3a merges 5dbf429011 into the branch.
- 813a9e9e8d is the merge-main bot's `ci: merge main` (merge base fc9e24c089).

## Evidence

- The previous block is resolved. CI named four `ADDED UNPINNED` sites, and each now has a `killed_by: tests/features.py` row: ledger.py:80 CONST (0e2b3d10), thermal_model.py:2280 GUARD_OFF (d85c286a), :3504 GUARD_OFF (89896ff5) and :4312 GUARD_OFF (12bdfb35). `tests / mutation` is green at this head.
- I applied my own targeted mutants, one per pinned site, in a worktree at the head (ev/mut2.sh, ev/mutants2-final.txt). Each was run against the features block from `# R10-HOTFIX-SAV-ESTIMATE: a month's reference basis` through the R11-VALVE-REFERENCE checks, using `features_block.py` with its own `--emit-prelude`. The unmutated block reads rc=0, 0 FAIL. All four mutants are KILLED:
  - `REFERENCE_BASIS = 8` fails 2 checks: the first booking stamp, and "a month stamped 4 keeps stating its saving".
  - 2280 `if False:` fails 4 checks: the digest, the 0.02 K hold at 20.662 / 19.115, the 21 C hold, and the gains clamp.
  - 3504 `if False:` fails "the curve the model reports is the plant's own" (22.714 against 25.125).
  - 4312 `if False:` fails the digest.

  These match the body's `## Unpinned sites`. The body names a second kill for 4312, "the stability count subdivides". That check falls outside the block I ran, so I did not re-derive it. The kill does not depend on it. After the run the tree was clean (0 changed).
- My first attempt ran the full `tests/features.py` under a 900 s timeout. It timed out (rc=124) on the unmutated base before reaching its end, so I discarded it and used the block driver above. The timed-out log is kept as ev/features-full-base-timedout.txt. Its three "FAIL" matches are `ok` lines whose text contains "FAILS" / "FAILED", not failures.
- The PR's own diff is unchanged by the main merge. I compared each non-ledger file's `+`/`-` lines in `git diff 92d38ecb64 abe961e6e5` against `git diff fc9e24c089 813a9e9e8d` (ev/own-diff-compare.txt). These are identical: ledger.py, mixing_valve.py, thermal_model.py, r10_sav_held_install.py, delivery/3685.md and tests/features.py. The only other differences are the ledger rows above and `tests/structure_budgets.json`, where main's merge moved the recorded `class_excess_loc` (17407 → 17406 before the merge, 17385 → 17384 after it). The −1 payment is preserved. `python3 tests/structure.py` at the head prints `ok class_excess_loc 17384 <= 17384` and `STRUCTURE RATCHET PASSED` (ev/structure-head.txt).
- I did not widen the scope. Main's merged production delta (92d38ecb64..fc9e24c089) touches 16 `custom_components/` files, mainly the #3616 room lift. None of them touches `thermal_model.py`, `mixing_valve.py` or `ledger.py`. A grep of that delta for `flow_setpoint`, `_valve_flow_set`, `_valve_ua`, `flow_target_for_indoor`, `REFERENCE_BASIS`, `mixing_valve` and `THROTTLING` finds only `two_zone=` passed into `rooms.gate`. The room lift adjusts `min_temp_margins` (the comfort floor). It does not change the valve curve this PR rewrites, so this PR's code is not put at any non-obvious risk.
- Merge with main: `git merge-tree --write-tree origin/main 813a9e9e8d` exits 0 with no conflict (ev/merge-tree.txt).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched in `git diff fc9e24c089 813a9e9e8d`, which printed no output.
- The PR body's `## Head` names 813a9e9e8dca4583a89f4ec46354cf2a8b389d91, the head I measured. `git ls-remote origin refs/pull/3685/head` printed the same SHA.
- CI: `merge_train.py classify 813a9e9e8dca4583a89f4ec46354cf2a8b389d91 --pr 3685` gives `GREEN 813a9e9e8dca4583a89f4ec46354cf2a8b389d91 pending: none red: none`, rc=0, both on first read and on re-read before this verdict (ev/classify-log.txt, ev/classify-final.txt). No required check is red, so no red check is owed an answer.
- The previous verdict's other items carry unchanged, because the production code is byte-identical: mutation proof M1–M7 and R1–R4, the finder harnesses at both ends, the null controls, the class enumeration, the forward carries and the archscore. Its `Note: body-stale` is settled: the body now names this head and the structure figure 17384. Its pending-owner Residual (the reproduction against a diagnostics bundle) is still open in the body as the dispatch condition, routed to R11-VALVE-REFERENCE.
- Closing self-audit: I ran `carry_audit.py check` over this verdict (ev/carry-audit.txt) with an empty body file, because this seat has no `gh` to fetch the body. It reports rc=0 and 1 item routed. The review packet's own carry_audit, run at this head over the PR body, reported 6 routed, 0 unrouted, 0 bad.

## Findings

- Residual: the owner has still not confirmed the dispatch condition. Carry 1's reproduction ran on R10-COMBI-TANK's synthetic install shape (the harness's `combi` row), not on a diagnostics bundle, because no committed bundle has a single-zone valved install. Carry: R11-VALVE-REFERENCE
