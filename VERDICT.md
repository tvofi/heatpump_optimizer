Fix review: merge f9a259a14267f7c291931f6defc54e1b378f8c79

bus-nonce: 68a25911c97a88dd5dbc2d73da47ef8b

## Round

First review round. No earlier `verdict/3395` or `probe/rev-3395*` ref exists at origin.

## Evidence

- Head measured: `f9a259a14267f7c291931f6defc54e1b378f8c79`. It is still the tip of `fix/r10-state-docs-push-race` at verdict time (`git ls-remote`). The body names this head and the authored code head `6ae023651`; the only commit after that adds `dev/programme/delivery/3395.md`.
- Role contracts are current: the three-dot `git diff` from the merge base to origin/main under `dev/governance/roles/` is empty.
- Merge with main: `git merge-tree --write-tree origin/main f9a259a1` exits 0 with tree `107597456936f8825bb460e9c1170366517dcf49`, so there is no conflict.
- CI on this head: `merge_train.py classify f9a259a1 --pr 3395` printed `GREEN f9a259a14267f7c291931f6defc54e1b378f8c79 pending: none red: none` with rc 0 (`ev/classify.txt`).
- Red checks (step 11): `classify` on the earlier head `6ae023651` prints `RED ... red: gate`. Both CI runs on that head (42722898434 and 42722904262) ended `cancelled`, not `failure`, about 40 s after they started, when the record commit was pushed on top. Nothing failed. A run cancelled because it was superseded is not a red outcome, so the body's `Red checks: none` is accurate. `pr-contract / pr-contract` passed at this head, with `CARRY-AUDIT: 0 finding item(s)` and `clean no refusal`.
- Mutation proof (step 1). Each mutant ran under `python3 tools/audit/seat/state_docs.py --self-test` at the head, and every one was killed (`ev/mutation-results.txt`, `ev/mut-*.txt`):
  - RESULT mutant=M1-bound-never: rc=1. "race on every attempt: refused rc 2" fails, and the log shows "attempt 4 of 3".
  - RESULT mutant=M2-pred-inverted: rc=1, with 4 checks failing.
  - RESULT mutant=M3-always-raced: rc=1. "non-race refusal: rc 2 at once, named not a race" fails.
  - RESULT mutant=M4-no-fetch (`remote_tip` replaces `fetched_tip`): rc=1, with 4 checks failing on "failed to unpack tree object".
  - RESULT mutant=M5-no-retry (the `except Raced` is never caught): rc=1, and the self-test crashes with an uncaught Raced. This mutant is my own.
  - RESULT mutant=M6-stale-prev (the tip is read once and reused across attempts): rc=1, and the self-test crashes on an unpack/read-tree failure. This mutant is my own and coarse, because its cached global also leaks into the beat arms.
  - RESULT mutant=M7-push-ignores-rc: rc=1, with 7 checks failing. This mutant is my own.
- Null control at both ends (steps 2 and 3). No finder harness is committed elsewhere. The group's roster brief on `handoff/audit-r10-roster` asks for this exact harness: a `--self-test` case where a rival push lands during generation. It landed in this PR as the self-test arms, so the harness is the brief's design, not one the fixer invented. I spliced the PR's race arms, together with `PUSH_ATTEMPTS = 3`, into the merge-base `state_docs.py` (b8f67a775) and ran them myself.
  - RESULT baseline-with-arms: rc=1, `4 self-test check(s) failed`: "race: one rival inside generation", "race on every attempt: refused rc 2", "bounded at PUSH_ATTEMPTS rivals" and "non-race refusal". "race null control" is not among the failures, so the null arm passes at the base (`ev/nullcontrol-base.txt`).
  - RESULT head: rc=0, `state_docs self-test: all checks passed` (`ev/selftest-head.txt`).
  - Both match the body's figures ("baseline 4 failed", "head all checks passed").
- Figures: `python3 tests/structure.py` at the head prints RESULT rc=0 and `STRUCTURE RATCHET PASSED` (`ev/structure-head.txt`). This matches the body.
- Steps 4, 5 and 14: the three-dot diff touches only `tools/audit/seat/state_docs.py` and `dev/programme/delivery/3395.md` (`ev/diffstat.txt`). It leaves VERSION, the manifest, RELEASE_NOTES, both claim files, every `*_budgets.json` and `tests/closures.json` untouched. No instrument moves, so there is no fixture drift to reconcile and no metric to game.
- Step 6 (class): the body names no enumeration rule. The roster brief for R10-STATE-DOCS-PUSH-RACE (class `push-race`) names one seam, the read-generate-push in `state_docs.py`'s `main()`. Its sibling, `roster_edit.py`, was fixed under R10-ROSTER-PUSH-RACE. The class is therefore one seam, and an absent rule is no gap here. I did not sweep the other `git push` sites under `tools/audit/seat/` because neither the brief nor the body puts them in this class.
- Step 15 (architecture): the publish pass moves out of `main()` into `publish_once()`, and the push into `push_state()`. The bounded loop matches roster_edit's shape. A refusal at an unmoved tip raises `Refuse` and is never retried. Nothing forces a push, and every rival commit is kept: the self-test checks this with `merge-base --is-ancestor`. There is no breach.
- Step 10 (forward-carry): the body declares `Forward-carry: none` and `Friction: none`. This review found nothing that changes a later stage.

## Findings

none
