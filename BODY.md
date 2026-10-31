R10-MERGE-SUBJECT-CASEARM: the merge-subject guard's call extent (`callExtent` in `tools/policy/agreement.mjs`) now reads each file's language the way the language reads it. Issue #2803 (the roster's `issues`; its `fixes` is empty, so this body closes none). Part of #201.

#2697 r9 already closed the case-arm class (the brief's original scope; Carry 3). Its body routed three spellings here as open, and each one passed the guard at main:
1. a blank line inside a Python argv, between the argv's bracket and `pr`;
2. the same in a JS argv;
3. a `)` inside a JS `/* */` comment after `merge`.

Two causes, both in `callExtent`:
- The backward read that finds the bracket a call opens in starts at the statement's first line, the line after the last blank one. A bracket opened above a blank line is never seen, so the extent becomes the `pr` line alone. A blank line ends nothing inside a Python or JS bracket.
- The comment reader knew `#` and `//` but not JS `/* */`. A closer in a block comment ended the call.

The three are instances of one class: **a lexical construct of the file's language that holds a bracket or a line end, standing in a merge call, read differently by the extent reader than by the language.** The new `LEXER` matrix in `dev/audit/harnesses/r10_merge_subject_argv_seam.mjs` lists that class's seams by rule. Each row is one (language, construct) pair: comments, every quote form, interpolation slots, blank lines, regex literals, and shell escapes and substitutions. Each row is planted at two seams with the closer that would end the call there, once with `merge` and once with `view` as the null. At main it reads 16 of 60 rows wrong, and the routed three are among them. This diff closes all 60:

- **The statement read, then the file.** `openAt` is the one backward reader. `callExtent` reads the statement first, as main does. Only when the statement opens no bracket, in a Python or JS file, does it re-read from the file's start.
- **Comments.** `commentEnd` replaces `commentAt` and returns where a comment ends. It adds JS `/* */`, which can span lines.
- **Quotes** (`quoted`, by file kind):
  - in a JS file, a backtick opens a template literal that holds its line ends, and a `/` where an expression can start opens a regex literal (`[...]` class included);
  - in a shell or prose file, a backtick opens a quote that ends with its line, and a `\` outside a quote makes the next character text;
  - an interpolation slot is code until the bracket that closes it, and then the string resumes. The slots are a template's `${`, a Python f-string's `{` (not `{{`), and a shell double quote's `$(`. Shell `${` is not a slot, because bash reads its body as a word.

Design choices, stated so a later seat does not read them as bugs:
- **The file-start re-read is a fallback.** A file-start read every time was measured worse than main: a JS regex literal holding a backtick, or an unterminated triple quote, carried into a wrapped argv that main refused, and the head then passed it. The fallback keeps every call whose statement holds its own bracket exactly as main reads it. The probe `a lexer state carried from the file start does not move a call its statement's bracket holds` pins this, and mutant P6 restores the always-read and is killed.
- **The regex literal is a heuristic.** It opens after `( , = : [ ! & | ? { } ; + - * % < > ~ ^`, a line start, or `return`. A division after an identifier or a closer is not a regex. A misread can only hide brackets on one line.
- **A shell backtick ends with its line.** In prose it is a code span, and that keeps a stray backtick from swallowing a file.

The diff touches `tools/policy/agreement.mjs` and two audit harnesses: `r10_merge_subject_argv_seam.mjs` (the LEXER matrix, plus the routed rows' new status line) and `r10_merge_subject_mutants.py` (moved needles and new rows). Both harnesses already have their `tests/closures.json` entries. The diff adds no file, and changes no `VERSION`, manifest or `RELEASE_NOTES.md`.

## Head

`6920bbc399bae4cc253653b41c9679eb53acb8fc`, the merge of `origin/main` at `c3a47e5656ef858674a1fd011c0e2f039c4ed838` into the fix head `44c8c1072d41f43e76be285ffae760eeffdc6df7`. The merge was made because main moved while the last `prepr.sh` ran. Main's delta touches `tools/pr/ci_predict.py` and records, not the guard. Every figure below was re-taken at this head between 2026-10-31T18:13Z and 18:45Z, and the merge base is `c3a47e5656ef`. The last `prepr.sh` run (rc=0) began and ended with `origin/main` at `a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0`, which moved nothing this diff touches and merges cleanly (`git merge-tree --write-tree`), so main is unmoved since that run and no second run was owed. The before end is `origin/main`. #2697's merged head is `5775b42e8f81cc80927e102191e786328b667a70`, the second parent of `f3ffb1c63`.

## Mutation proof

- **Failing test first.** `f5ae97565` adds the three routed probes alone. On main's guard they give `SELF-TEST 183 of 186 probes held`, and the three FAILs are the routed spellings (`extent: a blank line in a Python argv before "pr" ...`, `... JS argv ...`, `extent: a closer in a JS block comment after "merge" ...`). Their `pr view` nulls hold.
- **The fix deleted.** At this head, with the guard block (`// WHAT A MERGE CALL IS` to `// WHICH LINE IS MAIN'S`) replaced by main's, the result is `SELF-TEST 199 of 212 probes held`. The 13 FAILs:
  - the 3 routed spellings;
  - 8 `lexer:` probes: f-string slot holding its own quote, template slot holding a template, template slot holding an object literal and a template, regex literal, regex class holding a slash, escaped shell closer, shell `$(` in a double quote holding its quote, shell backtick;
  - 2 null controls that main over-refuses: `a shell backtick ends with its line, and an escaped line end still continues the call`, and `a template slot holds its line ends and its own braces ...`. Neither holds a subject writer, so the head refuses fewer non-writers there.

  The file was restored afterwards, and `git diff --quiet` was clean.
- **The mutation table.** `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` applies 106 mutants one at a time to the self-test. 104 are killed. No row prints `NOT APPLIED`. Y9 and Y10 survive, as they did at #2697 (Unpinned sites). The rows this diff adds or re-keys, each killed:
  - P5 (no file-start re-read): the two blank-line probes;
  - P6 (file-start read always): the carried-lexer-state probe;
  - P7 (the re-read in shell and prose too): `a prose parenthesis left open above a blank line ...`;
  - P1 to P4, X1, X2, M3, M5, M8, M10 to M12, T1 to T3, Y1, Y3, Y4, C1 and C2, re-keyed to the moved text;
  - J1 and J2 (no block comment; block comment ends at its line);
  - J3 and J4 (no template literal; template ends with its line);
  - J5 to J7 (no regex literal; regex wherever a slash stands; class not read);
  - J8 (no template slot);
  - F1 to F4 (no f-string slot; `{{` opens a slot; a slot's line end resets; a slot's own brace closes it);
  - S1 (no shell backtick), S2 (shell backtick holds line ends), S3 (no shell escape), S5 (no shell `$(` slot), S6 (shell `${` as a slot);
  - M4 (backslash continuation ignored), killed by the new Python/JS continuation probe now that a shell `\` is read as an escape.

  An equivalent mutant (S4, a shell escape that also takes a line end) was found, and its redundant condition was removed from the code instead of being listed.

## Null control

- **The unmodified tree.** `python3 -I tools/policy/agreement_py.py --out <f>` then `node tools/policy/agreement.mjs --py-json <f>` prints `merge-subject guard: 567 first-parent commit(s) past 07a09406a, 70 merge call(s) in 11 file(s)` and `RESULT divergent=0 unregistered=0 dead=0 refused=0` at this head. No false refusal on the scanned files.
- **The regression differentials, each with origin/main at both ends as the null:**
  - `planted`: `main_not_head=0` at both ends;
  - `corpus`: `null=0` and `main_not_head=0` at both ends;
  - the #2697 harness: `TOTAL ... main_not_head=0` at both ends.
- **The instrument fires on a real regression.** `node dev/audit/rca/merge-subject-class-open/differential.mjs planted origin/main 4aad9c117` gives `main_not_head=9581 {"unmatched-closer-in-lead":9520,"other":61}`. So the zero above is a measurement, not a blind instrument.
- **Each LEXER, routed and lexer row is also run with `pr view`.** `null refused=0 of 60` at both ends.

## Figures

- `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 212 of 212 probes held`.
- `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` → 106 rows. Exactly Y9 and Y10 print `212 of 212`, every other row prints FAILs, and no row prints `NOT APPLIED` (Mutation proof).
- **Carry 2 and Carry 7, the precondition and regression control,** measured at the merge base `c3a47e5656ef`, which is `origin/main`:
  - `node dev/audit/rca/merge-subject-class-open/differential.mjs planted origin/main 6920bbc399bae4cc253653b41c9679eb53acb8fc` → `planted=96919 main_not_head=0 {}`;
  - the null, `... planted origin/main origin/main` → `main_not_head=0 {}`;
  - the positive control at `4aad9c117` → `main_not_head=9581` (Null control).
- **Carry 1, the finder's corpus plus the reviewer's unmatched-closer line:**
  - `node dev/audit/rca/merge-subject-class-open/differential.mjs corpus origin/main <head>` → `lead-closer=192 control=96 null=0 main_not_head=0` (its leads include `down) with \``);
  - `node dev/audit/harnesses/r10_merge_subject_differential.mjs origin/main <head>` → `TOTAL lines=124477 refused_main=7445 refused_head=7445 main_not_head=0`;
  - the reviewer's line `down) with gh pr merge 9 --subject x`, as `f.sh` and as `f.md` through `subjectWriters`, is refused at #2697's merged head, at main and at this head.
- **Carry 1's three routed spellings: the case arm, the `*)` arm and the glob arms.** `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs` → `OPEN R10-MERGE-SUBJECT-CASEARM expected-fail: held=49 of 49; null refused=0 of 49`, at main and at this head. #2697 r9 closed them, and this diff keeps them closed.
- **Carry 3 to Carry 6 (Carry 3, Carry 4, Carry 5 and Carry 6), the three spellings planted in a merge subject.** Each is run through `subjectWriters` from each ref's `tools/policy/agreement.mjs`, the same block cut the differential uses:
  - at #2697's merged head `5775b42e8`, and at main: `passed passed passed`;
  - at this head: `REFUSED REFUSED REFUSED`;
  - their `pr view` twins: `passed` at all three.

  In the harness: `OPEN R10-MERGE-SUBJECT-CASEARM routed expected-fail: held=0 of 3` at main, and `held=3 of 3; null refused=0 of 3` at this head.
- **The class's seams (fixer step 8).** `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs [<agreement.mjs>]`, `LEXER` lines. The rule is each (language, construct) pair, planted at two seams:
  - Python: a `#` comment, `'`, `"`, `'''`, `"""` over lines, an f-string slot, an f-string slot holding its own quote, an f-string over lines, a blank line;
  - JS: `//`, `/* */`, `/* */` over lines, `'`, `"`, a template literal, a template over lines, a slot holding a template, a slot over lines, a regex literal, a regex holding a quote, a regex class holding a slash, a blank line;
  - shell: `")"`, `')'`, `\)`, `$')'`, `"${x:-)}"`, `$(echo ")")`, `"$(echo ")")"`, a backtick.

  At main it gives `LEXER merge refused=44 of 60; null refused=0 of 60`, and at this head `LEXER merge refused=60 of 60; null refused=0 of 60`. The 16 rows main reads wrong, each now closed in this diff:
  - py, f-string slot holding its own quote, after `merge`;
  - py, blank line, before `pr` (routed 1);
  - mjs, `/* */` and `/* */` over lines, after `merge` (routed 3);
  - mjs, template literal and template over lines, after `merge`;
  - mjs, slot holding a template, after `merge`;
  - mjs, regex literal and regex class holding a slash, after `merge`;
  - mjs, blank line, before `pr` (routed 2);
  - sh, `\)`, `"$(echo ")")"` and backtick, each on the line and on a continuation line.

  Every returned seam is closed. No row is left open.
- **The tree census.** `node dev/audit/harnesses/r10_merge_subject_census.mjs <main's agreement.mjs>` gives the same output for this head's guard and for main's (`diff` empty): `TOTAL old=70 new=70`, `UNCOVERED 75 of 123`, `EXTENT 9 of 70`, `SPLIT 3 of 3`, the same lines. Those lines were dispositioned in #2697, and this diff moves none of them.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` The one script is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `ALL 2493 ENTITY CHECKS PASSED`, rc 0.
- run_always:
  - `python3 tests/env_drift.py --claims-only c3a47e5656ef858674a1fd011c0e2f039c4ed838` → `claims hygiene: c3a47e5656ef858674a1fd011c0e2f039c4ed838 ok`;
  - `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`;
  - `python3 tests/layout.py` → `layout self-test: ok`;
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` → `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, governance or instrument red predicted against c3a47e5656ef (a data-file read is not seen)`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

- Y9, `callExtent`'s close `text.slice(start, i + 1)` to `text.slice(start, i)`. It drops only the closing bracket character, which never holds a subject flag. Unchanged from #2697's disposition, and re-confirmed at this head.
- Y10, the blank-line test's `next < 0 ? text.length : next` to `next`. It changes only a file's single-character last line, which cannot hold a subject flag. Unchanged from #2697's disposition, and re-confirmed at this head.
- The regex-literal heuristic opens a regex after an operator, a line start or `return`, never after an identifier or a closer. A misread can only hide brackets on one line, and the LEXER matrix's three regex rows and the division null pin both directions.
- The lexical limits #2697 dispositioned still stand: an argv built across expressions, a word quoted or escaped inside itself, a gh alias, and `eval`. Merges go only through `tools/audit/seat/merge_pr.sh` and `merge_train.py`, which pass no `--subject`.

## Red checks

none. No check has run on this head yet.

## Forward-carry

none.

## Friction

none.
