# The audit toolkit

Everything a round runs on, so a finding can be re-measured by someone who
was not there: the playbook, the harness contract and the instruments a judge
re-runs.

Which of these paths the gate reads is `tests/closure.py`'s `INERT` and
`INERT_EXCEPT` to say; do not restate them.

`CLAUDE.md` tables every brief under `dev/governance/` and says which one binds
which seat; this file does not repeat that list. The rest of the layout:

```
dev/audit/config/             finding.schema.json (a finding without evidence cannot be returned), scopes, ledgers
dev/audit/rounds/round<N>/    a round's reports, harnesses and verdicts
tools/audit/seat/             the stateless seat instruments; each carries --self-test
```

## Running a round: the playbook

From round 11 a round runs from this section and the files it names; a rule
is the named file's, never this table's. `node tools/policy/brief_lint.mjs`
resolves every backticked path here against the tree under test, and its
playbook fixtures under `tools/policy/fixtures/` are the control that a renamed
or removed one goes red. Decision 0016 ties a round to its major version.

| phase | entry | exit | instrument | contract | artefact |
|---|---|---|---|---|---|
| 1 mandate and rulings | the prior round's final state comment on #201 | the owner's mandate comment, scope and expiry, and rulings on #201 | `tools/policy/budget_raise_gate.py` reads a mandate's state | `dev/governance/decisions/0013-verdicts-post-as-the-approver-app.md`, `CLAUDE.md` | the mandate comment id |
| 2 dimensions and finders | a pinned baseline SHA | every scope reported | `.claude/workflows/audit-find.js`, `tools/audit/check_scopes.py` over `dev/audit/config/scopes.json` | `dev/governance/roles/COMMON.md`, `dev/governance/dimensions/` | reports under `dev/audit/rounds/` |
| 3 verify and judge | the finders' reports | every finding judged, classes swept | `.claude/workflows/audit-verify.js` | `verifier.md`, `judge.md`, `dev/governance/rules/defect-root-cause.md` | the round's judge record, `dev/audit/config/bugclasses.json` |
| 4 P3 plan and owner approval | the judged register | `Plan review: approve`, then the owner's approval | `.claude/workflows/audit-plan.js`, `tools/audit/archscore/`, `tools/audit/seat/plan_audit.py` | `architect-planner.md`, `plan-review.md`, decision 0015 | the plan branch, ADRs |
| 5 roster and waves | the approved plan | the roster lints clean | `tools/audit/seat/roster_edit.py`, `tools/policy/brief_lint.mjs` | `standing-roster.md`, `dev/governance/rules/brief-citations.md` | `dev/programme/rosters/`, `critical-path.json` |
| 6 dispatch under the lane caps | after-edges merged; the roster stage compared with the merged pull requests naming the group, so only arms not on main are briefed | a seat running | `tools/audit/seat/pr_cap.py dispatch-gate`, `tools/audit/seat/cloud_dispatch.py` | `standing-dispatch.md`, `orchestrator.md` sections 5 and 5b | the trigger payload |
| 7 fixer and review, cloud seats and relay | a dispatched brief | a verdict at a frozen head | `tools/audit/seat/cloud-setup.sh`, `tools/pr/prepr.sh`, `tools/audit/seat/body_push.sh`, `tools/audit/seat/handoff_push.sh`, `tools/audit/seat/cloud_relay.sh` | `fixer.md`, `fix-review.md`, `designer.md`, `design-review.md`, `root-cause.md` | the handoff refs, the pull request, its verdict |
| 8 carries | a finding that changes a later stage | the carry in that stage's brief | `tools/audit/carry_audit.py`, `tools/audit/fold_ledger.py`, `tools/audit/seat/carry_fold.py` | `dev/governance/rules/finding-propagation.md` | the roster carry or `dev/programme/carries/` |
| 9 the hourly merge pitch | verdicted pull requests | merged, one train batch | `tools/audit/seat/train.sh`, `tools/audit/seat/merge_train.py`, `tools/audit/seat/merge_pr.sh` | `standing-merge.md`, `orchestrator.md` section 11 | merges on main |
| 10 post-merge beat and state docs | a merge | row, handover and state docs current | `tools/audit/seat/postmerge.py`, `tools/audit/seat/beatd.py`, `tools/audit/seat/state_docs.py` | `dev/governance/rules/delivery-status-tracking.md` | `dev/programme/delivery/`, `dev/programme/HANDOVER.md`, a #201 comment |
| 11 stamps | merges since the last tag | the tag pushed | `tools/release/stamp.py`, `.claude/workflows/web-stamp.js` | `orchestrator.md` section 13 | the tag and release notes |
| 12 projections and extension | a wave edge | the plan re-projected; a new group appended | `tools/plan/replan.py`, `tools/audit/seat/plan_page.py`, `tools/audit/seat/flow_metrics.py` | `orchestrator.md` section 2b | the projection, a roster group |
| 13 closure | every phase drained | the criteria below hold | `tools/audit/seat/state_docs.py`, `tools/audit/seat/handover_prompt.py`, `tools/audit/seat/resume_doc.py` | `orchestrator.md` section 9 | the final state comment on #201 |

Lessons (triage batch 141, P545): stack a later part only under the stack
study's conditions, at the parent's merge verdict, never its handoff (round
10's replay: 0.00 to 0.06 h gained in every arm); log a cloud fire by the
session id `list_runs` shows about 2 min later, never by the trigger id, which
later answers 404; an owner order with a trigger condition joins the
orchestrator's pending list the turn it is given, and rotation carries it;
`roster_edit.py append-carry` takes no `--reason`, and each queued op's drain
refusal is read back, since a refused line is never retried. A shape
classifier is driven over a spelling corpus (`fixer.md` step 2).

Closure, the owner's sentence (tvofi, 2026-11-07): "The programme is not
considered closed until both v.10.0.0 and the catalog PR has landed, there are
no open prs, handoffs, carries, findings or leads, and only issue 201 is open".
Its soak step (tvofi, 2026-11-11): round 10's last product merge gets a patch
release that tvofi runs on their install during closeout; v10.0.0 is stamped
only after tvofi says they opened the card's tabs on it, never without.

**Round 10's final shape** (owner cards 1, 2 and 6, 2026-10-24):

- The standing set: the beat jobs `beatd.py` runs from `tools/audit/seat/beat_jobs.py`, each writing digest
  `jobs/<row>`: the tick seat's `tick-digest` and `owed-check`, the roster
  seat's `roster-drain`; the merge seat runs `train.sh` under
  `tools/audit/seat/daemonize.py`; the dispatch and relay seat has no row and
  stays. Owner, verbatim: "make sure the retirement of the standing seats dont
  cause you to run things inline": a seat stays until its job is live and
  verified, and its work never moves into the orchestrator's turns.
- Context rotation, a fresh context between stages (rca, fix, handoff), never
  mid-task or mid-merge: about 150 k tokens for mechanical, standing and relay
  seats, reviewers and S and M fixers; about 300 k for L and XL fixers,
  designers, pre-studies, root-cause and plan seats; about 500 k for the
  orchestrator, which rotates through `state_docs.py` and the resume.
- A blocked verdict of a mechanical class (carry-*, body or figure staleness,
  red-check answer, row-format, head-moved, conflict) goes to a script where
  one exists, else to a fresh sonnet or haiku seat on a short brief; a
  judgement class (harness, mutation-*, class-open, defect, claim-refuted)
  resumes the fixer.

**Production share** (tvofi, 2026-11-01). From the v10.0.0 stamp the machinery
(`tools/audit/`, `tools/pr/`, `tools/plan/`, `tools/policy/`,
`.github/workflows/`, `dev/governance/`, seat scripts) is frozen: a change
merges only if it unblocks a named pull request touching `custom_components/`
or fixes a red, meaning the required `gate` job's on main (`tools/ci/gate.py`)
or a self-test red its own pull request introduces, never one inherited from
main; the rest waits for an instrument window the owner opens. Each round-11
machinery group names its ground; the merge seat checks it at admission. Of the owner's open-PR cap (`DEFAULT_CAPS` in
`tools/plan/replan.py`), 10 slots (the owner's count, not a tree value) are reserved for
`custom_components/` pull requests; a machinery PR never takes one, nor a
production one waits for a machinery slot. A proposal
is accepted only when its friction blocks a production merge, else ruled LOG.
Exempt from all three: a proposal proving over 10% on
CI time, programme completion time, right-first-time rate or token usage,
against a measured baseline and a null control.

**Round 11's opening plan carries:**

- An owner decision on moving the repository to an organization so the native
  merge queue replaces the train (a merge-queue ruleset returns HTTP 422 on a
  user-owned repository; round 10's D13 probe). Weigh plan, visibility, the
  HACS redirect, App installations, deploy key, ruleset ids and owner-keyed
  instruments; after a transfer re-probe queue latency, `merge_group` gate
  names and CI minutes against the train; adopt or decline, and close the held
  groups the queue makes moot (R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY,
  R10-FLY-CARRY-DOC-CONTEXT, R10-TRAIN-OVERLAP-GRADE, R10-FLOW-BODY-ONLY (a)). Context: the Lean flow
  pre-study, section K9 (out of the tree).
- Intake's baseline: R10-PROTECTION-CENSUS's rows (each red check per round-10
  production head: real catch, grader skew or infrastructure). On it, B1
  (triage batch 245, P740) opens the round unless ordered into round 10: on an
  all-product diff `briefs`, `policy-docs` and `wave-script` turn advisory, and
  `blueprints/` joins the product predicate.
- Retire the merge and dispatch seats into beat jobs (tvofi 2026-11-12;
  R10-STANDING-CONTRACTS-P2 carries 9, 12-14), size L, design first: the train
  (`train.sh`, `merge_train.py`) reports each pitch to the digest and retires
  `standing-merge.md`; `standing-dispatch.md`'s dispatch half calls `bus.sh
  dispatch`, never a second writer of the registry or reviewer-fire close. A
  seat stops only after its job ran one real cycle beside it (one pitch merged,
  the seat agreeing), never into the orchestrator's turns. Load, session s14
  from 2026-11-11T01:02Z: 48 merges, 46 reviewer fires.
- Every round-10 group at stage deferred reopens as written, brief and
  carries kept (triage batches 238, 240 and 241 name them and the carries
  re-homed to the groups owning `merge_train.py`,
  `tools/pr/cancel_superseded.py` and `tests/entities.py`).
- R10-ROUND-PLAYBOOK-FINAL's roster carries 17, 25, 26 and 35 to 41, as
  written there: `pr_cap.py`'s production slots, the budget keys' moved paths,
  D15's drawn-power gain, the stubs bump, R10-CI-PRIORITY-PAUSE's three, the
  boost settling tail, R10-PREPR-RESIDUE's seven and
  R10-PREPR-DARWIN-SELFTEST-LANE un-deferred as a macOS leg.
- Benchmark cards G1-G10, accepted (G11 rejected), baseline instruments
  `flow_metrics.py` and `review_strength.py`: G1 a machinery budget of about
  40% of dispatched groups; G2 evidence tiers keyed on closures; G3 a
  two-candidate pilot on L/XL product groups; G4 blind reviewer calibration;
  G5 contract regression evals; G6 ratchets on `tools/`; G7 every process
  change pre-registered with metric, baseline instrument, review date and
  revert criterion, at most about five unvalidated at once; G8 a
  rule-enforcement registry; G9 token and cost telemetry; G10 one tool
  surface. Do not regress: execution-grounded review, diff-scoped mutation,
  measured closures, the train, the frozen-head writer/reviewer split, state
  outside the context, one-sided caps, RCA triggers, null controls, claimed
  drift, small groups.
- The proposals tvofi accepted (V63-V103, exclusions in the proposal record);
  each DEFER of triage PRs #2827-#2831 is owner-accepted and pre-registered
  per G7 before it is built; T2, F5, Q2, Q3 and Q7 take a design seat.
- The architecture score target in `architect-planner.md` is a floor, not a
  cap; a production group takes sound score-improving changes in code it
  already touches. A seat aims at the improvement in the code and the score
  only reports it (`tools/audit/archscore/score.py`); no seat is credited for
  dS alone, and gaming is `fix-review.md` step 14 and `fixer.md` step 17's.
- The away/mold-guard visibility item (tvofi, 2026-11-01): while away is on and
  the mold floor holds the setpoint, the away status and the advisor's savings
  view say so; failing test on away on with the mold floor at or above the
  away target, null control below it.
- The D14 P2 sweep: the eleven F5 clone instances #2238 left are class P2's
  in `bugclasses.json`, re-measured and routed by owning seam. Before reading
  `probes_failed`, the sixth probe in `dev/audit/rounds/round10/D14/sweep-P2/`
  needs `defrost_interval` and `self._pump_signals` bound, or the predicate
  re-extracted; the enumerator's `--fixture` run reads 0 per family as its null.
- D15 reads the next bundle's `unhealthy_input` (only the newest snapshot
  carried it) and runs `dev/audit/harnesses/r10_scores_envelope.py --bundle PATH`.
- Recorded decisions: #1763's P2/I5 split is not built (owner, 2026-10-20);
  #1721's token-view detector stays unproven until an RCA refusal settles it;
  a decision record is named by number, never by path, so none joins
  `policy_lint`'s corpus.

## The harness contract

A harness is a standalone script under `dev/audit/rounds/round<N>/D<k>/`, Python or
Node, that produces the number a finding rests on. The judge re-runs it
without reading the finding, so it has to carry everything:

- A header comment stating what it measures (the metric definition, one
  line), the exact command to run it, the expected value ± tolerance, the
  baseline SHA it was measured against, and the machine.
- It runs from the repository root with `PYTHONPATH=tests/hastub` and never
  `cd`s elsewhere: `tests/harness.py` inserts relative paths, `tests/golden.py`
  opens `tests/golden/` relatively.
- Its first lines, before any numpy import, copy `tests/stress.py`'s thread
  pin — `os.environ.setdefault` for `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
  `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, all `"1"`.
  A threaded BLAS inflates `time.process_time()` by the thread factor and the
  ratio does not cancel unless both sides are pinned alike. Print the factor.
- It writes only under its own directory or a temp root derived from
  `$TMPDIR` (`mktemp -d`, `tempfile.mkdtemp`), a `pip download -d` or
  `--target` included: a literal seat path breaks the judge's re-run in
  another sandbox, and the cwd is the repository (round 8 judge notes 2, 9).
  It sets a private `HPO_PLANDATA` under that root before any Node harness;
  if it uses `env_drift.py` it reads the shared warmed cache in
  `~/.cache/heatpump_optimizer/` and takes a private `DRIFT_CACHE_DIR` only
  when it modifies `env_drift.py` itself.
- It prints one `RESULT <name>=<value> <unit>` line per number, plus
  `RESULT thread_factor=<process_cpu/thread_cpu>`, `RESULT load1=<1-min load>`
  and `RESULT swapins=<count>` at the end of the measurement, the
  `thread_factor` beside every timing and memory RESULT — a block that
  carries none is defective however quiet the box (#950, round 4 D9-INST).
  A `thread_factor` over 1.05 is a BLAS signal, rejected and re-taken. A
  harness running deliberate work on a second thread (the FakeHass trap below)
  can never meet the bare ratio (`h2_cycle.py`: 1.27–1.30 over four re-takes,
  structural), so it subtracts that thread's CPU, prints the residual
  `(process_cpu - deliberate_thread_cpu)/thread_cpu` as `thread_factor` and
  the subtracted CPU as its own RESULT.
  **`load1` is quoted, not gated**: the round-2 judge measured this box's
  ambient floor at 1.86 (best of ten retries: 1.55); a timing is protected by
  a *ratio* metric and a null control under the same load in the same
  session.
- It hooks a named production symbol (`instrumented_symbol` in the finding)
  and moves under a named `perturbation`: a config change or a one-line
  production edit under which the number must change in a stated direction.
  Perturb in memory (`mock.patch.object`, an attribute swap); an on-disk edit
  goes in a worktree of its own, never a tree another run imports from — the
  gate lease serialises `stress.py` alone, not an import (round 8 judge note 3).
  A RESULT computed from constants — `2·n+1` from the bounds shape,
  without hooking `simulate_step` — is voided by the judge.

## What to reuse, and what will trip you

Measured in this repository; verify a line before leaning on it, the tree
moves.

**Builders and fixtures**

| Need | Reuse | Note |
|---|---|---|
| A realistic coordinator payload | `tests/golden.py:_capture_coordinator(config)` and `coordinator_scenarios()` | 5 topologies (`coord_minimal`, `coord_dhw`, `coord_two_zone`, `coord_grid_fee`, `coord_all_features`); freezes the clock at `START`; injects 48 h of prices and forecasts |
| A plan scenario | `tests/golden.py:make(...)` and `SCENARIOS` | `capture(name, spec)` records everything; `assert_invariants` runs on record and check |
| Every entity through the real setup | `tests/entities.py:collect(module, data, coordinator)` | drives `async_setup_entry`; `_honest_coordinator(extra_config, states, dhw)` builds a coordinator with one input cycle done |
| A coordinator in feature tests | `tests/features.py:_t2_coord(states, **extra)`, `_zone_coord`, `_write_coord` | `features.py` cannot be imported — copy the two-liner `HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg))` |
| The CPU-time ruler | `tests/stress.py:reference_solve()` and `Calibration` | fixed L-BFGS-B over a seeded vector; never "improve" it |
| The 51-combination sweep (`sweep_combinations()`) | `tests/stress.py:build_case(...)`, `SEASONS`, `BUILDINGS` | thread pin (the `os.environ.setdefault` loop) must precede the `numpy` import |
| Closed-loop days | `tests/rolling.py:run_rolling(...)` | `learn=True` drives the real coordinator's learner; `SLOW=1` only |
| Challengers and null control | `tests/optimality.py` (`setup`, `evaluate`, `mock.patch.object`), `tests/backtest.py:score`, `tests/profiles.py` | price profiles `winter_typical`, `winter_extreme`, `summer_typical`, `summer_negative`, `shoulder`, `winter_narrow`, `winter_moderate`, `flat`; weather `winter_cold`, `winter_mild`, `summer_warm`, `summer_cool`, `shoulder` |
| The card in Node | `tests/card_rig.mjs:buildCard`, `planStates`, `makeCardContext`, `qaTopologies` | the DOM stub returns a constant 900×400 rectangle: no geometry |
| The card's drift states | `tests/card_drift.mjs:STATES` — run it with `--list` rather than carrying a count | drive both a working-tree card and a `git show` card |
| Real geometry | `tests/card_browser.mjs` | Playwright resolved from `NODE_PATH`; Chromium under `PLAYWRIGHT_BROWSERS_PATH` |
| Mutation-proof idioms | `tests/features.py` (search `_fl_orig = _FlOpt`: class-attribute swap, `try/finally`), `tests/features.py` (search `rail: {name}`: input-mutation rail over a `_SAFE` baseline dict), `tests/optimality.py` (`mock.patch.object`) | the third is the only `unittest.mock` use in the suite; the first two are cited by search text, not line number |

**Traps**

- `tests/harness.py:FakeHass.async_add_executor_job` runs the function inline
  on the calling thread. An event-loop or GIL measurement built on `FakeHass`
  measures nothing about the executor boundary; use a real loop and a
  `ThreadPoolExecutor`.
- `golden.py`, `env_drift.py`, `closure.py`, `frontend.py`, `manual_plan.py`,
  `stress.py` and `structure.py` have `__main__` guards.
  `entities.py`, `features.py`, `rolling.py`, `backtest.py` and
  `optimality.py` run every check at import and `sys.exit`.
- `tests/plan_view.py` writes a per-checkout plan payload under `/tmp` and
  every Node harness reads it; `card.mjs` alone falls back to an unhashed
  legacy path with a warning, the others fail. Set `HPO_PLANDATA` per harness.
- `tests/env_drift.py` runs `git worktree add` in the repository it is run
  from and refuses a ref that resolves to `HEAD`.
- `tests/closure.py` globs `tests/*.py` and `tests/*.mjs` non-recursively;
  `tests/run.sh`'s wiring check does the same. A script in a subdirectory is
  invisible to both and to `no-copies`.
- The assertion `tests/closure.py`'s `SLOW_GATED` comment places in
  `tests/entities.py` (each name `SLOW`-gated in `run.sh`) does not exist.
- `HeatPumpOptimizerSensorBase.__init_subclass__` wraps every subclass's
  `native_value` and `extra_state_attributes` in a non-finite scrub; deleting
  a per-sensor guard will not reproduce a non-finite publish.
- `optimizer.py`'s GIL yields are its `sleep(0.002)` calls: between
  L-BFGS-B starts (`_multi_start_minimize`), in `_lbfgsb_restart` and at the
  DHW-to-space seam; grep, never count them.

`check_scopes.py` proves `scopes.json`'s seats disjoint and complete, every
tracked path in a universe or on `_coverage_excluded`, and a harness naming a
brief cited by it.

## Harnesses that read moved paths are retired

A harness `tools/audit/seat/moved_paths.py` lists with a `[STALE?]` read is a
record, not re-run at `main`, unless a bug class's `detector` or `barrier`, or
the latest round's `ISSUES.json` or `JUDGE.json`, cites it: then it is
repaired, old path first. A seat re-running a retired one repairs it first.

## A defect in an instrument is a finding

A defect your dimension's method meets in an instrument (`tests/hastub`, the
gate's checks and budgets, the harness contract, the lint lanes, this toolkit)
is a finding **of your dimension** under the same bar as any other, not prose
in a report. It goes panel, judge, then issue, and **filing waits for the
judge**, who re-measures with the accused instrument; a verifier who cannot
make the accused check fire has not refuted it, and says which they could not
separate. `CLAUDE.md`'s order still governs: a one-line instrument repair is
made in place, with no issue.

## Rounds 1-3 are at a SHA

`tools/audit/round1/` to `round3/`, the done rosters `wave-1b-groups.json`,
`wave-2-groups.json` and `wave-3-groups.json`, `web-phase0.js` and
`triage-quiet-judges.json` are at
**`d5d8c4a72fa7be7aebecc9e58d55002be17cac08`** (`origin/main` at v6.3.18, on
`main`'s first-parent history; `git show d5d8c4a:tools/audit/round2/JUDGE.md`);
their briefs record what a judge established and refuted, so read them before
re-deriving anything a group in them settled. Every number anything still acts
on is in `dev/programme/register/audit-2026-09.md`. Round 2's harnesses are at
`757e164` (which still run is `round2/HARNESSES.md` at `d5d8c4a`, final at
that commit only), its numbers recorded at `c398fc84`; the tag `audit-round2-evidence` moved once, so cite the SHA. A
harness's root rule varies (`D6/claims.py` measures the working directory,
`D7/sysid_plant.py` its own checkout): copy it into the tree under test and say
which it used.

## The four that stayed

Each, added by a fix after its round closed, is an instrument someone re-runs:
evidence is archived, instruments are kept.

| file | metric | added by | who re-runs it |
|---|---|---|---|
| `j5_gil.py` | starvation share = sum(heartbeat gaps > 5 ms) / solve wall, on a real asyncio loop with a 1 ms heartbeat and `HeatPumpOptimizer.optimize` submitted the way production submits it | `8542e51` (W3-G3, #290 #199) | the #290 judge built it; `briefs/fix-review.md` §9 sends a fix reviewer to it |
| `h8_single_scenario.py` | whether the stress gate detects a 2x regression confined to one scenario, and stays quiet on a multi-start basin flip (#346) | `291ae76` (#378) | anyone changing `tests/stress.py`'s per-scenario or solver-work rules |
| `h9_basin_coverage.py` | how many of the 51 sweep scenarios the solver-work rule judges rather than exempts, against the tree's own floor (#387) | `32f309f` (#388) | the same |
| `k1725_blas_kernel_gap.py` | the ftol check's arms and the R9-F2.1 P3 margins, per OpenBLAS kernel via `OPENBLAS_CORETYPE` | `613bff1b` (#1726, #1725) | anyone adding a knife-edge optimizer comparison (`tests/README.md`'s kernel rule) |

All four drive production symbols under the harness contract; never run
`j5_gil.py` on `FakeHass` (the first trap above).
