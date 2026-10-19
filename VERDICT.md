Fix review: blocked 519bb4db971b5d49736fcacdd57d57bff8f6c630 carry-unsound: Forward-carry item 1 routes to R10-OPENPR-SILENT, which is done (#2422 merged 7ab3030b and delivered the tick carry sweep); carry_audit.py at this head refuses it BAD-DEST against handoff/audit-r10-roster

bus-nonce: fb2e93390840f16fcc1e203c044d6794

Round 8. Round 7 blocked this same head on the body only. The head is still 519bb4db971b5d49736fcacdd57d57bff8f6c630, the same commit as origin/fix/r10-carry-enforce when this verdict was written. fix-review.md has not changed on main since the merge base (the diff over dev/governance/roles/ is empty).

## Blocking: the carry route is out of date (step 10)

- The body's Forward-carry item 1 reads "the carry now sits in the roster entry of R10-OPENPR-SILENT (#2422) ... Carry: R10-OPENPR-SILENT".
- On handoff/audit-r10-roster, 59cf492cd marks R10-OPENPR-SILENT `resume.stage: done` ("delivered by PR #2422"). origin/main's roster still says `in-progress` because it lags behind the roster branch.
- I ran this PR's own checker, `carry_audit.py --roster-ref <ref> check --body` (ev/carry_check.txt):
  - HEAD tree: 0 bad destinations.
  - origin/main: 0 bad destinations.
  - origin/handoff/audit-r10-roster: `BAD-DEST body item 5978f947: R10-OPENPR-SILENT is done (resume.stage done)`, rc=1.
- The body passes today only because main's roster lags. This is the gap the body's own Friction item 4 describes. queue_pre_flight's `findings` step reads origin/main's roster, so the next roster sync to main will PARK this PR, and pr-contract will refuse the body on the next main merge.
- The substance has already landed. On origin/main, orchestrator_tick.py has `carry_sweep()` (CARRY section, opt-in with `--only CARRY`). It runs `sweep --last N --issues` over origin/main and the tick's roster ref. Its self-test arms cover exit 0, 1 and 2, and it reports `UNREADABLE ... carry_audit.py absent (it lands with #2404)` until this PR merges. #2422 merged before its carry's stated precondition ("PR #2404 is merged"). It degrades loudly rather than silently, so that is not this PR's defect.
- Fix, a body edit only: re-route item 1 to a destination that is still open, or close it in the marker's grammar, e.g. `Carry: dismissed: delivered by #2422 (7ab3030b); orchestrator_tick.carry_sweep goes live when this PR merges`. Update the prose that says the carry "now sits" in that roster entry to match. Then re-run `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body`.

## Everything else checked at this head: no findings

- Mutation proof (step 1): `python3 dev/audit/harnesses/r10_carry_parser_mutants.py` printed `RESULT sites=152 unmapped=0 mutants=190 survived=0`, the same as the body (ev/mutants.txt). I also planted two mutants of my own (ev/own_mutants.txt), and both were killed:
  - A: the `findings_gate` call removed from PreFlight (the body's M10) left `queue_pre_flight self-test: 41 checks, 4 failed`.
  - B: the done-group refusal at carry_audit.py:304 removed left `carry_audit self-test: 144 checks, 1 failed` ("a done group is a bad destination").
  - Both files were restored and the tree is clean.
- Self-tests (ev/selftests.txt): carry_audit 144/0, queue_pre_flight 41/0, merge_train 189/0. All match the body.
- Merges with main (step 13): `git merge-tree --write-tree origin/main HEAD` (origin/main abb397938) gives tree dfb7e449, rc=0, with no conflicts.
- Release stamps (step 5): VERSION, the manifest and RELEASE_NOTES.md are untouched.
- CI (step 11): the head's check-runs API (filter=all) lists 51 runs, 36 success and 15 skipped, none red and none in progress (ev/check_runs.tsv). The body's Red checks section now names b419463b1's pr-contract red (BAD-DEST, R10-OPENPR-SILENT), which answers round 7.
- Not re-derived: the remaining figures in the body (sweep-row harness, ISSUE-UNOWNED and ROSTER-DRIFT counts, the policy lints). They were taken at code head 74201dd56, and per the body this head adds only merges with no resolution. I did not re-take them this round, so they are unverified here and not confirmed.
