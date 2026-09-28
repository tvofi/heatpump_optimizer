**Source:** the #1736 shape screen and the RCA-1736 follow-up tvofi asked for on 2026-09-28: a one-time enumeration, classification and update of the bug-class register for rounds 1–9, a sweep for RCAs conducted but not documented, and the owed RCAs conducted in bulk. The documents:
- [register/REGISTER-V2.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/register/REGISTER-V2.md);
- [RCA-BULK-2.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/rca/RCA-BULK-2.md) §3 (R-register);
- [register/RCA-INVENTORY.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/register/RCA-INVENTORY.md).

Measured at origin/main `3490cb16`.

## What

`tools/audit/bugclasses.json`, the only instrument that counts across rounds, has decayed.

- **Missing rounds.** Round 8 was never classified: its 39 survivors are in no class. Round 9 reached only barriered classes, and 186 register rows sit in no class. The rounds 1–7 seed itself omitted 88 survivors.
- **Re-minting.** The round-9 judge minted 20 of its 31 "new" classes for mechanisms the register already had, which reset their counts to zero: P10 became N-loop-cpu, P2's entity half and I5's translation half split off.
- **Splitting.** The judge split mechanisms below the trigger: dead-member vs structure-blind, and the three translation classes.
- **No unit of count.** Class issues print "2 + 7", N reads 2, and the fix plan counts a third way.
- **No fold step.** Nothing in the round writes the register: `audit-verify.js` only reads it, and only barrier PRs ever edited it.
- **Lost RCA records.** 40 of the 82 RCAs ever conducted are in neither the register nor an issue. 9 records are lost (deleted comments, and 404 PRs by the retired author App). 14 round-9 class RCA docs survive only in `handoff/audit-r9-plan` history at `763b0ba4`.

**Cost:** four classes crossed the trigger in round 8 unseen and got their RCAs 64.5 h late. P4, P8, P10 and I2 never got one: 28 instances since. N-shared-config escaped into 115 releases (RCA-1736). At least 4 seats have re-derived lost records, this investigation included.

## Fix shape

**R9-EG-R0 (data; lands first).** Land register v2:
- `bugclasses.json` from `alt/register/bugclasses.v2.json` at `53a9bbab`: 574 rows; 549 counted in 28 classes, 22 `_unclassified` with reasons, 3 `_excluded`; 95 RCAs indexed under `_rca`. The round 1–7 source (`findings.tsv`) had omitted **88 survivors**, including all of round 5's first run at `eaa2a06`, and counted 3 non-survivors. The reconciliation is in `register/RECON.md`.
- `finding.schema.json`'s `class_guess` enum in the same PR, which `check-wave-script.mjs:730-737` requires.
- The RCA docs in-tree under `tools/audit/rca/` (INERT, outside `POLICY_GLOBS`): the 14 round-9 class RCAs from `763b0ba4`, RCA-1736, and RCA-BULK-1..4.
- The applied reclassifications are listed per row in `rows_v2.tsv`. tvofi reviews the flag list before merge.

**R9-EG-R1 (mechanism; owner-gated).**
- (i) `tools/audit/fold_ledger.py`: deterministic, run by `audit-verify.js` after the sweep. It appends instances, counts judged survivors plus sweep seams marked `beyond_finding`, refuses a survivor whose class is absent, and refuses a new id without `nearest`/`differs`. It opens the round-record PR.
- (iv) `fold_ledger.py --check` in an existing lane (<1 s): every in-tree judge survivor is in exactly one class; every class that met an adopted trigger has a `barrier` or an `rca`; every `rca` resolves in-tree. Demonstration (`register_check.py`): at main it exits 1 with 186 unclassified rows and 12 classes owed; on v2 with RCAs cited it exits 0; it would have failed at `9fd07379` on round 8.
- **Policy, tvofi decides:**
  - (ii) `judge.md`: reuse before minting; a class is a mechanism, never a site.
  - (iii) `defect-root-cause.md`: a cross-round trigger (≥3 over any 3 consecutive rounds, or ≥5 total while open).
  - (v) Where an RCA is recorded (in-tree doc, and a short Root cause section on the issue).
- **Refused:** rebuilding the 9 lost records. Their countermeasures landed.

## Disposition

Scheduled: **R9-EG-R0**, its own data PR once tvofi has reviewed the flag list (no after-edge, so it can land in wave 0), then **R9-EG-R1** after R9-F11.4 (`audit-find.js`/`audit-verify.js` are code-owned; F11.4 is the lane's driver fix).
