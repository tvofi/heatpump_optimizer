R10-MERGE-SUBJECT-HARDEN: the merge-subject guard in `tools/policy/agreement.mjs` (`mergeSubjectGuard`). Part of #201. No issue is filed for this group; the orchestrator files and wires one.

This is a re-cut at round 7. Round 6 was blocked on a regression. `callExtent` looked for the bracket a merge call opens in only on the line of `pr`. So when an argv was wrapped after its program (`subprocess.run(["gh",` + newline + `"pr", "merge", ...,` + newline + `"--subject", s])`), its subject on a later line went unread. The before end, `d0d35231`, had refused that writer.

The fix is a structural reader, not another spelling:
- **`callExtent` reads the open bracket from the statement's first line**, which is the line after the last blank one, and keeps the innermost bracket still open at `pr`. A line end there resets a quote, as the forward read already does, except inside a Python triple quote. This puts the wrapped argv and the exploded argv (one element per line, as black or prettier writes it) in the same class as a one-line call.
- **A comment is prose to both reads**, by the file's language (`commentAt`): Python `#`, a `#` that starts a shell or Markdown word, and JS `//`. The first cut without this read a parenthesis in a shell comment block (`merge_pr.sh:152`) as an open call, and the finder's harness refused the unmodified tree. That over-fire is now pinned by a null probe.
- **`VALUE` is a run of parts**, where no two parts can open at the same character and the bare part is one character, so a failing match takes linear time. The parts are a quoted run, a slot, a bracketed subscript, call arguments, a lone `$`, and a bare character. So `cfg["repo"]`, `os.environ["REPO"]`, `f"{o}/{r}"`, `REPOS[0]`, `join(o, r)`, JS `cfg['repo']` and `"$O"/"$R"` are each one value.
- **`GAP` reads more between the words**: a `#` or `//` comment to the line end, a `/* */` comment, and the join of two adjacent string literals (`"gh pr " "merge 9 ..."`).

This settles all five round-6 findings in code. None is carried as dismissed.

The diff touches `tools/policy/agreement.mjs` and the four `dev/audit/harnesses/r10_merge_subject_*` harnesses. All of them already have their `tests/closures.json` entries. It changes no `VERSION`, manifest or `RELEASE_NOTES.md`: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD` lists none of them.

## Head

`0260b62dbcdbef574aafb9f1972d3abc54f0f5c3`. It merges `origin/main` at `ab00437c94bd8d8ca7b47b69095c47535f3e645a` onto the round-6 head `683dd52cbb938ad00b38857117710791f5581f4b`.

Every figure below was taken in this pass, at this head's tree. `date -u` at the last figure: 2026-10-25T05:10:00Z. The before end is `d0d35231c633ca447acf04770f9034281417b72d`, the head before round 6's re-cut.

## Mutation proof

- **Failing test first**, by commit on this branch, with `node tools/policy/agreement.mjs --self-test`:
  - at `9f248c37` (round 6's guard plus the extent probes): `SELF-TEST 143 of 148 probes held`. Five fail:
    - `extent: an argv wrapped after its program`;
    - `... after a variable program`;
    - `an exploded argv`;
    - `an exploded JS argv`;
    - `an exploded call of separate arguments`.

    Each is `... is one call in every file kind, its subject refused`.
  - at `1d087292` (the extent fix plus the value and gap probes): `SELF-TEST 158 of 168 probes held`. The ten `gap:` probes fail.
  - at this head: `SELF-TEST 177 of 177 probes held`.
- **Mutation table.** `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` gives 84 rows and no `NOT APPLIED`. Exactly Y9 and Y10 print `177 of 177` (Forward-carry). These rows cover the new parts:
  - P1, the line-local scan restored: `170 of 177`;
  - P2, the statement start never moves back: `170`;
  - P3, no quote reset at a line end in the backward read: `176`;
  - P4, a triple quote reset at a line end: `176`;
  - C1 to C5, the comment reader: each `176` or `174`;
  - G1 to G4, the `GAP` comment and literal-join arms: `174` to `176`;
  - R11g to R11j, the new `VALUE` parts and the run: `173`, `176`, `176`, `166`.

  X5 is now killed (`176`) by the enclosing-table null probe, where round 6 had to disposition it.

## Null control

- **The unmodified tree under the finder's harness.** `bash dev/audit/harnesses/r10_merge_subject_plants.sh` and `bash dev/audit/harnesses/r10_merge_subject_plants.sh d0d35231c633ca447acf04770f9034281417b72d` each run `python3 -I tools/policy/agreement_py.py --run` unperturbed:
  - this head: `63 merge call(s) in 11 file(s)`, `refused=0`;
  - the before end: `58 merge call(s) in 11 file(s)`, `refused=0`.
- **Null plants**, refused=0 at both ends:
  - a wrapped argv with no subject and a later `other("--subject", s)`;
  - an f-string program running `pr view`;
  - `gh pr view -t "x y"`.
- **Self-test nulls.** Every new `gap:` probe has a `pr view` twin. There are also:
  - the enclosing-table siblings on earlier and later lines;
  - a parenthesis in a shell or Python comment line;
  - a prose apostrophe;
  - `${#a[@]}`.

  All are held.

## Figures

- `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 177 of 177 probes held`.
- **The extent class, generated independently of the guard's probes.** `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <agreement.mjs>` runs four shapes whose bracket opens lines before `pr` (wrapped after `gh`, wrapped after `GH`, exploded argv, exploded JS argv), each under `.py`, `.mjs` and `.sh` names. Each shape runs once with the subject on a later line and once with none plus a later statement's flag (the null). Each guard was passed as a file from `git show <sha>:tools/policy/agreement.mjs`:
  - this head: `WRAPPED merge refused=12 of 12; null refused=0 of 12`;
  - `683dd52c`: `WRAPPED merge refused=0 of 12; null refused=0 of 12`. This is the regression;
  - `d0d35231`: `WRAPPED merge refused=3 of 12; null refused=0 of 12`. Only the wrapped-after-`gh` shape is refused there.

  The program class is unchanged: `PROGRAM-CLASS merge refused=144 of 144; view refused=0 of 144` at this head and at `683dd52c`.
- **The finder's harness at both ends, under plants** (the two `r10_merge_subject_plants.sh` runs above):
  - `an argv wrapped after its program` (the round-6 Block's writer): `refused=1` at this head (`merge_train.py:4982`) and `refused=1` at the before end (`merge_train.py:4981`). The reported line is the line of `pr` here and the program's line there.
  - Two plants give `refused=1` at this head and `refused=0` at the before end:
    - `an exploded argv`;
    - `a subscript value between pr and merge`.
  - The five round-6 gains still give `refused=1` here and `0` there: the f-string, `%`-format and `.format` programs, `${cfg.gh}` and `gh pr -R $(cat r) merge`.
  - The other ten plants give `refused=1` at both ends.
- **Every seam on the tree:** `node dev/audit/harnesses/r10_merge_subject_census.mjs <683dd52c's agreement.mjs>`, over the 290 files the guard scans. Its rules do not depend on spelling.
  - `TOTAL old=63 new=63` with no `DIFF` line. The new `VALUE` and `GAP` arms add no match on the tree.
  - Line rule: `UNCOVERED 57 of 98 line(s) holding both words`. These are the round-6 kinds: `refs/pull/<n>/merge` refs, dict keys and values, and interpolated pull-request numbers in prose.
  - Cross-line rule, new: `SPLIT 1 of 1`. This is a `pr` word followed by a `merge` word on a later line, with at most three tokens between, that no match covers. The one hit is `tools/policy/check-wave-script.mjs:234`, the `STAGE_REFERENT` table rows `review: [['pr', 'open_pr'], ...]` and `merge: [...]`. It is a table, not a call.
  - Extent rule, new: `EXTENT 11 of 63`. These are matches whose statement (its first line to the next blank line) holds a subject flag outside the extent read. I read each of the 11. Every one is the flag of another command in the same paragraph:
    - `"-F"` of a `gh api` row at `gh_read.py:446`;
    - `-b main` of `throwaway_git_init` at `merge_pr.sh:152` and at `merge_train.py:3127`, `:3138`, `:3252`, `:3256` and `:3287`;
    - a fake gh reading another call's `--body-file` at `merge_train.py:2556`, `:2561`, `:4023` and `:4053`.

    So no seam is open.
  - The extent rule's null control: the round-6 Block's writer appended to `merge_train.py`, then `node dev/audit/harnesses/r10_merge_subject_census.mjs <d0d35231's agreement.mjs> <683dd52c's agreement.mjs>`, which reads with round 6's guard. It gives `EXTENT 12 of 64`, listing `merge_train.py:4981: flag "\"--subject"`. With this head's guard as the second argument, it gives `EXTENT 11 of 64`. The file was then restored.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` The script is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `2 of 2440 ENTITY CHECKS FAILED`, at this head and at `origin/main` `ab00437c94bd` (a detached worktree, same command). Both runs fail the same two checks:
  - `gate-sweep.yml: on CI's completion, no concurrency, ...`;
  - `graders-head-copy's delivery_status step is red only when ...`.

  Neither reads a file this diff touches.
- run_always, at this head:
  - `python3 tests/env_drift.py --claims-only origin/main` → `claims hygiene: origin/main ok`;
  - `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`;
  - `python3 tests/layout.py` → `layout self-test: ok`;
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` → `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check` → `RULES-SYNC ok: every generated rule is the generated form of its source`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, wave-script or instrument red predicted against ab00437c94bd (a data-file read is not seen)`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` → `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
- `git merge-tree --write-tree origin/main HEAD` exits 0, with no conflict.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

`ci_predict.py` lists none. Two surviving mutants and two bounds remain, each dispositioned under Forward-carry:
- **Y9:** the close `text.slice(start, i + 1)` becomes `text.slice(start, i)`. It drops only the closing bracket character, which never holds a subject flag.
- **Y10:** the blank-line test's `next < 0 ? text.length : next` becomes `next`. It changes only a file's one-character last line.
- **A blank line between the open bracket and `pr`.** The statement read starts after the last blank line, so a bracket opened before a blank line inside an argv is not seen. That is the same bound the forward read already sets in a shell or prose file. Black never writes a blank line inside a bracket. The census's SPLIT and EXTENT rules read no such site on the tree.
- **The two words split across expressions, or spelled through evaluation.** A lexical scan cannot read these:
  - `["gh", "pr"] + ["merge"]`;
  - `args += ["--subject", s]`;
  - in-word quoting (`m"erge"`);
  - a gh alias;
  - `eval` of a built string.

  `git grep -n -e '--subject' tools/audit/seat/merge_pr.sh tools/audit/seat/merge_train.py` prints nothing.

## Red checks

none. No check has run on this head yet. main's push CI may show `tests / ci-ratchet` red. That is the repo-wide artifacts-listing fault, with a hotfix in flight. This diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

- A blank line between an argv's open bracket and `pr`, under Unpinned sites. Carry: dismissed: the statement read is bounded by a blank line, as the forward read is in shell and prose files; black writes no blank line inside a bracket, and the census SPLIT and EXTENT rules read no such site on the tree
- The two words split across expressions or spellings, under Unpinned sites. Carry: dismissed: a lexical writer scan cannot follow words split across expressions, in-word quoting, gh aliases or eval; the census reads no such site on the tree; merges go only through merge_pr.sh and merge_train.py, which never pass --subject
- Y9 and Y10. Carry: dismissed: near-equivalent mutants, re-run at this head with no writer miss

## Friction

none.
