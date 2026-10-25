R10-MERGE-SUBJECT-HARDEN: the merge-subject writer scan in `tools/policy/agreement.mjs` (`subjectWriters`, `callExtent`). Part of #201. No issue is filed for this group; the orchestrator files and wires one.

Round 9, re-cut minimal. Round 8 was blocked because the head regressed main: a line whose lead holds a closer with no opener on the line was refused by main's line guard and passed by the extent reader. The reviewer's case is a wrapped Markdown parenthetical closing on the merge line, `down) with gh pr merge 9 --subject x`. List markers (`1)`, `a)`, `:)`), case arms and a shell array closed on the merge line are the same class.

The fix is the root fix round 7 named. The cause: with no bracket open at `pr`, `callExtent` starts its forward read at the line's start, and a closer there drove the depth below zero and ended the call before `pr`. Now a closer before `pr` that drives the depth below zero is skipped and the depth stays 0. Past `pr` it still ends the call. No guard main has is removed or loosened: the change only lengthens an extent that ended before `pr`. The stated class is unchanged: the `CLASS`, `PROGRAM-CLASS` and `WRAPPED` rows of `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <agreement.mjs>`.

The diff touches `tools/policy/agreement.mjs`, the five `dev/audit/harnesses/r10_merge_subject_*` harnesses (the differential is new) and their `tests/closures.json` entries. It changes no `VERSION`, manifest or `RELEASE_NOTES.md`: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD` lists none of them.

## Head

`71f6ecbeb92d26c87c8d557d264245314a7e85f7`. It merges `origin/main` at `b89fea13e99f23cc75f01bb1604030cabea4ca66` onto round 9's code head `2cb5fd9619329d1c8c277ee2df5ae4bffce8ea66`, which merged `102f74975840` onto round 8's head `4aad9c1175318dec0b90da4113259c3ddb38309f`. The code is round 9's: `git diff 2cb5fd961 HEAD` over the diff's files is empty, and `origin/main` changed no `tools/policy/agreement.mjs` line since `102f74975840`. Every figure below was taken at this head in this pass. "main" below is `b89fea13e99f`, whose guard is the line guard. Each other end's guard was passed as `git show <sha>:tools/policy/agreement.mjs` to a file.

## Mutation proof

Failing test first. Commit `598636fe5` adds three self-test probes and changes no guard line: `git diff 4aad9c1175318dec0b90da4113259c3ddb38309f 598636fe5 -- tools/policy/agreement.mjs` adds 11 lines, all in `selfTest`. The probes are:
- the reviewer's line in a `.md` file, refused at line 2;
- `1)`, `:)`, `*)` and `[0-9]*)` arms, and `x=(` / ` a` / `); gh pr merge 9 --subject x`, each refused;
- a null control: the same prose with no subject, with a later line's `gh pr edit 9 --title t`, passes.

`node tools/policy/agreement.mjs --self-test`:
- at `598636fe5`, whose guard is 4aad9c11's byte for byte: `SELF-TEST 178 of 180 probes held`, with exactly the first two probes printing `FAIL`;
- at this head: `SELF-TEST 180 of 180 probes held`.

`python3 dev/audit/harnesses/r10_merge_subject_mutants.py`: 86 rows, none `NOT APPLIED`, exit 0. Rows are counted by `grep -c '|'` and survivors by `grep -c 'SELF-TEST 180 of 180'`, which prints 2. Two rows are new:
- K1 deletes the skip: `SELF-TEST 178 of 180`, both closer probes `FAIL`.
- K2 skips the closer but keeps the depth negative: `179 of 180`, the null control `FAIL`.

The survivors are Y9 and Y10, under Unpinned sites.

## Null control

**The differential against main**, the brief's acceptance (1): `node dev/audit/harnesses/r10_merge_subject_differential.mjs b89fea13e99f [<head-ref>]`. It runs main's and the head's `subjectWriters` over one corpus. It counts lines read, refused `file:line` keys at each end, and the keys main refuses and the head does not (main_not_head). Refused-at-main is a subset of refused-at-head exactly when main_not_head is 0. The corpus:
- tree: the 290 files the guard scans;
- plants: the reviewer's round-8 plants, copied verbatim from the verdict's `md_plant.sh`, `probe.mjs`, `probe2.mjs` and `probe3.mjs`;
- generated: 25 closer-in-lead leads × 8 writers × 3 tails × 3 indentations × 4 file kinds. The leads are list markers, case arms (default and glob included), bare closers, statement tails, and a parenthetical, link, array, JS callback or Python list opened on the line before;
- null: each generated writer with its subject flag deleted.

| part | this head | 4aad9c11 (null control) |
|---|---|---|
| tree | lines=90745 refused_main=0 refused_head=0 main_not_head=0 | same |
| plants | lines=714 refused_main=245 refused_head=245 main_not_head=0 | refused_head=190 main_not_head=55 |
| generated | lines=17568 refused_main=7200 refused_head=7200 main_not_head=0 | refused_head=1800 main_not_head=5400 |
| null | lines=7200 refused_main=0 refused_head=0 | same |
| TOTAL | lines=109027 refused_main=7445 refused_head=7445 main_not_head=0, exit 0 | refused_head=1990 main_not_head=5455, exit 1 |

At 4aad9c11 the `MAIN-NOT-HEAD` lines include the reviewer's line, `plants f.md:2 "Merge it by hand (the train is\ndown) with ...`.

**The finder's harness**, `python3 -I tools/policy/agreement_py.py --run`, driven by `bash dev/audit/harnesses/r10_merge_subject_plants.sh [<sha>]`. This round adds the reviewer's plant to it, appended to `.claude/workflows/web-fragments.md`, with its no-parenthesis control:

| plant | this head | 4aad9c11 | main |
|---|---|---|---|
| unperturbed | 63 calls, refused=0 | 63, refused=0 | 53, refused=0 |
| the 18 spelling plants (each `<name>: ... refused=1`) | refused=1 each | refused=1 each | refused=0 each |
| a closer in the lead: a case arm without its paren | **refused=1** | **0** | 1 |
| control: the same case arm with its paren | refused=1 | 1 | 1 |
| a closer in the lead: a Markdown parenthetical wrapped onto the merge line (the reviewer's line) | **refused=1** | **0** | 1 |
| control: the same prose with no parenthesis | refused=1 | 1 | 1 |
| the three null plants (no subject, `pr view` twice) | refused=0 | 0 | 0 |

Every run exits 0. So on every closer-in-lead plant the head now refuses what main refuses, and 4aad9c11 does not.

## Figures

**The stated class**, from `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <agreement.mjs>`:

| line | this head | 4aad9c11 | main |
|---|---|---|---|
| `PROGRAM-CLASS merge refused=` | 144 of 144 | 144 | 12 |
| `WRAPPED merge refused=` | 12 of 12 | 12 | 0 |
| `CLASS merge refused=` | 43 of 43 | 43 | 13 |
| every null twin of the three | 0 refused | 0 | 0 |
| `OPEN R10-MERGE-SUBJECT-CASEARM expected-fail: held=` | 49 of 49 | 16 of 49 | 49 of 49 |
| `OPEN R10-MERGE-SUBJECT-CASEARM routed expected-fail: held=` | 0 of 3 | 0 of 3 | 0 of 3 |

The case-arm enumeration now adds the `*)` default arm and the `[0-9]*)` glob arm to `never)`, `(never)`, `a|b)` and `(a|b)`. Each is run at indentation 0, 2 and 8 spaces and a tab, in `.sh` and `.md`, plus the one-line `x)`. That is 49 spellings. Every one holds at this head, as at main.

**Every seam on the tree:** `node dev/audit/harnesses/r10_merge_subject_census.mjs <4aad9c11's agreement.mjs>`, over 290 files:
- `TOTAL old=63 new=63`, with no `DIFF` line;
- `UNCOVERED 62 of 103`, `EXTENT 11 of 63`, `SPLIT 2 of 2`.

The EXTENT and SPLIT lines are the same sites the round-8 review read:
- EXTENT is another command's flag in the same paragraph: `gh_read.py:446`, `merge_pr.sh:152`, and `merge_train.py:2556`, `:2561`, `:3127`, `:3138`, `:3252`, `:3256`, `:3287`, `:4023` and `:4053`;
- SPLIT is `check-wave-script.mjs:234`, a table, and `cloud_relay.sh:44`, a comment.

**The gate and the hygiene checks**, at this head:
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` The script is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `2 of 2440 ENTITY CHECKS FAILED`. The same two fail at `origin/main` `b89fea13e99f` (a detached worktree, same command): `gate-sweep.yml: on CI's completion, no concurrency, ...` and `graders-head-copy's delivery_status step is red only when ...`. Neither reads a file this diff touches.
- run_always:
  - `python3 tests/env_drift.py --claims-only origin/main` → `claims hygiene: origin/main ok`;
  - `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`;
  - `python3 tests/layout.py` → `layout self-test: ok`;
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` → `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`, exit 0. No budget file is in the diff.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check` → `RULES-SYNC ok: every generated rule is the generated form of its source`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, wave-script or instrument red predicted against b89fea13e99f (a data-file read is not seen)`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` → `tmp_paths: 0 refused, 0 stale allow entries at HEAD, ledger lines added since b89fea13e99f`.
- `git merge-tree --write-tree origin/main HEAD` exits 0.
- `origin/main` moved to `0825aee641c8` (#2749, #2775, #2780) after these figures. `git merge-tree --write-tree origin/main HEAD` against it also exits 0: `tests/closures.json` merges as a set through the ledger driver. No figure here was re-taken against it.

`date -u` at the last figure: 2026-10-25T14:17:09Z.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

`ci_predict.py` lists none. Two near-equivalent mutants survive:
- Y9: `text.slice(start, i + 1)` becomes `text.slice(start, i)`. It drops only the closing bracket character, which never holds a subject flag.
- Y10: `next < 0 ? text.length : next` becomes `next`. It changes only a file's one-character last line.

## Red checks

none. No check has run on this head yet. main's push CI may show `tests / ci-ratchet` red. That is the repo-wide artifacts-listing fault, with a hotfix in flight. This diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

R10-MERGE-SUBJECT-CASEARM's carry on the roster branch `handoff/audit-r10-roster` at `dbd592fe4` (`roster_edit append-carry R10-MERGE-SUBJECT-CASEARM`) records that round 9 already closes the case-arm class (49 of 49 at this head, in the table above) and that the group's remaining scope is the three spellings below. Each is an `OPEN R10-MERGE-SUBJECT-CASEARM routed` row of `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <agreement.mjs>`, printing `XFAIL` at this head, at 4aad9c11 and at main (`routed expected-fail: held=0 of 3`). Main's line guard passes each too, so this PR regresses main on none of them. Each item routes as follows:

- A blank line in a Python argv (its `routed a blank line in a Python argv` row prints `XFAIL`). Routed to the group as the first spelling of its carry at `handoff/audit-r10-roster` `dbd592fe4`. Carry: R10-MERGE-SUBJECT-CASEARM
- A blank line in a JS argv (its `routed a blank line in a JS argv` row prints `XFAIL`). Routed to the group as the second spelling of its carry at `handoff/audit-r10-roster` `dbd592fe4`. Carry: R10-MERGE-SUBJECT-CASEARM
- A `)` in a JS `/* */` comment after `merge` (its `routed a closer in a JS block comment` row prints `XFAIL`). Routed to the group as the third spelling of its carry at `handoff/audit-r10-roster` `dbd592fe4`. Carry: R10-MERGE-SUBJECT-CASEARM
- The group's regression-against-main control: every line main refuses stays refused at the group's head, measured at the stage's merge base by the differential above. The group's first carry entry on the same roster branch records it, and the carry at `dbd592fe4` adds each routed spelling's plant at both ends. Carry: R10-MERGE-SUBJECT-CASEARM
- Round 4's verdict non-blocking item 2, program spellings outside `PROGRAM` (`${GH:-gh}`, `$(command -v gh)`, `gh.exe`). Each is a self-test probe that holds at this head (`SELF-TEST 180 of 180`), and the first two are plants of the finder's harness at refused=1. Carry: dismissed: fixed in this pull request, each spelling is a held self-test probe (item 44acb938)
- A JS regex literal holding a closer between `merge` and the subject (`String(n).replace(/\)/g, '')`). Carry: dismissed: a lexical scan cannot tell a regex literal from division without parsing JS; no such site is on the tree, by the census's EXTENT rule above
- The two words split across expressions (`["gh", "pr"] + ["merge"]`, `args += ["--subject", s]`), in-word quoting, gh aliases and `eval`. Carry: dismissed: a lexical writer scan cannot follow any of these without evaluation; the census reads no such site, and merges go through merge_pr.sh and merge_train.py, which pass no --subject
- Y9 and Y10. Carry: dismissed: near-equivalent mutants, re-run at this head with no writer miss

## Friction

none.
