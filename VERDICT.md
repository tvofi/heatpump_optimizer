Fix review: merge 4bf7c2eaa95b3b4463ba273e3ca4c230c435e32b
bus-nonce: 606bc2c9d418ef82dcd2b778a294c950

Round 5 of PR #2745 (R10-SAV-COMFORT): a fresh review of the round-4 re-cut. Head measured `4bf7c2eaa95b3b4463ba273e3ca4c230c435e32b`, still the PR head at posting. Merge base `3b4180dcc680e2e2e06f4d8ed0a0839a7374d78f`; three-dot diff 49 files, +841/−320. Measured from a detached worktree at the head, with scratch worktrees at the round-3 head `3b55da2c6` and at the `origin/main`-merged tree (`git merge-tree --write-tree` → `7671889f3`, then `git archive`). CI's heavy runs are cited, not re-run (fix-review.md step 11); my own runs are the finder's committed bytes, the committed probes and targeted checks.

## RESULT lines (mine, on the finder's `r10_sav_baseline.py`, sha1 `bc31f356191ededbfb0b15f768b258249867b134`)

MERGE BASE `3b4180dcc`:
- transient SOUND: 2.06 kW at all four starts, spread 0.00 kW
- cost SOUND: receipt `total_sek` 15.0 = row `actual_sek` 15.0
- coverage SOUND: 28.00
- null DEFECT: baseline 154.1, actual 137.41, saved 16.69 = **10.83238932735682 %**
- `arms run 4, defect 1: null`

HEAD `4bf7c2eaa`:
- transient SOUND: 2.06 kW at all four starts, spread 0.00 kW
- cost DEFECT: receipt 15.0 vs row 4.2
- coverage SOUND: 28.00
- null DEFECT: baseline 154.1, actual 137.41, saved 16.69 = **10.83062946138871 %**
- `arms run 4, defect 2: cost null`

FINDER'S HARNESS BYTES against the ROUND-3 PRODUCTION TREE `3b55da2c` (evidence `finder_r3_transient.txt`, `finder_r3_null.txt`):
- transient DEFECT: 1.95 / 1.90 / 1.88 / 1.95 kW, spread **0.07 kW**
- null DEFECT: **6.179161545814557 %**

The round-3 tree carried a re-specified harness, not these bytes: it scored the transient arm green by measuring step 0 against that plan's comfort-matched target — the dependence on the start state the arm exists to catch — and printed the 0.07 kW spread beside it as a diagnostic. Running the finder's own bytes against the same production code restores the defect, which is what the round-4 block said the re-specification had hidden.

`origin/main`-MERGED TREE (`git merge-tree --write-tree`, 281 main commits past the merge base plus the head; tree `7671889f3`, exit 0, no `MERGE-CLAIM` line):
- all four arms byte-identical to the head: transient SOUND 0.00 kW; cost DEFECT 15.0 vs 4.2; coverage SOUND 28.00; null DEFECT 10.83062946138871 %. The merge train's merge moves none of them.

Probes at the head: `r10_sav_null_terms.py` default — booked 128.4 kWh, plan 114.5, gap 13.9; steady at target 128.4, steady at the delivered room 121.7, comfort 6.6; plan vs steady at the delivered room −7.2 kWh (+5.64 % of steady_at_target); 23.7 kWh_th of stored heat drawn beyond the thermostat's (the probe's sign is −23.7); power-weighted COP 8.383 vs 7.149 (+17.27 %). Its `const` arm — outdoor at the window mean — gap 15.6 = comfort 5.1 + start drawdown 10.1, timing **+0.00 %**. `r10_sav_volume.py` — flat SOUND, saving 0.0000 at `meter_calibration` 1.56; vary SOUND, timing +74.88; meter-reads-the-model 48.0 at calibration 1.0. `r10_savings_upgrade_month.py` — rc=0, 2.800 / 28.000 / 2.800.

## Ruling on the flat-price null (the claim to judge hardest)

**The numbers are as stated.** I re-took both ends on the finder's committed bytes: base 10.83238932735682 %, head 10.83062946138871 %, a 0.00176 pp difference — the body's "within 0.002 percentage points" holds.

**The mutual exclusion is measured, not asserted.** I ran the finder's null and transient arms against the round-3 tree, where the comfort-matched reference was in place: transient DEFECT at 0.07 kW and null 6.179161545814557 %. So comfort matching fails the 3.0 bar too, and it breaks #2255's 0.05 kW start-independence. The COP-timing term alone is 7.2 kWh of the 128.4 kWh booked thermostat (5.6 %), above 3.0 %; removing it would delete a real saving the roster carry says "must survive". Both candidate references were measured; the claim that the bar cannot be met while the COP saving and #2255's property both stand is therefore shown, not reasoned. The only part I could not re-derive is the warm-up skip sweep (see Not established).

**The owner's permission is quoted accurately and covers what was done.** The roster carries the binding criterion verbatim (`dev/programme/rosters/wave-r10-groups.json`, tvofi 2026-10-24): "Under one flat price, the volume difference may remain, but timing savings must be 0." The residual at this head is exactly the volume difference — 13.9 kWh (6.6 comfort + 7.2 COP, rounded) — and the timing term measured at one flat price is +0.00 % on `r10_sav_null_terms.py`'s `const` arm, the #2255 harness that is at the merge base and not this branch's (the branch's own `r10_sav_volume.py` reads the same 0.00). The owner's spec also prescribes the reference the re-cut restored ("a plain thermostat over the exact same price profile"). So a control that cannot be met is covered by the owner's recorded decision, not by a seat's reasoning. Not a blocking finding.

## The round-4 block, item by item

1. **The finder's harness is restored, not re-specified.** `dev/audit/harnesses/r10_sav_baseline.py` is sha1 `bc31f356191ededbfb0b15f768b258249867b134` at the merge base and at the head — verified from both blobs, not taken from the body. The re-cut took the restore branch the round-4 verdict allowed, and the body states the null remains at 10.83 % (DEFECT) rather than claiming the arm green. Owed item 1 is answered.
2. **The mutation proof is re-anchored and every live mutant is killed.** `python3 dev/audit/harnesses/r10_sav_baseline_mutants.py` on a copy of the head tree: M0 rc=0 failing=0; M1 6, M2 5, M4 4, M5 2, M7 1, M8 4, M9 4, M10 4, M11 5, M12 1, M13 1, M14 1, M15 1, M16 1, M17 6; M3 and M6 print `RETIRED` with their reasons. The dead-code control holds: counting each base anchor in the file it names at the head gives M1 0, M3 0, M4 0, M6 0, M9 0, M10 0, M11 0, M13 0, M14 0, M15 0 and M2 1, M5 1, M7 1, M8 1, M12 1, M16 1 — exactly the body's set.
3. **The upgrade control is ported.** `r10_savings_upgrade_month.py` runs at the head, rc=0, printing the expected 2.800 / 28.000 / 2.800 (it died at the round-3 head on the renamed `_coverage_factor`).

## Findings (non-blocking; record-only — none changes a measured fact)

**F1. The body's instrument/scenario counts are imprecise.**

- `## Instrument changes` opens "Two files under `dev/audit/harnesses/` differ from the base", but three do: `r10_sav_baseline_mutants.py` (M), `r10_savings_upgrade_month.py` (M) and `r10_sav_volume.py` (A). The paragraph then covers the first two only; the upgrade-month port and the volume probe are described further down. The baseline harness's unchanged sha1 is stated correctly in both places.
- `## Re-cut` (the "per-step inputs" paragraph) says "`env_drift.py --all` reads the tree byte-identical to the merge base on all 56 scenarios, so nothing moved", and the body's own `## Figures` says `claimed_drift.txt` "differs from the base by exactly two lines — `negative_prices` and `summer_dhw_only`". At this head the instrument prints exactly those two `CLAIMED` moves (`negative_prices` savings % −13.19 → 16.17; `summer_dhw_only` −7.62 → 5.88) beside `NO UNCLAIMED DRIFT: 56` and `NO STALE FIXTURE: 56`. The `## Figures` statement is the correct one; the `## Re-cut` sentence contradicts it.
- "`capacity` has 0 occurrences inside `savings_months`" is 1 by literal count: `ledger.py:386`, inside that function's docstring ("capacity, wear, uncovered intervals"). The capacity **code** term and M6's anchor are both 0, so the mutant is dead and the control's substance holds; what is imprecise is the count.
- `## Head` credits `a50fe5146` with "the one-basis ledger and the duty re-freeze". That commit inserts nothing: it deletes three round-3 harnesses (`r10_sav_comfort*.py`) and their three golden pins, 370 deletions in all, and touches no production file. The re-cut's production change is in `0ff823754` (`optimizer.py`, `price_tiles.py`, `tests/features.py`, the golden claims); `ledger.py`, `pump_arbiter.py` and `payload.py` are untouched across the whole re-cut (`3b55da2c6..HEAD`).
- `## Red checks`' replay bullet says "the head is unpushed, so that job has not run on it". The head is the pushed PR head and `tests / replay` is green on it.
- Step 9 disclosure: `r10_sav_volume.py` is the branch's own instrument (added by this diff, `A` at `3b4180dcc..HEAD`), and the body lists it among the harness sha1s and uses its readings without saying so — "(unchanged since round 3)" is the closest it comes. The verdict above does not rest on it (the timing term comes from the inherited `r10_sav_null_terms.py`), and its three readings agree with the finder's arms, but the disclosure is owed.

These are record errors, not measurement errors: every figure the verdict turns on is re-derived above, and the canonical `## Figures`/`## Null control` sections carry the correct data. They should be corrected, but they do not change the fix.

Carry: #2492

## The four container reds, checked at the base (`3b4180dcc`)

All four reproduce at the base in this container, re-taken here from the base worktree:

- `tests/optimality.py` — a fresh run at the merge-base worktree: `1 of 84 OPTIMALITY CHECKS FAILED`, the one `one|summer_negative|shoulder: a recorded claim still has a gap (not stale)` (`claimed but gap 0.0000% is at or below the bar -- the claim closed and should be removed`), exit 1. Same check and count as the body.
- `tests/stress.py` — fresh run: `2 of 113 STRESS CHECKS FAILED` — `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]` and `the probed scenarios' memory peaks stay within their recorded budgets [typical_slab/shoulder attributable RSS 14.5 MiB vs recorded 9.4 MiB; probe 106.3 MiB over a 91.8 MiB baseline]`. The body's run printed `1 of 113` (the setpoint case alone); this container's extra one is a memory budget on a loaded box. Both are the runner's condition, and the head's CI fast lane is green.
- `tests/entities.py` — fresh run: `4 of 2463 ENTITY CHECKS FAILED`, exit 1; the `hb:` heartbeat controls (wall-clock spins) are among the failure lines.
- `node tests/card.mjs` — base worktree: `FATAL ERROR: Ineffective mark-compacts near heap limit ... JavaScript heap out of memory` after ~1,290 green lines, the same V8 heap abort the body records.

None of the four is this diff's: two are platform/load (arm64 ladder, wall-clock heartbeat, RSS on a loaded box), one is this node build's default heap, and the optimality one is the arm64-only stale claim the body quotes from the check's own comment. The head's CI fast lane is green, so none of them is green-then-red on this diff.

## Not established

- The warm-up skip sweep ("0.07 / 0.07 / 0.06 / 0.05 / 0.04 kW at 0/4/8/16/32 h") has no committed harness; I did not re-derive it, and the mutual-exclusion ruling rests on the two reference arms above, not on this sweep. Carry: #2492

## Other checks (re-derived)

- `tests/structure.py`: fresh runs at the head and at the `origin/main`-merged tree both print `class_excess_loc = 18059` and `STRUCTURE RATCHET PASSED`, exit 0; the budget is re-recorded to 18059 with `recorded_at` the merge base (what `recorded_at_sha()` records), while the merge base's and `origin/main`'s budgets both read 18079. A decrease, so no raise and no `## Raise justification` is owed.
- `env_drift.py --all`: `NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE: 56`, the two claimed diffs as above; `card_claimed_drift.txt` byte-identical to the base; `claims-for: 7.0.4` = `VERSION` 7.0.4.
- `VERSION` 7.0.4, the manifest version 7.0.4 and the `RELEASE_NOTES.md` heading `## v7.0.4` are untouched.
- Architecture score `dS +0.0000 NULL`.
- `git merge-tree --write-tree origin/main HEAD` exits 0 with no `MERGE-CLAIM` line; the merged tree's arms and ratchet are measured above.
- CI at the head: 47 check contexts, 0 non-green (`success`/`skipped`); `tests / mutation`, `tests / replay`, `tests / fast (3.14)` and `governance / delivery-status` are all green. Every red the body names on an earlier branch commit is named and answered there.
- `carry_audit.py pr 2745`: 5 finding items, 5 routed, 0 unrouted, 0 bad. The `R10-SAV-ACTUATION` brief records carry 5 seam 2's two controls and its `after: R10-SAV-COMFORT`.
- The body has every `.github/PULL_REQUEST_TEMPLATE.md` heading plus `## Re-cut` and `## Instrument changes`; the `## Re-cut` note the contract now requires is present and materially honest apart from F1.

## Carries

Carry: #2492
