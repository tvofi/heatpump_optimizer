Fix review: merge 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725

PR #2513, group R10-ROSTER-OPS. Fresh reviewer seat; a previous reviewer returned merge at this same head (probe/rev-2513-e19a37e0), read as one argument only -- every figure below was re-taken here. Measured head 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725 (full sha in ev/HEAD.txt), still refs/pull/2513/head at verdict time (ev/head_at_verdict.txt). Merge base 6961f06637964001a2ed544e495ea0312eeefa37; dev/governance/roles/ unchanged base...main. Detached worktrees at the head (two: one for the fixer's driver, one for my own plants, so they never shared a file) and at the base.

RESULT selftest head=6b46b4f8ba93ae7574312493a03fd7e0c1d2b725 "roster_edit self-test: 94 checks, 0 failed" (ev/selftest_head.txt)
RESULT selftest base=6961f0663 "roster_edit self-test: 64 checks, 0 failed" (ev/selftest_base.txt) -- matches the body's df6ca4bc figure; roster_edit.py is unchanged between those bases
RESULT mutant=null rc=0 fails=0 (ev/null.txt)
RESULT mutants-driver plants=19 "without a FAIL line: none", rc=0, no crash tail (ev/mutants_full.txt) -- the body's A5/A6 crashes were host-side; all 19 killed by FAIL lines here
RESULT mutants-harness self-test "r10_roster_ops_mutants self-test: 63 checks, 0 failed" (ev/mutants_selftest.txt)
RESULT own-mutant=M2 (del carry[i] -> carry.pop()) rc=1 fails=4 -- killed
RESULT own-mutant=M7 ('-' not special) rc=1 fails=2 -- killed
RESULT own-mutant=M8 (duplicate-edge check removed) rc=1 fails=1 -- killed
RESULT own-mutant=M1 (_cycle never marks a node finished) rc=1 -- killed by a traceback, not a FAIL line
RESULT own-mutant=M3 (_cycle tests state 2 instead of 1) rc=1 -- killed by a traceback, not a FAIL line
RESULT own-mutant=M4 (--match substring -> prefix) rc=0 -- SURVIVES; fail-closed (prefix hits are a subset of substring hits, so it can only refuse more or resolve an ambiguity to an entry that still contains the text)
RESULT own-mutant=M5 (after stored sorted) rc=0 -- SURVIVES; edge order carries no dispatch meaning in the after-graph
RESULT own-mutant=M6 (.strip() dropped from the split) rc=0 -- SURVIVES; fail-closed ("A, B" is refused as an unknown group, never written)
   (ev/own_mutants.txt, driver ev/own_mut.py -- my own instrument, disclosed, not landed)
RESULT live origin/main roster: 91 groups, 64 non-empty carry, 27 "carry": [], 0 key-less; dump round-trips; set-after to every group's own edges: 0 refused, 0 byte changes; append-carry+drop-carry on every group: 0 byte changes; a reversed real edge is refused as a cycle (ev/live_probe.txt, driver ev/live.py, in-memory, nothing written)
RESULT live handoff/audit-r10-roster roster: 108 groups, 2 key-less (R10-HANDOFF-ARCHIVE, R10-DEPENDABOT-AIOHTTP); append+drop there adds "carry": [] to those two -- outside the body's claim, which is scoped to main's roster (default --roster-ref); non-blocking
RESULT selftest_wiring "38 self-testing, 38 wired, 0 unwired"; tmp_paths "0 refused"; STRUCTURE RATCHET PASSED; closure select vs 6961f0663 "MODE: SCOPED -- 2 script(s) run", 5 changed files; archscore "Architecture score: dS +0.0000 NULL" (ev/cheap_checks.txt). tests/entities.py could not run locally (python3.11 SyntaxError; 3.12/3.13 lack homeassistant) -- CI fast (3.14) green is the record for it.
RESULT merge-tree origin/main(43f79c08b) 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725 rc=0 tree 91022da7f, no conflict (ev/merge_tree.txt)
RESULT version: VERSION, manifest, RELEASE_NOTES.md, claim files, *_budgets.json, closures.json, closure.py untouched (ev/merge_tree.txt: empty diffstat)
RESULT CI at head: 49 check runs, all concluded; every one success/skipped except nightly-status=failure (ev/check_runs.tsv)

Steps:
1. Mutation proof re-run: 19/19 plants killed by FAIL lines; 8 plants of my own, 5 killed (2 by traceback), 3 fail-closed survivors (M4, M5, M6) -- not blocking, noted for a later tightening.
2/9. The group's controls ("each op's mutant fails its self-test arm; existing ops and the no-op path unchanged") are the finder's harness; the mutant driver is the fixer's, disclosed. I measured with the driver plus my own plants and live-roster probe (disclosed above).
3. Null control re-run clean; base self-test 64/0, head 94/0, the 30 added checks each tied to a plant.
4. No golden fixture or claim file touched; env_drift not applicable.
5. Untouched.
6. Class: the group brief carries two deliverables; this PR delivers only the ops (set-after, drop-carry) and the roster's resume.next_step dispatches the roster-sync reconciler at a new head, so the reconciler and the group's four carry items are not this PR's to disposition. For the ops it delivers, the existing ops and no-op path are pinned unchanged (no-op set-resume/set-after byte-identical arms; D1).
7. Body's Head names 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725; its figures were taken one origin/main merge earlier touching none of the five files; I re-took them at this head.
8. Not re-derived: "121 checks, 27 failed" on the arms-without-ops tree (not rebuilt). Every other figure re-derived above.
10. Forward-carry: none claimed, none owed by this diff.
11. nightly-status red grades main: its log names the nightly "slow" lane failing (run 39387919507) -- this diff's one governance.yml hunk adds a step to instrument-self-tests, outside what nightly-status reads; not this PR's, and the body answers it. instrument-self-tests red at 716a34f2 is answered in the body with its cheaper detector (selftest_wiring.py --check); green at this head. pr-contract at head green, started 10:35Z after nightly-status concluded 10:04Z.
12. Head unchanged at verdict time.
13. merge-tree clean against current origin/main.
14. No budget, score, ledger, closure, INERT, golden or claim movement; self-test count rise earned by the new arms.
15. Additions stay in the existing load-modify-dump flow; no breach. Owner: .github/workflows/governance.yml is code-owned (/.github/workflows/ @tvofi, CODEOWNERS:99), so merging still needs tvofi's approving review.
Round: first verdict from this seat at this head (second reviewer at this head overall).

bus-nonce: 99034209417c54cc2ba8a44f34229a0c
