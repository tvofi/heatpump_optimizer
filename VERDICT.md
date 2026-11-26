Fix review: merge 2003bbb48cc1b0d70edf0a39b2264aa4c9a533b4

bus-nonce: a66b1b136e5cfdd874976cb97d09e4da

## Scope

This is a later round over the last merge verdict at `b2b6ff8c93` (probe `rev-3805-e9835d83`). `review_carry.py b2b6ff8c93 2003bbb48c` prints `FRESH-REVIEW`. The PR's own diff moved in seven files. None is under `custom_components/`, so the scope is not widened (fix-review.md step 12):
- `tests/features.py`, commit `4967642106`: the combi exchange-exit check now hands the exchange injected builds (one plan that repeats, one that alternates) instead of relying on whether the unengaged solve converges, which depends on the BLAS build.
- `docs/architecture.md`, commit `a6d8334a46`: the HA-free module count goes from 66 to 67.
- Count re-records forced by the main merges: `dev/audit/rounds/round4/D6/claims.{py,md,json}`, `tests/deployment_shape.py` and `tests/closures.json`. These come from main's `flow_limit.py` landing alongside this branch's `dhw_charges.py`.

## Evidence

- CI: `merge_train.py classify 2003bbb48c --pr 3805` printed `GREEN 2003bbb48cc1b0d70edf0a39b2264aa4c9a533b4 pending: none red: none`, rc 0 (ev/classify.txt). There are no reds, so no `## Red checks` answer is owed.
- Merge with main: `git merge-tree --write-tree origin/main 2003bbb48c` exits 0 with no conflict, and the ledger driver merges `tests/closures.json` as a set (ev/merge-tree.txt).
- Mutation proof of the rewritten check, in each case `tests/features.py` run in full on a copy of the head (ev/features-*.txt):
  - Unmutated: EXIT 0, and the check reads `ok combi: the exchange leaves its rounds ...`. The previous round's note said this check failed in block mode at `[4 of 4]` on this box; it now passes here.
  - Mutant `optimizer.py:2092` early exit replaced by `if False:` (never leave the rounds): EXIT 1, `FAIL ... [repeating 4, alternating 4 of 4]`. Killed.
  - Mutant `optimizer.py:2092` early exit replaced by `if True:` (always leave after the first round): EXIT 1, `FAIL ... [repeating 1, alternating 1 of 4]`. Killed.
  - The check therefore tells a working repeat exit apart from both a missing exit and an unconditional one.
- Figures re-derived at this head:
  - `docs/architecture.md` "other 67 modules": an AST census of the package finds 104 `.py` modules. 36 import `homeassistant` at module level, and one, `inputs.py`, imports it only inside a function. 104 - 36 - 1 = 67. Matches.
  - `claims.py` reports `RESULT arch_modules_on_disk=104`, `arch_map_listed=104` and `claims_false=0`. Matches the C32/C33 rows and the docstring's 104.
  - `tests/deployment_shape.py`: the counts of 123 files and 186 of 561 pairs are pinned by that script, which ran green in CI at this head. Not re-run here.
- Prior findings: the round-6 block-mode note on the combi check is settled by `4967642106` (it passes above). The review-packet note is not settled; see Findings.
- Review packet: `review_packet.py render --pr 3805 --head 2003bbb48c --reviewed-head 2003bbb48c` still refuses with `UNAVAILABLE: git merge-base --is-ancestor b2ce461c origin/handoff/audit-r11-roster: fatal: Not a valid object name b2ce461c`, and writes no packet. This review ran without a packet; its scope was derived by hand as above.

## Findings

- Note: review-packet: `review_packet.py` still reads the body's roster item id `b2ce461c` as a commit and refuses. This is the fifth round of this PR with no packet. The same defect was reported last round, and its root-cause seat belongs to the orchestrator. Carry: dismissed: dispatch-side instrument defect outside this diff, already reported with round 6's verdict

## Friction

- `fix-review.md`: `cost`: the dispatch names the head itself as the reviewed head. The real previous verdict, at `b2b6ff8c93`, had to be recovered from the probe refs before the delta could be cut. Carry: dismissed: one occurrence in this round
