Fix review: merge 0c3138c5f35760a738cf78694f91cb65af4c3726

bus-nonce: ef64bfe28eb4a7e0c5fa3fdc85eaacff

## Summary

First-round review of PR 3343 (R10-HOTFIX-PREPR-SELFTEST-DARWIN). I run on Linux, where the arm was always green, so **I could not reproduce the Darwin failure**. The Darwin claim rests on reading the diff, a simulated shim, and the seat's recorded evidence in the PR body.

- Diff (three-dot): `tools/pr/prepr.sh` (+5/-2 effective) and `dev/programme/delivery/3343.md` (the delivery row, present). No new tracked file beyond that row, no budget file touched, VERSION / manifest / RELEASE_NOTES.md untouched (empty diff). `## Head` names 0c3138c5 and the authored code head.
- Merge: `git merge-tree --write-tree origin/main HEAD` is clean (tree 26f5b333).
- Reading: the two changed calls prepend the real interpreter's directory (`dirname sys.executable`, resolved under the real HOME before the planted one) to PATH only for `body_privacy_line`. `body_privacy_line` calls `python3 -I tools/audit/seat/ref_privacy.py`. With the real interpreter first on PATH it cannot reach a HOME-resolving shim, so it cannot exit 127. The rc and message checks are unchanged, so they still judge the subject.
- Note on the body's wording: at main on a shim host, `body_privacy_line` as written returns rc 1 with the shim's message for the clean body, not 127. The shim's 127 is captured inside $(...) and the function ends in `return 1`. The arm's "got 127" in the PR body is the fixer's observed output on the Mac. The disagreement is cosmetic and the failure mode is the same (clean body wrongly nonzero).

## Evidence

- Self-test at merge-base (main side): `ev/selftest-base.txt`, 514 passed, 0 failed, rc 0 (Linux null control: the arm is green at main).
- Self-test at the head: `ev/selftest-head-full.txt`, 514 passed, 0 failed, rc 0 (green at both ends).
- Planted-HOME pair at the head on Linux, real python3 (`ev/pair.txt`): planted body rc 1, clean body rc 0. Same at main.
- Simulated Darwin shim (`ev/shim.txt`; a python3 shim that execs the venv under $HOME or prints "no venv under $HOME" and exits 127; real HOME has the venv, planted HOME does not). Main-side call: planted rc 1 with the shim's message, clean rc 1 with the shim's message (clean case wrong). Head-side call: planted rc 1 with "home-directory, account-name in the body", clean rc 0. This is a simulation, not the Mac.
- Mask check (mutant): in a worktree of the head I replaced `tools/audit/seat/ref_privacy.py` with `sys.exit(0)`. `ev/selftest-mutant.txt` is 513 passed, 1 failed, rc 2: `FAIL a body naming the host home directory is refused by body_privacy_line (got 0, wanted 1)`. The arm still fails when its subject fails.
- `python3 tests/entities.py`, run plainly: **did not run clean.** It exits rc 1 at import (`ModuleNotFoundError: No module named 'homeassistant'` from tests/harness.py) in this cloud environment (`ev/entities.txt`). This is an environment limit, not a result on the tree, so entities is unverified here. The diff adds one delivery row, no other tracked file.
- CI at the head: `merge_train.py classify ... --pr 3343` returns RED (`red: gate`, exit 1) on every poll (`ev/classify*.txt`). Cause, from the gate logs (`ev/oldgate-logs.txt`): two older `gate` suites, runs 42510666835 (code, 128840026466) and 42510666939 (edit, 128839941254), failed at 19:41-19:42Z with the one line "run(s) [42516277088] at this head are still being judged; their gate decides". The deciding run 42516277088 (suite 115166803851, gate check-run 128840815485) concluded **success** at 19:45:44Z on this head. The train's A5 rule keeps the worst gate of each suite, and a deferral red is never re-run. All other required contexts in the digest are success, including `pr-contract` (128840624028), `budget-raise-gate` and `tests / mutation`. I judge the head GREEN on the deciding gate. This is the deferral class the PR body's `## Red checks` already describes.
- `ev/HEAD.txt` holds the reviewed head.

## Findings

- Follow-up: `## Red checks` names only gate check-run 128823275143. The head also carries two later concluded deferral reds from suites 115152319844 and 115152320114 (check-runs 128840026466 and 128839941254, same one-line deferral, all superseded by the success of 42516277088). `pr-contract` ran green after them, so the body check passes, but the body does not name them. This is the train's classify staying RED on a settled deferral (R10-HOTFIX-TRAIN-DEFER-WAIT / R10-HOTFIX-SWEEP-SETTLE-LOOP's class), so the orchestrator should merge on the deciding gate, not on classify's exit code. Carry: dismissed: the settled-deferral class is already carried by the PR body (R10-HOTFIX-SWEEP-SETTLE-LOOP), pr-contract is green at the head, and the fix is unaffected
