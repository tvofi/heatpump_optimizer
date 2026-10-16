Fix review: merge 788c116a408a37b6b276adf95fd17ba69f333fb0

bus-nonce: 1ce523d5f3f11a8ca9c075b23590bea3

This review covers the wording delta only. I reviewed from a detached worktree at 788c116a408a37b6b276adf95fd17ba69f333fb0 and re-read that head before posting. The roles diff against origin/main is empty.

**The authored delta** is 411cbe61b, which changes two files:
- `tests/card.mjs`: 4 lines added, 3 removed.
- `dev/programme/delivery/2283.md`: one line.

da499aa4a merges it, and 788c116a4 merges origin/main 03ee0f998. The card blob is still cb4035b6.

## The three over-claims from the last verdict are closed

1. **The check is renamed to `no press throws`.** It measures exactly that:
   - RESULT `T1b_census_only_throw_on_press` rc=1 fails=1, on `FAIL no press throws`.
   - RESULT `K1_navigation_api_in_try` rc=0 fails=0. That is the listed gap, and the name no longer claims it.
2. **The comment header is now `Part of a browser's navigation surface, inert`.** It names the four primitives it adds (history, open, location, window dispatchEvent) and states that the Navigation API's `navigation` is not among them. This matches the block's code.
3. **The title has been retitled**, to `R10-DEEPLINK: one card helper for HA deep links, with direct checks on its routes`. The delivery row carries the same title.

**No old wording remains.** A grep of `tests/card.mjs`, the driver, the delivery row, the card's `www/` and the PR body finds none of "primitive is swallowed", "every link button", "complete and inert" or "every link a button".

**No check logic changed.** The diff's only code-line change is the string argument of one `check(...)` call.

## Other checks

- **Card test**: `node tests/card.mjs` prints ALL CARD CHECKS PASSED at the head, after `plan_view.py`. The null control gives RESULT `NULL_no_plant` rc=0 fails=0.
- **"Part of #2253"** still holds. #2253 is now OPEN again, so the body's "stays open here" is true.
- **Forward-carry**: R10-DEEPLINK-CENSUS is on origin/main, and #2317 is open.
- **Release files** are untouched against the merge base, and `git merge-tree --write-tree origin/main HEAD` exits 0.
- **The body's Head section** names 411cbe61b, merged into ef47407a0 and then with origin/main 03ee0f998, which matches `git log`. It says the mutation proof was taken at 974af2ca3. That holds, because the check logic has not changed since.
- **CI**: all 45 check-runs at 788c116a4 have concluded, 30 success and 15 skipped, none red. The body's `Red checks: none` holds.

Rounds 4 and 5 confirmed the substance of the narrowed claim: every listed gap passes, and every claimed check is red under its plant. The instrument `mut4.py` is my own.

Evidence (relative to the scratchpad, under `rev-2283-r6/evidence`): `mut4.py`, `mut4_r6.txt`, `card_head.txt`, `check_runs.txt`, `HEAD_MEASURED`.
