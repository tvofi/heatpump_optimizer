# BLOCKED: R10-HOTFIX-GATE-STALE-JOBS r2, at the body push

The code is handed off: refs/heads/handoff/r10-hotfix-gate-stale-jobs = bc806747bfd242e61d728b6784ab36d742193bd9.
`tools/pr/prepr.sh` is clean at that head (PRE-PR rc=0, body check ok, CARRY-AUDIT 2 routed). origin/main was d7582ed40 and had not moved.

`body_push.sh` refuses: CARRY-MISSING R10-FLY-GH-READ-RETRY, items 0290a23c and da72de94. Those are the two
suspected fail-open readers (codescan_wait.py own-run path, pr-contract.yml red list) that this seat was told to
disposition. It routes them onward to that group, which is live, carries-open, and names both files. Landing them needs a write to
handoff/audit-r10-roster, and this seat may push only its return refs. I did not dismiss them to get past the refusal.

Question: will the orchestrator land the two ops below on the roster branch (or name another destination)?
After that, `bash tools/audit/seat/body_push.sh r10-hotfix-gate-stale-jobs BODY.md` pushes the body unchanged.

Ops (`carry_audit.py land-ops` output):

append-carry R10-FLY-GH-READ-RETRY 'From this pull request, body item 0290a23c: `tools/ci/codescan_wait.py` `source()`, own-run path: when this run owns codeql it returns `_jobs()` at once, with no poll, and `legs_uploaded()` then keeps only legs whose upload step is listed `success`. A stale step row would read as "stood down", and that leg'\''s analysis would be neither waited for nor read, so the check may fail open. I read this in the code; it is unmeasured (RCA section 3). The next step is to measure step rows inside the three incident windows before anything is built. The roster brief write is the orchestrator'\''s; this seat may push only its return refs. Carry: R10-FLY-GH-READ-RETRY (items 0290a23c)'
append-carry R10-FLY-GH-READ-RETRY 'From this pull request, body item da72de94: `.github/workflows/pr-contract.yml`, step "List the red checks at this head": it keeps only `status == "completed" and conclusion == "failure"` check runs, so a red that is still lagging is left off the list the body must answer, and the check may fail open. I read this in the code; it is unmeasured, and the next step is the same measurement as above. Carry: R10-FLY-GH-READ-RETRY (items da72de94)'
