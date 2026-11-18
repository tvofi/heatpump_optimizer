# RCA: an options-flow setting persisted in ConfigEntry.data

Seat: round-11 root-cause, class `N-entry-data-placement` (production). Instances R11 4, 4 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P2`) as one (`fold_ledger.py` `_group_counts`): `N-duplicated-rule`, `N-entry-data-placement`, `N-inverted-aggregate`, `N-mode-coupled-write`, `N-wrong-law`, 8 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`config_flow._create_setup_entry` writes every key the setup wizard collected into
`ConfigEntry.data` and leaves `options` empty. The options flow edits the same keys in `options`,
so after one options save the integration holds two copies of 41 settings, and the reader decides
which one wins. D10-s1-03 counts the 41 keys. D17-s2-05 shows the flow-control field `after_save`
landing in `data`, where nothing reads it. The sweep adds the reconfigure and re-auth saves. The
flow has one writer per step and no rule about which container a key belongs to.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D10-s1-03` (verified, low): planted copy: continue_settings_in_data=41; perturb split -> 0, merged_equal=1; perturbation: --perturb: _create_setup_entry splits the connection-screen keys into data and the rest into options.
- `R11 D17-s2-05` (verified, low): planted copy: entries_with_after_save=2; perturb -> 0; perturbation: entries_with_after_save 2->0; next step finish_setup in both arms.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s1/cfg_data_options.py` took 0.3 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-entry-data-placement.json`) lists 4 seams. The ledger carries 2 of the seams as instances beyond the finding. Its enumerator is cited as `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round11/D14/sweep/entry_data_placement.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

The D10 brief grades config-flow rules (`config-flow`, `reconfiguration-flow`). It does not ask
which container a stored key lands in, and the D17 brief that drove `after_save` first ran in this
round (2026-11-15). No test asserts the split. No process looked at the placement of a key.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 4 instances over the 148 releases they accumulated in, 0.027 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.027 x 15660 s | 423 s/release |
| form | a `tests/` arm walking the setup flow at its defaults and refusing an options-schema key in `entry.data` or a flow-control key in either container |
| catch share q | 1.0: the arm reads the created entry, the one place the defect is visible |
| expected benefit, q x cost | 423 s/release |
| arm time | 0.3 s (`dev/audit/rounds/round11/D10/s1/cfg_data_options.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 4.9 s/release |
| verdict | passes by 86.7x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm must show 41 keys on this baseline, 0 under the `--perturb` split, and 0 on the
fixed tree. The fix also owes a migration moving existing entries' settings from `data` to
`options`. The arm does not cover the migration, which needs its own test.
