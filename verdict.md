Fix review: merge 8050a943c21757575afb59fd2b5d7125714fff9b

bus-nonce: f140c868b4b1751fef5ec410f3e6ef33

CI-only re-check of #3195 at the bot pin commit, as briefed. The prior verdict (verdict/3195, head 611e1aa6f) blocked on `ci-red` only (`tests / mutation` unpinned-site refusal). I did not re-review the code.

## Findings

- Residual: M2 still survives (two-zone `zone = lowers` -> `zone = rooms`, `optimizer.py:468`). The body now routes it under `## Forward-carry`. Carry: R10-SAV-COMFORT
- Residual: the comfort loop and baseline check in `tests/features.py` abort uncaught on a crashing mutant (`optimizer.py:454`, `:515`), so later checks go unrun. The body's "a mutant that crashes fails a named check" holds only for the state-field checks. Carry: R10-SAV-COMFORT
- Follow-up: the body's M13 (`baseline_kw` end to end), M3 (midpoint rule) and M9/M10 (calibrated-month scaling) test gaps, plus carry 5 and the summer start-bound limit. Carry: #2492
- Follow-up: `COST_RUNNER_CLASSES` has no band for `ref_ms` about 20.3-20.7 (red at 611e1aa6f; green at this head). Belongs to the replay cost budget's owner. Carry: R10-REPLAY-COST-BUDGET

## Evidence

- Step 1: `review_carry.py 611e1aa6f 8050a943c` prints `CARRY` (1 branch-only commit, `8050a943c ci: pin killed mutants`) (`ev/review_carry.txt`).
- Step 2: `merge_train.py classify` exited 2 (`REFUSE ci: the check runs ... could not be read`) on every run. The cause is the sandbox proxy: `gh api --paginate` follows numeric `repositories/{id}` links and gets HTTP 403. So classify is unreadable here. I read the head's check runs myself with explicit `page=1` and `page=2` (`ev/check_runs.tsv`, 107 rows, matching `total_count` 107):
  - Every `gate` run of this head is `completed success`: 127074091068 (run 41975396780, the current one), 127073162987, 127073153324, 127073136092.
  - `tests / mutation` is `success` (both rows); `prelude` is `success` (4 rows). `tests / replay` is `success` in run 41968562933; its other row is `skipped`.
  - `tests / mutation-pins` and `tests / mutation-autofix` are `skipped`: with the pins committed, there is nothing to pin.
  - Nothing is queued or in progress.
  - Two rows are red, and neither is this PR's: `tests / nightly-status` (grades main, inherited) and `governance / delivery-status` (OVERDUE on other PRs' rows, per verdict/3195). Neither feeds `gate`, and `gate` is green.
  - I judge the head GREEN from these rows, not from classify's exit code.
- Step 3: the PR body's `## Head` names `8050a943c21757575afb59fd2b5d7125714fff9b`. `## Red checks` names the `tests / replay` runner-band red at 611e1aa6f and carries it to the replay cost budget's owner. It names no red at this head. One stale sentence remains: "The final head above has had no CI yet". It is now untrue, and harmless.
- Findings routed by verdict/3195 are carried in the body: M2 and the runner band as above, and M13, M3, M9/M10 under `Carry: #2492`.
- The body's figures were re-derived at 611e1aa6f in verdict/3195. The only change since is the bot's 11 `killed_by` anchors.
