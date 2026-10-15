D13-s3-01 (#2227, class N-move-stale-path) found that the D13 brief's standing DORA instrument cannot start. `dev/governance/dimensions/D13.md` step 4 names `dev/audit/rounds/round4/D11/dora_keys.py` as its base.
- R9-RO-8 (`de46d8da9`) moved that file under `dev/audit/rounds/` and left its library `d11lib.py` live under `tools/audit/round4/D11/`.
- `bc0f17ddb` moved the `cfr_exclusions.json` it opens out of `.claude/workflows/`.
- The import and the literal both broke, and no check noticed.

`dev/audit/rca/R10-N-move-stale-path.md` names the cause, process state (c): every move check keys on whether a cited path EXISTS, never on whether the cited program RUNS. It prices countermeasure form (ii) at about 2 s per release against 128 s. Form (ii) is a narrow arm over the programs live text tells a seat to run under a `historical` prefix. The RCA refuses the whole-tree form (i). This pull request ships form (ii) and fixes every live instance the arm finds.

What changes:
- `dev/audit/rounds/round4/D11/dora_keys.py` resolves both moved paths through `tests/layout.py`, the move map's own resolvers, not a hand-patched path.
  - The library: beside the file while it is there, else at the path `layout.json` moved it from (`canon`).
  - The exclusion list: wherever `layout.json` moved it to (`locate`).
  - Its docstring COMMAND line names the file's current path.
- `dev/audit/rounds/round5/D11/seat-b/corpus_churn.py` opens `policy_budgets.json` and `policy_lint.mjs` through `locate`. Both left `.claude/workflows/`. `carry-201.json`'s `remeasure` tells a seat to run this file. It now runs end to end. At the merge base it raised `FileNotFoundError ... .claude/workflows/policy_budgets.json`.
- `tests/entities.py` gains the cited-program arm.
  - Sources: every executable a policy file cites. The policy set is `policy_lint.mjs`'s own `policyFiles()`, never a copy of `POLICY_GLOBS`. Also every program a carry's `remeasure` tells a seat to run, keyed on the command (`python3`/`node`/`bash`/`run <path>`). A citation is followed through the move map (`locate`) and kept when it lands under a `layout.json` `historical` prefix.
  - Both sources are read from the git index, the way `tests/layout.py` reads prose. They are INERT, and a worktree read records them into the closure, the pair `closure.py merge` refuses (#357).
  - Probe: each cited `.py` is loaded in a fresh interpreter the way a seat runs it. That means cwd at the root, its own directory first on `sys.path`, `PYTHONPATH=tests/hastub`, and nothing the gate process imported.
  - Every repository path the program OPENS must resolve. An opened path is a path literal that is an argument of `open`/`Path`/`join`/a subprocess call/an existence test, directly or through a name assigned that literal. A literal that is an argument of `locate`/`canon` is resolved through that call.
  - The check keys on the open, not on every literal it holds, because `codeowners_gap.py` (a carry names it, and CI runs it) holds retired paths as classifier test inputs and never opens them.
  - A cited executable the arm cannot load is refused.
  - The `#1407` pin above it loads `dora_keys.py` in-process, where `governance_cost.py` had already put `d11lib` on `sys.path`. That is why it stayed green while the instrument could not start.
- `tools/policy/policy_lint.mjs` exports `policyFiles` for that arm: one export line and a comment, with no behaviour change.
- `tests/closures.json`: `tests/entities.py` re-recorded with `./tests/derive_closures.sh --single tests/entities.py` (Darwin, a Python lane), so that `prepr.sh`'s `ci predict` raises no `UNDER-SCOPED`. No `inert_reads` entry was edited by hand. `corpus_churn.py` is on `tests/closure.py`'s INERT list (`dev/audit/`), and the arm opens it, so `closure.py merge` refused the INERT-and-recorded pair. It joins `INERT_EXCEPT` by name, on the `web-fix-wave.js` route the list documents (a file a gate script opens is a dependency), beside `dora_cfr.py`. The other cited programs were already outside INERT. Because `tests/closure.py` is a gate file, the scoped gate reads `MODE: FULL` for this diff.

Alternatives considered:
- Move `dora_keys.py` back beside `d11lib.py`, the RCA's other option. Rejected: `tools/audit/round4/` is a `layout.json` retired prefix, and `tests/layout.py` already reports `d11lib.py` and `governance_cost.py` there as "reintroduces moved path". Moving it there would also force a policy edit to `D13.md`'s citation.
- Hand-patch the paths to today's spelling. Rejected: that breaks again on the next move. The resolvers make `layout.json` the one answer to where a file is, which is the guarded shape the RCA's class search found in every live tool.
- Scan every path literal a cited program holds. Rejected: it over-fires on `codeowners_gap.py`'s classifier inputs. See the null control below.
- The whole-tree enumerator as a gate arm (form (i)). Refused, as the RCA's cost test records.

Part of #201.

Closes #2227.

## Head

`0461329ceb9afbe96c44d4e0d553d0b7e67b54d6`, the branch cut from `origin/main` `5603ee319`, with `origin/main` merged at `7cbb59e73` (`78324e4a1`) and at `4e28c97f7` (`694120d5a`), neither with a conflict. Commits, in order:
- `8d5b657e1`: the failing arm.
- `aaaac99d1`: the `dora_keys.py` fix.
- `cdf2194da`: plants the arm's stale literal from `tests/layout.json`'s first retired file entry, never spelled in a live file. `prepr.sh`'s layout guard refused the spelled form.
- `d16ea96e7`: reads policy text from the index (#357, above).
- `75d4f76af`: the first closure re-record.
- `cccf2f932`: the second failing arm. It reads carries' `remeasure` commands and keys literals on what a program opens, and is red on `corpus_churn.py`'s three opened stale paths.
- `a86998d3e`: the `corpus_churn.py` fix.
- `4e28c97f7`: merges `origin/main`.
- `0461329ce`: the `INERT_EXCEPT` entry and the `tests/entities.py` closure re-record.

## Mutation proof

The arm block was driven alone: an `exec` of the `tests/entities.py` block between its `# --- N-move-stale-path (#2227)` and `# --- D11-04 (#1194)` headers, with the module's own `layout` imports and a `Results` stand-in. Each mutation was applied to the committed tree and restored with `git checkout`.
- M1: `corpus_churn.py`'s `policy_budgets.json` read reverted to the bare literal. FAIL `every program live policy or a carry's remeasure tells a seat to run, under a historical prefix, loads and resolves the paths it opens (#2227)`.
- M2: `_sp_literals` keyed on every held literal, not on opens (`opened=False` default). Both arm checks FAIL: `codeowners_gap.py`'s classifier inputs read as stale opens, and the null control below refuses that.
- M3: the carry command reader disabled (`_SP_RUN` matching nothing). Both checks FAIL: the carry floor is unmet, and `codeowners_gap.py` drops out of the cited set the control requires.
- M4: `dora_keys.py`'s library line reverted to `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`. FAIL, `dora_keys.py: does not load -- ModuleNotFoundError: No module named 'd11lib'`.
- M5: `CFR_EXCLUSIONS` reverted to the bare `.claude/workflows/cfr_exclusions.json`. FAIL, `dora_keys.py:118 opens '.claude/workflows/cfr_exclusions.json', which resolves to nothing`. The literal reaches the open only through the name `CFR_EXCLUSIONS`, so this also proves the name tracking.
- Failing test first: at `8d5b657e1` the policy arm failed on both `dora_keys.py` reasons, and the carry extension's commit failed on `corpus_churn.py`'s 68/100/133 opens before its fix.

## Null control

- `dev/audit/rounds/round4/D12/units.py` (cited by `COMMON.md`, the RCA's named null control) loads and resolves at the merge base and at the head.
- `codeowners_gap.py`, cited by `carry-201.json` and run by CI's governance job, holds at least one path literal that resolves to nothing. The check requires more than 0, under `opened=False`. It has no opened faults, and the check requires `[]`. Without the open key the arm would refuse a running program (M2).
- Planted perturbations inside the control check:
  - `open(<retired path>)` appended to `units.py`: refused.
  - `_P = <retired path>; os.path.join('.', _P)`: refused.
  - `open(locate(<retired path>))`: accepted.
  - a held, unopened `(<retired path>,)`: accepted.
  - a nonexistent `no_such_harness.py`: refused.
  - A policy text citing `tests/golden/config_flow.json` yields no citation.
  - A carry text `python3 -I .../units.py; see .../dora_keys.py` yields only the commanded `units.py`.
- Non-vacuity: the checks require at least 20 policy files, at least 1 carry, at least 1 carry-sourced citation and at least 3 cited programs. At the head the arm reads 41 policy files and 8 carries, and cites 5 programs (`cited` lines below).

## Figures

- The arm at the head prints one `cited` line per program, all `runs`:
  - `dora_keys.py`, by `D13.md` and `carry-201.json`;
  - `units.py`, by `COMMON.md`;
  - `corpus_churn.py`, `dora_cfr.py` and `codeowners_gap.py`, by `carry-201.json`.

  Before `origin/main` `694120d5a` retired carries 2232/2236/2238, the same arm also cited and ran their two round-10 catch-up probes.
- `python3 dev/audit/rounds/round5/D11/seat-b/corpus_churn.py`: rc 0 at the head, with `RESULT tag_window ...` lines through `v7.0.0`. At the merge base (a detached worktree at `78324e4a1`) it gives rc 1 with `FileNotFoundError ... .claude/workflows/policy_budgets.json`.
- The finder's harness `dev/audit/rounds/round10/D13/s3/d13_s3.py`, its `dora_instrument_check()` (the M4-instrument metric) driven alone. The network-bound M4/M5 arms were not run. The command was `PYTHONPATH=tests/hastub python3 <driver>` from a detached worktree at `5603ee319` and from this branch.
  - Bare: the base reads `RESULT dora_keys_loads=0` (`ModuleNotFoundError d11lib`) and the head reads `1` (`load_exclusions -> ['record']`).
  - `D13S3_FIX_IMPORT=1`: the base reads `0` (`FileNotFoundError`) and the head reads `1`.
  - The finder's perturbation, adding `D13S3_DORA_EXCL=dev/governance/config/cfr_exclusions.json`, reads `1` at both ends.
- The class enumerator `python3 -I dev/audit/rounds/round10/D14/sweep-N-move-stale-path/enumerate.py .` reads `seams=2872 broken=369` at `78324e4a1` and `seams=2877 broken=368` at the head. `diff` of the sorted outputs gives the whole delta:
  - gone: `dora_keys.py 89 import d11lib` and `dora_keys.py 103 path .claude/workflows/cfr_exclusions.json`. Both are closed in this diff.
  - moved: `dora_keys.py 118` and `corpus_churn.py 74/106/139`, the same literals now as `locate()`'s argument. They are guarded: this is the move-aware-resolver shape the sweep dispositions as guarded, and the enumerator does not read the call.
  - Lines inside `tests/entities.py` whose numbers shifted. Each is the same literal at a new line, not a new seam.
- Seams by the class rule this arm enumerates: every program live policy or a carry command names under a historical prefix. There are 5. `dora_keys.py` and `corpus_churn.py` are closed in this diff. The other 3 already run.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff 694120d5a...` prints `MODE: FULL`, because `tests/closure.py` is a gate file, so CI runs every script. Run here at the head, with the seat venv python 3.14:
  - `tests/entities.py`, by the `--single` recording: `ALL 2320 ENTITY CHECKS PASSED`.
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/closure.py selftest`: rc 0, `ALL 115 closure shrink pins PASSED`.
  - `python3 tests/layout.py --guard`: `GUARD: 0 refusal(s)`.

  Before the `tests/closure.py` line, the same diff scoped to `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, which were those two scripts.
- `prepr.sh` at the head: rc 0, no REFUSE, `ci predict` predicts no closures or fast red.

## Red checks

none

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`, group R10-STALE-PATHS's `carry`: the 35 evidence-only seams under D2 (the RCA's "Needs tvofi" 1) are already carried to R10-BRIEFS-FOLD. This pull request adds nothing new to carry.

## Friction

none

