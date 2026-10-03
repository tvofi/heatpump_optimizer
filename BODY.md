The P11 class barrier for a Home Assistant name production reaches that the 2025.2.0 floor
(`hacs.json`) does not have, the countermeasure of R9-RCA-1869. Two instances are measured:
v6.3.1 released `Platform.DIAGNOSTICS` (#210), and #1869 imported
`UnsupportedStorageVersionError` (2026.3+). Both passed every PR-gate lane, because
`tests/hastub` defines both names and nothing on the PR gate knew the floor.

- **The check.** `tests/entities.py` gains a section, "P11: every Home Assistant name
  production reaches exists at the floor", placed beside P6. It runs on P6's parsed trees
  and walks (`_P6_TREES`, `_P6_WALKS`); that closure already holds every production `.py`.
  `ha_contract.py` cannot host it, because it must not open production. It reads
  production's unguarded reach in three arms: imports, module attributes, and class
  members (followed through re-exports). Each reach is answered from the snapshot. A
  question the snapshot does not hold is `UNRECORDED` and fails, for a module and for a
  name alike. Planted null controls are included. Node ids are kept per file, as the RCA
  seat's note requires.
- **The snapshot.** `tests/ha_floor_names.json` holds 193 recorded answers. It was recorded
  from upstream source at the tag by `python3 tests/ha_floor.py record`, which walks the
  check's own decision path. Nobody edits it by hand.
- **The library and tool.** `tests/ha_floor.py` holds `check`, `record`, `verify` and
  `verify-inside`. It is `NOT_A_TEST` in `closure.py` and in both `run.sh` skip arms,
  following the `issue996_count.py` precedent.
- **The nightly truth step.** In `tests.yml` `nightly-ha`, on the `2025.2.0` arm,
  `python tests/ha_floor.py verify --image …` asks Home Assistant itself every recorded
  question again. It runs after the lane, under `!cancelled()`. A pin beside the existing
  `nightly-ha` install pin holds its wiring.
- **The record.** `tools/audit/rca/R9-RCA-1869.md` holds the RCA seat's analysis, with its
  cost labels kept as the seat set them, plus a section 5 for what landed and what it
  measured. It is cited by `rca` in P11's `bugclasses.json` entry, with an `_rca` index
  entry and both instances in `non_round_instances`.
- **The carry.** `carry-1649.json` `/carries[3]/brief` is still live, since EG-B4 has not
  merged. It gains "(2026.3+)" after the name.

**Code-owned paths: `.github/workflows/tests.yml`, `tests/run.sh` and `tests/closure.py`.**
The merge needs @tvofi's approving review. No policy file (`POLICY_GLOBS`) is touched. No
budget moves: `tests/structure.py` passes, and nothing under `custom_components/` changed.

## Head

`78d0c57c64fb614e1cb51d76fb61c8698f1efebf`, measured at merge base
`b8fa39f8c4df25bf68d1b3ce914e7b910ac45a2b`.

## Mutation proof

The countermeasure is a check. Each checker mutant was run through the section's own code,
sliced unedited from `tests/entities.py` at the head (`$SCRATCH/mutants.py`, sha1
`753294b0`), on three trees.

- **M1: guard recognition off** (`_guard_body` returns nothing). Red on `ef37a5ba1`,
  `e43ae8dc9` and origin/main:
  - FAIL `every Home Assistant name production reaches unguarded exists at the floor, and
    every one is recorded (P11 floor)`. On main the guarded and `TYPE_CHECKING` imports
    turn up unrecorded. On `e43ae8dc9` the guarded `store.py:65` is missing.
  - FAIL `and the P11 floor arm names each planted defect, passes each guarded or
    typing-only one, and fails an unrecorded import closed (null controls)`. Both
    `plant_guarded` and `plant_typing` are named.
- **M2: import arm removed.** Red on all three trees, through the same null-control check
  (`plant_import` goes unnamed). On `ef37a5ba1` the production check goes **green**, which
  shows the import arm is what catches #1869.
- **Production mutation sites:** none. `tests/mutation_table.py --scope changed` draws its
  sites from `custom_components/heatpump_optimizer/`, and this diff touches nothing there.
- **M0: unmutated.** Red on `ef37a5ba1` only, through the production check
  (`UnsupportedStorageVersionError at store.py:36`). Green on `e43ae8dc9` and on main.

## Null control

The unmodified tree at the head: `python3 tests/ha_floor.py check` prints
`checked=141 missing=0 unrecorded=0`, rc 0. The full `tests/entities.py` at the head prints
the three P11 checks `ok`. The legitimate shapes stay green:
- `e43ae8dc9`, the guarded import;
- `ef37a5ba1` with the import moved under `if TYPE_CHECKING:`, rc 0;
- `v6.3.3`, the #210 repair.

The truth control works in both directions. With three answers flipped in a copy,
`verify-inside` against real Home Assistant 2025.2.0 prints `wrong=3`, rc 1. A copy tagged
`2026.3.0` is refused.

## Figures

`D` is a scratch directory. Each tree comes from
`git archive <ref> custom_components | tar -x -C $D/<ref>`. `$SCRATCH` is this seat's
scratch, and the scripts there are cited by sha1. Every count below is printed by the
command beside it. The rule each count follows is `floor_check`'s, in `tests/ha_floor.py`.

- ef37a5ba1 (the #1869 defect): `MISSING homeassistant.helpers.storage.UnsupportedStorageVersionError at store.py:36`, rc 1 — `python3 tests/ha_floor.py check --package $D/ef37a5ba1/custom_components/heatpump_optimizer`
- e43ae8dc9 (its fix): `checked=141 missing=0 unrecorded=0`, rc 0 — `python3 tests/ha_floor.py check --package $D/e43ae8dc9/custom_components/heatpump_optimizer`
- 03ba7f70f (#1869's base): `checked=141 missing=0 unrecorded=0`, rc 0 — `python3 tests/ha_floor.py check --package $D/03ba7f70f/custom_components/heatpump_optimizer`
- origin/main b8fa39f8c, which is the head's production tree: `checked=141 missing=0 unrecorded=0`, rc 0 — `python3 tests/ha_floor.py check`
- v6.3.1 and v6.3.2: `MISSING homeassistant.const.Platform.DIAGNOSTICS (class member) at __init__.py:95`, rc 1. v6.3.3: `checked=119 missing=0`, rc 0 — `python3 tests/ha_floor.py check --package $D/v6.3.1/custom_components/heatpump_optimizer`
- origin/main with `Platform.DIAGNOSTICS` planted in `PLATFORM_LIST`: `MISSING … Platform.DIAGNOSTICS (class member) at __init__.py:128`, rc 1 — `python3 tests/ha_floor.py check --package $D/plant-diag/custom_components/heatpump_optimizer`
- the snapshot: `answers=193 true=175 false=18 undecidable=0`. Cold-cache record: 30.4 s wall, one run. A record from main alone is byte-identical to the committed file — `python3 tests/ha_floor.py record --cache $D/cache --out $D/snap.json`
- truth against Home Assistant 2025.2.0, run in a local virtualenv rather than the image: `asked=193 wrong=0`, 2.13 to 2.72 s over three runs — `python3 tests/ha_floor.py verify-inside $D/stage/ha_floor_names.json`
- in-place standing cost, timing the arm's calls on P6's trees and walks: 0.164 to 0.423 s per run over 15 runs. The same arm without walks takes 0.287 to 0.544 s. At 73 runs per round that is at most about 31 s per round; the RCA seat estimated at most about 130 s — `python3 $SCRATCH/cost.py` (sha1 `dec7a72f`)
- entities.py at the head: `ALL 2085 ENTITY CHECKS PASSED`, the three P11 checks and the nightly wiring pin among them — `python3 tests/entities.py`
- harness_headers.py at the head, the other script that reads `tests.yml`: `ALL 95 HARNESS HEADER CHECKS PASSED` — `python3 tests/harness_headers.py`
- structure ratchet: `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`
- the ledger: `0 violation(s)` — `python3 tools/audit/fold_ledger.py check`
- the code-owner surface: `uncovered_files=0`, with `tests/ha_floor.py` `NO-PR-JOB` — `python3 tools/audit/round6/D11/fix/codeowners_gap.py --check`
- the scoped gate: `MODE: FULL`, because `tests.yml` is a gate file — `python3 tests/closure.py select --diff b8fa39f8c4df25bf68d1b3ce914e7b910ac45a2b --workdir $D/scope`

## Red checks

`none`: no CI has run on this branch yet. The trigger that RCA-1869 answers was #1869's
`nightly-ha (2025.2.0)` red, and this PR is that answer.

This diff touches `tests.yml`, so the main-grading exemption does not cover `nightly-status`
or `delivery-status`. If `nightly-status` is red at this head, it is grading main's last
scheduled run, which ran without this diff (2026-10-03 08:11Z on `2e569748a`, still in
progress when this was written). The new nightly step is already covered by a cheaper
detector on every PR: the `nightly-ha re-asks the floor-names snapshot` pin in
`tests/entities.py`. At the merge base that pin would find 0 verify steps.

## Forward-carry

`.claude/workflows/carry-1649.json` `/carries[3]/brief`, the EG-B4 carry, gains the
qualifier "(2026.3+)". No later stage needs a brief change of its own: the check's refusal
names its own remedy (`python3 tests/ha_floor.py record`, or guard the reach).

## Friction

- `CLAUDE.md#new-tracked-file: cost: a new tests/*.py library needs three edits beyond its closure: NOT_A_TEST in closure.py and both run.sh skip arms, and all three files are code-owned`
- `gate-scoping.md: cost: a --single recording of entities.py cannot record a file it imports for the first time, because its own orphan check fails the recording; the two-step merge route took its rc and inert_reads from a Darwin run, and this branch kept the committed Linux values for those fields`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
