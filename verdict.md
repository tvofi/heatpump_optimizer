Fix review: merge eda11668ae28b26d1efcb841e8e60431dec97590

bus-nonce: 45db6e377505caa99814f8b5419601d0

Round: second review of #2525 (this head repairs a returned round). Measured head: eda11668ae28b26d1efcb841e8e60431dec97590, still the PR head when this was written. Detached worktree at that head. `dev/governance/roles/` is identical between the merge base and origin/main, so this review ran under the current contract.

RESULT head=eda11668ae28b26d1efcb841e8e60431dec97590 code_head=5d477d6e9d3b in_head=yes: every PR file but the delivery row is blob-identical to the code head
RESULT merge_tree=clean tree=e302cb15840f exit=0 (ev/merge_tree.txt)
RESULT pr_cap_selftest="21 checks, 0 failed" pr_args_selftest="54 checks, 0 failed" tick_selftest="152 checks, 0 failed" selftest_wiring="37 self-testing, 37 wired, 0 unwired"
RESULT dispatch_gate_live: refuses at 6/6 at origin/main and names six in-progress groups, rc=1 (ev/dispatch_gate_live.txt)
RESULT structure=PASSED layout_guard="0 refusal(s)" policy_lint="TOTAL: 0 error(s); FIXTURE ok" rules_sync=ok orchestrator.md lines 319->317
RESULT mutation (a) main's pr_cap.py: pr_args "54 checks, 6 failed", the six open-path arms the body names: KILLED
RESULT mutation (b) n<cap -> n<=cap: pr_cap "21 checks, 1 failed": KILLED
RESULT mutation (c) tick n=len(prs): tick "152 checks, 2 failed", the two arms the body names: KILLED
RESULT mutation (d) unreadable roster -> zero: pr_cap "21 checks, 3 failed": KILLED
RESULT own mutants: overcap line deleted KILLED(1); WIP_STAGE=fixing KILLED(6); empty-reason arm deleted KILLED(1); open_info rc=1 KILLED(1); open_pr.sh info call made gating KILLED(6+)
RESULT committed harness dev/audit/harnesses/r10_seat_selftests_mutants.py M0 S15: "M0: 0 seat step(s) red", S15 pr_cap.py KILLED, "RESULT survivors=0"
RESULT ci at head: 49 check runs, all completed; every one is success or skipped except nightly-status (failure) (ev/check_runs.tsv)

Findings, by step:
1/3 Mutation proof and null control: (a) to (d) re-run and each reproduces the body's exact tallies. The null controls are present and pass: 0 WIP passes; 20 open PRs is information only, rc 0; an unreadable roster is a refusal, and the tick prints no WIP line for it.
2/9 Harness: the finding is the owner's ruling (tvofi 2026-10-20/21), with no numeric finder harness, so the mutants and self-test arms are the measurement. I also ran the committed seat-self-test mutant harness (S15 on pr_cap.py, M0 across every seat step).
4/5 None of the claim files, goldens, VERSION, the manifest or RELEASE_NOTES is in the diff.
6 Class: the body names no enumeration rule. I used my own: every reference to pr_cap or an open-PR or soft cap across the tree. It returns open_pr.sh and orchestrator_tick.py (both in the diff), cloud_relay.sh and update_pr.sh (neither calls the cap; both are covered in the body or its docs), and tools/plan/replan.py:53,713. replan.py's check #4 bounds groups in flight against `slots` when a wave opens. That is dispatch, which the ruling allows, and it never refuses opening or updating a PR, so it is outside the class. Only its comment still says "open-PR cap": stale wording, not blocking.
7 The body's ## Head names 5d477d6e as the code head and describes eda11668 as that head plus a main merge plus the delivery row. Verified blob-by-blob.
8 Every figure the body quotes re-derives at this head (tallies above). The live dispatch-gate refusal matches the body.
10 Forward-carry: "none". The change binds the orchestrator's §5 directly, so no later stage's brief needs a carry.
11 Red checks: nightly-status is red. Its inputs, tests/nightly_status.py and .github/workflows/tests.yml, are untouched by the diff (ev/nightly_status_scope.txt), so it grades main and the body names it. The previous head's policy-docs, env-matrix and pr-contract reds are named, with a cheaper detector and its cost. All three are green at this head, and so are closures (under-approximation), fast, coverage, instrument-self-tests and mutation.
13 merge-tree against origin/main 43f79c08 is clean, exit 0.
14 No budget or recorded metric moves. orchestrator.md drops two lines by cutting prose. I checked each cut against the tree:
  - "merge_train.py" is still named at lines 256 and 288.
  - The "filed issue asked for a mechanism already in the tree" example is in CLAUDE.md:179.
  - "one push credential / yours alone" is in decision 0013 ("The orchestrator still holds the credential").
  No obligation is lost.
15 Architecture: the WIP count goes through roster_lib (the one schema reader, reader_ref and show_roster) and is counted by group id, and the tick reuses pr_cap's wip_groups. Nothing is re-parsed and there is no new ref logic. No breach.

Policy wording against the ruling ("the soft cap of 6 gates only starting or dispatching a new roster group; opening or updating a pull request for an owed handoff is never refused by it"):
- orchestrator.md §5: "The soft cap gates only dispatching a new roster group ... Opening or updating a pull request for an owed handoff is never refused by it." Matches.
- INSTRUMENTS.md open_pr.sh entry: "gates only dispatching a new roster group, and never refuses opening or updating a pull request for an owed handoff". Matches.
- INSTRUMENTS.md cloud_relay.sh entry: "which the soft cap never refuses (it gates only group dispatch)". Matches in meaning.
- INSTRUMENTS.md pr_cap.py entry: "on dispatch ... `info` ... never refuses". Matches in meaning.
- pr_cap.py docstring: the ruling verbatim.
The INSTRUMENTS cloud_relay and pr_cap entries are paraphrases, not the same words, but nothing in them departs from the ruling.

Not verified here: the body's own `ci_predict.py` and `closure.py select` outputs. I relied on CI's closure-scope and closures runs, both green at this head.

Approval still owed, not by this verdict: orchestrator.md is policy and pr_cap.py, open_pr.sh and orchestrator_tick.py are code-owned paths, so the PR needs tvofi's approving review at this head.
