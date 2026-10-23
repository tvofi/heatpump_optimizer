Fix review: blocked a9e26e070f9fffcb9015cebb402c0ee4b95e2537 carry-missing: not carried to #2674 (no dev/programme/carries/carry-2674.json; carry_audit BAD-DEST, pr-contract red)

bus-nonce: 2883e993a9d2b4a599feb3f265bcad32

Round 1. Group R10-LIVESTATE (round 10, XL). Measured head `a9e26e070f9fffcb9015cebb402c0ee4b95e2537` from a detached worktree; merge base `6120fb5138dccca84a5f5ca1e8bd3ef8487a1efa` (= origin/main tip at review). Head re-read before posting: unchanged (PR state CLOSED for the CI cut-over window; head not moved). `fix-review.md` current: `git diff <merge-base>...origin/main -- dev/governance/roles/` empty.

## The block

`## Forward-carry` routes item ls-r2 (seven unprobed per-cycle store-load leads) with `Carry: #2674`. #2674 exists (OPEN) but has no owner: no live roster group lists it and `dev/programme/carries/carry-2674.json` is absent at the head and at origin/main. `finding-propagation.md`: a stage with no live roster group gets its own carry file, "and creating it is part of the finding"; "Name a destination that exists." Instrument: `python3 -I tools/audit/carry_audit.py check --body <body>` at the head prints `BAD-DEST body item 7d5ed33c: #2674: #2674 has no owner ...`, `CARRY-AUDIT: 2 finding item(s): 1 routed, 0 unrouted, 1 bad destination(s)`, rc 1 (`evidence/carry_audit.out`). CI agrees: both `pr-contract` runs at this head (runs 40040274724, 40040275435) fail on the same step with the same line. Repair: add `dev/programme/carries/carry-2674.json` (fields per `brief_lint.mjs`) carrying ls-r1's probe recipe and its null as the precondition, or route ls-r2 to a live group; re-run carry_audit.

Everything else measured below holds; on a repair confined to the carry file (no production or test change) these numbers carry.

## RESULT lines (mine; finder harnesses where they run, ports checked against them)

- m4 (finder, `dev/audit/rounds/round10/D1/s1/m4_mode_midsolve.py`, unmodified, reads the cwd tree): base `torn_midsolve_total=2` of 2, `torn_null_total=0`; head `torn_midsolve_total=0` of 2, null 0.
- l3 (finder, `dev/audit/rounds/round10/catchup/leads/l3_restore_race.py`): base `main differ_total=3 of 3`, `perturbed differ_total=0 of 3`; head: `TypeError: 'AwayState' object is not callable` (drives the replaced `restore_session` signature, as the design's drev-01 predicted).
- probe_away_restore (finder, base copy run from the base tree; it resolves its root from `__file__`): base `lost_midload=1`, `lost_null=0`; `--perturb` `lost_midload=0`. Head: `TypeError: cannot create weak reference to 'types.SimpleNamespace'` (its stub coordinator meets the new weak-keyed gate).
- Port `dev/audit/harnesses/r10_livestate_restore_race.py` (fixer's port, disclosed as such in the body): base `l3_differ_total=3 of 3`, `l3_null_differ_total=0`, `probe_lost_midload=1`, `probe_lost_null=0`, `gated=0` -- equal to both finder originals at base; head `0 of 3`, null 0, probe 0, null 0, `gated=1`. Read the port: same three scenarios and the probe's stored payload; at head it spawns through `boost.spawn_restore_session`, the production path.
- Manual-plan: design-review probe `design-verdict/r10-livestate` 5af5526b5 `evidence/probe_manual_restore.py` at base `lost_midload=1 lost_null=0`; at head it raises (its stub store lacks `async_wait_for_read`, as the design said it would need porting). Port `r10_livestate_manual_plan_load.py`: base clear 1 / apply 1, nulls 0; head 0 / 0, nulls 0. The port's stub `async_wait_for_read` mirrors `store.py:784` (shielded future set by the load).
- Held context reads after await, the design's own inline AST pass (`evidence/fr-2675-ast.py`, extracted from the design note, not the fixer's port): base `held-ctx-reads-after-await=9`; head 0; planted read (`ctx._current_state.room_temperature` after `_async_learn_house_heat_loss`) 1. The fixer's port agrees: base 9, head 0.
- event_hub_inplace_writes, the finder's file from `fabaf4664` byte-for-byte (port diff: header and Command line only): base 3 (`coordinator.py:3514`, `:3517`, `:8611`); head 0; planted `ctx._current_state.peak_guard_active = True` after `_on_power_event`'s publish: 1.
- shared_config_seams (finder): base `seams_total=80` (A 3, B 41, C 17, D 19); head 43 (A 3, B 16, C 3, D 21), as the design's spike and drev-04.
- R10-LIVESTATE block of `tests/features.py`, run alone with an extractor I built (`evidence/fr-2675-extract.py`, my own instrument): head `ALL 11 FEATURE CHECKS PASSED`; against base production code D1-s1-02, the rerun check and P2 fail, then the block raises at the M11 check (`_fixed_mode_action` absent at base).

## Mutation proof (my mutants, head, block alone)

M1 supersede `if False:` -> 2 fail; M2 rerun guard `if True:` -> 1 (rerun check); publish in place -> 1 (P4); I1 post-await copy from the pre-await local -> 1 (I1/I3); `session_restored` gate skipped -> 1 (L3); drev-02 `task is None` gate never set -> 1; clear's `async_wait_for_read` removed -> 1; apply's removed -> 1; cursor not advanced -> 1 (P6). `_resolve_away` `if True:` survives the block but fails the carried D14-s1-01 control (`tests/features.py` "a switch written during its await is not reverted", extracted alone: 1 of 1 FAIL), the drev-05 null against the identity form; `if False:` is the ledger's GUARD_OFF pin (killed by the whole script, per the pin). `==` for `is` survives both: equal-content replacement resolves to the same value, an equivalent mutant here.

Ledger: 17 added/renamed files under `tests/mutation_ledger/killed_by/` = 13 new sites + 2 re-keyed (`_async_update_data`, `_resolve_away`) + 2 `utc_shift` moves; every entry's `old` line is present at the head. The `mutation` CI lane was still running at review; not re-run (`fix-review.md` 11).

## Late fixes

- Typing (item 13): `_async_handle_ecl110_state_message` and `_on_power_event` bind `ctx = _ctx_of(self)`; both callbacks are synchronous, so the bound ctx is not held across an await. CI `typing` at this head: success.
- `tests/boost_drift_replay.py` (item 14): `ctx` is now read only after `_update_current_state` and used at two later reads; no read precedes it. Base and head run under a gate slot: both `ALL 46 BOOST DRIFT CHECKS PASSED`; the 12 `hh_scale` figures identical and the whole output identical (`diff` empty; `evidence/bdr_base.txt`, `evidence/bdr_head.txt`). The test change masks no production regression.

## Other checks

- Structure: `tests/structure_budgets.json` six rows, all lowered (class_excess_loc, coordinator_attrs, coordinator_multiassigned_attrs, max_cc, max_class_loc, seam_cut_total); `python3 tests/structure.py` at head `STRUCTURE RATCHET PASSED`. `tests/ci_budgets.json` hub_solve_writes and shared_inplace_writes lowered; event share earned (event harness 3 -> 0, planted 1); `arch_score_head.py` drops only the rows the fix retired. CI `arch-score` success.
- Roster widening: `handoff/audit-r10-roster` 4e4a5d5c6 R10-LIVESTATE `resume.note` records the six files.
- #2674 cited in the body and exists (the block above is its missing carry file, not the citation).
- VERSION, manifest, RELEASE_NOTES, both claim files untouched in the three-dot diff. `git merge-tree --write-tree origin/main <head>` exit 0.
- Not run by me: `env_drift.py --all` and the scoped gate (CI `fast` in progress at review).

## Non-blocking notes

- The rerun in `finally` is guarded by `_mode_superseded`, where the design said "not guarded" with an `async_set_mode` clear; `async_run_optimization` CC 15 (design 14), `functions_cc_over_15` flat at its cap. This is the drev-06 option that keeps the AUTO -> COMFORT -> AUTO rerun, disclosed in item 2 and tested (M2). Carry: dismissed: drev-06 permitted it, the body discloses it, and the structure cap holds
- m4 at this merge base reads 2 of 2 torn, not the 1 of 2 the body cites from the design table at fd7e289d0; head 0 either way. Carry: dismissed: re-measured here, the conclusion does not change
- `tests/ci_budgets.json` `reason` cites `dev/audit/rounds/round10/D7/arch2-s2/event_hub_writes.py`, absent from the tree (it lives at fabaf4664; the in-tree copy is `dev/audit/harnesses/r10_livestate_event_hub_writes.py`). Carry: dismissed: the reason string is not a linted brief, and the in-tree port is cited in the body
