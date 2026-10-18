R10-RECARRY-HEAD: every `## Head` note lands under the heading, not a quote of it. No issue is filed for this group, so the body closes none.

**Cause.** `app_push.sh --recarry` found where to write its note with `s.index('## Head')`, which is the first substring, not the heading. #2400's preamble quotes "`## Head` note" above its `## Head` heading, so both recarry notes were written into the prose:

- The live body read at 2026-10-18T16:4xZ has the fd0f5d9 note at line 13, the edc4484 note at line 15, and `## Head` at line 28.
- pr-contract refused **both** recarry heads: runs 39140677514 and 39140677791 at edc4484, and run 39142591987 at fd0f5d9.

So the brief's "at least the second recarry did not" is narrower than what happened. Every recarry of a body that quotes `## Head` above the heading misplaces its note. The number of recarries does not matter, and the self-test's single-recarry arm shows this. The later green run 39145381763 at fd0f5d9 passed only after someone hand-wrote an `update_pr.sh`-style note under the heading (line 30).

**Fix.** There is now one owner for this: `tools/pr/head_note.py`. `prefix(body, note)` finds the `## Head` heading the way `checkPrBody`'s `sections()` reads it: a line outside a code fence made of `##`, whitespace and `Head`. It inserts the note after that heading and its blank lines, so each later note sits above the earlier ones. A body with no heading exits 1 and leaves the file untouched. Callers:

- `app_push.sh --recarry` builds the same two note texts as before and calls the CLI.
- Six heredocs in `open_pr.sh`, `update_pr.sh` and `handoff_push.sh` called `s.index('## Head\n\n')`. That is the same substring class, and it misplaces a note under a fenced `## Head` example (see Figures). Each now imports `prefix` through `PYTHONPATH="$PRT"`. `$PRT` is the script's own `tools/pr`, resolved before any `cd`.

**Alternatives considered:**

1. Patch only `app_push.sh`'s heredoc to a heading regex. This was rejected because it would leave six writers with a second, weaker grammar, which is the duplication the agreement lane refuses.
2. Write the note through `push.sh`'s `write_head`. This was rejected because `write_head` rewrites the section's SHA line, while these writers prefix a record and leave the earlier text in place, and `write_head` also refuses a fenced section.
3. Have the train re-read the body after each recarry and refuse a misplaced note. This was rejected because it detects the defect one CI cycle late instead of removing it.

## Head

`4b2f770e0fe0790a49429ec369fe89b6807836b1`, branched from origin/main `5a41a56696c6bd6245b7cc1261a39a5057ba6bb0` (merge-base; origin/main's tip at 2026-10-18T17:1xZ). Every figure below was taken at this head unless marked base. The mutation proofs were taken at `8cbd4afb1`; `git diff --quiet 8cbd4afb1 HEAD -- tools/pr` holds, so they describe this head's `tools/pr`.

## Mutation proof

Each mutant was applied to `tools/pr/head_note.py` at this head, then `bash tools/pr/app_push.sh --self-test`, `python3 tools/pr/head_note.py --self-test` and `python3 dev/audit/harnesses/r10_recarry_head.py .` were run, and the file was restored with `git checkout`:

- **M1: the heading predicate becomes a substring** (`elif "## Head" in line:`).
  - app_push prints `135 checks, 4 failed`, including `FAIL double recarry: ... (got 'unnamedunnamed', want 'namednamed')` and `FAIL a single recarry of the same body ... (got 'unnamed')`.
  - head_note prints `6 checks, 5 failed`.
  - The harness prints 6 rows containing `unnamed`.
- **M2: fence tracking removed** (`fence = not fence` → `pass`).
  - app_push prints `135 checks, 1 failed` (head_note's arms).
  - head_note prints `6 checks, 1 failed`: `FAIL a \`## Head\` line inside a code fence is not the heading`.
  - The harness prints 6 rows with `fenced=unnamed`.
- **M3: the note goes before the heading line** (`return pos`).
  - app_push prints `135 checks, 4 failed`, including the null-control arm (`got '0unnamednamed'`).
  - head_note prints `6 checks, 5 failed`.
- **The base production code under the new arms (failing first).** The new arms were run against the base `app_push.sh` note heredoc, before the fix edit, and printed `app_push self-test: 133 checks, 2 failed`:
  - `FAIL double recarry: \`## Head\` names the second recarry's head, and still the first's (got 'unnamedunnamed', want 'namednamed')`
  - `FAIL a single recarry of the same body: \`## Head\` names its head ... (got 'unnamed', want 'named')`

## Null control

- **A single recarry of a body with no prose `## Head`.** The arm reads `0namednamed` at base (in the failing-first run, where that arm was `ok`) and at head. The section names both the new head and the body's own. So the arms fail on the misplacement, not on the stub machinery.
- **The arms read pr-contract's own reader.** `policy_lint.mjs --pr-body --head <sha>` is grepped for "`## Head` does not name". The harness refuses a reader run that prints no `PR-BODY:` line. Its first draft lacked that guard and read every cell `named` while `policy_lint` crashed outside a git tree. That draft was caught by M2's expected `fenced=unnamed` not appearing at base, and was fixed before any figure here was taken.
- **Harness controls.** In `r10_recarry_head.py`, the `plain` and `crlf` bodies read `named` for all six writers at both base and head.

## Figures

- `bash tools/pr/app_push.sh --self-test`: `app_push self-test: 135 checks, 0 failed`. At base it prints 127 checks. This diff adds 8: two pushes, double, single, prose untouched, null control, no-heading refusal, and head_note's own arms.
- `python3 tools/pr/head_note.py --self-test`: `head_note self-test: 6 checks, 0 failed`. The app_push self-test runs it, so CI's `instrument-self-tests` runs it too.
- `python3 dev/audit/harnesses/r10_recarry_head.py <tree>`, run on a `git archive origin/main tools/audit/seat tools/pr tools/policy` export (base) and on this head:
  - Base: `writers: 6`, every row `plain=named quoted=named fenced=unnamed crlf=named`.
  - Head: `writers: 6`, every row `plain=named quoted=named fenced=named crlf=named`.
  - The seat writers' `'## Head\n\n'` key happened to skip #2400's backticked quote but not a fenced example. `crlf` is normalised by the writers' text-mode read, and reads named at both ends.
- **Class seams.** The rule is a writer that locates `## Head` by substring:

      git grep -nE "(index|find|rfind|split|partition|replace)\((s, *)?['\"]## Head|s\.index\('\\\\n', s\.index\('## Head" <ref> -- tools tests .claude .github ':!tools/audit/round*'

  - Base: 7 lines, `app_push.sh:344` plus 6 in `open_pr.sh` (39, 56), `update_pr.sh` (24) and `handoff_push.sh` (79, 98, 114). All are closed in this diff.
  - Head: 0 lines, rc 1.
- **Other `## Head` readers and writers** that the broader `git grep -nE "## Head" -- '*.sh' '*.py' '*.mjs'` returns:
  - `push.sh` `write_head`/`head_section_sha`/`head_section_names` match the heading line with awk `^##[[:space:]]+Head[[:space:]]*$`. They are already guarded.
  - `record_row.py` `sections()` reads only the headings its own `pr_body` emits. It is already guarded, as its docstring says.
  - `policy_lint.mjs` `sections()` is the canonical reader.
  - The rest are prose, messages or self-test fixtures.
- `node tools/policy/agreement.mjs` prints `divergent=0 unregistered=0 dead=0`. Its 3 `refused` pairs are the documented missing `--py-json` input. No grammar is written twice, because `head_note.py` uses string operations.
- `python3 tests/closure.py select --diff 5a41a5669`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, over 8 changed files, and `scope.run` names `tests/entities.py`. That script is selected by the `tests/closures.json` entry below. `tools/pr/`, `tools/audit/` and `dev/audit/` are INERT, so no new file is unclassified.
- `python3 tools/pr/ci_predict.py --apply-inert` printed `APPLIED inert_reads tests/harness_headers.py: dev/audit/harnesses/r10_recarry_head.py` and then `CI PREDICT: no closures or fast red predicted against 5a41a56696c6`. The new harness is read by `harness_headers.py`'s scan, and `prepr` refused the handoff until this entry was committed (`4b2f770e`).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`, the script `scope.run` names, prints `1 of 2347 ENTITY CHECKS FAILED` at this head **and at base `5a41a5669`**, on the same check: `graders-head-copy's delivery_status step is red only when ...`, with every stubbed case reading 0. This box produces an identical case map at both ends, and the diff touches neither `tests.yml` nor `tests/delivery_status.py`, so this failure is not this diff's (see Friction).
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `run_always` lines:
  - `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`.
  - `tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`.
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`, at base and at head. At `c45946b7` it printed `1 of 109 HARNESS HEADER CHECKS FAILED` (`FAIL depth seams: dev/audit/harnesses/r10_recarry_head.py:44`, a fixed-depth `dirname` chain). `38284b8c` replaced the chain with the canonical `repo_root` walk from `tools/audit/repo_root.py`.
  - `tests/layout.py`: `layout self-test: ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- **Overlap with #2400** (open, in the train): `git merge-tree --write-tree HEAD origin/fix/r10-bus-orphans-force` reports `CONFLICT (content)` in `tools/audit/seat/handoff_push.sh` and `tools/audit/seat/update_pr.sh`. #2400 rewrites the heredoc lines on either side of the `i=s.index(...)` line this diff removes. The resolution is mechanical: keep #2400's argv and note text, then apply `prefix(s, ...)`.

## Red checks

none. No check has run on this branch. #2400's red `pr-contract` at edc4484 and fd0f5d9 is this defect's trigger (`defect-root-cause.md`, second trigger), and it is answered here:
- **The cheaper detector** is the new `app_push.sh --self-test` double-recarry arm. It runs offline in `instrument-self-tests` on every pull request, and its standing cost is about 2 s of that job: two stubbed recarries and four `policy_lint --pr-body` reads.
- **Process state (c).** The recarry self-test existed and was followed, but its one body fixture had `## Head` as its first line. So a substring and a heading search returned the same index, and the fixture could not tell them apart. The analysis itself is `root-cause.md`'s seat. The orchestrator dispatches it if wanted.

## Unpinned sites

Every changed line is under `tools/` or `dev/audit/`, outside the mutation inventory.

- `head_note.py` is pinned by its self-test (M1 to M3) and the app_push arms.
- `app_push.sh`'s call is pinned by the double, single and no-heading arms.
- The six seat-script call sites are pinned by no CI check. Those scripts drive `gh` and `app_push.sh` against GitHub, and their existing `--self-test` covers only `write_row`, which #2400 replaces. `dev/audit/harnesses/r10_recarry_head.py` extracts and runs each heredoc offline. M1 and M2 turn its rows red, and base reads `fenced=unnamed`. It is a re-runnable harness, not a gate. A CI pin would mean wiring the harness into `instrument-self-tests` (`governance.yml`), which was left out of this group's scope.

## Forward-carry

`tools/audit/seat/INSTRUMENTS.md`, `head_note.py` entry: any new `## Head` note writer goes through it. No later stage's brief changes.

## Friction

- `fixer.md`: cost: two of the seven seams sit on lines #2400 rewrites, which is the merge-tree conflict in Figures. Closing the class here conflicts with a PR already in the train, and leaving those seams open would leave the class open. They were closed, and the merge order is the orchestrator's call: if #2400 lands first, this branch takes a mechanical resolution by merge.
- `fixer.md`: unclear: the brief's hypothesis was "the second recarry did not". The measurement says every recarry did not, and the second was simply the one the train stopped on. Its edc4484 red was not acted on, because main moved under it first.
- `tests/entities.py`: unenforced: the `graders-head-copy` delivery_status stub check fails locally at base `5a41a5669` as well (`cases` all 0). CI's run on this branch will show whether it is this box's alone. It is not this diff's, and it is not worked around here.
