Fix review: blocked ff8b073827a8938d679ced28644cd28401f16dbc mutation-vacuous: cancel_superseded.priority_pass has_merge_verdict guard survives

bus-nonce: 526573753a97fcd80bdfc314652dc36b

Round 1 (first review of this group's part). Measured head ff8b073827a8938d679ced28644cd28401f16dbc; base 154dbb4c61652135381ce66646d23f7109d1c142.

## Block

- mutation-vacuous: in `tools/pr/cancel_superseded.py` `priority_pass`, replace `if has_merge_verdict(api, a.repo, pr) is not False:` with `if False:`. That deletes the live verdict lookup the sweep runs before it cancels. `cancel_superseded.py --self-test` then prints `58 checks, 0 failed`, rc 0 (ev/mutants.txt, M9). Carry 6 asks for this proof by name: "Mutation proof: dropping the verdict check cancels the verdicted run." The body's mutant (` or pr in protected` -> ` or False`) kills the pure `priority_plan` filter, but its tests hand `protected` in directly. Nothing pins the lookup that fills `protected` from posted `Fix review: merge` comments. The pause's own lookup, `ci_pause.pick`'s `_verdicted`, is pinned (M7 killed). The repair: a `priority_pass` self-test whose stub answers the comments read with a merge verdict, with `priority_cancel` on, asserting that no cancel is POSTed for that PR. M9 is the only survivor among the nine mutants I ran.

## Findings

- Ruling on carry 4 (the orchestrator's question): a priority-cancel mechanism that is built but switched off does **not** by itself meet the owner's "should be built in, no critical path, outside or hotfix PR should wait in CI queue". Here is the evidence either way.
  - **For the PR:** carry 6 (CI-PRIORITY-NO-VERDICT-CANCEL) amends carry 4 so that a queued run may be cancelled "only where the body's before/after measure (carry 4) shows that cancelling shortens a priority PR's queued wait". The shim result (21 cancels drained nothing) is a real measurement. So keeping the sweep's *queued-run cancel* off is compliant.
  - **Against the PR, point 1:** carry 6 (ii) makes holding the live half: "starting no rerun or dispatch of a non-priority PR's CI (the train and merge_pr unstale reruns, rerun helpers) while a priority run is queued". That is not built. At this head, `priority_step` with `allow_cancel` false returns at once. The only reruns it holds are its own. With nothing cancelled, those never exist. `merge_train.Train.unstale` (merge_train.py:4167, POST .../rerun at :4183) and `infra_rerun` (:4133) take no priority input. The body's enumeration dismisses `Train.unstale` as "protected by carry 6 (i)". Clause (i) protects runs from cancellation. It says nothing about holding reruns.
  - **Against the PR, point 2:** the before figure carry 4 asks for is not taken: "minutes a priority PR's first job waits queued, before ... re-measured at the merge base". The body gives the queue-wide median (33 min) and says so. With the switch off, no after figure can ever be taken, so the decision to turn it on has no instrument.
  - **Against the PR, point 3:** the same `priority_cancel` switch also disables the train's P267 pause (`ci_pause.CiPause.poll`, `PAUSE-HELD`). Carry 6 amends carry 4 only. Its evidence covers cancels of *queued* runs, which hold no runner slot. The pause cancels a victim's *non-completed* runs (`select(.status != "completed")`), including in-progress ones, which do hold slots. Extending the shim's zero to the owner-directed pause (tvofi 2026-10-28) goes beyond what carry 6 rules. That extension is `pending owner confirmation`.
  - **Net:** at merge, a critical-path, outside or hotfix PR's queued wait changes by nothing. The only live output is a `PAUSE-HELD`/holding log line.
  - **Re-cut owes:** carry 6 (ii)'s hold wired into the rerun sites the body's own enumeration returns; carry 4's priority-PR first-job before-figure at the merge base; and either the pause decoupled from `priority_cancel` or an owner ruling that carry 6 reaches it.
  - Carry: R10-CI-PRIORITY-PAUSE
- Body figures `roster_edit 310`, `orchestrator_tick 317` and `merge_train 670` checks are stated for fbdfd5ddf25f. At this head (after main's merge e54681df5b) I measured 311, 319 and 743, each 0 failed. These are main's added checks, not a regression. The body's figures need re-taking at the head they name. Carry: R10-CI-PRIORITY-PAUSE

## Evidence

- Setup: `git fetch --unshallow --tags origin` ok; `cloud-setup.sh --check`: `OK python3 is /opt/hpo/venv-ci/bin/python3`. Role contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty (current).
- Merge with main: `git merge-tree --write-tree origin/main ff8b0738` exits 0, tree 71fc0cf6d8, `LEDGER-MERGE: resolved tests/closures.json` (ev/HEAD.txt).
- Self-tests at head (ev/selftests-at-head.txt): ci_priority 12, ci_pause 14, cancel_superseded 58, roster_lib 92, roster_edit 311, beat_jobs 203, orchestrator_tick 319, merge_train 743 checks; all 0 failed.
- Mutants (ev/mutants.txt, driver ev/mut.py, each restored): M1 zombie record killed (2 FAIL); M2 `or pr in protected` killed (3 FAIL); M3 `if prio:`->`if True:` killed by crash (IndexError), as the body says; M4 `allow_cancel` hold removed killed (1 FAIL); M5 pause CP guard killed; M6 pause dormancy switch killed; M7 pause verdict guard killed; M8 `is_outside` in `tier` killed; M9 sweep `has_merge_verdict` SURVIVED (rc 0).
- `VERSION`, the manifest version, the notes heading and both claim files are untouched in the three-dot diff.
- Finder's harness: none named. The group is an instrument feature, and its controls are the carries' self-test items, which I re-ran above.
- CI on this head: `merge_train.py classify ff8b0738 --pr 3560` printed `rc=3 WAIT ... pending: gate red: none` on every poll from 17:52 to 17:55Z (ev/classify.log). This verdict is a block on a surviving mutant and does not depend on CI. `owed-reds` lists required contexts. No red was concluded at this head when I last read it, so no `## Red checks` answer is owed by this verdict.
- Carry 6 (iii), the queue share of main runs: the body reports 18 of 43 at 2026-11-11T23:26Z. That is a sliding-window figure I cannot re-derive at its timestamp; not verified.
