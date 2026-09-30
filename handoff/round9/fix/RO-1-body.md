<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Round-9 reorganisation PR R9-RO-1 (lane RO): the repository layout barrier, in report mode. This PR moves no files.

Before: nothing in the tree says where a tracked file belongs. A file placed outside the planned structure, a moved path added back, or prose that still cites a path after it moved all pass every check. brief_lint's basename fallback (`lookupPath`) keeps resolving a moved `fixer.md` or `HANDOVER.md`.

After: `tests/layout.json` encodes the target tree of the reorganisation plan (section 2, with tvofi's D1 to D4 of 2026-09-30T16:20Z). It holds eleven ordered categories, 155 retired entries and the historical prefixes. `tests/layout.py` checks four arms and prints a count for each. Today those counts are the distance to the target, so each later RO pull request shows its step on this meter. The check exits 0 until R9-RO-9 passes `--enforce`.

How:
- The **category** arm refuses any tracked path that matches no category glob, or more than one.
- The **retired** arm refuses a tracked path at a retired `old` path. It reads "planned move not yet made" while the entry's `since` is null, and "reintroduces moved path" once `since` names the PR that made the move.
- The **reference** arm refuses a retired `old` path cited as a path token (not the head or tail of a longer name) in any live text file.
- The **dead** arm refuses a category glob or retired entry that matches no tracked file, and a retired target that does not land in exactly one category.

The checker reads the index, not the worktree: paths come from `git ls-files` and text from `git grep --cached`. So its recorded closure is `tests/layout.json` plus itself, and the INERT prose it reads does not turn into a dependency. Historical text is excluded by prefix and also through the move map, so a delivery row counts as historical before it has moved.

`retired` is generated with `python3 tests/layout.py --gen-retired <inventory.tsv>`, using the plan's move map. The generator emits one entry per maximal directory that moves whole, and otherwise one entry per file. It skips any path the target still admits: `.claude/rules/` stays as a generated copy under D1. Regenerating keeps each existing `since`.

The script is wired into `tests/run.sh` as `run_always`, because a pure `git mv` is scoped only by its destination. It is also wired into `tests/derive_closures.sh`, and its closure was recorded with `--single` on Linux. The manifest gets a CODEOWNERS line.

Design choices (`fixer.md` step 11):
- **An overlap is an error; category order is only for display.** The plan calls the categories ordered, and also says matching two is refused. I followed the second.
- **Retired entries are exempt from the dead arm.** A deletion can never match a file again, so a typo in a deleted path's `old` is caught only while that file still exists.
- **On today's tree, "real tree green" means report mode exits 0.** It cannot mean zero findings until RO-9, because the categories describe the target, not today's tree.

## Head

`19f75625` is the code head, on `handoff/r9-ro-1`. Merge base is `830f84ad` (origin/main at 2026-09-30T16:25Z). This body and the resume note ride in one transport commit above it, touching only `handoff/` paths.

The full gate ran on `f26077a6`, the first code commit. Every script it names is unchanged from `f26077a6` to `19f75625` except these two, which were re-run at the head:
- `tests/entities.py`, which the next commit fixed.
- `tests/layout.py`, which gained an independent `ls-files` count, one historical filter, five self-test cases and two comment rewordings.

`tests/deployment_shape.py` changed in its docstring only, and was also re-run at the head.

## Mutation proof

`tests/layout.py` is the change, and `--self-test` is its driver. I ran twelve single-edit mutants of its predicates, each on a detached worktree at `19f75625`, with `python3 tests/layout.py --self-test`. All twelve were killed (rc=1). Each self-test case names the exact vector of per-arm counts it expects, so a mutant that lights the wrong arm fails as surely as one that lights none.
- M1, change `len(names) > 1` to `> 2`: red on `path in two categories`.
- M2, drop the token head boundary: red on `negative: a longer name that contains it`.
- M3, empty the historical-prefix exclusion: red on `negative: the citation under the archive` and `negative: the citation in a delivery row`.
- M3b, drop the moved-into-historical exclusion: red on `negative: the citation in a row not yet moved`.
- M4, disable the dead-glob arm: red on `dead category glob`.
- M5, make the directory-citation lookahead demand a slash: red on `live citation of a retired directory, no slash`.
- M6, disable the retired-file arm: red on `retired file re-added`, `retired target outside every category` and `negative: the citation in a row not yet moved`.
- M7, make `tracked()` drop one path: red on all fourteen cases, through the enumeration guard.
- M8, disable the retired-target category check: red on `retired target outside every category`.
- M9, disable the outside-every-category refusal: red on `file outside every category` and three more.
- M10, drop the file-entry tail boundary: red on `negative: a longer name that contains it`.
- M11, disable the dead-retired-entry check: red on `dead retired entry`.

M0, the unmutated file, gives rc=0.

In an earlier round, two mutants survived. The Python historical filter duplicated the grep's pathspec exclusion exactly: with it and without it, the arm read the same 1519 findings. The retired-target check had no case of its own. So I deleted the duplicate filter, and I added the self-test cases that now kill M3b, M8 and M11.

`mutation_table.py --scope changed --base origin/main`: `MUTATION TABLE PASSED (empty scope)`, "no production code line added or modified against the base". `--max 0` was not used.

## Null control

- **Base tree.** The self-test's base tree is built from the real manifest: one instance of every category glob, and the target of every retired entry. It reads `(0, 0, 0, 0)`. Each planted case differs from it by one file or one manifest edit.
- **Negative controls.** Five cases must stay green, and do:
  - the citation under the archive;
  - the citation in a delivery row;
  - the citation in a row that has not moved yet (only the category and retired arms fire there, as they must for a file at an old path);
  - a longer name that contains the path;
  - the new path cited.
- **Vacuity guard.** Every case also asserts that the checker enumerated as many paths as a separate `git ls-files` count lists, and at least as many as were planted.
- **Base comparison for ownership.** The `codeowners_gap.py` output at `830f84ad` and at the head differs only in the pattern count per arm (+1, the `tests/layout.json` line). Coverage is identical, and `uncovered_files` is 16 at both ends. So `tests/layout.py` is not on the required-check enforcement surface: it runs under `run.sh`, not directly from a workflow.

## Figures

- `python3 tests/layout.py` at `19f75625`, on the index, rc 0:
  - `layout: 3094 tracked path(s) enumerated` (`git ls-files | wc -l` prints 3094)
  - `category 2253`, `retired 2251`, `reference 1518`, `dead 27`
  - `layout: MODE: REPORT (exit 0 on findings until R9-RO-9)`
  - `layout self-test: ok`, over 14 cases
  - The full list is in `python3 tests/layout.py --verbose`.
- What the four counts are:
  - **category (2253)** is the 2251 planned moves plus `.claude/workflows/carry-1743.json` and `carry-1747.json`. Both landed after the inventory was measured at `754d2319` and have no row. Rule: `--verbose` category lines whose path is under no `retired.old`. Its null control is the same filter on the retired lines, which gives 0.
  - **reference (1518)** is live citations of retired paths. The plan counted 1,471 at `754d2319` with a different tokenizer, and its section 4.1 says to re-derive the figure.
  - **dead (27)** is the target-only globs: dev/*, docs/img/*, docs/design and tools/{policy,pr,seat,coverage,devices}.
- `python3 tests/layout.py --gen-retired inventory.tsv` (the plan's `handoff/round9/fix/RO/inventory.tsv` at `4e8f6d47`, sha1 `0e625ec7`) regenerates the committed `retired` list byte for byte: `regen identical`.
- Full gate, `PYTHON=<3.14.0rc2 venv, pinned requirements-ci.txt> GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=830f84ad ./tests/run.sh`, on a Linux cloud box at `f26077a6`:
  - `MODE: FULL`, because `tests/run.sh`, `tests/closures.json` and `tests/derive_closures.sh` are gate files.
  - `2 TEST SCRIPT(S) FAILED`: `tests/entities.py` and `tests/stress.py`. Both are answered under Red checks. Every other script printed ok.
  - `tests/layout.py (3s)` and `tests/harness_headers.py` were ok.
- `PYTHONPATH=tests/hastub python tests/entities.py` at `5d9b3666`: `ALL 1990 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python tests/deployment_shape.py`: `ALL DEPLOYMENT SHAPE CHECKS PASSED`.
- `node .claude/workflows/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`.
- `node .claude/workflows/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `./tests/derive_closures.sh --single tests/layout.py`: `tests/layout.py 2 files` (`tests/layout.json`, `tests/layout.py`).
- `python3 tests/closure.py selftest`: `ALL 23 closure shrink pins PASSED`.

## Red checks

- **`tests/entities.py` at `f26077a6`**, the #1218 selection-cost note: the `deployment_shape.py` docstring cited 351 script pairs (27 choose 2). A 28th recorded closure makes 378, and `tests/layout.py` joins the scripts with no production closure. Fixed in `5d9b3666`.
  - Cheaper detector: running `tests/entities.py` (about 90 s) right after `derive_closures.sh --single`, before the full gate. It exists, and it costs a new-script PR one extra run. I name it rather than build it.
- **`tests/stress.py` at `f26077a6`**, `every scenario's solve costs what it should, in CPU, for this machine`: `shoulder/tariff+cycle` measured 268x its reference against a 268x budget. This diff touches no production file and no solver input. The gate ran stress alongside the other lanes on a shared cloud box. I re-ran it once, alone under the gate lease (`tests/gate_lock.py auto-lease -- python tests/stress.py`, same interpreter, same tree; `stress.py` and the production code are unchanged from `f26077a6` to `19f75625`). It printed `ALL 87 STRESS CHECKS PASSED`, with the worst scenario at `shoulder/tariff+cycle used 9354 ms of CPU = 241.2x its 38.8 ms reference; budget is 268x`. So this is a machine-load reading, not a failure of this PR. CI runs stress under its own lease. No cheaper detector exists: this CPU arm is itself the detector for solver cost.
- The **pre-approval red** is owner review. `tests/run.sh`, `tests/derive_closures.sh` and `.github/CODEOWNERS` are code-owned, and `tests/layout.json` becomes code-owned. tvofi's approving review is owed. No `.github/workflows/*` file is touched, and no workflow step is added.

## Forward-carry

`tests/layout.py` (its module docstring and `gen_retired`) and `tests/layout.json` (`_doc`) carry items 1, 3 and 5 below, and the `since` rule of item 2, for every later RO seat, since they open these files to read the meter. Items 2, 4 and 5 go in full into the R9-RO-2 to R9-RO-9 `brief` strings of the round-9 roster on `handoff/audit-r9-fixplan`, which is not in main's tree: the orchestrator applies there the text in the RO-1 resume note on the transport commit above the code head. Each item was measured on this branch.
1. **RO-2 to RO-9:** `tests/layout.py` reads the index. A move is metered only after `git add` or `git mv`, and an unstaged edit reads as if it were not there. The control: re-wording a staged comment left `reference` at 1519 until it was staged, and staging it gave 1518.
2. **RO-2 to RO-9:** every planned move is already in `retired`, with `since: null`. A move PR sets `since` to its PR number for the entries it lands. It does not add entries. `--gen-retired` keeps `since` when it regenerates. The control: the regenerated list is byte-identical to the committed one.
3. **RO-5:** `.claude/rules/` is not retired, because the target admits it as D1's generated copy. `--gen-retired` skips any path that a target category admits. So `.claude/rules/*.md` citations are not counted, and the lift to `dev/governance/rules/` is metered only by the category arm going green for the new files.
4. **RO-4:** the carry calls (archive or programme) are the inventory's at `754d2319`. `carry-1743.json` and `carry-1747.json` have no row and sit in the category count. Re-derive the open or closed state at RO-4's merge base, and regenerate.
5. **RO-9:** enforcing means `run_always "$PYTHON" tests/layout.py --enforce` in `tests/run.sh`, plus `fast` and the required contexts, as section 7 says. The `MODE:` line then reads `ENFORCE`.

## Friction

- fixer.md: cost: step 5's `MODE: FULL` covers a diff that adds one run_always script. The full gate ran about 18 minutes on the cloud box, and in parallel lanes `stress.py`'s CPU arm reads at its budget edge.

🤖 Generated with [Claude Code](https://claude.com/claude-code) · https://claude.ai/code/session_01UqT5TwuvFRR3dxKprGpYTe
