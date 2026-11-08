Fix review: merge a379c307830addd67fc1abbcde3a71fdb16b8704

bus-nonce: ff70e4b19c34409f834ce2db553837d1

## Evidence

Round 1 (first-round review). Measured head a379c307830addd67fc1abbcde3a71fdb16b8704, base d2e4d2d10cfe15b9ec51c36422029718e8367f1c, from detached worktrees; head re-read via ls-remote before return, unchanged. Roles diff merge-base...origin/main: empty.

- RESULT harness (a) base, git shim advancing GIT_TEST_DATE_NOW 70 s per call (ev/finder-shim.sh): 22 passed, 2 failed, rc=2 (ev/shim-base.txt). The finding reproduces; failing rows are "unset ... not a byte more" and "set ... plus one role pack line", the two byte comparisons the body names.
- RESULT harness (b) head, same shim: 24 passed, 0 failed, rc=0 (ev/shim-head.txt).
- RESULT null control (c) head, no shim: 24 passed, 0 failed on each of 3 runs (ev/plain-head.txt).
- RESULT mutant 1: deleted the one production line (the GIT_TEST_DATE_NOW pin) at head (ev/mutant1-diff.txt). Under the shim the hook self-test fell back to 22 passed, 2 failed (ev/mutant1-shim.txt), so the mutant is killed.
- RESULT prepr.sh --self-test at head: 514 passed, 0 failed, rc=0 (ev/prepr-selftest-head.txt). With mutant 1: 513 passed, 1 failed, rc=2. The one failure is the new row, "FAIL the session-start self-test passes while git's clock ticks between its reports (null control) (got 2, wanted 0)" (ev/prepr-selftest-mutant1.txt). The row is real and fails when its check fails. It is wired like its sibling row above it: same `hk=$(...); r=$?; st "$r" 0 ...` shape, and on failure it prints the same tail of non-ok lines.
- Does any changed line newly let something pass? The pin is `: "${GIT_TEST_DATE_NOW:=$(date +%s)}"`, set only inside the `--self-test` branch. Its value is the current wall time, so relative dates are unchanged apart from being frozen. The hook's normal output path is untouched, and no row, retry or tolerance was removed or loosened. A caller's pin stands (`:=`), and that is what lets the prepr row's shim, which defers via `:-`, test it.
- Merge with origin/main: `git merge-tree --write-tree origin/main a379c307830addd67fc1abbcde3a71fdb16b8704` exits 0, clean.
- VERSION, manifest, RELEASE_NOTES.md, claim files and *_budgets.json are untouched by the three-dot diff (ev/untouched.txt). The claim files are byte-identical, so env_drift.py has nothing to compare.
- Body: `## Head` names a379c307830addd67fc1abbcde3a71fdb16b8704, which is current. The delivery row dev/programme/delivery/3307.md is in the diff. Roster group R10-HOTFIX-MAIN-IST-RED is named in the title, body and row. Figures 22/2 and 24/0 were re-derived above.
- CI: `merge_train.py classify a379c307830addd67fc1abbcde3a71fdb16b8704 --pr 3307` returned "GREEN a379c307830addd67fc1abbcde3a71fdb16b8704 pending: none red: none", rc=0 (ev/classify-final.txt). governance / instrument-self-tests (job 128617405604) passed at this head, the job that was red on main. The final packet has no refusals (ev/review-packet-final.md); gate id=128622035713 passed and pr-contract / pr-contract id=128621741994 passed.
- About `## Red checks: none`: the first render refused on gate id=128617684448 (failure). Its log reads "FAIL run(s) [42443433781] at this head are still being judged; their gate decides". That is an ordering refusal of an early edit-kind run, not a red on this patch, and the later gate run at the same head passed. The pr-contract run that started after it passed, and per step 11 that run is the evidence.

## Findings

- Follow-up: the body's diff-mutant step was skipped with MUTANT_CMD unset, which departs from the 2026-11-07 mutant ruling. The diff writes exactly one production line, and this review's targeted mutant of it is killed by both the hook self-test and the new prepr row, so no survivor exists for that line. Carry: dismissed: the one changed production line was mutated here and killed twice; nothing left to pin
- Follow-up: prepr ran with PREPR_SKIP_CLOSURES=1 because the cloud toolchain lacks homeassistant, so closures were not recorded locally. CI's tests / closure-scope and tests / closures passed at this head, and no new tracked file needs classifying except the delivery row, which is handled by the delivery convention. Carry: dismissed: CI closure lanes green at the head; no closure movement owed

## Friction

none
