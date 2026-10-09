# Power-clamp seat (live-fix wave, PRs 7a and 7b): resume

Binding design note: `/Users/timmalmstrom/hpo-seats/live-arch/DESIGN.md`.
Decision record: #201 comment 6067353918, under mandate 6067089637.
Rule for this seat: **synthetic numbers only.** Never quote the real install's
nameplate or metered draw range in code, tests, harnesses, bodies, commits or
reports. The synthetic overstated-nameplate shape used everywhere is
configured 1-10 kW, asked U(3, 10), drawing U(1.2, 1.8).

## 7a: #2065, handed off for round 5

- PR: https://github.com/tvofi/heatpump_optimizer/pull/2065, branch
  `fix/live-power-clamp-foundation-pr`. Round 4's `merge` verdict stands at
  `90b9e87f7`; the frozen handoff head is now
  `9b39bb7c68ff6a0cf5914c27c7cb93293400a9f3` on
  `handoff/r9-live-power-clamp-foundation`, body on the orphan
  `handoff-body/r9-live-power-clamp-foundation` (with this note as `RESUME.md`;
  round-5 body at `/Users/timmalmstrom/hpo-seats/live-power-clamp/body/BODY5.md`,
  round-5 evidence under `scratch/r5/`).
  Do not push the PR branch: the orchestrator moves a frozen head.
- Round 5 is one commit: `9b39bb7c6`, the update-branch merge of main
  `d8a4bd36f638` (#2059; #2024's flow meter at `a8ce87571`). The PR was **DIRTY**
  -- three content conflicts -- so no CI ran at all, and no code line of the lane
  moved: 6 files carry a hand resolution (`dev/audit/rounds/round4/D6/claims.py`,
  `tests/deployment_shape.py`, `tests/features.py`, `docs/architecture.md`, and the
  two regenerated register files `claims.json`/`claims.md`). `tests/closures.json`
  was settled by main's own ledger driver at the merge (`LEDGER-MERGE: resolved`,
  22 lists as sets) and `closure.py selftest` is green on it.
- Measured at `9b39bb7c6`, main `d8a4bd36f638` (all of it re-derived, nothing
  carried -- see the trap list below): `arch_modules_on_disk=75`,
  `arch_map_listed=75`, `arch_map_missing=0`, `ha_module_level_importers=27`,
  `config_defaults_compared=89`, `config_ranges_compared=91`,
  `claims_extracted=125 / true=123 / false=0 / stale=0 / unverifiable=2`;
  `architecture.md` = 75 modules, 27 importers, "the other 47"; deployment-shape
  census = 93 production files, 528 pairs, 406 comparable, 123 at >= 0.80, 18 at
  1.00, per-pair 93/83/75/57/21/91/58; `MODE: SCOPED -- 28 script(s) run, 5 scoped
  out`; `structure.py` PASSES with `max_class_loc 8818 <= 8818` and
  `seam_cut_total 762 <= 762` (16 budget keys, 21 ok lines, 41 counting rules --
  derive, never carry); `layout: GUARD: 0 refusal(s)`; archscore `dS +0.0000 NULL`;
  ledger inventory 5943, unpinned 4620 against 4622 at the base, `draw_range`
  unpinned 0, completeness 0, form 0, `killed_by` 1220, `survivor_triage` 84;
  `--pin-killed` `PIN KILLED: nothing to pin` (rc=0); `ci_predict --base
  d8a4bd36f638` prints no `ADDED UNPINNED`; both claim files byte-identical to
  main's; `merge-tree origin/main HEAD` now exits 0.
- Round 4's evidence stands unchanged and is NOT re-derived here: the 7a block is
  the file's own 51 (`ALL 51 DR BLOCK PASSED` re-taken at this head), the 16
  mutation arms are `16 of 16 red (0 survived)` re-run at this head with identical
  tallies, the null-control harness at 20 seeds prints the same four rows, and the
  fifteen `draw_range.py` sites' dispositions are the 12 seat rows + 2 lane rows
  recorded at `279212233` and `a456c5ed`.
- Whole-file `tests/features.py` at the merged head: `1 of 3930 FEATURE CHECKS
  FAILED` (3911 + #2024's 19, the disclosed `R9-F2.1 P3` Accelerate arm only).
  The scoped local run got through `env_drift --claims-only`, `closure selftest`,
  `features`, `env_drift --all` (56/56), `validate`, `edge`, `backtest` before the
  orchestrator stopped it at 41 min -- the box was at load 62-110 with other seats
  mid-merge. The other 19 scripts are CI's at this head; say so in the body rather
  than re-running them: **tvofi's standing rule is heavy lanes run in CI**
  (2026-10-07), and a seat's 28-script local run at that load is queue pressure,
  not evidence. `run.sh` leases only `stress.py`, which never started, so
  `gate_lock.py status` read `no lease` before and after.
- Two reds in that partial run were NOT the tree's, and each needs a control run
  to say so: `entities.py` reported `FAILED (190s)` in its lane while a hand run of
  the same script prints `ALL 2236 ENTITY CHECKS PASSED` (its own output shows it
  waiting on another seat's gate lease, and the lane's log died with `run.sh`'s
  workdir, so don't explain a lane exit you cannot read -- re-run and cite the
  re-run). And every entities run on this box prints ~46 `FAIL` lines (`hb:positive_control`,
  `a3:roster`, `a5:byte_unchanged`, ...) that are the harness's NEGATIVE-CONTROL
  arms: the rows that judge them print `ok`, and the closing tally is `ALL 2236
  ENTITY CHECKS PASSED`. Counting `^  FAIL` lines as failures would have reported
  a red at main too -- compare the two trees' name sets (`diff` of sorted unique
  names) rather than reading a count.

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
- **A new production module moves five records at once, and a merge where two
  lanes each add one resolves them to neither side's number.** The records are:
  `docs/architecture.md`'s three sentences (headline `N modules, of which 27`,
  `27 of the N`, `the other N-27-1` -- the last two are read by NO check, only
  C32 reads the first), `dev/audit/rounds/round4/D6/claims.py`'s two arch headers
  (executed by `tests/harness_headers.py`), the committed register
  `claims.json`/`claims.md` (regenerate by running `claims.py`, never hand-edit),
  `tests/deployment_shape.py`'s selection-cost note (its `all N files` and the
  per-pair counts, re-derived by `tests/entities.py`'s `_d308_pairs` rule -- the
  lane script itself does not print them), and `tests/closures.json` (the ledger
  driver's business, not yours). Round 5's live case: both sides printed `74`, the
  merged tree had `75`; git reported those lines as CLEAN and the prose would have
  shipped false. The instrument, not the diff, is the resolution.
- **Both-sides-write-the-same-number is the silent case**: `git diff` shows no
  conflict for `all 92 files` when the merged tree has 93, because each side
  independently moved 91 to 92. Sweep the merged TEXT against the merged TREE for
  every count main and your branch both touched -- `comm -12` of the two
  `git diff --name-only <merge-base> <side>` lists is the file set; the census
  commands above are the per-number test.
- A `tests/features.py` block slice must end at the next top-level block header
  (`^# --- `), not at `sys.exit(R.close(`: your block stops being the last one in
  the file the moment another lane appends after yours, and the old rule then
  over-captures and dies on names it never imported (`NameError: FakeState`). The
  r4 harness broke exactly that way; r5's asserts the slice holds one block.
- `/usr/bin/timeout` does not exist on macOS: wrapping a venv run in it exits 127
  and prints nothing, which reads as "the tool produced no answer". Run the tool.
- `closure.py select` keys on the diff against the merge base: after the merge the
  base IS main's tip, so derive scope only once the merge commit exists.
- `main`'s claim file grows under you (`658 -> 671` lines this window, #2024's
  rows). A lane that claims nothing must come out byte-identical to main's --
  `git show origin/main:tests/golden/claimed_drift.txt | cmp - <path>` is the
  check, and it passed here because the branch touches no fixture at all.
- Re-run the ledger check after editing any line `mutation-autofix` has pinned.
  That is round 2's lesson. The rows are content-anchored
  (`FILE:SCOPE KIND DIGEST`), so main's line shifts move no key:
  `layout_problems()` returning 0 is the measurement that says `--normalize` has
  nothing to do. Don't run it "because a merge happened".
- `tests/run.sh` takes the gate lease for `stress.py` itself: never set
  `HPO_GATE_LOCK_LABEL` for a lease you did not take (`gate-scoping.md`).
- A `## Friction` entry that wraps so a continuation LINE starts with a backticked
  token and a colon (`` `LEDGER-MERGE: resolved`, and ...``) is read by
  `policy_lint.mjs`'s `frictionEntries` as a NEW entry and refuses the whole body
  (`does not parse`), which in turn makes `prepr`'s ancestry-reds step report every
  red as UNANSWERED even the ones the body does answer. Re-wrap the sentence (name
  the instrument, not the quoted marker) and both refusals clear.
- A `git ls-files | xargs grep -l` sweep can report files that contain nothing:
  xargs batches + `head` truncation produced three phantom "stale census" hits at
  this head, none real. Re-run any such sweep as `git grep -lE`, one process, no
  batching, before you edit a file because a pipeline named it.
