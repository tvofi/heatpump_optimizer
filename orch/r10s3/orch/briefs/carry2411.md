## Forward-carry

The carries are roster carries the orchestrator appends (`roster_edit append-carry`); the texts are in the seat's report.
- The mutation instrument's owner (the lane holding `tests/mutation_table.py` and `tests/entities.py`'s R9-F10.13 block): `tests/entities.py`'s `--anchor` self-test runs `mutation_table.main` against the live tree, and `clone_tree` overlays the working tree. So under `--pin-killed`, entities.py "kills" every mutant of a line that already carries a pin, by refusing the ledger/inventory disagreement.
  - Control: the equivalent rewrite `if 0 < dt:` of `ledger.py:186` fails the same single check.
  - Re-measure: at a later head, mutate any pinned line equivalently, and run `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`.
  - Until it is fixed, a `killed_by: tests/entities.py` pin on a line with a second pin is unproven. The ledger holds 123 `killed_by: tests/entities.py` pins in all, by `grep -rl '"killed_by": "tests/entities.py"' tests/mutation_ledger/killed_by | wc -l`. How many of them sit on a line with a second pin, or are vacuous, is not measured.
- The month row's flat-price null, its three terms, and the `summer_dhw_only` start-bound limit go to the group the orchestrator adds for the comfort-matched baseline. R10-ADVISOR's seam does not own `_compute_baseline_power` or `ledger.py`.
- R10-ADVISOR: its carried null ("savings about 0 on a flat-price profile"), restated so its acceptance separates comfort, COP timing and stored heat. The `const` arm of `r10_sav_null_terms.py` is the control.
- R10-SCORES and R10-ADVISOR: the row semantics in "What R10-SCORES and R10-ADVISOR read after this".
- The stamp (`tools/release/stamp.py` / web-stamp): restore the 19 suspended may-drift entries verbatim when the stamp empties the claim list. The obligation is written beside each entry in `tests/golden/claimed_drift.txt`.

## Friction
