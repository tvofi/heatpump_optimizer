Fix review: blocked 8be64a110fa4e741889920c4eff2b6b4cb99cf3a root-cause-unanswered: arch-score went red, unanswered

bus-nonce: 65e9c0a8c8965d45d266a32bed605367

Round: 4. Round 1 was `Fix review: blocked b891dfa04 mutation-survivor`, round 2 was `Fix review: blocked 8be64a110 carry-missing` (no roster SHA), and round 3 was `Fix review: blocked 8be64a110 carry-missing` (the carries had no controls, and the push-lines carry was half refuted). This round is the minimal re-cut that the three-round rule calls for, at the same code head. Round 3's finding is fixed: all four carries now have controls, and I reproduced each control myself. What blocks now is step 11, and the fix touches only the body.
Measured head: 8be64a110fa4e741889920c4eff2b6b4cb99cf3a (ev/HEAD). I re-read it with `git ls-remote` after CI concluded and it had not moved. The PR's updated_at is 14:51:30Z.
Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current. origin/main is at 64b0ae690, and the merge base is e59f0291a.
Environment: /opt/hpo/venv-ci/bin/python3, CPython 3.14.7, with PYTHONUNBUFFERED=1 exported.

## Blocking (step 11)

All of the head's workflows had concluded when I read the check-runs API with filter=all (66 runs, ev/check-runs.tsv); `closures` was the last, at 15:07:41Z. The latest `pr-contract` run, 118132821783, started at 14:58:48Z. That is after every other red at this head had concluded, and the body had not changed after it was last edited at 14:51:30Z. The run read the body and refused it (ev/log_pr-contract_118132821783.txt):
`record red-history ... every failure conclusion across them: arch-score, instrument-self-tests, nightly-status`
`ERROR [pr-body] ... check \`arch-score\` is red and \`## Red checks\` does not name it.`
`arch-score` failed twice at this head: job 118114889124 and job 118124086255. Both died on `API rate limit exceeded for installation (HTTP 403)` (ev/log_118124086255.txt, ev/log_118114889124.txt). The later runs 118129031265, 118129773400 and 118129779749 are green. The body's `## Red checks` names `nightly-status` and `instrument-self-tests` but not `arch-score`, and `arch-score` is not one of the exempt checks (`nightly-status`, `delivery-status`). This head also has red runs of `env-matrix` (118114889280, `the GitHub API is unreachable`) and `validate-hacs` (118114888472, `GitHubRatelimitException`). Both were re-run green, and `pr-contract`'s range list no longer names either. Still, the body does not answer them, and the earlier `pr-contract` run 118129038012 refused all three.
The fix is in the body only: add `arch-score` (and to be safe `env-matrix` and `validate-hacs`) to `## Red checks`, give the 403 installation-quota cause with the job ids, and give the cheaper-detector answer. Then the next `pr-contract` run has to pass. No code change is needed.

## Carry controls, re-run by me (step 10). All four reproduce.

Roster: `handoff/audit-r10-roster` tip is 1dc0151de365911c7b635dc87d26333317731b3e (ev/roster_tip.txt), which is the SHA the body cites. Four `append-carry` commits come after ebf81fc1d (ev/roster_log.txt). Each new entry starts `Supersedes the uncontrolled #2444 entry at roster ebf81fc1d` and has a Control (precondition), a Null control and a Re-measure instruction. The old uncontrolled entries remain in place because the roster is append-only, and the new entries mark them as superseded. This does not block.
- c1, seven unwired self-tests (R10-CI-LAYOUT): I ran the carry's loop verbatim at the head and got 24 `wired` and 7 `unwired`. The seven are exactly the named files: check_scopes.py, merge_throughput.py, worktree_gc.sh, coverage/partition.py, record-predicate/row_files_replay.py, approve_held_runs.sh and head_note.py (ev/c1_loop.txt). Null control: I planted tools/pr/zz_probe.py with `--self-test`, and the loop printed `unwired tools/pr/zz_probe.py` (24 wired, 8 unwired). The 24 wired files stayed wired. I then removed the probe (ev/c1_null.txt). The carry's other null arm, that the new check exits 1, is the receiving group's future work and cannot be measured now.
- c2, push and merge lines (R10-CI-LAYOUT), on a throwaway worktree with one line mutated at a time and restored, and `git status` clean afterwards (ev/c2_*.txt):
  - Unmutated: handoff_push.sh rc=0, merge_pr.sh rc=0 (`12 checks, 0 failed`), open_pr.sh rc=0 and update_pr.sh rc=0 (`46 checks, 0 failed`).
  - handoff_push.sh lines 75, 94 and 108, each replaced by `true`: rc=0 every time. These lines are unpinned.
  - merge_pr.sh line 169 replaced by `exit 0`: rc=0 with `12 checks, 0 failed`. This line is unpinned.
  - open_pr.sh line 44 replaced by `true`: rc=1 with `46 checks, 4 failed`. update_pr.sh line 58 replaced by `true`: rc=1 with `46 checks, 2 failed`. Both lines are pinned.
  - These match the carry and the body's narrowed Forward-carry line. `grep -n` finds no other push or `gh pr merge` line in handoff_push.sh or merge_pr.sh: handoff_push.sh has three `bash "$_push"` sites.
- c3, census cost (routing): `r10_field_coverage_paths.sh` gives `RESULT misread=0` rc=0 at the head, with the nine inputs reading RUN and README SKIPPED. At fb9b3fc1f it gives `RESULT misread=8` rc=1. A copy of the harness with an added probe, custom_components/heatpump_optimizer/coordinator.py, reads SKIPPED, which is the current choice the carry describes (ev/c3_*.txt). The copy was deleted afterwards.
- c4, the Friction item (R10-BRIEFS-FOLD): this container's clone has no `seat/` line in `.git/info/exclude`, so it is the null state: `git check-ignore -v` returned rc=1 and `git status --short` showed `?? tools/audit/seat/zz_probe.py` (ev/c4_this_clone.txt). In a throwaway `--shared` clone with `seat/` appended, it printed `.git/info/exclude:7:seat/	tools/audit/seat/zz_probe.py` (rc=0), and `git status --short` did not list the file (ev/c4_affected.txt). Both control and null reproduce.

## Verified at this head

- Step 1/2, the mutation proof. I ran `python3 -I dev/audit/harnesses/r10_seat_selftests_mutants.py` on a clean worktree of the head, under PYTHONUNBUFFERED=1 (ev/harness_full.txt): 36 lines `== M0 rc=0`, then `grep -c ' KILLED'` = 34, with 0 SURVIVED and 0 NOT RUN, `RESULT survivors=0`, rc=0. `git status --short` was empty afterwards. S04, S04U and S30 are KILLED. This harness is the fixer's own, as earlier rounds noted, because no finder harness is committed (step 9).
- Figures (ev/figures.txt):
  - `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - `selftest_wiring: 37 self-testing, 37 wired, 0 unwired` rc=0, and `selftest_wiring self-test: 15 checks, 0 failed`.
  - `STRUCTURE RATCHET PASSED`, and `policy_lint.mjs --budgets` rc=0.
  - daemonize.py prints `SELF-TEST PASS` both with and without PYTHONUNBUFFERED.
- Step 5: VERSION, manifest.json, RELEASE_NOTES.md and tests/golden show an empty diff from the merge base.
- Step 13: `git merge-tree --write-tree origin/main 8be64a110` exits 0 against origin/main 64b0ae690, with tree ca4fcaab376f and no MERGE-CLAIM line.
- Step 7: the body's `## Head` names 8be64a110, the head I measured.
- CI: `instrument-self-tests` is success (14:24:37Z to 14:28:03Z), and so are `closures`, `coverage`, `mutation`, `policy-docs` and CodeQL. The re-runs of `env-matrix`, `validate-hacs` and `arch-score` are green. `nightly-status` is red, but that is main's red and the body answers it.

## Not re-derived

- The offline spy's `37 files, 0 refused`. Round 2 measured it at this same head, and I did not re-take it.
- The body's job-time figure (job 118026250746). I did not re-read it.
- The macOS sandbox-exec path, which this Linux seat cannot run.
- The gate scripts `tests/entities.py` and `harness_headers.py`. I cite CI for these.
