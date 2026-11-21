Fix review: merge e9ad13fa58e02965bb5eb772b19535c09c9523c6

bus-nonce: 1ac47e2069b6a09bdb6e7d87a03f1127
pending-ci: gate

## Scope

Round 4 of this PR, the round the body calls its re-cut. This is a delta review over the reviewed head 98cb43e750457b41ae6feb9a0c56cf1d6728e201 (the packet's `## Review scope: delta`). `review_carry.py 98cb43e7 e9ad13fa` prints `FRESH-REVIEW`. The delta's own commits:
- b4091e0b59 adds the lone-survivor check and its null control to `tests/open_meteo.py`.
- c995a3255c updates two `tests/entities.py` migration checks so they read main's 7.2 key placement (#3742).
- 012ec8517a and b3f7a46cc6 are mutation-autofix ledger pins.
- The rest are merges of main.

Widened, per step 12: the merge resolution of `custom_components/heatpump_optimizer/__init__.py:async_migrate_entry` changes production code. At 98cb43e7 the repair ran on each side separately (`repaired_numbers(entry.data, ...)`, `repaired_numbers(entry.options, ...)`). At the head it is `placed(repaired_numbers(effective, repairs))` over `effective = {**entry.data, **entry.options}`. The risk is non-obvious: a key in both sides with a bad options value, a misordered effective mapping, or the repair dropped by the resolution would change what every reader takes, and CI would not flag the resolution itself. I reviewed exactly that function, plus `entry_config.number_repairs`, `repaired_numbers` and `placed`. The composition gives the same effective mapping as the per-side repair did: the repairs are computed from the effective mapping in both versions, and a None repair drops the key from every side. Every resolution mutant below is killed.

## Findings

- Note: paperwork: the body's design paragraph says "Reach: `async_migrate_entry` runs for `entry.version < CONFIG_ENTRY_VERSION`". After the merge with main, the repair also runs on a minor-version migration (`minor < CONFIG_ENTRY_MINOR_VERSION`, the 7.1 to 7.2 placement). The reach is wider than the body states. That is no defect: on a healthy entry the repair is a no-op, as the null control shows. Carry: dismissed: a stale sentence in the body, settled by the fixer's next body edit on this PR.

## Evidence

- Head reviewed: e9ad13fa58e02965bb5eb772b19535c09c9523c6 (`ev/HEAD.txt`). Merge base: e893cd3d1ebd1ec3bb56756ce902144a370fe821. The body's `## Head` names this SHA.
- The previous verdict's block, M12, is resolved. In a worktree at the head, with bytecode writing off (a stale `.pyc` from a same-size sed edit otherwise masks the restore):
  - At the head, `tests/open_meteo.py` reads `ALL OPEN-METEO CHECKS PASSED`. Both new checks read `ok` (`ev/head_open_meteo.txt`).
  - With `if len(kept) < 2:` changed to `< 1` the script exits rc=1 with `FAIL a lone sample left after the year-1 drop is no series: mean_over claims no window` (`ev/m12_open_meteo.txt`). Its null control stays `ok` under the mutant.
  - With the guard off (`if False:`) the result is the same: rc=1, same check (`ev/m12b_guardoff.txt`).
  - `git status --porcelain` read empty after each run.
- Previous findings: the P8 residual was dismissed and is unchanged. The stale `_MAX_INTERVAL_MINUTES` name no longer appears in the body, and `git grep` finds no such name in `custom_components/` at the head.
- Mutation proof for the merge resolution, run on the migration section of `tests/entities.py` (lines 1-148 plus 15576-15757, extracted as `ev/mig_block_driver.py`; driver `ev/mig_mutants.sh`, output `ev/mig_mutants.txt`). At the head: `ALL 13 MIGRATION BLOCK CHECKS PASSED`. The mutants:
  - mR, `placed(effective)` (repair dropped): `FAIL an old entry's non-numbers under numeric options are repaired, with one warning naming them`.
  - mP, back to the per-side repair with no placement: that check and `FAIL a 7.1 entry migrates to 7.2: ...`.
  - mO, `{**entry.options, **entry.data}`: `FAIL a 7.1 entry migrates to 7.2: ...`.
  - The worktree was clean afterwards.
  - I did not run whole `tests/entities.py`, which the body says runs for over an hour. CI's lanes carry it.
- The finder's harness at the head, from plan export 819aa2e3 (`parsers_fuzz.py` sha1 74da66cd7b0beac627cb2a636e6c0364c1ddc019), `--arm openmeteo`: `openmeteo_year1_solve_failures=0` and `openmeteo_healthy_solve_failures=0`, which matches the body (`ev/finder_openmeteo_head.txt`). I did not re-run the merge-base end in this round. Round 3 measured 3 there (round 3's `ev/finder_*`).
- `git merge-tree --write-tree origin/main e9ad13fa` (origin/main 78d3b40221) exits rc=0 with no conflict (`ev/merge-tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md`, `tests/golden/` and `tests/*budgets.json` all have an empty three-dot diff (`ev/untouched.txt`).
- The role contract is current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.
- Step 16: the delta adds no path that skips an actuator write.
- CI: `merge_train.py classify e9ad13fa --pr 3734` was polled about every 70 s from 11:41 to 12:11 UTC. It read WAIT throughout, last line `WAIT e9ad13fa58e02965bb5eb772b19535c09c9523c6 pending: gate red: none` (`ev/classify_poll.log`), so the verdict carries `pending-ci: gate`. At render, the packet's `gate` failure was an earlier run's. The body's `## Red checks` answers that red and the others in the range, and I checked that each was answered, not the answer.
