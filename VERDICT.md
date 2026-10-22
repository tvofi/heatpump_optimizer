Fix review: blocked 056776d8754930075a030426dd807208e0fd2bc3 contract-red: required check pr-contract is red at this head, because its carry_audit run (in-tree roster, no --roster-ref) refuses this round's new "Carry: R10-FLOW-ROSTER-FREEZE" as BAD-DEST (not a group of the roster), and that group reaches main's roster only when #2588 merges

bus-nonce: bded6e9cf5bed45afc449a17d12c90d7

## Round

This is round 6 overall. Round 1 blocked a8a2778e (mutation-vacuous). Rounds 2 and 3 returned merge at a54aed8b. Round 4 was the conflict update 929ee160. Round 5 blocked f44296a6 with carry-missing. This is the re-review after fixer round fix2580z, at 056776d8754930075a030426dd807208e0fd2bc3. From f44296a6 to this head the PR's own diff (`git diff $(git merge-base origin/main H)...H`) is byte-identical apart from the blob index of INSTRUMENTS.md, which main moved. The only commits since then are three merges of origin/main (f78491bb2, 4743fc8f6, 056776d87). The round changed the PR body only. No round so far has blocked on code. Whether "from the fourth round, a re-cut" applies to a block that is only about the body is the orchestrator's call.

## Block

- **The required `pr-contract` check is red at this head (fix-review.md step 11).** It ran twice: job 119596472527, started 02:03:56Z, and job 119596643713, started 02:04:29Z after the body edit. Both concluded `failure` on the step `python3 -I tools/audit/carry_audit.py check --body /tmp/pr-body.md`, which printed:
  - `BAD-DEST body item 5eb7818a: R10-FLOW-ROSTER-FREEZE: R10-FLOW-ROSTER-FREEZE is not a group of the roster`
  - `CARRY-AUDIT: 2 finding item(s): 1 routed, 0 unrouted, 1 bad destination(s)`, exit 1.
- **Why it fails.** CI's carry_audit reads the in-tree `dev/programme/rosters/wave-r*-groups.json`. R10-FLOW-ROSTER-FREEZE is a group on origin/handoff/audit-r10-roster (306a96d5f). It is also on #2588's head ad10fd21, but it is not on origin/main 3976515a0 and not at this head (ev/roster-membership.txt). I reproduced it locally: `python3 -I tools/audit/carry_audit.py check --body <body>` at this head prints the same BAD-DEST line (ev/carry-audit-intree-head.txt).
- **This round caused it.** Every earlier PR head had pr-contract green, and the body's own ## Red checks says so. The previous body dismissed this item. This round turned it into a carry to a group that main does not yet know.
- **The body does not answer it.** Its ## Red checks names only nightly-status. pr-contract is in main's required_status_checks (ev/required-checks.txt), so the PR cannot merge at this head.
- **The routing is otherwise right.** The brief said not to block only because the roster file lacks the append, and this block is not that. The append texts themselves are sound (see Evidence). The defect is that the gate the merge depends on refuses the body as written.
- **Two ways to clear it.** Either one leaves the code as it is:
  - (a) Once #2588 merges, merge origin/main into the branch so the in-tree roster carries R10-FLOW-ROSTER-FREEZE. The body stays as it is, and pr-contract re-runs green on the new head. merge-tree is clean today, so this asks for no absorb on cleanliness grounds, only for the roster.
  - (b) Re-route that one item to a destination main's roster already knows, and keep the ROSTER-APPEND text for the orchestrator.
  - Either way, add pr-contract to ## Red checks with its cause.

## Findings

- R10-ORCH-MACHINERY still has to receive this PR's ROSTER-APPEND text as one new `carry` entry: the handoff job reads the hold file only through `cloud_relay.sh held <pr>`, rc 0 skip, rc 1 proceed, rc 2 refuse the pass, with control, null control, malformed control and mutant. The roster freeze (#2588) means only the orchestrator can land it. At 306a96d5f the destination holds 0 matches. Carry: R10-ORCH-MACHINERY
- R10-FLOW-ROSTER-FREEZE still has to receive the hold-file grammar precondition (plain PR-number lines only; one malformed line refuses the whole handoff arm, rc 2, `OWED <utc> handoff-hold-malformed <file> -` in <log>.level; read back only through `cloud_relay.sh held`) with the body's ROSTER-APPEND text, once the freeze lifts. At 306a96d5f the destination holds 0 matches. Carry: R10-FLOW-ROSTER-FREEZE
- On a host whose HOME is /root (this cloud seat), the finder's harness at origin/main 3976515a0 has M0 red. ref_privacy refuses `dev/audit/rca/R10-RCA-HARNESS-FRICTION.md:11` as home-directory, because `roles/root-cause.md` contains `/root-cause.md`. That file is main's (#2561), not this PR's. At this head M0 is green, because the check judges only lines added since the merge base. Carry: dismissed: host-only false positive on main's own lines, outside this diff; CI runners' HOME is /home/runner so no gate reads it, and R10-REF-PRIVACY, the group owning ref_privacy.py, is done with no live successor

## Evidence

- RESULT head: measured 056776d8754930075a030426dd807208e0fd2bc3 from a detached worktree. `git ls-remote origin refs/pull/2580/head` printed 056776d8754930075a030426dd807208e0fd2bc3 at reading, and the PR API head.sha agrees. The body's ## Head names this SHA and explains it as an automatic origin/main merge (3976515a0) over f78491bb2. ev/HEAD.txt.
- RESULT roles: `git diff $(git merge-base origin/main H)...origin/main -- dev/governance/roles/` prints 0 lines, so the contract is current. The merge base is origin/main 3976515a0.
- RESULT prior block cleared (content): the earlier block had two parts. (1) R10-ORCH-MACHINERY had no read rule and no control. The body now carries a fenced ROSTER-APPEND that names the group, the finding (#2580, cloud_relay.sh held, rc 0/1/2 semantics), the evidence (the refusal line and level line) and the controls. That is the routing the brief asks to judge, and it is adequate. (2) The false ROSTER-FREEZE dismissal is now a carry with its own append text. The append text's claims were checked against the code at this head: `held()` and `hold_list()` at cloud_relay.sh:212-221, the CLI `held)` arm at :569, and the self-test's malformed loop at :498 has exactly nine variants ('41 99' 'abc' '41x' '0' '-1' '041' '41,99' ' 41' '41 # c').
- RESULT carry_audit, as the brief asks (`--roster-ref origin/handoff/audit-r10-roster check` over the body): `2 routed, 0 unrouted, 0 bad destination(s)`. Item 188e4ffa routes to ['R10-ORCH-MACHINERY'] and item 5eb7818a to ['R10-FLOW-ROSTER-FREEZE'] (ev/carry-routing.txt). Null control: renaming the ORCH carry to R10-NO-SUCH-GROUP gives `1 routed, 1 bad destination(s)` (ev/carry-audit-null.txt). Without --roster-ref (CI's mode) it prints the BAD-DEST under ## Block.
- RESULT destinations: on origin/handoff/audit-r10-roster 306a96d5f, R10-ORCH-MACHINERY and R10-FLOW-ROSTER-FREEZE both have resume.stage `not-started`, so both are live. The body's grep `cloud_relay\.sh held|cloud-handoff-hold|malformed` over brief+carry gives 0 and 0, re-derived. As control, R10-FLOW-RELAY-HOLD's own entry gives 1. #2588 is open (`roster(r10): register the Lean flow study groups...`, head ad10fd21), and that head carries R10-FLOW-ROSTER-FREEZE.
- RESULT self-test: `cloud_relay.sh --self-test` prints `189 checks, 0 failed` at the head and `81 checks, 0 failed` at origin/main 3976515a0. Both re-derived. ev/selftest-*.txt.
- RESULT finder's harness (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`, every mutant):
  - Head: 53 KILLED, M0 `0 seat step(s) red`, `RESULT survivors=0`, rc 0. The per-row failure counts for cloud_relay-2 to -11 are 36/49/2/3/18/2/1/1/27/1. cloud_relay-1 died on the self-test's `updated` file. All of this matches the body, re-derived.
  - origin/main 3976515a0: 42 KILLED, M0 1 red (the ref_privacy host case under Findings), `RESULT survivors=1`, rc 1. This matches the body's shape. The body attributed the main red to #2557's file at 93e6a63d2, and at 3976515a0 the refused line is #2561's file. ev/harness-*.txt.
- RESULT mutation proof: the earlier proof still holds at this head (rows above). This round changed no production line, so it has no new code mutant. Its one change, the carry destination, was perturbed by the null control above.
- RESULT null control: the in-test `a well-formed hold file owes no refusal (null control)` passes inside the 189. Every harness row ran its unmutated step first, and none printed NOT RUN.
- RESULT figures re-derived at this head (ev/quick-checks.txt):
  - STRUCTURE RATCHET PASSED; ALL 2382 ENTITY CHECKS PASSED; ALL 109 HARNESS HEADER CHECKS PASSED; layout self-test: ok.
  - tmp_paths 0 refused; throwaway_git 0 refused; selftest_wiring 73/73/0 unwired.
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (PREPR_SKIP_CLOSURES=1).
  - Own diff 4 files, +133/-3.
- RESULT figures not re-derived: the body's merge-tree tree 9aa93118 was taken at the older main 93e6a63d2, and today's run gives a different tree (below). The body's fail-first counts at f78491bb2 were not re-taken separately: the harness rows at this head reproduce the same counts.
- RESULT VERSION, manifest, RELEASE_NOTES and tests/golden: the three-dot diff stat prints 0 lines. CI's prepr `--version-edit` agrees (`no version edit`).
- RESULT merge-tree: `git merge-tree --write-tree origin/main 056776d8754930075a030426dd807208e0fd2bc3` exits 0, tree d833aefe, clean. ev/merge-tree.txt.
- RESULT CI (check-runs API at this head): 24 success, 14 skipped, 3 failure, 1 in progress (coverage).
  - The failures are pr-contract twice (## Block) and nightly-status.
  - nightly-status grades main's scheduled runs, and this diff reaches nothing it reads. The body's ## Red checks answers it. Main's ci-ratchet runner-speed red belongs to R10-CI-LAYOUT and is not this PR's.
  - The intermediate merges f78491bb2 and 4743fc8f6 have `total_count` 0, because they were never a PR head. ev/check-runs-*.tsv.
- RESULT class seams: the body's grep of cloud_relay.sh is unchanged, because the file did not change since f44296a6. The previous review re-read it and agreed.
