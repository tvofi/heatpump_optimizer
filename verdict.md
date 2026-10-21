Fix review: merge 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725

PR #2513, group R10-ROSTER-OPS, round 1 (no earlier verdict on the PR). Measured head 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725, still the PR head at verdict time (`git ls-remote origin refs/pull/2513/head`). Merge base 6961f0663 (= origin/main tip); `dev/governance/roles/` unchanged between base and main. Detached worktrees at the head and at df6ca4bc.

RESULT selftest head=6b46b4f8b "roster_edit self-test: 94 checks, 0 failed" (ev/selftest_head.txt)
RESULT selftest base=df6ca4bc "roster_edit self-test: 64 checks, 0 failed" (ev/selftest_base.txt)
RESULT mutant=null rc=0 fails=0 (ev/null.txt)
RESULT mutants driver plants=19 killed=19 "without a FAIL line: none", no crash (ev/mutants_full.txt) -- the body's A5/A6 crash was host-side; at this head and on a healthy host all 19 have FAIL lines
RESULT mutants-harness self-test "63 checks, 0 failed" (ev/mutants_selftest.txt)
RESULT own-mutant=R1 (finished DFS node never marked 2) rc=1 -- killed, by a crash in _cycle (ValueError) not a FAIL line
RESULT own-mutant=R3 (cycle check sees only the edited group's edges) rc=1 fails=3 -- killed
RESULT own-mutant=R4 (any revisit reported as a cycle: false positive on shared ancestors) rc=1 fails=5 -- killed
RESULT own-mutant=R2 (`.strip()` removed from set-after's split) rc=0 -- SURVIVES; fail-closed (a spaced list is refused as an unknown group, never written), so not blocking (ev/own_mutants.txt)
RESULT live-roster origin/main: 91 groups, 64 non-empty carry, 27 `"carry": []`, 0 key-less -- body's census confirmed; dump round-trips; every group re-set to its own after-edges: 0 refused, 0 byte changes; append-carry+drop-carry on every group: 0 byte changes (ev/live_probe.txt)
RESULT selftest_wiring "38 self-testing, 38 wired, 0 unwired"; tmp_paths 0 refused; STRUCTURE RATCHET PASSED; closure select "MODE: SCOPED -- 2 script(s) run", 5 changed files; archscore "dS +0.0000 NULL" (ev/cheap_checks.txt)
RESULT merge-tree origin/main 6b46b4f8b: rc=0, tree 111b48c93, no conflict
RESULT version: VERSION, manifest version, notes heading and claim files untouched (diff and pr-contract's "no version edit")
RESULT CI at head (ev/check_runs.tsv, all concluded): every run success/skipped/neutral except nightly-status (failure)

Steps:
1/14. Mutation proof re-run (19 plants, all killed) plus four of my own on _cycle and the split; one fail-closed survivor (R2). No budget, closure, INERT, golden or claim file moves; the self-test count rise (64 -> 94) is earned by 30 new arms, each tied to a plant.
2/9. The finding's harness is the brief's controls; the mutant driver is the fixer's own and disclosed as such in the body. I measured with my own plants and an in-memory live-roster probe I built (disclosed here; not landed).
3. Null control re-run: clean.
4. No fixture or claim file touched; env_drift not applicable.
5. Untouched.
6. Class: the body's issue (#2496) names two deliverables; this PR claims only the first (set-after, drop-carry) and closes nothing, and the roster's resume.next_step dispatches the roster-sync reconciler at a new head. Not class-open for the ops it delivers. Note for the orchestrator: the group's four `carry` items (owner-gate count in orchestrator_tick.py, open_pr.sh stale body, update_pr.sh `ps` guard, the three roster-sync predicates) are not dispositioned in this body; they ride the second deliverable.
   Other configuration: origin/handoff/audit-r10-roster's roster has 2 key-less groups (R10-HANDOFF-ARCHIVE, R10-DEPENDABOT-AIOHTTP); there append-then-drop leaves `"carry": []`, not byte-identical. The body scopes its claim to main's roster (the default --roster-ref), where it holds.
7. The body's Head section names 6b46b4f8b. Its figures were taken one main-merge earlier, a merge touching none of the five files; I re-took them at this head.
8. Not re-derived: "121 checks, 27 failed" on the arms-without-ops tree (I did not rebuild that tree). All other figures re-derived above.
10. Forward-carry: none claimed; none owed by this diff.
11. nightly-status red grades main's slow lane (log: "slow failed 1 night ago", head 0c298f6); the diff's one governance.yml hunk adds an instrument-self-tests step, outside what it reads -- not this PR's, and the body answers it. instrument-self-tests red at 716a34f2 is answered with its cheaper detector (selftest_wiring.py --check); green at this head. pr-contract at head green.
12. Head unchanged at verdict time.
13. merge-tree clean.
15. Architecture: additions sit in the existing load-modify-dump flow; no breach. Owner: governance.yml is code-owned (/.github/workflows/ @tvofi), so merge still needs tvofi's approving review.

bus-nonce: e19a37e0fbf070d7829735b3404f9a8f
