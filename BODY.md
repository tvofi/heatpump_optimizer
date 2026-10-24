R10-MERGE-SUBJECT-HARDEN: two findings from the #2423 review, recorded there and not fixed, both in the merge-subject guard in `tools/policy/agreement.mjs` (`mergeSubjectGuard`). Part of #201. No issue is filed for this group yet; the orchestrator files and wires one.

1. **The title template accepted too much.** `TEMPLATE_SUBJECT`'s second arm was `/\(#\d+\)$/`, which is only an end anchor. It passed subjects the host's `<title> (#N)` template never writes: `(#8)` (no title), `x(#8)` (no space), ` x (#8)` and `x  (#8)` (an untrimmed title), `x (#08)` and `x (#0)` (not a pull-request number), and `x \t(#8)`. The arm is now `/^\S(?:.*\S)? \(#[1-9]\d*\)$/`: a trimmed, non-empty title, one space, then `(#N)` with N ≥ 1.
2. **The writer scan read one line.** `subjectWriters` tested `MERGE_CALL` and `SUBJECT_ARG` against single lines. It missed a `--subject` on a shell continuation line, one later in an argv list split over lines, and a `commit_title` on a later line of a `merge_pull_request(` call. The live seam is `merge_train.py`'s own merge call (`self.run(["gh", "pr", "merge", str(pr), ...` in the retry loop), which spans two lines. Planting a `--subject` on its second line passes the base guard unseen. The scan now reads each match's call extent (`callExtent`). The extent starts at the innermost bracket left open before the match on its line, or at the line's start if none is open. It ends where that bracket closes, or at the first line end that is outside the call's brackets and not escaped by `\`. A blank line always ends it. Quoted text (with escapes) opens no bracket. `MERGE_CALL` also tolerates whitespace inside `gh pr merge` and `"pr", "merge"`, so an argv list broken between `"pr",` and `"merge"` is still a call.

Design choices, stated so a later seat does not read them as bugs:
- The title arm cannot tell a hand `--subject "<anything> (#N)"` from the host's template. It refuses only shapes the host never writes. The writer scan, not the shape, is what keeps hand subjects out.
- The extent is the call's own bracket group, not the statement around it. So a sibling argv in the same table (`gh_read.py`'s argv table, which holds a `gh pr merge` entry next to entries carrying other flags) is not read as the merge call's. A first cut that joined whole bracketed statements raised exactly that false positive on the tree, at `gh_read.py` and `merge_train.py`'s self-test, and was replaced.
- Alternatives that lost: (a) joining lines by statement, with bracket depth carried across the file. It was refused for the false positives above. (b) Enumerating continuation spellings (`\`-newline, `,`-newline) as extra regexes, which is the #1874 spelling-list shape. The extent reader removes the line assumption instead of listing the cases it breaks on.

The `never --subject` line in `dev/governance/roles/orchestrator.md` belongs to RCA-FRICTION, not this group, and is untouched. The diff touches `tools/policy/agreement.mjs` only. It changes no `VERSION`, manifest or `RELEASE_NOTES.md`.

## Head

`09b1d002c19f941e9ba77367554e086c8cec50ee`, cut from origin/main `50af6174f53c0f9bec3f705c3a4bb99615f71acc` (the merge base; origin/main had not moved when fetched at the end of the work).

## Mutation proof

Each mutant was applied to the head's `tools/policy/agreement.mjs`, followed by `node tools/policy/agreement.mjs --self-test`, then a restore. All 11 were killed. The failing probes:

- M1, title arm back to `/\(#\d+\)$/`: `FAIL a subject GitHub's title template never writes is refused` (35 of 36).
- M2, number back to `\d+`: `FAIL a subject GitHub's title template never writes is refused` (35 of 36).
- M3, extent ends at every line end (the line scan): `FAIL a --subject on a shell continuation line is refused, at the call line`, `FAIL a --subject in an argv list split over lines is refused`, `FAIL an argv list broken between "pr" and "merge" is still a merge call`, `FAIL a merge_pull_request call whose commit_title is on a later line is refused` (32 of 36).
- M4, `\` continuation ignored: `FAIL a --subject on a shell continuation line is refused, at the call line`.
- M5, the line-end check ignores bracket depth: `FAIL a merge_pull_request call whose commit_title is on a later line is refused`.
- M6, blank-line end deleted: `FAIL null control: a split merge call with no subject passes, and a flag on the next command is not the call's`.
- M7, closing the enclosing bracket does not end the extent: `FAIL null control: a sibling argv in the call's own table is not the call's`.
- M8, extent always starts at the line's start: `FAIL null control: a sibling argv in the call's own table is not the call's`.
- M9, `MERGE_CALL` back to literal single spaces: `FAIL an argv list broken between "pr" and "merge" is still a merge call`.
- M10, quote marks not read as quotes: `FAIL null control: a bracket in a quote, past an escaped quote, opens no command`.
- M11, escapes inside a quote not read: `FAIL null control: a bracket in a quote, past an escaped quote, opens no command`.

Failing test first: the head's 36 probes were run against the base's production block (`// THE GUARD.` through `subjectWriters`, swapped back in). They gave `SELF-TEST 31 of 36 probes held`. The five FAILs were the title-template probe and the four writer-miss probes named under M3. The null-control probes held at the base.

## Null control

- Finding 1, on real history: over `git log --first-parent --merges --format=%s origin/main` (1048 subjects at `50af6174f`), the old arm accepts 15 and the new arm accepts 15. No subject is accepted by one and refused by the other. The tightening refuses no subject the host has written. The rule is the two regexes above applied to each subject. Had it been false, a `DIFF` line would have printed for each subject the old arm accepts and the new refuses.
- Finding 1, synthetic: `null control: titles of the host shape pass, a parenthesis in the title included` covers `x (#8)`, `fix: a (b) (#8)` and `Revert "y (#7)" (#8)`. The existing `both GitHub templates pass the merge-subject guard` still holds.
- Finding 2, unperturbed tree: with `python3 -I tools/policy/agreement_py.py --run`, both base and head print `refused=0`. The head adds no false refusal on any of the 11 files the scan reads.
- Finding 2, synthetic: a split call with no subject flag passes. So do `--body` on the next command, a `--subject` after a blank line, a flagged sibling argv in the call's table, and a quoted bracket past an escaped quote. These are the three `null control:` writer probes.

## Figures

- Self-test at head: `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 36 of 36 probes held` (27 at the base; 9 probes added).
- The finder's harness at both ends. The instrument is `python3 -I tools/policy/agreement_py.py --run`, the wave-script's agreement run, which reads the whole tree. It ran unperturbed, and again with `"--subject", "Merge pull request #%s (x)" % pr,` inserted at the start of the second line of `merge_train.py`'s split `gh pr merge` call:
  - base `50af6174f`, unperturbed: `52 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
  - base, perturbed: `RESULT ... refused=0`. The planted writer is missed.
  - head `09b1d002c`, unperturbed: `55 merge call(s) in 11 file(s)`, `RESULT ... refused=0`, `AGREEMENT ok`.
  - head, perturbed: `REFUSED merge-subject-pr writer tools/audit/seat/merge_train.py:1482`, `refused=1`.
- Call count 52 → 55, by rule: the base counted lines matching `MERGE_CALL`; the head counts matches. A per-line census over the scanned files (the base regex `.test` per line against the head regex's `matchAll` count per line) gives 52 lines and 55 matches. The three lines that differ each hold two matches: `.claude/workflows/web-fragments.md` (the mapping-table row naming both `merge_pull_request` and `gh pr merge`) and `tools/policy/fragments_sync.mjs`'s two `GH_READ`/`GH_WRITE` lines. The whitespace-tolerant `MERGE_CALL` adds no call site on the tree. Had it added one, a line with base 0 and head 1 would have printed.
- `pair merge-subject-pr: 4 readers, 1055 items, 0 divergent`, from `python3 -I tools/policy/agreement_py.py --run` at head. The guard walks `249 first-parent commit(s) past 07a09406a`, the same at both ends.
- The class census (fixer.md step 8). Rule 1 is `git grep -n -F '\(#' -- 'tools/*.py' 'tools/*.mjs' 'tools/*.js' 'tools/*.sh' 'tests/*.py' '.github/*' '.claude/*'`, excluding `tools/audit/round*`. It returns:
  - `tools/policy/agreement.mjs` `TEMPLATE_SUBJECT`: closed in this diff.
  - `tools/policy/agreement.mjs` discovery registry `'\\(#(\\d+)\\)': 'pair:merge-subject-pr'`: a registry key, not a shape rule.
  - `tests/delivery_status.py` `SQUASH_SUBJECT`, `tools/release/stamp.py` `PR_RE`, `tools/policy/policy_lint.mjs` `MERGE_SUBJECT_RE`, and the comments near it: already guarded. Each is a PR-number reader that must read history at or before the cutoff. The `merge-subject-pr` pair holds them to agreement, and the guard ensures any new merge they read has the host shape.
  - `tools/policy/record-predicate/sweep.mjs` `/\(#(\d+)\)\s*$/`: a PR-number reader over record lines, not a merge-subject shape guard. Already outside this guard's concept.
  - `tests/delivery_status.py:152`: a comment carrying a census command.
- The class census, rule 2: `git grep -n -E 'gh pr merge|merge_pull_request' -- '*.py' '*.mjs' '*.sh'` filtered to regex and test sites. It returns `agreement.mjs` `MERGE_CALL` (closed in this diff) and `fragments_sync.mjs:213-214`. Those two test a grant string for membership and are not a writer scan, so they are a distinct concern and need no change. It also returns `dev/audit/rounds/round3/D11/agency.py` `WRITE`, a round-3 record, which stays as written (fixer.md step 10). No other line-based merge-writer scan exists.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; the one run is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `2 of 2425 ENTITY CHECKS FAILED` at head, and also `2 of 2425 ENTITY CHECKS FAILED` at base `50af6174f` in a detached worktree. Both runs fail the same two checks: the `gate-sweep.yml` U0c wiring check, and `graders-head-copy's delivery_status step is red only when ...`. Neither reads `tools/policy/agreement.mjs`. Both fail on this container at the untouched base, so they belong to the environment or to main, not to this diff. CI's run is the authority. Had the diff caused either, the base run would have printed `1 of` or `0 of`.
- run_always: `python3 tests/env_drift.py --claims-only origin/main` → `claims hygiene: origin/main ok`; `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`; `python3 tests/layout.py` → `layout self-test: ok`; `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` → `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures or fast red predicted against 50af6174f53c`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

none: `ci_predict.py` lists none, and every production line added is killed by a self-test probe (M1 to M11 above).

## Red checks

none.

## Forward-carry

n/a: neither finding changes how a later stage must work.

## Friction

none.
