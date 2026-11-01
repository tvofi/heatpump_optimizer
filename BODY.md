## Re-cut

Round 4 of #3049, re-cut to the minimal fix for the round-3 block (fixer.md, "Past three rounds, re-cut rather than repair"). The PR adds the gh call-log (P284): `tools/audit/seat/shims/seat-gh`, installed as `gh` by `seat_venv.sh --install-shims`, appends `<utc> <ppid> <parent, 80 chars> <subcommand> <api path or verb>` to `$HPO_STATE_DIR/gh-calls.log` (directory 0700, log 0600), then execs the first real gh past itself; `tools/audit/seat/gh_calls.py` reads it (`--top`, `--coverage`) and self-tests the shim (`--self-test`, wired in governance.yml).

This pass changes only the parent field's rule, its arms and the text that states it. The field is argv[0]'s basename plus, for `sh|bash|zsh|dash|ksh`, `python*|Python|pypy*` or `node|perl|ruby`, at most one more word, read option by option, one letter at a time:
- a known no-value letter is passed over (python `bBdEhiIOqPRSuvVx`, shell `abfhiklmnprtuvxBCEHPT`, node/perl/ruby `w`);
- a known value-taking letter (python `-W`/`-X`, shell `-o`/`-O`) passes over its value, glued or the next word, unlogged;
- `c`, `e` or `s` logs the option up to that letter and ends the field, so attached code is cut off (`-cCODE` logs `-c`, `-BcCODE` logs `-Bc`) and a stdin script's arguments are never read (`bash -s -- --token V` logs `bash -s`);
- `--eval`, `--print`, `--command` (bare or `=CODE`) log the name only and end the field;
- any other letter or long option ends the field unlogged;
- `-m <module>` logs the module; the first non-option word is the script and ends the field.
The result is cleaned (`tr -c 'A-Za-z0-9_./: -' '?'`) and cut to 80 characters.

Stated residual, by design: argv[0] and the script path are the caller's identity and are logged as given, so a value placed in a path is logged too: `sh ./GH_TOKEN=abcLEAKVAL/script` logs `sh ./GH_TOKEN?abcLEAKVAL/script`, and an argv[0] whose basename holds a value (a `bashLEAKVAL` symlink) logs it. The shim's header comment, `instruments/shims_seat-gh.md` and `instruments/gh_calls.py.md` now state the rule and this residual, no stronger.

Carries: none. Nothing outside the round-3 findings was changed; daemon coverage, shim latency and the delivery row are untouched from the previous head.

Commits: the failing arms first (`bfc39a1d8`), then the fix (`8f39a456b`).

## Head

`8f39a456bc466f9dc8f29dfe9d828bc12c15898f`, measured on a root host (uid 0), origin/main `6421fe135d9f5a9e65433a4433f000d2419486bf` (read 2026-11-01T10:06:02Z). No main merged: `git merge-tree --write-tree HEAD origin/main` exits 0 (no conflict), and origin/main did not move between this pass's `tools/pr/prepr.sh` run and the handoff, so no second run was owed.

## Mutation proof

Failing test first: the 22 exact-field arms over a fake `ps` were committed at `bfc39a1d8` and run against the unfixed shim: `gh_calls self-test: 72 checks, 18 failed`. The 18 FAIL lines are every arm below except four that the old rule already met: `python3 -WLEAKVAL caller.py`, the `-I` null control, `sh ./a=b/s.sh` and the 80-character cut. Those four are pinned by the mutants below instead.

With the fix, each field rule has an in-tree mutant arm (`fmutant` in `gh_calls.py`), each replacing production text in the shim and requiring an exact-field arm to change; each check also requires the mutant text to differ from the shim, so none is vacuous:
- code option logged whole, not cut after its letter: killed (`python3 -cCODE`).
- `-s` passed over as a no-value letter: killed (`sh -s LEAKVAL` logs `sh LEAKVAL`).
- unknown option letter passed over: killed (`ruby -r LEAKVAL x.rb`).
- unknown long option passed over: killed (`node --require ./LEAKVAL.js n.js`).
- value-taking letter read as no-value: killed (`python3 -W ignore::LEAKVAL caller.py`).
- `=` allowed by the field's `tr -c` (reviewer's survivor a): killed (`sh ./a=b/s.sh` must log `sh ./a?b/s.sh`).
- the 80-character cut removed (reviewer's survivor b): killed (a 96-character script path must log exactly its first 80 characters).
- `--eval*|--print*|--command*` passed over (reviewer's survivor c): killed (`node --eval=CODE` must log `node --eval`).
- a long code option logged with its attached code: killed (`node --print=LEAKVAL`).
The four existing field mutants (whole argv logged, `-c` not ending the field, `-m` not taking its module, python not followed to its script) were rewritten to the new production text and are killed. Restored: `gh_calls self-test: 81 checks, 0 failed`, 19 `mutant killed` arms.

## Null control

The field is not cut to nothing: through the real `ps`, `PY -I W/caller.py --body LEAKVAL` logs exactly `python3 W/caller.py` and `cd W && PY -m caller --body LEAKVAL` logs `python3 -m caller` (self-test arms, and the finder's probe at this head: `python3 <W>/caller.py` and `python3 -m caller_mod`). Through the fake `ps`, `python3 -I caller.py --body LEAKVAL` logs `python3 caller.py` and `python3 -W error -m caller_mod LEAKVAL` logs `python3 -m caller_mod`. A fixed string or an empty field fails all four. The fake `ps` is itself controlled by the real-`ps` arms, which still read the true parent. Hermetic control: the self-test's planted fake gh makes the old-style-PATH arm red and stays invisible to the hermetic PATH (`control:` and `mutation:` arms ok); this host carries a real gh at `/usr/local/bin/gh`, outside the arm's PATH, and the no-real-gh arm reads ok. Planting a decoy at `/usr/bin/gh` was refused by this seat's sandbox, so the in-test decoy arms are the control here.

## Figures

- Self-test: `env -u BASH_ENV python3 tools/audit/seat/gh_calls.py --self-test` at the head, root host: `81 checks, 0 failed` (rule: every `ok`/`FAIL` line; one arm self-skips as root, `skip unwritable-directory arm`, so a non-root host prints 82). At `bfc39a1d8` (arms, unfixed shim): `72 checks, 18 failed`.
- `env -u BASH_ENV bash tools/audit/seat/seat_venv.sh --self-test`: `21 checks, 0 failed`.
- Finder's harness at both ends: the reviewer's two probe drivers, kept in the review evidence ref and not in the tree (fixer.md step 18: a reviewer's driver stays in evidence), exported with `git show origin/probe/rev-3049-4ca2508c:ev/probe.sh` (sha1 9e7d60c7460a4f5b52003197aa93aa6f16415195) and the same for probe2 (sha1 1d8e6d5fc9831989720d22000bd8cfd2b0e70abb), each run against an exported shim under `env -u BASH_ENV`, perl, ruby and node present; count rule: lines starting `LEAK`.
  - baseline `a7e6a3e5d`: probe.sh 44 LEAK, probe2.sh 9 LEAK.
  - unfixed head `e24bda11a`: 9 and 5 LEAK, the round-3 shapes.
  - this head: 2 and 0 LEAK. The two left are the residual above, both by design: `sh ./GH_TOKEN=abcLEAKVAL/script` and the `bashLEAKVAL` argv[0] symlink.
  - one NOLINE at every end in each file: `bash --command=` (bash rejects it) and `node --print=` (it never reaches gh). Both are shapes that never call gh.
  - the round-2 shapes in probe.sh (25 census flags, 19 out-of-census flags, env-assignment, piped-secret, argv-list) are clean at this head.
- Extra shapes of this seat (27 command lines through a fake `ps`: `-Wd -c`, `-X dev=V -c`, `bash -O x -c`, `sh -ce`, `zsh -c`, `ksh -s`, `perl -w -e`, `node -r V -e`, `node --inspect=V`, `python3 -mV`, `python3 -- V`, `bash +o V`, `pypy3 -cV`, `/usr/bin/env python3 -c V` and others): 0 LEAK. So no new arm was owed.
- Class rule (fixer.md step 8): the enumerating rule is the field's own case table. Each branch is a seam with its disposition:
  - known no-value letter, value-taking letter, code/stdin letter, `--eval/--print/--command`, unknown letter, unknown long option, `-m`, the script word, `=` cleaning, the 80-character cut: each closed here by an exact-field arm and a killed mutant.
  - argv[0] and the script path: the disclosed residual.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` (base `df66556f2`): `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, scope.run = tests/entities.py, tests/harness_headers.py.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2493 ENTITY CHECKS PASSED`, rc 0. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`, rc 0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh <body.md>` at the head against origin/main `6421fe135`: `PRE-PR: ... rc=0`, no refusal. Its CI-predict step: `no closures, fast, governance or instrument red predicted`. No closures skip was passed; the step printed its own `skip closures` line (no full derive off CI).

## Red checks

- none at the PR head `e5da61c2d` (read with the GitHub check-runs API: no concluded failure among 41 runs; `governance / instrument-self-tests`, `tests / closures` and `codeql / Analyze (python)` were still in progress).
- The CodeQL `py/overly-permissive-file` question (alert 46) is still open: this seat cannot read code-scanning alerts (no gh REST, no MCP code-scanning tool). The self-test still sets two test logs to `0o600 | 0o044` to pin that an existing 0644 log is made 0600. Those logs live in a private `TemporaryDirectory` (0700 parent), and the 0644 mode is the arm's input. If CodeQL flags them, the finding is a false positive on test input and no cheaper detector exists. This pass does not touch those lines.

## Forward-carry

none

## Friction

none
