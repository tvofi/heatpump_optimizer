_Requested by **tvofi**_

R9-FR-5 (roster brief on `handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json`): `prepr.sh`'s closures recorder resolves its interpreter **deliberately** — prefer an interpreter that parses the tree (`$HPO_RECORDER_PYTHON`, then the seat venv `tools/audit/seat/seat_venv.sh` builds), adapt to the ambient `python3` only when it parses the tree, and **refuse with the build command** when none does — mirroring `gate-scoping.md`'s mypy-census rule (#1091/#1099/#1095): an unpinned interpreter fails rather than measuring.

**The two incidents this closes.** R9-FR-3 and R9-WEB-5 each lost a full `prepr.sh` pass to the same defect: `tests/derive_closures.sh` records under `${PYTHON:-python3}` — the first `python3` on PATH — and on a seat whose PATH still resolves to pyenv 3.11, that interpreter cannot parse the tree (the nested same-quote f-string at `tests/entities.py:3850` is 3.12 syntax, PEP 701). The recording dies at compile, the wrapper still exits 0 (the #1591-review G shape), and step 6b refuses with **"failed while being recorded: tests/entities.py (exit 1) — fix the script first; a re-derive would record the same truncation"** — advice pointed at the wrong artifact. The script is fine; the interpreter is the defect. Measured at `origin/main` `283eb22f0` on this machine (ambient `python3` 3.11.5, seat venv 3.14.7 — the incidents' exact shape), Figure F1 below re-derives that refusal verbatim.

**What the fix is** (in `tools/audit/prepr.sh` only — the recorder already honours `$PYTHON`, so `derive_closures.sh` is untouched):

- `recorder_python` resolves the interpreter in one place, in order: `$HPO_RECORDER_PYTHON` (an override in the style of `HPO_TYPING_PYTHON`; **checked, never trusted and never skipped past** — a seat that named one asked for it by name, and silently recording under something else is the defect), then `$HPO_STATE_DIR/venv-ci/bin/python3` (the seat venv, whose pins are what recorded scripts import), then the ambient `python3` as the **adaptation**.
- Every candidate must pass `recorder_parses`: `ast.parse` over every `tests/*.py` and `custom_components/**/*.py` the recorder may run or import — 111 files, 0.2 s, the same parse the incident fails. The guard is the parse, not the path: a venv that exists but cannot parse is skipped, exactly as a good ambient is used.
- `closures_line` resolves **lazily**, on the first script this machine will actually record, so a diff whose recordings are all left to CI owes no interpreter; the result reaches `derive_closures.sh` as `PYTHON=<resolved>`.

Under a seat already running a good interpreter nothing changes — the ambient candidate resolves by name, `PYTHON=python3` equals the unset default, and the recording is byte-unchanged (Figure F4). When no candidate parses, the step refuses before anything records, naming `tools/audit/seat/seat_venv.sh` (Figure F3) instead of the truncated-recording refusal.

Alternatives rejected:

- **Hardening `derive_closures.sh` itself.** The recorder is also CI's lane driver, where the interpreter is already pinned by the workflow; the incident is a seat-time failure and `prepr.sh` is the seat-time gate. One resolution point, in the gate that refuses.
- **Probing "can run `closure.py`" or a version floor.** A version floor pins a number that drifts; a `closure.py`-only probe under-covers the recorded scripts. `ast.parse` over the recorder's actual input domain is the property, and it self-maintains as files change.
- **Refusing whenever the ambient cannot parse, even with no recording to do.** Rejected: lazy resolution keeps `PREPR_SKIP_CLOSURES`-style boundaries intact — a branch whose recordings are all left to CI (node lanes, lease-guarded scripts) never owed an interpreter.

## Head

`b8cabfb80db2ea5b627ac3cb2d9ebd4c707eb736` (extends 81cc117b by automatic origin/main absorbs; prepr.sh is unchanged between the heads, so the verdict carries) (measured 2026-10-04; `origin/main` `283eb22f0` — R9-FR-2's merge — merged in at `b8cabfb80db2ea5b627ac3cb2d9ebd4c707eb736`, merge never rebase, and steps 2–8 re-executed after it)

## Mutation proof

Three hand mutants, each `bash tools/audit/prepr.sh --self-test` with the mutant applied, failing rows pasted, restored:

- **`PYTHON` never passed to the recorder** (`PYTHON="$rp"` deleted from the `derive_closures.sh` invocation): `174 passed, 1 failed` — "and the recorder received that interpreter as \$PYTHON".
- **a refused resolution records anyway** (`rp=$(recorder_python) || { echo "$rp"; r=1; break; }` reduced to `rp=$(recorder_python)`): `172 passed, 3 failed` — "6b refuses an override that cannot parse the tree instead of recording under it", "and the step's refusal names the venv build command", "and nothing recorded under the refused interpreter".
- **the override is trusted, never checked** (`if recorder_parses "$HPO_RECORDER_PYTHON"` → `if :`): `170 passed, 5 failed` — the override-refused arm and its refusal-text row, plus the same three step-level rows.

`tests/mutation_table.py --scope changed` at the head: `no production code line added or modified against the base ... MUTATION TABLE PASSED (empty scope)` — `tools/audit/prepr.sh` is outside the table's production scope, so the self-test rows above are the pinning instrument and CI's mutation check owns what it can select.

## Null control

- **Failing first**: at 9a04d5e03 (fixture commit, `recorder_python` absent) `bash tools/audit/prepr.sh --self-test` reads `148 passed, 13 failed` — all thirteen new rows fail (`recorder_python: command not found` on the resolution arms; step 6b still recording without resolving), every pre-existing row green. At the final head: `175 passed, 0 failed` (FR-2's merge added fourteen rows).
- **Ambient adapts**: the resolution arm "a parsing ambient is used as-is, so a recording under it is byte-unchanged" — the seat-venv seat's own path, where `recorder_python` returns `python3` by name and `PYTHON=python3` is the unset default.
- **The parse guard is the parse, not the path**: the arm "a venv that cannot parse is skipped for a parsing ambient" — presence in `$HPO_STATE_DIR` selects nothing by itself.
- **Resolved == explicit** (F4): the recording taken through the resolution at the head and `origin/main`'s own recorder handed the same interpreter explicitly agree on every closure-relevant field — `script`, `rc`, `how`, and the 208-file closure as repo-relative paths. Excluded by stated rule, because the two runs ran in different checkouts: absolute checkout paths, `seconds`, per-run `mktemp` directory names, and the synthetic fixture commit SHAs `tests/entities.py` mints inside its throwaway repositories (their timestamps differ per run).

## Figures

Rule for every count below: the printed line of the named command at the named head, pasted, not restated.

- **F1 — the defect at `origin/main` `283eb22f0`**, in a detached snapshot worktree, ambient `python3` = 3.11.5:
  - `python3 -c 'import ast; ast.parse(open("tests/entities.py").read())'` → exit 1, `SyntaxError: f-string: f-string: expecting '}'` (line 3850).
  - `./tests/derive_closures.sh --single tests/entities.py --record-only --out-dir <dir>` → wrapper exit 0; the recording JSON reads `recording rc: 1 | files recorded: 1`.
  - main's own `closures_verdict` over that dir prints: `failed while being recorded: tests/entities.py (exit 1) -- fix the script first; a re-derive would record the same truncation` — the refusal FR-3 and WEB-5 hit, advice at the wrong artifact.
- **F2 — the adaptation at the head**: `recorder_python` (same machine, same PATH) → `rc=0`, resolves `/Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3`; `PYTHON="$(recorder_python)" ./tests/derive_closures.sh --single tests/entities.py --record-only --out-dir <dir>` → recording rc 0; main's `closures_verdict` over it prints `scoped recordings are covered`.
- **F3 — the refusal at the head**: `HPO_STATE_DIR=<empty dir> recorder_python` (no seat venv, ambient 3.11.5) → exit 1, prints `no interpreter that parses the tree was found (tried the seat venv at <dir>/venv-ci/bin/python3 and the ambient python3) -- build the seat venv: tools/audit/seat/seat_venv.sh` — the named command, before anything records.
- **F4 — resolved == explicit** (the two runs ran in different checkouts, so the rule excludes checkout location, `seconds`, per-run `mktemp` names and synthetic fixture SHAs; the compared fields are `script`, `rc`, `how` and the file closure as repo-relative paths):
  `python3 -c` over the two recordings, normalising each `files` entry by its own checkout root and sorting:
  `a=json.load(open('rec-resolved/entities.py.json')); b=json.load(open('rec-venv-explicit/entities.py.json'))` →
  `script equal: True | rc equal: True | how equal: True` and `file closures equal (repo-relative): True | count: 208`.
- `bash tools/audit/prepr.sh --self-test` at the head: `175 passed, 0 failed` (failing first: `148 passed, 13 failed` at 9a04d5e03).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` at the head: `MODE: SCOPED -- 0 script(s) run, 30 scoped out.` — keyed on the mode line; the diff is `tools/audit/prepr.sh` alone, which no measured closure reaches, so the remainder is CI's.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.
- `bash tools/audit/prepr.sh <this body>` at the final head, after the push: every step green, `PRE-PR: `b8cabfb80db2ea5b627ac3cb2d9ebd4c707eb736`...` rc 0.

## Red checks

`nightly-status` (expected red): it grades `main`'s last scheduled run, and this diff touches none of its inputs (`tests/nightly_status.py`, `tests/delivery_status.py`, the workflow files, the plan, `docs/HANDOVER.md`) and no delivery row — the row is the orchestrator's, written on opening. This branch's own pushed commits carried no check runs when this body was written (no pull request yet).

## Forward-carry

`none` — the instrument now self-resolves; a seat running `prepr.sh` needs no new instruction, so no brief or contract changes how it must work.

## Friction

`none`

