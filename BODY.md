R10-CI-LAYOUT-P2, sub-PR P2b ("cut-over"), unit **U0c**: the umbrella skeleton. Part of #2495.

## Head

Code head `d22b5f303e09a67106fb44da03ad9e014eb1f840` (`handoff/r10-ci-layout-p2-u0c`), cut from `origin/main` `fef4a1351db3e8e328d714e84299284c6876eecb`, which contains P2a's merge `a1633381a` (`git merge-base --is-ancestor a1633381a origin/main`: rc 0). Every figure below is taken against that base (2026-10-22T23:33Z to 2026-10-23T00:20Z, `date -u`). `git log fef4a1351..HEAD` holds the unit's 3 commits and no merge.

`origin/main` has since moved to `e45fc34fb`. That tip is not merged here, so the coordinator can cherry-pick the unit's commits. `git merge-tree --write-tree HEAD origin/main` is rc 0, a clean merge. Of the files this unit reads, main's delta touches only `tests/entities.py` (`_friction_trailer_fixture`) and `policy_lint.mjs`'s `FRICTION_TRAILER_RE`, neither read by these pins.

Probe ref (NOT part of P2b): `handoff/r10-ci-layout-p2-u0c-probe` = `65f112ec51dfa1f3d1617dda2bac74adab394eda`, the head plus one commit.

## Unit

U0c, files and `git diff --stat origin/main...HEAD`:

```
 .github/workflows/ci.yml                           | 324 ++++++++++++-
 .github/workflows/gate-sweep.yml                   |  53 +++
 dev/audit/harnesses/r10_ci_layout_u0c/ci_map.json  |  49 ++
 dev/audit/harnesses/r10_ci_layout_u0c/mutants.py   | 144 ++++++
 .../harnesses/r10_ci_layout_u0c/sweep_map.json     |  12 +
 dev/audit/harnesses/r10_ci_layout_u0c/unitcheck.sh |  41 ++
 tests/closure.py                                   |   3 +
 tests/entities.py                                  | 503 +++++++++++++++++----
 8 files changed, 1032 insertions(+), 97 deletions(-)
```

Production: `.github/workflows/ci.yml` (replaces PR 0's stub), `.github/workflows/gate-sweep.yml` (new, no `concurrency:`), `tests/closure.py` (`gate-sweep.yml` joins `GATE_FILES`, because it re-runs `gate` jobs and so decides which verdict stands at a head, as `ci.yml` does). Tests: `tests/entities.py`. Harnesses: `dev/audit/harnesses/r10_ci_layout_u0c/` (`unitcheck.sh` + two maps, `mutants.py`), inert under the existing `dev/audit/harnesses/` prefix (`closure.is_inert`: True).

`tests/entities.py`, every edit:
- the stub pin (`_ci_stub_defects`) is replaced by the umbrella pin `_ci_umbrella_defects` and the sweep pin `_gs_defects`, each with in-file plants;
- `_forgery_defects` refuses `statuses: write` at workflow and job level (carry 8) and requires exactly one `gate` reporter in `ci.yml`, the job `gate`, with plants for both;
- `_CC_TWIN_ROUTE["ci.yml"] = "per-run"`;
- the `edited` pin lists `ci.yml` with its 13 jobs;
- `_rc_producer` skips a `uses:` job (a caller reports `<id> / <job>`, DESIGN-P2 2.1), so `ci.yml`'s `hassfest` caller is not read as the producer of the bare context `hassfest`;
- the contract follower's watched list (`_PR_WORKFLOW_NAMES`) excludes `CI`: its `pr-contract` needs every unit of its own run;
- `_PT_EXEMPT` gains `tools/ci/gate.py` and `tools/ci/prelude.py` (reason in the entry; the arm is carried below). This one is outside my row's named pins. It is the least change that keeps the head-copy pin true once a workflow runs those programs with a token: arming them means editing `tests.yml`, which is U5's file.

Design decisions that depart from the DESIGN-P2 2.2 sketch, each with its reason:
- **Unit guards key on the prelude's `workset`, not on `kind`.** The guard is `contains(format(' {0} ', needs.prelude.outputs.workset), ' <id> ')`. A2 item 2 added the `kernel-points` and `label` kinds. Under those kinds the sketch's `pr != '' && kind != 'review'` runs `arch-score` and `pr-contract` on a `labeled` event, but `prelude.workset('label', pr)` is empty. The pin derives each caller's guard from `prelude.workset` for every modelled event, and plant "a unit guarded on the event, not the workset" (the sketch's own guard) is refused.
- **`run-name` gains the two label arms**, so it renders `prelude.title(*prelude.derive(event), github.sha)` for every event. On `merge_group` it reads `pr=- base=-`, because no expression can cut the PR number out of the queue ref. No reader takes a source from a queue run's title: `gate.py` builds its own run's title, and a queue head has one run.
- **`refresh` holds `contents: read` and `pull-requests: read` beside `actions: write`.** The sketch says `{ actions: write }`, but the job checks out, and `gate.py --refresh` reads `pulls/N`.
- **`kernel-points` is a caller** (U11's unit, A2), so the caller set is `gate.py`'s `UNITS` plus `kernel-points`.
- **YAML anchors are not used.** Each job's restore is inline, because I have not measured Actions' support for anchors.

## Interface

What U1-U11 build against. Every callee declares `on: workflow_call` with exactly the inputs below, each `type: string` and optional (`default: ""`). GitHub refuses a run whose caller passes an input the callee does not declare.

| caller job (id == file stem) | `with:` | `secrets:` | caller grant (caps the callee) | runs when |
|---|---|---|---|---|
| `tests` | `gate_scope`, `pr`, `base`, `head`, `recheck`, `no-skip` | `CLOSURES_PUSH_TOKEN`, `HPO_RUNS_PEM`, `HPO_RUNS_APPID` (until M-3) | `contents: write`, `actions: write`, `pull-requests: read` | workset names `tests` |
| `codeql` | `legs` | – | `contents: read`, `security-events: write` | workset names `codeql` |
| `governance` | – | – | `contents: read`, `pull-requests: read`, `issues: write` | workset names `governance` |
| `hassfest` | – | – | `contents: read` | workset names `hassfest` |
| `validate` | – | – | `contents: read` | workset names `validate` |
| `kernel-points` | `pr`, `base`, `head` | – | `contents: read` | workset names `kernel-points` |
| `arch-score` | `pr`, `base`, `head` | – | `contents: read`, `pull-requests: read` | workset names `arch-score` |
| `budget-raise-gate` | `pr`, `base`, `head` | – | `contents: read`, `pull-requests: read`, `issues: read` | workset names `budget-raise-gate` |
| `pr-contract` | `pr`, `base`, `head` | – | `contents: read`, `checks: read`, `pull-requests: read`, `security-events: read`, `actions: read` | `!cancelled()` and workset names `pr-contract` |

Values:
- every `with:` key `k` reads `${{ needs.prelude.outputs.k }}`, except `recheck` and `no-skip`, which read `${{ inputs.k }}` (empty on every event but a dispatch);
- `legs` is a JSON object `{"actions"|"javascript-typescript"|"python": "skip"|"analyze"}`. U3's handoff `0f7f2608` reads it as `fromJSON(inputs.legs || '{}')[matrix.language]`, which is compatible;
- `gate_scope` is `auto`, or `full` on `push`;
- `pr`, `base` and `head` are `prelude.derive`'s PR number, base ref NAME and head SHA (empty `pr`/`base` on `push` and on a dispatch naming no PR).

Inside a called workflow, `github.event_name` and `github.event` are the caller's.

**Prelude outputs**, `needs.prelude.outputs.*`: `kind`, `pr`, `base`, `head`, `gate_scope` (prelude.py's `scope`), `legs`, `workset` (space-separated, sorted). A failed prelude leaves each empty, which skips every unit, and `gate` then FAILs `prelude: failure`.

**`needs:` graph**:
- `prelude` → each of the 9 callers;
- `pr-contract` needs `[prelude, tests, codeql, governance, hassfest, validate, kernel-points, arch-score, budget-raise-gate]`;
- `gate` needs `[prelude]` + all 9 callers, `if: ${{ !cancelled() }}`;
- `refresh` (`pull_request`/`pull_request_review` only) and `cancel-superseded` (non-bot same-repo `pull_request` only) need nothing.

**Check names**:
- `<caller id> / <callee job name>`, e.g. `tests / fast (3.14)`, as `tools/ci/gate.py` `REQUIRED` names them;
- the one required check is `gate`;
- a callee job's `name:` must keep rendering the names `gate.py` `UNITS` lists.

**Block for the probe cut**: all callers sit between `  # >>> units: …` and `  # <<< units` in `ci.yml`. The pin refuses a caller outside it. A per-unit probe keeps prelude, refresh and gate plus its own caller, and drops the rest from `gate`'s and `pr-contract`'s `needs:`.

**`run-name`**: `CI <kind> pr=<n|-> base=<ref|-> sha=<github.sha>`, `prelude.parse_title`'s grammar.

**Triggers**:
- `pull_request: [opened, synchronize, reopened, edited, labeled]`;
- `pull_request_review: [submitted, edited, dismissed]`;
- `push: [main]`;
- `merge_group: [checks_requested]`;
- `workflow_dispatch` with inputs `pr`, `base`, `recheck`, `no-skip`;
- `concurrency: CI-${{ github.run_id }}`, `cancel-in-progress: false`.

**`gate-sweep.yml`**:
- `name: Gate sweep`, one job `sweep`, triggered by `workflow_run` of `["CI"]` with `types: [completed]`;
- grant `actions: write`, `contents: read`, `pull-requests: read`; no `concurrency:`;
- runs `python3 -I tools/ci/gate.py --sweep --run "$RUN_ID"` from the default branch's commit.

## Static map

`sh dev/audit/harnesses/r10_ci_layout_u0c/unitcheck.sh` runs `archive/probe/design-ci-rev4:measure/rev/unitcheck2.py static`:
- for `ci.yml`, BEFORE is `origin/main`'s `ci.yml` (the stub), mapped as a new file: `ci_map.json` drops the three `stub|` rows, gains all 37 rows, and changes `|triggers`;
- for `gate-sweep.yml`, which main lacks, BEFORE is the empty document `{}`: `sweep_map.json` gains 4 rows and changes `|floor` and `|triggers`.

```
ci.yml head:          STATIC rows 2->39 lost 0 gained 0 changed 1 (mapped 1) misplaced 0 rc 0
gate-sweep.yml head:   STATIC rows 2->6 lost 0 gained 0 changed 2 (mapped 2) misplaced 0 rc 0
plant, an unmapped job added (want rc 1):   STATIC rows 2->42 lost 0 gained 3 changed 1 (mapped 1) misplaced 0 rc 1
plant, gate's checkout deleted (blind, reads rc 0):   STATIC rows 2->38 lost 0 gained 0 changed 1 (mapped 1) misplaced 0 rc 0
plant, a caller's with: changed (blind, reads rc 0):   STATIC rows 2->39 lost 0 gained 0 changed 1 (mapped 1) misplaced 0 rc 0
```

The instrument's limit on this unit, measured by the last two lines: a file mapped as new has every row `gained`, so the static half refuses only an unmapped addition. A gained row deleted (gate's checkout) and a caller's `with:` changed both read rc 0. `unitcheck2` hashes no `uses:`, `with:` or `secrets:` of a job, so this blind spot holds for every caller in `ci.yml`, not just for a new file. The control for both is `tests/entities.py`'s umbrella pin, which refuses each (plants "shallow gate checkout" and "a caller handed another input's value"). Carry: R10-CI-LAYOUT-P2

## Controls

**Failing first.** The new pins were run against `origin/main`'s workflows, with this head's `tests/entities.py` copied into a worktree of `fef4a1351`, through a one-off block runner. It execs exactly the text of `tests/entities.py` from `# Forgery (DESIGN-P2 2.1, rev1 item 12(b))` to `# --- the lane-skip instrument (R9-CI-SKIP)`, with a stand-in `R.check` that prints ok/FAIL. All three are red there. The forgery pin reads `defects=['ci.yml: jobs [] report `gate`, not exactly the job `gate`']`. The umbrella pin names the triggers, the types, the concurrency, the callers, the missing units block and the needs. The sweep pin names the triggers, jobs, permissions, checkout and program step. At this head all three are green.

**Carry 8, failing first, on main's own reader.** A one-off probe execs `_forgery_defects`, cut from the given `tests/entities.py` (from `def _forgery_defects(` to the next double blank line), over three single-workflow plants: `statuses: write` at the top, `statuses: write` on a job, and `statuses: read` on a job (the null):

```
--- origin/main's entities.py
workflow statuses: write: []
job statuses: write: []
null: statuses: read: []
--- head's
workflow statuses: write: ['x.yml: top grants statuses: write']
job statuses: write: ['x.yml: j grants statuses: write']
null: statuses: read: []
```

**In-file plants** (`tests/entities.py`; each must be named, or its check is red):
- **Forgery**: a `gate` job id outside `ci.yml`; a job named by an expression; `checks: write` on a job; `statuses: write` on a job; `statuses: write` on the workflow; `write-all`; no top-level permissions; a second `gate` reporter in `ci.yml`; no `gate` in `ci.yml`; `gate` granted `statuses: write`.
- **Umbrella**: run-name without the labeled arms; run-name without `sha=`; no `merge_group`; `labeled` dropped; a group per PR; `gate` skippable on `merge_group`; `gate` skipped when the prelude fails; a unit guarded on the event, not the workset; a caller handed another input's value; secrets inherited; a caller off its stem; `gate` not needing a unit; a shallow gate checkout; an output prelude.py never prints.
- **Sweep**: keyed on the exit code; a crash read as done; a concurrency group; the PR's head checked out.

The sweep pin RUNS the step's own text under bash, with a stand-in `python3` printing each outcome. Seven cases: `SWEEP-DONE` at rc 0 and at rc 1 (the "never the exit code" case), `SKIP`, `RATE-LIMITED` after a re-run at rc 1 and alone at rc 0, a traceback, and empty output. Each must give the step's rc and its `::error title=RATE-LIMITED::` / `::error title=sweep failed::` annotation.

## Null control

The real tree passes: the full suite, `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head, run as `mutants.py M0` (its line under `## Mutation proof`). That harness passes M0 only when exactly the `KNOWN_RED` check fails (`1 of 2400`) and it is among the FAIL lines. The one red is the `policy_lint` interaction under `## Red checks`, at this head by design.

## Mutation proof

`python3 dev/audit/harnesses/r10_ci_layout_u0c/mutants.py --jobs 3` runs one detached worktree per mutant, the full `tests/entities.py` in each, and requires the aimed check among the FAILs. M0 must fail nothing outside `KNOWN_RED`. M6 mutates the pin itself, not the workflow: the forgery reader forgets `statuses`.

```
M0 PASS rc=1 | 1 of 2400 ENTITY CHECKS FAILED | aimed red: []   (at d22b5f303)
M1 KILLED rc=1 | 2 of 2400 ENTITY CHECKS FAILED | aimed red: ["the CI umbrella: …"]
M2 KILLED rc=1 | 2 of 2400 ENTITY CHECKS FAILED | aimed red: ["the CI umbrella: …"]
M3 KILLED rc=1 | 2 of 2400 ENTITY CHECKS FAILED | aimed red: ["the CI umbrella: …"]
M4 KILLED rc=1 | 3 of 2400 ENTITY CHECKS FAILED | aimed red: ["the CI umbrella: …", 'a superseded long-job pull-request run is cancelled; …']
M5 KILLED rc=1 | 2 of 2400 ENTITY CHECKS FAILED | aimed red: ["forgery: …"]
M6 KILLED rc=1 | 2 of 2400 ENTITY CHECKS FAILED | aimed red: ["forgery: …"]
M7 KILLED rc=1 | 2 of 2400 ENTITY CHECKS FAILED | aimed red: ["gate-sweep.yml: …"]
M8 KILLED rc=1 | 2 of 2400 ENTITY CHECKS FAILED | aimed red: ["gate-sweep.yml: …"]
M9 KILLED rc=1 | 3 of 2400 ENTITY CHECKS FAILED | aimed red: ["gate-sweep.yml: …"]
M10 KILLED rc=1 | 2 of 2400 ENTITY CHECKS FAILED | aimed red: ["the CI umbrella: …"]
RESULT survivors=0   (M1-M10 at a82736d35)
```

The commit between the two heads changes only the harness: `git diff --stat a82736d35 d22b5f303` lists `mutants.py` alone.

## Figures

**Replays over `tools/ci/gate.py`** (unchanged by this unit), `python3 dev/audit/harnesses/r10_ci_gate_core.py replay|sim [--model]`:

```
gate_replay2.py over tools/ci/gate.py: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt
gate_replay2.py over the MODEL: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt
gate_sim.py over tools/ci/gate.py: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_sim.txt
gate_sim.py over the MODEL: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_sim.txt
```

**Scoped gate.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL -- every test script runs`, because `.github/workflows/ci.yml changes the gate itself`. CI owns that run (`fixer.md` step 5). Locally, under `PATH=/opt/hpo/venv-ci/bin` (Python 3.14.7) and `PYTHONPATH=tests/hastub`, `run.sh`'s `run_always` lines and the scripts this diff edits:
- `tests/env_drift.py --claims-only fef4a1351`: rc 0;
- `tests/closure.py selftest`: rc 0;
- `tests/layout.py`: rc 0;
- `tests/harness_headers.py`: rc 0 (`ALL 109 HARNESS HEADER CHECKS PASSED`);
- `tests/structure.py`: rc 0 (`STRUCTURE RATCHET PASSED`);
- `tests/entities.py`: above.

**Hygiene**:
- `python3 tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries`;
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries`;
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `87 self-testing, 87 wired, 0 unwired`, rc 0;
- `tools/pr/ci_predict.py --base origin/main`: `no closures or fast red predicted against fef4a1351db3`.

No new self-test, no new push site (`PUSHERS` unchanged), no mutants in `r10_seat_selftests_mutants.py`: this unit adds no instrument.

## Live checks owed

All on a draft probe PR from `ci-probe/<…>` cut from `handoff/r10-ci-layout-p2-u0c-probe` (`65f112ec51dfa1f3d1617dda2bac74adab394eda`), App-pushed, over P2a on main.

What the probe commit changes, and why:
- `ci.yml` is cut to `prelude` + `probe` (calls the new `.github/workflows/probe.yml`, one job `probe` running `true`) + `refresh` + `gate`;
- `cancel-superseded` is dropped;
- **every base restore is removed**, so the probe runs its OWN `tools/ci/`;
- `gate.py`'s `UNITS`/`REQUIRED` and `prelude.py`'s `CODE_UNITS`/`BODY_UNITS` are cut to `probe / probe`.

Without the restore removal, main's full `REQUIRED` judges and every run FAILs ABSENT.

Two consequences on the probe ref:
- `gate.py`/`prelude.py` `--self-test` read red (27 checks: 7 and 1 failed), and so do the entities umbrella pins, by construction;
- main's standalone workflows also fire on the probe PR's `pull_request` events.

Offline, the cut predicate gives `gate.gate` = PASS for `probe / probe` success, `probe / probe: failure`, `SKIPPED` and `ABSENT` for the first three perturbations' shapes.

Each item below is the exact edit or action the coordinator applies:
1. **Baseline**: open the draft PR. The `pull_request` `opened` run's `gate` is `success` and its summary says `PASS`.
2. **Forced red → FAIL**: in `.github/workflows/probe.yml`, `      - run: "true"` → `      - run: "false"`; push. `gate` fails, `FAIL probe / probe: failure (this run)`. Revert and push.
3. **`if: false` → FAIL SKIPPED**: in `probe.yml`, under `  probe:` add `    if: false`; push. `gate` fails, `FAIL probe / probe: SKIPPED (this run)`. Revert and push.
4. **Unit removed → FAIL ABSENT**: in `ci.yml`, delete the `  probe:` caller job (the 10 lines between `# >>> units` and `# <<< units`) and change `gate`'s `needs: [prelude, probe]` → `needs: [prelude]`; push. `gate` fails, `FAIL probe / probe: ABSENT (this run)`. Revert and push.
5. **Edit 1 s after push (item 1)**: push a commit, then 1 s later PATCH the body (`ci_probe.py`). Two runs: `code` and `edit`. The edit run's prelude waits for the code run, both complete, neither is cancelled, and the edit run's `gate` PASSes taking `probe` from the code run (its summary names `run <id>`).
6. **M-1**: for every run above, `display_title` equals the rendered `run-name` (`CI <kind> pr=<n> base=main sha=<github.sha>`). That includes one run cancelled while pending: dispatch twice and cancel the second while `queued`.
7. **`sha=` token**: a `pull_request` run's `display_title` `sha=` equals the test merge commit (`refs/pull/<N>/merge`).
8. **M-3(a)**: whether an App push, and a `GITHUB_TOKEN` push, each leave a held `ci.yml` run (`action_required`).
9. **M-4**:
   - the checks read `probe / probe`;
   - a **skipped caller's** check name: record whether a `uses:` job skipped by its `if:` writes a bare `probe` check run;
   - `event_name` and `event` inherited by the callee;
   - the caller's grant capping the callee: read each job's "Set up job" token headers;
   - the callee floor (`contents: read`);
   - queue latency of a call.
10. **M-5**:
    - (a) a throwaway twin `ci.yml` with `concurrency: {group: "CI-${{ github.event.pull_request.number }}", cancel-in-progress: true}`: re-run a completed run's `gate` while a newer run of that group is in progress, and read through the runs API whether the newer run is cancelled;
    - (b) on this `ci.yml`, the same re-run while a newer run at the head is in progress: the newer run is unaffected, and the attempt's group holds only its run.
11. **M-6**: `tools/audit/seat/sweep_driver.py`, once `--nochain` and once `--chain`:
    - an edit while a code run is in flight, then a review while the code run's refreshed `gate` attempt is not completed;
    - the review run's green `gate`'s sweep logs that attempt polled (and re-run if red);
    - every `gate` at the head ends green;
    - record each attempt's read-to-completion gap and the status values a re-run `gate` passes through.
12. **M-7**: list an in-flight run's jobs with `filter=latest` while `probe` runs; record whether `gate` appears before its needs finish.
13. **Fork**: `gate.py` driven with a `pulls/N` whose `head.repo.full_name` differs FAILs, offline already (P2a self-test). If the probe can reach one, a fork PR's `gate` FAILs `its head is not in this repository`.
14. **`merge_group`**: if the probe can enter a merge queue, `gate` reports on the queue commit and its `if:` did not skip.

The sweep's trigger path (`workflow_run` firing for `CI`) is not exercisable before merge (DESIGN-P2 section 7, step 3a).

## Wiring

- **None for workflows or entities beyond this diff.**
- **For the coordinator (P2b assembly)**: callee units must add their `workflow_call` inputs exactly as in `## Interface`. `kernel-points.yml` (U11) must declare `pr`, `base` and `head`, and `codeql.yml` (U3) already declares `legs`.
- **For U9b**: on the assembled tree, `tests/entities.py`'s `_EDITED_FILES` expectation loses `pr-contract.yml`, `budget-raise-gate.yml` and `arch-score.yml` once U6, U7 and U8 drop `edited` from them. `_CC_TWIN_ROUTE` loses them likewise. `_PR_WORKFLOW_NAMES`/`_crr_defects` go when U10 deletes `pr-contract-rerun.yml`.

## Red checks

- **main's ancestry**: at `origin/main` `fef4a1351` (`gh api commits/<sha>/check-runs?filter=latest`, 2 pages, 163 runs), no check run concluded `failure`; 27 `rerun-stale-contract` runs concluded `cancelled` (that follower's head-keyed `cancel-in-progress` group, by design). Root-cause trigger: not fired by this branch.
- **At this head, locally, by design**: `tests/entities.py` check "the template arm turns the acceptance red on a template that fails its own contract (and the real template keeps it green)". The real template reads rc 1 because `tools/policy/policy_lint.mjs` (line 3897) finds the contract's workflow as the one file matching `\n  pr-contract:\n`, and `ci.yml`'s caller job `pr-contract` matches too ("FIXTURE VACUOUS: .github/workflows/(2 files define pr-contract)"). The same reader makes CI's `policy-docs` red, and **`policy-docs` runs the BASE's copy**, so no edit in P2b can clear it on P2b's own run (see ESCALATE). Cheaper detector: this check is that detector; it ran locally in 7.5 min and named it before any push. Carry: R10-CI-LAYOUT-P2

## P2a defect

None fixed.

One contract deviation is recorded, not fixed. Contract item 3 says entry points print `PASS` / `FAIL <reason>` / `RATE-LIMITED` as stdout's first token. `gate.py --sweep` (U0b's `sweep.py`) prints `SKIP …`, `SWEEP …`, `SWEEP-DONE …` or `RATE-LIMITED …`, and never `PASS`, with rc 1 for both a rate limit and a crash (#2622's forward-carry). `gate-sweep.yml` therefore keys on the LAST output line's first word over that real vocabulary. The first line would miss a rate limit that follows a re-run (pinned case 4). Changing sweep.py's words is U0b's file and not needed for soundness. Carry: R10-CI-LAYOUT-P2

## Forward-carry

- **The `policy_lint` deadlock**: `tools/policy/policy_lint.mjs` must recognise a `uses:` caller as no definition of the `pr-contract` job, and that fix must be on `main` BEFORE P2b, because `policy-docs` restores the reader from the base. Measured above: `node tools/policy/policy_lint.mjs` at this head rc 1, at `origin/main` rc 0. Carry: R10-CI-LAYOUT-P2
- **The head-copy arm for the umbrella's programs**: `tools/ci/gate.py` and `tools/ci/prelude.py` now run base-restored with a token, and `_PT_EXEMPT` names them because `graders-head-copy` lacks `actions: read` and `pull-requests: read`. A changed `gate.py` first runs under the Actions token on main (#1721's class) until an arm with those grants lands. The owner is U5 (`tests.yml`). Carry: R10-CI-LAYOUT-P2
- **The static null control's caller blind spot**: the design's per-unit static half (tag `archive/probe/design-ci-rev4`, `measure/rev/`) hashes no `uses:`, `with:` or `secrets:` of a job, so the coordinator's per-unit re-run against current main cannot see a caller's inputs change. The entities umbrella pin is the control. Carry: R10-CI-LAYOUT-P2
- **A skipped `uses:` caller's check name** is unmeasured (live item 9, M-4). If it is the bare caller id, then until the ruleset cut-over an edit run would write skipped `hassfest`/`pr-contract`/`budget-raise-gate`/`arch-score` check runs under the 17 old context names. That is moot only because P2b lands with the ruleset PUT. Carry: R10-CI-LAYOUT-P2
- **`dev/audit/harnesses/r10_ci_layout_p0_mutants.py` M1/M2 no longer apply** (its stub substitutions match nothing at this head). That is a record of PR 0's proof, and stays as written. Carry: dismissed: a recorded measurement, not an instruction

## Friction

none
