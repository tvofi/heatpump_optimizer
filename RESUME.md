# Power-clamp seat (live-fix wave, PRs 7a and 7b): resume

Binding design note: `/Users/timmalmstrom/hpo-seats/live-arch/DESIGN.md`.
Decision record: #201 comment 6067353918, under mandate 6067089637.
Rule for this seat: **synthetic numbers only.** Never quote the real install's
nameplate or metered draw range in code, tests, harnesses, bodies, commits or
reports. The synthetic overstated-nameplate shape used everywhere is
configured 1-10 kW, asked U(3, 10), drawing U(1.2, 1.8).

## 7a: #2065, handed off for round 4

- PR: https://github.com/tvofi/heatpump_optimizer/pull/2065, branch
  `fix/live-power-clamp-foundation-pr`. Remote head `a456c5ed` (`ci: pin killed
  mutants`, the lane's own `AUTOFIX: changed`). The frozen handoff head is
  `90b9e87f7dece277cfbf46cbc64b2b3f816d841c` on `handoff/r9-live-power-clamp-foundation`,
  body on the orphan `handoff-body/r9-live-power-clamp-foundation` (with this note
  as `RESUME.md`). Do not push the PR branch: the orchestrator moves a frozen head.
- Round 3 blocked because 15 `draw_range.py` sites had no disposition, not because
  the fix was wrong ("The fix itself is sound and this is round 3"). Round 4 is a
  re-cut body (`fixer.md`: past three rounds, re-cut rather than repair), plus:
  - `acba8517d` -- twelve new checks in `tests/features.py`'s 7a block (107 lines,
    with a `_dr_at(pairs)` helper that feeds an exact population). The block is
    now 51 checks; `ALL 51 DR BLOCK PASSED`; the file prints `1 of 3911 FEATURE
    CHECKS FAILED` (the disclosed Accelerate arm, the only failure).
  - `279212233` -- 14 `killed_by` rows under
    `tests/mutation_ledger/killed_by/draw_range.py/` (84 lines;
    `tests/mutation_budgets.json` untouched). 15 sites, 14 anchors: the two
    comparison bounds on line 116 share an anchor and both were driven.
  - `90b9e87f7` -- merge of the lane's `a456c5ed`, whose two rows (`:175` killed by
    `tests/features.py`, `:262` killed by `tests/structure.py`) replaced this
    seat's rows for the same anchors (add/add resolved in the lane's favour).
- **Measured facts a later round must not re-derive from the body's prose:**
  - 13 of the 15 sites survived the branch's original 39 checks, because those
    checks read the threshold *through* the constant (`n=_dr.MIN_SAMPLES`,
    `range(_dr.WINDOW)`, `_dr.RUNNING_FLOOR_KW`) and so adapted to the mutant.
    A check that wants to kill a constant has to count in literals. CI's own shards
    agree independently: they drove `:48`, `:51`, `:102` and printed `lives` for
    all three.
  - The pin lane at `6f420a1f7` pinned 2 of 15, proved 3 survivors, and started
    nothing else: shards 1 and 3 spent 2 h 14 min and printed `MUTATION TABLE
    REFUSED -- nothing was measured: 0 mutant(s) timed out, 5 not started for
    --budget-minutes` / `measure: skip-measure-failed, 0 anchor(s)`, while
    `mutation-autofix` still answered `changed` and stood green. Waiting for a bot
    commit was never going to dispose of 13 sites.
  - `--pin-killed` cannot drive on this host: run for one anchor with
    `tests/features.py` as its only driver it spent 730 s on the baseline and
    printed `MUTATION TABLE INCONCLUSIVE -- the baseline is already red in
    tests/features.py, so no mutant's verdict means anything` (`baseline_refusal`).
    The kills were therefore measured per site with that tool's own rule
    (`killed()`: red AND failing above a green baseline) on the block, and the rows
    were written through `normalize` + `write_budgets` -- the two calls
    `apply_pins` uses -- so the layout is the lane's. Both kill forms were re-taken
    on the whole file: FAIL-line arm `2 of 3911` against the baseline's `1`,
    crash arm counted `2` by `failing_count`'s traceback term.
  - At `90b9e87f7`: `unpinned_sites` 4622 (base 4624 at `c518447eb804`), 0 in
    `draw_range.py`; `completeness_problems` 0; `ledger_form_problems` 0;
    `tools/pr/ci_predict.py --base c518447eb804` prints no `ADDED UNPINNED`;
    `--pin-killed` answers `PIN KILLED: nothing to pin` (rc=0); structure PASSED,
    layout 0 refusals, archscore `dS +0.0000 NULL`, `MODE: SCOPED -- 28 script(s)
    run, 5 scoped out`, both claim files byte-identical to main's.
  - `bash tools/pr/prepr.sh <body>` passes rc=0 at this head, with only the
    push-order WARN (the head is ahead of the PR branch, which is the handoff).

## #2066 is stacked on #2065

#2066 (cop-floor) contains `1e957282e` and must merge after #2065. Its
`MeasuredCop.judge_ratio` reads `draw_range.follows_ask`, which #2066 adds on top
of 7a's samples. That function relies on `from_dict` dropping samples that have
no configuration, which round 2 delivered.

## 7b: the clamp. Open it only after #2065 merges.

Start from fresh `origin/main`, after #2065 has merged, in a new worktree.
Build per DESIGN.md section 5 row 7 and section 6 "7 vs duty_floor_kw":

1. **Floor.** The solve copy's `min_electrical_power` is `planned_range(...)[0]`.
   It rides the existing `**self._model_corrections(now)` spread in `_solve_hubs`,
   or an equivalent single spread. The live parameters keep the configured value.
   On a duty-cycling install the min end stays configured; S4 already does this,
   and 7a's `S4 on a duty-cycling install that runs below its configured min`
   pins the further rule that the min end is never booked above its own max.
2. **Ceiling.** `planned_range(...)[1]` composes into `power_caps_extra` on the
   existing `env_caps` line in `_solve_record`, using `np.minimum`. Never edit
   `max_electrical_power`: it is also the emitters' design power.
3. **`on_threshold_kw`.** `thermal_model.on_threshold_kw` reads the live
   parameters, so it must key on S4's effective range. Otherwise a metered floor
   below half the configured one reads a running pump as standby.
4. **carry-2065 precondition, from #2066.** The duty floor both readers take must
   be capped by the observed running draw's low end, and never fall below
   `on_threshold_kw`. That floor is `ThermalParameters.flow_lift_power_floor_kw`,
   read by `_fold_measured_cop` and `_fold_flow_lift` and reported as
   `cop_learner.power_floor_kw`.
   - The control is `dev/audit/harnesses/cop_duty_floor.py`, row
     `min3_running_folded`: an overstated 3.0 kW modulation floor while the pump
     runs below it. Run it at the merge base and at the head with
     `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`.
   - Done when `min3_running_folded` reads 15/15, or the body names why the lowest
     draws stay refused. Every `min3_idle`, `min3_standby` and `min3_duty_cycled`
     row must stay 0; `min1_running_folded` must stay 15/15.
   - The carry file is `dev/programme/carries/carry-2065.json`. Where it and
     DESIGN.md disagree, the newer one wins.
5. Every module function takes values or a view, never the coordinator. Pay for
   in-class lines inside the PR. Propose any budget raise to the orchestrator first.

### Local prototype: branch `wip/live-power-clamp-full`

In the seat worktree's repository. The pre-design-note prototype: module-level
coordinator helpers `_planned_draw_range`, `_draw_floor`, `_with_draw_cap`, a
solve-record test block and `scratch/probe.py`. **It still uses the old shapes;
replace them with the synthetic shape above before reusing any of it.** Reuse it
for the proof shape only: `_solve_record` gets the floor and the cap; the planner
books no level above the metered max; on a switch-plus-setpoint install no on
level falls below the metered min; the null pump plans byte-identically. The
structure there is superseded by DESIGN.md, so rebuild the helpers as
value-taking S4 consumers.

Proof 7b owes: a failing test first; mutants of the two call sites and the
`on_threshold_kw` keying; null controls (a pump that draws what it is asked, the
mild 6 kW part-load pump, and a frequency-write install, all planning
byte-identically); the carry-2065 harness rows above at both ends.

## Seat traps learned

- `python3` on this host is 3.11 and dies on this tree's nested f-strings. Under
  `bash tools/pr/prepr.sh` that surfaces as a bogus `no-copies` refusal
  ("SyntaxError: f-string: expecting '}' (0 in all)"). Run prepr with
  `PATH="$HOME/.local/state/hpo/venv-ci/bin:$PATH"` first.
- prepr's `ancestry reds` step refuses a `## Red checks` that does not name every
  check red anywhere in the branch's range -- `fast (3.14)`, `nightly-ha (stable)`
  and `nightly-status` included -- even when they are green at the head being
  handed off. A re-cut body deletes round history; it does not delete answers.
- `tmp_paths.py --check` scans the ledger lines a branch adds since the merge base
  for temp, home and seat paths. A pin reason must cite its instrument by what it
  printed, not by where it lives. PR bodies are not scanned.
- The claim `--pin-killed` is the route for a red `mutation-autofix` assumes a host
  where every driver's baseline is green. On the seat's Darwin it is not
  (`baseline_refusal`), so the rows are hand-measured -- say that in the reason
  rather than implying the tool wrote them.
- `prepr`'s push-order step refuses when `mutation-autofix` has pushed. Fast-forward
  the PR worktree to the remote before any `app_push`.
- A body-only push must answer every red standing at the current head, nightly
  lanes included.
- A harness belongs under `dev/audit/harnesses/`, never `tools/audit/harnesses/`
  (`tests/layout.py`). List it in `harness_headers.py`'s inert reads in
  `tests/closures.json`.
- A new module changes the D6 claims headers (`dev/audit/rounds/round4/D6/claims.py`),
  the architecture module counts, and `tests/deployment_shape.py`'s selection-cost
  note.
- Re-run the ledger check after editing any line `mutation-autofix` has pinned.
  That is round 2's lesson.
