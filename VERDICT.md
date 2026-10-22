Fix review: merge c8b85d11564a9f429fafbe3353a4b8746e45b187

bus-nonce: 4609f9ffca1b26db069b09122e427086

## Round

Re-review at a moved head (round 3 of the review; the earlier verdict at 83d9662d was merge). Head reviewed: `c8b85d11564a9f429fafbe3353a4b8746e45b187`, re-read as the PR head before writing. The head moved only by merges: c1b8252dc (7a3fc062b + 841c65da4) and c8b85d11564a9f429fafbe3353a4b8746e45b187 (c1b8252dc + origin/main 46e368127); both trees equal `git merge-tree --write-tree` of their parents, so both are automatic. The one hand resolution is inside 841c65da4 (the `r10_seat_selftests_mutants.py` docstring and MUTANTS tail), judged below. Apart from that hunk, the PR's own diff against origin/main is byte-identical to its diff at 83d9662d (only hunk offsets differ).

## Findings

- Surviving mutant: replacing `--max-age) max=${2:-}; shift 2 || shift ;;` with `--max-age) shift 2 || shift ;;` (the option is parsed but ignored, so the age limit is always 1200) leaves `heartbeat.sh --self-test` at 7 checks, 0 failed. Its two watcher fixtures (fresh at --max-age 600, 1800 s stale at --max-age 1200) give the same result under the default. My hand null control shows the arm works at this head (900 s old: STALE under --max-age 600, FRESH under 1200), and the owner's watcher uses the default. So this is a test gap, not a defect: the self-test should add one fixture whose verdict flips with --max-age (for example 900 s old under 600). Evidence: ev/own_mutants.txt R4, ev/null_controls_watch.txt. Carry: R10-ORCH-MACHINERY
- The roster carry "Revision 12" on R10-FLOW-ANDON (origin/handoff/audit-r10-roster 743463c61, added in 735981f4e at 2026-10-21T20:42Z) asks for three more alarms: a handoff tip ahead of its PR head for over 20 minutes, a lock whose owner pid is dead, and a seat self-test process older than 1 h. This PR does none of them and its body does not mention them. The heartbeat this PR lands is the group's K8 brief and is complete on its own, so the gap does not block this merge, but the alarms are still owed after it. Carry: R10-FLOW-ANDON
- Self-test hygiene item (a) in the same roster carry says a new mutant "sits inside the block of the instrument it tests, never appended at the file's end". tick_loop-1 and tick_loop-2 come after S35..S38 at the end of MUTANTS, not next to tick_loop's S31..S34. The ids follow the per-file convention and the merge with #2529 resolved cleanly. Whoever next adds mutants to that file should move them. Carry: R10-ORCH-MACHINERY

## Evidence

- Mutation proof (finder's seat harness `dev/audit/harnesses/r10_seat_selftests_mutants.py`, run in full at the head): `M0: 0 seat step(s) red`, 48 KILLED, `RESULT survivors=0`, exit 0. The six from this PR are tick_loop-1, tick_loop-2 and heartbeat-1..4, all KILLED. #2529's S35..S38 are KILLED too (ev/mutants_head.txt).
- My own mutants at the head (ev/own_mutants.txt): R1, a host path (`out=$out`) in the heartbeat message, is KILLED (2 tick_loop checks fail). R2, a failed heartbeat aborting the pass, is KILLED (1 fails). R3, the watcher comparison inverted, is KILLED (2 fail). R5, the commit gaining a parent, is KILLED (3 fail). R4 survives (see Findings).
- Both ends (ev/both_ends.txt): main's tick_loop.sh --once against a bare remote leaves no heartbeat/orchestrator ref, and the head's watcher prints `HEARTBEAT STALE: no heartbeat/orchestrator` with rc=1. The head's tick_loop.sh --once moves the ref to `TICK-PASS <utc> relay=absent tick=0`, with no host path and no parent, and the watcher prints `HEARTBEAT FRESH` with rc=0.
- Null controls for the --watch --max-age arm (ev/null_controls_watch.txt): under the default 1200 s limit, ages 60 and 1190 are FRESH (rc 0) and 1260 and 3600 are STALE (rc 1, naming the message). A 900 s ref is STALE under --max-age 600 and FRESH under 1200. A non-numeric --max-age exits 2. A message carrying $HOME is refused (`HEARTBEAT NOT PUSHED: ref_privacy guard refused the message`, rc 1).
- The loop continues on a failed push. tick_loop's self-test checks "a failing heartbeat is printed ... loop still exits cleanly" and "null control: a refused push is printed with its reason and the pass still completes", and both are ok. heartbeat.sh pushes with `-f --no-verify` (heartbeat-1 KILLED).
- Resolution null control (my probe, ev/ids_probe.py, ev/ids_null_control.txt): at the head it prints `main=35 branch=37 head=41 union=41 missing_from_head=[]`, rc 0. With origin/main in the head's place, the six andon ids are missing (rc 1). With 7a3fc062b in its place, S35..S38 are missing (rc 1). This re-derives the body's figures.
- Every figure in the body was re-taken at this head, not at 841c65da4 as the body took them (ev/figures_head.txt):
  - heartbeat self-test: 7 checks, 0 failed. Re-derived.
  - tick_loop self-test: 12 checks, 0 failed. Re-derived.
  - ref_privacy --check: 0 refused (20 files with a push site, 10 guarded). Re-derived.
  - ref_privacy --self-test: 66 checks, 0 failed. Re-derived.
  - selftest_wiring: 73 self-testing, 73 wired, 0 unwired. Re-derived.
  - throwaway_git: 0 refused. Re-derived.
  - STRUCTURE RATCHET PASSED, no budget file in the diff. Re-derived.
  - closure select: `MODE: SCOPED -- 2 script(s) run`, the scripts being entities.py and harness_headers.py. Re-derived.
  - harness_headers: ALL 109 PASSED. Re-derived.
  - entities.py (venv-ci, PYTHONPATH=tests/hastub): the first run printed `1 of 2382 ENTITY CHECKS FAILED`. It ran alongside the mutation harness and my mutant worktree, and I captured only its tail. The re-run alone printed `ALL 2382 ENTITY CHECKS PASSED` (ev/entities_rerun_head.txt). I count the figure as re-derived on the re-run. I could not identify the first run's failing check.
  - Not re-derivable here: the body's timestamp and its claim that the figures were "at 841c65da4 against 5a755f53efda", which describe the fixer's run. The same numbers hold at this head.
- Merge-tree: `git merge-tree --write-tree origin/main c8b85d11564a9f429fafbe3353a4b8746e45b187` exits 0, and its tree e3b2f51d0 equals the head's tree (ev/merge_tree.txt). The merge base is origin/main 46e368127, so the head is 0 commits behind.
- roles/: `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- VERSION, the manifest, RELEASE_NOTES and both claim files are untouched (ev/head_chain.txt).
- carry_audit over the PR body (`--roster-ref origin/handoff/audit-r10-roster check`): `3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt).
- CI on this head, from the check-runs API per commit (ev/check_runs.txt, ev/check_runs_final.txt):
  - instrument-self-tests, mutation, closures, closure-scope, scope, coverage, coverage-ratchet, arch-score, budget-raise-gate, briefs, policy-docs, typing, lane-proofs, fast (3.14), browser, env-matrix, hassfest, validate-hacs, delivery-status, wave-script, graders-head-copy and CodeQL Analyze all succeeded. pr-contract succeeded twice, and a third run was in progress at the final read.
  - c1b8252dc and 841c65da4 carry no check runs.
- Red checks: `nightly-status` failed. It grades main's scheduled lanes, and this diff reaches nothing it reads (no production module, tests/ driver, budget or tests.yml). The body names and answers it. ci-ratchet did not run on this head, and main's red there is runner-speed variance owned by R10-CI-LAYOUT, which the body also answers.
- Mutation lane: green. The diff writes no production code line (only seat tools, a workflow step, a harness, docs and a delivery row), so the lane draws no mutant and its green does not show that mutants were evaluated.
- Forward-carry: the body routes R10-ORCH-MACHINERY to register `heartbeat.sh --once` as the beat's job, and dismisses the owner-scheduled watcher by design.
- carry_audit over this verdict: read whole, it prints `0 finding item(s)`, because `## Findings` is not a heading the tool reads as notes. Read with this verdict's `## Findings` bullets placed under `## Forward-carry`, it prints `3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`. Both destinations, R10-ORCH-MACHINERY and R10-FLOW-ANDON, are live roster groups at stage not-started (ev/carry_audit_verdict.txt, ev/carry_audit_verdict_findings.txt).
