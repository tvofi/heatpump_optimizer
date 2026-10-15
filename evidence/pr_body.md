D13-s3-01 (#2227, class N-move-stale-path) found that the D13 brief's standing DORA instrument cannot start. `dev/governance/dimensions/D13.md` step 4 names `dev/audit/rounds/round4/D11/dora_keys.py`. R9-RO-8 (`de46d8da9`) moved it under `dev/audit/rounds/` and left its library `d11lib.py` under `tools/audit/round4/D11/`. `bc0f17ddb` moved the `cfr_exclusions.json` it opens out of `.claude/workflows/`.

`dev/audit/rca/R10-N-move-stale-path.md` gives the cause as process state (c): every move check asks whether a cited path EXISTS, never whether the cited program RUNS. It prices countermeasure form (ii) at about 2 s per release against 128 s. Form (ii) is a narrow arm over the programs live text tells a seat to run under a `historical` prefix. The RCA refuses the whole-tree form (i). This pull request ships form (ii) and fixes every live instance the arm finds, in both halves of the class:
- the program half, where a moved dependency breaks a cited program;
- the citation half, where a command spells a moved program's old path.

What changes:
- **`dora_keys.py`** resolves both moved paths through `tests/layout.py`, the move map's own resolvers.
  - The library resolves beside the file while it is there, else at the path `layout.json` moved it from (`canon`).
  - The exclusion list resolves to wherever `layout.json` moved it to (`locate`).
  - The docstring COMMAND line names the file's current path.
- **`corpus_churn.py`** (`dev/audit/rounds/round5/D11/seat-b/`) opens `policy_budgets.json` and `policy_lint.mjs` through `locate`. `carry-201.json` tells a seat to run it.
- **`carry-201.json`**: five `remeasure` commands are re-pointed to where their programs live (`corpus_churn.py`, `dora_keys.py` twice, `dora_cfr.py`, `codeowners_gap.py`). On those same lines, three more retired paths move to their `layout.json` targets, because `tests/layout.py --guard` reads a touched line as a new citation of each retired path on it: `cfr_exclusions.json`, `field_coverage.mjs` and `prepr.sh`. Record fields that recount what was run stay as written.
- **`tests/entities.py`**, the cited-program arm:
  - **Sources.** Every executable a policy file cites, taken from `policy_lint.mjs`'s own `policyFiles()` and never a copy of `POLICY_GLOBS`. Also every program a carry's `remeasure` commands (`python3`/`node`/`bash`/`run <path>`). A citation is followed through `locate` and kept when it lands under a `historical` prefix.
  - **Index reads.** Both sources are INERT, so they are read from the git index, the way `tests/layout.py` reads prose. A worktree read would record them into the closure, the INERT-and-recorded pair `closure.py merge` refuses (#357).
  - **Probe.** A cited `.py` is loaded in a fresh interpreter the way a seat runs it: cwd the root, its own directory first on `sys.path`, `PYTHONPATH=tests/hastub`. Every repository path it OPENS must resolve. A path counts as opened when it is a literal argument of `open`/`Path`/`join`/a subprocess call/an existence test, directly or through a name assigned that literal. A `locate`/`canon` argument is resolved through the call. The key is the open, because `codeowners_gap.py` holds retired paths as classifier test inputs it never opens.
  - **Command spelling.** A carry command must also name its program as written, since a shell does not follow the move map.
  - **Refusal.** A cited executable the arm cannot load is refused.
- **`tools/policy/policy_lint.mjs`** exports `policyFiles`: one export line, no behaviour change.
- **`tests/closure.py`**: `corpus_churn.py` joins `INERT_EXCEPT` by name, beside `dora_cfr.py`, on the list's documented `web-fix-wave.js` route (a file a gate script opens is a dependency). `tests/closure.py` is a gate file, so the scope is `MODE: FULL`.
- **`tests/closures.json`**:
  - `tests/entities.py` was re-recorded with `./tests/derive_closures.sh --single`.
  - Three reads were added by hand from CI's Linux recording (see `## Red checks`). `entities.py` gets `dev/audit/rounds/round4/D12/cells.py` and `d12lib.py`. `harness_headers.py` gets `corpus_churn.py`.
  - `corpus_churn.py` left both `inert_reads` lists, since it is no longer INERT.

Alternatives considered:
- Move `dora_keys.py` back beside `d11lib.py`. Rejected: `tools/audit/round4/` is a retired prefix, where `tests/layout.py` already reports two files as "reintroduces moved path", and the move would force a policy edit to `D13.md`.
- Hand-patch the code paths to today's spelling. Rejected: it breaks again on the next move. The commands in a carry are different: a seat pastes them, so they must be spelled as they are.
- Scan every path literal a cited program holds. Rejected: it over-fires on `codeowners_gap.py`.
- The whole-tree enumerator as a gate arm (form (i)). Refused, by the RCA's cost test.

Part of #201.

Closes #2227.

## Head

`5014df1399aebbffde19178a50ab6fd999d4b379` merges the authored code head `e0e5be6bbe6ff77c0495a8e441547cf341ba2ddc` and then merges origin/main `613b10c51` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`e0e5be6bbe6ff77c0495a8e441547cf341ba2ddc`. Cut from `origin/main` `5603ee319`. `origin/main` merged at `7cbb59e73`, `4e28c97f7`, `414e268f8` and `b03feb40b`; the last is `613b10c51`, the merge base, and none had a conflict. Commits since the review at `fc75984b2` (= `0461329ce` + the row):
- `cf477e3c7`: the closure repair.
- `2f1c30b68`: the stale-command check, failing first.
- `7bd01490e`: carry-201's five commands.
- `e0e5be6bb`: the touched lines' other retired paths, and one comment reworded off a retired prefix.

## Mutation proof

The arm block was driven alone: an `exec` of the `tests/entities.py` block between `# --- N-move-stale-path (#2227)` and `# --- D11-04 (#1194)`, with the module's `layout` imports and a `Results` stand-in. Each mutation was applied to the committed tree and restored with `git checkout`.
- M1, `corpus_churn.py`'s `policy_budgets.json` read reverted to the bare literal: FAIL `every program live policy or a carry's remeasure tells a seat to run, under a historical prefix, loads and resolves the paths it opens (#2227)`.
- M2, `_sp_literals` keyed on every held literal: both arm checks FAIL.
- M3, the carry command reader disabled: both checks FAIL.
- M4, `dora_keys.py`'s library line reverted to the sibling `sys.path.insert`: FAIL, `does not load -- ModuleNotFoundError: No module named 'd11lib'`.
- M5, `CFR_EXCLUSIONS` reverted to the bare literal: FAIL, `dora_keys.py:118 opens '.claude/workflows/cfr_exclusions.json'`. The open is reached only through the name.
- Failing first:
  - `8d5b657e1` fails on both `dora_keys.py` reasons.
  - `cccf2f932` fails on `corpus_churn.py`'s opens at lines 68, 100 and 133.
  - `2f1c30b68` fails with `commands naming no file` on carry-201's five pre-move spellings. Reverting `7bd01490e` reproduces that failure.

## Null control

- `units.py` (cited by `COMMON.md`) loads and resolves at both ends.
- `codeowners_gap.py` holds more than 0 stale path literals under `opened=False` and has 0 opened faults. The check asserts both.
- Planted:
  - `open(<retired>)` is refused.
  - `_P = <retired>; os.path.join('.', _P)` is refused.
  - `open(locate(<retired>))` is accepted.
  - A held `(<retired>,)` is accepted.
  - A nonexistent harness is refused.
  - `tests/golden/config_flow.json` in policy prose yields no citation.
  - A carry text yields only its commanded program.
  - `python3 <canon(units.py)>` is reported stale, and `python3 <units.py>` is not.
- Floors: at least 20 policy files, 1 carry, 1 carry-sourced citation and 3 cited programs. The head reads 41 policy files and 8 carries, and cites 5 programs, all `runs`:
  - `dora_keys.py` (`D13.md`, carry-201);
  - `units.py` (`COMMON.md`);
  - `corpus_churn.py`, `dora_cfr.py` and `codeowners_gap.py` (carry-201).

## Figures

- `python3 dev/audit/rounds/round5/D11/seat-b/corpus_churn.py`: rc 1 at the merge base `613b10c51` (`FileNotFoundError ... .claude/workflows/policy_budgets.json`), rc 0 at the head.
- The finder's harness `dev/audit/rounds/round10/D13/s3/d13_s3.py`, with its `dora_instrument_check()` driven alone (the network-bound M4/M5 arms not run), via `PYTHONPATH=tests/hastub python3 <driver>` at `613b10c51` and at the head:
  - bare: `RESULT dora_keys_loads=0` at the base, `1` at the head;
  - `D13S3_FIX_IMPORT=1`: `0` at the base, `1` at the head;
  - plus `D13S3_DORA_EXCL=dev/governance/config/cfr_exclusions.json`: `1` at both ends.
- The class enumerator `python3 -I dev/audit/rounds/round10/D14/sweep-N-move-stale-path/enumerate.py .` reads `seams=2875 broken=368` at `613b10c51` and `seams=2881 broken=367` at the head. It does not scan `.json`, so carry-201 is not in it. `diff` of the sorted outputs gives every changed line:
  - gone: `dora_keys.py 89 import d11lib` and `dora_keys.py 103 path .claude/workflows/cfr_exclusions.json`, both closed here.
  - moved, now as `locate()`'s argument and guarded (the enumerator does not read the call):
    - `dora_keys.py 103 -> 118`;
    - `corpus_churn.py 68 -> 74`, `100 -> 106` and `133 -> 139`.
  - shifted, the same literals at new line numbers, in the sweep's `tests/` not-applicable bucket:
    - `tests/closure.py 3844 -> 3850` and `3845 -> 3851`, the round-3 D2 fixture paths;
    - `tests/entities.py 29371 -> 29585`, `29374 -> 29588` and `32066..32109 -> 32280..32323`.
- Seams by this arm's rule (every program live policy or a carry command names under a historical prefix): 5.
  - `dora_keys.py`: closed here.
  - `corpus_churn.py`: closed here.
  - The other 3 already ran.
  - The carry-201 command spellings are closed here.
- Gate scope: `python3 tests/closure.py select --diff 613b10c51...` reads `MODE: FULL` (`tests/closure.py` is a gate file). At the head, seat venv python 3.14:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2321 ENTITY CHECKS PASSED`.
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`.
  - `python3 tests/layout.py --guard`: `GUARD: 0 refusal(s)` against `613b10c51`.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `prepr.sh` at the head: rc 0, no REFUSE.

## Red checks

At `fc75984b2`, #2289's first head:
- `closures`, check-run 116584227429: `UNDER-SCOPED`. CI's Linux `strace` recording found three reads the committed closures did not list:
  - `tests/entities.py` reads `dev/audit/rounds/round4/D12/cells.py` and `d12lib.py`, which the `units.py` probe child imports.
  - `tests/harness_headers.py` reads `corpus_churn.py`, which left INERT in this diff, so its old `inert_reads` entry no longer covers the read.
- `closures-autofix`, check-run 116595179899: `skip-classifier-disagrees`, because the PR moves a file out of INERT. So no bot commit came, and the `--single` prohibition lapsed.
- `pr-contract`, check-run 116606752470: re-run after those reds, it refused the body, which said `none` here.

Answer: `cf477e3c7` adds the three reads from that job's own list by hand, and this body names the reds. The local predictor missed them for two reasons:
- Darwin's `--single` recorder is an audit hook that does not follow the probe's child process. `prepr.sh`'s `ci predict` reads that recording, so it predicted nothing.
- The predict never reached `harness_headers.py`, whose read only changes class when a file leaves INERT.

The cheaper detector would check, at the moment a file is added to `INERT_EXCEPT`, every script whose `inert_reads` lists it. That is one `json` read. No tool runs it today. The root-cause seat owns the analysis of whether to build it.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`, group R10-STALE-PATHS's `carry`. The 35 evidence-only seams under D2 are carried to R10-BRIEFS-FOLD. The reviewer's F1 and F2 on #2289 are not blocking and are not carried by this pull request. F1 is the open shapes the arm does not follow; F2 is that the citation side is checked only on main's full run. Both were reported to the orchestrator for routing.

## Friction

none

