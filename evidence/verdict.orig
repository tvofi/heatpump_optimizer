Fix review: merge f4e168719d12f071bbc7771944e9430147a223db

bus-nonce: a71ad76c02dff7e6ce6a5308fcc45606

Review round 4, by a cloud seat. This re-takes the round-4 review whose return was lost. I judged it afresh and did not rely on that seat's evidence. Earlier verdicts on the PR: round 1 `blocked aac8c5e80` (three mutation survivors), round 2 `merge 98d33ce03` (its evidence is cited in round 3), and round 3 `merge 6f6aa4e48` (a carry). Since round 2 every round has judged a carry or a resolution delta, not a repair, so `fixer.md`'s "re-cut from the fourth round" has nothing to act on here.

Measured head: `f4e168719d12f071bbc7771944e9430147a223db`. I re-read it just before writing this: `refs/heads/fix/r10-sensor-payload` and `refs/pull/2379/head` both point at it. Merge base with origin/main: `55dc8d9c2`. Evidence is in `ev/`.

## Resolution delta since the carried merge 6f6aa4e48

The first-parent chain is `6f6aa4e48 -> fe4d15d76 (bot, ci: merge main) -> 60368fbac (bot, ci: merge main) -> b44e17cb0 (merges 9e2cdca95) -> f4e168719 (merges origin/main 55dc8d9c2)`. No authored commit lies on that range. Every commit is a merge.

- The PR's own patch, `git diff <merge-base> <head>`, is the same at both ends: 41 files, +756/-385, at 6f6aa4e48 and at f4e168719. I compared the changed lines (`+`/`-`) of every file. Only `tests/structure_budgets.json` differs, and only in context lines: main moved `seam_cut_total` from 752 to 720 and `recorded_at`'s base value. The branch's own lines are unchanged (`duplication_copies 33 -> 17`, `recorded_at -> 811df3cf3`). See `ev/patch_delta_files.txt`.
- I ran `git show --cc` on each merge (`ev/combined_merge_hunks.txt`). fe4d15d76, b44e17cb0 and f4e168719 have no combined hunks, so no evil-merge content. 60368fbac has one: the `structure_budgets.json` `recorded_at` / `seam_cut_total` adjacency, which keeps both sides. 9e2cdca95 has two hunks in `tests/entities.py` (`ev/9e2cdca95_cc.patch`). Both keep both sides, exactly as the body describes: the `zone_setpoint_names` P2 owner beside main's `slot_floor_rule`, and both `_P2_PLANTS` entries. No production file changed in any merge resolution.

## Checks at this head

- **Merge with main.** `git merge-tree --write-tree origin/main <head>` exits 0 against c8cc75ea9. It also exits 0 against 176851e95, which main moved to during this review. That range touches only tooling and record paths and none of the PR's files (`ev/main_ahead_overlap.txt` is empty).
- **CI.** The commit's check-runs API returns 46 runs: 31 success, 15 skipped, none failed or pending (`ev/check_runs.tsv`). All 11 workflow runs concluded success. `mutation` (job 117719203618) reads `MUTATION TABLE PASSED`. Its log shows the three round-1 survivors killed: climate.py:140 GUARD_OFF by finite_boundary, and entity.py:142 and sensor.py:2808 CMP_BOUND by entities. The null control `climate.py:43 NULL_COMMENT` survived every driver, as it should. It is not INCONCLUSIVE (`ev/mutation_job.log`).
- **Red checks.** None is red at the head. The body answers the earlier red `mutation` and `nightly-ha (stable)`. pr-contract is green in both runs.
- **Local checks.** `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2349 ENTITY CHECKS PASSED`. `tests/finite_boundary.py` prints `ALL 106 FINITE BOUNDARY CHECKS PASSED` with `number_states=50 number_state_escapes=0`. `tests/structure.py` passes with `duplication_copies 17 <= 17`. The body quotes 2348 and 101, taken at an earlier head. The increases come from main's checks merged in since (`git diff 98d33ce03 HEAD -- tests/finite_boundary.py` comes from main's store fixes 40ad33528 and 36f0f5cbe), not from this diff.
- **VERSION, manifest, notes, claims.** VERSION, the manifest version, the `RELEASE_NOTES.md` heading, `tests/golden/` and both claim files are untouched three-dot from the merge base.
- **Forward-carry.** D8-s1-01 is still on origin/main in R10-ARCH-SHAPES' `carry`, with the control and a re-run instruction (`ev/forward_carry_main.txt`).
- **Role file.** `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.

## Mutants, mine, run at this head

Each mutant ran in its own detached worktree at f4e168719, which was then removed. Records are in `ev/mutant_*.txt`.

- R1 (`payload_number` drops the bool test): KILLED by finite_boundary. Four arms fail, including the number-state census (`BaselineCostSensor.native_value: True -> 1`, ...).
- R2 (numpy unwrap off, entity.py:140): KILLED by `payload_number reads numpy.int64(7) as 7 (#2379) [got None, want 7]`.
- R3 (climate.py:140 `if measured is not None` set to False): KILLED by `climate current_temperature reads the measured upper floor first`.
- R4 (sensor.py:2808 `<=` changed to `<`): KILLED by `_gap_energy_rate falls back to the contract price at a zero spot price`.
- R5 (Home Assistant owner skip deleted): KILLED by `Home Assistant's own native_value default is not wrapped by the scrub`.
- R6 (the scrub keys on `cls.__dict__` again, patch 00's shape): KILLED. The NaN-mixin arm, the no-rewrap arm and the #1541 leak arm all fail.
- R7 (upper and lower names swapped in `zone_setpoint_attributes`): KILLED by finite_boundary `zone_setpoint_attributes keeps upper and lower apart`. tests/entities.py alone does not catch it, which is expected: P2 pins the single spelling, not the values.

Each body mutation claim I re-ran (M1, M2, M3, and the round-1 pins) reproduces with the arm the body names.

## Finder's harnesses, both ends

Each is a scratch copy of origin/main's file. The only edits are `BASE` set to the end's SHA and `REPO` set to my worktree. The sha1 of each matches the body. The fork end is 811df3cf3 and the head end is f4e168719.

- `shape_payload_guard.py`, fork: `implementations=35 guard_families=4 driven_sites=26 distinct_answer_vectors=5 disagreeing_probes=3 (0,True,'21.5')`. Head: `implementations=6 guard_families=2 driven_sites=1 disagreeing_probes=0`. Confirmed.
- `probe_scrub_mixin.py`, fork: `mixin_supplied=0 nan_published=1 nan_published_outside_pkg=0 nan_published_null=0`. Head: `nan_published=0 nan_published_outside_pkg=0 nan_published_null=0`. Confirmed. The carry's outside-package figure is 0 at both ends.
- `scrub_escapes.py`: `entity_classes=91 escapes=0` at both ends. Confirmed.
- P6 `enumerate.py --tree` over `git archive` trees, fork: `seams=56 instance=31 guarded=5 not_applicable=20`. Head: `seams=26 instance=0 guarded=6 not_applicable=20`. Its null control gives `--fixture clean` instance=0 and `reintro` instance=1. Confirmed, with the blindness the body already discloses: mixin seams drop out of the enumerator, and my R1, R2 and R6 mutants plus the census cover them behaviourally.
- archscore. `--diff 55dc8d9c2 HEAD`, the current merge base, gives `dS +5.6289 IMPROVES` (`duplication_copies 64 -> 41`, `coord_footprint 2506 -> 2499`). The dS matches the body. The body's command `--diff 811df3cf3 HEAD` now reads `+7.4577` at this head, because the head carries main's own improvements since 811df3cf3 (`private_cross_module`, `layer_violations`, `shared_inplace_writes` and others). The body's `coord_footprint 2547 -> 2540` endpoints are stale for the same reason. The PR's own delta is unchanged at -7. This is a stale figure, not a gamed one. The `duplication_copies` drop is earned: R6 and R1 show the mixin mechanism carries the behaviour, and round 2 confirmed that 30 per-sensor bodies were deleted.
- `f1_active_now.py` (D8-s1-01): not re-run. `coordinator.py` is not in this diff, and the PR's patch is identical to the one round 2 measured flat (1 and 4).

## Notes, not blocking

- The figures the body quotes at earlier heads (2348 entity checks, 101 finite-boundary checks, the archscore against 811df3cf3) are true at the commits it names, not at this head. The head's figures above differ only by what main merged in.
- `tests/closure.py select --diff 55dc8d9c2` at the head prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out`. The body's `2 script(s)` was measured against 7e79b6762, a different base.

I posted, approved, merged and pushed nothing, except the probe ref this verdict returns on.
