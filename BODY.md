R10-HOTFIX-REFERENCE-BASIS: a production hotfix that gates the v10.0.0 stamp. Pull request #3587 (merge 931970141c) changed the savings reference the ledger books for one install class, but `ledger.REFERENCE_BASIS` was not bumped. The class is a two-zone house behind a throttling (manual) valve whose curve is the bound. In cold hours with no sun, the first-step reference power rose by 1.12 to 1.15 %. Controls are bit-identical. The verification seat measured this at origin/main d7004eaa77 by calling `_compute_baseline_power` at 931970141c^1 and at 931970141c: +5, 0, -5 and -15 °C give +1.15 %, +1.13 %, +1.13 % and +1.12 %. Sun at 300 W/m2, an unvalved install, a single-zone valve and a plain house are all bit-identical.

The in-code rule at `ledger.py` says "Bump when the booked reference changes". `docs/dashboard-card.md` promises that "when an update changes how the baseline is booked, every month up to the update stops stating a saving". v7.1.17 shipped basis 2 with the pre-#3587 reference. Without this bump, a month first booked on v7.1.17 that keeps booking after the upgrade would sum two references into one saving.

**The change.** It mirrors the previous bump, 194625754d (basis 1 to 2), and its stale-pin deletion, fc372c8094:
- `REFERENCE_BASIS = 3` in `custom_components/heatpump_optimizer/ledger.py`. Its comment now records what basis 2 was: a valve-limited two-zone house held at level floors below the plant's ceiling, released in v7.1.17, where #3587 holds it at the valve top.
- The features check `a month's first savings booking stamps the reference in force, once` pins the literal 3.0 and `_SB_NOW == 3`, so a bump stays deliberate.
- A new check reads a persisted stamp 2.0 as the old basis after a booking: no saving or percent, both columns kept, the stamp unchanged.
- A null-control check reads a stamp 3.0 as current after a booking.
- The killed-by pin `tests/mutation_ledger/killed_by/ledger.py/@module.CONST.1e17aeec.json` (`old: REFERENCE_BASIS = 2`) is deleted, as fc372c8094 deleted the pin on `= 1`. Its line no longer exists, so `ci_predict` would read it as STALE PIN.

**Docs.** No sentence in `docs/dashboard-card.md` or README.md names the basis number or which releases count as old, so nothing in them became false. The *old basis* paragraph (dashboard-card.md, "So does a month booked, wholly or in part, against an earlier baseline ...") is what this change makes true again. No strings change.

**User cost.** On an install whose current month was first booked on v7.1.17, the Savings tab's row for that month shows *old basis* after the upgrade. It states no saving and no percent, and it keeps its two cost columns (baseline and paid). Every month first booked before v7.1.17 already reads *old basis*, so this costs nothing more there. The next month is stamped fresh and states its saving. Single-zone and unvalved installs in that small set also lose the open month's stated saving, because the basis is global. That is the same trade 194625754d made.

## Release note

### A month first booked on v7.1.17 shows "old basis" after this update (R10-HOTFIX-REFERENCE-BASIS)

This release changes how the savings baseline is booked for a two-zone house behind a throttling valve: in cold hours with little sun, the baseline is about 1 % higher than before. The month that is open when you upgrade, if it was first booked on v7.1.17, shows *old basis* on the Savings tab. It keeps its baseline and paid columns but states no saving, because those two baselines cannot be added into one figure. Earlier months are unchanged, and next month states its saving again. Nothing to do.

## Root cause

Per dev/governance/rules/defect-root-cause.md: the defect did not reach a release (#3587 merged after the v7.1.17 tag and is in no tag) and turned no check red. This section is the record the verification asked for, not a triggered analysis.

- **Cause.** #3587 replaced the held state of `_thermostat_held_state` with `valve_top_equilibrium` for a valve-limited two-zone house. That changed `baseline_power`, which `_settlement_schedule` books into `savings_baseline`. Its body said so ("That affects `baseline_cost` and the saving against it on every two-zone valved install whose curve is the bound"). The bump rule lives as a comment on `REFERENCE_BASIS` in `ledger.py`, a file #3587's diff did not touch. Neither its fixer nor its reviewer opened that file, and nothing in the fixer or fix-review contract names it.
- **Process state: (b).** A rule existed (the `ledger.py` comment and the dashboard-card promise) and was not followed. No check enforces it, and the rule sits where a change to the reference does not show it.
- **The cheaper detector.** One features check could pin a digest of `_compute_baseline_power` for a fixed set of installs, including `replay_install` with its manual valve, beside the literal `REFERENCE_BASIS` it was recorded under. A change to the booked reference would then fail on the digest until the same diff re-records it, and the re-record line sits next to the basis literal. Standing cost: one re-record per legitimate reference change. That is two in the last day (194625754d and this one), plus whatever float drift across BLAS builds the simulated reference shows, which is unmeasured and must be measured before the check is built.
- **Countermeasure.** Worth building, but not inside a hotfix. It is routed below. The digest's reproducibility across CI builds is the open question.

## Head

`b0c1f6dbd6de47f7d195f9d3ef185d6178639bfd`, on origin/main `d7004eaa77`. The failing-first commit is `33d368ce0a214653dec082fd95b03ab2baf9e55e` (test only); the fix is the commit above it.

## Mutation proof

Failing first. At 33d368ce0a, with the test changed and `REFERENCE_BASIS` still 2, the reference-basis block (`tools/audit/seat/features_block.py` from `# R10-HOTFIX-SAV-ESTIMATE: a month's reference basis.` to `# R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0`, with its prelude from `--emit-prelude`) printed `3 of 9 FEATURES BLOCK FAILED`:
- the literal-3.0 pin;
- the stamp-2 check (`old_basis` False, saving stated);
- the stamp-3 check (`old_basis` True).

At the head it prints `ALL 9 FEATURES BLOCK PASSED`.

`python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd '<that block>'` printed:
- `SURVIVED NULL`
- `KILLED basis_reverted_to_2` (`REFERENCE_BASIS = 3` -> `= 2`)
- `KILLED basis_bumped_to_4` (`= 3` -> `= 4`)
- `KILLED old_basis_only_below_2` (`old_basis = self.meta_mean(...) != REFERENCE_BASIS` -> `< REFERENCE_BASIS - 1`: the old-basis comparison weakened so that a stamp 2 reads current)
- `KILLED old_basis_off` (`old_basis = False`)

## Unpinned sites

- custom_components/heatpump_optimizer/ledger.py:78 CONST: pinned by mutation-autofix, as the same line at basis 2 was (97478d9785, `ci: pin killed mutants`, after 194625754d). The spec run above kills `= 4` and `= 2` on this line through the features block.

## Null control

- A month stamped 3.0 that books on under the head still states its saving and percent, with its stamp unchanged (`a month stamped 3, the reference in force, keeps stating its saving as it books on`).
- The unmutated tree under the mutant driver: `SURVIVED NULL`.
- The verification's probe: unvalved, single-zone-valve and plain installs are bit-identical across #3587, and so is sun at 300 W/m2.

## Figures

none

## Red checks

- `mutation` at b0c1f6dbd6de: red by construction on the 1 site under `## Unpinned sites` (the bumped `REFERENCE_BASIS = 3` line); mutation-autofix pins killed sites after the push, as it pinned the same line at basis 2 (97478d9785). The cheaper detector is `tools/pr/ci_predict.py`'s ADDED UNPINNED line, which predicted it at this handoff; the spec mutant run under `## Mutation proof` already kills both CONST moves on the line, so no further detector is owed.

## Forward-carry

- A features check pinning a digest of `_compute_baseline_power` for fixed installs, including `replay_install` with its manual valve, recorded beside the literal `REFERENCE_BASIS`, so that a diff changing the booked reference fails until it re-records and faces the bump. First measure whether the digest reproduces across CI's BLAS builds (`tests/features.py`, the reference-basis block). Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
