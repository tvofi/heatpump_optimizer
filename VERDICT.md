Fix review: blocked 5a5b2c4fca00886ffa425268ee9b604fcaf58045 root-cause-unanswered: gate

bus-nonce: 79332eeac2d420b8b3bf03f9fc68277b

Round 1 (first review of this PR by this seat). Head measured: 5a5b2c4fca00886ffa425268ee9b604fcaf58045, still the PR head at post time (refs/pull/3361/head).

## Block

Check `gate` (check run 128920160526, ci.yml "CI edit pr=3361", run 42540449051 attempt 1, 00:52Z) concluded failure at this head. Its log: `FAIL run(s) [42539949919] at this head are still being judged; their gate decides`. The body's `## Red checks` says "none" and answers nothing. That is rule 11's silence. I read it as an ordering race between the edit and code runs' gates, not a defect in the diff, and I name no cheaper detector.

Attempt 2 of that run (gate 128931727137) and the code run's gate (128931066114) are both success, so no red remains at this head. `merge_train.py classify` still prints `RED ... red: gate` on 5 runs spread over about 15 minutes, because `latest_runs` keeps the worst gate of each check suite. The attempt-1 suite is still listed under `check-runs?filter=all`. I did not re-run CI or touch it.

To clear: add one line to `## Red checks` naming `gate` (race between the two runs' gates, no cheaper detector, or whatever the author finds), and have the orchestrator run `merge_train.py unstale` so that classify reads GREEN. The code and its measurements need no change. Everything below holds at this head, so a re-review of an unchanged patch can carry (`review_carry.py`).

## Findings

- Residual: the review packet could not be rendered. `review_packet.py render` printed `UNAVAILABLE: git merge-base --is-ancestor 42454528717 origin/handoff/audit-r10-roster: fatal: Not a valid object name 42454528717`, and no packet file was written. A 11-digit run id (the 1760-job run in the body) is being passed where a commit is expected. I reviewed from the PR body, the live checks and the diff. Carry: #2731

## Evidence

- RESULT merge-tree origin/main vs head: clean (rc 0, no conflict; ev/merge_tree.txt). Merge base of head and origin/main: 19865e5a866c.
- RESULT claim files, VERSION, manifest, RELEASE_NOTES and goldens: none in the 12-file diff (`git diff 19865e5...HEAD --name-only | grep -E 'VERSION|manifest|RELEASE_NOTES|golden|claimed'` prints nothing). No fixture moved, so there is no drift to claim.
- RESULT gh_read_run.py --self-test: 13 checks, 0 failed (matches the body). RESULT stamp.py --self-test: RESULT stamp_self_test=pass. RESULT r10_codescan_wait_race.py --selftest: 14 checks, 0 failed. RESULT r10_red_list_lag.py --selftest: 5 checks, 0 failed (ev/selftests.txt).
- RESULT mutation, the fix deleted (two `if st >= 500 and size != 30` lines removed from `pages()`): `selftest: 14 checks, 3 failed pages['fallback', 'over50', 'many1760']`, rc 1. This matches the body (ev/mut_fallback.txt). The file was restored.
- RESULT mutation, loop bound reverted to `range(1, ghapi.MAX_PAGES + 1)`: `selftest: 14 checks, 1 failed pages['many1760']`. This matches the body's null control (ev/mut_bound.txt). The file was restored.
- RESULT null control, NON_JSON: the base `gh_read.py` with `invalid character 'S' looking for beginning of value` on stdin `--classify` exits 1, and the head exits 0 (ev/nonjson.txt).
- RESULT null control, write argv: `gh_read_run.py gh api -X POST ...` exits 2 with "not a read, so not run" (ev/write.txt).
- RESULT structure.py: STRUCTURE RATCHET PASSED. RESULT field_coverage.mjs: FIELD COVERAGE ok, refused=0. RESULT ci_predict.py: `no closures, fast, governance or instrument red predicted against 19865e5a866c` (ev/predict.txt).
- No budget file is in the diff, so no raise is owed. The body's `dS +0.0000 NULL` is a CI-green figure (arch-score, budget-raise-gate and closure-scope are success at this head). I did not re-derive it.
- Figures I did not re-derive: the live Pages and 502 measurements (run 40132661027 and per_page probes), the 1 lagging red in 379 lists, the 118 diff mutants and 26 survivors, the 360-mutant sweep at the old base, and the app_approve.sh 322 checks. They need live GitHub or long runs, and the heavy ones are CI's to cite. The body's bound probe on main's `pages()` is covered only through the mutation above.
- Forward-carry (rule 10): the body writes every item to #2731 as `Carry: #2731`. I did not open #2731. The roster-branch SHA is not named, and the carries are stated to be in the issue, not in a roster. I treat this as the body's disclosed choice.
- Enumeration rule (rule 6): the body names `git grep -n 'gh api' -- .github/workflows` (24 reads) and the urllib enumerator, and dispositions every seam in Forward-carry. No seam is left undispositioned. I did not re-run the grep.
- Version: the PR touches no VERSION, manifest or notes heading.
- CI at this head: all completed jobs are success or skipped except the attempt-1 `gate` above. classify rc 1, "RED ... red: gate", repeated (ev/classify.txt). The pr-contract job was skipped in every run, so the "pr-contract started after the last red" condition of rule 11 never held. The block is posted on that ground and on the unanswered `gate` red.
- Head: ev/HEAD.txt holds 5a5b2c4fca00886ffa425268ee9b604fcaf58045.
