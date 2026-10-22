Design review: approve-with-amendments

R10-CI-LAYOUT plan addendum A1-A6 (`PLAN.md` beside this file). Reviewed adversarially
from fresh `origin/main` `e8c67e1d3` (2026-10-19 12:29Z), the roster entry at
`origin/handoff/audit-r10-roster`, all six carries, `ev/`, `ev/design/` (DESIGN-P1,
DESIGN-P2, REVIEW5) and `../ci-ratchet/`. Read-only: nothing posted, nothing pushed.
Live reads made by this seat: ruleset 23698884, the rulesets list, `rules/branches/main`,
the last 12 Tests push runs, the jobs of push run 39246896264, the runs of
09:40-10:10Z and four of their failed-job logs, and PRs #2444 and #2447. About 20 calls
in, the tool reported that the shared 5000/h user quota was exhausted. That is the
quota the seats and the tick draw on, and A1 below now covers it. After that this seat
made no further calls.

Nothing in the plan is refused. Every item is approved or amended. Section 5 lists 9
dispatch-blocking defects the plan misses, B1-B9; B1-B3 are roster or design defects
outside A1-A6. Section 6 is the amended unit list, with the PR each unit lands in.

---

## 1. Verdicts on A1-A6

### A1, the REST budget: AMEND

The plan budgets only the polls the umbrella adds. Two measurements this seat made show
that this is the wrong quantity.

- **The second exhaustion happened at low volume.** At 09:57:32Z, `validate-hacs`
  (job 117997987428) read `API rate limit exceeded for installation`. In
  09:40-10:10Z the repository created **41 runs**: 12 `pull_request`, 1 review, 6
  `push` and 22 `workflow_run`. The 07Z hour had 281. So the quota runs out under
  today's layout with no polling at all, and the plan's model does not explain the
  09:56Z incident. Also red in that 09:56 push wave: `merge-main`, Governance `record`,
  `env-matrix`, and `rerun-stale-contract` (at 09:56:33Z). Their logs did not match
  the grep, so their cause is unverified.
- **The baseline consumers are unmeasured.** One example: the `ci-ratchet` job alone
  makes 1 artifact listing plus up to 45 zip downloads plus 3 run downloads plus 1
  runs listing, so about 50 calls per push run (`tests.yml:2883-2943`; est. from the
  code). The `workflow_run` re-runners and the autofix lanes' `curl` loops are not
  counted anywhere either.
- **Job-level `/rate_limit` deltas cannot attribute calls.** The `GITHUB_TOKEN` quota
  belongs to the repository and is shared by every concurrent job, so the delta between
  a job's start and end includes every other job's calls.
- **A 403 feeds itself.** A gate that goes red on a 403 is exactly what
  `gate-sweep.yml` re-runs (DESIGN-P2 2.1), and every re-run spends more of the
  exhausted quota.
- **The plan's own figures miss its rule.** With the sweep at 15 s, the worst case is
  2 × 40 × 10 = 800 calls/h, above its own 500/h rule before the prelude is counted.

Amended A1 (it blocks U0, U6, U8, U9 and the combined control):
1. **Budget the total, not the increment.** Per code head and per push run, count
   every `GITHUB_TOKEN` call that every job makes (all workflows, `workflow_run` runs
   included, the prelude, gate, sweep, `ci-ratchet` and autofix included). Project
   it at the measured peak: 10 code heads/h plus that hour's push runs and
   `workflow_run` runs. Merge rule: **the projected total is at most 700/h** (70 % of
   the documented 1000/h; the documented limit itself is unverified here), shown
   before and after PR 2 on the same hour's mix.
2. **Count calls, do not difference them.** Count by instrumentation: `GH_DEBUG=api`
   for `gh`, and a counting wrapper for `curl` and `aiogithubapi` where possible, per
   job. Use `/rate_limit` deltas only as a total cross-check, over a window with no
   other activity. Each figure is printed beside its failure count.
3. **Intervals.** The prelude's verdict wait polls at ≥ 60 s. `gate.py --sweep` polls
   at ≥ 30 s (20 polls in its 600 s bound) and makes one runs listing per poll for all
   the runs it polls, never one call per run. `pr-contract`'s code-scanning analyses
   poll is ≥ 30 s inside its 10-minute bound. Conditional requests (`If-None-Match`)
   are allowed, but the budget assumes every poll is counted: the 304 exemption is
   unverified, and an Actions runs listing changes whenever any run updates.
4. **A rate limit is its own outcome.** When `prelude.py`, `gate.py` and the sweep read
   a 403/429 with `rate limit exceeded`, they report `RATE-LIMITED` and fail closed.
   The sweep never re-runs a gate whose failure is `RATE-LIMITED` until
   `X-RateLimit-Reset` has passed. Plant: a stubbed 403 gives FAIL `RATE-LIMITED` and
   zero sweep re-runs. Null: a stubbed ordinary red is re-run as the design says. This
   also covers today's `contract_rerun.py` until PR 2 deletes it.
5. **The seat side has a budget too.** `sweep_driver.py`, `merge_train.py wait-ci`,
   the tick and the fan-out's probe pushes draw on the shared user/App quota, which
   this review saw exhausted. Each seat-side poll is ≥ 60 s and backs off on 403
   (github-poll-five-minutes already sets 300 s for the tick). Before each probe push,
   the fan-out reads `/rate_limit` and pauses below 20 % remaining.
6. **The 09:56Z incident is attributed before U0 starts:** which jobs spent the
   09:00-09:57Z quota, from the counts in item 2 or from logs. If the main consumer is
   one job (`ci-ratchet`'s artifact loop is the first suspect), its reduction is a
   payment inside PR 2, not a follow-up.

### A2, `kernel-points.yml` (#2368 merged as `499f952b`): AMEND, choosing U11

The file is on main: triggers `workflow_dispatch` and `pull_request: [labeled,
synchronize]`, a label guard, a 4-coretype matrix, and a `cancel-in-progress`
concurrency group for non-bot senders. It is also in `pr-contract-rerun.yml`'s
`workflows:` list. U11 is approved over the exemption, with these amendments:
1. `ci.yml`'s `pull_request` types gain `labeled`. `gate` stays `if: ${{ !cancelled() }}`
   on that event too. A skipped `gate` would pass a required check (DESIGN-P2:332), so
   entities pins that no `gate` `if:` can be false for any type in `ci.yml`'s `on:`.
2. Kind derivation. `labeled` with label `kernel-points` is a kind whose WORKSET is
   `{kernel-points}`. `labeled` with any other label has an empty WORKSET, and its gate
   only re-judges. `synchronize` with the label present adds `kernel-points` to the code
   run. `kernel-points` is never in `REQUIRED` or `gate_required` (it is never required
   today), but `pr-contract`'s red list names it when it is red.
3. Its `cancel-in-progress` group is **not** ported into `ci.yml`, whose run-id groups
   cancel nothing (N1). The unit's job carries the matrix as it is.
4. `kernel-points.yml` keeps only `workflow_call` and `workflow_dispatch`, and the
   dispatch arm takes the 4.3 item 5 ref guard: a dispatched run at an open PR's head
   FAILs unless `pr` is named. Otherwise a dispatched red at a PR head goes unseen once
   `pr-contract-rerun.yml` is deleted.
5. U11 measures the `labeled` events per PR head over the last 7 days, read-only.
   A1's projection counts them, because each one is a run with a prelude wait.

### A3, packaging: AMEND (four PRs, with the carries re-routed to their current owners)

The PR 0 split is approved. It is approved design content (DESIGN-P1 step 5b), it
unblocks the fan-out's live work, and it does not touch the 17 (section 2). The carry
re-routing in the plan is stale against the live state:
- **#2444 (R10-SEAT-SELFTESTS-CI) is open** at `b891dfa0`. It already folds carry 5
  (the field-coverage pathspec: `tests/ci_budgets.json`, `tests/ci_ratchet*`,
  `tools/audit/archscore`, the card `www/`). It wires `merge_pr.sh` and the
  `tools/audit/seat/` self-tests. It **forward-carries three items back to
  R10-CI-LAYOUT**: the 7 unwired self-tests outside `tools/audit/seat/`
  (`check_scopes.py`, `merge_throughput.py`, `worktree_gc.sh`, `coverage/partition.py`,
  `record-predicate/row_files_replay.py`, `pr/approve_held_runs.sh`, `pr/head_note.py`),
  the uncovered push/merge lines of `merge_pr.sh`, `handoff_push.sh`, `open_pr.sh` and
  `update_pr.sh`, and the census-filter cost. It does not do carry 3. Re-routing carries
  2 and 3 into SEAT-SELFTESTS-CI would re-cut an open PR.
- **#2447 (R10-PREPR-UNPINNED-RED) is open.** Its step 6f already does carry 1
  (`throwaway_git.py --check`, with a plant and a null). It does **not** do carry 6
  (`ci_predict.py` / `body_push.sh`), which sits in both its roster carry and
  CI-LAYOUT's.

Amended packaging. Section 6 has the unit list.
- **PR 0**: the stub, **plus the ci-ratchet payments (a), (b) and (c)** (section 3).
- **PR G** (new; scoped, because `governance.yml` is not a gate file; code-owned): carry 3,
  plus #2444's forward-carries 1 and 2. It is cut **after #2444 merges** (same job, same
  file) and lands before U4 cuts `probe/ci-layout-governance`.
- **PR 1**: phase 1, less step 5b.
- **PR 2**: the umbrella, plus A1, A2/U11, A5 and carry 6 (in U9).
- Carry 5 is struck from CI-LAYOUT once #2444 merges, verified by
  `dev/audit/harnesses/r10_field_coverage_paths.sh origin/main` reading `misread=0`.
- Carry 1 is struck once #2447 merges, verified by its step 6f on main.
- Carry 6 is struck from PREPR-UNPINNED-RED's roster carry, so it has one owner.
- The census-filter cost is recorded as decided (custom_components/ stays out of the
  pathspec, tvofi). It owes no unit.

U5 stacked on PR 1's verdict head: approved, with one rule. U5 re-cuts when PR 1's head
changes for any reason other than a merge of main.

**Fallback.** If PR 0's ratchet half has no verdict when U0's offline work ends (≈ T+4 h
after dispatch), the stub ships alone as PR 0, and (a)-(c) follow as their own PR, still
before PR 1.

### A4, the shared BEFORE twin: AMEND

Approved, bound to a base. A BEFORE twin is valid only for the units whose probe refs
are cut from the same `origin/main` SHA as the twin. Main's layout changes three times
during the fan-out: PR 0, PR G and PR 1. So:
1. Re-take the twin whenever a merge touches `.github/workflows/`, `tests/run.sh`,
   `tests/closure.py` or `tools/coverage/coverage_tree.sh`.
2. Every AFTER null run carries byte-identical twin diff text, checked by hash.
3. Each unit's evidence names the twin's base SHA. The combined control refuses a unit
   whose twin base differs from its probe base.
4. The twin is a draft, so it counts toward `pr_cap.py`.

### A5, the merge train reads several `gate` runs: AMEND

Approved, with both directions and the platform as the reference:
1. `merge_train.py`'s `ci` step adopts the reading M-2 measures.
2. The combined control runs `wait-ci` on two heads. On head (i), an older red `gate`
   sits beside a newer green one, and the train proceeds only if M-2 shows that the
   platform takes the newest. On head (ii), an older green sits beside a newer red, and
   the train refuses.
3. On both heads, the train's verdict equals GitHub's own required-check evaluation for
   `gate`: `pulls/N` `mergeable_state`, or the GraphQL `statusCheckRollup`. A
   disagreement FAILs.
4. A `RATE-LIMITED` gate (A1 item 4) is never a pass.

### A6, "main stays green": AMEND

The set comparison ("the merge adds no failing job to main's push run, against the
base's push run") is approved, with three amendments:
1. **`ci-ratchet` is not grandfathered.** It is in this group by tvofi's ruling. From
   PR 0's merge onward it must turn green under the window rule in section 3, and no
   later PR may leave it red.
2. **Renamed jobs are mapped.** Across PR 2, the comparison maps each old name to its
   `tests / …` name through `required-contexts.json` `gate_required` and the unit map.
   Without the map, every job reads as both removed and added.
3. **The baseline is the base push run plus main's previous 3 push runs.** A job red on
   any of them is baseline-red: today that is `record-autofix` and Governance `record`
   (3 of 9). A baseline red that recurs on 2 or more of the 4 runs is named, and routed
   if it has no owner. The 09:56Z `record` red was part of the rate-limit incident and
   is attributed under A1 item 6.

---

## 2. The split against live ruleset 23698884

Live read at about 12:35Z: byte-identical to `ev/ruleset-23698884.json` on name,
target, enforcement, conditions, bypass_actors and rules. `updated_at` is
`2026-10-19T00:29:10.971+02:00`. There are 17 contexts, and only `budget-raise-gate`
is bound, to `integration_id` 15368. `strict_required_status_checks_policy` is
`false`. There is no merge-queue rule. `rules/branches/main` lists only
`deletion`/`non_fast_forward` (ruleset 22628467) and
`required_status_checks`/`pull_request` (ruleset 23698884). Classic branch protection
answers 404. Ruleset 23937752 targets tags only.

| step | required set | satisfiable? |
|---|---|---|
| PR 0 (stub + ratchet) open, then merged | 17 | **yes**. `ci.yml` is `workflow_dispatch` only, so it writes no check at a PR head. `run.sh`, `coverage_tree.sh` and `ci_ratchet.py` rename no job. FULL, because `tests/run.sh` and `tests/closure.py` are both in `GATE_FILES` (`closure.py:453`). (The plan's 0.7 says `GATE_FILES` lists `tests.yml` alone. It lists 9 entries; only `tests.yml` among the workflows.) |
| PR G open, then merged | 17 | **yes**. Only steps are added to `governance.yml`, and `wave-script`, `policy-docs` and `env-matrix` keep their job ids. PR G's planted divergence must redden `wave-script`, which is required. That plant runs on a probe, never at PR G's head. |
| PR 1 open, then merged | 17 | **yes**, as in DESIGN-P1 3. The 8 moved jobs include `recheck-gate`, a `needs` of 5 required jobs. The entities producer assertions (`:27701-27752`) must be re-run at PR 1's head with `recheck-gate` gone, with the `merge_group` and `workflow_dispatch(recheck)` events listed. |
| fan-out (probe PRs) | 17 | not applicable: drafts, never merged. Each probe push runs 12 old workflows plus `ci.yml`, so A1 item 5 applies |
| PR 2 open, under the 17 | 17 | **no, by construction.** Its head produces `gate` and `tests / …`, not the 17 names. Only the PUT makes it mergeable. |
| between PUT and merge | `gate` | only PR 2's head has a producer. A record PR from the old layout is refused (its merge goes through the record lane's `PUT pulls/N/merge`, which is subject to the ruleset; #2446 merged as `tvofi`, and the always-bypass actors are a DeployKey and Integration 5094721). So main cannot move under PR 2 |
| after the merge | `gate` | yes for every PR that merges new main |

The split is sound. Two conditions are added:
- **No push run is in flight at the PUT.** A push run in flight runs `record-autofix`,
  which can open a record PR from the old layout. That PR is then stuck until it is
  recarried.
- **PR G merges before U4 cuts its ref, and PR 1 merges before U5/U9 assemble.**
  Otherwise the static maps drift (plan 4.3).

---

## 3. The ci-ratchet payments: they fit, landing in PR 0

Re-measured from fresh main.
- `ci_ratchet.py:174-193`: `critical_path_minutes` is the **median wall
  (created_at → updated_at) of the completed push `Tests` runs in a window of 8**
  (`tests.yml:2941`, `per_page=8`).
- `script_runs_per_push` is the **max** over the push runs in the artifact window
  (`:207`, last 15 runs, 45 artifacts).
- The last 7 completed push runs read 59.0-59.8 min, plus 44.6 and 60.9.
- In push run 39246896264, `fast (3.14)` ends at +58.5 min, `closures` at +26.9,
  `coverage` at +9.2, and `ci-ratchet` adds 1 min. `fast` is the binding constraint,
  and `closures` leaves 28 min of headroom.

| payment | fits? | lands in | amendment |
|---|---|---|---|
| (a) `arch_score.py` + `arch_score_head.py` from `lane_units` (`run.sh:517-518`) to `lane_golden` | **yes.** `../ci-ratchet/ev/lane_model.txt` puts c3530277's wall at 60.4 → 49.4 and 0dac0bf8's at 59.9 → 49.4. The median of the last 8 modelled runs is about 45 against 54.825. A separate job is not needed and would add a check name: choose `lane_golden` | **PR 0** (`run.sh` is a gate file and code-owned, so FULL either way) | Confirm from CI in two stages. First, on PR 0's own FULL run, the `fast (3.14)` job ends at least 5 min sooner than its base's FULL run (same event class). Second, after the merge, by the window rule below. Add an entities pin that the two lines sit in `lane_golden` and not in `lane_units`; its mutant moves one back. |
| (b) the floor re-validation (`coverage_tree.sh:282-300`) re-measures only the `reused` scripts | **yes.** It is the cause of efdc055a's 67.0 min run (`closures` ended at +65.8, after re-running all 20), so it protects `critical_path_minutes` as well as the count | **PR 0**, not W1. W1 edits `coverage_tree.sh:147-160,190-200`, a different region, and its PR lands about 10 h later | the test in `entities-tests-unlanded.diff` (`_coverage_revalidation`, with a floor-met null). PR 1 keeps that test green after W1, as the guard against a silent revert |
| (c) `script_runs()` (`ci_ratchet.py:170-171`) excludes class `reused` | **yes.** 73 − 19 = 54 against 68. The derivation re-reads the window's artifacts, so it goes green on the first push run after the merge | **PR 0**. PR 2's edit at `:177,185` (the `Tests` name and the `tests.yml/runs` URL) is a separate region | **Re-record `script_runs_per_push` in the same PR.** Excluding 19 rows otherwise loosens the ratchet by 19 without anyone deciding it. The value is the every-script-measured-once count, re-derived (≈ 53 = 33 non-coverage + 20; est.). The window max (≈ 34 on a floor-met push) is the wrong value, because under (b) a legitimate floor-FAIL push measures each script once and must stay green. Its `reason` says that this is a tightening, not a raise. Controls: the unlanded `_CIR_REUSE` test with its null, and the CI-RATCHET-RED brief's control (a planted extra script run turns `ci-ratchet` red). |

**When "green" is reached (this gates R10-STAMP).**
- `script_runs_per_push` is green on the first push run after PR 0.
- `critical_path_minutes` is the median of 8, so it is green only once **at least 5 of
  the 8 newest completed push runs** fall under 54.825. That means about 5 merges after
  PR 0.
- **Never re-run a push Tests run to check.** A re-run moves `updated_at`, and that run's
  wall then counts the whole gap. Wait for new push runs instead.
- If the window is still red 6 push runs after PR 0, stop and re-measure: the model's
  4-worker contention bound is the assumption most likely to fail. A raise is the last
  resort, under rule 2.

**After PR 2.** U9's re-keyed reader (the `tests / *` span of `ci.yml` push runs, with
its null over the last 8 old runs) must carry (c)'s exclusion and its test unchanged.

---

## 4. tvofi's ruleset step: not yet exact. Amendments

The jq transform was dry-run (`ev/ruleset_dryrun.txt`). It changes only
`required_status_checks`, and the read-back compares the payload's keys. Seven gaps
remain:
1. **Run it as a script with `set -euo pipefail`.** As written, a failed GET leaves an
   empty rollback file and the block continues.
2. **Save the rollback to an absolute path** that outlives the shell. Proposed:
   `~/hpo-orch/r10s3/cutover/ruleset-rollback-23698884-<UTC>.json`. Before the PUT,
   `jq -e` asserts that the file holds exactly 17 contexts.
3. **Preconditions, read immediately before the PUT. Any mismatch stops the script.**
   - The live ruleset's six keys hash equal to the JSON staged in PR 2's body. The
     staged value is the read at that time, not today's `updated_at`.
   - `commits/H/check-runs?check_name=gate` has a newest `gate` with conclusion
     `success`, `app.id == 15368`, and `head_sha == H`.
   - `gh api user --jq .login` reads `tvofi`.
   - No Tests or `ci.yml` push run is `in_progress` on main.
   - The open-PR list is empty, PR 2 aside.
4. **The read-back has two halves.**
   - The PUT result equals the payload.
   - Everything except `required_status_checks` equals the rollback file. This half
     proves the PUT changed nothing else, which today's read-back does not.
5. **A payload the API rejects.** No read-only endpoint validates a ruleset PUT, and the
   payload passes `bypass_actors` with `actor_id: null` for the DeployKey (as the GET
   returns it). State in the body that a 4xx leaves the ruleset unchanged, and that the
   two-half read-back shows it. The rollback uses the same GET-shaped body, so the same
   applies to it.
6. **Rollback triggers, each with a time bound.** Roll back if any of these holds:
   - PR 2 is not merged within 15 min of the PUT;
   - main's push `gate` is not green within 75 min;
   - step 3a fails and its own rollback (disable `gate-sweep.yml`, run
     `sweep_driver.py`) does not hold.

   The order is ruleset first, then the revert of PR 2. The revert PR's head has the old
   layout, so it produces the 17 and can merge. Doing it the other way round deadlocks.
   The rollback has its own read-back: all six keys equal the rollback file.
7. **U9's instrument.** It runs `--dry-run`, `--apply` and `--rollback`, with a
   self-test over saved JSON, and is **wired in `instrument-self-tests`**. PR G's widened
   `selftest_wiring.py` then keeps it wired. tvofi runs one command, and PR 2's body
   shows its dry-run output at H.

---

## 5. Dispatch-blocking items the plan misses

| # | item | needed before dispatch |
|---|---|---|
| B1 | **Each carry needs exactly one owner.** Carry 5 is in SEAT-SELFTESTS-CI's roster carry and CI-LAYOUT's, and #2444 pays it. Carry 6 is in PREPR-UNPINNED-RED's carry and CI-LAYOUT's, and #2447 does not pay it. #2444 forward-carries 3 items here that are not yet in the roster. | a roster edit per A3 (orchestrator) |
| B2 | **R10-CI-RATCHET-RED is still a separate roster group** at `stage: not-started`, with `next_step: fixer` and `files: [tests/ci_ratchet.py, .github/workflows/tests.yml]`. The dispatch watcher could dispatch a second fixer onto the files PR 0 edits. Separately, the plan's 4.6 ("dispatch it as its own group") and its risk row "PR 2 makes the stamp read `gate`, which does not list `ci-ratchet`" are superseded by the ruling and refused. | set the group's stage so the watcher skips it, with the fold note (orchestrator) |
| B3 | **The approved design weakens the stamp.** Today `stamp.py` needs the whole Tests push run green, `ci-ratchet` and `coverage-ratchet` included. After PR 2 it reads the push `gate`, whose `REQUIRED` (DESIGN-P2:544-553) lists the 17, and `record-autofix` only under D-1-refused. A red `ci-ratchet` would then stop blocking stamps, the outcome the plan's risk table counts as a mitigation. **Amendment (U0 `REQUIRED`, U9 stamp reader):** on `push`, `REQUIRED` gains every job whose failure reddens today's Tests push run (`tests / ci-ratchet`, `tests / coverage-ratchet`, and so on, enumerated by command from `tests.yml`, not from memory). Parity control: that enumerated set equals `REQUIRED[push]`; a planted red `ci-ratchet` turns the push `gate` red and makes `stamp.py` refuse. It is the design's own rule that `stamp.py` "keeps refusing as it does today" (DESIGN-P2:1066), extended to every job. | U0's interface, before batch 1 |
| B4 | **The window rule for green** (section 3): 5 of 8 push runs, never re-run. Without it, the first red push run after PR 0 will be misread as a failed payment. | the PR 0 brief |
| B5 | **A1 as amended**, including the 09:56Z attribution and the seat-side quota. | U0 |
| B6 | **The roster entry still describes two PRs.** `next_step` reads "dispatch a fixer for phase 1", and `owner_gate` is stale. The plan's replacement owner_gate text (section 6 of the plan) must also name PR 0 and PR G, and `tests/run.sh` (owned) for PR 0. | a roster edit before the first fixer |
| B7 | **R10-STAMP ordering.** Its carry reads "runs after R10-CI-LAYOUT merges", because ci-ratchet is red. With the payments in PR 0, the stamp can run once the window is green, before PR 1 (plan 4.4 allows "before PR 1"). That ordering is a recommended decision under the R10 grant, for the orchestrator to record. If it is not taken, the stamp waits until about T+27 h. | orchestrator decision; does not block PR 0 |
| B8 | **PR G must wait for #2444.** Both edit `instrument-self-tests` in `governance.yml`. Cut PR G from main after #2444 merges, and re-run #2444's `selftest_wiring.py --check` and mutant harness at PR G's head. | PR G's brief |
| B9 | **PR 1's producer check after `recheck-gate` moves** (section 2), on the `merge_group` and recheck events explicitly. | PR 1's brief |

Not blocking. TRAIN-HOLD's `after` groups (TICK-TRAIN, TICK-ORCH) are both `done`, so
plan 4.1's drain order is executable now. #2368 is merged, so A2 is designed against the
real file.

---

## 6. Amended unit list and PR placement

| unit | content | lands in | CI / gate |
|---|---|---|---|
| PR 0-stub | DESIGN-P1 5b: inert `ci.yml` (`workflow_dispatch`, inputs, `permissions: {}`), its entities pin, `GATE_FILES += ci.yml` | **PR 0** | FULL; code-owned; mandate |
| PR 0-R(a) | `arch_score.py` and `arch_score_head.py` to `lane_golden`, plus a placement pin | **PR 0** | as above |
| PR 0-R(b) | the floor re-validation re-measures only `reused` scripts, plus `_coverage_revalidation` and its null | **PR 0** | as above |
| PR 0-R(c) | `script_runs()` excludes `reused`; `script_runs_per_push` re-recorded down to the every-script-once count; `_CIR_REUSE` and its null; a planted extra run turns the ratchet red | **PR 0** | as above; the tightening needs no `## Raise justification` |
| PR G-1 | carry 3: the wave-script restore list derived from the transitive importers' closure of `agreement_py` (at least `stamp.py`, `delivery_status.py`, `merge_train.py`); planted divergence in each turns it red; a dropped-import mutant turns the derivation red; null `divergent=0` | **PR G** | scoped; code-owned |
| PR G-2 | #2444 forward-carry 1: wire the 7 self-tests outside `tools/audit/seat/`; widen `selftest_wiring.py` to `tools/`; dispose of each of `ev/selftest_enum.txt`'s 35 NOT-CI files by command (`.md` and fixtures: "not a self-test", and why); a mutant per added step | **PR G** | as above |
| PR G-3 | #2444 forward-carry 2: offline seams for `merge_pr.sh`'s post-gate path and the push lines of the 3 wrappers, under `offline_spy.py` | **PR G** | as above |
| PR 1 | DESIGN-P1 section 4 less 5b, W1 included; B9's producer check; R(b)'s test stays green across W1 | **PR 1** | FULL; code-owned and policy |
| U0 | as designed, plus A1 items 1-6, B3's `REQUIRED[push]` parity, and A2 item 2's kinds | **PR 2** | — |
| U1-U8, U10 | as designed; U6 adds A1's 30 s code-scanning poll; U4 is cut after PR G; U5 is stacked on PR 1's verdict head | **PR 2** | — |
| U11 | `kernel-points` as a `workflow_call` unit, with A2 items 1-5 | **PR 2** | — |
| U9 | readers as designed, plus the A5 train reading in both directions with the platform cross-check; `ci_ratchet.py:177,185` re-keyed with its null and (c) kept; the `stamp.py` push-gate reader (B3); carry 6 (`ci_predict.py` runs the same `carry_audit` check as `pr-contract`: plant, an unrouted body refused; null, a routed body passes); the ruleset instrument (section 4) | **PR 2** | — |
| combined control | as designed, plus A1's total projection at most 700/h, A5's two heads and the A4 twin-base check | **PR 2** body | — |
| cut-over | the section 4 script (tvofi), then `merge_train.py run [PR 2 @ H]` | at PR 2's merge | tvofi's one action |

Struck from the group once the paying PR merges, each verified at main: carry 1 (#2447)
and carry 5 (#2444). The census-filter cost is recorded as decided.

Order: #2368 is merged. Then:
1. From T0, in parallel: PR 0, #2444 and #2447 merging, and TRAIN-HOLD dispatched.
2. Then PR G, and the stamp once the ratchet window is green (B7).
3. Then PR 1, as plan 4.2 orders it.
4. Then PR 2 at a wave boundary.
- tvofi 2026-10-19: hard floor 60 s between GitHub polls for every poller (design review's 30 s sweep poll is overruled -> >=60 s).
