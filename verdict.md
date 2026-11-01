Fix review: merge ac4441b465bd44bef5b13206e38e60a1482c92bd

bus-nonce: 83a7f015bf5d23b33c80f970df1619f7

Round 1. Measured head ac4441b465bd44bef5b13206e38e60a1482c92bd from a detached worktree; origin/main at review time 61b0076f4854, merge base of the PR c3a47e5656ef. Re-read at post: CI classify GREEN for this head (pending none, red none).

## Evidence
- RESULT finder harness r10_merge_subject_argv_seam.mjs, head's harness run against main's guard and head's guard: LEXER merge refused=44 of 60 at main, 60 of 60 at head; null (pr view) refused=0 of 60 at both; routed rows held=0 of 3 at main, 3 of 3 at head; OPEN CASEARM class held=49 of 49 at both; null refused=0 of 49.
- RESULT differential.mjs planted origin/main vs 6920bbc: planted=96949 main_not_head=0. Positive control against 4aad9c117: main_not_head=9585 (body says 9581; origin/main has moved on since the body was written, so the corpus is larger, same shape: unmatched-closer-in-lead 9524, other 61). Corpus mode: lead-closer=192 control=96 null=0 main_not_head=0, as the body.
- RESULT r10_merge_subject_differential.mjs origin/main head: TOTAL lines=124513 refused_main=7445 refused_head=7445 main_not_head=0 (body: lines=124477, same refused counts; the line total follows the moved main). Null lines refused 0 at both.
- RESULT agreement.mjs --self-test: 212 of 212 probes held. Mutants script: Y9 and Y10 survive, both with 212 of 212 held; they touch only the closing-bracket slice end and a single-character last line, so no probe distinguishes them, as the body argues. Every other mutant row, including S1, S2, S3, S5, S6, C5, fails at least one probe (read in the output, e.g. S1 210 of 212).
- RESULT live tree: python3 -I agreement_py.py then agreement.mjs --py-json: divergent=0 unregistered=0 dead=0 refused=0 at head and at main (head 10.8 s, main 10.3 s). No file in the live tree newly refuses. Corpus over 378 historical files shows refused_head = refused_main = 7445, so no historical file newly refuses either; I did not scan a separate branch tree beyond that corpus.
- RESULT census at the head against main's guard: the output differs only in the TOTAL old=70 new=70 line printed when main's guard is passed; UNCOVERED 75 of 123, EXTENT 9 of 70, SPLIT 3 of 3 as the body.
- Own attacks (ev/own_attacks.txt): a line-start division with a later division hiding a --subject flag after a mis-read regex is still refused at both ends (the call's flag stayed visible); a regex literal holding a backtick before a wrapped argv, and a Python argv holding a blank line and a ')' string, pass at main and are refused at the head; nothing that main refused passes at the head; null refused=0.
- Performance: 2000 bracketless merge calls in a 130 KB JS file take 1.8 s at main and 4.6 s at the head; both superlinear on that artificial shape, the live tree (70 calls) costs 10.8 s against 10.3 s. This is a measurement, not a defect of the diff.
- python3 tests/structure.py: STRUCTURE RATCHET PASSED. Diff holds 4 files (agreement.mjs, two harnesses, delivery/3076.md); no VERSION, manifest, RELEASE_NOTES, golden or claim file is touched. No new tracked file.
- git merge-tree --write-tree origin/main head: clean, tree 0a42adf7, no conflicting path.
- CI: merge_train.py classify exits 0, GREEN for ac4441b465bd44bef5b13206e38e60a1482c92bd. The gate check was still running when the packet was rendered; classify at post time is GREEN, nothing red. Not re-run: gate, mutation (cited from CI).
- The three routed spellings are pinned: they pass at main and are refused at the head, with pr view twins passing at both.
