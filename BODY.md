## Re-cut note

Round 5 of #3049, a minimal re-cut (fixer.md, "Past three rounds, re-cut rather than repair"). The round-4 block: the shim split the caller's `ps -o args=` line on spaces, and a value-taking option (python `-W`/`-X`) skipped exactly one word as its value, so a value that is one argv word containing a space was only partly skipped (`python3 -X "importtime LEAKVAL" c.py` logged `python3 LEAKVAL`). The header, the instrument page and the old body claimed more than the code did. Nothing outside that block changed: two commits touch only the parent-field rule of the shim, its arms in `gh_calls.py` and the two texts that state it.

Why: P284, the shared token's core bucket was spent twice with no host log naming the caller. `tools/audit/seat/shims/seat-gh`, installed as `gh` by `seat_venv.sh --install-shims`, appends `<utc> <ppid> <parent, 80 chars> <subcommand> <api path or verb>` to `$HPO_STATE_DIR/gh-calls.log` (directory 0700, log 0600) and execs the first real gh past itself; `tools/audit/seat/gh_calls.py` reads it and self-tests the shim.

The fix: a value-taking letter (python `-W`/`-X`, shell `-o`/`-O`) now ends the parent field unlogged, its value never read, instead of skipping its value. Cost: a script after such an option is not named (`python3 -W error c.py` logs `python3`). The field is otherwise as before: argv[0]'s basename plus at most one more word; a no-value letter is passed over; `c`/`e`/`s` log the option up to that letter and end the field; `--eval/--print/--command` log the name only; any other letter or long option ends it unlogged; `-m <module>` and the first non-option word are logged. Cleaned to `[A-Za-z0-9_./: -]`, cut to 80. Stated residual, by design: argv[0] and the script path are logged as given (`sh ./GH_TOKEN=abcLEAKVAL/script` logs `sh ./GH_TOKEN?abcLEAKVAL/script`; a `bashLEAKVAL` argv[0] symlink logs `bashLEAKVAL`), and `ps` joins argv with spaces, so a script path containing a space is cut at it. The shim header and `instruments/shims_seat-gh.md` state exactly this.

## Head

`2f97d5701e0ae1e189dfe919dd6d5d08a0189202` (code and handoff head), measured on a root host. Branched from PR head `50694d12d3d488bf96b49b0cf44b3bb0eb6a6fce`; origin/main is `e4c9e2016a455d787d3a7604ef88c803c3ba5c70` and `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict), so main was not merged. `tools/pr/prepr.sh` was run at this head with main unmoved since.

## Mutation proof

Failing test first: commit one adds the exact-field arms `python3 -X 'a LEAKVAL' caller.py` and `python3 -W "ignore LEAKVAL" caller.py` (field must be `python3`), moves the other value-letter arms to the new expectation, and adds the mutant arm; against the previous shim: `gh_calls self-test: 84 checks, 8 failed`. Commit two (the shim) makes it `84 checks, 0 failed`. The new `fmutant` arm "a value-taking letter skips one word as its value, not ending the field" restores the old skip in the shim text and requires `python3 -X 'a LEAKVAL' caller.py` to change: `ok mutant killed`. The nine mutants of the previous round and the four older ones are unchanged and read killed.

## Null control

The field is not cut to nothing: through the real `ps`, `python3 -I W/caller.py --body LEAKVAL` logs `python3 W/caller.py` and `python3 -m caller_mod` for `-m`; through the fake `ps`, `python3 -I caller.py --body LEAKVAL` logs `python3 caller.py` (self-test arms, unchanged). The unfixed shim logs `python3 LEAKVAL` for the new arms, which is the 8 FAIL lines above.

## Figures

- `python3 tools/audit/seat/gh_calls.py --self-test`: `84 checks, 0 failed` (rule: every `ok`/`FAIL` line; one arm self-skips as root).
- `env -u BASH_ENV bash tools/audit/seat/seat_venv.sh --self-test`: `21 checks, 0 failed`.
- Finder's harness at both ends: the drivers live in the review evidence ref and not in the tree, exported with `git show origin/verdict/3049:evidence/finder-probe.sh`, the same for `finder-probe2.sh` and the reviewer's `probe3.sh`, each run against the shim exported from 50694d12 and from this head under `env -u BASH_ENV` (count rule: lines starting LEAK). Old head: probe 2, probe2 0, probe3 2 (the two spaced values). This head: probe 2, probe2 0, probe3 0. The two left in probe are exactly the disclosed residual above. Each file has one NOLINE (a bash --command= and a node --print= shape that never call gh); probe3 has 4 NOLINE at both ends.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2497 ENTITY CHECKS PASSED`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
- Claim files, `VERSION`, `RELEASE_NOTES.md` and the manifest: untouched by this pass.

## Red checks

- `governance / instrument-self-tests`: red on main itself (the uutils failure), fixed by #3086; this branch's `gh_calls.py` and `seat_venv.sh` self-tests pass above, and the PR head 50694d12 read GREEN in `merge_train.py classify`. No cheaper detector exists for a red on main before its fix lands; the standing cost is nil here.
- `CodeQL` and open `code-scanning alert 46 (py/overly-permissive-file)`: at this head no check has run yet (the head is not pushed to the PR), and `prepr.sh` reports `CodeQL` red from the branch's existing alert. This seat cannot read code-scanning alerts (no gh REST, no MCP code-scanning tool). At the PR head 50694d12, `merge_train.py classify` read GREEN, 53 check-runs, none failed, `codeql / Analyze (python)` success. The alert concerns the self-test setting two test logs to `0o600 | 0o044` to pin that an existing 0644 log is made 0600; the logs live in a private `TemporaryDirectory`, and the mode is the arm's input. No cheaper detector exists for a mode that is the test's deliberate input; this pass does not touch those lines.

## Forward-carry

none

## Friction

none
