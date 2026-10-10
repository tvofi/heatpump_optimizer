R9-CI-1 round 2 (lane CI, the autofix chain). Round 1 (#2049, merged 2026-10-08 06:40) made the two repairing jobs repair at all; #2060 fixed the lone-shard download. This PR re-derives RO-11's figures against the logs that exist now and fixes what the last day's logs still show: the pin lane drew its null control from a *shard* (8 of 9 shards refused on #2070 and 43 of 49 sites went unmeasured), its 120-minute budget cut the EXCLUSIVE tail of sites that had already run every shared driver green (the report called them "not started" after two hours of running), and the jobs and the rule both said a `GITHUB_TOKEN` push leaves a *held* run to approve, which the branch-level run query contradicts.

The dispatch arm is deliberately **not** built: the sibling lane `R9-RC-AUTOFIX-GOVERNANCE` measured that dispatching `governance.yml` from the autofix job restores only 3 of the 5 ABSENT required contexts (`pr-contract.yml` and `budget-raise-gate.yml` take no `workflow_dispatch` trigger), so a bot tip stays unmergeable and the arm fails the cost test. What this PR buys is the lane's own claim: **the pin lane measures and pins inside its budget on a real head**, and reports what it cut when it cannot.

## Head

`7f40401c7` on `handoff/r9-ci-1` — the merge of `origin/main` `70b50c573` (#2072) into the fix, whose own commit is `a5005008d` (its arms came first at `5ae1c1608`, red at `23d354970`). The merge brought five files, none of them one this diff or the pin lane reads: `CLAUDE.md`, `dev/governance/roles/fixer.md`, `dev/programme/carries/carry-1922.json`, `dev/programme/delivery/2072.md`, `tools/pr/prepr.sh`. The three CI proof runs below were taken at `a5005008d`'s tree, which the merge does not change in any file the lane reads.

## Pre-study, re-derived

`bash tools/audit/seat/autofix_statuses.sh <out-dir> 2` re-run 2026-10-09 (the newest 200 pull-request runs of `tests.yml`; 97 autofix jobs, 63 statuses read, 34 logs expired — counted, never read as a status). RO-11's own 20-run window is inside the expired set, so its figures are superseded rather than reproduced, and the cause it named is refuted by a log that survives:

| RO-11 claim (#2030) | What the logs print (2026-10-09) |
|---|---|
| `mutation-autofix` ended `skip-no-measurement` in 8 of 20 runs, "because a 345 s `env_drift.py` baseline consumed `--budget-minutes` before any site was measured" | 17 `skip-no-measurement` in the 48 readable mutation statuses. The one underlying log that survives (#2024, run 37750067882, job 113246917810) *measured* — `measure: skip-nothing-killed, 0 anchor(s)`, artifact `mutation-pins-1` uploaded — and the merge read the lone artifact as no measurement: #2060's download-root bug, fixed 2026-10-08 16:39. **0 `skip-no-measurement` after that merge.** The 357 s baseline is real (`baseline tests/env_drift.py: rc=0 failed=0 357s`, shard 3 of run 37925123437) and is not the cause: in that same shard the baseline ended at 11:47 and the drive then ran for 128 minutes. |
| `skip-measure-failed` in 2 | 2 in RO-11's window; 4 across the readable 200 — 2 pre-#2049 (one a head whose `fast` was red in the same run: an honest refusal), 2 after it (the tail cut below, and one more red head). |
| `closures-autofix` ended `skip-manual-repair-owed` in 4 | 3 readable, all `INERT READS UNDER-APPROXIMATED`, all pre-#2049. **0 after its merge**, against 8 `changed`. |
| `closures-autofix` ended `skip-failed-recording` in 6 | 0 readable — the class reads `changed` where it appears, which is round 1's change (a failed recording of a script the check did not name no longer blocks). |

Post-#2049 corpus (37 readable statuses, 2026-10-08 06:40 → 2026-10-09 15:16): `mutation-autofix` 11 `changed`, 7 `skip-no-measurement` (all before #2060), 2 `skip-measure-failed`, 4 `skip-not-unpinned`, 2 `skip-not-allowed`, 1 `skip-nothing-killed`, 1 `skip-head-moved`; `closures-autofix` 8 `changed`, 1 `skip-not-allowed` (the loop guard, which `ci-autofix.md` documents as open).

## The change

- **`null_for` reads the whole pool.** `whole = list(pool)` is taken before `--shard` slices it, so every shard of one refusal drives the same null control, which is the RUN's artifact (driven under every driver in play on unmutated trees), not a shard's. #2070's head `3ecb86adaf` (run 37890872462) refused 8 of its 9 shards in under a minute — "no full-line comment in any file in the pool" — because the anchor deal landed those shards on files with no whole-line comment; 43 of 49 sites were never measured and that head's fix review was blocked on 40 of them.
- **`SKIP-BUDGET-TAIL` is its own verdict.** A survivor whose EXCLUSIVE tail the deadline cuts is not a site the admission never started: the report line ("TAIL CUT … it survived every shared driver"), the `PIN KILLED:` summary's count and the refusal's headline all name it apart, and the summary's head — what `measurement()` reads — is unchanged.
- **The budget is 260 minutes**, the step 340, the job 350, `SITES_PER_SHARD` 5 (was 6), `MAX_SHARDS` 12 (was 10), `max-parallel` 12. Derived from the run that measured this pool rather than estimated it (37925123437 shard 3, base `b2b6acd64`, 5 `draw_range.py` sites): a site's shared work is `sum(closures.json recorded.seconds for drivers whose closure reaches the file)` ≈ 3160 s, the 3-worker pool cost 1.46x that, so five sites took ~128 min of shared work and their tails (stress.py and harness_headers.py, a settle and a run each, ~980 s a survivor) ~114 min more — ~248 min against a 120-minute budget, which is why every tail was cut and the shard refused having completed nothing. The step's 340 covers the worst run still in flight at the deadline (`driver_timeout` is `TIMEOUT_SCALE` 3 × `boost_drift_replay.py`'s 1489.6 s ≈ 75 min) plus checkout, pip and upload.
  - Rejected, with measured costs: reusing a measured baseline (the eager phase is env_drift's ~6 min of a 248-minute shard — round 1's "the baseline was not the cost" confirmed by the surviving log); six sites a shard (~291 min, past the step's ceiling); `--jobs` 4 (the pool cost at 4 workers is unmeasured; RCA-1565's 0.47x-3.27x band is a 3-worker measurement); speeding up `boost_drift_replay.py` (the largest single win, ~47 % of a site's shared seconds, but a test-harness change, not this lane's — it stays in the R9-RO-9 carry).
- **Stale claims corrected** where they are read: the three autofix jobs' held-run comments and `dev/governance/rules/ci-autofix.md`'s "Governance's contexts come from the held run once approved (#1514)". A `GITHUB_TOKEN` push creates **no** `pull_request` run (measured on two bot heads — #2070 at `a9ba0b88`, #2066 at `63084989`: the four dispatched runs only, and the approve step's own 60 s poll printed `no action_required run ... appeared`). The approve step stays as the fail-soft insurance #1276 added it as. Also the "each in its own subdirectory" comment above the shard download (#2060's carry, closed by R9-RO-9 without it).

## Mutation proof

`python3 tests/entities.py` — the closure the checks live in — run once per mutant in a separate worktree at this head (`a5005008d`), the tree restored after each run. Each mutant reddens **1 or 2 of 2252 checks**, the ones that pin that line:

- **The arm first.** Before the fix, the seven checks were red at `23d354970` (`5ae1c1608`): `7 of 2245 ENTITY CHECKS FAILED`, and those seven are the only failures — every other `FAIL` line in that output is a deliberate negative control of the `a3:`/`a4:`/`hb:`/`a12:`/`a13:` classes. After the fix the same closure prints `ALL 2252 ENTITY CHECKS PASSED`.
- `null = null_for(whole)` → `null_for(pool)`: 2 failed — `a shard whose files hold no whole-line comment inherits the whole pool's null control…` and `and an empty pool passes before a null control is sought` (the wiring pin).
- `verdict[i] = "SKIP-BUDGET-TAIL"` → `"SKIP-BUDGET"`: 1 failed — `the split admits a mutant on its shared work and charges the EXCLUSIVE tail only to a survivor that reaches it; a lazy driver costs one run`.
- the tail-cut report line reverted to the admission wording: 1 failed — `a budget refusal names a tail-cut site as one that survived every shared driver, a never-started one as not started, and a tail-cut-only run as no verdict measured -- all refused, none PASSED`.
- `if tail and not cut:` → `if False:` (the refusal's headline branch): 1 failed — the same refusal-wording check.
- the tail term dropped from `PIN KILLED:`'s parenthesised split: 1 failed — `the pin summary counts budget cuts, exclusive-tail cuts and timeouts apart from survivors, and names a survivor's remedy only when one survived`.
- `SITES_PER_SHARD, MAX_SHARDS = 5, 12` → `6, 10`: 1 failed — `the pin shard count scales with the diff's new sites, five a shard, capped at twelve, and sizes the matrix the shards run`.
- tests.yml `max-parallel: 12` → `10`: 1 failed — the same shard-count check, through its derived `f"max-parallel: {MAX_SHARDS}"` clause.
- tests.yml `&& budget=(--budget-minutes 260)` → `120`, and the step's `timeout-minutes: 340` → `170`: 1 failed each — `mutation-nightly, mutation-ledger and the pin step each pass a budget`.

The perturbation the harness moves under is those nine mutants, plus the budget pair on a real head (`120` in the incident vs `260` here, § Null control): the same code and the same pool, cut on one side and measured on the other.

## Null control

- **A head CI kept green.** Draft #2079 carries this branch alone (no production site added) with base `main`. `mutation` concluded **success**, `mutation-pin-plan`, `mutation-pins`, `mutation-autofix` are all **skipped**, and no bot commit exists: the change does not fire, and pins nothing, where the lane was already green. Its Tests run (38034950357) concluded success with no non-green job.
- **The budget arm, on a real head, pinned all five sites.** Draft #2080 carries a head whose diff adds the five `draw_range.py` expressions the incident's shard sat on — rewritten equivalently (operand order, `1.0 * 10`) so the ratchet draws new sites on the same heavy driver set — over this fix as its base. Its shard drove all five inside the budget and pinned every one: `PIN KILLED: 5 pinned, 0 left unpinned`, `measure: measured, 4 anchor(s)`, `shards merged: measured`, `AUTOFIX: changed` — and the bot pushed `ci: pin killed mutants`, head `61fbb9dd7` (Tests run 38043679085). The incident's shard 3 on the same five lines (Tests run 37925123437, base `b2b6acd64`) had 120 minutes: it spent 128 of them on the shared sweep and its five tails were then cut — `MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s) timed out, 5 not started for --budget-minutes` — because the budget ran out *before the drivers that kill these sites returned*. 260 lets the sweep finish, and the killers pin them.
- **The before arm for the shard fix is the incident itself.** At #2070's head `3ecb86adaf` (run 37890872462) eight shards refused with `no full-line comment in any file in the pool`; at the same head content on this fix (draft #2082, run 38043679149) those shards print `PIN KILLED -- {4,5,6} new unpinned site(s) ... to drive` and start the drive. The run then stops on that head's own `tests/structure.py` budget (`dead_top_level_symbols 2 > 1`), a fixture artifact of stacking an older branch's tree on today's main — not this fix's claim.

## Figures

- 63 statuses read of 97 autofix jobs, 34 logs expired: `bash tools/audit/seat/autofix_statuses.sh <out-dir> 2`, 2026-10-09.
- the pre/post-#2049 split of those statuses: counted from `<out-dir>/status.tsv` against #2049's merge time (2026-10-08T06:40:23Z).
- the incident's shard timeline (357 s env_drift baseline, 128 minutes of shared work, the five tails cut): `gh api repos/tvofi/heatpump_optimizer/actions/jobs/113802408312/logs`.
- the lone-shard log that reads a measured shard as no measurement: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/113246917810/logs`.
- 5 sites added by the proof head, one shard: `python3 tests/mutation_table.py --scope changed --base origin/main` (draft #2080's head).
- 49 sites added by #2070's head, ten shards: the same command at draft #2082's head.
- the fix head's checks — only `pr-contract` non-green, and that on a proof-only draft body: `gh api repos/tvofi/heatpump_optimizer/commits/a5005008d77254ceeca7ed65bdfbdf92e3ef4afa/check-runs`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/policy_lint.mjs`: TOTAL: 0 error(s) across 40 policy file(s); `--budgets`: `.claude/rules/ci-autofix.md` 91/96 lines, 1466/1469 tokens (the correction pays its own way inside the cap).
- `PYTHONPATH=tests/hastub python3 tests/closure.py selftest`: ALL 57 closure shrink pins PASSED.
- `python3 tools/pr/ci_predict.py --base origin/main`: CI PREDICT: no closures or fast red predicted.
- the proofs' own runs and jobs: Tests 38043679085 (#2080, shard job `mutation-pins (1)`, autofix job `mutation-autofix`), Tests 38043679149 (#2082), Tests 38034950357 (#2079), all read through `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: FULL — `.github/workflows/tests.yml` changes the gate itself, so every closure is suspect.

## Red checks

- `pr-contract` on the three proof drafts (#2079, #2080, #2082) is red: their bodies are proof-only and carry no `## Red checks` answer, and they are tvofi-authored rather than `hpo-author`. That is `pr-contract` working as designed on a carrier that is not a delivery. No cheaper detector is owed: the drafts exist to move one behaviour on a real head, and they are closed rather than merged.
- On this branch's own head, CI has no red: `gh api .../commits/a5005008.../check-runs` lists `pr-contract` alone as non-green, and that red belongs to the draft's body, not the branch's code.

## Forward-carry

- **The `ci-watch.sh --self-test` fixture** the sibling lane needs (they own the file): head `a9ba0b8874092db8780f93fa290b282b5ce200b5` (a `ci: pin killed mutants` push) carries **30 completed check-runs and nothing pending**, with **5 of the 17 required contexts ABSENT** — `policy-docs`, `wave-script`, `pr-contract`, `env-matrix`, `budget-raise-gate`. Enumerated with `gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` against ruleset 23698884's context list.
- **The dispatch arm's refutation** belongs in that lane's brief: dispatching `governance.yml` restores 3 of 5 ABSENT contexts; `pr-contract.yml` and `budget-raise-gate.yml` take no `workflow_dispatch` trigger, and `pr-contract`'s job is `if: pull_request || merge_group`, so a dispatched run would SKIP — and a skipped required context satisfies the ruleset, which is the false-green `tests/entities.py` already refuses by refusing that dispatch.
- The R9-RO-9 carries this lane does not take: the pin drive's ~2000 s a killed site (driver ordering), and `tests/boost_drift_replay.py` timing out as a mutation driver on two sites a run.

## Friction

- `ci-autofix.md: stale`: the rule said a `GITHUB_TOKEN` push's runs wait `action_required` and that Governance's contexts come from the held run once approved; measured 2026-10-09 at two bot heads, no run is created at all. Corrected in this diff.
- `orchestrator.md: cost`: while cleaning up a stray process of my own I killed the R9-UX-7 seat's mutant loop (pgid 37696, `hpo-seats/r9-ux-7/mutate.sh` and its `tests/entities.py` child). That seat has been told to re-run and to check for half-written evidence. From here I kill only a pid I started.
- `brief-citations.md: unclear`: the architect note partitions `.github/workflows/governance.yml` as "the three autofix jobs"; those jobs live in `.github/workflows/tests.yml`, and `governance.yml` holds none of them.

## Approval

This diff edits the code-owned `.github/workflows/tests.yml` and the policy rule `dev/governance/rules/ci-autofix.md` (plus the generated `.claude/rules/` and `.cursor/rules/` copies). It needs tvofi's approving review at the head before merging. No budget file is raised: `tests/structure.py` passes at the merge base and at the head, and `policy_lint --budgets` shows `ci-autofix.md` inside its cap.
