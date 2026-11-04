R10-LEARNED-STORE-LOAD: two latent learned-store lifecycle defects, found by the R10-FACTORY-RESET fixer, each reproduced through the production coordinator and fixed in `coordinator.py`'s learning seam.

1. **A save during the thermal load wrote the COP and T4b learners' defaults.** `_async_load_thermal_learning` awaited its gated re-anchor save halfway through applying the read. That was before `_COP_STORE_KEY`/`cop_samples`, `measured_cop`, the cusums, the COP baselines and every `_load_t4b_learners` key had loaded. So the saved payload (the loader's own, and any save scheduled behind the read) carried those learners as defaults. A restart in that window lost them on disk. Fix: the gated save is now the loader's last step.
2. **A restore right after setup found the snapshot ring empty, and no restore ever rolled back sample counts.** `async_restore_learned_snapshot` waited for the reads of the stores it rewrites but not for the snapshot store it restores from, so it read the empty constructor ring and returned False. `_apply_learner_payloads` set the four scalar learners through their setters and left each sample count at its live, drifted value. Fix: the restore also waits for `_snapshot_store`'s read. The four scalar learners now load through one parser, `_load_scalar_learners`, shared by the store loader and the snapshot restore, so a count rolls back with its learner.

**The load barrier.** The brief asks for "one load barrier that every save and restore awaits". That barrier is the store's existing read fence (`QuarantiningStore.async_wait_for_read`), not a new mechanism. Every `QuarantiningStore.async_save` already awaits it, and so does each restore and reset (ls-r1). It is a load barrier, and not merely a read barrier, exactly when the loader applies its read with no await in between. Defect 1 was the one learned loader that broke that rule. With the save moved to the end, it holds again, and the coordinator comment at the save names the invariant.

Alternatives considered:
- I wrote and measured a separate `LoadFence` (an in-flight-loads set in `store.py`, held by the thermal and snapshot loaders and awaited by both saves, the restore and the factory reset). It was rejected. Once the save moved, no mutant of its save-side waits could fail any check, so it was a parallel mechanism that nothing pins (fixer step 17: the existing mechanism, never a parallel one). It also cost a new class and the reindent of a 70-line method.
- Making the thermal loader spawn its save instead of awaiting it was rejected too: direct-call loaders in tests would lose the re-anchor write.

**Carry 1, STRANDED CARRY 55 (#2674, seven unprobed store-load leads),** is already answered, and was re-run here. #2674 is closed by probe (owner comment, 2026-11-01). Its harness `dev/audit/harnesses/r10_store_load_leads.py` (sha1 `9b69a689bda785ea14769dc8d42858a493cacbde`) prints identical `_lost=`/`fresh_call_writes` lines at base and head (`diff` of the two greps, empty). That is `price_shape_lost=0 null=0` and `extra_legionella_observer_lost=0 null=0`, every other lead `fresh_call_writes=0` with its gate-open arm `lost=1 null=0`. The census reads `0 of 12` at both. `dev/programme/carries/carry-2674.json` is owed deletion in a record PR, per that comment.

`coordinator.py` edits stay inside the learning seam (loader, restore, the new `_load_scalar_learners`, mapped `learning` in `tests/seam_map.json`). Nothing outside this group's seam changed.

## Head

`origin/main` has not moved since the `prepr.sh` run (still `c3a279e3252a8b57bb00b5a677318cd4fe20387f`), so no merge or second run was needed.

`708ec813407f9e24427f33f278ae82bb017edfca`. The fix is `69dcabb8e`. `3999ed07c` adds only the structure record, and `708ec8134` only deletes five stale ledger pins, so the gate and mutant figures taken at `69dcabb8e` describe the same production tree, branched from `origin/main` `c3a279e3252a8b57bb00b5a677318cd4fe20387f`. Every figure below was taken at that head, with the merge base as the control. Toolchain: `bash tools/audit/seat/cloud-setup.sh` then `--check` read OK, and numpy 2.5.4 / scipy 1.18.1 match `tests/requirements-ci.txt`.

## Mutation proof

Three mutants, one per gate, run by `tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'bash partial.sh'` (archive copy; `partial.sh` runs `tests/features.py` through the new checks and exits with their status). The NULL mutant survived. Each mutant's failing checks, from re-applying it to a `git archive HEAD` copy:

- **M1, the loader saves mid-load** (the gated save re-inserted before `self._measured_cop = …`, so it runs before the T4b learners load): killed. Failing checks:
  - `a thermal save issued mid-load keeps the stored COP and T4b learners in every payload` [raced `[(30, []), (30, ['-5']), (30, ['-5'])]`]
  - `a re-anchor persists exactly once`
  - `adding a power meter re-anchors both learners at zero confidence`
  - `a lower-floor sensor swap voids the ratio and leaves the scale intact`
  - `an indoor sensor swap voids the scale and leaves the ratio intact`
  - `a store without recorded zone sensors keeps both learners and adopts the ids`
- **M2, the restore skips the ring's read** (`for store in _restored_stores(self):`): killed. Failing check: `a restore issued right after setup applies the newest snapshot, sample counts included` [raced `(False, (1.0, 0, 1.0, 0))`].
- **M3, the restore drops sample counts** (the base setter loop back in place of `_load_scalar_learners(thermal)`): killed. Failing checks:
  - `a restore issued right after setup applies the newest snapshot, sample counts included` [`(True, (1.4, 0, 1.1, 0))`]
  - `a snapshot restore re-anchors a pre-edit scale, not restores it`

## Null control

Each new check carries its own null control: the same command run after the load landed (`_store_race(..., after=True)`).

- **At the base**, the save check's null fails too: `[(0, []), (30, ['-5'])]`. That is defect 1 itself, because the loader's own save carries the defaults whenever the load runs, raced or not. The restore check's null reads `(True, (1.4, 0, 1.1, 0))`: the snapshot applies, but its counts do not.
- **At the head**, both the raced and the null arms read the stored state: every saved payload is `(30, ['-5'])`, and the restore reads `(True, (1.4, 33, 1.1, 21))`.
- **A fully loaded entry still behaves as it does today:** every other check in `tests/features.py` up to the new block is unchanged (`1089` run, same set, at base and head), and the scoped gate is green (Figures).
- **The changed test is `a snapshot restore re-anchors a pre-edit scale, not restores it`.** Its snapshot now carries `house_heat_loss_samples: 300` instead of leaving 300 on the live learner. The re-anchor law weighs the snapshot's count, as the loader weighs the store's (`a converged scale is re-anchored onto the new nameplate`, same 300, same expected value).

## Figures

- New checks at base vs head (`bash partial.sh` in a base worktree and at the head; base output kept from a partial copy of `tests/features.py`):
  - base: `2 of 1089 PARTIAL FAILED`, the two new checks.
  - head: `ALL 1089 PARTIAL PASSED`.
- Mutants: `python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd "bash partial.sh" --timeout 900` printed `SURVIVED NULL`, `KILLED M1-loader-saves-mid-load`, `KILLED M2-restore-skips-ring-read` and `KILLED M3-restore-drops-sample-counts`. A first run printed `SURVIVED` for all four because the wrapper piped the runner through `grep` and lost its exit status. That was a vacuous harness, repaired before this run (Friction).
- Both ends of the restored counts' range: `ends_probe.py` (scratch, not landed) snapshots a coordinator, perturbs a second one to scale 1.6 with 77 samples, and restores into it.
  - Zero evidence: head `(True, 1.0, 0)`, base `(True, 1.0, 77)`.
  - On the clamp (`HOUSE_HEAT_LOSS_SCALE_MAX`, 500 samples): head `(True, 3.0, 500)`, base `(True, 3.0, 77)`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED`. The gate ran `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`; result: `ALL 4779 FEATURE CHECKS PASSED`, every other run script green, and `tests/structure.py` red only on three improved rows not yet recorded; they are recorded in the second commit, after which `python3 tests/structure.py` exits 0.
- Structure: `python3 tests/structure.py` breaches nothing. `class_excess_loc` and `max_class_loc` each read one below budget, unrecorded; how that was paid is in Friction.
- Class census (fixer step 8): the instrument is the setup census already in the tree. Its harness form is `dev/audit/harnesses/r10_store_races_census.py` (sha1 `dfaa8ff388283bd364f29ebb7c491f5ac33805ae`), and its in-suite form is `no write in the setup refresh is lost to a store read still in flight`. It enumerates every store the constructor builds and reads, from the constructor itself.
  - Base and head both print `census_lost_total=0 of 12` and `census_unfenced_differs=_ctx,_price_learner`, so the census is live.
  - It cannot see defect 1, because the loser there is the disk payload, not the in-memory state the census diffs. The new save check covers that seam.
  - The other learned loaders under the same rule (apply the read without an await) are `async_load_profile`, `async_load_draws`, `_async_load_price_model`, `_async_load_accuracy` and `_async_load_snapshots`. The census reads them clean at both ends.

## Red checks

- `mutation` at 708ec8134 (predicted): red by construction on the 2 sites under `## Unpinned sites`. mutation-autofix pins killed sites after the push. No cheaper detector is owed: `prepr.sh` step 6d already names each site before the handoff, and the five pins this diff made stale were deleted by hand in the third commit, as the `ledger` arm's repair directs.

## Unpinned sites

- `custom_components/heatpump_optimizer/coordinator.py:4377 GUARD_OFF` (`if save:`, the loader's gated re-anchor save): killed when applied by `mutant_run.py --spec guard_off.json --cmd 'bash partial.sh'` (`KILLED GUARD_OFF-4377`, NULL survived). Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:4388 GUARD_OFF` (`_load_scalar_learners`'s per-learner apply): killed when applied by `mutant_run.py --spec guard_off.json --cmd 'bash partial.sh'` (`KILLED GUARD_OFF-4388`, NULL survived). Pinned by mutation-autofix.

## Forward-carry

- n/a: STRANDED CARRY 55 (#2674) is answered by #2674's own probe reading, re-run at this head (description). The invariant this PR rests on (a learned loader applies its read with no await before its last assignment) is stated at the code site and pinned by the new save check; no later stage's brief changes.

## Friction

- `fixer.md#2`: unenforced: the mutation wrapper first piped the check runner through `grep`, so every mutant, NULL included, read `SURVIVED`. Nothing refuses a wrapper whose NULL and real mutants all survive; reading the uniform result caught it. Carry: dismissed: caught by reading
- `ratchet-budgets.md`: cost: the new one-parser method put `class_excess_loc` and `max_class_loc` 5 lines over their zero-headroom budgets. I paid that by shortening four comments this diff wrote, with no raise. Carry: dismissed: paid in diff
