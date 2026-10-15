Fix review: blocked 5014df1399aebbffde19178a50ab6fd999d4b379 class-open: carry-201's carries/1 remeasure still tells a seat to "run the D13 instrument (tools/audit/round5/D13/seat-a/dora_cfr.py)", a pre-move path that names no file; the new stale-command check misses it because _SP_RUN needs the path straight after `run`, and the body says the carry-201 command spellings are closed

bus-nonce: 05c9793294925756b62927821d95a987

Round 2 (round 1 blocked fc75984b2, comment 6199763846). Reviewed at head 5014df1399aebbffde19178a50ab6fd999d4b379, merge base 613b10c51, detached worktrees, seat venv python 3.14. The delta reviewed is cf477e3c7, 2f1c30b68, 7bd01490e, e0e5be6bb plus main's merge.

RESULT ci: every check-run concluded; all success or skipped except Analyze (python) = cancelled (116625518165), a required context, so it needs a re-run whatever this verdict says. closures = success (116630932631): the hand-added reads hold.
RESULT finder_dora_keys_loads base=0 head=1 (bare, at 613b10c51 / head)
RESULT corpus_churn base_rc=1 head_rc=0
RESULT arm at head: PASS, both checks; 5 cited, all runs
RESULT failing_first 2f1c30b68 = FAIL ("commands naming no file", carry-201's pre-move spellings)
RESULT M6 carry-201 restored to fc75984b2's copy (staged) = FAIL; M8 stale list never appended = FAIL (the control check)
RESULT M7 one spelling reverted = no mutant: the planted form did not exist in the file (see the block)
RESULT enumerator base=2875/368 head=2881/367, matching the body; the delta lines match the body's disposition
RESULT body figures re-derived: 2875/2881, d13 0->1, churn rc 1->0; ALL 2321 ENTITY CHECKS PASSED taken from the body, not re-run (FULL gate is CI's, fast success)

The block. With the arm's own regexes over every carry's `remeasure` strings, these executable spellings name no file at the head:
- carry-201 /carries/1: "At your own merge base: run the D13 instrument (tools/audit/round5/D13/seat-a/dora_cfr.py) with its fixtures ..." Its target is under a historical prefix, so it is inside this arm's class rule. The fixer extended that rule in-group to the citation half (F3), and the body states "The carry-201 command spellings are closed here". `_SP_RUN` requires `python3|node|bash|run` immediately before the path, so "run the D13 instrument (<path>)" is not read as a command. The arm still counts dora_cfr.py as cited only because a later sentence in the same carry ("Or run dev/audit/rounds/.../dora_cfr.py") spells it correctly. Re-point that spelling, and either widen the command reader to this shape or say in the body why it stays out.
- Outside this arm's rule (targets not under a historical prefix), a finding and not a block: carry-201 /carries/2 commands `node .claude/workflows/policy_lint_mutants.mjs` and `node .claude/workflows/policy_lint.mjs`, which moved to tools/policy/. A seat pasting them also gets ENOENT. tests/layout.py's reference arm is in REPORT mode (exit 0) until R9-RO-9, so nothing enforces that half.

What holds:
- closures repair: the three hand entries are exactly the reads CI's Linux recording named, ci-autofix.md's lapse on skip-classifier-disagrees applies, and CI closures is green at this head.
- The Red checks section names closures, closures-autofix and pr-contract, with the detector question answered (none exists; the INERT_EXCEPT-to-inert_reads lookup costed and left to the root-cause seat).
- The stale-command check is load-bearing (2f1c30b68 red, M6 and M8 red) and does not over-fire on the re-pointed carry.
- Forward-carry unchanged and present in R10-BRIEFS-FOLD; F1 and F2 named as routed by the orchestrator.

Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/revstale-ev2 (arm.py and drive_d13.py are the reviewer's own drivers; round2_mutants.txt, enum_*.out, churn_*.out, pr_body.md).
