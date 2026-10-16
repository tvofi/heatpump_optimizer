Scrubs the owner's home path and account name from every tracked text file on `main` (measured at `dec1a2645`, 2026-10-16). Part of #2310 (group R10-REF-PRIVACY-SCRUB).

Rewrite rules, applied in this order and only to the matched span: a `/private/tmp/claude-<uid>/-Users-<name>-.../<session>/scratchpad/` prefix becomes `<scratchpad>/`; an absolute path under the home directory becomes `~/`; any other standalone account name becomes `<owner-home>` (it never fired: zero such spans remained). 128 files, 955 lines changed, every line replaced in place, so line numbers and line counts are unchanged.

Policy files touched: `dev/governance/roles/nudge.md` only, two path spans (a seat-worktree root and a state-mirror root). A path scrub there changes no rule; it is a privacy correction under mandate 6175172275. `CLAUDE.md`, `AGENTS.md`, `.claude/rules` and `.cursor/rules` carry no hit and are untouched. Files that the policy caps measure (`policy_lint.mjs --budgets`) stay under their caps.

## Head

0855dad0fa0a32d35c5178ab27b505d4010ce8b6

## Mutation proof

n/a: no production code or check changes, only text spans in records, logs, harness docstrings and mutation-ledger `reason` strings. The nearest standing detector is the residual search in `## Null control`.

## Null control

The residual search over the tree at the branch head returns zero files (text and binary alike), and the same search at `origin/main` returns 128, so the search can fail:

    U=$(basename "$HOME"); git grep -al -i "$U" origin/main | wc -l     # 128
    git grep -al -i "$U" HEAD | wc -l                                   # 0

## Figures

Rule for every count: files tracked at the ref whose bytes match the account name case-insensitively (`git grep -l`), the name taken at run time as the basename of the home directory. Not written here.

- 128 files at `origin/main` (97 under `dev/`, 31 under `tests/`): `git grep -lI -i "$U" origin/main | sed 's|^origin/main:||' | cut -d/ -f1 | sort | uniq -c`
- Breakdown under `dev/` (sums to 97): `dev/audit/rounds/round10` 57, `dev/audit/rounds/round9` 18, `dev/archive/handoff` 13 (the `r9-f2-solver-4` and `r9-f2-solver-5` evidence logs), `dev/audit/rca` 7, `dev/governance/roles` 1, `dev/programme/rosters` 1: `git grep -lI -i "$U" origin/main -- dev | sed 's|^origin/main:||' | cut -d/ -f1-4 | sort | uniq -c`
- Under `tests/`: 31, all `tests/mutation_ledger/killed_by/**.json`, text in the free `reason` field only (keys `anchor` and `old` untouched): `git grep -lI -i "$U" origin/main -- tests | cut -d/ -f1-3 | sort | uniq -c`
- Skipped, with reason: none. Binary files with a hit: `git grep -al -i "$U" origin/main` minus `git grep -lI -i "$U" origin/main` is empty (0). Hits in `tests/golden/**`, `VERSION`, the manifest, `RELEASE_NOTES.md`: 0 (`git grep -l -i "$U" origin/main -- tests/golden VERSION RELEASE_NOTES.md 'custom_components/*/manifest.json' | wc -l`).
- Diff shape: 955 lines added and 955 deleted, and no file changes its line count: `git diff --numstat origin/main HEAD | awk '$1!=$2' | wc -l` prints 0.
- Rewritten file kinds by extension: 45 `.json` (31 of them ledger files), 32 `.py` (docstring `Command:` lines only; each passes `py_compile`), 24 `.log`, 23 `.md`, 3 `.out`, 1 `.txt`: `git diff --name-only origin/main HEAD | sed 's/.*\.//' | sort | uniq -c`
- sha1 citations: a changed file cited by sha1, git blob id or sha256 (7-char prefixes) anywhere in the tree: 0. No `figure_lint` citation or record needed re-keying. Instrument: a per-file `git grep -n -I <prefix>` over all 128 files' original sha1, blob id and sha256.
- Ledger: `python3 tests/mutation_table.py --normalize` rewrites nothing further and retires 0 keys (`1672 disposition(s), 0 retired key(s)`); `python3 tools/merge/ledger_merge.py --self-test` passes.
- Gate scope (`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`): `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; `scope.run` names `tests/entities.py` (2329 checks passed) and `tests/harness_headers.py` (109 passed). Also `tests/layout.py` passed.
- `python3 tools/audit/seat/tmp_paths.py --check`: 0 refused. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `node tools/policy/policy_lint.mjs`: 0 errors across 41 policy files; `--budgets` rc 0. `node tools/policy/brief_lint.mjs`: TOTAL: 0 error(s) across 47 file(s), rc 0 (full run, including the carry self-test fixtures).

## Red checks

none

## Forward-carry

none

## Friction

none
