R10-MERGE-SUBJECT-HARDEN: the merge-subject writer scan in `tools/policy/agreement.mjs` (`subjectWriters`, `callExtent`). Part of #201. No issue is filed for this group; the orchestrator files and wires one.

This is a minimal re-cut at round 8, under the owner's three-round split. The PR's stated class is now **the spellings in the table under Figures, and no others**. The rule that enumerates them is a command: the `CLASS`, `PROGRAM-CLASS` and `WRAPPED` rows of `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <agreement.mjs>`. A spelling that the harness does not list is not claimed.

The guard is unchanged from round 7. This round adds two things, both in the harnesses:
- the class table, with a null twin per row;
- the shell case-arm writer (`never) gh pr merge ... ;;`), pinned as an expected-fail of the new group R10-MERGE-SUBJECT-CASEARM.

The diff touches `tools/policy/agreement.mjs` and the four `dev/audit/harnesses/r10_merge_subject_*` harnesses, which all have `tests/closures.json` entries. It changes no `VERSION`, manifest or `RELEASE_NOTES.md`: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD` lists none of them.

**Against main, the case arm is a regression.** main's line guard reads `never) gh pr merge "$n" --squash --subject "x" ;;` as one line and refuses it. This head does not. The finder's harness shows it: `refused=1` at the merge base and `refused=0` here (Null control). The owner ruled not to widen the guard to chase the case arm. So until R10-MERGE-SUBJECT-CASEARM lands, main would pass that one spelling, which it refuses today. No such writer exists on the tree: the finder's harness reads `refused=0` unperturbed at both ends.

## Head

`43940f751710310f4b32f0171b87b8fac153458a`. It merges `origin/main` at `1aa765fdd202647debaa7699f74bc15cf52ab674` onto the round-7 head `e73424f247781b8d5e55abe52f54d7005cb51f39`. Every figure below was taken at this head in this pass. The other ends named are:
- the merge base `1aa765fdd202`, which is main's guard;
- round 6's head `683dd52cbb93`;
- the head before round 6, `d0d35231c633`.

Each guard was passed as `git show <sha>:tools/policy/agreement.mjs` to a file.

## Mutation proof

- `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 177 of 177 probes held`.
- `python3 dev/audit/harnesses/r10_merge_subject_mutants.py`: 84 rows, none `NOT APPLIED`, exit 0 (rows counted by `grep -c '|'`; the survivors by `grep -c 'SELF-TEST 177 of 177'`, which prints 2). Each row deletes or weakens one production part of the guard and re-runs the self-test. Exactly Y9 and Y10 print `177 of 177`. They are dispositioned under Unpinned sites.
- The guard is unchanged since round 7, so the failing-test-first record of the extent, value and gap parts stands at round 7's commits `9f248c37` and `1d087292`. This round adds no production line.

## Null control

The finder's harness, `python3 -I tools/policy/agreement_py.py --run`, is driven by `bash dev/audit/harnesses/r10_merge_subject_plants.sh [<sha>]` at each end:

| plant | head | 683dd52c | merge base |
|---|---|---|---|
| unperturbed | 63 calls, refused=0 | 63, refused=0 | 53, refused=0 |
| an argv wrapped after its program | refused=1 | 0 | 0 |
| an exploded argv | refused=1 | 0 | 0 |
| a subscript value between pr and merge | refused=1 | 0 | 0 |
| the 15 other spelling plants | refused=1 each | refused=1 each | refused=0 each |
| `OPEN R10-MERGE-SUBJECT-CASEARM: a case arm without its paren` | **refused=0** | 0 | **1** |
| control: the same case arm with its paren | refused=1 | 1 | 1 |
| the three null plants (no subject, `pr view` twice) | refused=0 | 0 | 0 |

## Figures

**The stated class**, from `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <agreement.mjs>`. Each row is run with a subject, which must be refused, and as its null twin, which must pass. The twin is `pr view`, or for the REST, MCP and GraphQL rows the call without the subject field.

| row family (harness lines) | head | 683dd52c | d0d35231 | merge base |
|---|---|---|---|---|
| program class: 12 forms × 12 program expressions (`PROGRAM-CLASS merge`) | 144 of 144 | 144 | 44 | 12 |
| extent: an argv whose bracket opens lines before `pr` (wrapped after `gh` or `GH`, exploded, exploded JS), each as `.py`, `.mjs` and `.sh` (`WRAPPED merge`) | 12 of 12 | 0 | 3 | 0 |
| words, gaps, options, values, flags and the REST, MCP and GraphQL merges, 43 rows (`CLASS merge`) | 43 of 43 | 31 | 30 | 13 |
| every null twin of the three families | 0 refused | 0 | 0 | 0 |

The 43 `CLASS` rows, each printed `CLASS <row> <file>: merge refused; null passed` at this head:
- **words:** bare, double-quoted and single-quoted `merge`;
- **gaps:** `\`-newline before `pr`, before `merge` and before the subject; a Python argv in either quote; a space before a comma; `#`, `//` and `/* */` comments between the words; two adjacent literals;
- **options between the words:** `-R o/r`, `--subject "x y"`, `-t "x y"`, `-R $(cat r)`, `-R "$O"/"$R"`, `-R {repo}`, and the values `cfg["repo"]`, `os.environ["REPO"]`, `REPOS[0]`, `join(o, r)`, `f"{o}/{r}"` and JS `cfg['repo']`;
- **the flags:** `--subject x`, `--subject=x`, `--title`, `--body`, `--body-file`, `-t x`, `-tx`, `-b`, `-F`, `-mt x`, `-dmb x` and `-mF f`;
- **extent:** an exploded call of separate arguments; a call split over lines; a parenthesis in a shell comment above;
- **the API merges:** `merge_pull_request(commit_title=)`, `/pulls/N/merge -f commit_message=` and `mergePullRequest(commitHeadline:)`.

The rule for this table is the closure the reviewer asked for. Every row is refused at this head and every null twin passes. At the merge base, 30 of the 43 `CLASS` rows, 132 of the 144 program rows and all 12 extent rows pass unread. Against round 6's head, the rows this round's re-cut closed are the 12 extent rows and 12 `CLASS` rows: the comment gaps, the literal join, `"$O"/"$R"`, the six value parts and the exploded call. Those are the rows `683dd52c` misses.

**The open spellings**, from the same command's `OPEN` lines:
- `OPEN R10-MERGE-SUBJECT-CASEARM expected-fail: held=16 of 33; null refused=0 of 33` at this head, `683dd52c` and `d0d35231`, and `held=33 of 33` at the merge base. The 33 are:
  - `never)`, `(never)`, `a|b)` and `(a|b)`;
  - each at indentation 0, 2 and 8 spaces and a tab;
  - each in a `.sh` and an `.md` file;
  - plus the one-line `x) gh pr merge 9 -t s`.

  The 16 held are exactly the paren spellings. Each of the 17 printed `XFAIL` has no leading paren.
- `OPEN R10-MERGE-SUBJECT-CASEARM routed expected-fail: held=0 of 3; null refused=0 of 3` at all four ends. These are round 7's blank line in a Python argv, the same in a JS argv, and a `)` in a JS block comment after `merge`.

**Every seam on the tree:** `node dev/audit/harnesses/r10_merge_subject_census.mjs <683dd52c's agreement.mjs>`, over the 290 files the guard scans:
- `TOTAL old=63 new=63 over 290 file(s)`, with no `DIFF` line.
- `UNCOVERED 58 of 99 line(s) holding both words`. I read each of the 58. None is a `pr merge` call. They are:
  - `refs/pull/<n>/merge` refs;
  - dict keys and values (`"pr": 2526, "kind": "merge"`);
  - prose and log strings that interpolate a pull-request number;
  - one `git ... merge` in `cloud_relay.sh`.
- `SPLIT 1 of 1`: `tools/policy/check-wave-script.mjs:234`, the `STAGE_REFERENT` table. It is a table, not a call.
- `EXTENT 11 of 63`. Each is another command's flag in the same paragraph:
  - `-F` of a `gh api` row at `gh_read.py:446`;
  - `-b main` of `throwaway_git_init` at `merge_pr.sh:152` and `merge_train.py:3127`, `:3138`, `:3252`, `:3256` and `:3287`;
  - a fake gh's `--body-file` at `merge_train.py:2556`, `:2561`, `:4023` and `:4053`.

  So no seam on the tree is open.

**The gate and the hygiene checks:**
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` The script is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `2 of 2440 ENTITY CHECKS FAILED`, at this head and at `origin/main` `1aa765fdd202` (a detached worktree, same command). The same two checks fail at both: `gate-sweep.yml: on CI's completion, no concurrency, ...` and `graders-head-copy's delivery_status step is red only when ...`. Neither reads a file this diff touches.
- run_always:
  - `python3 tests/env_drift.py --claims-only origin/main` → `claims hygiene: origin/main ok`;
  - `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`;
  - `python3 tests/layout.py` → `layout self-test: ok`;
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` → `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`, exit 0.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check` → `RULES-SYNC ok: every generated rule is the generated form of its source`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 1aa765fdd202 (a data-file read is not seen)`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` → `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
- `git merge-tree --write-tree origin/main HEAD` exits 0, with no conflict.

`date -u` at the last figure: 2026-10-25T07:39:52Z.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

`ci_predict.py` lists none. Two near-equivalent mutants survive:
- **Y9:** `text.slice(start, i + 1)` becomes `text.slice(start, i)`. It drops only the closing bracket character, which never holds a subject flag.
- **Y10:** `next < 0 ? text.length : next` becomes `next`. It changes only a file's one-character last line.

## Red checks

none. No check has run on this head yet. main's push CI may show `tests / ci-ratchet` red. That is the repo-wide artifacts-listing fault, with a hotfix in flight. This diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

- The shell case-arm writer, a spelling outside the stated class. It is pinned by the `OPEN R10-MERGE-SUBJECT-CASEARM` lines of `dev/audit/harnesses/r10_merge_subject_argv_seam.mjs` and by the case-arm plant in `r10_merge_subject_plants.sh`. Against main it is a regression (see above). Its class text, which is the group's brief: R10-MERGE-SUBJECT-CASEARM (roster cfb203cab) owns every shell case-arm spelling of a merge writer: with and without the leading paren (`never) ...` and `(never) ...`), at any indentation, and multi-pattern arms (`a|b) gh pr merge ... ;;`). The roster has no brief field for it, so this text is its brief: the failing test enumerates those spellings and is marked as the group's. The cause, from the round-7 review: `callExtent` starts the forward read at the line's start when no bracket is open at `pr`, so the arm pattern's unmatched `)` ends the extent before `pr`. Carry: R10-MERGE-SUBJECT-CASEARM
- Three spellings outside the stated class and outside the case-arm class text: a blank line between an argv's bracket and `pr` in a Python or JS file, and a `)` inside a JS `/* */` comment after `merge`. They miss at every end, the merge base included, so none is a regression. They are pinned under `OPEN R10-MERGE-SUBJECT-CASEARM routed`. I route them to the guard's next owner. The roster seat should add them to that group's brief or re-route them. Carry: R10-MERGE-SUBJECT-CASEARM
- A JS regex literal holding a closer between `merge` and the subject (`String(n).replace(/\)/g, '')`). Carry: dismissed: a lexical scan cannot tell a regex literal from division without parsing JS; no such site is on the tree, by the census's EXTENT rule above
- The two words split across expressions (`["gh", "pr"] + ["merge"]`, `args += ["--subject", s]`), in-word quoting, gh aliases and `eval`. Carry: dismissed: a lexical writer scan cannot follow any of these without evaluation; the census reads no such site, and merges go through merge_pr.sh and merge_train.py, which pass no --subject
- Y9 and Y10. Carry: dismissed: near-equivalent mutants, re-run at this head with no writer miss

## Friction

none.
