D3 pin harvest, round 11 (proposal P-R11-D3-PIN-HARVEST). The round-11 D3 finder boxes measured mutant kills of sites unpinned in the mutation ledger, but nothing wrote those kills to `tests/mutation_ledger/killed_by/`, so later rounds would screen them again. This branch enumerates every mutant a D3 box reports KILLED, re-drives each unpinned one at origin/main 46d0a521 through `tests/mutation_table.py`'s own drain, and records the kills that reproduce through `mutation_table.apply_pins` / `apply_drained`. No production file changes, and no budget is raised.

`--pin-killed` only drives sites a diff adds, and `--drain` drives a seeded slice of the whole stock, so neither can be pointed at a list of anchors. `dev/audit/rounds/round11/D3/harvest/pin_harvest.py` narrows the drain's pool (`drain_pool`) to the box-reported anchors and changes nothing else. The drive, the kill rule, the baseline, the null control, `pin_results`' whole-anchor rule and `write_drain` all stay mutation_table's. It sits with the round's evidence, not in `tools/audit/seat/`, because its self-test arm would otherwise owe a workflow run line under `selftest_wiring.py`. The alternatives were a `--anchors` option on `mutation_table.py`, a change to a grader CI runs from the base copy, and hand-writing `pins.json` from `--anchor` reports, which would mean hand-edited pins. Both lost.

Sources read, all of them:
- every `dev/audit/rounds/round11/D3/s1/state/results/<bucket>/*.json` on main (the boxes m5, rem, top6 and u1a–u1d land their records there), verdict `KILLED`;
- `dev/audit/rounds/round11/D3/s2/drive/pairs.jsonl`, `hit: true`;
- each `refs/heads/handoff/audit-r11-find-D3-*` box ref (g01–g47, g46-h, g47-h, m5, rem, top6, u1a–u1d), its `s1/wave/D3-*/results/*.json` with `gate.verdict == KILLED`, mapped to an anchor through the main record that shares the key.

The verify refs (D3W, VD3L), the judge ref (`JUDGE.json`: verdicts `verified|merged|weakened|unreproduced`) and the D3 fold carry no per-mutant KILLED verdict of their own. The fold is used for the collision split.

Method:
1. **Batching.** Each candidate was driven with `--scripts` set to the script its box named, so the run re-verifies the box's own kill.
2. **Pass 2.** Fourteen anchors had only `tests/stress.py` or `tests/harness_headers.py` as their box killer. mutation_table's full scope never drives either script, because each measures the machine. Those 14 were re-driven with the default driver set.
3. **Collisions.** A candidate is deferred:
   - to a D3 fold group when its anchor is one of that group's findings, resolved through the shared result key;
   - to an open pull request when that PR's diff removes, in the same file, a line equal to a line of the site's `old` text, or touches the site's row file.

   Ledger rows are one file per anchor, so a pin of a different anchor in the same production file touches no file a group edits.

## Head

`70ca147447d5` is this PR's head, a merge of main only: it adds no change to the branch's own files. The previous head was `394bfe187c7f60f1565abe03a9eb7f525490a4eb`.

`fb32d8db2d003c31f9bcb67462d3b8f06d85fef3`: the branch, cut from origin/main `46d0a521befa01ff62cf647e04d3a2b783ea2fc1`, with origin/main `ef797d794017c98f7fb2d8a168d7de63d435ef3b` merged in, because merge-tree reported 13 add/add conflicts on `killed_by` rows main had pinned meanwhile. main's copy of each is kept. Every drive ran at `b987439d5545278ede5a0c46aad1ac19286d9313`, the harvest scripts' commit on that base. The 305 rows were applied there with `apply_pins`, and the pass-2 row was applied at `34867f49` with `apply_drained`, whose re-key against the inventory drops any row whose anchor or `old` text moved.

## Mutation proof

The harvest changes no production line. The proof that each row's killer kills its site is mutation_table's own measurement. Each row's `reason` records the driver's baseline and mutant rc and failed-check counts, for example `GUARD_OFF (if False:) took tests/entities.py from rc=0 failed=0 to rc=1 failed=3.`

Each batch's drive ran mutation_table's comment-only null control through every driver in play, and every batch report records `null control ... survived every driver` (`dev/audit/rounds/round11/D3/harvest/drive/*/report.txt`). A drive whose null control dies refuses.

prepr's diff-mutant step, run with `PREPR_SKIP_CLOSURES=1` and `MUTANT_CMD=python3 dev/audit/rounds/round11/D3/harvest/pin_harvest.py --self-test`, printed `ok       diff mutants           [1s] no survivor among the diff's first 40 mutant(s) under: python3 dev/audit/rounds/round11/D3/harvest/pin_harvest.py --self-test`. The diff adds no `.py` line outside `tests/` and `dev/`, which is where that step draws from.

For `pin_harvest.py` itself, `python3 dev/audit/rounds/round11/D3/harvest/pin_harvest.py --self-test` covers the pool narrowing. Its two checks fail if `narrowed` stops filtering or stops passing the drain's arguments through.

## Null control

At the head, `pin_harvest.py drive` declines both anchors of this pair and drives nothing (`HARVEST -- 0 of 2 anchor(s) unpinned at HEAD`, `DRAIN: nothing drivable`):
- `__init__.py:async_unload_entry GUARD_OFF 160eafd4`, which a box reported KILLED and which already holds a row at main;
- `__init__.py:<module> GUARD_OFF e1433e05`, unpinned at main (its row path does not exist in `origin/main`) and pinned by this branch (killed by `tests/entities.py`).

## Figures

Drives and dispositions measured against 46d0a521; the unpinned counts at ef797d79 and the head were taken after the merge, 2026-11-27.

- enumerated: 542 KILLED identities (532 ledger anchors and 10 non-ledger hand-mutant ids), of which 356 are unpinned at main, 158 already disposed and 18 gone from main's inventory. Command: `python3 -I dev/audit/rounds/round11/D3/harvest/enumerate.py UNPINNED.json CAND.json DECLINED.json`.
- dispositions: 306 pinned, 36 dropped-not-reproduced, 18 dropped-anchor-gone, 13 deferred-fold, 1 deferred-pr, 158 declined-already-disposed, 10 declined-not-inventory. Command: `cut -f1 dev/audit/rounds/round11/D3/harvest/DISPOSITIONS.tsv | sort | uniq -c`.
- unpinned sites: 1818 at 46d0a521 and 1504 at the pre-merge head e3cfbde1, a fall of 314 sites under 306 anchors; 1739 at origin/main ef797d79 and 1446 at the head, a fall of 293, because main had already pinned 21 of the 306 anchors itself, so the branch adds 285 rows. Command: `python3 -I -c 'import sys; sys.path.insert(0,"tests"); import mutation_table as m; print(len(m.unpinned_sites(m.load_budgets(), m.inventory())))'`, run at each SHA.
- deferred-fold, 13 anchors by group: R11-D3-PINS-solver 6; R11-SEAM-cycle-reporting-p2, R11-D3-PINS-fabric, R11-D3-PINS-inputs, R11-SEAM-store-p2, R11-D3-PINS-sysid, R11-D3-PINS-money and R11-D3-PINS-plant 1 each. Command: `awk -F'\t' '$1=="deferred-fold"{print $3}' dev/audit/rounds/round11/D3/harvest/DISPOSITIONS.tsv | sort | uniq -c`. Carry: dismissed: each anchor is one of that group's own finding sites, pinned by that group's pull request
- deferred-pr, 1 anchor: `thermal_model.py:ThermalModel.simulate_trajectory BOOLOP e31090ce`, deferred to #3914. Command: `awk -F'\t' '$1=="deferred-pr"' dev/audit/rounds/round11/D3/harvest/DISPOSITIONS.tsv`. Carry: dismissed: #3914 rewrites the site's line, so the site it leaves is that pull request's to pin
- dropped-not-reproduced, 36 anchors, by drive: 12 lived under every default driver and were killed in the box only by `tests/stress.py`; 8 survived `tests/features.py`; 7 `tests/structure.py`; 3 `tests/entities.py`; 2 `tests/manual_plan.py`; 1 `tests/plan_view.py`; 1 `tests/solar_alignment.py`; 1 timed out in pass 2 (box killer `tests/harness_headers.py`); 1 whose only box killer (`node tests/card.mjs`) is not a mutation_table driver. Command: `awk -F'\t' '$1=="dropped-not-reproduced"{sub(/.*\| drive /,"",$3); print $3}' dev/audit/rounds/round11/D3/harvest/DISPOSITIONS.tsv | sort | uniq -c`.
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`).

## Red checks

- `tests / closures`: red at 394bfe18 as UNDER-SCOPED, repaired by the closures-autofix bot's `ci: re-record closures` commit. A cheaper detector exists: prepr step 6d, `--single`, run before the handoff would have printed it. The branch did not run it.
- `pr-contract` and `gate`: red only because this section carried no line for `tests / closures`; this line answers it.

## Forward-carry

- `typing_ruler.py` holds 82 of the pins, and each is a growth in the mypy census under the pinned toolchain (`HPO_TYPING_PYTHON`). No `.github/workflows` file sets that variable, so the census reproduces only in the `typing` job, not in a gate lane. A later round re-verifying these rows must run with the pinned toolchain, or it will read them as `PIN NOT REPRODUCED`. Carry: dismissed: a precondition of re-verification, recorded in this body and in each row's driver name; no stage brief re-verifies these rows.

## Friction

- tool-gap: cost: `mutation_table.py` has no path that pins a given list of pre-existing anchors (`--pin-killed` is diff-only, `--drain` is a seeded slice, `--anchor` records nothing), so a harvest needs the pool-narrowing driver added here. Carry: dismissed: the driver is tracked with the round's evidence and reruns as-is
- stale-anchor: unclear: 18 box-reported anchors no longer exist in main's inventory, because their line text or scope changed since 92d38ecb. They were not mapped to successor sites, which remain in the unpinned stock the nightly drain walks. Carry: dismissed: a successor is a new site with no box measurement of its own

## Unpinned sites

n/a: the diff adds no production site. The 36 box-reported kills that did not reproduce are listed with their drive and reason in `dev/audit/rounds/round11/D3/harvest/DISPOSITIONS.tsv` (`dropped-not-reproduced`), and survivors are listed, never triaged.

