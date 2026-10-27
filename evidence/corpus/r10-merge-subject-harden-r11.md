R10-MERGE-SUBJECT-HARDEN: the merge-subject writer scan in `tools/policy/agreement.mjs` (`subjectWriters`, `callExtent`). Part of #201. No issue is filed for this group; the orchestrator files and wires one.

Re-cut minimal. The guard is unchanged from the previous return: `git diff 71f6ecbeb92d26c87c8d557d264245314a7e85f7 HEAD -- tools/policy/agreement.mjs` is empty. This pass changes only the instruments. Four of them cut the guard block out of `agreement.mjs`: the argv-seam harness, the census, the differential harness and `dev/audit/rca/merge-subject-class-open/differential.mjs`. Two of them spelled the same `nonTemplateMerges` cut, which the agreement lane reported as `unregistered=1`. The cut is now one exported helper, `dev/audit/harnesses/merge_subject_guard_block.mjs` (`guardBlock`, `guardEval`), and all four import it.

The helper does not cut `nonTemplateMerges` at all. Its removal was dead code: with it deleted, every instrument prints byte-identical output at every ref it loads. A declaration that `new Function` evaluates is never called, so the later constants it reads are never read. The alternatives lost. Registering the grammar in `agreement.mjs` keeps a second copy of dead code. Exporting from `differential.mjs` runs that file's CLI on import. Re-spelling the cut by position, as the census did, hides the duplicate from the lane without removing it.

The diff touches `tools/policy/agreement.mjs`, the five `dev/audit/harnesses/r10_merge_subject_*` harnesses, the new helper, `dev/audit/rca/merge-subject-class-open/differential.mjs` and their `tests/closures.json` entries. It changes no `VERSION`, manifest or `RELEASE_NOTES.md`: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD` lists none of them.

## Head

`4dbc9c23092512db9bbbc4cee3327d7f0689883d`, which merges `origin/main` at `bc52ad2af1d0cfe95896119b649fa56e14c74b5b` onto `71f6ecbeb92d26c87c8d557d264245314a7e85f7`. Every figure below was taken at this head in this pass. "main" is `bc52ad2af1d0`. "pre-change" is the instruments at `e5aa81ea3f6c51ecc089950d5c8b8c4ca3e3e6eb`, the merge commit before the helper. `date -u` at the last figure: 2026-10-25T16:05:27Z.

## Mutation proof

Guard: `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 180 of 180 probes held`. `python3 dev/audit/harnesses/r10_merge_subject_mutants.py`: 86 rows (`grep -c '|'`), 0 `NOT APPLIED`, 2 survivors at `SELF-TEST 180 of 180` (`grep -c`). The survivors are Y9 and Y10, under Unpinned sites. Every other row prints at least one `FAIL`.

Helper: the identity comparison below is the check. A mutant that drops the helper's pre-extent opening (`const from = h`) makes `hdiff`, `rca.named`, `rca.corpus` and `rca.planted` print `DIFFER`, so the check is not vacuous. Each of those four loads main's guard, which opens at that comment. The helper was restored after the run.

## Null control

**Instrument identity, pre-change against this head.** Each instrument was run in a detached worktree at `e5aa81ea3` and again at this head, with the same arguments, and the outputs were compared with `cmp -s a b && echo IDENTICAL || echo DIFFER`:
- `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs` → IDENTICAL
- `node dev/audit/harnesses/r10_merge_subject_census.mjs` → IDENTICAL
- the same, given `bd81b886388c`'s `agreement.mjs` → IDENTICAL
- `node dev/audit/harnesses/r10_merge_subject_differential.mjs bc52ad2af1d0 e5aa81ea3` → IDENTICAL
- `node dev/audit/rca/merge-subject-class-open/differential.mjs named|corpus|planted bc52ad2af1d0 e5aa81ea3` → IDENTICAL for each of the three modes

Every one of these exits 0. The mutant under Mutation proof is the control that a difference reads `DIFFER`.

**The differential against main**, `node dev/audit/harnesses/r10_merge_subject_differential.mjs bc52ad2af1d0`:

| part | lines | refused_main | refused_head | main_not_head |
|---|---|---|---|---|
| tree | 91458 | 0 | 0 | 0 |
| plants | 714 | 245 | 245 | 0 |
| generated | 17568 | 7200 | 7200 | 0 |
| null | 7200 | 0 | 0 | — |
| TOTAL | 109740 | 7445 | 7445 | 0 |

It exits 0.

**The finder's harness**, `bash dev/audit/harnesses/r10_merge_subject_plants.sh` (it drives `python3 -I tools/policy/agreement_py.py --run`):
- unperturbed: `63 merge call(s) in 11 file(s)`, `refused=0`;
- each of the 18 spelling plants and the 4 closer-in-lead plants and their controls: `REFUSED` (`grep -c REFUSED` → 22);
- each of the 3 null plants: `refused=0`.

## Figures

- `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs`:
  - `PROGRAM-CLASS merge refused=144 of 144; view refused=0 of 144`
  - `WRAPPED merge refused=12 of 12; null refused=0 of 12`
  - `CLASS merge refused=43 of 43; null refused=0 of 43`
  - `OPEN R10-MERGE-SUBJECT-CASEARM expected-fail: held=49 of 49; null refused=0 of 49`
  - `OPEN R10-MERGE-SUBJECT-CASEARM routed expected-fail: held=0 of 3; null refused=0 of 3`
  - it exits 0.
- `node dev/audit/harnesses/r10_merge_subject_census.mjs <4aad9c11's agreement.mjs>`: `TOTAL old=63 new=63 over 290 file(s)`, `UNCOVERED 67 of 108`, `EXTENT 11 of 63`, `SPLIT 2 of 2`, exit 0.
- `python3 -I tools/policy/agreement_py.py --run` → `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` The one script is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `2 of 2445 ENTITY CHECKS FAILED`. The same two fail at main `bc52ad2af1d0` (a detached worktree, same command): `gate-sweep.yml: on CI's completion, no concurrency, ...` and `graders-head-copy's delivery_status step is red only when ...`. Neither reads a file this diff touches.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`. No budget file is in the diff.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check` → `RULES-SYNC ok: every generated rule is the generated form of its source`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, wave-script or instrument red predicted against bc52ad2af1d0 (a data-file read is not seen)`. Before `--apply-inert` it predicted one `tests / closures` red, the `INERT READS` entry for the new helper. That entry is committed.
- `python3 -I tools/audit/seat/tmp_paths.py --check` → `tmp_paths: 0 refused, 0 stale allow entries at HEAD, ledger lines added since bc52ad2af1d0`.
- `git merge-tree --write-tree origin/main HEAD` exits 0.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

`ci_predict.py` lists none. Two near-equivalent mutants survive:
- Y9: `text.slice(start, i + 1)` becomes `text.slice(start, i)`. It drops only the closing bracket character, which never holds a subject flag.
- Y10: `next < 0 ? text.length : next` becomes `next`. It changes only a file's one-character last line.

## Red checks

none. No check has run on this head yet. main's push CI may show `tests / ci-ratchet` red. That is the repo-wide artifacts-listing fault, with a hotfix in flight. This diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

The first three spellings below each print `XFAIL` in an `OPEN R10-MERGE-SUBJECT-CASEARM routed` row of the argv-seam harness (`routed expected-fail: held=0 of 3`). Main's line guard passes each of them too, so this PR regresses main on none. Each item routes as follows:

- A blank line in a Python argv. Carry: R10-MERGE-SUBJECT-CASEARM
- A blank line in a JS argv. Carry: R10-MERGE-SUBJECT-CASEARM
- A `)` in a JS `/* */` comment after `merge`. Carry: R10-MERGE-SUBJECT-CASEARM
- The group's regression-against-main control: every line main refuses stays refused at the group's head, measured by the differential above. Carry: R10-MERGE-SUBJECT-CASEARM
- Round 4's verdict non-blocking item 2, program spellings outside `PROGRAM` (`${GH:-gh}`, `$(command -v gh)`, `gh.exe`). Each is a self-test probe of `node tools/policy/agreement.mjs --self-test` that holds at this head (`SELF-TEST 180 of 180`), and the first two are finder's-harness plants that print `REFUSED`. Carry: dismissed: fixed in this pull request, each spelling is a held self-test probe (item 44acb938)
- A JS regex literal holding a closer between `merge` and the subject (`String(n).replace(/\)/g, '')`). Carry: dismissed: a lexical scan cannot tell a regex literal from division without parsing JS; no such site is on the tree, by the census's EXTENT rule above
- The two words split across expressions (`["gh", "pr"] + ["merge"]`, `args += ["--subject", s]`), in-word quoting, gh aliases and `eval`. Carry: dismissed: a lexical writer scan cannot follow any of these without evaluation; the census reads no such site, and merges go through merge_pr.sh and merge_train.py, which pass no --subject
- Y9 and Y10. Carry: dismissed: near-equivalent mutants, re-run at this head with no writer miss

## Friction

none.
