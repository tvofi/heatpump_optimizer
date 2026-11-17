# D5 verify-4
Trees: D5-s6 and D5-s7 measured in planted export copy ../audit-r11-px-D5-4 (PYTHONPATH=tests/hastub), load1 0.36-1.38, thread_factor 1.00.

## D5-s6-01: verify (low)
- value 3; reproduced stamp_py=3; independent comment says three vs 6 regexes; 2 dead paths confirmed by ls
- metric: count of comment claims the executed production symbol contradicts
- method: truth_checks.py in px copy (planted export copy (px-D5-4), PYTHONPATH=tests/hastub, load1 0.36-1.38, thread_factor 1.00); own grep/ls: len(RECORD_CLASS_RES)=6 entries, .claude/workflows/policy_lint.mjs absent, tools/policy/policy_lint.mjs present, tools/audit/README.md absent
- attacks: perturb stamp: stamp_py 3->0, others unchanged; null: other results unchanged
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class I5; seam_rule enumerates: True

## D5-s6-02: verify (low)
- value 1; reproduced replay_draws_py=1; independent find shows no tests/replay_draws.tsv
- metric: count of comment claims the executed production symbol contradicts
- method: truth_checks in px; find: only tests/replay_cost_draws.tsv exists
- attacks: perturb replay 1->0
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class I5; seam_rule enumerates: True

## D5-s6-03: verify (low)
- value 1; reproduced row_position_usage_rc=2; independent path absent (ls); rc 2
- metric: count of comment claims the executed production symbol contradicts
- method: truth_checks in px; grep shows docstring path dev/audit/harnesses/row_position.py
- attacks: perturb row_position 1->0
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class I5; seam_rule enumerates: True

## D5-s6-04: verify (low)
- value 1; reproduced plan_audit_usage_rc=2 unrecognized --target; independent grep: no add_argument --target
- metric: count of comment claims the executed production symbol contradicts
- method: truth_checks in px; grep plan_audit.py shows usage line with --target and subparser lacks it
- attacks: perturb plan_audit 1->0
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class I5; seam_rule enumerates: True

## D5-s6-05: verify (trivial)
- value 1; reproduced update_pr_sh=1; independent find: none
- metric: count of comment claims the executed production symbol contradicts
- method: truth_checks in px; head -2 update_pr.sh says updatepr.sh; find finds no updatepr.sh
- attacks: perturb update_pr 1->0
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class I5; seam_rule enumerates: True

## D5-s6-06: weaken (trivial)
- value 2 of 3 units; reproduced roster_lib_py=3; independent 2 unqualified units (lines 79, 642) in tracked tree; 1 qualified
- metric: comment units defining behaviour by a script no tracked path holds, unqualified by a ref
- method: truth_checks in px (3); own read of roster_lib.py: module docstring (line 9) DOES qualify it with the archive tag archive/handoff/audit-r9-alt, and git ls-tree of that tag holds handoff/round9/state/alt/gen_table_rev3.py
- attacks: perturb gen_table 3->0 (both) moves; but finder's claim 'no unit qualifies with a ref' is false for 1 of 3 units (the ref gives no file path though)
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class I5; seam_rule enumerates: True

## D5-s6-07: verify (trivial)
- value 1; reproduced plan_table_py=1; independent find: absent from tree (exists only on archive tag)
- metric: count of comment claims the executed production symbol contradicts
- method: truth_checks in px; grep plan_table.py:205 names gen_table_rev3.py, no file in tree
- attacks: perturb gen_table 1->0; weak point: sibling roster_lib cites tag, plan_table does not
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class I5; seam_rule enumerates: True

## D5-s6-08: verify (low)
- value 404 sentences/99 files; reproduced C5-len=404; independent longest 196 words by period-only split; direction agrees
- metric: prose sentences over 40 words in D5 comment units (text_ledger splitter)
- method: m4_ledger.py in px: units=3781 C5-len=404 C5_files=99 (planted export copy (px-D5-4), PYTHONPATH=tests/hastub, load1 0.36-1.38, thread_factor 1.00); own splitter on tools/replay/export.py docstring: longest sentence 196 words (finder 166, splitter difference, same direction)
- attacks: perturb --c5-split tools/replay/export.py: 404->400 (down); other cells unchanged; leave-one-out: dropping that file leaves 400 across 98+ files, aggregate not single-file driven
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class new; seam_rule enumerates: True

## D5-s7-01: verify (low)
- value 454 (1 C1 + 3 C2 + 450 C5); reproduced 454; independent 467 units with >40w sentence (own splitter)
- metric: D5 units of tests/features.py failing C1/C2/C5
- method: m4_comments.py in px: c2_fail=3 c5_fail=450 c1_fail=1 false_rows=454, units=3863; own tokenize+ast splitter on period-only: 467 units >40w (finder 450, my split breaks differently); w5-partition path at features.py:57049 verified absent (ls tools/audit/w5-partition)
- attacks: perturb c5-split 450->0; c2-define 3->0; plant 3->4; null controls move correct direction; leave-one-out not needed (single file)
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class new; seam_rule enumerates: True

## D5-s7-02: verify (trivial)
- value 14; reproduced 14; independent 14
- metric: units of tests/finite_boundary.py with a sentence over 40 words
- method: m4_comments.py in px: c5_fail=14; own splitter 14 units
- attacks: c5-split 14->0
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class new; seam_rule enumerates: True

## D5-s7-03: weaken (trivial)
- value 3 (own splitter 2); reproduced 3; independent 2
- metric: units of tests/frontend.py with a sentence over 40 words
- method: m4_comments.py in px: c5_fail=3; own period-only splitter: 2 units, so the third is splitter-sensitive (boundary at ~40 words)
- attacks: c5-split 3->0
- reach: n/a (comment/doc text; not a runtime path; HA stub irrelevant); class new; seam_rule enumerates: True

