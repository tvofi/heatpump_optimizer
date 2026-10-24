# R10-CI-LAYOUT: execution plan for the CI transition

Planning seat, read-only. Tree: `origin/main` at `c3530277` (2026-10-19 07:39Z). Roster:
`origin/handoff/audit-r10-roster`. Approved design: `probe/design-ci-rev4` (`1371a0a6`,
DESIGN-P1.md and DESIGN-P2.md), approved by `probe/design-ci-review5` (`afc00bfe`). Copies
are in `ev/design/`. This plan does not redesign the umbrella. It decides packaging, order,
timing and controls so the group lands with the fewest CI cycles, recarries and owner
steps. Where it changes something the approved design fixed, it says so and names who
approves the change (section 6).

`EV` below is `/Users/timmalmstrom/hpo-orch/r10s3/plans/ci-layout/ev`. Every figure names
the file it comes from. Each file is printed by a script in `EV`, run over read-only GETs
(`sh EV/fetch.sh EV`, then `sh EV/fetch2.sh EV`). **(est.)** marks a figure that was not
measured.

---

## 0. What the measurements change about the brief

1. **The approved design never budgets REST calls. As written, its polling alone could
   go past the limit that broke CI this morning.** At 07:46:36Z `validate-hacs` read
   "API rate limit exceeded for installation", and `rerun-stale-contract` was refused the
   same way at 07:46:43Z (`EV/incident_ratelimit_lines.txt`). In the 07Z hour the
   repository created **281 workflow runs**: 122 PR-event, 120 `workflow_run`, 30 push,
   8 dispatch, 1 schedule (`EV/allruns_by_hour.txt`). Revision 2 of the design has
   verdict preludes poll for earlier runs, measured at **1325 s of waiting per head**
   (its own `verdict_wait.txt`: 8.10 runner-hours over 22 heads). The design gives no
   poll interval for that wait. At 5 s (the interval it uses for the sweep), and at the
   measured peak of 10 code heads per hour, the prelude alone makes **about 2651
   calls/h**. GitHub documents the `GITHUB_TOKEN` limit as 1000 per hour per repository
   (not measured here). At 60 s the figure is about 221/h (`EV/api_model.txt`; a model
   from measured inputs, assumptions named in `EV/api_model.py`). This is new design
   item **A1** (section 6). It must be settled before U0 is dispatched, because U0 ports
   `prelude.py` and `gate.py`.
2. **A ninth PR workflow is about to land, and the design does not cover it.** Open PR
   #2368 (R10-PUMP-MODEL D2, `APPROVED`, `CLEAN`) adds `.github/workflows/kernel-points.yml`
   (`pull_request: [labeled, synchronize]`, label-gated, never required). It also adds
   `"Kernel points"` to `pr-contract-rerun.yml`'s `workflow_run` list
   (`EV/open_pr_ci_files.txt`, `EV/pr2368_kernel-points.yml`). PR 2 deletes
   `pr-contract-rerun.yml` on the premise that every check at a PR head comes from the
   umbrella. A standalone `kernel-points.yml` breaks that premise. This is design item
   **A2**.
3. **Main's push runs are already red, on a job outside this group, and the red blocks
   stamps.** 9 of the last 10 main pushes have a red Tests run. `ci-ratchet` failed on
   all 9 (`GREW critical_path_minutes: 58.65 (budget 54.825)`,
   `GREW script_runs_per_push: 73 (budget 68)`), and `record-autofix` and Governance
   `record` also failed on 3 (`EV/main_push_reds.txt`, `EV/logs/ci-ratchet_*.log`).
   `stamp.py` rule 2 requires a successful Tests push run at HEAD (`stamp.py:547-566`),
   so the stamp is blocked today. No open issue names it (`EV/issues_ratchet.json`) and
   no roster group owns it (`EV/roster_open_groups.txt`). PR 1 does not fix it: on a
   push, `fast` is the critical path and W1 leaves `fast` alone (DESIGN-P1 2(c)). Two
   consequences:
   - "PR leaves main green" has to be judged as **no new failing job on main's push run,
     compared with the base's push run** (a set comparison), not as "the run is green";
   - the red should be dispatched now, outside this group (section 4).
4. **Recarries, not first runs, are what make PRs slow.** The 5 most recent fix PRs took
   3-9 CI heads each, median 7, and a median 15.6 h from first CI to merge, about 2 h
   per head (`EV/pr_lifetimes.txt`). 62 of their 116 commits are merges of main
   (`EV/pr_commit_kinds.txt`). Main moved 10 times in 3 h 20 min this morning, and 5 of
   those 10 moves were automatic record PRs (`EV/main_last12.txt`). Each avoided head
   saves about 2 h. This drives the ordering in section 4.
5. **W1 saves more on today's PR runs than the design measured on 2026-10-18.** I ran
   the design's own `c1_counterfactual.py` over today's 6 completed fix-PR Tests runs.
   The median gain is **656-777 s** (bare cost 480-239.1 s), with 1 of 6 runs slower,
   by up to 409 s (`EV/c1_today_filtered.txt`). The design reports 232-342 s on 24 runs
   (DESIGN-P1 2(c)). n=6 is small, so this plan uses the range 232-682 s.
6. **The R-3 owner action is already settled by a read, so it costs tvofi nothing.**
   DESIGN-P1 R-3 asked tvofi to confirm the `ledger` and `record-writer` environments'
   deployment-branch rules. Both have one branch policy, `main`, of type `branch`, and
   no other protection rule (`EV/raw/environments.json`,
   `EV/raw/env_ledger_branch_policies.json`, `EV/raw/env_record-writer_branch_policies.json`).
   GitHub's branch policies have no workflow-file dimension, so a job moved to
   `nightly.yml` on `main` is admitted.
7. **Two carry items are not CI-layout work, and they already have owning groups in
   wave 3.**
   - Carry 1 edits only `tools/pr/prepr.sh`. R10-PREPR-UNPINNED-RED owns that file (no
     owner gate, no workflow edit).
   - Carry 2 and R10-SEAT-SELFTESTS-CI are the same task in `governance.yml`, which is
     not a gate file. A PR there runs scoped CI, not FULL (`tests/closure.py:452-489`,
     where `GATE_FILES` lists `tests.yml` alone).
   - Carry 3 is a three-line restore-list fix in that same `governance.yml` job.

   Folding any of the three into the FULL, code-owned and policy-gated PR 1 or PR 2 adds
   review surface to the slowest PRs and saves nothing. Section 5 re-routes them.

---

## 1. Target layout and per-PR figures

This is the approved design's layout. It is unchanged except for A2 (`kernel-points.yml`).

| | today (measured, `c3530277`) | after PR 0 (stub) | after PR 1 | after PR 2 |
|---|---|---|---|---|
| workflow files | 13 (`EV/inventory.txt`), 14 once #2368 merges | +1 `ci.yml` (inert) | +`nightly.yml`, +`.github/actions/nightly-ha/` | `ci.yml` real; `pr-contract-rerun.yml` deleted; `budget-raise-gate-rerun.yml` → `gate-sweep.yml` (DESIGN-P2 2.1) |
| workflow runs started per code head (fix PR) | **12**: 11 `pull_request` + 1 review (`EV/measure.txt` A) | 12 | 12 | **1 code run + 1 per edit or review** (DESIGN-P2 4.3) |
| `workflow_run` runs | **431 in 3.73 h ≈ 115/h**, 103 of them with an executed job (`EV/workflow_run_per_title.txt`, `EV/measure.txt` D) | same | same | one `gate-sweep.yml` run per `CI` completion (≈ 2-3 per head, est.) |
| job records per code head | **48** (44 distinct names) (`EV/measure.txt` A, `EV/jobs_per_head.txt`) | 48 | **40**: −8, being `recheck-gate`, `mutation-nightly`, `mutation-ledger`, `mutation-ledger-push`, `slow`, `record-autofix`, `mutation-pin-plan`, `composed-proof` (DESIGN-P1 Totals) | ≈ 41 per code run: −1 `cancel-superseded`, −1 CodeQL `scope`, +`prelude`, +`refresh`, +`gate` (est., derived from DESIGN-P2 10) |
| jobs executed per code head | **33** (29 distinct) | 33 | **32**: `composed-proof` gone | ≈ 33 (est.: +`prelude`, `refresh`, `gate`; −2 above) |
| check runs per head | **49** (`EV/measure.txt` A) | 49 | ≈ 41 | ≈ 45-55 (est.). Check-run writes do not draw on the token's REST quota |
| API-consuming job executions per code head | **11**: `validate-hacs`, `arch-score`×2, `pr-contract`×2, `budget-raise-gate`×2, `env-matrix`, `nightly-status`, `closures`, plus 1 review-run `budget-raise-gate` (`EV/api_jobs_per_head.txt`) | 11 | 11 | ≈ 14 per head (est.: +`prelude`, `refresh`, `gate`), minus ≈ 2.8 executed `workflow_run` jobs per head |
| polling REST calls per head | ≈ 0 (no polling job on today's PR graph, est.) | 0 | 0 | **265 at 5 s, 133 at 10 s, 44 at 30 s, 22 at 60 s** for the prelude wait alone, plus the sweep's poll (worst 240 at 5 s) (`EV/api_model.txt`) |
| required contexts | 17 | 17 | 17 | **1** (`gate`, app 15368) |
| **PR critical path, median code-wave wall** | **2746 s** (n=5 fix heads, 1738-3224; ends at `Tests/composed-proof` 4 of 5) (`EV/measure.txt` A) | 2746 s | **≈ 2064-2514 s**: 2746 − W1's 232-682 s (`EV/c1_today_filtered.txt`, DESIGN-P1 2(c)) (est.) | **≈ 2124-2574 s**: +≈60 s umbrella tail (DESIGN-P2 3.3, est.; M-4 measures the call hop) |
| main push Tests wall | **3507 s median** (2655-4018, n=10) (`EV/push_median.txt`) | same | same (`fast` is the push critical path; DESIGN-P1 2(c)) | same plus the tail (est.) |

Per-job durations and queue times at today's heads are in `EV/measure.txt` section B. The
critical-path shape: `coverage` (median 1229 s) → `closures` (median 497 s scoped, max
1830 s) → `composed-proof`, which queues a median 570 s behind both. `CodeQL/Analyze
(python)` (median 630 s, max 1672 s) and `fast` (scoped median 249 s, max 3169 s) sit
off that path. After W1, the path becomes max(`fast`, `coverage`, `closures`, CodeQL
python).

**What PR 2 does for the incident.** The run count per head drops about 12× (12 PR runs
plus about 11.5 `workflow_run` runs per head, falling to about 3-5). The REST cost per
head goes **up or down depending on the poll intervals**, which the design leaves open.
A1 pins them. Without A1, the umbrella could exhaust the token at 2-3 code heads per
hour, a third of today's peak.

---

## 2. The PR sequence

**Decision: three small-to-XL PRs in this group, not two.** The two carries that are
pure `governance.yml` edits move to SEAT-SELFTESTS-CI, and carry 1 moves to
PREPR-UNPINNED-RED (section 5).

| PR | content | CI mode | gates | required set while it is open | after merge |
|---|---|---|---|---|---|
| **PR 0, the stub** | DESIGN-P1 step 5b alone: `.github/workflows/ci.yml` (`on: workflow_dispatch`, inputs `pr`/`base`/`recheck`/`no-skip`, `permissions: {}`, one job `stub` running `true`), its `entities.py` inert pin, `GATE_FILES += ci.yml` in `tests/closure.py` | FULL (it edits a gate file), plus one `closures-autofix` cycle (est.) | code-owned (`/.github/workflows/ @tvofi`, CODEOWNERS:37), approved under the mandate; not policy | 17, all produced. The stub writes no check at any PR head | 17. `gh workflow run ci.yml --ref probe/ci-layout-*` becomes possible, so the fan-out's live checks can start |
| **PR 1, phase 1** | DESIGN-P1 section 4 exactly, **less step 5b** (already on main) | FULL, plus a `closures-autofix` cycle (`tests/closure.py prune` before the first push) | code-owned and policy (`ci-autofix.md`, `defect-root-cause.md`, `rules_sync`), approved under the mandate | 17, all produced (DESIGN-P1 3; `entities.py:27701-27752` asserts producers) | 17. Dispatch `gh workflow run nightly.yml --ref main` at once (DESIGN-P1 2(a); `nightly-status` reads RUNNING/red for about 3.8 h, which blocks nothing) |
| **PR 2, the umbrella** | DESIGN-P2 sections 2, 4, 5, 9 and 10, assembled on `probe/ci-layout-all`, plus the addendum (A1, A2, A5) | FULL (it edits `tests.yml`, `ci.yml` and `closure.py`) | code-owned and policy (R-10, orchestrator §11, nudge, steward, template, web-fragments), approved under the mandate, plus **tvofi's ruleset PUT** | its head produces `gate` and not the 17 old names, so it **cannot merge under the 17**. That is why the cut-over sits exactly at its merge (section 3) | `[gate]` |

**Why three PRs, not two.** In the approved packaging the stub rides in PR 1, so no
`probe/ci-layout-*` ref can dispatch `ci.yml` until PR 1 merges (DESIGN-P2 10: "PR 1's
stub must be on `main`"). The live halves of U0-U4 and U6-U8 then all wait behind PR 1,
the group's longest PR (FULL, policy, likely 4-5 heads at about 2 h each, from
`EV/pr_lifetimes.txt`). As its own PR, the stub lands in about 3.5 h (est.) and the
fan-out's live work runs **in parallel with** PR 1. Section 7 puts the saving at about
6-8 h of critical path (est.). The cost is one more FULL cycle, which runs in parallel
with PR 1's build, and one more mandate approval. tvofi personally does nothing more.
The stub is already approved design content: only its packaging moves.

**Fallback if the design review refuses the split:** two PRs as approved. Section 7's
timeline then grows by the U0 live window (about 4 h) plus U1-U8's live windows (about
3 h). Nothing else changes.

**Required checks are satisfiable at every step.**
- PR 0 and PR 1 rename no job and add no `name:`. `nightly.yml` carries no required id
  (DESIGN-P1 3), so the 17 have producers at every PR head, on every event including
  `merge_group`.
- The only moment where a required context could lack a producer is between tvofi's
  PUT and PR 2's merge. During that window `gate` is produced at PR 2's head, which is
  the only PR allowed to merge. Section 3 keeps the window to minutes.
- The ruleset has `strict_required_status_checks_policy: false`
  (`EV/ruleset-23698884.json`), so no up-to-date requirement forces a recarry at the
  cut-over.

**No PR leaves main red.** "Red" is the set of failing jobs on main's push run after the
merge, compared with that set on the base's push run (`EV/main_push_reds.txt` is the
baseline shape). A PR may not add a failing job. This replaces "main is green", which is
false before this group starts (section 0.3).

---

## 3. The ruleset cut-over: one tvofi action, at one moment

**When.** All of these hold at once:
1. PR 2 has a merge verdict at head H, CI is green at H, and the mandate approval is at
   H.
2. The open-PR queue is drained: no other open non-draft PR, record PRs merged.
3. The orchestrator has declared the merge freeze (no train running, no dispatch of
   new openers).

The orchestrator tells tvofi a window in advance (#201 is the orchestrator's write).
tvofi runs the block below, and within the same minute the orchestrator runs
`merge_train.py run` on a single-entry queue `[PR 2 @ H]`.

**Before** (live read 2026-10-19, `EV/ruleset-23698884.json`), 17 contexts:
`fast (3.14)`, `browser`, `briefs`, `closure-scope`, `closures`, `typing`, `hassfest`,
`validate-hacs`, `policy-docs`, `wave-script`, `pr-contract`, `env-matrix`,
`Analyze (actions)`, `Analyze (javascript-typescript)`, `Analyze (python)`, `mutation`,
`budget-raise-gate` (integration 15368).

**After**, 1 context: `gate` (integration 15368). Everything else is byte-identical: the
`pull_request` rule (`require_code_owner_review: true`, `dismiss_stale_reviews_on_push:
false`), both `always` bypass actors, `strict: false`, `do_not_enforce_on_create: false`.
The 17 move into `gate.py`'s `REQUIRED` as `<stem> / <job>`, plus `arch-score /
arch-score` when the diff reaches `custom_components/` (D-2). They are recorded in
`required-contexts.json`'s `gate_required` (DESIGN-P2 7).

**The block** (PR 2's body stages it, re-derived from the live JSON at that moment;
dry-run tested now, see `EV/ruleset_dryrun.txt`: only `required_status_checks` differs,
everything else is `IDENTICAL`):

```sh
R=repos/tvofi/heatpump_optimizer/rulesets/23698884
gh api "$R" > ruleset-rollback-23698884.json
jq '{name,target,enforcement,conditions,bypass_actors,rules}
    | (.rules[]|select(.type=="required_status_checks")|.parameters.required_status_checks)
      = [{"context":"gate","integration_id":15368}]' ruleset-rollback-23698884.json > ruleset-gate.json
gh api -X PUT "$R" --input ruleset-gate.json >/dev/null
gh api "$R" | jq -S '{name,target,enforcement,conditions,bypass_actors,rules}' \
  | diff <(jq -S . ruleset-gate.json) - && echo READBACK-OK
```

Rollback, ruleset first and then the revert of PR 2 (DESIGN-P2 7):
`jq '{name,target,enforcement,conditions,bypass_actors,rules}' ruleset-rollback-23698884.json | gh api -X PUT "$R" --input -`.

U9 should land this as an in-tree instrument with `--dry-run` / `--apply` /
`--rollback` and a self-test over a saved JSON, as tools-live-in-repo requires. tvofi
then runs one command, and CI shows the dry-run.

**After the PUT** (orchestrator; DESIGN-P2 7 steps 3-5). Merge PR 2. Two things then run
in parallel:
- main's push run must show `gate` green, about 58 min (`EV/push_median.txt`);
- step 3a's trigger-path check on a draft probe PR from the new main, about 75 min
  (est.).

Unfreeze once both pass, or once the trigger-path rollback is in place. Because the
queue was drained, step 4 (merge main into every open PR) recarries nothing.

**tvofi's personal steps in the whole group: exactly this one.** Every PR approval is
the CODEOWNER session's under mandate 6175172275 (scope `all`, to 2026-10-28). Packaging
decisions fall under the R10 grant ("decisions = recommended"). R-3 needs no owner
action (section 0.6).

---

## 4. Ordering against the other open PRs and the merge train

Workflow PRs land by `merge_train.py run`, never by batch proof (orchestrator.md §11: "A
workflow ... change takes `run`"). A `run` recarries whenever main moved since the last
CI, and every recarry of a FULL PR costs about 58 min (est., using the push wall). Rules:

1. **Before PR 1's first push**, drain these:
   - #2368, which is approved and clean. It also brings `kernel-points.yml` to main, so
     A2 is designed against the real file.
   - R10-TRAIN-HOLD (#2302). It edits `record-autofix`'s automerge step in `tests.yml`,
     which PR 1 moves verbatim into `nightly.yml`. Landing it first means PR 1 carries
     it through the move, and `unitcheck2.py static`'s verbatim-move rows prove it. If
     it lands after PR 1, it is the move-PR silent-revert shape. Its hold ref also stops
     record PRs from moving main under PR 1's and PR 2's FULL runs.

   If TRAIN-HOLD is not ready when PR 1 is, PR 1 does not wait: TRAIN-HOLD re-targets
   `nightly.yml` after PR 1 (forward-carry into its brief before PR 1 merges).
2. **Merge every other ready PR first, then PR 1 alone.** When PR 1's verdict arrives,
   batch-merge whatever else is ready, then run `[PR 1]`: one recarry, one FULL, merge.
   Merging PR 1 first and the rest after would recarry each of the rest onto a gate-file
   change.
3. **Freeze CI-file edits by other groups from the moment the U-units cut their probe
   refs until PR 2 merges.** The files are `tests.yml`, `governance.yml`, `codeql.yml`,
   `hassfest.yml`, `validate.yml`, `pr-contract.yml`, `arch-score.yml`,
   `budget-raise-gate.yml` and `kernel-points.yml`. Each unit's static map is taken from
   main's file, and a later edit there is silently dropped when PR 2 assembles. The
   exceptions, ordered before their unit cuts its ref:
   - SEAT-SELFTESTS-CI (with carries 2 and 3) lands **before U4** cuts
     `probe/ci-layout-governance`;
   - PREPR-UNPINNED-RED (with carry 1) lands **before U9**, which edits the same
     `REDS_JQ` at `prepr.sh:935-938`.

   At assembly, U9 re-runs `unitcheck2.py static` against **current** main, so any edit
   that slipped through is refused, not lost.
4. **Forward carries into later groups' briefs** (finding-propagation; these are roster
   edits, which are the orchestrator's):
   - R10-REPLAY-LANE (wave 13) lists `nightly.yml` as a file. PR 1 creates it, and the
     `slow` lane lives there afterwards.
   - R10-REPLAY-SCOPED (wave 14) edits `tests.yml`, which after PR 2 is a
     `workflow_call` callee whose check names carry `tests / `.
   - R10-STAMP: `stamp.py` reads the `ci.yml` push run's `gate` after PR 2 (DESIGN-P2 9).
     Stamp before PR 1, or after PR 2's cut-over, never between PR 2's open and its
     merge.
5. **PR 2 goes at a wave boundary** (work-in-waves): after a drain and before the next
   wave's dispatch, so the cut-over recarries no open PR. Under the soft cap
   (`pr_cap.py`: 6 open, drafts counted), the fan-out's draft probe PRs count. Section 7
   keeps at most 4 of them open at once.
6. **Dispatch the `ci-ratchet` red now, as its own group** (fix it, or verify it
   independently, then file; out-of-scope findings get fixed). Call it
   `R10-CI-RATCHET-RED`: root-cause the growth of `critical_path_minutes` from at most
   54.825 to 58.65 and of `script_runs_per_push` from 68 to 73, and repair it, or bring
   the owner a re-record if no payment exists. It touches `tests/ci_budgets.json` and
   `tests/ci_ratchet.py`. PR 2 changes `ci_ratchet.py:177,185`, so that group lands
   before U9 cuts its ref. It also unblocks the stamp before PR 2.

---

## 5. Carry items: where each one folds, with its controls

| carry | folds into | why there | plant (must turn red) | null (must stay green) |
|---|---|---|---|---|
| 1. `prepr.sh` runs `tests/throwaway_git.py --check` | **R10-PREPR-UNPINNED-RED** (wave 3, `tools/pr/prepr.sh`, no owner gate) | the carry is owed "to the group that edits `tools/pr/prepr.sh`". That group does, scoped CI, not code-owned. Inside CI-LAYOUT it would wait about 20 h for PR 2 | a self-test under `tools/` with a planted raw `git init`: `prepr.sh` exits red naming the call, before any self-test runs | the unplanted tree: `prepr.sh` green, and the step's wall time printed beside it |
| 2. Fold the instrument self-tests no workflow runs (`merge_pr.sh --self-test` and others) into `governance.yml` | **R10-SEAT-SELFTESTS-CI** (wave 3, `governance.yml`; its brief already wires `tools/audit/seat/` self-tests) | same file and same goal. `governance.yml` is not a gate file, so scoped CI. Must land before U4 cuts its ref (section 4.3). The brief widens from `tools/audit/seat/` to all of `tools/`, as the carry asks | per added self-test, a mutant reddens its step. Enumerate by command: `git grep -l -e '--self-test' -- tools/` lists **70 files, 35 named in no workflow, 25 of those under `tools/audit/seat/`** at `c3530277` (`EV/selftest_enum.txt`; a literal match, so callers count too, and each file still needs a disposition: run in CI, or not and why) | the self-tests already in CI stay green and keep their step names. `instrument-self-tests` keeps its name and is not required, so the 17 do not change |
| 3. The wave-script restore list omits `stamp.py` and `delivery_status.py` | **R10-SEAT-SELFTESTS-CI**'s PR (same file, same lane) | a three-path edit in `governance.yml:624-690`, scoped. The derivation must be the importers' closure, not a hand list. A first-level import read already finds **a third missing file, `tools/audit/seat/merge_train.py`** (`EV/wave_script_restore_gap.txt`) | a planted divergence in each added file (`stamp.py`, `delivery_status.py`, `merge_train.py`): wave-script red. A closure-derivation mutant that drops one import: the derivation check red | the unplanted head reads `divergent=0` (the #2423 false `divergent=2` gone), and the restore list equals the derived closure |

The same rows need SEAT-SELFTESTS-CI's `owner_gate` corrected from `None` to code-owned
(`/.github/workflows/ @tvofi`), approved under the mandate.

**CI-LAYOUT keeps its own controls** (unchanged from the design):
- PR 1: `unitcheck2.py static` under DESIGN-P1 4's closed map, plus the runtime
  `stepset.py` pairs; `c1_consumers.sh HEAD` lists only the two fixture files.
- PR 2: the per-unit static and runtime halves; the combined control (DESIGN-P2 10); and
  the must-fix items N5-1 to N5-4 (roster brief).

**Two economies the design review should approve** (A4, A3):
- **One shared BEFORE twin.** The runtime null's BEFORE is "the same diff on main's
  layout". Main's layout does not depend on the unit, so U4, U6, U7 and U8 can share one
  BEFORE twin draft PR carrying a no-op diff (one docs line). Each unit's AFTER null run
  carries the same diff, and the unit-specific perturbations stay on each unit's own
  probe PR. That is four BEFORE twins fewer, about 4 × 12 runs per push (est.), and four
  open PRs fewer against the cap.
- **U5 stacked on PR 1's verdict head**, rather than waiting for PR 1's merge. U5's
  probe ref is cut from PR 1's verdicted head; PR 0's stub on main makes it
  dispatchable. If PR 1 recarries, the probe merges the same main. If PR 1's content
  changes after its verdict, U5 re-cuts.

---

## 6. Risks, rollbacks, and what the design review must approve before dispatch

**Addendum the design review must approve before any fixer is dispatched.** It is one
round of a short document and changes only what is listed here.

| id | item | blocks |
|---|---|---|
| **A1** | **REST budget.** Pin every poll the design adds: the prelude's verdict wait at ≥ 60 s with conditional requests (`If-None-Match`; GitHub documents that a 304 does not count, unverified here), `gate.py --sweep` at ≥ 15 s (40 polls in its 600 s bound), and `pr-contract`'s code-scanning wait at ≥ 15 s. U0 measures each API job's consumption as the `GITHUB_TOKEN` `/rate_limit` reading at job start and end (that endpoint is not counted). The combined control reports calls per head and the projection at 10 code heads/h; the merge rule is a projection ≤ 500/h, half the documented limit. The cost: a verdict run ends up to 60 s later, off the code run's critical path | U0, U6, U8 |
| **A2** | **`kernel-points.yml` (#2368).** Either a unit U11 (`workflow_call`, its caller guarded on the label, plus the `labeled` action given a kind), or a recorded exemption: it stays standalone and label-only, and `pr-contract` keys a re-read on its completion. Then the deletion premise of `pr-contract-rerun.yml` is restated to cover it. Recommendation: U11, because the exemption keeps a second `workflow_run` writer | U0 (kind derivation), U6, U9, U10 |
| **A3** | **Packaging**: PR 0 split out; carries 1-3 re-routed (section 5); U5 stacked on PR 1's verdict head | dispatch of PR 0 and PR 1 |
| **A4** | **Shared BEFORE twin** for the runtime null (section 5) | U4, U6-U8 |
| **A5** | **The merge train reads several `gate` runs.** `merge_train.py`'s `ci` step stops on any latest red check at the head. With one check suite per `CI` run, an older red `gate` (R-9's defer red) sits beside a newer green one. U9 changes the step to the binding reading M-2 measures, and the combined control runs `merge_train.py wait-ci` on such a head. DESIGN-P2 9 lists only `DISPATCH`, `PR_ONLY` and `--ignore-red` | U9 |
| **A6** | "Main stays green" means no added failing job on main's push run (section 2), given the `ci-ratchet` red that predates this group | every merge |

**Risks and rollbacks.**

| risk | how this plan meets it | rollback |
|---|---|---|
| R-API: the fan-out reproduces this morning's exhaustion (probe PR pairs each run 12 workflows) | A1; at most 4 probe PRs open at once; probe pushes paused while a merge train runs; the shared BEFORE twin. The tick greps failed-job logs for `rate limit exceeded for installation` as a cheap detector (est. cost: one log read per red API job) | stop probe pushes. Reds from a 403 are re-runs, not code |
| R-1 cut-over window (DESIGN-P2 R-1) | queue drained; PUT and merge in one minute | ruleset first, then revert PR 2 |
| PR 1's FULL plus `closures-autofix` cycle | `closure.py prune` before the first push; wait for the bot's `ci: re-record closures` and read its summary line | revert PR 1. The ruleset is untouched |
| R-2 pin-plan fold unexercised (DESIGN-P1 R-2) | `entities.py` wiring pins; live on the next refusing PR | one autofix cycle |
| nightly-status red window after PR 1 (R-4) | dispatch `nightly.yml` at merge; the train's default `--ignore-red nightly-status` | none needed; it blocks nothing |
| silent revert of a CI-file edit during the fan-out | section 4.3 freeze, plus `unitcheck2.py static` against current main at assembly | re-apply the dropped rows |
| R-7 `workflow_run` trigger path first runs after merge | step 3a inside the freeze | disable `gate-sweep.yml` and run `sweep_driver.py` (DESIGN-P2 7) |
| ratchet zero headroom (`structure_budgets.json`; the policy corpus caps for PR 1's and PR 2's policy text; `ci_budgets.json` for PR 2's `ci_ratchet` change) | `tests/structure.py` and `policy_lint.mjs` caps run before each push (fixer step), with payments found before a raise is proposed | a raise is a mandate decision only once no payment exists (CLAUDE.md rule 2) |
| `stamp.py` blocked by the `ci-ratchet` red | R10-CI-RATCHET-RED dispatched now (section 4.6) | PR 2 makes the stamp read `gate`, which does not list `ci-ratchet` |

**The roster's `owner_gate` text is stale.** It reads "NOT dispatchable until a design
review approves", but the review approved at round 5. It should read:

> Code-owned (`/.github/workflows/`, and `/.github/actions/` after PR 1, CODEOWNERS) and
> policy (PR 1: `ci-autofix.md`, `defect-root-cause.md` and `rules_sync`; PR 2: R-10's
> `pr-contract` change, `orchestrator.md` §11, `nudge.md`, `steward/SKILL.md`, the PR
> template, `web-fragments.md`). Each PR is approved at its merged head by the CODEOWNER
> session under mandate 6175172275 (scope `all`, to 2026-10-28). tvofi's own step: the
> ruleset 23698884 `required_status_checks` PUT at PR 2's merge (one action, staged in
> PR 2's body). The design was approved at round 5 (`probe/design-ci-review5`,
> `afc00bfe`, on rev4 `1371a0a6`). The plan addendum (A1-A6, this file) must be approved
> before dispatch. R-3 needs no owner action (environments read 2026-10-19).

---

## 7. Step timeline

T0 is the moment the addendum review is dispatched, assumed to be 2026-10-19 11:00Z.
Every duration is **(est.)** unless it cites a file. The anchors:
- scoped PR code wave: 46 min (`EV/measure.txt` A, median 2746 s);
- FULL: about 58 min (`EV/push_median.txt`, median 3507 s);
- review and recarry: about 2 h per head (`EV/pr_lifetimes.txt`).

The seat cap is 8; cloud units run at most 4 at once.

| # | step | starts after | duration (est.) | lane | ends ≈ |
|---|---|---|---|---|---|
| 0 | addendum review A1-A6 (opus reviewer) | T0 | 2-3 h | design | T+3 h |
| 0' | #2368 merges; R10-CI-RATCHET-RED and R10-TRAIN-HOLD dispatched; SEAT-SELFTESTS-CI (+carries 2, 3) and PREPR-UNPINNED-RED (+carry 1) dispatched | T0 | 4-8 h each, in parallel | other groups | T+4…8 h |
| 1 | **PR 0 stub**: build 0.5 h, FULL 1 h, autofix cycle 1 h, review 0.5 h, `run` merge | T0 (approved content); merge after 0 | 3.5 h | A | T+3.5 h |
| 2 | **PR 1** build (opus fixer) | T0 | 5-6 h | A | T+6 h |
| 2r | PR 1: FULL + autofix + review rounds (≈ 3 heads beyond the first) + one `run` recarry | 2, and TRAIN-HOLD merged | 6-7 h | A | T+13 h |
| 3 | U0 offline: `gate.py`/`prelude.py` ports, `gate_replay2`/`gate_sim` driving the port, `sweep_driver.py` with N5-1 | 0 | 4 h | B | T+7 h |
| 3l | U0 live: M-1, M-3(a), M-4 to M-7, the A1 `/rate_limit` reads | 1 and 3 | 4 h | B | T+11 h |
| 4 | U1, U2, U3, U6 (batch 1) | U0's interface (3) | 3 h | B, cloud ×4 | T+10 h |
| 5 | U4, U7, U8, U11 (batch 2); U4 after SEAT-SELFTESTS-CI merges | batch 1 | 3 h | B, cloud ×4 | T+13 h |
| 6 | U5 stacked on PR 1's verdict head | PR 1's verdict (≈ T+12 h) | 3 h | B | T+15 h |
| 7 | U10 | U5 | 1.5 h | B | T+16.5 h |
| 8 | U9 readers, plus the combined control on `probe/ci-layout-all` (events serial on 2-3 draft PRs, about 46 min per code run) | 5, 7, and PR 1 merged | 4.5 h | B | T+21 h |
| 9 | **PR 2**: assemble, push, FULL + autofix 2 h, review 3 h | 8 | 5 h | A | T+26 h |
| 10 | **cut-over**: drained queue, freeze, tvofi PUT, merge, push run ∥ step 3a, unfreeze | 9, at a wave boundary | 1.5 h | A | **T+27.5 h** |

That lands about 2026-10-20 14:30Z, ahead of the round-10 closure on 2026-10-21. The
two-PR fallback moves step 3l behind step 2r (T+13 h), and step 10 to about T+34 h.

**What can run in parallel:**
- steps 0, 0', 1, 2 and 3 from T0;
- steps 4 and 5 beside 2r;
- step 6 overlaps 5.

Steps 8, 9 and 10 are serial. The critical path is 0 → 3 → 3l/4/5 → 8 → 9 → 10, with
PR 1 (2r) gating 6 and 8.

**Expected CI cycles (est.):**
- PR 0: 2 FULL (the first push and the autofix);
- PR 1: about 5 FULL (the first push, the autofix, 2 review rounds, 1 recarry at the
  merge);
- PR 2: about 4 FULL;
- the units: scoped dispatches.

Without the drain-first rule (section 4.2), every intervening merge adds one FULL to
PR 1 and PR 2; at this morning's rate that is about 2 per CI hour (`EV/main_last12.txt`).

---

## Enumerators

| command | prints |
|---|---|
| `sh EV/fetch.sh EV`; `sh EV/fetch2.sh EV` | `EV/raw/` runs, jobs (`filter=all`) and check runs at main's last 10 heads, the open PR heads and the 10 merged PR heads; branch Tests runs |
| `python3 -I EV/measure.py EV` | `EV/measure.txt`: per-head runs, jobs and checks; job durations and queue; heads per PR; `workflow_run` per hour; main push runs |
| `python3 -I EV/inventory.py <tree>` | `EV/inventory.txt`: workflows, triggers and jobs; literal API call sites (a static lower bound) |
| `python3 -I EV/c1_counterfactual.py EV/c1raw --boost B` (the design's instrument) | `EV/c1_counterfactual_today.txt`, `EV/c1_today_filtered.txt` |
| `python3 -I EV/api_model.py EV` | `EV/api_model.txt` |
| inline `python3 -I -` blocks (text in this session) | `EV/jobs_per_head.txt`, `EV/main_push_reds.txt`, `EV/allruns_by_hour.txt`, `EV/heads_per_hour.txt`, `EV/workflow_run_per_title.txt`, `EV/pr_lifetimes.txt`, `EV/push_median.txt`, `EV/roster_open_groups.txt`, `EV/wave_script_restore_gap.txt` |
| `gh api …/rulesets/23698884`, then the jq dry run | `EV/ruleset-23698884.json`, `EV/ruleset_dryrun.txt` |
| `gh api …/environments`, `…/environments/<e>/deployment-branch-policies` | `EV/raw/environments.json`, `EV/raw/env_*` |
| `gh run view --job <id> --log` for the incident jobs and `ci-ratchet` | `EV/logs/`, `EV/incident_ratelimit_lines.txt` |
| `git grep -l -e '--self-test' -- tools/` with a per-file workflow grep | `EV/selftest_enum.txt` |
| `gh api pulls/<n>/files`, `pulls/<n>/commits` | `EV/open_pr_ci_files.txt`, `EV/pr_commit_kinds.txt` |

`EV/raw/allruns_0400_1000.json` hit the listing's 1000-row cap, so 04Z is partial. The
05-09Z rows are complete (the oldest row is 04:06:02Z).
