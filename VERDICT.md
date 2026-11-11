Fix review: blocked 5289e1fee495ba8d7e81a5c1e5c8c328aca77d7f mutation-vacuous: rv_book_no_latch, rv_pass_decay_dropped, rv_detach_keeps_episode, rv_persist_stays_dirty, rv_published_undecayed, rv_ctx_supply, rv_ctx_plan_control, rv_ctx_disinfecting, rv_ctx_boost, rv_ctx_electric, rv_ctx_fault, rv_ctx_loop, rv_ctx_last_write, rv_gate_demand_true, rv_gate_plan_any, rv_gate_source_leg, rv_gate_setpoint, rv_gate_inlet, rv_lit_ignores_freshness

bus-nonce: f4a692c8fe66500a7452e5a92d2e9ad0

Round 1 (first review) of the handoff r10-duty-switch-restart-learning, group R10-DUTY-SWITCH-RESTART-LEARNING part A. Measured from a detached worktree at 5289e1fee495ba8d7e81a5c1e5c8c328aca77d7f against origin/main cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf, which is the head's merge base (the head already holds main). `git ls-remote origin refs/heads/handoff/r10-duty-switch-restart-learning` still printed 5289e1fee495ba8d7e81a5c1e5c8c328aca77d7f when this was written. No pull request exists, so there is no review packet and no CI run to read: every figure below is this seat's own run, and the role contract was read from the rendered role pack (`git diff <merge-base>...origin/main -- dev/governance/roles/` is empty).

## Block

Two blocks; the first line carries the first.

1. mutation-vacuous. The body's 58 mutants are all killed at this head (re-run, `ev/mutants_body_spec.txt`), but they sit almost entirely in the pure learner. The design names "the count conditions, each void rule" as mutation targets, and in production those rules are live only through the arbiter's glue, which the section does not pin. The reviewer's 31 further single-replacement mutants (`ev/reviewer_mutant_spec.json`, same driver, same command as the body's) leave 19 alive (`ev/mutants_reviewer_spec.txt`):
   - `_switch_context` (pump_arbiter.py), a void input replaced by its neutral constant: rv_ctx_supply, rv_ctx_plan_control, rv_ctx_disinfecting, rv_ctx_boost, rv_ctx_electric, rv_ctx_fault, rv_ctx_loop. Only the defrost input is pinned (the body's context_defrost). With any of these seven the matching void rule never fires on an install, and every section check passes.
   - `_switch_context`, rv_ctx_last_write: the latest-write stamp set to None; the censoring of an off time by a later arbiter write is then dead through the arbiter.
   - `_report_write` (pump_arbiter.py), the count gates' inputs: rv_gate_demand_true (demand always true), rv_gate_plan_any (all to any over the stop window), rv_gate_source_leg (the replaced record's age replaced by 1e9), rv_gate_setpoint (the command's space set-point replaced by 0.0), rv_gate_inlet (the inlet replaced by None). The body's departures "source-leg age is the replaced mode record's" and "the space set-point is the command's" are therefore unpinned: reverting either changes no check.
   - `_lit`, rv_lit_ignores_freshness: a stale flag reading counts as lit.
   - duty_switch.py: rv_pass_decay_dropped (the pass no longer ages the latches, so a usable direction never switches off between episodes: design point 8's relearn path through `note_pass`), rv_published_undecayed (the published k and n ignore age), rv_detach_keeps_episode (detach leaves the open episode), rv_persist_stays_dirty (a successful save leaves the record dirty, so the store is written on every one-minute pass), rv_book_no_latch (the latch not re-evaluated at a booking; on an install the next pass re-evaluates it, so this one is the weakest of the nineteen).
   None is an equivalent mutant: each changes what an install records, publishes or writes to disk. The body's `## Red checks` answer for `tests / mutation` says `mutation-autofix` pins the listed sites; it pins killed sites only, and several listed sites (pump_arbiter.py:1415 to :1429 among them) hold these survivors, which `ci-autofix.md` leaves to triage by hand. Owed: checks driven through the arbiter for each void input, each count gate input, the write censor, the pass's latch aging, the published decay, the detach and the save-once behaviour.

2. carry-missing: not carried to R10-DUTY-SWITCH-RESTART-LEARNING-PR-B and R10-DUTY-SWITCH-PLANNER-PRICE. The body's first `## Forward-carry` item (parts B and C get no ready read API and must add a reader with its first caller; n has no ceiling; the loop void is wider than the design's) names `docs/design/2026-11-10-duty-switch-restart-learning/design.md` as where it lands. That file at the head is byte-identical to the approved note (blob fe5c7235475a in both, `ev/forward_carry.txt`) and holds none of it; it still reads "Read API for B and C, unused in A: per direction, usable (bool), stop probability, median off seconds" and "Version 1: per direction k, n", both false at this head, while `duty_switch.py`'s docstring cites it as the design. Parts B and C are live roster groups on `handoff/audit-r10-roster` e0458e6fd809cb73d4cc1f165d7d6917e2ccacf2, and neither brief nor carry of either names the missing reader, the wider void or the stored encoding (`ev/roster_carry.txt`). Owed: the carry in those two groups' briefs with its control (the `dead_top_level_symbols` refusal, and the mutant `publish_only_observed` for the conditional keys B or C would read), and the in-tree note either amended with the build's departures or no longer cited as what was built.

## Departures from the approved design: rulings

Eight of the nine are ruled in the list; the ninth, the store kept through a factory reset, is the first item under Findings: accepted for part A, where nothing reads the estimate, and the owner's to rule before a later part does.

- Store encoding, k and the kept weight: accept. `ev/load_probe.txt`: the round trip is equal, and every in-bounds pair is a valid record.
- Stored tallies stopped and kept: accept; the design publishes them.
- Read API not built: accept in the code; block 2 covers what it owes the later parts.
- Origin not in the context: accept; nothing in A reads it.
- Loop void on any moved target: accept as costing evidence only; its arbiter input is unpinned (rv_ctx_loop, block 1).
- Source-leg age from the replaced mode record: accept the reasoning; unpinned (rv_gate_source_leg, block 1).
- Space set-point from the command: accept the reasoning; unpinned (rv_gate_setpoint, block 1).
- Conditional publication: accept. The premise is confirmed in the direction that matters: `env_drift.py --all` reports no unclaimed drift and no stale fixture at this head, and the body's mutant publish_only_observed is killed. The body's "fourteen keys read as five stale fixtures" without the condition was not re-derived.

## Findings

- Factory reset keeps the duty-switch store (`_FR_STORES`, "kept: observed facts"), while every other learned estimate is voided there (thermal_learning, accuracy, price_model, dhw_profile, dhw_draws; `coordinator.py` `_FACTORY_VOID`). The store holds an estimate with a latch, the kind the reset voids, and the registry would also need its in-memory learner emptied. The body routes it to the owner; it must be ruled before any part reads the estimate. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- No finder harness exists for this group (the design note says so: outside report, owner-routed). `dev/audit/harnesses/r10_duty_switch_section.py` is the fixer's instrument, lands in the tree, and was the only harness available to this review; the design's seven evidence items each map to a section check. Carry: dismissed: outside report with no finder seat, the design note records it and the fixer's harness lands in this diff
- `tests/features.py` at the head fails one check of 5266, the `combi_type_branch` census, on six lines none of which is in this diff's hunks (`ev/cross_checks.txt`). The body's third forward-carry is on the roster in R10-COMBI-TANK-PR-B's carry at e0458e6fd8 (`ev/roster_carry.txt`); the body names `tests/features.py` as where it lands, which is not a brief. Carry: R10-COMBI-TANK-PR-B

## Evidence

- RESULT section_checks_head: 29 passed, rc 0 (`ev/section_head.txt`). No baseline run: the section's first import does not exist at the merge base.
- RESULT body_spec_mutants: 58 KILLED, NULL survived, rc 0 (`ev/mutants_body_spec.txt`).
- RESULT reviewer_mutants: 12 KILLED, 19 SURVIVED of 31, NULL survived (`ev/mutants_reviewer_spec.txt`).
- RESULT load_probe: 36 malformed or out-of-bounds payloads all load an empty learner; an extra top-level key loads whole; decay leaves p unchanged; one episode after switch-off does not switch on; a clock stepping back grows no count (`ev/load_probe.txt`; the probe is the reviewer's).
- RESULT structure: STRUCTURE RATCHET PASSED, rc 0; `tests/structure_budgets.json` untouched (`ev/structure_head.txt`).
- RESULT archscore: dS -0.0081, coord_footprint 2496 to 2510, the only metric that rises (`ev/archscore.txt`). The body explains it under `## Architecture score` in one line naming the metric, which is what `tools/audit/archscore/gate.py` asks. No budget is raised. A cheaper registry was looked for and not found: the rise is the statements of the three functions that take the coordinator plus one call line at each of four arbiter sites, and the per-coordinator side table is the shape fixer step 17 names.
- RESULT golden_drift: NO UNCLAIMED DRIFT, NO STALE FIXTURE, 56 scenarios, rc 0, against the merge base (`ev/env_drift_all.txt`); nothing under `tests/golden/` is in the diff, neither claim file is touched.
- RESULT gate_mode: MODE: SCOPED, 23 scripts run, 10 scoped out (`ev/closure_select.txt`). The scoped gate itself was not re-run.
- RESULT class_enumeration: the body's rule prints pump_arbiter.py:1336, :1561, :1733 and the comment at pump_mode.py:85 (`ev/class_enum.txt`): one mode write, in `_write`, reported there; no seam outside the diff.
- RESULT versions: `VERSION`, the manifest and `RELEASE_NOTES.md` are not in the diff.
- RESULT merge: the head's merge base is origin/main's tip; `git merge-tree --write-tree origin/main 5289e1fee495ba8d7e81a5c1e5c8c328aca77d7f` exits 0.
- RESULT mutation_ledger: one pin removed, the starts sensor's RETURN_DEL, whose line the diff rewrites; the body's mutant publish kills the new line.
- The arbiter's reader was read, not only run: an absent, unavailable, unknown or non-numeric frequency state resolves to None, and the meter path returns None for the same states, so no signal is never "stopped" (design item n1).
- Red checks: no run exists. `merge_train.py owed-reds` lists `tests / mutation` (`ev/owed_reds.txt`); the body's predicted answer is judged in block 1, not blocked on as a red.
- Outside pull request 3420 now heads at 2599cc38edffa760722e1c063da7d949f11ca963, four commits past the e05c6b1ccc this branch was built from (`ev/pr3420.txt`); the roster note at e0458e6fd8 already records that rewrite and the decision not to restart on it. The branch's first ten commits keep the contributor as author and no message in the range carries a session or co-author trailer.
- Not re-derived: the body's count of closures re-recorded, its "22 closures" friction figure, the control run of `tests/features.py` on an archive of main, and the pre-merge scoped gate's two reds.
