R10-LEARNED-STORE-LOAD: two latent learned-store lifecycle defects, found by the R10-FACTORY-RESET fixer, each reproduced through the production coordinator and fixed in `coordinator.py`'s learning seam.

1. **A save during the thermal load wrote the COP and T4b learners' defaults.** `_async_load_thermal_learning` awaited its gated re-anchor save halfway through applying the read. That was before `_COP_STORE_KEY`/`cop_samples`, `measured_cop`, the cusums, the COP baselines and every `_load_t4b_learners` key had loaded. So the saved payload (the loader's own, and any save scheduled behind the read) carried those learners as defaults. A restart in that window lost them on disk. Fix: the gated save is now the loader's last step.
2. **A restore right after setup found the snapshot ring empty, and no restore ever rolled back sample counts.** `async_restore_learned_snapshot` waited for the reads of the stores it rewrites but not for the snapshot store it restores from, so it read the empty constructor ring and returned False. `_apply_learner_payloads` set the four scalar learners through their setters and left each sample count at its live, drifted value. Fix: the restore also waits for `_snapshot_store`'s read. The four scalar learners now load through one parser, `_load_scalar_learners`, shared by the store loader and the snapshot restore, so a count rolls back with its learner.

**The load barrier.** The brief asks for "one load barrier that every save and restore awaits". That barrier is the store's existing read fence (`QuarantiningStore.async_wait_for_read`), not a new mechanism. Every `QuarantiningStore.async_save` already awaits it, and so does each restore and reset (ls-r1). It is a load barrier, and not merely a read barrier, exactly when the loader applies its read with no await in between. Defect 1 was the one learned loader that broke that rule. With the save moved to the end, it holds again, and the coordinator comment at the save names the invariant.

Alternatives considered:
- I wrote and measured a separate `LoadFence` (an in-flight-loads set in `store.py`, held by the thermal and snapshot loaders and awaited by both saves, the restore and the factory reset). It was rejected. Once the save moved, no mutant of its save-side waits could fail any check, so it was a parallel mechanism that nothing pins (fixer step 17: the existing mechanism, never a parallel one). It also cost a new class and the reindent of a 70-line method.
- Making the thermal loader spawn its save instead of awaiting it was rejected too: direct-call loaders in tests would lose the re-anchor write.

**Carry 1, STRANDED CARRY 55 (#2674, seven unprobed store-load leads),** is already answered, and was re-run here. #2674 is closed by probe (owner comment, 2026-11-01). Its harness `dev/audit/harnesses/r10_store_load_leads.py` (sha1 `9b69a689bda785ea14769dc8d42858a493cacbde`) prints identical `_lost=`/`fresh_call_writes` lines at base and head (`diff` of the two greps, empty). That is `price_shape_lost=0 null=0` and `extra_legionella_observer_lost=0 null=0`, every other lead `fresh_call_writes=0` with its gate-open arm `lost=1 null=0`. The census reads `0 of 12` at both. `dev/programme/carries/carry-2674.json` is owed deletion in a record PR, per that comment.

`coordinator.py` edits stay inside the learning seam (loader, restore, the new `_load_scalar_learners`, a `tests/features.py` disposition for the learner-feeder class check, mapped `learning` in `tests/seam_map.json`). Nothing outside this group's seam changed.

## Head

`c6444f38f775cb9859e80a0dfcb0fd420b6e390b`. Branched from PR head `876c1c4e38d2d768580f804c3135236678485a76`, with `origin/main` `8e90d81443317f76f22602a89651f7ca17c633f9` merged in (the #3180 hotfix included; tip read 2026-11-04, `prepr.sh` rerun after that merge). The fix is `69dcabb8e`. The repair commits on top change the parser's spelling only (below), drop the one ledger pin that spelling made stale, and add one `tests/features.py` disposition. The mutation proofs were taken at `69dcabb8e`, where the three predicates they break (the save's position, the ring's read wait, the shared parser) are the ones this head still carries; the checks they killed pass at this head (`ALL 4779 FEATURE CHECKS PASSED`). Toolchain: `bash tools/audit/seat/cloud-setup.sh` then `--check` read OK, numpy 2.5.4 / scipy 1.18.1 match `tests/requirements-ci.txt`.

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
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED`. The gate ran `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`; result: `ALL 4779 FEATURE CHECKS PASSED`, `tests/golden.py` and `tests/guard_pins.py` rc=0, `tests/entities.py` `ALL 2602 ENTITY CHECKS PASSED`.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED` at the head. A first spelling of the parser put `class_excess_loc` and `max_class_loc` 3 lines over budget (`FAIL class_excess_loc 17642 > 17639`); the compacted spelling clears it with no raise.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` printed `Architecture score: dS +0.0042 IMPROVES` with `coord_footprint 2381 -> 2374`; no reflective write or computed attribute access is added (see Red checks).
- Class census (fixer step 8): the instrument is the setup census already in the tree. Its harness form is `dev/audit/harnesses/r10_store_races_census.py` (sha1 `dfaa8ff388283bd364f29ebb7c491f5ac33805ae`), and its in-suite form is `no write in the setup refresh is lost to a store read still in flight`. It enumerates every store the constructor builds and reads, from the constructor itself.
  - Base and head both print `census_lost_total=0 of 12` and `census_unfenced_differs=_ctx,_price_learner`, so the census is live.
  - It cannot see defect 1, because the loser there is the disk payload, not the in-memory state the census diffs. The new save check covers that seam.
  - The other learned loaders under the same rule (apply the read without an await) are `async_load_profile`, `async_load_draws`, `_async_load_price_model`, `_async_load_accuracy` and `_async_load_snapshots`. The census reads them clean at both ends.

## Architecture score

The first spelling of `_load_scalar_learners` wrote the sample counts through `setattr(self, f"_{samples}", n)`, which the gate measured as `reflective_writes 11->12` and `computed_attr_access 28->29` (arch-score run 126496102862). Paid by improving the code, not by explaining it: the parser now assigns the four sample counts by name from one generator, with no computed attribute. `score.py --diff origin/main` now reads `dS +0.0042 IMPROVES` (`coord_footprint 2381 -> 2374`), so no metric rises and no explanation line is owed.

## Red checks

Every concluded red check at PR head `876c1c4e38d2d768580f804c3135236678485a76`, from the whole check-run set (`get_check_runs`, 81 runs, read in one page):

- `arch-score / arch-score` (BRANCH-OWNED): `dS +0.0042 WORSENS (reflective_writes 11->12; computed_attr_access 28->29)`. Paid, see `## Architecture score`. No cheaper detector is owed: `archscore/score.py --diff origin/main` is the check's own instrument and runs offline in seconds; this seat did not run it before the first push.
- `tests / replay` (MAIN-OWNED): `synthetic-dhw-only.json cycle_cost cpu_ratio 2.851 over budget 2.173`, the host-class cost-budget flake that #3174 R10-REPLAY-COST-BUDGET addresses (#3167 hit the same). Main's own slow lane failed the same check at run 41749544997, job 126403921052: `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 3.382 over its budget 2.173]`, `1 of 176 replay checks FAILED`. The branch does not touch the replay path: `git diff $(git merge-base origin/main HEAD)...HEAD --stat` names `coordinator.py`'s learned-store loader and restore (load and restore time, not the per-cycle path the replay times), `tests/features.py`, the delivery row, `tests/seam_map.json`, `tests/structure_budgets.json` and golden ledger pins. The budget is not changed here.
- `tests / mutation` (BRANCH-OWNED, red at earlier commits of this branch, green at the PR head `876c1c4e38d2d768580f804c3135236678485a76`, runs 126496102859 and 126496066770): red by construction on the two new unpinned GUARD_OFF sites the diff added, which `prepr.sh` step 6d predicted; cleared by mutation-autofix's `ci: pin killed mutants` commit. No cheaper detector is owed: step 6d already names each site before the handoff, and the standing cost is one autofix commit per diff that adds a guard.
- `tests / nightly-status` (MAIN-OWNED, unrequired): grades main's slow lane; it is red because the lane above (job 126403921052) failed on the same replay `cycle_cost`. Nothing in this diff feeds it.
- `pr-contract / pr-contract` and `gate`: red on the unanswered reds above plus an HTTP 502 reading the check-runs (transient); they aggregate the others and are answered by this section.

## Unpinned sites

- none: the diff adds no unpinned mutation site (`prepr.sh` step 6d: `the diff adds no unpinned mutation site`). The parser's respelling removed the guard line the ledger pin `GUARD_OFF.3986447e` named, so that pin was deleted as the `ledger` arm's repair directs; the save guard's pin (`GUARD_OFF` on `if save:`) stays.

## Forward-carry

- n/a: STRANDED CARRY 55 (#2674) is answered by #2674's own probe reading, re-run at this branch (description). The invariant (a learned loader applies its read with no await before its last assignment) is stated at the code site and pinned by the new save check; no later stage's brief changes.

## Friction

- `fixer.md#2`: unenforced: the mutation wrapper first piped the check runner through `grep`, so every mutant, NULL included, read `SURVIVED`. Nothing refuses a wrapper whose NULL and real mutants all survive; reading the uniform result caught it. Carry: dismissed: caught by reading
- `ratchet-budgets.md`: cost: the one-parser method put `class_excess_loc` and `max_class_loc` over their zero-headroom budgets twice (5 lines, then 3 after the arch-score respelling). Paid by shortening comments and compacting the parser, with no raise. Carry: dismissed: paid in diff
