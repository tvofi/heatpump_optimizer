Fix review: blocked 9ef51b8215dd7216950f177386fb2f5a8f010a47 metric-gamed: archscore: the body still states dS +0.0012 IMPROVES, and this diff scores dS +0.0000 NULL three-dot, unrepaired since round 1

bus-nonce: de774e283b26fc790fb40c74a9cd6ac6

This is round 2 of this fix review. I measured head 9ef51b8215dd7216950f177386fb2f5a8f010a47. At post time, a fetch of `fix/r10-hotfix-ci-critpath-2` resolves to it, and the body is unchanged (updated_at 19:55:52Z). It merges code head 536da691c and origin/main a7dd7f50d, which is the merge base. The only branch-side change since the round-1 head b02ffd170 is the `record_table()` refactor in tests/ci_ratchet.py and its pin.

## Block

The round-1 block was a body-only repair, and it was not made. The PR body, read live at this head (updated_at 2026-10-31T19:55:52Z), still states `Architecture score: dS +0.0012 IMPROVES` in three places: in `## Figures`, in `## Architecture score` ("coord_footprint 2390 -> 2388"), and as the `Architecture score:` line of `## Raise justification`.

- I ran `python3 tools/audit/archscore/score.py --diff a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 9ef51b8215dd7216950f177386fb2f5a8f010a47` in a detached worktree at the head. That is the three-dot comparison, because the merge base equals origin/main. It prints `Architecture score: dS +0.0000 NULL` (ev/archscore-3dot.txt).
- The three-dot diff touches tests/ci_ratchet.py, tests/ci_budgets.json, tools/policy/budget_raise_gate.py and a delivery row. None of these is coordinator code, so coord_footprint cannot move.
- CI's arch-score job 124640032401 on this head concluded success. That is consistent with NULL, which is admissible.

The brief makes an honest `## Raise justification` a condition, and fix-review step 14 holds every figure the body quotes to the change. A NULL must be stated as NULL. The repair is still body-only and does not move the head: replace the three occurrences with `dS +0.0000 NULL` measured three-dot, and drop the coord_footprint clause. After that, a re-verdict needs only the body and the post-edit `pr-contract` and `budget-raise-gate` runs, plus tvofi's re-approval at the head. Every other check below passes at this head.

## Findings

- Instrument finding, carried from round 1 and still unpropagated: budget_raise_gate checks only the shape of the `Architecture score: dS <n> <verdict>` line. It never checks the value against the arch-score job. That is how the unearned IMPROVES got through the gate for a second round. The body's `## Forward-carry` reads "none", so it names no roster SHA for me to check. No `handoff/audit-r10-roster` ref exists on origin. Carry: R10-HOTFIX-CI-CRITPATH-2
- budget_raise_gate's MAX0 typing calls removing the band (1.3 -> absent) a raise, although the PR's own text says "absent is a band of zero". This fails closed and is unchanged from round 1. Carry: dismissed: a fail-closed false positive that opens no gate weakness, and only the owner can decide that removal should be routine

## Evidence

- M6 is now killed. The mutant deletes the `**{k: budgets[k] for k in BAND_KEYS if k in budgets},` line in `record_table()`. On the mutated tree the self-test fails 1 of 45 checks, "--record carries the band over unchanged and re-records every derived metric". On the head it passes all 45 (ev/m6.txt). Round 1's M6 survivor is settled.
- Full M1-M6 under `env -u BASH_ENV`, summary lines (ev/mutants.txt):
  - M1, band ignored in compare: ci-ratchet 45 checks, 2 failed.
  - M2, band on every row: 2 failed.
  - M3, gate row MAX instead of MAX0: budget_raise_gate 240 checks, 1 failed.
  - M3b, gate row deleted: 1 failed.
  - M4, bounds check dropped: 1 failed.
  - M5, `>=` for `>`: 4 failed.
  - M6, record carry-over dropped: 1 failed.
  - The worktree is clean afterwards.
- Self-tests at the head: `ci-ratchet self-test: 45 checks, 0 failed` and `budget_raise_gate self-test: 240 checks, 0 failed`.
- compare() and the null control at the head budgets vs the same table without the band (ev/null-control.txt):
  - 34.467: ok with the band, GREW without it.
  - 35.567, the edge: ok with the band, GREW without it.
  - 35.777: GREW both ways.
  - script_runs_per_push 55: GREW both ways.
  - archscore.unused_boundary_imports 1: GREW both ways.
  - So the band applies to critical_path_minutes only, and the counters stay at zero tolerance. budget_problems(head) is [].
- budget_raise_gate treats a missing band as zero. CI job 124640032305 prints `RAISE tests/ci_budgets.json: critical_path_minutes_band: None -> 1.3`, and the self-test passes "a critical-path band added is a raise (absent is a band of zero)".
- Band 1.3, not re-derived by me this round. This seat has no `gh` for `--gather-runs` (only search is permitted). Between b02ffd170 and this head, nothing changed in the band value, in run_minutes or in the input set. Round 1 re-derived it from the body's own 86-run query: `RESULT n=86 median=32.550 p90=34.267 sliding8 ... max|dev|=1.300` (review/3045 f7c7d4c6, evidence/band-1025.txt). I rely on that measurement and do not re-certify it.
- Red checks at the head:
  - `budget-raise-gate` is red: `REFUSED: tvofi's approval is on b02ffd170d50, not this head 9ef51b8215dd`. The body answers it under `## Red checks` as red by design until approval at the head. It needs tvofi's re-approval after the body edit.
  - The main-side `tests / ci-ratchet` red is answered there too.
  - `merge_train.py classify 9ef51b8215dd7216950f177386fb2f5a8f010a47` exited 1 at 20:25:21Z with `RED 9ef51b8215dd7216950f177386fb2f5a8f010a47 pending: none red: gate` (ev/classify-log.txt).
  - The `gate` job 124647791391 names its only failure: `FAIL budget-raise-gate / budget-raise-gate: failure (this run)`. budget-raise-gate 124647394312 fails on the stale approval, and the body answers that red.
  - pr-contract 124647618162 succeeded at 20:23Z, after the last red concluded. arch-score 124647394298 succeeded. No other check is red.
- Merge: `git merge-tree --write-tree origin/main 9ef51b8215dd7216950f177386fb2f5a8f010a47` gives tree ac49332ac at exit 0 (ev/merge-tree.txt).
- Claims and versions: tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to the merge base. VERSION, manifest.json and RELEASE_NOTES.md are untouched three-dot.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Roles: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Scoped-gate MODE line: not read. The gate is CI's heavy run and is not re-run by this seat.
- Head line: the body names 9ef51b8215dd7216950f177386fb2f5a8f010a47, which matches the head I measured.
- Harness: no committed finder harness is named, because this is a red-main hotfix. The mutants (/home/user/mut.py, inlined in ev/mutants.txt labels) and the null-control snippet are mine, not the fixer's.
