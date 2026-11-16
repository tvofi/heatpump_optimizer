Closes #3636

"Apply this plan" failed whenever the published plan had a run starting 20 hours or more from now. The card's `apply()` trimmed the draft at the edit floor only, so it sent runs past the manual-plan window that the editor itself would not let the user touch, and `build_override` in `manual_plan.py` refuses any slot starting past now plus the window. The card now drops every run starting at or after `ceilingParts().applyEnd` (now plus the published `manual_plan_window_hours`) less `APPLY_CLOCK_SKEW_MS`. It does not use `editCeiling`, which also takes the zoomed visible end into account, so a zoomed-in view does not change what is applied. The lower bound is unchanged. A run straddling the window is still sent whole, because the backend frees every step past the expiry itself. The backend refusal is untouched: it protects the stored plan across restarts.

Clock skew: the card measures the window from the browser's clock and the service measures it from the server's. `APPLY_CLOCK_SKEW_MS` is one plan step (`PLAN_STEP_MS`). Runs start on step boundaries, so holding back a run that starts in the last step before the ceiling costs at most one step of pinned time before the expiry, and a browser clock up to one step fast is still accepted. If the browser clock is slow, the card only drops runs the server would also have accepted, so nothing is sent that the server refuses. Alternatives considered: (a) relaxing the backend refusal, which the brief rules out because a slot starting past the window corrupts the stored plan at the next restart; (b) clamping a run's start to the ceiling instead of dropping it, which would invent a slot the plan never had; (c) no skew allowance, which leaves the reported failure reachable on any browser clock that runs fast (mutant M2 below).

No user-facing text changes. Release note for the stamper: credit the reporter, GitHub user rasenschachmatt, for the report and the suggested fix.

## Head

9f66f1cc43563528dbf526bc5e2ba83c696210fb, measured against origin/main 5825e1346c14eecace5c87c046558774145a94dc at 2026-11-15T23:10Z.

## Mutation proof

Run in a detached worktree at the head, `HPO_PLANDATA` pointed at the payload `tests/plan_view.py` wrote, then `node tests/card.mjs`:

- M1, the new predicate removed (`.filter((r) => r.end > lo && r.start < hi)` changed to `.filter((r) => r.end > lo)`): `3 CARD CHECK(S) FAILED` — `no slot sent starts at or after the manual-plan window (#3636)`, `a run straddling the window is sent whole, later ones dropped (#3636)`, `a run starting within one step of the window is held back for clock skew (#3636)`.
- M2, `APPLY_CLOCK_SKEW_MS = 0`: `1 CARD CHECK(S) FAILED` — `a run starting within one step of the window is held back for clock skew (#3636)`.
- Unmutated, same worktree and payload: `ALL CARD CHECKS PASSED`.

The same three checks fail on the merge base with the new test applied (failing test first). The fix adds no `.py` lines, so `prepr.sh`'s mutant draw has nothing to draw.

## Null control

The captured plan ends inside the window (checked: `the captured plan ends inside the window (#3636)`, planEnd < ceiling minus one step). Its payload is compared byte-for-byte with the payload from the same plan when `manual_plan_window_hours` is 1000, which is too wide to bind. Both are produced by production code: `a plan wholly inside the window sends the same payload (#3636)` passes at the head. It also passes under M1 and M2. The existing checks in the apply block (`it never tries to reschedule the past`, `no slot is sent past the expiry`) pass at the head as well.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
<!-- figure-block: scope-line mb=5825e1346c14eecace5c87c046558774145a94dc head=9f66f1cc43563528dbf526bc5e2ba83c696210fb -->
~~~text
MODE: SCOPED -- 9 script(s) run, 24 scoped out.
~~~
<!-- /figure-block -->
- `node tests/card.mjs` at the head: `ALL CARD CHECKS PASSED`. At the merge base with the new test: the 3 #3636 checks named above fail, and the other 3 #3636 checks pass.
- Other scoped scripts at the head, `PYTHONPATH=tests/hastub`: `tests/arch_score_head.py`, `tests/deployment_shape.py`, `tests/doc_claims.py`, `tests/harness_headers.py`, `tests/plan_view.py`, `tests/features.py` (`ALL 5710 FEATURE CHECKS PASSED`), `node tests/card_drift.mjs` each exit 0, and `tests/entities.py` prints `ALL 2723 ENTITY CHECKS PASSED` and exits 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL` (the diff touches only the card JS and its test).
- Seam enumeration for the class (every in-tree caller that sends slots to the service): `git grep -n '"apply_manual_plan"' -- custom_components/heatpump_optimizer/www` returns one call site, `ManualPlan.apply()` in the card, which this diff closes. The service is also reachable by hand from Developer Tools; slots sent that way are validated by the same `build_override`, which refuses them with an explicit error, and that refusal is unchanged.
- Finder's harness: none. #3636 is an outside report with no harness; the reporter's repro is encoded as the seeded-plan checks above.

## Red checks

none

## Forward-carry

none

## Friction

none
