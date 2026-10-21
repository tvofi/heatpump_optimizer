Fix review: blocked 441d19932f40475ddc0420f3b67ba8d90202eb2c vacuous-test: MB5 (monthly_held_cost_delta read from predicted_cost) passes every check; MX1 (tiles dropped from the ledger save) passes too; carries to R10-UX-HEALTH and R10-LIVESTATE are not in the roster

bus-nonce: cecf419ef61f5daf10cddb3679e265ca

Round 1: the first review of this head. Measured at `441d19932f40475ddc0420f3b67ba8d90202eb2c`, a `mutation-autofix` bot commit (`ci: pin killed mutants`, 16 `killed_by` files only) on top of the body's `21eeb5b23`. Code head `cd1c837ca`. Merge base `e7c664856`. Re-read the head before posting: it was still `441d19932f40475ddc0420f3b67ba8d90202eb2c` (`ev/head-at-post.txt`). Role file: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so my copy is current.

## Blocking

1. **Step 1: a mutant on the line item 8 rests on survives (MB5, the body's own mutant).** I replaced `simulated.baseline_cost - result.baseline_cost` with `simulated.predicted_cost - result.predicted_cost` in `async_simulate`'s `monthly_held_cost_delta` (coordinator.py:11095), exactly as the body describes. Result: `python3 tests/features.py` gives `ALL 4276 FEATURE CHECKS PASSED` and rc 0 (`ev/mut-MB5.log`, `ev/mut-MB5.diff`, finished 16:45:46Z). The body says `#2257: at the real what-if seam …` kills it (+25.16 / +148.33). That check is the only one that reaches this line at a real seam. The `held figure, the cap tile the plan's` check reads `monthly_figure`'s key choice, not this line. And the body itself says the check depends on the clock: `_solve_coord` "anchors its horizon on the real clock; each run reads its own". At my run's clock the plan's single-solve pair came out monotone and convex, so the check passed. MB2 shows the same thing: at 16:34Z this check was `ok` under MB2, not red as the body records. MB2 is still killed by three other checks. So whether the PR's central change can be reverted unnoticed depends on the time of day the suite runs. The fix needs a check that pins this line without depending on the clock. One option: a fixed-clock seam, or a what-if pair whose plan delta and held delta differ in sign by construction.

2. **Reviewer's class attack: deleting the persistence leaves every check green (MX1).** The body says "the days persist with the ledger, so a restart does not start the mean over". I deleted `"price_tiles": price_tiles.book(self),` from `_async_save_ledger` (coordinator.py:7918). Every script that reads `price_tiles` stays green: `tests/features.py` ALL 4276 PASSED, `tests/finite_boundary.py` ALL 106 PASSED, `tests/entities.py` ALL 2375 PASSED (`ev/mut-MX1*.log`; the `fails=46` in `ev/mutants-other.txt` is my grep counting `FAIL` inside passing check names, and the log ends `ALL 2375 ENTITY CHECKS PASSED`). The load side is pinned: MX2, deleting the `price_tiles.restore(...)` call, passes features.py but fails finite_boundary's `the healthy rich seed round-trips unchanged … [changed=['ledger']]`. Nothing pins the save side. A check is owed that saves, reloads and reads the same published mean.

3. **Step 10: carry-missing. The forward-carries are not carried to R10-UX-HEALTH or R10-LIVESTATE.** The body routes both by `Carry:` markers (items 6ce59610, 4c077302) and says "the orchestrator writes the roster brief". At `origin/handoff/audit-r10-roster` `f424d993d15f9ba103680ecf88a710539f789bcf`, neither group's `brief` or `carry` mentions `open_options`, `advisor:settings`, `_price_tiles` or `price_tiles.book`. `git grep` across the roster's `dev/programme` finds neither term (`ev/carry-destinations.txt`). Both groups are `not-started`, so both are live destinations. `finding-propagation.md` says "the producing PR does not merge until the carry is in the tree". Open seams (a) and (b), the Plan page what-if, the fuse advisor and the gap/DHW rows, are marked `dismissed:` to a "Phase 1b roster burst". That burst has no file in the tree either. The same rule sends a sibling seam to a new issue or a carry file. This is the orchestrator's write, not the fixer's code, but it gates `merge`.

## Non-blocking

- **MX4 survives.** Replacing the mean of daily means with a pooled mean (`sum(sums)/sum(counts)`) passes features.py, because the horizon check folds exactly two samples into every day, so the two estimators agree. The check named `… publishes the mean of their daily means` cannot tell them apart. Carry: R10-ADVISOR
- **The null bounds the held figure per delivered degree, but the tile is read per degree of setting.** In the `null` arm the plan delivers −0.514 K and +0.327 K per degree of schedule moved, at +59.4 per delivered degree. Over a three-day loop, moving the setting a degree therefore changes the bill by roughly 30 and 19 SEK a month, against the tile's 54.4. The body states the delivered fraction, so this is disclosed. Whether three days reaches steady state is not shown. Carry: R10-ADVISOR
- **The harness is the fixer's own (step 9).** The finding has no committed finder harness: the owner's screenshot. `dev/audit/harnesses/r10_advisor_degree.py` was written by the fixer. The body presents it as "the instrument" without saying it is the fixer's own. The carried null harness, `r10_sav_null_terms.py const`, is untouched by this diff. I ran it at both ends and it reads identically, with timing +0.00 % (`ev/finder-null-terms-const-{base,wt}.txt`). That is flat by design, because the plan is unchanged. Carry: R10-ADVISOR

## RESULT lines (mine)

```
RESULT merge-tree origin/main 49c222280 + head: rc=0 tree 5c574eb26ef5 (no conflict, no MERGE-CLAIM line)
RESULT version/manifest/notes heading: untouched (empty three-dot diff)
RESULT head node tests/card.mjs: ALL CARD CHECKS PASSED
RESULT head python3 tests/features.py: ALL 4276 FEATURE CHECKS PASSED
RESULT mutant=MC1 rc=1 fails=5   (body: same 5 names)
RESULT mutant=MC2 rc=1 fails=1   (body: same)
RESULT mutant=MC3 rc=1 fails=2   (body: same)
RESULT mutant=MC4 rc=1 fails=2   (body: same)
RESULT mutant=MB1 rc=1 fails=4   (body: same 4; real-seam held 0.0/0.0)
RESULT mutant=MB2 rc=1 fails=3   (body names 4; the real-seam check was ok at 16:34Z)
RESULT mutant=MB3 rc=1 fails=1
RESULT mutant=MB4 rc=1 fails=1
RESULT mutant=MB5 rc=0 fails=0   SURVIVES (body: killed by the real-seam check)
RESULT mutant=MX1 (ledger save drops price_tiles) features rc=0, finite_boundary rc=0, entities rc=0  SURVIVES
RESULT mutant=MX2 (restore call deleted) features rc=0, finite_boundary rc=1 (round-trip null control)
RESULT mutant=MX3 (weekend/holiday casts deleted) rc=1 fails=1
RESULT mutant=MX4 (pooled mean) rc=0 fails=0  SURVIVES
RESULT mutant=MX5 (fold keeps days past the horizon) rc=1 fails=1
RESULT mutant=MX6 (no-heating null-row guard deleted) rc=1 fails=1
RESULT fixer harness r10_advisor_degree.py days null timing at head: every RESULT line the body quotes reproduces exactly
  (days base 5/40 non-monotone, std 48.5/48.6; head 0/40, std 29.6/29.5; published 0/11, std 1.1;
   null −0.514 K / +0.327 K delivered, truth +59.4, held +54.4 (−8.4 %), first_solve +145.6 / +85.1; timing +1.3 / +40.8 vs held +54.7)
RESULT finder null harness r10_sav_null_terms.py const: base == head, timing gain +0.00 %
RESULT card_drift.mjs vs e7c664856: 1 state moved and claimed (advisor_page), 39 identical
RESULT class rule 1 (inbox builders): 6 lines / 5 builders, same as the body; rule 2 (monthly scaling): price_tiles + async_simulate + card DAYS_PER_MONTH, same as the body
RESULT advisor:settings PENDING row: deleted; only health:settings (R10-UX-HEALTH) remains
RESULT CI at head (81 check runs, all concluded): only nightly-status red
```

## Steps

- **Step 2/3:** no finder harness exists (see the step 9 note). I ran the carried null harness at both ends (flat), and the fixer's harness at the head (all quoted figures reproduce).
- **Step 4:** `card_drift` matches the one claim. `env_drift --all` against the merge base: `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`, rc 0 (`ev/env_drift.txt`). The solver claim file is untouched, and that is correct.
- **Step 5:** untouched.
- **Step 6:** both rules reproduce, and the seams are dispositioned in the body. The rules' only open seams are those whose destination is missing (blocking item 3). My widened grep also found `coordinator.py:9124`, a kWh month extrapolation that is not a what-if. It is outside the class.
- **Step 7:** the body's head section names `21eeb5b23`. The head adds only the `mutation-autofix` pin commit, which `ci-autofix.md` treats as a carry.
- **Step 11:** `nightly-status` is red on main's nightly lanes (`mutation-nightly`, `slow`, run 39563978649), which this diff does not reach, so it is not this PR's. Every other check is success or skipped. CI's `mutation` lane is green, but its operators do not include MB5- or MX1-shaped edits.
- **Step 13:** clean.
- **Step 14:** `structure_budgets.json` only lowers four rows. Those rows are earned by moving the tiles' state into `price_tiles.py`: put `_price_tile_specs` back on the class and the LOC returns. Seam map: one entry removed, with the method.
- **Step 15:** the store and payload hunks serve the tile seam. No breach found.

bus: verdict/2572 at c83ed4d8eeac260bd91540d0bfe2832ee2423c7d, confirmed from cloud (review/2572 at 01f1d4200cfad5247da4ab490daeab10813b01b8); evidence: ~/.zcode/bus/verdicts/2572/c83ed4d8eeac260bd91540d0bfe2832ee2423c7d/evidence

