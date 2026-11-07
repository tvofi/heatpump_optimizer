R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT: where the 06 Nov nightly's 320 drain draws went, and three changes that raise pins per night.

The owner asked: measure from scheduled nightly run 42139479636's mutation-ledger shard logs where the drawn mutants go, then make the sound changes that raise pins per night. The measurement (`## Figures`) splits the 320 draws into: 90 killed, 44 lives, 1 timed out, 185 not started for `--budget-minutes`. Of the 90 kills, only 20 landed as pins. The other 70 had already been pushed by workflow_dispatch run 42135552492. That run started 33 minutes earlier on the same UTC date, so it drew the same slice under the same date seed 20261106.

Three changes, each tied to one line of that breakdown:

1. **The seed is the run id** (`nightly.yml` mutation-ledger, `--seed "${{ github.run_id }}"`). This is aimed at the 70 duplicate kills. Every run draws from the unpinned stock as it stood at its own checkout. So two runs on one date, a dispatch beside the schedule, drew one slice twice and the later push landed 22% of its kills (20 of 90). A run's four shards share one id, so they stay disjoint. The seed is printed in each `DRAIN SHARD` header, so a night's draw still replays. mutation-nightly keeps its date seed: it records nothing, so a duplicate draw there costs no pin.
2. **Admission charges no reach-free pair** (`drive_pool` and `drive_pin_pool` take `free`; `main()` passes `reach_free`). This is aimed at the 185 unstarted sites. Each mutant was admitted only if the sum of all its shared drivers fit before the deadline, and that sum included pairs `reach_skip` drops without a run. On the same draw those pairs are 37% of the shared pairs and 13% of the charge (`drain_admission_probe.py`). The charge now counts only runs that happen. `drive()` keeps its own check for lazy drivers, whose trace exists only after their deferred baseline.
3. **`--budget-minutes 270`**, the owner-allowed time raise, also aimed at the 185 unstarted sites. At 240 the four shards closed admission 16-80 minutes before the budget deadline, and the longest job ended 225 minutes into its 330-minute timeout. 270 is mutation-nightly's own sizing under the same timeout, leaving the same 60 minutes for runs in flight.

Alternatives considered, and why each lost:
- **More shards or `--jobs`.** The runners have 4 cores (`nproc` 4) and `--jobs 4` already uses them. More shards adds runner-hours without any measured share of the loss that it would recover.
- **Dropping or reordering a costly driver.** `tests/features.py` kills 130 of the 194 kills across both runs' logs, so dropping it loses coverage.
- **Optimistic admission** (charging less than a survivor's full sweep). It would re-open R9-F10.12's overrun and bias the measured prefix toward cheap mutants.
- **Draw de-duplication against existing pins.** It is already in place: `unpinned_sites` excludes every disposed site before `drain_pool`. What was missing was de-duplication between concurrent runs, which change 1 provides.
- **Survivor triage.** It stays manual, per `ci-autofix.md`; nothing here touches it.

The pins-per-night after-figure is owed on a workflow_dispatch nightly from `main` after this merges. The `mutation-ledger` jobs run only on `refs/heads/main` (`if: github.ref == 'refs/heads/main'`), so no dispatch on this branch measures them. No seat instrument requests a nightly dispatch either (`tools/audit/seat/INSTRUMENTS.md` lists none). The before-figure is run 42139479636, plus dispatch 42135552492 as the run it collided with. The after run, owed by the seat that lands this PR (`gh workflow run nightly.yml --ref main`, nightly.yml's own recipe), reads the same way, with `nightly_drain_breakdown.py` over its four shard logs, `--prior` naming any run that pushed during it. A dispatch on the same date as a scheduled run no longer duplicates its draw.

## Head

2fef6b26ac392e49366a8d4acb9b26f4a1162a7f, merge base a37c58e5f32123b4028e90983799dc2aa81816f8. Since the kept body's head 6a6b04ac6 the branch moved by four commits: 37d64edf2 (`record: the delivery row for #3269`), 221154c0b (merge of origin/main), a37c58e5f's merge into it, and the merge commit 2fef6b26. The merges brought in main's own commits only: the added lines of `nightly.yml`, `tests/mutation_table.py` and the two harnesses against the merge base are identical at 6a6b04ac6 and at 2fef6b26 (checked as the +/- lines of each file's diff). origin/main has since moved to 4b5d771bd; the head is held still for this body re-take, so it is not merged again here and `tools/pr/prepr.sh --body-check` is the run for the body.

## Mutation proof

Each fix line was deleted in its own copy of the 2fef6b26 tree, and `tests/entities.py` was run (`PYTHONPATH=tests/hastub`). All three deletions re-ran at 2fef6b26 and each gave `1 of 2646 ENTITY CHECKS FAILED`; the failing check's name was not re-read in that run, so the names and values below are the kept body's, taken at 6a6b04ac6 where the code lines are identical:

- `drive_pool`'s `and not (free and free(m, s))` deleted (re-run at 2fef6b26): `1 of 2646 ENTITY CHECKS FAILED` -- `FAIL budget admission charges no pair reach_skip frees, in both schedules, and main() hands the schedule its reach predicate` (the serial schedule reads `['SKIP-BUDGET'] * 4` where `['LIVES', 'LIVES', 'SKIP-BUDGET', 'SKIP-BUDGET']` is owed).
- `drive_pin_pool`'s `and not (free and free(m, s))` deleted: `1 of 2646 ENTITY CHECKS FAILED` -- the same check (the split reads `['SKIP-BUDGET'] * 4` where `['LIVES'] * 4` is owed).
- `main()`'s `free=reach_free` deleted: `1 of 2646 ENTITY CHECKS FAILED` -- the same check (`"free=reach_free)" in _MUT_BODY`).
- The seed and budget lines are pinned by `mutation-ledger measures without a write grant and mutation-ledger-push writes only rows` and `mutation-nightly, mutation-ledger and the pin step each pass a budget`, which now require `--seed "${{ github.run_id }}"` and `--budget-minutes 270`. At the merge base, that first check fails with `missing=['--seed "${{ github.run_id }}"']`.

## Null control

- The branch's code base (6a6b04ac6's parent, 80016a71f567) runs commit a567652fa's `tests/entities.py` with base `mutation_table.py` and `nightly.yml`: `2 of 2646 ENTITY CHECKS FAILED`, exactly the two checks above (`TypeError("drive_pool() got an unexpected keyword argument 'free'")` and the seed). The head reads `ALL 2646 ENTITY CHECKS PASSED`.
- The new check carries its own null: a `free` that frees nothing closes both schedules at once (`['SKIP-BUDGET'] * 4`, no run), as charging everything did.
- The breakdown rule fails closed: a drawn site no class reads prints `UNCLASSED` and exits 1. It did so on dispatch 42135552492's shard 3 (`pump_schedule.py:103 CLAMP_DROP -- killed by tests/features.py, but its anchor also covers a site no run killed`) before the `split` class existed. With that class, all eight shard logs classify every drawn site.
- `killed new` without `--prior` equals `killed` (shard 1: 14 and 14). Each run's `killed new` equals the file count of the ledger commit its push made: 20 for 42139479636 (b346319a6, `20 files changed`) and 104 for 42135552492 (5d75a576f, `104 files changed`).

## Figures

Shard logs are `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs` for jobs 127635902545, 127635902861, 127635902894, 127635902936 (run 42139479636) and 127622647328, 127622647263, 127622647186, 127622647350 (dispatch 42135552492), saved one file per job.

- Breakdown of run 42139479636, `python3 dev/audit/harnesses/nightly_drain_breakdown.py <4 scheduled shard logs> --prior <4 dispatch shard logs>`:
  - shard 1/4: drawn 80, killed 14, killed new 0, lives 6, split 0, timed out 0, not run 60; slack 55 min
  - shard 2/4: drawn 80, killed 35, killed new 20, lives 22, split 0, timed out 0, not run 23; slack 16 min
  - shard 3/4: drawn 81, killed 21, killed new 0, lives 8, split 0, timed out 1, not run 51; slack 80 min
  - shard 4/4: drawn 79, killed 20, killed new 0, lives 8, split 0, timed out 0, not run 51; slack 37 min
  - total: drawn 320, killed 90, killed new 20, lives 44, split 0, timed out 1, not run 185
  - Rule: the harness docstring, one class per drawn site.
- Breakdown of dispatch 42135552492, the same command over its 4 logs with no `--prior`: drawn 320, killed 104, killed new 104, lives 66, split 1, timed out 1, not run 148; slack 23-40 min per shard.
- mutation-nightly (job 127635903188) is the re-verification lane: it records no pin, so it adds none to pins per night, and no change here touches it.
- Job wall clock: `gh api repos/tvofi/heatpump_optimizer/actions/runs/42139479636/jobs` started_at/completed_at. The longest mutation-ledger shard is (2), 00:54:49Z-04:39:03Z, 225 minutes of `timeout-minutes: 330`.
- Admission share, `python3 -I dev/audit/harnesses/drain_admission_probe.py <tree at 785c2b604> OUT.json -- --scope full --drain DIR --max 320 --jobs 4 --seed 20261106`, then `--summary OUT.json`:
  - mutants 320; shared pairs 6028, reach-free 2234 (37%)
  - admission charge 132.6 h, reach-free 17.8 h (13%)
  - median charge per mutant 23.8 min charged, 20.2 min without the reach-free pairs
  - 785c2b604 is the scheduled run's head: same 3091 unpinned sites, same seed, same 320-site union of the four shards. The seconds are this container's baselines, so the shares are the figure and the hours are not.
- Killing drivers: `sed -n '/DRAIN SHARD/,/DRAIN: /p' <8 shard logs> | grep -o "pinned .* -- killed by tests/[a-z_]*.py" | awk '{print $NF}' | sort | uniq -c`: tests/features.py 130 of 194.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tools/audit/archscore/score.py --diff a37c58e5f`: Architecture score: dS +0.0000 NULL (the diff touches no scored production module).
- Gate scope, `python3 tests/closure.py select --diff a37c58e5f`: `MODE: FULL` (nightly.yml changes the gate itself), so the full suite is left to CI. `tests/entities.py`, the script pinning every changed line, ran locally: ALL 2646 ENTITY CHECKS PASSED.
- `python3 tools/pr/ci_predict.py`: not re-run at the moved head.

## Red checks

Read from `repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs?filter=all&per_page=100` across all pages, for 2fef6b26 and the three earlier heads 6a6b04ac6, 37d64edf2 and 221154c0b.

Concluded red at 2fef6b26:
- `pr-contract / pr-contract` (128444733261, run 42382938580). Class: this body. The step "Check the body against the contract" refused the kept body for `## Red checks: none` while `tests / nightly-status` was red. Answer: this re-take names it.
- `tests / nightly-status` (128434352318, 14:48Z). Class: a check that grades `main`, not required on `main-protect`. It printed `NIGHTLY FAILED: mutation-ledger (1), mutation-ledger (2), mutation-ledger (3), mutation-ledger (4), mutation-ledger-push, mutation-nightly, slow failed in the last verification dispatch`. The lanes are the cancelled lanes of dispatch 42369836867: it ran on main at 08fd676e9, started 11:50:04Z, and every lane except the two `nightly-ha` ones and `record-autofix` was cancelled at 12:09:16Z, 19 minutes in, with `mutation-ledger-push` cancelled at 12:09:17Z (`mutation-ledger (1)`..`(4)`, `slow` and `mutation-nightly` conclusion `cancelled`; none `failure`). This PR cannot be the cause: that run's head 08fd676e9 is a main commit that predates this branch's nightly.yml edit, and a workflow_dispatch run reads the workflow file at its own ref. Nothing on this branch is read by it. The `concurrency` group is `${{ github.workflow }}-${{ github.run_id }}` with `cancel-in-progress: false`, so the cancel came from outside the workflow; the log does not name who. A later dispatch, run 42382408131 on main at a37c58e5f (started 14:36:39Z), was still in progress when this body was taken: its `slow` and both `nightly-ha` lanes succeeded, and the `mutation-ledger` and `mutation-nightly` lanes were running. Answer: no change to this PR. The cheaper detector is the one that already ran: `nightly-status` names each lane and its run, and the diff check is `git rev-parse` of that run's `head_sha` against the PR's edit, a few seconds and no standing cost beyond that job. A detector that attributes before merge does not exist: `mutation-ledger` runs only on `refs/heads/main`, so no run on this branch reaches the changed lanes, which the opening text records. The nightly's own text asks that a fix be proven by `gh workflow run nightly.yml --ref main`; there is no fix to prove here, so no run id is owed beyond naming 42369836867 (the cancelled one) and 42382408131 (the in-flight one).
- `gate` (128435456876, run 42382939427, edit lane, 15:03Z) and `gate` (128446939177, run 42382938580, code lane, 15:43Z). Class: derived. The first printed `FAIL run(s) [42382938580] at this head are still being judged; their gate decides`, the second `FAIL pr-contract / pr-contract: failure (this run)`. Answer: both clear when `pr-contract` is green.

Earlier heads:
- 221154c0b: `pr-contract / pr-contract` (128427624688), the same refusal of the kept body for `tests / nightly-status` (128428266851, same failure as above, and 128417291088 at 13:30Z); `gate` 128417509338 (waiting on run 42377206719) and 128427776068 (`FAIL codeql / Analyze (python): cancelled`); `codeql / Analyze (python)` and `governance / instrument-self-tests` concluded `cancelled`, superseded by a later push. Cleared by the push of 2fef6b26 for the cancelled and waiting ones. The pr-contract and nightly-status reds at that head did not clear; they are the reds above.
- 37d64edf2: `gate` 128242269705, 128251802432 and 128255521603, each `FAIL run(s) [42319940810 / 42322858924] at this head are still being judged`. Class: derived, waiting on an in-flight run. Cleared by the push of 221154c0b.
- 6a6b04ac6: `gate` 128241848129 and 128241847931, `prelude` 128241711485 and 128241699537, `refresh` 128241711163 and 128241699572, all `cancelled` at 00:43Z by the next push. Class: superseded. Cleared by the push of 37d64edf2.

## Forward-carry

none

## Friction

- nightly-dispatch-instrument: unenforced: the brief says to request the before/after workflow_dispatch nightly "through the instruments", but `tools/audit/seat/` has no instrument that requests a nightly dispatch, and `mutation-ledger` runs only on main, so a fixer cannot take the after-figure before merge. Carry: dismissed: one-off for this group, whose after-run is named under Forward-carry for the seat that lands it; a fixer may not write the roster branch to land it there
