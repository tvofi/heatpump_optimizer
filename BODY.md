R10-CI-LAYOUT-P2, sub-PR P2b ("cut-over"), units **U5** (tests.yml into the umbrella) and **U5b** (the ci-ratchet payment), each its own commit range. Part of #2495.
Built offline against U0c's "## Interface" (`handoff-body/r10-ci-layout-p2-u0c`) and P2a as merged (`a1633381a`). Design: DESIGN-P2 §2, §4.2, §10's U5 row at `1371a0a6`; plan §0 item 5 and §6 at `1011d6b2f`; roster carry 3 (pay, don't raise).

## Head

Code head: `handoff/r10-ci-layout-p2-u5` = `fbc994804` (full SHA in the ref), on origin/main `e45fc34fb145` (contains `a1633381a`: `git merge-base --is-ancestor a1633381a origin/main` rc 0), stacked as the brief says:
- U0c's three commits (`fef4a1351..d22b5f303`, cherry-picked as `af84fe54d`, `aac28f8ed`, `4ee8ceb8e`);
- U9a's four (`fef4a1351..c9d647e64`, as `6d0050dc6`..`b0bd2d25e`), clean picks;
- then this unit: **U5** `39927cea4`, **U5b** `08a059415`, and `fbc994804`, which makes U5's three harnesses take the canonical `repo_root` walk (`harness_headers.py` refused their `parents[n]` roots; no reading moved).

So `git log origin/main..HEAD` holds ten commits: seven are the stack's and three are mine. No roster branch is merged.

origin/main moved to `d6308d77c` before the push (read 2026-10-23 00:47 UTC). Its 29 changed files share none with this unit: `git diff --name-only e45fc34fb d6308d77c | grep -E 'tests.yml|run.sh|tools/ci|required-contexts|entities.py|r10_ci_gate_core'` printed only `tests/closures.json` (two `inert_reads` lines, a file this unit does not edit). Every figure below is at base `e45fc34fb`.

## Unit

`git diff --numstat` per range (production: `tests.yml`, `run.sh`, `gate.py`, the fixture, the `entities.py` text; everything under `dev/audit/harnesses/` is test):

```
U5  b0bd2d25e..39927cea4
137  160  .github/workflows/tests.yml
 43    0  dev/audit/harnesses/r10_ci_layout_u5/tests_map.json
156    0  dev/audit/harnesses/r10_ci_layout_u5/unitcheck.py
  8    5  tests/entities.py
U5b 39927cea4..08a059415
 66    1  .github/workflows/tests.yml
 24    7  dev/audit/harnesses/r10_ci_gate_core.py
104    0  dev/audit/harnesses/r10_ci_layout_u5/run_part.py
 54    0  dev/audit/harnesses/r10_ci_layout_u5/script_runs.py
 13    3  dev/audit/harnesses/r10_ci_layout_u5/tests_map.json
  3    2  dev/audit/harnesses/r10_ci_layout_u5/unitcheck.py
 50   11  tests/run.sh
 12    5  tools/ci/gate.py
  1    0  tools/policy/fixtures/required-contexts.json
```

That is about 145 production lines added in U5 and 129 in U5b, against the about-400 bound. The new files sit under `dev/audit/`, an `INERT` prefix of `tests/closure.py`, so they need no classification line.

**U5** (`tests.yml`, plus the `_PT_EXEMPT` text):
- `on: workflow_call` with U0c's six inputs (`gate_scope`, `pr`, `base`, `head`, `recheck`, `no-skip`; each `type: string`, `default: ""`) and the three secrets (`required: false`). `push`, `pull_request`, `merge_group` and `workflow_dispatch` are gone; inside a call `github.event_name` is the umbrella's, so every job guard is unchanged.
- The workflow `concurrency:` group and the `cancel-superseded` job are removed (ci.yml owns both).
- `fast`: the "Decide the gate scope" step is removed. "Run the suite" takes `GATE_SCOPE: ${{ inputs.gate_scope == 'auto' && 'auto' || 'full' }}` and `GATE_SCOPE_BASE: ${{ env.GOLDEN_REF }}`. The prelude's rule (push full, otherwise auto) equals the old step's on every event `tests` runs on, and an empty input runs full.
- `browser` and **`typing`** stand down at the step level. Each gains a first step, "Say the lane-skip decision this run stands on", and every other step carries the closure-scope skip `if:`. **Departure, raised:** the design's U5 row names `browser` only. `typing` carries the same job-level skip (O17's Level 0, on its `typing_skip`), which the design's map predates. `typing` is a required `tests / typing`, and under 4.2 a skipped required job FAILs `gate`, so every roster-only pull request would have failed. This applies the design's own 4.2 rule to the second job it covers.
- `lane-proofs` and closure-scope's "Identify the diff…" step read `inputs.recheck == 'true' && inputs.no-skip != 'true'`.
- The three autofix push steps: four `gh workflow run <wf>.yml --ref` lines become `gh workflow run ci.yml --ref "$HEAD_REF" -f pr="$PR" -f base="$BASE_REF"`, with env `PR: ${{ inputs.pr }}` and `BASE_REF: ${{ inputs.base }}`. The codeql trigger probe is dropped.
- The approve steps are **retargeted, not deleted** (M-3 open, default keep). Their code lists every `action_required` run on the branch, so a held `CI` run is approved like any other. Only their comments change, to name the CI run and M-3.
- `ci-ratchet`'s "Fetch the recent push runs' durations" runs `python3 -I tests/ci_ratchet.py --gather-runs "$RUNNER_TEMP/runs.json"` (U9a's Wiring line).
- `tests/entities.py` `_PT_EXEMPT`: the reasons for `tools/ci/gate.py` and `prelude.py` are rewritten; the arm is declined (see Wiring).

**U5b** (`tests.yml`, `run.sh`, `gate.py` with the fixture, the gate-core harness):
- New job `tests / arch-instrument` (`needs: [closure-scope]`, the same event guard as `fast`, 60 min cap). It runs the pair through `RUN_PART=arch ./tests/run.sh` under `fast`'s scope (`GATE_SCOPE` from `inputs.gate_scope`; `GATE_SCOPE_BASE: origin/${{ inputs.base || 'main' }}`, where select takes the merge base) and `fast`'s lane-skip decision (`fast_skip`). It stands down at the step level.
- `fast` sets `RUN_PART: fast`.
- `lane-proofs` needs `arch-instrument`, and records fast's proof only when `arch-instrument` also succeeded. That proof now stands in for both jobs.
- `tests/run.sh`: `RUN_PART` (`fast`, `arch`, anything else is everything):
  - `fast`: `lane_golden` `skip`s the pair by name ("…CI's tests / arch-instrument job runs it"), so the TEST NEVER RAN accounting sees both.
  - `arch`: `LANES="golden"` and `ALL_LANES="golden"` (no stress lane); `lane_golden` runs only the pair; the per-script accounting owes exactly the pair; the plan's skip list is cut to the pair, so its NOT RUN block is honest.
  - Unset: byte-for-byte the old behaviour. The entities placement pin (the pair's `run` lines in `lane_golden`) and the `LANES="units golden e2e"` pin both still hold.
- `tools/ci/gate.py`: `UNITS["tests"]` gains `arch-instrument`, so it is required on pr, pr-cc, no-pr and push. The self-test changes with it:
  - "REQUIRED['pr'] is the 17 contexts…" compares the 17 less `arch-instrument`;
  - "arch-instrument is P2b's" (want False) becomes "arch-instrument is required on every event class";
  - new: "a run without tests / arch-instrument" FAILs naming it.
  
  The fixture's `gate_required` gains `tests / arch-instrument`, so the entities equality holds.
- `dev/audit/harnesses/r10_ci_gate_core.py`: the shim keeps `arch-instrument` out of the design model's 17 names and fills it green into any run carrying `tests / *`. `b3` now reads **this tree's** `tests.yml` (see P2a defect).

The payment is **headroom, not forced**: about 5 min, 10 %, against +15 % runner variance (plan §0 item 5). Main's window then read 49.86 median against the 54.825 budget. Roster carry 3's diagnosis put the pair at about 41 of `fast (3.14)`'s 58 min on a slow runner.

## Interface

Consumed (U0c, binding):
- The `tests` caller's `with:` is exactly `gate_scope`, `pr`, `base`, `head`, `recheck`, `no-skip`, and its `secrets:` are `CLOSURES_PUSH_TOKEN`, `HPO_RUNS_PEM`, `HPO_RUNS_APPID`. `tests.yml` declares exactly these. The grant is `contents: write`, `actions: write`, `pull-requests: read`; no job here asks for more (the widest is the autofix jobs' `contents: write` + `actions: write`).
- The prelude's workset gives `tests` code kinds only: pull_request (opened, synchronize, reopened, a retarget), push, merge_group, workflow_dispatch.
- `ci.yml`'s `workflow_dispatch` inputs `pr`, `base`, `recheck`, `no-skip`, for the autofix dispatch.

Exported:
- Check names `tests / <job>`, unchanged for every job that existed, plus **`tests / arch-instrument`**. Its id differs from `arch-score / arch-score` (D-2).
- `tools/ci/gate.py` `UNITS["tests"]` = `fast (3.14)`, `arch-instrument`, `browser`, `briefs`, `typing`, `mutation`, `closures`, `closure-scope`; `REQUIRED` and `gate_required` follow from it.
- `tests/run.sh` env `RUN_PART=fast|arch`.

Gone from `tests.yml`: the `cancel-superseded` job, the concurrency group, and its own `workflow_dispatch` (merge_train dispatches `ci.yml`, per U9a).

## Static map

`python3 dev/audit/harnesses/r10_ci_layout_u5/unitcheck.py` (BASE default `origin/main` = `e45fc34fb`). It runs `measure/rev/unitcheck2.py` from `archive/probe/design-ci-rev4`, read via `git show`, never copied, under `dev/audit/harnesses/r10_ci_layout_u5/tests_map.json`:

```
ok   static, the head (want rc 0):   STATIC rows 169->178 lost 0 gained 0 changed 25 (mapped 25) misplaced 0 rc 0
```

rc 0 against current main. At U5's own commit `39927cea4`, under U5's map: `STATIC rows 169->171 lost 0 gained 0 changed 23 (mapped 23) misplaced 0 rc 0`.

The map, per the §10 row:

| kind | rows |
|---|---|
| dropped | `cancel-superseded|`, `cancel-superseded|order`, its two steps; `fast|Decide the gate scope` (moved to the prelude: its `scope` output reaches `fast` as `inputs.gate_scope`; U0c's map covers the prelude's step) |
| gained (U5) | `browser|Say the lane-skip decision this run stands on` and `typing|…`, each placed by `after` at `<job>|^` |
| gained (U5b) | the `arch-instrument` job (its row, its order row and five steps: wholly new, so no placement needed) |
| changed (U5) | `|triggers`; `browser|` and its 8 steps; `typing|` and its 6 steps (the `if:`s); `fast|Run the suite`; `lane-proofs|` and `closure-scope|Identify the diff and base the heavy lanes would judge` (the `inputs.*` `if:`s); the three autofix push steps; `ci-ratchet|Fetch the recent push runs' durations` |
| changed (U5b) | `lane-proofs|Record fast's green run at this base and diff`, `lane-proofs|Save fast's proof` |

`|floor` is unchanged (not listed).

Two things the instrument cannot see: a mapped `changed` row may change any way, and `uses:`/`with:` are not hashed on a step's caller. So the harness adds the stand-down and interface checks below.

## Controls

**Static, stand-down and interface** (`unitcheck.py`, after U5b; `RESULT PASS (0 failed)`):
```
ok   static, the head (want rc 0):   STATIC rows 169->178 lost 0 gained 0 changed 25 (mapped 25) misplaced 0 rc 0
ok   stand-down, the head (want none): none
ok   stand-down, BASE's tests.yml (want arch-instrument absent, browser and typing refused): arch-instrument: required by gate.py, absent from tests.yml; browser: a job-level `if:` reads a skip decision (!cancelled; typing: a job-level `if:` reads a skip decision (!cancelled(
ok   interface, the head (want none): none
ok   plant 1, an unmapped job added (want rc 1):   STATIC rows 169->181 lost 0 gained 3 changed 25 (mapped 25) misplaced 0 rc 1
ok   plant 2, browser's decision step moved after its checkout (want rc 1):   STATIC rows 169->178 lost 0 gained 0 changed 25 (mapped 25) misplaced 1 rc 1
ok   plant 3, browser's job-level skip restored: static (blind, reads rc 0):   STATIC rows 169->178 lost 0 gained 0 changed 24 (mapped 24) misplaced 0 rc 0
ok   plant 3: stand-down (want browser refused): browser: a job-level `if:` reads a skip decision (...)
ok   plant 4, an undeclared input passed (want refused): caller passes ['base', 'gate_scope', 'head', 'legs', 'no-skip', 'pr', 'recheck'], tests.yml declares ['base', 'gate_scope', 'head', 'no-skip', 'pr', 'recheck']
```

The stand-down rule's job set is derived from `gate.REQUIRED`'s `tests / *` names (`coverage` excepted: it is required on push only, where closure-scope never runs). The BASE line is the defect at the baseline; the head line is its absence.

**U5b, the run.sh switch.** Failing test first: `python3 dev/audit/harnesses/r10_ci_layout_u5/run_part.py` drives `tests/run.sh` serially (`GATE_JOBS=1`, `GATE_SCOPE=full`) with a stub `PYTHON` per part.

At `39927cea4`, before the switch:
```
ok   unset: the pair runs (null): rc=0 ran 35 script(s), pair ran: ['tests/arch_score.py', 'tests/arch_score_head.py']
FAIL fast: the pair is skipped by name, and nothing else moves: rc=0 ran 35, pair skipped [], named the job: False, other scripts as unset: False
FAIL arch: only the pair runs, and its accounting passes: rc=0 ran [... all 35 ...]
RESULT FAIL (2 failed)
```

At the head:
```
ok   unset: the pair runs (null): rc=0 ran 35 script(s), pair ran: ['tests/arch_score.py', 'tests/arch_score_head.py']
ok   fast: the pair is skipped by name, and nothing else moves: rc=0 ran 33, pair skipped ['tests/arch_score.py', 'tests/arch_score_head.py'], named the job: True, other scripts as unset: True
ok   arch: only the pair runs, and its accounting passes: rc=0 ran ['tests/arch_score.py', 'tests/arch_score_head.py']
RESULT PASS (0 failed)
```

**The plan's mutant** (dropping the lane-skip leaves `fast` unchanged, which is red): `run_part.py --mutant` removes the fast branch, keeping the `run` lines.
```
FAIL fast: the pair is skipped by name, and nothing else moves: rc=0 ran 35, pair skipped [], named the job: False, other scripts as unset: False
MUTANT KILLED: refused ['fast: the pair is skipped by name, and nothing else moves']
```

**The parallel path** (`GATE_JOBS=3`, stub `PYTHON`): arch rc 0, `ALL TEST SCRIPTS PASSED`, 2 scripts; fast rc 0, `ALL TEST SCRIPTS PASSED`, the two `SKIP: tests/arch_score*.py (RUN_PART=fast: CI's tests / arch-instrument job runs it)` lines.

**Under scoping.** The `PYTHON` stub runs only `tests/closure.py` for real. In a scratch worktree that carries this `run.sh` committed and an untracked `docs/README.md` (docs only), with `GATE_SCOPE=auto GATE_SCOPE_BASE=HEAD`:
- arch: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. NOT RUN names only `tests/arch_score.py` and `tests/arch_score_head.py`, then `NO TEST SCRIPT RAN`, rc 0.
- fast, same diff: rc 0, `4 TEST SCRIPT(S) PASSED; 31 SCOPED OUT AND NOT RUN`.
- On this branch's own diff (a gate file): `MODE: FULL`, and the arch part ran the pair alone.

**Null control, `script_runs_per_push == 54`, unchanged.** `python3 dev/audit/harnesses/r10_ci_layout_u5/script_runs.py`. Its rule is `tests/entities.py`'s `_cir_once_count`: the closures plan (`closure.test_scripts()` less `SLOW_GATED`) plus `coverage_tree.sh`'s DERIVED `fast)` list, run by bash. Readings:
- base `e45fc34fb` (stacked tree): `script_runs_per_push=54 budget=54`;
- head: `script_runs_per_push=54 budget=54`;
- plant `--plant-drop-pair` (a payment that stopped measuring the pair): `script_runs_per_push=52 budget=54 (PLANT: the pair dropped from the closures plan)`, so the instrument moves.

`ci_ratchet.py`'s `script_runs` still counts the pair's rows: they come from the `closures` and `coverage` lanes (`LANES = ("closures", "coverage")`), and neither reads `RUN_PART`. `coverage_tree.sh` greps `run "$PYTHON" tests/…` lines and already excludes the pair, and `derive_closures.sh` does not call run.sh.

**gate.py, mutation proof.** Deleting `"arch-instrument"` from `UNITS["tests"]` gives `gate self-test: 28 checks, 3 failed`:
- `arch-instrument is required on every event class (U5b): got ['no-pr', 'pr', 'pr-cc', 'push'], want []`;
- `fixture gate_required == REQUIRED's union`;
- `a run without tests / arch-instrument (U5b): got 'PASS', want 'FAIL tests / arch-instrument: ABSENT (this run)'`.

Restored: `28 checks, 0 failed`.

**Gate-core harness** (`dev/audit/harnesses/r10_ci_gate_core.py`):

| arm | stacked base | head |
|---|---|---|
| `replay` | rc 0, IDENTICAL to `1371a0a6:measure/rev/gate_replay2.txt` | after U5b's `UNITS` edit and before the harness edit: crash (`TypeError` in the oracle's `newest`, because the model's ruleset was asked for an 18th context); after: rc 0, IDENTICAL |
| `replay --no-b3-fill` | – | output byte-identical to the base's (`diff nofill_base.txt nofill_head.txt` empty), so B3's null is unchanged |
| `b3` | GREEN | before the harness edit, reading origin/main: RED (`only in REQUIRED ['arch-instrument']`); after: GREEN |
| `b3 --plant` | – | RED (`only in tests.yml ['ci-ratchet']`) |

**The head-copy carry (declined; measured):**
- prelude: `prelude.outputs` driven over pull_request opened/synchronize/reopened (the only runs graders-head-copy executes in) made `API reads on pull_request code kinds: 0`. The null, an `edited` kind, made 1 read (`repos/o/r/actions/workflows/ci.yml/runs`).
- gate: `gate.gate` with every required job green but `pr-contract / pr-contract` queued gives `(False, ['pr-contract / pr-contract: PENDING (this run)'])`; the null, with it completed, gives `(True, [])`. ci.yml's `pr-contract` needs `tests`, so inside `tests` it is never complete.

**Hygiene:**
- `tmp_paths --check`: 0 refused.
- `throwaway_git --check`: 0 refused.
- `selftest_wiring --check`: `87 self-testing, 87 wired, 0 unwired`.
- `tests/structure.py`: STRUCTURE RATCHET PASSED.
- `ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against e45fc34fb145`, and no `PREDICT mutation` line, so no unpinned sites.

**Scoped gate:** `closure.py select --diff <merge base>` reads `MODE: FULL -- … .github/workflows/ci.yml changes the gate itself` (U0c's file; this diff adds `tests.yml`, `run.sh` and `tools/ci/`, gate files too). Locally I ran the run_always set this diff reaches, serially, with a Python 3.13 venv from `tests/requirements-ci.txt`:
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: 11 of 2400 FAIL at the head against 1 of 2400 at the stacked base. The base's one is U0c's known red. The ten new ones are listed under Red checks.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: at `08a059415`, `1 of 109 HARNESS HEADER CHECKS FAILED` (the depth-root seam in this unit's three new harnesses); at the head, after `fbc994804`, `ALL 109 HARNESS HEADER CHECKS PASSED` (4 min, run alone).

## Live checks owed

For the coordinator, on `ci-probe/u5` with its `-before` twin, per DESIGN-P2 §10's U5 row:
1. **A `pull_request` pair** (twin draft PR on main's layout as BEFORE; the probe's draft PR as AFTER; same App identity). `unitcheck2.py runtime`: lost 0, gained 0, with allowed differences:
   - the umbrella's own jobs;
   - `cancel-superseded` dropped from tests;
   - `tests / arch-instrument` gained;
   - `browser`'s and `typing`'s first step gained.

   PR-only jobs that must appear: `tests / lane-proofs`, `tests / graders-head-copy`, `tests / nightly-status`, and the autofix chain (`closures-autofix`, `claims-autofix`, `mutation-autofix`, as executed or skipped by their own `if:`). Read `fast (3.14)`'s log for `GATE_SCOPE=auto` and `arch-instrument`'s for `RUN_PART=arch` with a MODE line.
2. **A dispatch pair with `-f recheck=true`** (`gh workflow run tests.yml --ref <before> -f recheck=true` against `gh workflow run ci.yml --ref ci-probe/u5 -f recheck=true`): `closure-scope`'s laneskip step and `lane-proofs` run on both sides.
3. **A dispatch pair with `-f no-skip=true`**: the laneskip step and `lane-proofs` are skipped, and every lane runs, `arch-instrument` included.
4. **Step-level stand-down**, from a re-dispatch at an identical base and diff whose `browser_skip` (or `typing_skip`) reads `skip`: `tests / browser` (or `typing`) concludes **success** having run only its "Say the lane-skip decision" step, and `gate` passes. The same for `arch-instrument` on `fast_skip`.
5. **The autofix dispatch**: one `ci.yml` dispatch with `-f pr=<n> -f base=main` from a GITHUB_TOKEN autofix push, whose prelude verifies and whose `gate` completes (§10 step 4; M-3(b) for the held run is U10's).
6. **U5b's two-stage proof** (plan §6.4):
   - P2b's own FULL run shows `tests / fast (3.14)` ending at least 5 min sooner than the base's;
   - after the merge, the review's §3 window rule: 5 of 8 push runs, and never re-run a push run.

## Wiring

- **`tests/entities.py` (U9b): the D11-s1-03 write-grant reader went blind on `tests.yml`.** `_prw_defects` inspects a workflow only when its `on:` lists `pull_request`. `tests.yml` is now `workflow_call`, so the main check ("no job holding a write grant on pull_request runs the pull request's own program…") reads green **vacuously** for it. Its two null controls catch this: "…restores and token hygiene undone…" `refused jobs on the undone copy: []`, and "…a report run from the working tree after the push step's pull…" `refused: []`. A `workflow_call` callee of a workflow that runs on `pull_request` must count as pull_request-reachable. The null's expected list loses `tests.yml:cancel-superseded`. I did not change the autofix jobs' restores or `persist-credentials: false`; the reader no longer looks at them.
- `tests/entities.py` (U9b), the rest of the reds this diff produces, all cut-over consequences:
  - `_AF_DISPATCHED` becomes `{"ci.yml"}` (the three "…dispatches every workflow owning a required context but Governance" lines), and "codeql.yml accepts the autofix jobs' dispatch" retires.
  - "every required context runs on a merge-queue entry" and "…on an autofix or batch-proof dispatch (B9)": `tests.yml`'s triggers now live in `ci.yml`, so read them there.
  - "exactly seven jobs override the workflow's read-only floor…" (now six; `cancel-superseded` is ci.yml's).
  - "tests.yml cancels a superseded older SHA" moves to `ci.yml`.
  - "a red that lands after pr-contract ran re-runs it…": `Tests` is no longer a pull_request workflow (the follower is U10's to retire).
- `tests/entities.py` (U9b), optional: register the two rules this unit's harness checks as pins, so CI guards them:
  - no `tests / *` job `gate.py` requires carries a job-level skip `if:` (`unitcheck.py`'s `stand_down_problems`);
  - `RUN_PART=fast` skips the pair by name and `arch` runs only it (`run_part.py`, 3 s with a stub).
- `tools/coverage/coverage_tree.sh:25` (comment): "`fast`, where run.sh still runs them" becomes "`tests / arch-instrument`, where run.sh runs them (RUN_PART=arch)". The script list itself is unchanged.
- **The head-copy arm (U0c's forward-carry) is declined, not wired.** The reasons are now in `_PT_EXEMPT`, measured under Controls:
  - `prelude.py` makes no API read on the pull_request code runs `graders-head-copy` runs in;
  - `gate.py`'s token paths judge or re-run this head, and from inside `tests` its judge always FAILs (`pr-contract` needs `tests`), so neither program's exit can show what the token sees.

  The U0 live probe remains their Actions-token run before P2b merges.
- No new self-test, so no `instrument-self-tests` step. No new push site.

## P2a defect

`dev/audit/harnesses/r10_ci_gate_core.py`'s `b3` arm enumerated `origin/main:.github/workflows/tests.yml` rather than the tree's. On any branch that moves a push job, it compared the branch's `REQUIRED` with main's jobs: it read RED here (`only in REQUIRED ['arch-instrument']`) for a parity the tree holds. Fixed to read the tree's file, the one this tree's `gate.py` is paired with; see Controls. No defect in `tools/ci/*.py` itself.

## Mutation proof

See Controls:
- `gate.py` without `arch-instrument` in `UNITS`: 3 FAIL, restored 0.
- `run.sh` without the fast skip: `MUTANT KILLED`.
- The static plants: 1, 2 and 4 refused; 3 refused by the stand-down half.

## Null control

See Controls:
- `script_runs_per_push` 54 at base and head, 52 under the plant;
- run.sh unset unchanged (35 scripts both ends);
- `replay --no-b3-fill` byte-identical;
- prelude's edit-kind read.

## Figures

- `STATIC … rc 0`: `python3 dev/audit/harnesses/r10_ci_layout_u5/unitcheck.py`.
- `script_runs_per_push=54`: `python3 dev/audit/harnesses/r10_ci_layout_u5/script_runs.py` (rule: `entities.py`'s `_cir_once_count`).
- run.sh parts: `python3 dev/audit/harnesses/r10_ci_layout_u5/run_part.py [--mutant]`.
- `gate self-test: 28 checks, 0 failed`: `python3 -I tools/ci/gate.py --self-test`.
- Replay and b3: `python3 dev/audit/harnesses/r10_ci_gate_core.py replay|b3 [--no-b3-fill|--plant]`.
- `11 of 2400` / `1 of 2400`: `PYTHONPATH=tests/hastub python3 tests/entities.py` at head and at the stacked base `b0bd2d25e`.
- Line counts: `git diff --numstat` per range, as above.
- The headroom (about 5 min, 10 %, +15 % variance) and the pair's 41 of 58 min are the plan's and roster carry 3's figures, not re-measured here: no CI run of this layout exists offline.

## Red checks

- **main's ancestry**: at `origin/main` `d6308d77c` (`gh api commits/<sha>/check-runs?filter=latest --paginate`, 43 runs, 2026-10-23 00:47 UTC), no check run had concluded `failure`. Two `rerun-stale-contract` runs were `cancelled` (that follower's head-keyed group, by design); four (`Analyze (python)`, `coverage`, `fast (3.14)`, `closures`) were still in progress. Root-cause trigger: not fired by this branch.
- `nightly-status`: if it reads red at the open (the roster's carry names it red on main's ancestry), it grades the nightly, not this diff. This unit changes no nightly input and no `tests/nightly_status.py` reader (carry 9 untouched).
- **At this head, locally, inherited from U0c**: entities' "the template arm turns the acceptance red…" is U0c's `policy_lint` "2 files define pr-contract" deadlock (U0c's Red checks and ESCALATE). It reads the same at the stacked base.
- **At this head, locally, by design of the cut-over**: the ten entities lines listed under Wiring, each a pin that reads `tests.yml` as a standalone pull_request workflow. Cheaper detector: `tests/entities.py` itself, which named all ten locally before any push. The D11-s1-03 reader's blindness is the one of these that is a lost guard rather than a stale fact (Wiring, first line).

## Forward-carry

- To the P2b coordinator and U9b: the Wiring lines above, first the D11-s1-03 reader. Carry: R10-CI-LAYOUT-P2
- To U9p (policy text): `ci-autofix.md`'s retrigger wording (the autofix jobs now dispatch `ci.yml -f pr -f base` once, not four workflows), and `tests/README.md` / HANDOVER on `RUN_PART`, where they describe the suite's split. Carry: R10-CI-LAYOUT-P2
- The `typing` stand-down departure (Unit) for the design reviewer. If it is refused, `typing` must instead lose its Level-0 skip, or every roster-only PR fails `gate`. Carry: R10-CI-LAYOUT-P2

## Friction

- `brief-environment: cost: as U9a found, the container's python3 is 3.11 without voluptuous; a 3.13 venv from tests/requirements-ci.txt was needed for entities.py. Carry: the dispatch payload's setup line.`
