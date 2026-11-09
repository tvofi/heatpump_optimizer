Fix review: merge 1ea3a2429ff03b904dacddd1fe7bfcb6485618c2

bus-nonce: 2296010f4c0144938d7396fb69d19550

Round 3 for #3348: blocked merge-conflict at 4cab619c, then blocked ci-red at this head, now this one. The patch is unchanged since the round-2 verdict. Its only block was CI, and CI now reads GREEN.

## Evidence

- Head measured: 1ea3a2429ff03b904dacddd1fe7bfcb6485618c2 (ev/HEAD.txt), from a detached worktree.
  - Re-read at 05:25:49Z by `git ls-remote`: refs/pull/3348/head and the branch both still at it (ev/head-reread.txt).
  - Its tree equals b6c6a067's (`git diff --quiet b6c6a067 1ea3a2429`), the SHA the body's figures name.
- Role contracts: `git diff <merge-base>...origin/main -- dev/governance/roles/` prints 0 lines, so the contract is current (ev/checks.txt).
- Merge: `git merge-tree --write-tree origin/main 1ea3a242` exits 0 against origin/main ddf43ca9 (ev/merge-tree.txt). Merge base 6457496a.
- CI: `merge_train.py classify 1ea3a242 --pr 3348` exits 0, `GREEN ... pending: none red: none`, at the first poll and again at 05:25Z (ev/classify.txt, ev/classify-final.txt). So round 2's ci-red block is cleared at the unchanged head.
- Red checks: the head's earlier `gate` reds were deferrals; round 2 quotes the log lines. The body answers this class in `## Red checks` (cheaper detector: none exists). `pr-contract / pr-contract` 128960506848 is success.
  - `governance / delivery-status` red is main's. This diff adds only its own row, `dev/programme/delivery/3348.md`, so `defect-root-cause.md` owes it no answer.
- RESULT self-tests at the head (ev/selftests-head.txt): gate 81 checks, 0 failed; sweep 71 checks, 0 failed; prelude 76 checks, 0 failed. Each matches the body.
- RESULT finder's harness (the RCA replay `r10_rca_gate_busy_defer_2.py replay --ci <git archive tools/ci tools/pr>`):
  - at the head: `3252-nosource: DECIDED` PASS; `3244-triple: DECIDED`, all PASS; `defects=no`, rc 0 (ev/replay-head.txt).
  - at main 6457496a: `3252-nosource: MISREAD` (`FAIL pr-contract / pr-contract: failure (run 42387066581)`); `defects=yes`, rc 1 (ev/replay-main-6457496a.txt).
  - at the live pin 9cbd7dd0, the null for the triple: `3244-triple: DEADLOCK` (ev/replay-pin-9cbd7dd0.txt).
- RESULT gate-core mutants: `r10_ci_gate_core.py mutants` prints `RESULT mutants=22 survivors=0`. M28 is KILLED by `source order null` (ev/gate-core-mutants.txt).
- RESULT reviewer mutants: 13 mutants, plus an unmutated control, from my own driver (ev/reviewer_mut.py; mine, not the fixer's). Each is applied in place at the worktree and the three self-tests run; the file is then restored, and `git status` was clean afterwards (ev/reviewer-mutants.txt).
  - The control reads 81/71/76, 0 failed.
  - KILLED: `run_jobs` not filling `starts`; my own run's `starts` not passed; siblings' `starts` not passed; `api["starts"]` dropped. Also killed: `later`'s `>=` turned to `<=`; the `.py` suffix dropped; `runs` dropped in `run()`; `runs` dropped in `settle()` (round 1's S15, now pinned by b6c6a067); the per-sweep pin cache off.
  - SURVIVED: 4 mutants, each under `## Findings`. 3 repeat round 1's G2, G8 and S16; one is new (`pull_request_review`).
- Class rule (the body's grep) at the head returns 8 lines: gate.py 124 and 126, sweep.py 114, 115, 224 and 270, prelude.py 236 and 303. The body dispositions each one. `gate.gate`'s id sort is gone (ev/checks.txt).
- Ratchet and untouched files:
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `archscore --diff 6457496a`: `Architecture score: dS +0.0000 NULL`.
  - The three-dot diff over VERSION, the manifest, RELEASE_NOTES.md, both claim files and every `*_budgets.json` is empty (ev/checks.txt).
- Figures I did not re-derive, the same as round 2:
  - the 1821-run / 5 / 3 codescan counts;
  - the `19 of 19 SAME` pin census;
  - the 73-mutant diff table, which is CI's heavy run and is cited, not re-run.
- Forward-carry: the body states `none`, and I found no finding that changes a later stage's brief.

## Findings

- Follow-up (non-blocking): Surviving mutant, `gate.fresh`'s `max(...)` over a unit's job starts replaced by `min(...)`, passes all three self-tests (round 1's G2, still open). The multi-job aggregation is unpinned. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up (non-blocking): Surviving mutant, `fresh`'s own-lag guard `any(...)` replaced by `all(...)`, passes (round 1's G8, still open). The multi-job arm of "never displaced" is unpinned. The code is correct and this is no regression from id order. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up (non-blocking): Surviving mutant, the poll path's `self.judge(..., list(listing.values()))` with the listing dropped, passes (round 1's S16, still open). b6c6a067 pinned the settle path only, and this call site's no-second-dispatch guard is still unpinned. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up (non-blocking): Surviving mutant, new this round: `PINNED_EVENTS` with `pull_request_review` removed passes every sweep self-test. No case drives a stale-pinned review-event gate. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up (non-blocking): Round 2's finding still stands: the sweep's stale-pin dispatch and settle re-judging reach PRs only while `gate-sweep.yml` is enabled. That workflow read `disabled_manually` in round 2. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Friction

- review-frugal-guard: cost: discovery reads were capped at 5 inline searches, so the carry-destination lookup was one roster read. Carry: dismissed: a session plugin's guard, not this repository's policy
