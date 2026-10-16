Fix review: merge 5c50fd3e0ae6e8b8bae463ba14fff8be6529b84e
bus-nonce: d47312c92419bdced6bb0f7609898ed5

Round 1 (one review; the head moved only by record, merge-main and pin commits, each judged as a delta).

Measured head: 5c50fd3e0ae6e8b8bae463ba14fff8be6529b84e, the merge-main bot's clean merge of origin/main into 21397979934cc3c41518bfa094f462598be7c270 (the head the coordinator's dispatch named). Its tree equals `git merge-tree` of its parents. Main brought coordinator.py, store.py and 7 other production files from other PRs. The `_roll_month` loop and the `peaks/closed_*` domains survive, and at 5c50fd3e0 I re-ran the #2230 block (12 passed), the bill harness (24 of 24), my attack harness (0 of 18 failing) and structure.py (passed; max_class_loc 8688 is main's own lowering, and duplication stays 35). The PR's own production diff against its merge base (5 files, +223/-239) is line-for-line the one at 793116abd, where the full measurement ran; every other production change since is main's. Every merge on the range (5f2371e69, 1c4d6c2f3, 7030273c3, 213979799, and earlier e93e8a8c2, d114395e6, f09549085) equals `git merge-tree --write-tree` of its parents. Base: merge base b22db919d, production identical to 5603ee319.

## Mutation proof (step 1)
The #2230 features block passes unmutated (`ALL 12 FEATURES BLOCK PASSED`, re-run at 21397979). Each of the body's five mutants was applied to an export and then restored:
- M1 drop `_close_window` at rollover: rc=1 (last window 1.0, restart 1.0)
- M2 retention -> `pass`: rc=1, plus the tracker null FAIL
- M3 `if self.closed_month:` -> `if False:`: rc=1, the same two FAILs
- M4 `closed_month` out of `as_dict`: rc=1 (last window 5.0, restart 1.0)
- M5 `_roll_month` books `[-1:]` only: rc=1
My own M6 (drop `closed_peaks` in `from_dict`): rc=1 (restart 0.0).

## Finder harnesses, base -> head (step 2, 3)
RESULT month_last_window.py last_window_reached base=0 of 24 head=24 of 24; --perturb 24 of 24 at both ends
RESULT r10_month_last_window_billed.py billed_spike_reached base=0 of 24 head=24 of 24; --null 24 of 24 at both ends; finder's one-line shape on base 0 of 24
RESULT equiv_peak_billing.py (P5, head vs base) values_compared=1536 mismatches=0; identity 0; perturb (peaks_averaged+1) 274
RESULT equiv_tariff.py (01b, a7e32fbba vs base) probes=8160 mismatches=0 parity_failures=0; perturb 920; identity 0
RESULT equiv_cyclic_range.py tokens=522 mismatches=0; --break 487; identity 0
I edited the equivalence harnesses only to take exported trees as base and head instead of git refs; the copies are in evidence.

## Attacks (step 6), reviewer-built harness evidence/reviewer_attack.py (mine, not the finder's)
RESULT attack_cases=18 failures=0 at head (17 fail at base)
- DST month ends 2024-03, 2027-10, 2029-03 and 2030-03, each with 15- and 60-minute windows: 5.0 billed
- k=3 distinct days, with and without a peak on the last day: 4.33; k=3 with distinct_days off: 4.5
- A restart (JSON round trip of as_dict) at each of the 6 steps between the rollover and the freezing settlement: 5.0
- A month masked out by peak_tariff_months: 0.0 booked, and the next month is clean
- Store: `peaks/closed_month` and `peaks/closed_peaks/#` are declared in store.py. The keys are additive and `from_dict` defaults them, so an old payload loads and no version bump or migration is owed.

## Architecture (steps 14, 15)
- The coordinator `_roll_month` hunk is one loop that books `PeakTracker.billing_statements`. All computation stays in the tracker. Sound.
- P5: `_peak_billing` maps each old argument to the record field it replaces, and every caller in the tree uses the record.
- structure.py measures duplication_copies 37->35 and max_class_loc 8705->8703. The two clone classes that disappear are the grid_fee month/day parsers (07) and `_day_peaks_batch`'s copy of the plateau rule (01b), so the movement is the change's own.
- `score.py --diff b22db919d HEAD`: dS +0.9094 IMPROVES (duplication 68->66 +0.3789, params_over_10 12->8 +0.5305). The PARAMS_OVER_10_LEFT rows retired are exactly the four P5 functions.
- Mutation ledger: the 11 removed killed_by rows name sites the refactor deleted; the one re-keyed CLAMP_DROP argument holds at the new text. `ledger_form_problems` and `completeness_problems` both return [] at the base and at 21397979.
- Pins 4aaea2d07: the 28 killed_by files equal, key for key, the union of run 38796525102's six `mutation-pins` artifacts (every status `measured`, every head f09549085). Nothing is pinned that was not killed, and nothing killed is left unpinned.
- Triage a8df7964e: I re-derived the 3 `equivalent` verdicts. `_peak_charge` CLAMP_DROP holds because a k past the width takes the exact whole-array sum in both arms. `_peak_excess` CMP_BOUND and GUARD_OFF hold because a 0 price charges 0.0, an inf or NaN threshold yields None, and a negative price is unreachable through the options bound. All three assume a finite plan, which is what the solver produces. The 2 `gap` verdicts are real, measure-zero, and were unpinned at the base under the pre-refactor text.
- closures: the two inert_reads entries are real reads by tests/harness_headers.py. `closures` was green at 532eb85d3, so no INERT READS red ever ran and there was no bot repair to read.
- P2 twin census r10_weekday_range_twins.py: pairs=49, identity 0, --perturb 49. The two cyclic_range_wrap dispositions in tests/entities.py now name #2238 / R10-ARCH-SHAPES.

## Body, forward-carry, red checks (steps 7, 10, 11)
- The ## Head section names 21397979934cc3c41518bfa094f462598be7c270. I re-derived its production stat (5 files, +223/-239 against the merge base) and its services.py note.
- Null control: the local pin run's refusal is disclosed, and the pins that landed are CI's measured kills, not the local run's.
- The forward-carry is in the tree on main (via #2277): R10-LEAF-IMPORTS and R10-SOLVER carry the PeakBilling constraint, and R10-ARCH-SHAPES carries the weekday twin with its harness and the instruction to remove both dispositions.
- Red checks: `mutation`, `pr-contract` and the pin-chain reset are each named and answered.
- VERSION, the manifest version and the notes heading are untouched (the pr-contract version-edit step agrees).

CI at 5c50fd3e0ae6e8b8bae463ba14fff8be6529b84e (check-runs API, 74 runs): all 17 required checks are completed success, and no run at this head is red or cancelled. The `mutation` lane is conclusive (not INCONCLUSIVE): 4430 unpinned against 4463 at the ratchet base, the ledger agrees with the inventory, and the NULL_COMMENT null control survived every driver.

Not verified by me: the heavy CI lanes (golden, optimality, stress, the mutation table). I cite their check-runs at this head, per tvofi 2026-09-30.

Non-blocking notes, not owed here:
- (a) Patch 01b, as prescribed, copies the scalar's #925 bracket comment and docstring paragraph into `_smooth_topk_sum_batch`, where the base had a one-line pointer. This is a D5 prose duplicate.
- (b) Each settlement re-books the closed month's capacity line through the following month, into a month whose receipt is already frozen. The writes are idempotent, and no reader sees them.
