Fix review: blocked 60c4b9b13e5a02bf54199b707c961e29bfe321a6 harness: class-open F1 (8 of 13 open shapes the arm misses) and F2 (a broken citation caught only on main's full run): the body says they are "routed by the orchestrator, not carried here" and names no destination, none exists, and the PR closes #2227

bus-nonce: 5a8712f16e6bb8d8f380bc316c677284

Round 3 (round 1 blocked fc75984b2, round 2 blocked 5014df139). **This is the third round and it still blocks, so round 4 is a minimal re-cut under fixer.md "Past three rounds", not a repair.** I reviewed at head 60c4b9b13e5a02bf54199b707c961e29bfe321a6, merge base d4c94f9a4, from detached worktrees with the seat venv python 3.14. The preamble diff of dev/governance/roles/ against origin/main is empty. The authored delta since 5014df139 is two commits: db1aa6583 (tests/entities.py, the widened reader) and 918f24e3f (carry-201.json, 4 lines). The rest is main's merges. merge-tree against origin/main 98fe51b42 exits 0, and the ledger driver resolved tests/closures.json.

RESULT ci: all 45 check-runs at the head completed, 30 success and 15 skipped, no failure, cancelled or neutral. All 17 required contexts are success, among them fast (3.14) 116689033932, closures 116696579703, mutation 116688919037, pr-contract 116689194979 and Analyze (python) 116688917445. No check-runs exist at the intermediate commits 69fc40453, 918f24e3f or 41f60c5a0.
RESULT finder_dora_keys_loads base=0 (ModuleNotFoundError d11lib) head=1, from the finder's d13_s3.py dora_instrument_check
RESULT corpus_churn base_rc=1 (FileNotFoundError) head_rc=0
RESULT arm at head: PASS on both checks. It reads 41 policy files and 8 carries and finds 5 cited programs, all of which run. _SP_STALE_RUN=[]
RESULT M9 /carries/1 "run the D13 instrument (tools/audit/round5/...)" restored and staged: FAIL (killed). This is round 2's block, now caught.
RESULT M10 /carries/2 `node .claude/workflows/policy_lint.mjs` restored and staged: FAIL (killed). This is round 2's finding, now caught.
RESULT M11 M10 left unstaged: PASS. The arm reads the index by design (#357).
RESULT moved spellings in any carry's remeasure, any extension: 0. I used my own probe, scan_all_paths.py, over every field of every carry.
RESULT VERSION, the manifest and the RELEASE_NOTES heading are untouched; both claim files are untouched.

Round 2's blocking point is answered. "run the D13 instrument (<path>)" is re-pointed, and the reader now takes every executable path token whatever verb comes before it. M9 shows the new reader is load-bearing. The policy_lint*.mjs commands that round 2 left non-blocking are re-pointed and caught too (M10).

What blocks:
1. F1 and F2 have no destination. The body's only disposition is "The reviewer's F1 and F2 are routed by the orchestrator, not carried here". It names no group, issue or brief. I searched for a destination and found none in any of these places:
   - wave-r10-groups.json on origin/main. R10-STALE-PATHS's `carry` holds only the RCA line and the 35-evidence-only-seams line. R10-BRIEFS-FOLD holds only the 35-seams line.
   - The roster handoff refs: audit-r10-roster ac894db5b, roster-c4 ffcf1a46a and r10-tick-roster 9b3fd503f.
   - The open PRs.
   - #201 comments since 2026-10-15.
   Both findings are about this PR's own countermeasure:
   - F1: _sp_literals misses aliases, a pathlib `/`, an f-string prefix, a dict lookup, tuple assignment and annotated assignment.
   - F2: the citation side is INERT, so a PR that adds only a broken citation is SCOPED to zero scripts, and main's full run catches it one merge later.
   The PR closes #2227. With these open and no destination, the class does not close (fixer.md step 8: "a distinct finding named by id", and finding-propagation.md). The cure is one of two:
   - Fix them in the diff.
   - Name a destination by id in the body and confirm it exists at the head before handoff. That can be a roster group's `carry` or brief, or a stage's brief, carrying round 1's plant list as the control. If the orchestrator owns the routing, it has to land before this verdict can turn.

What holds:
- The widened reader is sound and does not over-fire: 0 stale at the head, the null control's plants behave as the body states, and the floors are met.
- The body's Red checks section covers fc75984b2 (closures, closures-autofix, pr-contract) and 5014df139 (Analyze (python), cancelled then re-run 116655047872). Nothing went red at this head.
- Forward-carry: the 35-seams item is present in R10-BRIEFS-FOLD on main.

Findings (not blocks):
F4. carry-201's non-remeasure fields still spell moved paths: 26 tokens in from/control/brief, out of 37 moved spellings across 3 carries. The `brief` fields are forward constraints, not recounts. For example, /carries/2's brief says a corpus check belongs in `.claude/workflows/policy_lint.mjs`, which now lives in tools/policy/. These are prose citations, so they fall to tests/layout.py's reference arm, which stays in REPORT mode until R9-RO-9. Outside this arm's rule; listed in scan_all_paths.out.

Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2289-r3/evidence
- My own drivers and probes: arm.py, drive_d13.py and scan_all_paths.py. arm.py and drive_d13.py were inherited from round 2's reviewer.
- Outputs: arm_head.out, mutants_r3.txt, d13_both_ends.txt, churn_*.out, scan_all_paths.out, checkruns.tsv, roster_main.json, pr_body_at_review.md and head.txt.
