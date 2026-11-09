Fix review: merge 97b15d1667506caf05a78e1548859e29f837a5d7

bus-nonce: 18db52a1403735c9c85d00e210ed8eff

Round 1 of this head. Measured head 97b15d1667506caf05a78e1548859e29f837a5d7 (merges cleanly with origin/main: merge-tree rc 0, no MERGE-CLAIM line).

## Evidence
- Diff is six files, no production line: the RCA doc, the harness .py and its .json fixture, the `_rca` entry in bugclasses.json, the INERT READS line in tests/closures.json, delivery/3329.md (ev/diff-files.txt). No VERSION, manifest or RELEASE_NOTES change; no golden or claim file moved, so step 4 has nothing to compare.
- Mutation proof (no production line, so the harness is the detector; run by me with `git archive <sha> tools/ci` copies): RESULT replay reruns=86 max_attempt=44 sim_minutes=72 alarm=yes at 52f9fc5b34 (ev/replay-52f9fc5b34.txt); reruns=1 max_attempt=2 alarm=no at current origin/main (#3327 fixed arm 1 there) and at this head's tools/ci; reruns=0 at 52f9fc5b34^ (ev/pre-3287.txt). Body quotes the origin/main 4fe7d5934b figure, which main no longer shows because the fix has merged; the defect end still reproduces at 52f9fc5b34.
- Null control: `--no-restamp` at 52f9fc5b34 prints reruns=1 max_attempt=2 alarm=no (ev/null-52f9.txt), so the arm's power is the recorded re-stamp, as the body says.
- Both-ends and own harness: the finder's harness is the PR's own (disclosed in the body as the instrument built here, now in tree and on INERT). I ran it at both ends above.
- Not re-derived: the census figures (465/428/324/1618/17) and the 2.84 s probe need the live ci.yml TSV from 2026-11-08, which I did not re-take; the body labels the 1089/810 brief figures as not re-taken. structure.py: STRUCTURE RATCHET PASSED; fold_ledger.py check: 0 violation(s); harness_headers depth_root_seams(): [].
- Red checks: `merge_train.py owed-reds` lists gate among the required set. The head's red contexts: two stale `gate` runs (13:47Z, 14:04Z) that failed with "run(s) [42624597042] at this head are still being judged" while tests / closures was still running, and the earlier-round reds the body's `## Red checks` section answers. The latest `gate` run 129216459668 (14:20Z) is success after `tests / closures` 129194990571 succeeded at 14:19Z; every other check at the head is success or skipped (ev/gate-closures-runs.tsv). `merge_train.py classify` still printed RED (rc 1, ev/classify.txt) because it reads the two stale gate rows; I judge the head GREEN on the latest gate run and say so rather than rely on the exit code. pr-contract is success at the head.
- Forward-carry (step 10): the three body carries all route to #201 and carry_audit reports 3 routed, 0 unrouted. The fixer (#3327) had already merged, so carry 1 has no unmerged stage left to receive it; see Findings.

## Findings
- Follow-up: sweep self-test still passes a broken arm 1 and has no closed-loop convergence check (body states the candidate arm-1 copy passes `sweep.py --self-test`, 52 checks); the harness here is the control that separates them, not wired into the self-test. Carry: #201
- Follow-up: the attempt-watch beat row at attempt >= 20 (countermeasure B) is proposed, not built. Carry: #201
- Follow-up: orchestrator_tick.py:1441 reads a sweep re-run's re-stamped check runs as worker CI activity; the body says it was not measured whether check runs are re-stamped. Carry: #201
