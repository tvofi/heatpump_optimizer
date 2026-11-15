Fix review: blocked 1b9db1a72251463faf31ddeaa586119ed950dfb0 ci-red: required gate reads red at this head (merge_train classify RED); code review otherwise found no defect

bus-nonce: 74339497b2b76c4c1965f8af537ec49c

## Block

- `merge_train.py classify 1b9db1a72251463faf31ddeaa586119ed950dfb0 --pr 3632` exits 1: `RED ... pending: none red: gate`, steady at 21:15:58, 21:18:12, 21:19:25 and 21:20:38 UTC (`ev/classify-log.txt`, `ev/classify-final.txt`). A head still red takes no `merge` (C8).
- Which `gate` is red: job 132950553246 (run 43759178696, the edit run whose other jobs all skipped) failed at 20:41:14 with `FAIL run(s) [43759179139] at this head are still being judged; their gate decides`. That is gate.py's deferral, not a judgement of this diff. The run it defers to, 43759179139, published `gate` job 132957878950 = success at 21:06:37, and every required job in that run passed (`pr-contract / pr-contract`, `governance / policy-docs`, `governance / instrument-self-tests`, `tests / closures`, `tests / mutation` and the rest).
- `latest_runs` keeps the worst gate per suite, and the train waits SWEEP_SETTLE_POLLS for gate-sweep.yml to re-run the deferred red beside a green. By 21:20:38, about 14 minutes after the green gate concluded, no re-run of job 132950553246 had been listed. The deferral red is not the author's defect. Once that job is re-run, this head's code review below carries unchanged: no finding of my own blocks it. Carry: dismissed: evidence, not a finding

## Evidence

- Round: first (no prior reviewed head). Head measured: `1b9db1a72251463faf31ddeaa586119ed950dfb0`, the PR's head as fetched and as the body names it; base `98847b99d7bb3238686efd6869f805c89c6d1ff1`. `git diff <merge-base>...origin/main -- dev/governance/roles/` empty: contract current.
- Diff (three-dot): `tools/policy/policy_lint.mjs` (one `POLICY_GLOBS` regex plus a two-pin `assertAcceptance` arm) and `dev/programme/delivery/3632.md`. No `custom_components/` line; `VERSION`, manifest, `RELEASE_NOTES.md` and `tests/golden/` untouched (0 diff lines), so no claim-file check owed (`ev/diff-files.txt`).
- RESULT mutant-1 (glob line deleted): `node tools/policy/policy_lint.mjs` exit 1, `FIXTURE OVER-FIRES: checkCoverage reported dev/governance/dimensions/criteria/D10-criteria.md` — killed (`ev/mut1-remove-glob.txt`).
- RESULT mutant-2 (my own, glob widened to a subtree `[A-Za-z0-9_.\/-]+`): exit 1, `FIXTURE VACUOUS: checkCoverage did not report .../criteria/sub/D10-criteria.md` — killed; the deep-path arm is not vacuous (`ev/mut2-subtree-glob.txt`).
- RESULT null control, base: a throwaway tracked `dev/governance/dimensions/criteria/X-criteria.md` draws `ERROR [coverage] ... matches no POLICY_GLOBS pattern`, `TOTAL: 1 error(s)` (`ev/null-base.txt`). At head the same file draws no `[coverage]` error, only `[index]` and `[budgets]`, `TOTAL: 2 error(s) across 53 policy file(s)` (`ev/null-head.txt`) — matches the body.
- Figures re-derived at head: `TOTAL: 0 error(s) across 52 policy file(s)`, `FIXTURE ok: 93 error(s) hold 278 pins` (base: 276; the +2 is the `pins += 2` the new arms add and both arms are shown live by the two mutants, so the movement is earned) (`ev/head-policy-lint.txt`); `--budgets` byte-identical base vs head (`ev/budgets-diff.txt`); `RULES-SYNC ok`; `STRUCTURE RATCHET PASSED`.
- Byte-identity claim vs p2 `da868a90ffa5`: lines 255-272 of `policy_lint.mjs` identical between p2 and this head (`ev/p2-glob.txt`).
- Class: the body states one seam (one directory one level below the dimension briefs) and the issue none further; a one-seam class, no enumeration rule owed. No finder's harness: the defect is a grader refusing a not-yet-landed directory, and the null control above is its harness, rebuilt by me from the body's description (disclosed as the reviewer's).
- Merge with origin/main: `git merge-tree --write-tree origin/main <head>` rc 0, no conflict (`ev/merge-tree.txt`).
- Red checks: the body reports none; the review packet's digest read `gate` as failure at render while `merge_train.py classify --pr` reads it pending (`red: none`); classify decides (`ev/classify-log.txt`).
- Forward-carry: none named, none owed (p2 dispatch is the orchestrator's, stated in the body).
- Red checks owed (`merge_train.py owed-reds`, `ev/owed-reds.txt`): `gate` is in the set. Its only red at this head is the deferral above, which no cheaper detector predicts because it is CI's own run-ordering. The body's `## Red checks: none` predates it.
- Round: first. The head did not move during the review (PR `head.sha` = `1b9db1a72251463faf31ddeaa586119ed950dfb0` at read).

## Findings

- Follow-up: the deferred `gate` job 132950553246 at this head was not re-run by gate-sweep within about 14 minutes of the green gate at run 43759179139 (21:06:37 to 21:20:38 UTC). That leaves the head RED to `classify`. This is a one-head observation with no null control, so it is not an established finding; the orchestrator's re-run of the job settles this PR. Carry: dismissed: single unmeasured observation; re-run of job 132950553246 is the orchestrator's routine action
