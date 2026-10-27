Fix review: merge 57b2857ac59ebea3d58b6ce90dcaa1c41345f0cc

bus-nonce: 31c6fdbf86010e910016ad7fcbce1f93

Delta review of #2819 (R10-ARCH-SHAPES), round 6 — the delta after the round-5
`merge` at `e088bf833707542cfa027c1878b086e4e05ddd9e` (comment on `review/2819`).
Measured head: `57b2857ac59ebea3d58b6ce90dcaa1c41345f0cc`, still the PR head at
2026-10-27T04:41Z (re-checked immediately before this verdict). Reviewed from a
detached worktree at that head, never the main checkout. The roles diff
`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`
is empty (merge base `484d9902222031f8e081df9f53b52ffd50fcc0af`).

**The delta is what the dispatch says**: `aec11a772` (guard pins + closure),
`ea33506e0` (the remaining re-keyed sites), `632715d74` (the #1218 note), plus
merges of main and bot merges. `git diff --name-only aec11a772^..632715d74 --
custom_components/` prints nothing, so **no production file moved** in the
authored commits.

## Findings

- **Low, notation — one explanatory range in `## Null control` is short at its
  upper bound under the extent reading.** The body says "every hunk of that file
  sits at lines 3681–4311, 25004–25107 and 37940–38059" for `tests/entities.py`.
  Re-derived at this head (`git diff -U0 484d99022...57b2857ac -- tests/entities.py`),
  the new-side hunk **start** lines are `3681 3958 3968 4031 4153 4296 4311 |
  25004 25022 25084 25101 25107 | 37940 38014 38037 38045 38059`, whose min and
  max per cluster are **exactly** the body's three pairs (`evidence/entities_u0.diff`).
  So the figures are reproducible under "each hunk begins within these lines",
  and are not stale. Under the other reading — the region the hunks occupy — the
  last cluster-1 hunk (`+4311,24`) runs to `4334` and the last cluster-2 hunk
  (`+25107,2`) to `25108`, so the stated ends are short by 23 and 1 lines. The
  hunk starts are identical at the code head `8aaac4925`, and main changed no
  line of the file in `6fe5170cd..484d99022`. The **conclusion the range
  supports holds exactly**:
  `git diff 484d99022...57b2857ac -- tests/entities.py | grep -cE '^[+-].*(hb:|py-spy|positive_control|HB_CONTROL)'`
  reads `0`, so the failing hb checks at ~18.2 k are untouched by this diff. No
  check reads the range and no later stage acts on it.
  Carry: dismissed: the quoted endpoints are the exact min/max of the `-U0` hunk
  starts (reproducible, not stale), and the only gap is two hunk-extent tails in
  an explanatory range whose conclusion (the hb lane is untouched, grep=0) is
  independently verified at this head; no body edit changes a decision.

## Non-blocking note (instrument)

- `tools/audit/carry_audit.py pr 2819` exits 1 (`evidence/carry_audit_pr_mode.txt`) on
  one item: the round-earlier `blocked` verdict comment 6400399252, its
  `## Evidence` bullet reading "…and the residual set is the base's, not this
  diff's" (`evidence/review_6400399252.md` line 39). `items()`'s verdict branch sets
  `why="evidence"` for any item under an `## Evidence` heading on which
  `DEFERRED` or `NONBLOCK` matches (`carry_audit.py:202`, `:108-111`), and
  the matched word is `residual` used in its statistical sense — a measurement
  of the base's failing set, not outstanding work. The offending text lives in
  an immutable earlier review comment, so no body edit can clear it; the check
  `pr-contract` actually runs, `carry_audit.py check --body` (body only), passes:
  2 routed, 0 unrouted, 0 bad destinations (`evidence/carry_audit_bodyonly.txt`). The
  PR's red-check answer for `pr-contract` names this command and its body-side
  form passes at this head. Pre-existing, not this delta's and not a blocker.
  Carry: dismissed: instrument reads a statistical "residual" in an earlier
  verdict's Evidence bullet as outstanding work; the text is in an immutable
  comment, the body-only form `pr-contract` runs passes, and no destination
  needs this PR to fix it.

## The delta's own claim, verified

Every number below I measured at `57b2857ac` this session; the commands and
their output are under `evidence/`.

- **The pins are real and each is the killer.** `tests/guard_pins.py` at the head:
  `ALL 61 GUARD PIN CHECKS PASSED`. My own driver (`evidence/pin_kill_names.py`, mine,
  disclosed) applies each of the 12 recorded mutants from
  `tests/mutation_ledger/killed_by/` and prints the FAIL line: every one fails
  with its **own** `R10-ARCH-SHAPES` pin named, not some other check
  (`evidence/pin_kill_names.out`). 12/12 killed; the `quiet_windows._within_nameplate`
  anchor's two sites both killed (lo and hi bounds). A comment-only edit leaves
  `rc=0` (`evidence/pin_kill_check.out`).
- **The pins name sites the table reports.** `python3 tests/mutation_table.py
  --scope changed --base 484d99022 --max 0`: `3839 unpinned site(s) of 6390
  candidate sites, 3904 at the ratchet base ...; the ledger agrees with the
  deterministic inventory`, `no mutant is both generatable and drivable`,
  `MUTATION TABLE PASSED (empty pool)`, no `ADDED UNPINNED`
  (`evidence/mutation_ratchet_head_vs_base.txt`). `ci_predict.py --base origin/main`
  and `--base 484d99022` both print no added unpinned site.
- **The two survivors are honestly triaged.** `_async_drive_pumps` CMP_BOUND is
  `gap`: the head line reads `abs(finite_float(...)) > 0.01`, the base reads
  `abs(_as_float(...)) > 0.01` — re-keyed, unpinned on main, a real gap
  disclosed. `state_power_kw` GUARD_OFF is `equivalent`: with the guard off,
  `finite_float(getattr(None, "state", None))` is None and the next
  `if value is None: return None` answers identically (`ev` inspections).
- **The ledger rows count as the body says.** The three-dot diff adds exactly
  `14` `killed_by` rows whose `killed_by` is `tests/guard_pins.py` and `2`
  `survivor_triage` rows.
- **The #1218 note is derived, not gamed.** My own re-derivation of
  `entities.py`'s `_d308_pairs` (`evidence/d308_pairs_reviewer.py`, mine, disclosed):
  head `131 of 528` pairs at >=0.80, `406` comparable, `100` production files,
  `9` pairs involving `tests/guard_pins.py`; base `484d99022` `122`, `0`
  guard_pins pairs (`evidence/d308_head.txt`, `evidence/d308_base.txt`). The nine are
  block_duty, boost_drift_replay, card.mjs, card_drift.mjs, debug_collect,
  manual_plan, plan_view, solar_alignment, wood_advisor. The closure grew
  because the pins import `coordinator.py` and `sensor.py`
  (`guard_pins.py`'s closure now reaches both); removing the pins removes the
  growth, so the movement is earned.
- **The named production mutant still dies.** Baseline `ALL 4459 FEATURE CHECKS
  PASSED`; the branch's `monthly_cost_delta` spelling gives `2 of 4459 FEATURE
  CHECKS FAILED`, the two `#2257` checks the body names, and nothing else
  (`evidence/price_tiles_mutant.out`, `evidence/price_tiles_mutant_fails.txt`). The restored
  tree is clean.
- **Structure and architecture.** `tests/structure.py`:
  `STRUCTURE RATCHET PASSED`; 18 metrics (the budget file's keys less
  `recorded_at`); `class_excess_loc 18067`, `duplication_copies 15`,
  `functions_cc_over_15 28`, `max_class_loc 8222`, `methods_over_150 16`,
  `seam_cut_total 424` (`evidence/structure_head.txt`). Every moved budget is down, no
  raise (`evidence/structure_budgets_diff.txt`). `score.py --diff 484d99022`:
  `Architecture score: dS +1.8326 IMPROVES` with the five components the body
  lists (`evidence/archscore_head_vs_base.txt`).
- **Claims, version, notes.** Both claim files and `VERSION`, the manifest and
  the `RELEASE_NOTES.md` heading are byte-identical to the merge base
  (`evidence/claim_version_notes.txt`); `git diff origin/main...HEAD -- tests/golden/`
  prints 0 lines. I did not run `env_drift.py` (host-conditional); CI's
  `tests / fast (3.14)` is green at the head.
- **Head and merge shape.** `57b2857ac` is a pure automatic merge of its parents
  (`git merge-tree --write-tree b39bb6559 484d99022` tree equals the head tree),
  so no hand resolution lurks. `git merge-tree --write-tree origin/main HEAD`
  exits 0 (`evidence/merge_tree_main_head.txt`).
- **Carries.** Both `## Forward-carry` items route to `R10-ARCH-SHAPES-CLASSIFIER`,
  which is live at `dev/programme/rosters/wave-r10-groups.json` with
  `resume.stage: queued` (not done) and whose parked commit
  `996b54cf15ea3c7693383165ae2f080d2e04971b` is the tip of
  `park/r10-arch-shapes-classifier`. `carry_audit.py check --body` exits 0
  (`evidence/carry_audit_bodyonly.txt`).
- **The Unpinned sites list is an accurate historical snapshot.** Its line
  numbers match `04669d82f` exactly (accuracy:124, const:1335, coordinator:417
  and :4065, dhw_schedule:151 and :458, inputs:391, optimizer:1358,
  quiet_windows:343, sensor:1381, wood_fuel:136 and :157), which is what the
  body says it is ("before the previous pass's pins"). `coordinator.py:4065`
  is `4077` at the head, as expected after the merge of main.
- **The fix predicates were not re-spelled by main.** `git diff
  1f82fee49 6fe5170cd -- coordinator.py` has no hunk on `_plan_slots`,
  `_freq_fold_blocked`, `channel_heating_steps` or `freeze_reason`, and main
  changed none of `inputs.py`, `quiet_windows.py`, `const.py`,
  `dhw_schedule.py`, `optimizer.py`, `accuracy.py`, `wood_fuel.py`; main's
  `6fe5170cd..484d99022` window touched no production file at all. The earlier
  rounds' proof lines are byte-identical at this head.

## Red checks

Read from the head's check-runs API (`evidence/check_runs_final.json`, one page,
`total_count 55`, every `head_sha` = the measured head): 55 runs over 47 distinct
contexts, each `completed` — 39 `success`, 16 `skipped`, **0 non-green, 0
pending**. The contexts that ran are green, including `gate=success`,
`pr-contract / pr-contract=success`, `tests / mutation=success`,
`prelude=success`, `governance / delivery-status=success`. The body's
`## Red checks` names and
answers each historical red — `gate` (aggregator, no cause of its own),
`pr-contract`, `tests / mutation`, `tests / mutation-autofix`, `tests / fast
(3.14)`, `prelude`, `governance / delivery-status` — each with a cause and a
cheaper detector or a recorded finding that none exists. The trigger is
answered; I do not judge the answers beyond the trigger.

## What I did not do

- Did not run the heavy gate or the full mutation table (cited CI), nor
  `derive_closures.sh` (Linux-only path).
- Built four drivers of my own (`pin_kill_check.py`, `pin_kill_names.py`,
  `d308_pairs_reviewer.py`, `price_tiles_mutant.sh`), named as mine above and in
  `evidence/`; no finder's harness was re-implemented.
