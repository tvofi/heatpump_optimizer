HOTFIX R10-HOTFIX-TICK-BASH32. Since PR 3520 merged, `tools/audit/seat/tick_loop.sh` does not parse under macOS `/bin/bash` 3.2.57, the shell the production tick loop runs on. Its self-test's fail-closed rows put a `case` with unparenthesised patterns (`func)`, `bashenv)`, `none)`) inside a `$( ... )` command substitution. Bash 3.2 finds a substitution's end by counting parentheses, so the first pattern's `)` closes it early. The running loop's freshness check, the line carrying the `# mut:syntax` marker, runs `bash -n` on origin/main's copy, so every pass printed TICK-STALE and skipped the relay and sweep arms. For about an hour no handoff update reached any pull request. CI runs bash 5, which parses the script, so no check saw it.

The fix gives each of the three patterns its leading `(` (`(func) ...;;`). The self-test's `# mut:` markers and rows are unchanged.

The barrier is `tools/audit/seat/bare_array.py`, which already refused one bash-3.2-only failure (a bare `"${name[@]}"`) across every tracked `tools/**/*.sh`. It gains a second rule. Inside a `$( )`, `<( )` or `>( )` substitution, quoted or not, a `case` pattern without its leading `(` is refused. The output is the same `path:line: text`, through the same `--check [--ref]` and `--self-test` arms. Unquoted, such a site fails `bash -n` on 3.2. Inside double quotes `bash -n` passes and the substitution dies at run time. The rule catches both. There is no opt-out marker, because 3.2 never parses such a site. A small scanner tracks comments, quotes, `${ }`, backquotes, here-documents and `case` state. A `case` in a plain `( )` subshell, in backquotes or at top level is not refused, because 3.2 parses those. On a clean tree `--check` now prints nothing; it used to print an empty line. `tools/audit/seat/instruments/bare_array.py.md` and the `tools/audit/seat/INSTRUMENTS.md` index line describe both rules. The index line is 8 characters shorter than before.

`bare_array.py --check` over the whole tree after the fix found nothing else. At the base it finds exactly the three tick_loop.sh lines. A wider run of `/bin/bash -n` over every tracked `*.sh` in the repository found tick_loop.sh as the only failure.

## Head

e23b5abcdc655c3ba81f3c6a9ad45f09036c8023, one commit on main 154dbb4c61652135381ce66646d23f7109d1c142. `git merge-tree --write-tree origin/main HEAD` prints one tree.

- Failing first, at the base under `/bin/bash` 3.2.57: `/bin/bash -n tools/audit/seat/tick_loop.sh` gives `line 466: syntax error near unexpected token ';;'` at the `func) . "$t/execfn"; ...` line, rc 2.
- At the head: rc 0, no output.
- `/bin/bash tools/audit/seat/tick_loop.sh --self-test` at the head under 3.2.57: `tick_loop self-test: 41 checks, 0 failed`, rc 0.
- Bash 5: none on this host (`command -v bash` is `/bin/bash`; no Homebrew). CI's `governance / instrument-self-tests` runs the same self-test under bash 5.

## Mutation proof

The tick_loop.sh fix is its own mutant. Reverting the three `(` restores the base file byte for byte, and `/bin/bash -n` fails as quoted under Head. `python3 -I tools/audit/seat/bare_array.py --check --ref 154dbb4c61652135381ce66646d23f7109d1c142` refuses those three lines (rc 1):

```
tools/audit/seat/tick_loop.sh:466: func) . "$t/execfn"; export -f exec; "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
tools/audit/seat/tick_loop.sh:467: bashenv) BASH_ENV=$t/execfn "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
tools/audit/seat/tick_loop.sh:468: none) "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
```

`python3 tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --path tools/audit/seat/bare_array.py --cmd 'python3 tools/audit/seat/bare_array.py --self-test'` generated 174 mutants over the added lines of bare_array.py, including `main()`'s `--check`, `--ref` and usage arms. The self-test builds its scratch repository with `tests/throwaway_git.py`'s `throwaway_git_init`, and its word regex is `\w+` so that it does not duplicate another file's identifier grammar (the agreement lane).

Result: rc 1 with 39 SURVIVED lines. The other 135 were killed or skipped as non-compiling; the driver prints only survivors. Every survivor is triaged below.

Two earlier runs drove the self-test's growth. The first left 53 survivors, the second 22. Their survivors went one of two ways:

- Some were killed by a new row: an escaped quote and an empty quote in a led pattern, a leading newline, a comment at the text's start, `${#a}`, `$((1)))` closing, `;;&` consumed whole, a here-document whose first line is its delimiter, `<<-` against `<<`, and `esac` ending a body without `;;`.
- Others were removed as equivalent code. Three statements re-read the keyword or character they had just consumed. Modulo-based end-of-line arithmetic became regexes (`EOL`, `SQUOTE`, `PATTERN`). The arithmetic state was dropped: `$((` pairs as a substitution plus a paren.

The second run also found a real gap. A `case` right after a backquote was not read as a keyword (`` ` `` was missing from the command-position set). It is fixed, and a row pins it.

Triaged survivors, each with its reason:
- `COMMAND.search(text, max(1, i - 9), i)` (window lower bound 0 to 1). It differs only for a `case` at the text's first byte. That case is at top level, outside every substitution, so it can produce no hit. Its patterns at top level move no state that a later line reads. Equivalent for any script that parses.
- `CALL_DEL` of a `cs(...)` or `st(...)` call in `self_test()`, including the one inside the `cs` helper and the four CLI rows. Each deletes an assertion of the test itself, not a predicate of the instrument. Every predicate those assertions pin has its own mutants, and they are killed.
- `check=True` to `check=False` on the scratch repository's `git add` and `git commit`. This is equivalent while git succeeds. If git fails, the CLI rows that follow fail on the missing commit.
- `sys.path.insert(0, ...)` to `insert(1, ...)` for the `tests/` directory. Equivalent: no other path entry holds a module named `throwaway_git`.
- `STMT_DEL` of the write of `tools/b.txt` in the scratch repository. It is a null fixture: a non-`.sh` file holding a refused line that `--check` must not print. Deleting it leaves every assertion true. It pins `scan()`'s `.sh` filter, which predates this diff.
- The 34 `CALL_DEL` and `STMT_DEL` survivors on `self_test()` lines are the assertion deletions above.

## Null control

- The unmodified tree's `bare_array.py --self-test`: `bare_array self-test: ok`.
- The rule's own nulls, each a self-test row:
  - tick_loop.sh's shape with every pattern led by `(`
  - a case at top level, in a plain subshell, and in backquotes inside `$( )`
  - a case in a `<( )` with led patterns
  - `case` as an argument (`local rt case`), as a variable (`case=$(...)`) and inside a word (`mycase`)
  - comments, quoted text and here-document bodies holding pattern-shaped text
- Against the shell itself: two scratch harnesses compare each self-test fixture, and 28 hand-written snippets, with `/bin/bash -n` under 3.2.57. All 28 snippets agree. Among the fixtures, every refused shape fails under 3.2 and every passing one parses. The only exceptions are three shapes that 3.2 accepts at `bash -n` and kills at run time: a `$( )` inside double quotes, a `$( )` inside backquotes, and a `$( )` inside backquotes followed by a backquoted case. For the first two the run-time death was shown: `x="$(case a in a) :;; esac)"` prints `syntax error near unexpected token 'newline'` from the substitution, and the backquoted one prints `syntax error near unexpected token ';;'`.
- A balance harness runs the scanner over all 109 tracked `*.sh` files (515 `case` words). Every file ends with an empty context stack and no hit.

## Figures

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

- `python3 -I tools/audit/seat/bare_array.py --check --ref 154dbb4c61652135381ce66646d23f7109d1c142`: 3 refused lines, all in tick_loop.sh.
- `python3 -I tools/audit/seat/bare_array.py --check`: 0 lines, rc 0.
- `node tools/policy/policy_lint.mjs --budgets`: rc 0. The aggregates are flat: always-loaded ~3605, corpus ~68707, role fixer ~6280.

## Red checks

The defect reached main through a reviewed pull request, PR 3520. Every gate that parses `tools/audit/seat/tick_loop.sh` runs bash 5, and the production host runs bash 3.2. The same `tick_loop.sh --self-test` that CI ran green does not even parse on the host. Under `defect-root-cause.md`, the process state is **a detector existed for the class, but narrower than the class**. `bare_array.py` was built as the static refuser of bash-3.2-only failures in tracked `tools/**/*.sh` (triage P303), but it knew only one: the empty-array expansion under `set -u`. A run-time test on CI cannot see either failure, so only a static rule can stand in for the host's shell.

The countermeasure is the second rule built here. It runs in the existing `governance / instrument-self-tests` step "Refuse a bare array expansion in a set -u script", scoped by that step's existing condition. It refuses this PR's base (rc 1, the three lines quoted above) and passes its head. Measured standing cost on this host: `--check` grows from 0.12 s to 0.42 s and `--self-test` from 0.05 s to 0.49 s. That is about 0.7 s per run of the step.

The rule keys on case patterns only, as the instrument's docstring states. An unbalanced `)` inside a here-document, or inside `${...}`, within a substitution also fails 3.2's paren counting, but has no pattern to key on. No tracked script has one: at the head, `/bin/bash -n` passes on all 109 tracked `*.sh`.

## Forward-carry

none

## Friction

none
