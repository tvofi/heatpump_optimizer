Fix review: merge 885d4751ade87cd22eebe9eb404b3755674f5083

bus-nonce: 07d283da92fa465163431abde5c105d7

## Round

Second review of PR #2955 (R10-ERREXIT-COUNTERMEASURES), measured at head 885d4751ade87cd22eebe9eb404b3755674f5083, which contains the round-2 fixer commit 9ca68c8c5. I re-read the head from the API just before writing this, and it had not moved. The role file is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, and origin/main equals the PR base e5ddba1fad5e6eccfeceaeaaa249bc459963405b.

## Round-1 blockers

- Block, `tests / closures` red with INERT READS UNDER-APPROXIMATED: resolved. At this head `tests / closures` (job 123741244321) is success, and its log prints `closure: committed closures cover every file this run touched` (ev/closures-summary.txt). `closures-autofix` was skipped, so the recording is the fixer's own. I checked the narrowed read myself: `_SHELL_DOMAIN` is 263 of 312 tracked files, and every one of them is in `tests/entities.py`'s committed closure except `tests/closure.py`, a gate file whose edit forces `full`. M5, which restores the unnarrowed read, is killed (see Evidence).
- Finding 2, A's unguarded domain: the arithmetic shape (d) is closed. M7a and M7b each drop half of the arm and are each killed. Shapes (a), (b) and (c) are disclosed and carried in the body (Findings below).
- Finding 3, absolute-path shells: closed. The basename match and the `env` strip are pinned by plants. M6 (the body's) and my M8 (the `env` strip removed) are each killed.

## Findings

- Surviving mutant: removing `"sh"` from `_EX_SHELLS` (M9, ev/mutant-M9.diff) leaves all 2474 checks passing. The shell-arm null control plants `python`, `bash` and default steps, but no `shell: sh` step, so the body's claim that A covers "default shell, bash, sh" is untested for `sh`. The tree has no `shell: sh` step today, so no live instance is missed. Owed: a `shell: sh` step in the `_EX_SHELL_ARM` plant, expected (3, 3). Carry: R10-ERREXIT-COUNTERMEASURES
- A's remaining unguarded domain, which the body discloses and both A and the frozen finder harness `r10_errexit_capture.py` share: (a) `prep && cmd` then `rc=$?`, (b) `export RC=$?`, (c) `rc=${?}`. Each has zero live instances. For (b) and (c), the control is a planted step under errexit that should yield hits=1 and today yields 0. The class's next finder needs this. It is not yet written in the roster entry's carry text at origin/handoff/audit-r10-roster 9a313042, so it still has to be relayed there. Carry: R10-ERREXIT-COUNTERMEASURES
- `tools/pr/ci_predict.py` predicted no closures red at round 1's 9d97a52d5 and does not see an in-process read whose path list is computed at run time. The body hands this predictor miss to `root-cause.md`'s seat. It is not settled here. Carry: R10-ERREXIT-COUNTERMEASURES
- Carry 4, the class proposal ("a workflow step's meaningful nonzero exit ended by errexit before the step reads it", I1–I4), is still unminted: this PR mints nothing by design. It stays open on the group's carries for the judge or orchestrator. Carry: R10-ERREXIT-COUNTERMEASURES

## Evidence

- RESULT entities head: `env -u BASH_ENV PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 tests/entities.py` at 885d4751ade87cd22eebe9eb404b3755674f5083 printed `ALL 2474 ENTITY CHECKS PASSED`, rc 0 (ev/entities_head.txt). This matches the body's 2474.
- RESULT mutants, each in its own detached worktree of 885d4751ade87cd22eebe9eb404b3755674f5083, with diffs in ev/mutant-*.diff and the check lines unique to each mutant in ev/mutants-summary.txt. The other FAIL lines (`a8:register_once`, `hb:positive_control`) are inner self-test output that a passing run prints too.
  - M1, gate-sweep ` || true` removed: `1 of 2474` failed, U0c, with the three rc-1 defects as in the body.
  - M5, `_SHELL_DOMAIN = [f for f in _SHELL_TRACKED]`: `1 of 2474` failed, B's pin, `read 312 of 312`, `sites=19`, with the 8 beatd.py defects as in the body.
  - M7a (mine), `\(\(` dropped from `_EX_TEST_HEAD` only: `1 of 2474` failed, null controls, `cases wrong=['if arith']`.
  - M7b (mine), `\(\(` dropped from `_EX_READER` only: `1 of 2474` failed, null controls, `cases wrong=['arith list', 'if arith']`.
  - M8 (mine), the `env` strip disabled: `1 of 2474` failed, B's pin, `plants missed=['env bash']`.
  - M9 (mine), `sh` dropped from `_EX_SHELLS`: survived (Findings).
  - I did not re-run M2, M3, M4 or M6. They are the body's, and round 1 confirmed M2–M4 on unchanged lines.
- RESULT finder harness: `dev/audit/harnesses/r10_errexit_capture.py` (sha1 03767097bf17a13cae0b52425482dcf6b1c3ebdb, as the body states), run over `git archive <ref> .github`, printed `hits=0` rc 0 at base e5ddba1f and at 885d4751ade87cd22eebe9eb404b3755674f5083 (ev/det_checks.txt). It is flat at both ends by design, as the body says. Round 1 confirmed its positive arm on M4 at 265/5/1.
- Merge: `git merge-tree --write-tree origin/main 885d4751ade87cd22eebe9eb404b3755674f5083` exits 0, tree 690f637ee, with no conflict and no claim-file involvement. Both merge commits on the branch, 885d4751a and 98c8ac24a, have exactly the tree an automatic merge of their parents gives (ev/det_checks.txt), so neither contains a hand resolution. The hand resolution the body describes is in d93e51afc, under the authored head.
- CI at this head, all pages (55 runs, ev/check-runs.tsv): every workflow concluded, with 37 success, 17 skipped and 1 failure. The failure is `tests / nightly-status` (job 123739895869). It grades main's scheduled Nightly (run 40835853528, lane `slow`), it prints that it is NOT one of the required contexts on main-protect and does not block a merge, and this diff reaches nothing it reads, so it is not this PR's. `pr-contract` ran twice after the last red concluded (21:24:25Z), at 22:05:55Z and 22:08:12Z, and both succeeded, so the body's `## Red checks` (closures, closures-autofix, nightly-status) passed the contract. `tests / mutation` is green, but the diff writes no production code line, so no mutant is drawn; my targeted mutants above stand in for it.
- Forward-carry: roster entry R10-ERREXIT-COUNTERMEASURES at origin/handoff/audit-r10-roster 9a313042906fd96dadc44944d30621bf7f504711 holds carry (4) (the class proposal) and the round-2 arithmetic carry with its control. The group will sit at `carries-open` while carry (4) is open, which the roster already uses for other merged groups.
- VERSION, the manifest version, the RELEASE_NOTES heading and both claim files are untouched. No commit in e5ddba1f..885d4751ade87cd22eebe9eb404b3755674f5083 carries a Co-Authored-By or Claude trailer.
- Figures re-derived: 263 of 312 read (exact), 11 sites (exact, from the in-tree check line under M8 at head: `sites=11 without errexit=[]`), 152 added closure entries (the three-dot diff adds 152 lines to tests/closures.json), and 2474 checks. Figures not re-derived, so not verified by me: the selection cost (116 of 300 merges already selected, 1 more would), the agreement lane's before/after `dead=2` (CI `governance / policy-docs` and `instrument-self-tests` are green at the head; my local `agreement.mjs` run was mis-invoked and is not evidence), and the historical parity trees.
- Instruments: I built none beyond sed one-line mutants. The scoped gate was not re-run, per the step-11 rule to cite CI's heavy runs.
