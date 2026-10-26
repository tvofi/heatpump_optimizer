Fix review: blocked 3b55da2c65ca24780fa2b6da5137d64332279b36 harness: the finder's #2255 instruments are dead at this head and its baseline harness was re-specified by the fixer, so the owner-required flat-price null still reads 6.18 % on the modelled basis and 10 of 16 committed mutant anchors no longer apply
bus-nonce: 58212ca1d5f20f925bef2c2fb3135601

Round 3 of this fix (fix-review.md, fixer.md: a round-4 fixer owes a re-cut, not a repair). Head measured: `3b55da2c65ca24780fa2b6da5137d64332279b36`, the head at posting (`git ls-remote` reread immediately before). Merge base against origin/main `6fe5170cd` is `3b4180dcc`. Verdict class `harness` (fix-review.md steps 2, 3, 9).

## RESULT lines (mine; the finder's committed bytes, not the fixer's)

The finder's `dev/audit/harnesses/r10_sav_baseline.py` at its committed form, sha1 `bc31f356191ededbfb0b15f768b258249867b134`, run with `PYTHONPATH=tests/hastub:tests:custom_components` against each tree:

MERGE BASE `3b4180dcc680e2e2e06f4d8ed0a0839a7374d78f`:
- transient SOUND: booked baseline step 0 = 2.06 kW from all four starts, spread 0.00 kW (threshold 0.05)
- cost SOUND: receipt `total_sek` 15.0 = row `actual_sek` 15.0
- coverage SOUND: 24 settled hours of 672, open-row scale 28.00
- null DEFECT: baseline 154.1, actual 137.41, saved 16.69 = 10.83238932735682 % (threshold |pct| < 3)
- `arms run 4, defect 1: null`, rc=1

HEAD `3b55da2c65ca24780fa2b6da5137d64332279b36`:
- transient DEFECT: step 0 = 1.95 / 1.90 / 1.88 / 1.95 kW across the four starts, spread 0.07 kW (threshold 0.05)
- cost DEFECT: receipt `total_sek` 15.0 against row `actual_sek` 4.2
- coverage SOUND: 28.00
- null DEFECT: baseline 146.46, actual 137.41, saved 9.05 = 6.179161545814557 % (threshold |pct| < 3)
- `arms run 4, defect 3: transient cost null`, rc=1

The same head values reproduce at round 2's head `1a13f2b3` byte for byte (the only production change after it is the no-op `coverage_factor` extraction), so the movement from the merge base is the branch's own.

The finder's committed mutation proof `dev/audit/harnesses/r10_sav_baseline_mutants.py` (unchanged by this branch, from `8d16e9903`, #2255), one mutant per run:
- merge base, M1: rc=1, `failing=6` — killed by the #2255 section, including "the booked thermostat step is independent of the plan's start state (single-zone)" and "the booked thermostat step is the steady holding power at target"
- head, M1: rc=1, `AssertionError: M1 baseline starts from the plan's state` at the harness's own `assert orig.count(old) == 1`
- anchors present at the merge base / at the head, per mutant: M1 1/0, M2 1/1, M3 1/0, M4 1/0, M5 1/1, M6 1/0, M7 1/1, M9 1/0, M10 1/0, M11 1/0, M12 1/1, M13 1/0, M14 1/0, M15 1/0, M16 1/1, M8 1/1. Ten of sixteen are gone; the harness dies on its first mutant, so the finding's mutation proof does not exist at this head.

The committed control `dev/audit/harnesses/r10_savings_upgrade_month.py` (#2255/#2411; the roster row for the upgrade fix names it as its synthetic control), whose header records upgrade 2.800 / null 28.000 / fresh 2.800:
- at `1a13f2b3`: rc=0, prints `upgrade factor= 2.800`, `null factor= 28.000`, `fresh factor= 2.800`
- at the head: rc=1, `AttributeError: 'MonthlyLedger' object has no attribute '_coverage_factor'`, line 67 — `57eeda5a1` renamed the method to module-level `coverage_factor` and no harness was ported

`tests/structure.py` `class_excess_loc`, each run's own RESULT line:
- origin/main `6fe5170cd` budgets file: 18079
- `1a13f2b3`: 18075, `STRUCTURE RATCHET PASSED`
- head: 18072, `STRUCTURE RATCHET PASSED`
- null control (the extraction reverted, the joins revert kept): 18089, `1 FAIL class_excess_loc 18089 > 18072 (+17)`, `1 STRUCTURE BUDGET(S) BREACHED`
- plant (mechanical verbatim module-scope extraction of the same function, nothing else improved): 18072 — reproduces the head exactly, so the instrument cannot separate this extraction from a cosmetic move.

## The block

1. The finder's baseline harness was re-specified by the fixer. `dev/audit/harnesses/r10_sav_baseline.py` is `bc31f356` at the merge base and `88ac23e4` at the head; commits `c57fb1bc6` (transient) and `29f6d6cbc` ("the #2255 null arm's verdict is the comfort term, not a 0 % reading") change two of the four verdicts:
   - transient: `spread < 0.05` became `max(abs(first - _floor_demand_at_target(model, matched, ...)/cop)) < 1e-6`. The reference is the production private helper `_floor_demand_at_target` the fix works with, so the arm is the code judged against itself; it cannot fail for the reason #2255 named.
   - null: the owner-required flat-price control `|savings_pct| < 3.0` became `|kwh_base - kwh_room| < 0.02 * kwh_room`, a comfort-term comparison. The docstring now says the published percentage "is not 0 at a flat price".
   Step 2 requires the finder's harness at both ends; a fixer ports a name a rename breaks (`fixer.md` 3), not a verdict. On the finder's bytes the head fails three arms where the merge base failed one. The cost arm is answered (below); the transient and null arms are answered only by the re-specification. Step 9's rule applies: "A fixer who builds their own instrument must disclose it as their own, not the finder's" — the body's "Harnesses, both ends" list gives `88ac23e4` with DEFECT/SOUND readings and never says this branch rewrote the verdicts; a reader takes it for the finder's instrument.
   The same re-specification reaches the committed suite: `tests/features.py`'s #2255 checks are rewritten from "the booked thermostat step is independent of the plan's start state" to "depends on the start only through the comfort delivered", with the assertion now `max(abs((first - rerun) - (first[0] - rerun[0]))) < 1e-9` against a `_compute_baseline_power` rerun from a fixed state — a constant is allowed across starts, so an arbitrary start dependence passes. That may be the right work under the owner's spec, but it is not disclosed as a re-specification anywhere in the body, and it leaves the null control replaced rather than met.
   Owed: restore the finder's two verdicts, or record the re-specification where the finding lives (roster carry / owner acceptance, quoting the owner's words) and re-cut the body to (a) say the arms were re-specified by this branch and (b) name the published flat-price figure that remains on the modelled basis: +6.18 % at the head (10.83 % at the merge base) against the owner-required <3 %. The fixer's own harnesses (`r10_sav_comfort*.py`, `r10_sav_volume.py`) are the fixer's own and cannot stand in for the finder's arm; the body's `const` arm (+0.35 %) and this arm (+6.18 %) are two readings of one flat-price question that the body does not reconcile.

2. Ten of the finder's sixteen committed mutants can no longer be applied, and the harness asserts before writing. `dev/audit/harnesses/r10_sav_baseline_mutants.py` is unchanged by the branch; its anchors on the lines the fix moved (`state = _thermostat_held_state(...)`, `actual_sek = self.month_cost(key)`, `return max(1.0, month_hours(now) / settled)` at the old indentation, `surplus_above_caps`, the `_start_gap_cost` call, the demand clamps) are gone. At the base M1 is killed with six failures; at the head the same harness dies on M1's assert and no mutant is ever evaluated.
   Owed: port each anchor to the line the fix moved (or record each retirement and why), and re-run so every remaining mutant is shown killed at this head.

3. `dev/audit/harnesses/r10_savings_upgrade_month.py` is dead at the head. `57eeda5a1` renames `MonthlyLedger._coverage_factor` to module-level `coverage_factor` without porting the committed harness that drives it (line 67), which the roster row for the upgrade fix names as its control. rc=0 at `1a13f2b3` printing the header's 2.800 / 28.000 / 2.800; rc=1 at the head. No CI lane executes `dev/audit/harnesses/`: `tests/harness_headers.py`'s `_discover()` runs only `dev/audit/rounds/round*/D*` live-header files, and this harness is an `inert_reads` entry in `tests/closures.json`, so a green head does not and can never cover it.

## Answered, and accepted

- The cost arm's reversal (15.0 vs 4.2) is answered: the owner's acceptance quoted in the roster (`dev/programme/rosters/wave-r10-groups.json`, tvofi 2026-10-24) moves the row's Baseline, Actual and Savings onto one spot-plus-fee basis, so the closed-month receipt's bill total (capacity, wear, immersion) is no longer the row's counterpart. The branch left this arm unchanged and the body states the reversal. I do not block on it.
- Round 2's `metric-gamed` block is paid. `57eeda5a1` reverts the 14 line-joins of `8005c528` (which improved nothing) and extracts `coverage_factor` with `meta` as its argument, colocated beside `pro_rata_factor`; the call site is inside `savings_months` under `if estimated:` with `key == open_key`, and the base read `self.months.get(month_key(now), {}).get("meta", {})` — behaviour identical. It deletes lines and narrows an input, so it counts; it is not a re-join. `18075 -> 18072`, a decrease against `18079` at origin/main. The movement is partly the instrument's (the plant above reproduces it), and the change being sound, that is an instrument finding, carried below.
- Red checks: every red on a branch commit is named and answered in the body (replay 121226462191; fast 3.14 120941471531, 120942142230, 120926746399; mutation 120921728932, 120926210442, 121028737618; delivery-status 121326817924; ci-ratchet on main 121377149428). The head `3b55da2c` has 55 check runs, 0 non-success/skipped; `1a13f2b3` 42, 0. The round-3 commits `57eeda5a1` and `48ab3dcea` were never branch heads and have no runs of their own.
- CI at the head, cited not re-run: gate PASS; mutation `MUTATION TABLE PASSED`, 3900 unpinned of 6420 (3904 at `3b4180dcc`), 7 evaluated / 0 survivors, `ledger.py:34 NULL_COMMENT` survived; fast 3.14 `MODE: SCOPED -- 28 script(s) run, 5 scoped out`, `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, `ALL 2463 ENTITY CHECKS PASSED`.
- Claims: `card_claimed_drift.txt` byte-identical to origin/main; `claimed_drift.txt` adds 41 claim lines, suspends 15 may-drift entries, 0 removals outside may-drift; `claims-for` 7.0.4 = VERSION. `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading untouched.
- Merge: `git merge-tree --write-tree origin/main HEAD` at `6fe5170cd` exits 0 with no `MERGE-CLAIM` line.
- Carries: `carry_audit.py pr 2745` = 5 finding items, 5 routed, 0 unrouted, 0 bad; the R10-SAV-ACTUATION precondition carry is present at origin/main. Delivery row `dev/programme/delivery/2745.md` present at the head. The body names the head it measured.

## Not established

- The owner acceptance's third surface, "the closed-month receipt's saved line": `freeze_month_report` at this head publishes `lines`, `reasons`, `total_kwh`, `total_sek`, `basis`, `compressor_starts`, `contract_comparison`, `reasons_reconcile` (plus `mean_spot_price`, `capacity_peak_kw`) and no savings field, so I could not compare a receipt "saved line" with the row. If tvofi's acceptance meant a receipt field, it does not exist at this head.
- The body's figures were re-taken at `7c422999f`, not at the head. After `7c422999f` the head gained `57eeda5a1`, `48ab3dcea` and a main merge. I re-derived the structure figure, the four finder arms and the two dead harnesses at the head; I did not re-derive every other quoted number.
- The new transient criterion's soundness: my judgement is that matching a production helper to 1e-6 (and a production rerun up to one constant in `tests/features.py`) is self-referential, but I did not falsify it with a plant of a differently shaped baseline, so I state it as an objection, not as a measured defect.
- The attribution of the residual 6.18 % to COP timing and stored heat: I did not separate it into those terms myself.

## Carry

Carry: dismissed: step 14's instrument finding — `tests/structure.py` `class_excess_loc` counts class spans and leaves module scope unmeasured, so a mechanical verbatim extraction (my plant: 18089 -> 18072) reproduces this diff's movement; the diff's change is sound (narrower input, colocation, behaviour identical), so this is an instrument finding, not `metric-gamed`. No live group owns `tests/structure.py` (R10-STRUCTURE-BLIND, R10-STRUCTURE-ALIAS and R10-I5-DOCS are done), and a reviewer may not add a carry file; if tvofi wants it recorded, a future structure group's brief takes it.

## What a round-4 fixer owes (a re-cut, fixer.md past three rounds)

Start from the finder's two committed harnesses and the finder's four baseline arms, not from the branch's rewritten ones. Either make the modelled-basis flat-price reading meet the owner's null, or take the re-specification to the finding with the owner's words and say in the body that the arms were re-specified and what remains. Port the ten mutation anchors and the renamed `coverage_factor` call so both committed #2255 harnesses run at the head again, and re-cut the body's figures at the head rather than at `7c422999f`.
