The P11 class barrier for a Home Assistant name that production reaches and the 2025.2.0
floor (`hacs.json`) does not have. This is the countermeasure of R9-RCA-1869. Two instances
are measured:
- v6.3.1 released `Platform.DIAGNOSTICS` (#210);
- #1869 imported `UnsupportedStorageVersionError`, which exists only from 2026.3.

Both passed every PR-gate lane, because `tests/hastub` defines both names and nothing on the
PR gate knew the floor. **Merge order: #1875 lands after #1869.** At #1869's current head
`ef37a5ba1` this check is red, which is a true positive; its fix `e43ae8dc9` is green.

- **The check.** `tests/entities.py` gains a section beside P6, "P11: every Home Assistant
  name production reaches exists at the floor". It reuses P6's parsed trees and walks, and
  also reads subpackages. Every reach is answered from the snapshot. A question the
  snapshot does not hold is `UNRECORDED` and fails, whether it asks about a module or a
  name. The unit:
  - unguarded imports, including a constant `__import__` or `importlib.import_module`;
  - module attributes, through an alias, a local rebind, the bare dotted spelling, or a
    constant `getattr` with no default;
  - class members, imported directly or reached through a module alias such as
    `ir.IssueSeverity.X`, with re-exports followed.
- **Guards.** A `try` counts as a guard only when a handler catches `ImportError`,
  `ModuleNotFoundError` or `AttributeError` and does not raise again. Nothing inside a `def`
  or `lambda` within that `try` is blessed. `if TYPE_CHECKING:` counts only where the name
  is typing's and the module never rebinds it.
- **Null controls.** 18 planted trees in `FLOOR_CONTROLS`, each with its expected verdict,
  plus one subpackage control. Node ids are kept per file, as the RCA seat's note requires.
- **The snapshot.** `tests/ha_floor_names.json` holds 205 answers, recorded from upstream
  source at the tag by `record`, which walks the check's own decision path. Its `_comment`
  tells a seat how to re-record and how to resolve a conflict.
- **The library and tool.** `tests/ha_floor.py`, with `check`, `record`, `verify` and
  `verify-inside` modes. It is `NOT_A_TEST` in `closure.py` and in both `run.sh` skip arms.
  Its docstring states the unit, the guards, the residual and the re-record rule.
- **The nightly truth step.** In the `nightly-ha` job of `tests.yml`, on the `2025.2.0`
  arm, Home Assistant itself is asked every recorded question again. The step runs after the
  lane, under `!cancelled()`. A wiring pin in `entities.py` holds it.
- **The record.** `tools/audit/rca/R9-RCA-1869.md`, cited by `rca` in P11's
  `bugclasses.json` entry, which also gains its `_rca` index and both instances.
- **The carry.** In `carry-1649.json`, `/carries[3]/brief` gains "(2026.3+)".

**Round 1** (the verdict on a401932fc). Arm C now reads `z.C.n` where `z` names a module.
That spelling covers 35 production sites, every one unread before:
- 20 `ir.IssueSeverity.WARNING`;
- 15 `selector.*SelectorMode` or `selector.TextSelectorType` members.

The same round made these changes:
- closed the cheap residuals: the bare dotted spelling, a rebind, a constant `getattr`,
  dynamic import, subpackages, and the three guard-gaming shapes;
- killed both surviving mutants, each with its own plant;
- made the refusal and the snapshot name Python 3.12+ and an authenticated `gh`;
- re-recorded the snapshot (193 answers became 205);
- merged origin/main.

**For any branch that adds a Home Assistant name:** re-record in that branch with
`python3.13 tests/ha_floor.py record`, or any Python 3.12 or newer, with `gh`
authenticated. A seat without `gh` hands the re-record on. On a JSON conflict, take either
side, finish the merge, then re-record. The check's own refusal prints this.

**Code-owned paths: `.github/workflows/tests.yml`, `tests/run.sh` and `tests/closure.py`.**
The merge needs @tvofi's approving review. No policy file (`POLICY_GLOBS`) is touched, and
no budget moves.

## Head

`e61e39f4c880496af72afb76a3731c0018453eb9`, measured on a merge of origin/main at
`8c6e9a7ef`.

## Mutation proof

The countermeasure is a check. There were 17 single-edit mutants of `tests/ha_floor.py`,
built by `$SCRATCH/mut2/make.py` (sha1 `8ba1e75f`). Each was run through the section's own
code, sliced unedited from `tests/entities.py` (`$SCRATCH/mutants.py`, sha1 `762c8e03`), on
`ef37a5ba1`, `v6.3.1` and the head's own tree.

**All 17 are killed at the head.** For each one, FAIL `and the P11 floor arm names each
planted defect, passes each guarded or typing-only one, and fails an unrecorded import closed
(null controls)`:
- guard recognition off;
- import arm off;
- member arm off;
- fail-open (an unknown answer read as true);
- attribute arm off;
- `Exception` accepted as a guard (a survivor in round 1; `plant_except_exception` now kills
  it);
- annotations treated as typing-only without `from __future__ import annotations` (a
  survivor in round 1; `plant_no_future` now kills it);
- chain arm off;
- re-raise handler accepted;
- `def` bodies blessed;
- any `TYPE_CHECKING` accepted;
- bare dotted spelling off;
- rebind off;
- `getattr` off;
- dynamic import off;
- flat `glob` (killed by the subpackage control);
- a `getattr` with a default counted as a reach.

With guard recognition off, the production check also fails at the head, so the guards
are load-bearing. With the import arm off, `ef37a5ba1`'s production check goes **green**,
which shows the import arm is what catches #1869.

**Production mutation sites: none.** `tests/mutation_table.py --scope changed` draws its
sites from `custom_components/heatpump_optimizer/`, and this diff touches nothing there.

## Null control

The unmodified head tree passes: `python3 tests/ha_floor.py check` prints
`checked=147 missing=0 unrecorded=0`, rc 0.

The full `tests/entities.py` passes at the head, with all three P11 checks and the wiring pin
`ok`.

The legitimate shapes stay green:
- `e43ae8dc9`, the guarded import;
- `ef37a5ba1` with the import moved under a real `if TYPE_CHECKING:`;
- `v6.3.3`;
- the `plant_guarded`, `plant_typing` and `plant_getattr_default` controls.

The truth control works in both directions:
- three flipped answers give `wrong=3`, rc 1;
- a copy tagged `2026.3.0` is refused.

## Figures

`D` is a scratch directory, and each tree comes from
`git archive <ref> custom_components | tar -x -C $D/<ref>`. `$SCRATCH` is this seat's
scratch, and the scripts there are cited by sha1. Each count is printed by the command beside
it and follows `floor_check`'s rule in `tests/ha_floor.py`.

- ef37a5ba1 (the #1869 defect): `MISSING homeassistant.helpers.storage.UnsupportedStorageVersionError at store.py:36`, rc 1 — `python3 tests/ha_floor.py check --package $D/ef37a5ba1/custom_components/heatpump_optimizer`
- e43ae8dc9 (its fix): `checked=147 missing=0 unrecorded=0`, rc 0 — `python3 tests/ha_floor.py check --package $D/e43ae8dc9/custom_components/heatpump_optimizer`
- 03ba7f70f (#1869's base): `checked=147 missing=0 unrecorded=0`, rc 0 — `python3 tests/ha_floor.py check --package $D/03ba7f70f/custom_components/heatpump_optimizer`
- the head's production tree: `checked=147 missing=0 unrecorded=0`, rc 0 — `python3 tests/ha_floor.py check`
- v6.3.1 and v6.3.2: `MISSING homeassistant.const.Platform.DIAGNOSTICS (class member) at __init__.py:95`, rc 1. v6.3.3: `checked=125 missing=0`, rc 0 — `python3 tests/ha_floor.py check --package $D/v6.3.1/custom_components/heatpump_optimizer`
- the head with `Platform.DIAGNOSTICS` planted in `PLATFORM_LIST`: `MISSING … Platform.DIAGNOSTICS (class member) at __init__.py:128`, rc 1 — `python3 tests/ha_floor.py check --package $D/plant-diag/custom_components/heatpump_optimizer`
- chained members read at the head: 6 questions over 35 sites (20 `issue_registry.IssueSeverity.WARNING`, 15 `selector` members), every one answered true — `python3 $SCRATCH/chain_census.py` (sha1 `129044dd`)
- the fix reviewer's 20 plants plus the selector and issue-registry chains: 18 of 22 detected. The silent four are the relative re-export and the use after a guard (both residual, stated), the attribute of `__import__(...)`'s result (residual; the module itself is checked), and a real guard with a fallback (legitimate) — `python3 $SCRATCH/plants/plants.py` (sha1 `51f2d64b`)
- the snapshot: `answers=205 true=182 false=23 undecidable=0`. Recorded from the head alone, it is byte-identical to a record made with `e43ae8dc9` beside it — `python3.13 tests/ha_floor.py record --cache $D/cache --out $D/snap.json`
- truth against Home Assistant 2025.2.0, in a local virtualenv rather than the image: `asked=205 wrong=0` — `python3 tests/ha_floor.py verify-inside $D/stage/ha_floor_names.json`
- in-place standing cost, timing the arm's calls on P6's trees and walks: 0.367 to 0.665 s per run over 15 runs. The same arm without walks takes 0.474 to 0.819 s. At 73 runs per round that is at most about 49 s per round; the RCA seat estimated at most about 130 s — `python3 $SCRATCH/cost.py` (sha1 `d590b216`)
- entities.py at the head: `ALL 2086 ENTITY CHECKS PASSED` — `python3 tests/entities.py`
- harness_headers.py at the head, the other script that reads `tests.yml`: `ALL 95 HARNESS HEADER CHECKS PASSED` — `python3 tests/harness_headers.py`
- structure ratchet: `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`
- the ledger: `0 violation(s)` — `python3 tools/audit/fold_ledger.py check`
- the scoped gate: `MODE: FULL`, because `tests.yml` is a gate file — `python3 tests/closure.py select --diff 8c6e9a7ef --workdir $D/scope`

## Red checks

`nightly-status` was red at a401932fc. This diff touches `tests.yml`, so the main-grading
exemption does not apply, and the red is answered here.

**What it reports:** `NIGHTLY FAILED: mutation-ledger failed last night`. That is scheduled
run 37108891698 on main at `2e569748a`, job 111162760555, with `MUTATION TABLE REFUSED`:
- the null control `__init__.py:42 NULL_COMMENT` was "killed" by `tests/harness_headers.py`;
- the killer was `tools/audit/round4/D7/sysid_estimator_frontier.py`, which exited
  `rc=-24` (SIGXCPU) under the harness's CPU limit and printed no RESULT lines.

**Cause:** a CPU-time kill in main's nightly mutation lane. It is outside this diff: the diff
edits only the `nightly-ha` job in `tests.yml`, and touches neither `harness_headers.py`,
that harness, nor the `mutation-ledger` job.

**Owner:** the orchestrator, on main's nightly lane, which #1872's BLAS pin did not settle.

**Cheaper detector from this diff:** none exists; the red is not this diff's. Its proof is a
green dispatch of `tests.yml` on main once the lane is fixed, and that run id is not
available at this head.

`nightly-ha (2025.2.0)` on #1869 was the trigger RCA-1869 answers, and this PR is that
answer.

## Forward-carry

`.claude/workflows/carry-1649.json` `/carries[3]/brief`, the EG-B4 carry, gains the
qualifier "(2026.3+)".

The re-record rule is not carried into a policy file (`fixer.md` is owner-gated). It is
written where a seat meets it instead:
- the check's refusal text (`ha_floor.REMEDY`);
- the snapshot's `_comment`;
- the `tests/ha_floor.py` docstring.

## Friction

- `CLAUDE.md#new-tracked-file: cost: a new tests/*.py library needs three edits beyond its closure: NOT_A_TEST in closure.py and both run.sh skip arms, and all three files are code-owned`
- `gate-scoping.md: cost: a --single recording of entities.py cannot record a file it imports for the first time, because its own orphan check fails the recording; the two-step merge route took its rc and inert_reads from a Darwin run, and this branch kept the committed Linux values for those fields`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
