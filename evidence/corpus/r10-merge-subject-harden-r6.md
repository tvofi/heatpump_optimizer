R10-MERGE-SUBJECT-HARDEN: the merge-subject guard in `tools/policy/agreement.mjs` (`mergeSubjectGuard`). Part of #201. No issue is filed for this group; the orchestrator files and wires one.

The guard refuses two things:
- a merge commit on main whose subject is not GitHub's template (`TEMPLATE_SUBJECT`: a trimmed, non-empty title, one space, then `(#N)` with N ≥ 1);
- a merge call under `tools/` or `.claude/workflows/` that sets the commit subject or body (`subjectWriters`, which reads the call's own extent through `callExtent`).

**`MERGE_CALL` does not read the program.** A merge call is the words `pr merge`. Each word may be bare or quoted, and gaps (whitespace, `\`-newline, argv commas) and gh options may stand between them. Whatever expression stands in program position is accepted, and so is no expression at all. That covers `gh` on a path, `$GH`, `${cfg.gh}`, an f-string's `{GH}`, `%s`, `{}`, a list element, a concatenated variable, and a wrapper of any name. So no program spelling falls outside the reader, which closes the class structurally. Pinning more spellings would not.

The parts:
- `word`: a word bare or quoted, starting and ending at a non-word character, so `merged`, `xpr` and `$pr` are not words;
- `GAP` and `option`/`OPTIONS`: a gh option in any gap, with or without a value;
- `VALUE`: a quoted run (whitespace included), a `SLOT` (`${...}`, `{...}` or `$(...)`, whitespace included), or one bare run;
- `LEAD`: the token in program position. It is read only to anchor the call's first line, and its gaps cross a line only by a `\` continuation. The extent opens at `pr`, so a bracket the lead closes is not the call's, and neither is a sibling the lead shares a table with.

Design choice, stated so it is not read as a bug: prose or a test fixture that names the two words is read as a call. That can only add a refusal, never pass a writer. On the tree it adds five reads and no refusal (census below).

The diff touches `tools/policy/agreement.mjs` and three harnesses: `r10_merge_subject_argv_seam.mjs`, `r10_merge_subject_mutants.py` and `r10_merge_subject_plants.sh`. All four already have their `tests/closures.json` entries. It changes no `VERSION`, manifest or `RELEASE_NOTES.md`; `git diff --name-only $(git merge-base origin/main HEAD)...HEAD` lists none of them.

## Head

`46d41ddc3b4ae2c768be14f1c6c04f980b2a3dd4`. It merges `origin/main` at `662a3809ced43b41dba2166f04277f2d3c95e991`. Every figure below was taken in this pass, at this head's tree, between 2026-10-25T01:30Z and 02:31Z (`date -u` at the last figure: 2026-10-25T02:30:41Z). The before end is the previous code head of this group, `d0d35231c633ca447acf04770f9034281417b72d`.

## Mutation proof

- **Failing test first.** At this head, I replaced the guard block (from `// WHAT A MERGE CALL IS` up to `function nonTemplateMerges`) with the before end's and ran `node tools/policy/agreement.mjs --self-test`. It gives `SELF-TEST 119 of 141 probes held`. Twenty-two probes fail:
  - the ten `spelling:` probes for:
    - a program whose name only ends in "gh" (a wrapper);
    - an f-string program;
    - an f-string program of another name;
    - an f-string attribute program under shell=True;
    - a %-format program;
    - a .format program;
    - a JS template program that is no identifier;
    - an unquoted command substitution value;
    - a braced default value holding whitespace;
    - an f-string slot value holding whitespace;
  - twelve of the fifteen `program class:` probes. Only the list join, the argv and the JS argv passed already.
- **Mutation table.** `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` gives 67 rows, and no row prints `NOT APPLIED`. Exactly three rows print `141 of 141`: X5, Y9 and Y10 (Unpinned sites). Every other row prints the FAIL lines that kill it. These rows cover the new parts:
  - L1, `LEAD` dropped: `139 of 141`;
  - L2, the lead's gap crosses a bare line end: `139`;
  - L3, `LINE_GAP` without the continuation: `139`;
  - L4, the extent opened at the lead instead of at `pr`: `133`;
  - L5, the program read again, as `gh` by name only: `94`;
  - R4a, `word` without the start-of-word lookbehind: `140`, killed by `null control: a word that only ends in "pr" is not the pr command`;
  - R11d, `VALUE` without `SLOT`: `138`;
  - R11e, `SLOT` without the braced arm: `139`;
  - R11f, `SLOT` without the command substitution: `140`;
  - RV2, `GAP` at pr→merge narrowed: `117`;
  - RV5, no options between pr and merge: `128`.

## Null control

- **The unmodified tree under the finder's harness.** `bash dev/audit/harnesses/r10_merge_subject_plants.sh` runs `python3 -I tools/policy/agreement_py.py --run`, unperturbed:
  - at this head: `61 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`;
  - at the before end: `56 merge call(s) in 11 file(s)`, `refused=0`.

  The five added reads are listed under Figures (census). None adds a refusal.
- **Null plants**, at both ends:
  - `if False: os.system(f"{GH} pr view {n} -t x")`, appended to `merge_train.py`, gives `refused=0`;
  - `gh pr view 1 -t "Merge pull request #1 (x)" --json title`, appended to `merge_pr.sh`, gives `refused=0`.
- **Generated null probes.** In the self-test, every `program class:` shape is run with `pr view` over all nine program expressions, and each must give no refusal. That is 15 `null control:` probes, all held. The argv-seam harness's `pr view` arm gives `view refused=0 of 144` at both ends.

## Figures

- `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 141 of 141 probes held`.
- **The class, generated independently of the guard's probes.** `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs [<agreement.mjs>]` runs twelve interpolation forms (f-string in both quotes, `%s`, `%r`, `.format`, indexed `.format`, template literal, concatenation, list join, JS array join, shell `$(...)` and `"${...}"`) over twelve program expressions (`gh`, `/usr/bin/gh`, `GH`, `gh_bin`, `self.gh`, `cfg.gh`, `cfg["gh"]`, `os.environ["GH"]`, `shutil.which("gh")`, `which_gh()`, `hub`, `hgh`).
  - At this head: `PROGRAM-CLASS merge refused=144 of 144; view refused=0 of 144`, and each of the twelve per-form lines reads `merge refused=12 of 12`.
  - At the before end (`git show d0d35231c633ca447acf04770f9034281417b72d:tools/policy/agreement.mjs` passed as the argument): `merge refused=44 of 144; view refused=0 of 144`. By form:
    - f-string, f-string with single quotes, `%`, `%r`, `.format`, indexed `.format` and concatenation: each `0 of 12`;
    - template literal: `5 of 12`;
    - shell `$(...)`: `10 of 12`;
    - shell `"${...}"`: `5 of 12`;
    - list join and JS array join: each `12 of 12`.
  - Its first three lines, the argv-across-expressions shapes, are `[]`, `[]`, `["f:1"]` at both ends (Unpinned sites).
- **The finder's harness at both ends, under plants:** `bash dev/audit/harnesses/r10_merge_subject_plants.sh [d0d35231c633ca447acf04770f9034281417b72d]`. These five plants give `refused=0` at the before end and `refused=1` at this head, each refused at the planted line:
  - an f-string program (`merge_train.py:4177`);
  - a `%`-format program (`merge_train.py:4177`);
  - a `.format` program (`merge_train.py:4177`);
  - a JS template `${cfg.gh}` (`.claude/workflows/web-fix-wave.js:534`);
  - `gh pr -R $(cat r) merge` (`merge_pr.sh:258`).

  The harness's other ten plants give `refused=1` at both ends. The first-parent count it prints grows with main, so it describes this head only.
- **Every seam on the tree:** `node dev/audit/harnesses/r10_merge_subject_census.mjs <the before end's agreement.mjs>`. It covers the 290 files the guard scans. Its rule does not depend on spelling: every line that holds the words `pr` and `merge`, checked against the guard's matches.
  - `TOTAL old=56 new=61`. Five `DIFF` lines, each read by hand and each without a subject flag in its extent:
    - `tools/audit/seat/merge_pr.sh:152`: a comment naming the recorded call;
    - `:186`: a fake gh's `"pr merge "*)` case arm;
    - `:200`: a `grep -qxF "pr merge 42 ..."` expectation;
    - `tools/audit/seat/merge_train.py:3119`: a fake-train table key `{"pr merge": [...]}`;
    - `:3121`: the `n(calls, "pr merge")` count.
  - `UNCOVERED 55 of 95 line(s) holding both words`. I read each of the 55. None holds the two words as adjacent call words. Each is one of:
    - a `refs/pull/<n>/merge` ref (`ci_probe.py`, `codescan_wait.py`, `local_alerts.py`);
    - a dict key and value (`"pr": ..., "kind": "merge"`);
    - an interpolated pull-request number (`#${fix.pr}`, `#{pr}`) in prose, a log, a docstring or a verdict string that names a merge elsewhere on the line.

    So 55 seams are already not calls, five are read and pass, and no seam is open.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` The script is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `2 of 2429 ENTITY CHECKS FAILED` at this head, and `2 of 2429 ENTITY CHECKS FAILED` at `origin/main` `662a3809ced4` (a detached worktree, same command). Both runs fail the same two checks: `gate-sweep.yml: on CI's completion, no concurrency, main's program on the trigger's run id alone, ...` and `graders-head-copy's delivery_status step is red only when this copy's exit differs from the base copy's, ...`. Each runs a workflow step's shell on this box, and neither reads `tools/policy/agreement.mjs` or a harness this diff touches. So they belong to the environment or to main, not to this diff, and CI is the authority.
- run_always, at this head:
  - `python3 tests/env_drift.py --claims-only origin/main` → `claims hygiene: origin/main ok`;
  - `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`;
  - `python3 tests/layout.py` → `layout self-test: ok`;
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` → `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check` → `RULES-SYNC ok: every generated rule is the generated form of its source`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 662a3809ced4 (a data-file read is not seen)`.
- `git merge-tree --write-tree origin/main HEAD` exits 0, with no conflict.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

`ci_predict.py` lists none. Three surviving mutants and one seam remain, each dispositioned by written triage:
- **X5:** `callExtent`'s `start + (open.length ? 1 : 0)` becomes `start`. The extent then runs to the bracket around the call's own group, which can only add refusals.
- **Y9:** the close `text.slice(start, i + 1)` becomes `text.slice(start, i)`. It drops only the closing bracket character, which never holds a subject flag.
- **Y10:** the blank-line test's `next < 0 ? text.length : next` becomes `next`. It changes only a file's one-character last line, which cannot hold a subject flag.
- **The two words split across expressions or spellings.** A lexical scan cannot read these:
  - `run(["gh", "pr", "merge", n] + ["--subject", s])`, or `args += [...]`;
  - `["gh", "pr"] + ["merge"]`;
  - a word quoted or escaped inside itself (`m"erge"`);
  - a gh alias for `pr merge`;
  - `eval` of a built string.

  The program is no longer part of this seam: any expression in that position is read. Merges go only through `tools/audit/seat/merge_pr.sh` and `tools/audit/seat/merge_train.py`. `grep -n -e '--subject' tools/audit/seat/merge_pr.sh tools/audit/seat/merge_train.py` prints nothing.

## Red checks

none. No check has run on this head yet. main's push CI may show `tests / ci-ratchet` red: that is the repo-wide artifacts-listing fault, with a hotfix in flight. This diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

- The two words split across expressions or spellings, under Unpinned sites. Carry: dismissed: a lexical writer scan cannot follow words split across expressions, in-word quoting, gh aliases or eval; the census reads no such site on the tree; merges go only through merge_pr.sh and merge_train.py, which never pass --subject
- X5, Y9 and Y10. Carry: dismissed: near-equivalent or widening-only mutants, re-run at this head with no writer miss

## Friction

none.
