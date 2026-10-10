# R9-UX-10 — fixer seat note (2026-10-09, updated through 2026-10-10)

## Read this first: the topic was already handed off once

`refs/heads/handoff/r9-ux-10` already carries **`bcbc1af3b`** (2026-10-08
02:37, author Tvofi2): a complete R9-UX-10 handoff with its own body at
`refs/heads/handoff-body/r9-ux-10` (`87e22e92c`), four commits, a mutation
proof and a null control. No pull request was ever opened for it (`gh pr list
--state all --head fix/r9-ux-10` → `[]`). It is stacked on `handoff/r9-ux9` at
`543393cc`, i.e. cut **before #2024 merged**, and its body says "Retarget or
update this PR from `main` only after #2024 merges". #2024 merged on
2026-10-09 as `a8ce87571`; this seat was dispatched from that tip and did not
know the earlier handoff existed until it went to push.

**Nothing was overwritten.** A handoff head is frozen and only the orchestrator
moves it (`fixer.md` step 6), and the push would have been a non-fast-forward.
This seat's work is on two new refs:

- code head `refs/heads/handoff/r9-ux-10-v2` = `ff2c85753644cf2f713b9da312758869954fbd4a`
- body `refs/heads/handoff-body/r9-ux-10-v2` (`BODY.md` + this note)

**The choice between the two designs is the orchestrator's.** `BODY.md`'s "A
prior handoff already holds this topic" section carries the four measured facts
that bear on it; in one line each:

1. that branch's `structure_budgets.json` records `max_class_loc` 9047 and
   `seam_cut_total` 767, which against today's main (8818 / 762) are **raises**,
   so `budget-raise-gate` (0013) refuses it without the owner's approving
   review; this branch records 8795 / 760, both **down**, and asks for nothing.
2. that branch routes the metered heat through `simulate_step`'s
   `external_heat_kw` — the wood furnace's channel — and had to carve out
   two-tank plants because of it; this branch adds `measured_heat_kw` as the
   pump's own term and carves out nothing.
3. that branch rejected the two learners' replay dedupe because the archscore
   corpus plants it as `G2_dedupe`; measured here, the planted cases run against
   the **pin** (`tests/arch_score.py`'s smoke arm calls `cases.extract_pin`), so
   landing it does not touch the corpus.
4. that branch **measured** the divide-by-COP alternative missing by up to
   0.1639 K on a throttled two-zone Carnot plant, which is better evidence than
   this branch's reasoning for rejecting the same design. They agree.

Both feed the same two interval learners, both refuse a hot-water interval,
both leave the COP learner alone for the same reason.

## State at this head (2026-10-10, third session of this lane)

- Code head `ff2c85753` is **already pushed** to `handoff/r9-ux-10-v2`, and its
  merge base is `origin/main`'s tip `7cd5a588c` — three merges land in it
  (`7297c1bd1` for `23d354970`, `d3fbdcf63` for `7cd5a588c`), no new one is
  owed, and `git rev-list --count HEAD..origin/main` is 0.
- **The ledger composition, re-derived at this head, is six unpinned sites, all
  of them this diff's, and no stale pin**: `PYTHONPATH=tests/hastub python3
  tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: 6 unpinned
  site(s) the diff adds`, `CI PREDICT: no closures or fast red predicted against
  7cd5a588cbbb`, and no `STALE PIN` line in either arm; the same six print with
  `--base a8ce87571`, because the predictor subtracts the base's own unpinned
  set. The sites are `coordinator.py:828 GUARD_OFF`, `:828 CMP_BOUND*2`,
  `:830 RETURN_DEL`, `:5029 GUARD_OFF`, `:5184 GUARD_OFF` and
  `thermal_model.py:2604 CLAMP_DROP`, each with its reason in `BODY.md`'s
  `## Unpinned sites`.
- **A report that reached this seat described eleven sites** at an earlier head,
  with `_coarsen`'s "pre-existing shifted" entries dropping out and
  `_without_private_ids` contributing four of its own. Neither string exists in
  the tree — `git grep -lE "_without_private_ids|pre-existing shifted"
  origin/main` and the same pattern over the working tree both print nothing —
  and no instrument here prints eleven at either head, so that composition could
  not be reproduced and is **not** carried. The body says so in place, with the
  two commands.
- The censuses the retarget asked for, re-derived: `claims.py` →
  `claims_extracted=125`, `claims_checked=125`, `claims_true=123`,
  `claims_false=0`, `claims_stale=0`, `claims_unverifiable=2`,
  `arch_modules_on_disk=75 modules`, `arch_map_listed=75 modules`,
  `arch_map_missing=0 modules`, `ha_module_level_importers=27 modules` (the
  74-vs-75 merge-only-false class is consistent at 75); `deployment_shape.py` →
  `ALL DEPLOYMENT SHAPE CHECKS PASSED`; `arch_score.py --smoke` → `ALL 257
  ARCHITECTURE SCORE CHECKS PASSED`; `arch_score_head.py` → `ALL 15 ARCHITECTURE
  SCORE HEAD CHECKS PASSED`; `entities.py` → `ALL 2285 ENTITY CHECKS PASSED`.
- `structure.py` → `STRUCTURE RATCHET PASSED`, still 37 / 8795 / 760 against
  main's 38 / 8818 / 762, with `recorded_at` re-pointed to `7cd5a588c`.
- `field coverage` (the orchestrator's `app_push.sh` refusal) **does not
  reproduce**: `node tools/policy/field_coverage.mjs` → rc=0, `blind=0 dead=0
  refused=0 runs=139`, `FIELD COVERAGE ok`. Run it directly, not through
  `prepr.sh`, which deletes its own detail (`BODY.md`'s `## Friction`).
- Two scoped scripts could not be re-run to the end on this head because the box
  sat at load 65-80 with nineteen competing test processes: `tests/features.py`
  (its complete run at the previous head read `1 of 3938`, the one being the
  BLAS-class storage check) and `harness_headers.py` (green at the previous
  head; `12 of 109` here, all the D7 wall-limit shape). Both are named as such
  in the body and both are CI's at this head.

## What this seat's branch contains

- `ThermalModel.simulate_step(..., measured_heat_kw=None)`, spent in place of
  `cop * electrical_power` in both zone steps; `None` is byte-identical to
  omitting it (asserted), and free external heat still joins it.
- `coordinator._interval_measured_heat_kw` (one predicate: a reading exists,
  the plan gave the interval to space heating) and `coordinator._replay_interval`
  (the dedupe of the two learners' identical replay block, and the one place the
  parameter is passed). Both are module-level helpers with `learning` entries in
  `tests/seam_map.json`.
- `docs/configuration.md`'s flow row no longer says "read for display only".
- 8 new checks in `tests/features.py`'s #2016 block, and
  `dev/audit/harnesses/ux10_flow_into_model.py`, which runs that block (sliced
  verbatim out of the file) in **14 copies of the tree**: head, merge base
  (the failing-first red, 6 checks), and one mutant per added site plus the two
  `flow_meter` predicates the learner input now inherits. Every mutant is
  killed except `_replay_interval`'s `except`-arm `return None`, which is
  equivalent and carries a `survivor_triage` row.
- `tests/structure_budgets.json` re-recorded **down** (37 / 8795 / 760) with the
  reasons in commit `69d2dab1f`. No raise, no budget moved up.
- Ten commits; the last (`ff2c85753`) follows two source-text pins in
  `tests/features.py` whose subject the extraction moved — the #1520 humidity
  seam allow-list (now one entry for the shared helper, 9 allowed and 9 live)
  and #53's `hour_of_day` pin (now read out of the helper, and holding both
  learners to calling it). The full run at this head is `1 of 3887 FEATURE
  CHECKS FAILED`, and the one is a solver-objective check that fails
  identically at the merge base on this box (`## Red checks` 4).
- `## Architecture score` explains the one gate metric that rises
  (`coord_footprint` 2586 → 2590), verified by running `origin/main`'s own
  `tools/audit/archscore/gate.py` `unexplained()` against the body: `[]`. That
  required check landed on main in #2068, after this branch's merge base, so it
  will only fire once main is merged in — the section is there for when it does.
- Both golden claim files byte-identical to the merge base; `VERSION`, the
  manifest and the `RELEASE_NOTES.md` heading untouched.

## What the orchestrator owes

- Choose a branch. If this one: `tools/audit/seat/handoff_push.sh r9-ux-10-v2
  f9809c06ae7d5cdf13e3cf2ece3d3b74b69c9fdc "<title>"`, which reads `BODY.md`
  off the body ref, writes the delivery row and fixes `## Head`. The body's
  `## Head` currently names `f9809c06a…`; `handoff_push.sh` rewrites it.
- If the older one: it needs `git merge origin/main` (never a re-cut), a
  re-record of both budget rows against today's main, and `fixer.md` steps 2–8
  re-executed on the merged tree, because its evidence describes a tree that no
  longer exists. Its body already predicts the `budget-raise-gate` red.
- CI owes the mutation pins: 6 of the 7 sites this diff adds are killable and
  `mutation-autofix` pins them from its own measurement (`ci-autofix.md` — wait
  for the bot commit). The seventh is the triaged equivalent.
- Heavy scripts left to CI under the owner's 2026-10-07 ruling, all named in
  this diff's `scope.run`: `stress.py`, `optimality.py`, `golden.py`,
  `backtest.py`, `arch_score.py`. The gate lease was never held by hand.

## Local state, for a follow-up seat

- Worktree `/Users/timmalmstrom/hpo-seats/ux10/repo`, branch `fix/r9-ux-10` at
  `ff2c85753`, clean. It is a worktree of the shared repo at
  `/private/tmp/r9-main`; nothing was committed or checked out there (its own
  detached HEAD was restored to `83f7ca558` after this seat read a file from it).
- `/Users/timmalmstrom/hpo-seats/ux10/proto` is a scratch prototype worktree
  used to iterate while a long `features.py` run held the seat tree. **Remove
  it**: `git -C /Users/timmalmstrom/hpo-seats/ux10/repo worktree remove --force
  /Users/timmalmstrom/hpo-seats/ux10/proto`.
- Evidence: `/Users/timmalmstrom/hpo-seats/ux10/evidence/probe7/` (the 13-tree
  probe, `<variant>.block.txt`), `structure-base.txt` and `structure-head.txt`
  (the ratchet at both ends), logs under `/Users/timmalmstrom/hpo-seats/ux10/logs/`.
- The scratch scripts that built the branch are under
  `/Users/timmalmstrom/hpo-seats/ux10/ux10/` (`apply_patch.py`,
  `apply_data_patch.py`, `build_features.py`, `block.py`). They are one-off
  drivers, not instruments; the instrument the body's figures need is in the
  tree (`dev/audit/harnesses/ux10_flow_into_model.py`).
