D13-s3-01 (#2227, class N-move-stale-path) found that the D13 brief's standing DORA instrument cannot start. `dev/governance/dimensions/D13.md` step 4 names `dev/audit/rounds/round4/D11/dora_keys.py` as its base. R9-RO-8 (`de46d8da9`) moved that file under `dev/audit/rounds/` and left its library `d11lib.py` live under `tools/audit/round4/D11/`. `bc0f17ddb` moved the `cfr_exclusions.json` it opens out of `.claude/workflows/`. The import and the literal both broke, and no check noticed. R10-RCA `dev/audit/rca/R10-N-move-stale-path.md` names the cause, process state (c): every move check keys on whether a cited path EXISTS, never on whether the cited program RUNS. It prices countermeasure form (ii), a narrow arm over programs live policy cites under a `historical` prefix, at about 2 s per release against 128 s, and it refuses the whole-tree form (i) as dominated. This pull request ships form (ii) and fixes the instance.

What changes:
- `dev/audit/rounds/round4/D11/dora_keys.py` resolves both moved paths through `tests/layout.py`, the move map's own resolvers, rather than a hand-patched path.
  - The library: beside the file while it is there, else at the path `layout.json` moved it from (`canon`).
  - The exclusion list: at wherever `layout.json` moved it to (`locate`).
  - Its docstring COMMAND line names the file's current path.
- `tests/entities.py` gains the cited-program arm.
  - It takes the policy corpus from `policy_lint.mjs`'s own `policyFiles()`, never a copy of `POLICY_GLOBS`.
  - It finds every executable path that text cites under a `layout.json` `historical` prefix.
  - It loads each cited `.py` in a fresh interpreter the way a seat runs it: cwd the root, its directory first on `sys.path`, `PYTHONPATH=tests/hastub`, nothing the gate process imported.
  - It requires every repository-path string literal in its code to resolve. A literal that is the argument of `locate`/`canon` is resolved through that call.
  - It refuses a cited executable it cannot load, rather than reading it as running.
  - The `#1407` pin above it loads the same file in-process, where `governance_cost.py` had already put `d11lib` on `sys.path`. That is why it stayed green while the instrument could not start.
- `tools/policy/policy_lint.mjs` exports `policyFiles` for that arm. That is one export line and a comment, with no behaviour change.

Alternatives considered:
- Move `dora_keys.py` back beside `d11lib.py`, the RCA's other option. Rejected: `tools/audit/round4/` is a `layout.json` retired prefix, and `tests/layout.py` already reports `d11lib.py` and `governance_cost.py` there as "reintroduces moved path". A third file would grow that list, and `D13.md` (policy) would have to change its citation.
- Hand-patch the two paths to their current spellings. Rejected: it fixes this move and breaks on the next. The resolvers make `layout.json` the one source of where a file is, which is the guarded shape the RCA's class search found in every live tool.
- The whole-tree enumerator as a gate arm (form (i)). Refused, as the RCA's cost test records: the 35 evidence-only seams break by design under D2.

Part of #201.

Closes #2227.

## Head

`75d4f76afc11e7c0b5eb3b7f3d58ff64e2ac9981`. The branch was cut from `origin/main` `5603ee319`, and `7cbb59e73` merges `origin/main` `78324e4a1` into it with no conflict. Its commits:
- `8d5b657e1`: the failing arm.
- `aaaac99d1`: the fix.
- `cdf2194da`: plants the arm's stale literal from `tests/layout.json`'s first retired file entry (`.claude/workflows/agreement.mjs` today), so the literal is never spelled in `tests/entities.py`. `prepr.sh`'s layout guard refused the spelled form as a new citation of a retired path.
- `d16ea96e7`: the cited-program arm reads policy text from the index. Policy text is on `tests/closure.py`'s INERT list, so a worktree read recorded it into `entities.py`'s closure, the INERT-and-recorded pair `closure.py merge` refuses (#357). It is now read with `git show :<path>`, as `tests/layout.py` reads prose.
- `75d4f76af`: `tests/closures.json`, with `tests/entities.py` re-recorded by `./tests/derive_closures.sh --single tests/entities.py` (Darwin, a Python lane). The closure gains `dev/audit/rounds/round4/D12/units.py`, the arm's probe argument; its `recorded` seconds move.

## Mutation proof

The arm block was driven alone (`exec` of the `tests/entities.py` block between its `# --- N-move-stale-path (#2227)` and `# --- D11-04 (#1194)` headers, with the module's own `layout` imports and a `Results` stand-in). Each mutation was applied to the committed head and then restored with `git checkout`.
- `dora_keys.py`'s library line reverted to `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`. Result: FAIL `every program live policy cites under a historical prefix loads and resolves the paths it opens (#2227)`, with `dev/audit/rounds/round4/D11/dora_keys.py: does not load -- ModuleNotFoundError: No module named 'd11lib'`.
- `CFR_EXCLUSIONS` reverted to the bare literal `".claude/workflows/cfr_exclusions.json"`. Result: the same check FAILS, with `dora_keys.py:118 opens '.claude/workflows/cfr_exclusions.json', which resolves to nothing`.
- Failing test first: at `8d5b657e1` the same check failed on both reasons at once, the RCA's "red on this tree (two reasons)".
- In every arm, the arm's own control check stays `ok`.

## Null control

- `dev/audit/rounds/round4/D12/units.py`, cited by `COMMON.md`, loads and resolves at the merge base and at the head (`cited ... units.py by dev/governance/roles/COMMON.md: runs`). That is the RCA's named null control.
- Perturbations inside the arm's control check:
  - `units.py` plus a planted bare literal naming a retired file (read from the manifest) is refused.
  - The same literal wrapped in `locate(...)` is accepted.
  - An uncited, nonexistent `no_such_harness.py` is refused.
  - A text citing `tests/golden/config_flow.json` (a historical prefix, not an executable) yields no citation.
- Non-vacuity: the check requires at least 20 policy files and at least 2 cited programs. It reads 41 policy files and 2 cited programs at the head.

## Figures

- The arm at the head prints `cited  dev/audit/rounds/round4/D11/dora_keys.py by dev/governance/dimensions/D13.md: runs` and `cited  dev/audit/rounds/round4/D12/units.py by dev/governance/roles/COMMON.md: runs`.
- The finder's harness `dev/audit/rounds/round10/D13/s3/d13_s3.py`, its `dora_instrument_check()` (the M4-instrument metric) driven alone. The network-bound M4/M5 arms were not run. The command was `PYTHONPATH=tests/hastub python3 <driver>`, from a detached worktree at `5603ee319` and from this branch at the head.
  - Bare: the base prints `RESULT dora_keys_loads=0` (`ModuleNotFoundError d11lib`). The head prints `RESULT dora_keys_loads=1` (`load_exclusions -> ['record']`).
  - `D13S3_FIX_IMPORT=1`: the base prints `0` (`FileNotFoundError`, `CFR_EXCLUSIONS = .claude/workflows/cfr_exclusions.json`). The head prints `1`.
  - `D13S3_FIX_IMPORT=1 D13S3_DORA_EXCL=dev/governance/config/cfr_exclusions.json` (the finder's perturbation): `1` at both ends.
- The class enumerator `python3 -I dev/audit/rounds/round10/D14/sweep-N-move-stale-path/enumerate.py .` prints `seams=2871 broken=369` at the base and `seams=2875 broken=368` at the head. `diff` of the sorted outputs gives the whole delta:
  - gone: `dora_keys.py 89 import d11lib` and `dora_keys.py 103 path .claude/workflows/cfr_exclusions.json`. Both are closed in this diff.
  - added: `dora_keys.py 118 path .claude/workflows/cfr_exclusions.json`. It is guarded: the literal is `locate()`'s argument, the move-aware-resolver shape the sweep dispositions as guarded. The enumerator does not read the call.
  - the other `tests/entities.py` lines only shifted their line numbers.
- Seams the RCA's class rule names, re-run: every executable cited by `policyFiles()` under a `historical` prefix. There are 2. `dora_keys.py` is closed in this diff. `units.py` already runs.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `prepr.sh` `ci predict` at the head: `CI PREDICT: no closures or fast red predicted against 78324e4a1acb`.
- Scoped gate: `python3 tests/closure.py select --diff 5603ee319...` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/entities.py`, `tests/harness_headers.py`) against `78324e4a1`. The recorded run of `tests/entities.py` at the head (the `--single` recording above, seat venv python 3.14) printed `ALL 2320 ENTITY CHECKS PASSED`, and `tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`.

## Red checks

none

## Forward-carry

Carried to the orchestrator for R10-BRIEFS-FOLD, the roster group this group's carry names:
- The disposition of the 35 evidence-only seams under D2 (the RCA's "Needs tvofi" 1).
- A finding outside this arm's scope. `dev/programme/carries/carry-201.json` is a live carry, not in `POLICY_GLOBS`. Its `remeasure` lines tell a later seat to run `tools/audit/round5/D11/seat-b/corpus_churn.py`, `tools/audit/round4/D11/dora_keys.py`, `tools/audit/round5/D13/seat-a/dora_cfr.py` and `tools/audit/round6/D11/fix/codeowners_gap.py`. All four are pre-move paths, now under `dev/audit/rounds/`. Driven by this arm's own probe:
  - `corpus_churn.py` is broken: its literals `.claude/workflows/policy_budgets.json` and `.claude/workflows/policy_lint.mjs` resolve to nothing.
  - `dora_cfr.py` runs.
  - `codeowners_gap.py` runs in CI, but its classifier test inputs read as stale literals, so a literal check over carries would over-fire.
  - Widening the arm to carries therefore needs a decision on that key, and the carry's run commands need re-pointing.

## Friction

none
