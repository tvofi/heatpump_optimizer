R10-MERGE-SUBJECT-HARDEN: the merge-subject guard in `tools/policy/agreement.mjs` (`mergeSubjectGuard`). Part of #201. No issue is filed for this group yet; the orchestrator files and wires one.

The guard does two things:
- It refuses a merge commit on main whose subject is not GitHub's template (`TEMPLATE_SUBJECT`).
- It refuses a merge call under `tools/` or `.claude/workflows/` that sets the commit subject or body (`subjectWriters`).

This diff tightens both:

1. **The title template.** `TEMPLATE_SUBJECT`'s second arm is `/^\S(?:.*\S)? \(#[1-9]\d*\)$/`: a trimmed, non-empty title, one space, then `(#N)` with N ≥ 1. The old arm was the end anchor `/\(#\d+\)$/`, which also passed `(#8)`, `x(#8)`, ` x (#8)`, `x  (#8)`, `x (#08)`, `x (#0)` and `x \t(#8)`. The host never writes any of those.
2. **The writer scan reads a call, not a line.** `callExtent` runs from the innermost bracket left open before the match on its line (or the line's start) to where that bracket closes, or to the first line end that is outside the call's brackets and not escaped by `\`. Quoted text opens no bracket. A Python triple quote is read as one quote mark, and its line ends belong to the string. A blank line ends the extent, so prose with a stray parenthesis cannot run on, except in a `.py`, `.js`, `.mjs` or `.cjs` file, where the language reads a blank line inside a bracket as nothing.
3. **`MERGE_CALL` reads every spelling of one call that gh's argv and the Python, JS and shell call forms accept.** It is built from named parts:
   - `word`: bare or quoted, ending at a non-word character;
   - `GAP`: whitespace, `\`-newline and argv commas;
   - `OPTION`/`OPTIONS`: a gh option in any gap, with or without a value;
   - `VALUE`: a quoted run, whitespace included (`-t "x y"`), or one bare run;
   - `PROGRAM`: `gh` or `gh.exe` on any path, a shell variable with or without a default (`$GH`, `${GH:-gh}`), or a command substitution (`$(command -v gh)`);
   - a quoted `pr`/`merge` arm, for an argv whose program is a variable (`[GH, "pr", "merge"]`);
   - the REST, MCP and GraphQL merges.

   `GAP` stands at three sites and `OPTIONS` at three. Each site has its own probe, and each site is mutated alone (RV1 to RV6).
   `SUBJECT_ARG` reads the long flags, the short-flag cluster `-[mrsd]*[tbF]` (gh's `pr merge` boolean flags `-m -r -s -d` before `-t -b -F`), `commit_title`/`commit_message` and `commitHeadline`/`commitBody`.

Design choices, stated so a later seat does not read them as bugs:
- The title arm cannot tell a hand `--subject "<anything> (#N)"` from the host's template. The writer scan is what keeps hand subjects out.
- The extent is the call's own bracket group, not the statement around it. So a sibling argv in the same table (`tools/audit/seat/gh_read.py`'s argv table) is not read as the merge call's.
- The blank-line exception is keyed on the file's extension. In a shell or Markdown file, a blank line inside a bracket still ends the call. A bash array spread over a blank line (`args=(gh pr merge 1` + blank line + `--subject x)`) is therefore not read. That is the cost of not running prose on, and no such site is on the tree (census below). In a code file, a `\`-continued line followed by a blank line reads one line further. That can only add a refusal.
- What a lexical scan cannot read is dispositioned under Unpinned sites: an argv built across expressions, a word quoted or escaped inside itself, a gh alias, `eval`.

The diff touches `tools/policy/agreement.mjs` and four audit harnesses under `dev/audit/harnesses/`, which have their `tests/closures.json` entries:
- `r10_merge_subject_mutants.py`: the mutation table;
- `r10_merge_subject_plants.sh`: the finder's harness under plants;
- `r10_merge_subject_census.mjs`: the tree census;
- `r10_merge_subject_argv_seam.mjs`: the dismissed argv seam.

It changes no `VERSION`, manifest or `RELEASE_NOTES.md`.

## Head

`602830571d619ee621a5ad91d5b39f056d3b14f4`, which merges `origin/main` at `2636ce9e9378addc393b749160be0bd928af4f90` (2026-10-24T20:06Z). Every figure below was taken at this head. The before end is `5d79db511e0f801cc17605e1f8e3d935b3a7980e`.

## Mutation proof

- Failing test first: the self-test at this head, with the guard block (`// WHAT A MERGE CALL IS` through `subjectWriters`) replaced by the before end's, gives `SELF-TEST 89 of 99 probes held`. That run predates the two probes added for the RV6 and T3 kills. The ten failures:
  - `spelling: a quoted multi-word option value between "pr" and "merge"`;
  - `spelling: a quoted multi-word short-option value between "pr" and "merge"`;
  - `spelling: a quoted multi-word option value before "pr"`;
  - `spelling: an argv option with a multi-word value between "pr" and "merge"`;
  - `spelling: a quoted multi-word option=value between "pr" and "merge"`;
  - `spelling: the program in a variable with a default`;
  - `spelling: the program from a command substitution`;
  - `spelling: the program as gh.exe`;
  - `a GraphQL merge in a triple-quoted string opened on its line is refused, its commitHeadline on a later line`;
  - `a blank line inside a Python argv does not end the call: its --subject is refused`.
- The mutation table: `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` applies 71 string mutants, one at a time, and runs `node tools/policy/agreement.mjs --self-test` on each. 68 are killed, each printing the FAIL lines that killed it. Three hold `101 of 101`: X5, Y9 and Y10 (Unpinned sites). No row prints `NOT APPLIED`. The kills this pass adds:
  - RV1 (`GAP` at program→pr narrowed to `\s+`): `99 of 101`;
  - RV2 (`GAP` at pr→merge narrowed): `98 of 101`;
  - RV3 (the quoted arm's `GAP` narrowed to `, `): `98 of 101`, by `a variable-program argv with whitespace before a comma`, `a variable-program argv split over lines` and `a variable-program JS argv with a run of spaces`. These are the three writer misses the review showed under RV3;
  - RV4 (no options before pr): `99 of 101`;
  - RV5 (no options between pr and merge): `95 of 101`;
  - RV6 (no options in the quoted arm): `100 of 101`, by `a variable-program argv with an option between "pr" and "merge"`;
  - R11, R11a, R11b and R11c (`VALUE`'s double-quoted, single-quoted, whitespace-holding and bare runs): `95`, `100`, `96` and `96 of 101`;
  - R13a (no default in a braced variable), R13b (no command substitution) and R16a (no `gh.exe`): each `100 of 101`;
  - T1 (no triple quote) and T2 (a line end ends a triple-quoted string): each `99 of 101`;
  - T3 (a triple quote closed by one quote mark): `100 of 101`, by `a quote mark inside a triple-quoted string does not close it`;
  - B1 (the blank-line rule in every file): `100 of 101`.

## Null control

- The unmodified tree: under the finder's harness (`python3 -I tools/policy/agreement_py.py --run`), both the before end's guard and this head's print `56 merge call(s) in 11 file(s)` and `refused=0`. The changes add no false refusal on the files the scan reads.
- Null plant: `gh pr view 1 -t "Merge pull request #1 (x)" --json title`, appended to `tools/audit/seat/merge_pr.sh`, gives `refused=0` at both ends.
- Synthetic null probes in the self-test, each of which must pass:
  - `null control: the same triple-quoted merge with no subject passes, and the next statement is not its own`;
  - `null control: a blank line inside a bracket in a shell or prose file still ends the call`;
  - `a word that only begins with "merge"`, another pr subcommand with its own `-t`, a variable program running another subcommand, a backslash before CRLF, a comment line after a continuation, `-Amt...`, a program whose name only ends in `gh`, the boolean flags alone;
  - a sibling argv, a quoted bracket, a split call with no subject, and a flag on the next command.
- Title arm: `null control: titles of the host shape pass, a parenthesis in the title included`.

## Figures

- `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 101 of 101 probes held`.
- `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` → 71 rows. Exactly X5, Y9 and Y10 print `101 of 101`, and every other row prints FAILs (Mutation proof).
- The finder's harness at both ends, under plants: `bash dev/audit/harnesses/r10_merge_subject_plants.sh [5d79db511e0f801cc17605e1f8e3d935b3a7980e]`. It runs `python3 -I tools/policy/agreement_py.py --run` with the guard from the ref or the working tree, and restores every file it touched.
  - Unperturbed: `56 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0` at both ends.
  - Each of these plants gives `refused=0` at the before end and `REFUSED merge-subject-pr writer` at the planted line with `refused=1` at this head:
    - `gh pr --subject "x y" merge`, `gh pr -t "x y" merge`, `${GH:-gh} pr merge` and `$(command -v gh) pr merge`, each appended to `merge_pr.sh` (refused at `merge_pr.sh:258`);
    - a blank line inside the argv at `merge_train.py:864`, before a `--subject` (refused at `merge_train.py:864`).
  - The five plants the before end already refused (`gh pr "merge"`, `gh pr -R o/r merge`, `gh \`-newline-`pr merge`, `-mt`, and the single-quoted argv rewrite of `merge_train.py:864`) give `refused=1` at both ends.
  - The harness's first-parent count grows with main, so it describes this SHA only. The claim that holds across heads is `refused=0` unperturbed.
- The class's seams on the tree: `node dev/audit/harnesses/r10_merge_subject_census.mjs <the before end's agreement.mjs>`, over the 287 files the guard scans. Its rule is spelling-agnostic: every line holding the words `pr` and `merge`, against the guard's matches.
  - `TOTAL old=56 new=56`: no `DIFF` line, so this pass's parts match no new tree site.
  - `UNCOVERED 60 of 95 line(s) holding both words`. I read each of the 60, and none is a merge call:
    - fake-gh case patterns and recorded-call strings in self-tests (`merge_pr.sh:152`, `:186`, `:200`, `merge_train.py:3119`, `:3121`);
    - `refs/pull/<n>/merge` refs (`ci_probe.py`, `codescan_wait.py`, `local_alerts.py`);
    - log, prose, docstring and verdict-string lines naming a pull request and a merge;
    - dict keys (`"pr": ..., "kind": "merge"`).

    So no live site of the Block's shapes (quoted multi-word value, `${VAR:-...}` or `$(...)` program, variable-program argv, triple-quoted mutation, blank line in an argv) exists. The guard's own seams are what this pass closes.
- `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs` → `[]`, `[]`, `["f:1"]`: the two argv-across-expressions shapes are missed, and the one-expression control is refused (Unpinned sites).
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` The one script is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `2 of 2425 ENTITY CHECKS FAILED`, at this head and at `origin/main` `2636ce9e9` (a detached worktree, same command). Both runs fail the same two checks:
  - `gate-sweep.yml: on CI's completion, ... its outcome read from the output's word ...`;
  - `graders-head-copy's delivery_status step is red only when this copy's exit differs from the base copy's ...`.

  Each runs a workflow step's shell, and every planted case returns step rc 1 on this box. Neither reads `tools/policy/agreement.mjs` or a harness this diff touches, so both belong to the environment or to main, not to this diff. CI is the authority.
- run_always:
  - `python3 tests/env_drift.py --claims-only origin/main` → `claims hygiene: origin/main ok`;
  - `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`;
  - `python3 tests/layout.py` → `layout self-test: ok`;
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` → `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check` → `RULES-SYNC ok: every generated rule is the generated form of its source`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures or fast red predicted against 2636ce9e9378 (a data-file read is not seen)`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

Three surviving mutants and one seam, each dispositioned by written triage. `ci_predict.py` lists none.

- X5, `callExtent`'s `start + (open.length ? 1 : 0)` to `start`. The extent then runs to the bracket enclosing the call's own group, which only adds refusals. The only probe that would kill it pins a writer miss as correct (`run(["gh", "pr", "merge", n], "--subject", s)`), which is the argv seam below.
- Y9, `callExtent`'s close `text.slice(start, i + 1)` to `text.slice(start, i)`. It drops only the closing bracket character, which never holds a subject flag. It can add no writer miss.
- Y10, the blank-line test's `next < 0 ? text.length : next` to `next`. It changes only a file's single-character last line, which cannot hold a subject flag.
- The argv-across-expressions seam. A subject flag that joins the argv in another expression is outside the call's bracket group (`run(["gh", "pr", "merge", n] + ["--subject", s])`, or `args += [...]`). The same lexical limit covers a word quoted or escaped inside itself (`gh pr m"erge"`, `g\h`), a gh alias (`gh alias set m 'pr merge'`), `eval` of a built string, and an argv held in a variable and expanded later (`"${ARGS[@]}"`). Merges go only through `tools/audit/seat/merge_pr.sh` and `tools/audit/seat/merge_train.py`, and `grep -n -e '--subject' tools/audit/seat/merge_pr.sh tools/audit/seat/merge_train.py` returns nothing. Dismissed under Forward-carry.

## Red checks

none. No check has run on this head yet. On the before end, every completed gate check was success, skipped or neutral when the review read it. main's push CI may show `tests / ci-ratchet` red: that is the repo-wide artifacts-listing fault, with its hotfix in flight. This diff does not touch `tests/ci_ratchet.py`, and that red is not this PR's.

## Forward-carry

- The argv-across-expressions seam and its in-word spellings, under Unpinned sites. Carry: dismissed: lexical writer scan cannot follow argv built across expressions, in-word quoting or escapes, gh aliases or eval; no such site on tree (census: 0 of 60 uncovered lines is a call); merges go only through merge_pr.sh/merge_train.py, which never pass --subject
- A bash array spread over a blank line, in a shell file. Carry: dismissed: the blank-line rule's cost in non-code files, which keeps prose with a stray parenthesis from running on; no such site on tree (census)
- X5, Y9 and Y10. Carry: dismissed: near-equivalent or widening-only mutants, re-confirmed at this head with no writer miss

## Friction

none.
