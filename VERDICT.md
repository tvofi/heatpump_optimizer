Fix review: merge a7db67fc2d2ffec721f94bf1d83ce4226566d695

bus-nonce: 0750ab0bbafb2b2f1553a7a1af1caad6

Round 1. Triage record PR: the three-dot diff against the merge base is the ruling file dev/programme/triage/s6-batch96.md plus dev/programme/delivery/3069.md. No production code and no policy file.

## Findings

None.

## Evidence
- Head measured: a7db67fc2d2ffec721f94bf1d83ce4226566d695 (ev/HEAD.txt); CI classify exit 0, GREEN, nothing pending or red.
- (a) False-positive proof for r10-cop-gate-r4-merge: handoff tip is 9db842127; git cherry origin/main shows 0 plus lines; ledger.py landed (tools/audit/seat/ledger.py, tips on stdin) answers "9db84212731f2cce6fce2a8dda34dbf07fecee0f merges-only"; delivery/2975.md on main reads "merged 507a9ec"; _cg_aged count in tests/features.py on main is 4, the ruling says 5 (grep -c counts lines; a one-off miscount, not a ground of the ruling).
- (b) prepr.sh at 2b6bef745: step 1b header is line 3555, step 7c header line 3980, reds_line line 1329, alert_reds line 1276, reds_head_sha line 1366, "read at the open, never here" at 1557. All match; unchanged at origin/main. The carry moves an existing self-tested arm and adds no new check.
- (c) 1793472112 is 18:41:52Z and 1793475917 is 19:45:17Z (date -u -d).
- (d) open_driver.py is not on origin/main; P337 (s6-batch94.md) is on PR #3067's head only. The ruling calls it "P337's not-yet-written driver" and "a new file", so the carry does not name it as existing. Ordering dependency on #3067, not a defect.
- (e) Against the PR's own merge base the diff is exactly 2 files. Against 2b6bef745 it shows 10 files, because main moved; the body's base claim is a reading base, not the diff base.
- Gate: ruling_verdict reads ACCEPT for P350 and P351; triage_refusal returns None for both carries. Null control: flipping P350 to REJECT in a scratch copy gives "dev/programme/triage/s6-batch96.md#P350 is not an ACCEPT ruling (REJECT)" (ev/gate.txt, ev/null.txt).
- policy_lint: 0 errors across 50 policy files. tests/structure.py: PASSED. Claim files byte-identical to the merge base. git merge-tree --write-tree origin/main: exit 0. Delivery row 3069.md present in the diff.
- brief_lint (tools/policy/brief_lint.mjs; the path in the brief does not exist) reports one error, carry-990004 against wave-probe-groups.json PROBE-G1, a probe fixture this diff does not touch. I could not read origin/handoff/audit-r10-roster additions through it.
- Counts I could not re-derive: the 13 log files and 9 distinct update runs, the 57 min slot hold on #3049 and the 11.4 min median (n = 8) rest on out-of-tree session logs. The 7/3/2/1/2 red-check split rests on the same logs.
- The ruling cites ledger.py landed without a path; the instrument is tools/audit/seat/ledger.py.
