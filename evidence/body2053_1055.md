R9-CI-2a. `budget-raise-gate` left a **cancelled** check run beside a green twin at the live head of #2007, #2029, #2041 and #2049. The merge scripts read that cancelled run as blocking, so those merges were done by hand. Part of #201.

**What happened, from check-run data.** On each of the four heads there are two `pull_request` runs of `Budget raise gate`, created 0–1 s apart, both sent by `hpo-author[bot]`. The first one concluded `cancelled` and the second `success`. `tools/pr/app_push.sh` pushes the branch (`synchronize`) and then PATCHes the open PR's body (`edited`). The gate lists `edited` (a retarget moves the base it grades against). Its group was `<workflow>-<PR number>` with `cancel-in-progress: true` for author-sent `pull_request` events. So the `edited` run cancelled the `synchronize` run **at the same SHA**. That is not a supersession, because both runs graded one head. Workflows that do not list `edited` got exactly one run per head (`Tests`, `Governance` on the same four heads). On #2049 tvofi's attempt-2 re-run turned the cancelled run green, which is the manual workaround.

**The fix.** Each run of `budget-raise-gate.yml` gets a group of its own (`${{ github.workflow }}-${{ github.run_id }}`) and `cancel-in-progress: false`, so no run of this file cancels or queues another. The header's invariants still hold, and `_brg_defects` in `tests/entities.py` still checks them: one job, no `if:`, never a skipped run, the full verdict every run, `merge_group` support.

**Alternatives, and why each lost (fixer.md step 17).**
- *Keep the per-PR group and set `cancel-in-progress: false`* (the `pr-contract.yml` shape, R9-RC-PRCONTRACT). This is still exposed: GitHub cancels an older **pending** run in a group when a newer one queues, whatever `cancel-in-progress` says. `pr-contract.yml` hit exactly this on `record/autofix` at `e127970e9f`. Run 37730882515 (older head `2c8b342f04`) held the group from 05:08:31 to 05:08:57Z. Both new-head runs queued behind it, and the newer one cancelled the older at 05:08:36Z. That was 1 of the 300 `pr-contract` runs fetched.
- *A group keyed by head SHA.* The two twins share the SHA, so they would still share a group and still cancel or queue each other.
- *No `concurrency:` block at all.* This behaves the same as per-run groups. But `tests/entities.py` requires every workflow a pull request starts to declare one, and an explicit block states the decision where the next reader looks.
- What per-run gives up: an older head's run is no longer cancelled. The job takes seconds, and its check run is attached to the older SHA, which nobody reads. Disclosed order sensitivity: a retarget (`edited`, new base) at the same instant as a push could finish in either order. Both runs read the reviews live. After an approval, `budget-raise-gate-rerun.yml` now re-runs **every** red `pull_request` run of the gate at the head, which is the change below.

**The checker.** `_cc_problems` in `tests/entities.py` assumed that only `pr-contract.yml` lists `edited`. Its comment said so, and the exemption was keyed on the file's name. In fact it **required** this gate to cancel same-SHA twins, so it pinned the defect. Each workflow that lists `pull_request: edited` now needs an explicit route in `_CC_TWIN_ROUTE`: `serialised` (one group, no cancel: `pr-contract.yml`, unchanged) or `per-run` (`budget-raise-gate.yml`). An unrouted file is refused. Workflows that do not list `edited` behave as before.

**Instrument** (fixer.md step 18): `tools/audit/seat/run_twins.py` counts a workflow's cancelled `pull_request` runs that had a same-SHA `pull_request` sibling created within 10 s. It has a 4-case `--self-test`, including the null control "a cancelled run at an older SHA is other". It is listed in `tools/audit/seat/INSTRUMENTS.md`, and the `tools/audit/` prefix makes it INERT.

**The stale-verdict re-run (round 1 of review).** With the twins no longer cancelled, an author push on a raise PR leaves **two** red `pull_request` runs at one head until the owner approves. `stale_run` in `tools/policy/budget_raise_gate.py` re-ran only the newest red run, so after approval one red twin stayed. GitHub's ruleset refuses the merge while any suite at the head carries a non-success run: on #2009 an older cancelled suite blocked the merge beside a newer green one, and the merge went through 27 s after that older suite was re-run. `stale_run` now returns every red `pull_request` run of the gate at the head, waits while any is still going, and `rerun_stale` posts one re-run per id. On main, that twin was `cancelled`, which `RERUN_CONCLUSIONS` excludes, so a hand re-run was equally needed there. This is a gap the diff exposes, not a regression. `budget-raise-gate-rerun.yml` runs main's copy of the program, so the change takes effect once this merges. A `cancelled` run is still left alone, and after this diff the gate's concurrency no longer produces one.

## Head

`e4fa486c0ce36463091b26b09f4fd318ebd1d228` merges the authored code head `5d4d30a7d1c288a9083456b88b40b5872a8d30bc` and then merges origin/main `9cac1947` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`6ddb8c4c44d2851dabf6f9f3c19baa1d815d9dbf` is the bot commit `ci: re-record closures` (github-actions[bot], `closures-autofix`). It adds one `inert_reads` line, `dev/audit/harnesses/git_auto_maintenance_race.sh` under `tests/harness_headers.py`, and re-records two `seconds` figures. Its cause was main's `closures` red after #2051, inherited at `3362e0f0` (see `## Red checks`); #2055 lands the same line on main. The authored code head is now `5d4d30a7d1c288a9083456b88b40b5872a8d30bc`, which adds the `stale_run` change on `0c8784ac`.

`3362e0f056db1c99a07d836cbdb80e7fe9574d58` merges origin/main `470bbd60` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`e7bb6f1947b1593abe854021b105c12105a55d53` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2053.md`. The authored code head is `0c8784ac36e995359de96688ea530862a1d967d2`.

`51eb777886e8fd7cd39a879b915831e9df0ec86e` merges origin/main `0c25836e` into the authored code head `0c8784ac36e995359de96688ea530862a1d967d2` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`0c8784ac36e995359de96688ea530862a1d967d2` (code commit `e960a747`, then the instrument commit). Merge base `ef3ca657`, origin/main at 2026-10-08T06:40Z.

## Mutation proof

The workflow change carries the fix, so the mutants mutate the predicate:

- **Old block restored** (main's `concurrency:` in `budget-raise-gate.yml`, new checker; this is the failing-test-first run): `PYTHONPATH=tests/hastub python3 tests/entities.py` gives `2 of 2205 ENTITY CHECKS FAILED`:
  - `FAIL a superseded long-job pull-request run is cancelled; pr-contract same-SHA twins are not  [["budget-raise-gate.yml: cancel-in-progress under pull_request by hpo-author[bot] is 'True'", "budget-raise-gate.yml: two pull_request runs by hpo-author[bot] get groups 'Budget raise gate-7' and 'Budget raise gate-7'"]]`
  - `FAIL budget-raise-gate gives each author-app pull_request event at one SHA a group of its own and cancels none (R9-CI-2a)  [groups='Budget raise gate-7'/'Budget raise gate-7' cancel='True']`
- **Only `cancel-in-progress: false` → `true`** in the new block, at the head: `2 of 2205 ENTITY CHECKS FAILED`, the same two check names, with `cancel='True'` on the second.
- Restored: `ALL 2205 ENTITY CHECKS PASSED`.
- **`stale_run`, failing test first.** The new self-test cases were written before the change. `python3 tools/policy/budget_raise_gate.py --self-test` on the old `stale_run` fails, including `FAIL rerun: two red twins at one head, both re-run: got ('rerun', 4), want ('rerun', [3, 4])` and `FAIL rerun: an older red run beside a newer green one is still re-run: got ('none', None), want ('rerun', [3])`. The remaining failures are the return-shape change from an id to a list of ids.
- **`stale_run` mutant**: the red list taken over `same[-1:]` (the newest only) instead of `same` gives `budget_raise_gate self-test: 206 checks, 3 failed`:
  - `FAIL rerun: two red twins at one head, both re-run: got ('rerun', [4]), want ('rerun', [3, 4])`
  - `FAIL rerun: an older red run beside a newer green one is still re-run: got ('none', []), want ('rerun', [3])`
  - `FAIL rerun: end to end, two red twins post two re-runs`
- Restored: `budget_raise_gate self-test: 206 checks, 0 failed`.

## Null control

- The checker's own null control (`and the cancelling block, a serialised one, or an unrouted `edited` file is refused`) feeds `_cc_problems` three bad shapes, and each is refused. They are main's old block (a `cancel-in-progress` problem), a per-PR group with no cancel (a `get groups` problem), and an `edited`-listing file that `_CC_TWIN_ROUTE` does not name (`names no twin route`).
- The existing `pr-contract.yml` checks pass unchanged: `pr-contract does not cancel two author-app pull_request events at one SHA`, and its null control. So the route table did not loosen the serialised file.
- `run_twins.py` against `pr-contract.yml`, which stopped cancelling on 2026-10-05, reads `same-sha-twin=1` against the gate's 85 over the same kind of window. The instrument separates the two designs instead of counting every cancelled run.

- `stale_run`'s own null control: `rerun: twins both green re-run nothing (null control)` expects `('none', [])` and passes, so the every-red rule does not re-run green runs.

## Figures

- `python3 tools/audit/seat/run_twins.py --fetch budget-raise-gate.yml <dir>`, i.e. 3 pages, the newest 300 runs, 2026-10-06T23:29Z..2026-10-08T06:36Z: `pull_request=255`, `cancelled pull_request runs: same-sha-twin=85 other=2`.
- `python3 tools/audit/seat/run_twins.py --fetch pr-contract.yml <dir>`, the newest 300 runs, 2026-10-06T19:40Z..2026-10-08T05:37Z: `same-sha-twin=1 other=0`.
- These are sliding windows: re-running moves them. The rule is in `run_twins.py`'s docstring.
- The four named heads, from `gh api repos/tvofi/heatpump_optimizer/actions/runs?head_sha=<head>`, filtered to `Budget raise gate`. Each holds one cancelled and one successful `pull_request` run, created ≤1 s apart:
  - #2007 `0a68a286` runs 37662110702 / 37662111152
  - #2029 `94ce0fe6` runs 37673845508 / 37673849216
  - #2041 `a102be64` runs 37733334989 / 37733335299
  - #2049 `27fdda2a` runs 37732476751 (attempt 1 cancelled, attempt 2 by tvofi success) / 37732477448
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`, and `scope.run` = `tests/entities.py`, `tests/harness_headers.py`.
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2205 ENTITY CHECKS PASSED` (Python 3.14; the 3.11 interpreter cannot parse the file).
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Re-taken on 2026-10-08 on the merged tree this push creates: the PR head `6ddb8c4c`, plus the code head `5d4d30a7`, plus origin/main `9cac1947` (#2055). The claimnotes driver resolved `tests/closures.json` with `LEDGER-MERGE: resolved tests/closures.json`.
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2212 ENTITY CHECKS PASSED`.
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `python3 tools/policy/budget_raise_gate.py --self-test`: `206 checks, 0 failed`.
- **Seams (step 8).** `grep -l -E "types: \[[^]]*edited" .github/workflows/*.yml` lists every workflow that can receive a same-SHA `pull_request` twin. It returns:
  - `budget-raise-gate.yml` (closed in this diff).
  - `pr-contract.yml`: already guarded against `cancel-in-progress`, route `serialised`. Its residual, the pending-replacement cancel above (1 of 300), is a **distinct finding** that this diff does not take. Per-run would remove serialisation, and serialisation stops the `synchronize` run's body read racing the PATCH. Weighing that is its own fix. It goes to the orchestrator, not to an issue.
  - The `pull_request_review: edited` line in `budget-raise-gate.yml` is the same file.

## Red checks

- `closures`, check run 113217602310 at `3362e0f0`: `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: dev/audit/harnesses/git_auto_maintenance_race.sh`. This is main's red, inherited with the merge of `470bbd60`. #2051 added that harness and `tests/closures.json` had no `inert_reads` entry for it, and main's own `closures` on `470bbd60` failed the same way (run 37746914557). The bot's `ci: re-record closures` (`6ddb8c4c`) repaired it on this branch, and #2055 repairs it on main. No cheaper detector exists on this branch: the inert dimension is recorded only under Linux `strace` (`ci-autofix.md`), so the `closures` job is the earliest point the gap can show. The detector for the defect is #2051's own `closures` run, and the gap is that PR's to answer.
- `pr-contract`, check runs 113212898963 at `e7bb6f19` and 113229290002 at `3362e0f0`: body staleness. The body's `## Red checks` did not yet name the reds standing at those heads (`fast (3.14)`, then `closures`). This re-take names every red and clears both.
- `fast (3.14)`, check run 113197582684 at `e7bb6f19`. Its one failed entity check was `tools/release/stamp.py's --self-test passes`, which raised `OSError: [Errno 39] Directory not empty` while cleaning up its fixture's `.git`. The cause is main's own flake, the stamp self-test's temp-dir cleanup race, not this diff. #2051 fixed it on main (merge `470bbd60`). Its RCA, `dev/audit/rca/R9-RCA-stamp-race.md`, names the cheaper detector and its cost. `fast (3.14)` was green at `3362e0f0`, after the merge.
- `delivery-status` is not a required context. It went red on main's history: 9 merge commits whose subjects `subject_number` does not recognise, so the window was reported UNCHECKED. This diff does not cause it.

## Forward-carry

none. The two findings under `## Carries / follow-ups` go to R9-CI-2 through the orchestrator; neither changes a later stage's procedure.

## Carries / follow-ups

Both go to R9-CI-2. Neither is taken in this diff.

- **`pr-contract.yml`, replacement of a queued run in its shared group.** The file has one group per pull request and `cancel-in-progress: false`. GitHub still cancels an older *pending* run when a newer one joins the group. On `record/autofix` at `e127970e9f`, run 37730882515 (older head `2c8b342f04`) held the group from 05:08:31 to 05:08:57Z. Both new-head runs queued behind it, and the newer one cancelled the older (37730887572) at 05:08:36Z. That was 1 of the 300 runs `run_twins.py --fetch pr-contract.yml` read. Per-run groups (this PR's route) would remove it. They would also give up the ordering that keeps the `synchronize` run's live body read from racing `app_push.sh`'s body PATCH, and that trade-off is R9-CI-2's to weigh.
- **Every red run at a head must be re-run green; reading the newest run is not enough.** On #2007, #2029, #2041 and #2049 the cancelled `budget-raise-gate` run had the lower id, and a green run of the same name followed at the same head. On #2009 **GitHub's ruleset itself** refused the merge ("base branch policy prohibits the merge") while an older suite at the head held a `cancelled` run beside a newer green suite. The merge went through 27 s after that older suite was re-run. So teaching the merge scripts to judge a context by its newest run would unblock nothing. The remedy is to re-run every non-success run at the head. This PR does that for the budget gate's red twins (`stale_run`) and stops the gate cancelling its own. A cancelled or red run of any other context, from another workflow or a manual cancel, still needs the same re-run, and R9-CI-2 should give the merge and finish scripts that step.

## Friction

- `fixer.md#step-5: cost: tests/entities.py uses 3.12+ f-string syntax; the default python3 3.11 refuses it, so the seat ran it under the CI venv's 3.14.`
- `CLAUDE.md#instruments: stale: tools/audit/harnesses/ is named but does not exist on main; the instrument went to tools/audit/seat/.`

## Approval

This changes `.github/workflows/budget-raise-gate.yml`, which is code-owned (decision 0013 keeps `.github/workflows/` owned). It merges only on tvofi's approving review at the head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)


