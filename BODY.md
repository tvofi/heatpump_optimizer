Group R11-HOTFIX-CORPUS-MIRROR-PY311 (owner item, DX0 setup). `tools/audit/seat/corpus_mirror.py` decided a zip member's dir-ness with `zipfile.ZipInfo.is_dir()`. CPython 3.11.5's body is `self.filename[-1] == '/'`, which raises IndexError for an empty member name (later 3.11 patches and 3.12+ guard it), so on a 3.11.5 seat `--self-test`'s one-byte fuzz check failed with `raised ['IndexError']`: an archive's shape reached the caller as a traceback, decided by the interpreter's zipfile.

The fix reads dir-ness from the name alone: one helper, `names_directory(name)` (`name.endswith("/")`), at all three sites in `archive_refusal` and `safe_extract`. An empty name is no directory, so its target equals the archive's directory and it is refused by the existing rule "a member's path is the archive's directory".

Alternatives: (a) catch IndexError around `is_dir()` — keeps the interpreter deciding a rule and adds a second boundary beside `read_archive`; lost. (b) a separate "empty name" rule — the existing rule already states the property (the path is the directory itself); a new rule would duplicate it; lost.

The new self-test case builds an archive whose member is `zipfile.ZipInfo("")` and runs `safe_extract` with `ZipInfo.is_dir` replaced by 3.11.5's body for that call only, so it reads the defect on every interpreter, not only 3.11.5.

Class: the rule "`.is_dir()` in a tracked `*.py` file that imports zipfile" (`for f in $(git grep -lE "import zipfile|from zipfile" -- '*.py'); do git grep -n "\.is_dir()" -- "$f"; done`) returns three seams at the base, all in this file's `archive_refusal`/`safe_extract` — closed in this diff — and, outside them, only `pathlib.Path.is_dir` calls (`tests/entities.py`, two; this file's self-test, one), which read no zip member: residue by category "a pathlib call on a host path".

## Head

`b25ced9bddf9ca8970c9e92f85c2a50b43f5a311`, measured against `origin/main` at `8ef450936a1786abf4bb9610dc3336da4e77e8de`, 2026-11-22T15:57Z.

## Mutation proof

1. Fix removed: commit `2363d587ca` is the new check over the unfixed code. `python3 tools/audit/seat/corpus_mirror.py --self-test --no-mutants` there prints `FAIL archives: a member with an empty name is refused whole as the directory itself, read from the name under any interpreter's ZipInfo.is_dir; got ('RAISED IndexError', None)` under python3.14, /usr/bin/python3.11 (3.11.18) and /usr/bin/python3.12.
2. In-tree mutants (the self-test's `MUTANTS`, one per changed predicate), all killed by `python3 tools/audit/seat/corpus_mirror.py --self-test` at the head:
   - `dir-ness from the name` (helper body back to `zipfile.ZipInfo(name).is_dir()`) — killed by `a member with an empty name`;
   - `dir entry is a parent` — killed by `a member that is the directory itself`;
   - `dir entry not written` — killed by `archives null: nested files` (that null case now reports a raise as its own FAIL line instead of a traceback naming no case, which the mutant harness could not credit);
   - the existing `directory itself` mutant's needle follows its renamed line, still killed.

## Null control

At the base, the interpreter's own `is_dir` on this host (3.14, already guarded) passes the whole self-test, which is why the defect was invisible off a 3.11.5 seat; the finder's harness with 3.11.5's `is_dir` reads the defect at the base and not at the head (Figures).

## Figures

- Finder's harness (3.11.5 `ZipInfo.is_dir` patched in, then `--self-test --no-mutants`): `python3 -c 'import runpy,sys,zipfile; zipfile.ZipInfo.is_dir=lambda s: s.filename[-1]=="/"; sys.argv=["tools/audit/seat/corpus_mirror.py","--self-test","--no-mutants"]; runpy.run_path(sys.argv[0], run_name="__main__")'` — at base 8ef4509: `FAIL archives: each of N archives one byte away ... raised ['IndexError']` (N is the fuzz corpus the check generates from timestamped seeds; it prints its own count); at the head: `corpus_mirror self-test: ok (without mutants)`.
- Null control: `python3 tools/audit/seat/corpus_mirror.py --self-test --no-mutants` at the base — `ok (without mutants)`.
- At the head under each local interpreter: `/usr/bin/python3.11 tools/audit/seat/corpus_mirror.py --self-test --no-mutants`, same with `/usr/bin/python3.12` and `python3` (3.14) — each `ok (without mutants)`. 3.11.5 itself was not installable on this seat; the patched `is_dir` is its verbatim body.
- `python3 tools/audit/seat/corpus_mirror.py --self-test` at the head — `ok (with mutants)`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` — `MODE: SCOPED -- 0 script(s) run`.
- `python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` — `Architecture score: dS +0.0000 NULL` (a tools/ file outside the scored tree).

## Red checks

none

## Forward-carry

none

## Friction

none
