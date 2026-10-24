R10-RECARRY-HEAD: every `## Head` note lands under the heading, not a quote of it. No issue is filed for this group, so the body closes none.

**Cause.** `app_push.sh --recarry` found where to write its note with `s.index('## Head')`, which is the first substring, not the heading. #2400's preamble quotes "`## Head` note" above its `## Head` heading, so both recarry notes were written into the prose:

- The live body read at 2026-10-18T16:4xZ has the fd0f5d9 note at line 13, the edc4484 note at line 15, and `## Head` at line 28.
- pr-contract refused **both** recarry heads: runs 39140677514 and 39140677791 at edc4484, and run 39142591987 at fd0f5d9.

So every recarry of a body that quotes `## Head` above the heading misplaces its note, not only the second. The later green run 39145381763 at fd0f5d9 passed only after someone hand-wrote an `update_pr.sh`-style note under the heading.

**Fix.** One owner: `tools/pr/head_note.py`. `prefix(body, note)` finds the `## Head` heading the way `checkPrBody`'s `sections()` reads it: a line outside a code fence made of `##`, whitespace and `Head`. It inserts the note after that heading and its blank lines, so each later note sits above the earlier ones. A body with no heading exits 1 and leaves the file untouched. Callers:

- `app_push.sh --recarry` builds the same two note texts as before and calls the CLI.
- Six heredocs in `open_pr.sh`, `update_pr.sh` and `handoff_push.sh` called `s.index('## Head\n\n')`, the same substring class, which misplaces a note under a fenced `## Head` example. Each now imports `prefix` through `PYTHONPATH="$PRT"`, the script's own `tools/pr`, resolved before any `cd`.

**Merge with main.** Main moved under this group (#2406, #2419, #2421, #2422 reworked the seat tools: `delivery_row.sh`, `pr_args.sh`, `ensure_row`, the extra `$_added`/`$ROW` note argument). The three seat scripts conflicted. Resolution: take main's version of each file whole, then re-apply only this fix on top of it (the `PRT` line and the six `prefix` call sites), so main's newer behaviour is kept unchanged. `app_push.sh`, `head_note.py` and `INSTRUMENTS.md` merged without conflict. The harness `r10_recarry_head.py` passes a fifth argument (`""`) now, because main's `update_pr.sh` and `handoff_push.sh` heredocs read five argv values; before that edit two of the six writers read `crash` for every body.

**Alternatives considered:**

1. Patch only `app_push.sh`'s heredoc to a heading regex. Rejected: six writers would keep a second, weaker grammar, the duplication the agreement lane refuses.
2. Write the note through `push.sh`'s `write_head`. Rejected: it rewrites the section's SHA line, while these writers prefix a record and keep the earlier text, and it refuses a fenced section.
3. Have the train re-read the body after each recarry and refuse a misplaced note. Rejected: it detects the defect one CI cycle late instead of removing it.

## Head

`bef08da499276ead55f0f8457479f116fa730e85`, the merge of origin/main `768bfc0c3` into the previous authored head `4b2f770e0` (the one conflict resolution is described under Merge with main). It is a descendant of both, and origin/main's tip is its merge-base (read 2026-10-19T06:55Z). Every figure below was taken at this head unless marked base. The mutation proofs were re-taken at this head.

## Mutation proof

Each mutant was applied to `tools/pr/head_note.py` at this head, then `bash tools/pr/app_push.sh --self-test`, `python3 tools/pr/head_note.py --self-test` and `python3 dev/audit/harnesses/r10_recarry_head.py .` were run, and the file was restored with `git checkout`:

- **M1: the heading predicate becomes a substring** (the `elif` condition becomes `"## Head" in line`): app_push prints `135 checks, 4 failed`; head_note `6 checks, 5 failed`; the harness prints 6 rows containing `unnamed` (`quoted=unnamed fenced=unnamed`).
- **M2: fence tracking removed** (`fence = not fence` becomes `pass`): app_push `135 checks, 1 failed`; head_note `6 checks, 1 failed`; the harness prints 6 rows with `fenced=unnamed`.
- **M3: the note goes before the heading line** (`return min(nxt, len(body))` becomes `return pos`): app_push `135 checks, 4 failed`; head_note `6 checks, 5 failed`; 6 rows `unnamed`.
- **The base writers.** The harness run on a `git archive origin/main` export (the seat scripts as main has them) prints, for all six writers, `plain=named quoted=named fenced=unnamed crlf=named`. This is the failing-first control: at base the fenced body is misplaced, at head it is not.

## Null control

- **A single recarry of a body with no prose `## Head`** reads `0namednamed` at base and at head (the arm is in `app_push.sh --self-test`). The section names both the new head and the body's own, so the arms fail on the misplacement and not on the stub machinery.
- **The arms read pr-contract's own reader.** `policy_lint.mjs --pr-body --head <sha>` is grepped for "`## Head` does not name", and the harness refuses a reader run that prints no `PR-BODY:` line.
- **Harness controls.** The `plain` and `crlf` bodies read `named` for all six writers at both base and head.

## Figures

- `bash tools/pr/app_push.sh --self-test`: `app_push self-test: 135 checks, 0 failed`.
- `python3 tools/pr/head_note.py --self-test`: `head_note self-test: 6 checks, 0 failed`. The app_push self-test runs it, so CI's `instrument-self-tests` does too.
- `python3 dev/audit/harnesses/r10_recarry_head.py <tree>`:
  - Base (`git archive origin/main`): `writers: 6`, every row `plain=named quoted=named fenced=unnamed crlf=named`.
  - Head: `writers: 6`, every row `plain=named quoted=named fenced=named crlf=named`.
  - The seat writers' `'## Head\n\n'` key skips a backticked quote but not a fenced example. `crlf` is normalised by the writers' text-mode read and reads named at both ends.
- **Class seams.** The rule is a writer that locates `## Head` by substring:

      git grep -nE "(index|find|rfind|split|partition|replace)\((s, *)?['\"]## Head|s\.index\('\\\\n', s\.index\('## Head" <ref> -- tools tests .claude .github ':!tools/audit/round*'

  - Base (origin/main): 7 lines, `app_push.sh:344`, `open_pr.sh` (39, 52), `update_pr.sh:53`, `handoff_push.sh` (69, 89, 105).
  - Head: 2 lines, both inside `tools/pr/head_note.py` and neither a locator: line 11 is the docstring quoting the old defective call, and line 61 is the self-test splitting a fixture string. No writer locates the heading by substring.
- `node tools/policy/agreement.mjs`: `divergent=0 unregistered=0 dead=0 refused=4`. The 4 `refused` pairs are the documented missing `--py-json` input (`merge-subject-pr`, `dead-member-liveness`, `governance-workflow-jobs`, `budget-raise`), the same at main. `head_note.py` uses string operations, so no grammar is written twice.
- `python3 tests/closure.py select --diff origin/main`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures or fast red predicted against 768bfc0c341d`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries`.
- `python3 tests/layout.py`: `layout self-test: ok`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`.
- `tests/harness_headers.py` was started and stopped locally: it walks the whole harness corpus serially and one harness there ran for minutes. Not claimed here; CI's check-run is the authority. This diff adds one harness, whose header was already conformant at the previous head (`ALL 109 HARNESS HEADER CHECKS PASSED` there, after the `repo_root` walk replaced a fixed-depth chain).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` was not re-run: the scoped gate names it only through the `closures.json` entry, and the previous head's one red there (`graders-head-copy`, a stub check) failed at base alike and is not this diff's.

## Red checks

none. No check has run on this head.

## Unpinned sites

Every changed line is under `tools/` or `dev/audit/`, outside the mutation inventory.

- `head_note.py` is pinned by its self-test (M1 to M3) and the app_push arms.
- `app_push.sh`'s call is pinned by the double, single and no-heading arms.
- The six seat-script call sites are pinned by no CI check: those scripts drive `gh` and `app_push.sh` against GitHub. `dev/audit/harnesses/r10_recarry_head.py` extracts and runs each heredoc offline. M1 and M2 turn its rows red, and base reads `fenced=unnamed`. It is a re-runnable harness, not a gate; wiring it into `instrument-self-tests` was left out of this group's scope.

## Forward-carry

none

## Friction

- `fixer.md`: cost: the previous head conflicted with main in three seat scripts that four merged PRs rewrote around the very lines this fix touched. Re-applying the fix on main's whole file was mechanical, but it cost a full re-take of this body, and the harness needed a fifth argument to keep driving the new writers. Carry: dismissed: a one-off conflict from four PRs merging around the same lines; this group's merge resolved it and no rule or wording change would have prevented it.
- `tests/harness_headers.py`: cost: it runs the whole harness corpus serially and takes many minutes on this box, so a local run is not a practical gate here. Carry: dismissed: CI runs this check on every pull request and is the authority; the box's slowness is local cost, and no tool or wording change follows.
