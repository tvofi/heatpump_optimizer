Part of #201

R10-TOOLS-O1. Two items: the `tools/pr/prepr.sh` self-test label that ran a command, and `d15_restart_gaps.py`, which sat in `tools/audit/seat/` with no entry in `INSTRUMENTS.md`.

**Item 1.** At origin/main (994695e06) line 1738 of `tools/pr/prepr.sh` is `st "$(closure_lane tests/entities.py 1)" record 0 "a `slot` script is recorded here, ..."`. Two defects on the one line. The label is in double quotes, so the backticks ran `slot` as a command substitution: `--self-test` printed `tools/pr/prepr.sh: line 1738: slot: command not found`. And `st` takes `got want label`, so the stray `0` shifted the label: the run printed `ok   0` and the real text was a fourth argument `st` ignores. The fix escapes the backticks and drops the `0`, so the run prints `ok   a `slot` script is recorded here, inside the slot this run holds (#2267)`.

**Class rule.** `dq_backticks` (new, in `prepr.sh`) reports every unescaped backtick inside a double-quoted string, skipping single quotes, comments and quoted heredocs, with `$( )` opening a fresh context. The self-test drives it over a planted line (null control), over a fixture of the four shapes it must not report, and over `tools/pr/*.sh`.

**Item 2: instrument or harness (fixer.md step 18).** Harness, so it moves to `dev/audit/harnesses/`, not into `INSTRUMENTS.md`. Why: its own docstring names it "R10-D15-GRADER harness (#2268 arm b)"; it prints `RESULT ... unit=` lines for one measurement (`restart_gaps`) over one input bundle; it carries a perturbation (`--plant`) with stated expected readings, which is a harness's null control; and it is a grader for `D15.md` M1's rule, not an operator tool for a lane (no merge, push, gate or watch step calls it; `git grep d15_restart_gaps` finds only itself). `INSTRUMENTS.md` says what `harnesses/` holds: re-runnable measurement harnesses. The only edit to the moved file is its usage line. `git grep d15_restart_gaps` returns one hit, the new path in its own docstring. `dev/audit/harnesses/README.md` does not exist at origin/main (removed in 72826387f, "archive finished plans"; `INSTRUMENTS.md` and `.github/CODEOWNERS` still name it), so there is no index to extend. I did not create it: it is an owner-codeowned path and a new policy-adjacent file. Orchestrator: say if the owner wants it recreated.

## Head

502943a632c4bb7b11ff64357d35262857248d82

## Mutation proof

The predicate mutated is the fix itself: restoring the bare backticks on the `slot` label (`sed '/record "a \\`slot/s/\\`/`/g'`), then `dq_backticks tools/pr/*.sh`:

    tools/pr/prepr.sh:1774: st "$(closure_lane tests/entities.py 1)" record "a `slot` script is recorded ...
    check rc=1 (wanted 0)

so the self-test row `no script in tools/pr/ runs a command inside a double-quoted label` goes red. Restored: the same command prints nothing and rc=0. At origin/main the unfixed line is the baseline: `bash tools/pr/prepr.sh --self-test` printed `line 1738: slot: command not found` and `ok   0` (274 passed). The full self-test was not re-run on the mutant (3 min at load 30); the check body is the function run above.

## Null control

`bash tools/pr/prepr.sh --self-test` at origin/main: `grep -n 'slot: command' st-before.txt` returns `135:tools/pr/prepr.sh: line 1738: slot: command not found`, and the row printed is `ok   0`. At this head: `grep -c 'command not found' st-after.txt` is 0, the row prints the intended label, and the run ends `277 passed, 0 failed` (274 + three new rows). The reader's own null control is its planted `bad.sh` line, reported; the `ok.sh` fixture (escaped backtick, single-quoted backtick, comment, quoted heredoc) is not.

## Figures

- Gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (`tests/entities.py`). Changed files (3): `dev/audit/harnesses/d15_restart_gaps.py`, `tests/closures.json`, `tools/pr/prepr.sh`. Rule: mode line, not the count. `tests/closures.json` gains one line: the moved harness in `inert_reads` of `tests/harness_headers.py` (a sorted-list insert; `prepr` step `ci predict` named it as `PREDICT closures INERT READS`, which `closures-autofix` would otherwise push). `python3 tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`.
- Seams of the class, rule `dq_backticks tools/pr/*.sh` (an unescaped backtick inside a double-quoted string, over `tools/pr/*.sh`). At origin/main it returns exactly one seam, `tools/pr/prepr.sh:1738`, which is this diff's line: closed here. At this head it returns nothing.
- The same class through a wider net, `grep -nE '"[^"]*`[^"]*"' tools/pr/*.sh` (a backtick anywhere between two double quotes on one line, comments excluded): about 35 lines at origin/main. Dispositions: every `\`` inside a double-quoted string is escaped, so inert (`app_push.sh` 774, `app_approve.sh` 360 and 941, `preflight.sh` 284, `push.sh` 294/296/410/413/439/450/465/660/675-677/703/715/735/737, `prepr.sh` 286-288/392/441/446/448/914/1339/1580/1601/2657/2700/2701); backticks inside a single-quoted or quoted-heredoc body, so not shell-evaluated (`app_push.sh` 348/350 in `<<'NOTE'`, 780 in `python3 -c '...'`; `app_approve.sh` 469 in `python3 -c '...'`; `prepr.sh` 133 in `<<'AWK'`, 2057 and 2059 in single quotes; `push.sh` 216/223/226 in an awk program in single quotes, 411 in single quotes). The remaining match is `prepr.sh:1738`, closed here. That net is a superset of the reader and returns no seam the reader does not.
- Arity: `st` takes three arguments, so a fourth silently drops the label. Rule: `shlex.split` of every line starting `st` in `tools/pr/*.sh`, count != 4 words. It returns 18 lines; 17 are shlex noise from quotes nested in `"$(grep ... "..." )"` or a `;;` token (read by eye: each has exactly three arguments), and `prepr.sh:1738` is the one real fourth argument, closed here. Not turned into a check: the shlex noise is higher than the one hit it catches and the reader above already covers the failing text.
- Self-test count: `bash tools/pr/prepr.sh --self-test | tail -1` is `277 passed, 0 failed` (was `274 passed, 0 failed` at origin/main).
- Moved harness still runs, at the new path: `dbg_bundle_gen.py --days 1 --out <scratch>` then `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/d15_restart_gaps.py --bundle <bundle.json> --plant 12054 | grep restart_gaps` prints `RESULT restart_gaps=1 unit=count`; unplanted it prints 5 `RESULT` lines.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries`. `python3 tools/audit/seat/moved_paths.py dev/audit/harnesses/d15_restart_gaps.py tools/audit/seat/INSTRUMENTS.md`: one hit, `INSTRUMENTS.md:5` `.claude/rules/ -> dev/governance/rules/`, a prose mention of the generated directory, not a stale path; unrelated to this move. `tests/layout.json` needs no entry: no tracked path retired, and the harness directory is already listed (`tools/audit/harnesses/` -> `dev/audit/harnesses/`).

## Red checks

none

## Unpinned sites

Step 6d lists none that this diff adds beyond the new `dq_backticks` check row; it is a value check (the reader's output against a planted line and a clean tree), not a mutation-killable pin.

## Forward-carry

none

## Friction

none
