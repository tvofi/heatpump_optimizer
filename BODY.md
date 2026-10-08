Part of #1922 (R9-RO-9 has two more parts: R9-RO-9b retires the old paths, R9-RO-9c enforces the layout; this PR closes nothing). The R9-RO-9a "instrument carries" scope from the RO-9 pre-study, plus three coordinator additions: machine paths in mutation-ledger reasons, INERT READS predictions, and direct-push merge commits in the rows gate. Non-policy: `node tools/policy/policy_lint.mjs --corpus-filter` over the diff's paths prints nothing. No budget moves.

What changed, each failing first:

- **C9a, `tests/mutation_table.py` `added_unpinned`.** The old code matched in one greedy pass. A twin line added in a new def above the base's line used up the base's site, so the base's own line was reported as added. Now the match runs in two passes: first every site takes a base twin under its own def, then leftovers take any twin. This is the same code CI's `mutation` ratchet and `ci_predict` call.
- **C9b, `added_keys`.** All mutants of one operator on one line share a ledger anchor, and `pin_results` pins an anchor only when every mutant under it is killed. So the key now carries a multiplicity: `FILE:LINE KIND*N`. One key per anchor goes through CI's refusal, `ci_predict` and prepr 6d's sed. Before, three bare copies of one key were written.
- **C5, `tools/pr/ci_predict.py` `no_recording`.** An edit to `tests/derive_closures.sh` is now charged only with the recordings it drops, compared against the base's `rec` lines. Before, it was also charged with main's unrecorded scripts.
- **C5, `tools/pr/prepr.sh` 7d.**
  - A key now matches whole, so `f.py:12 CONST` is not satisfied by `f.py:12 CONST_X`.
  - The refusal names the exact heading it wants and any near-miss it found.
  - The matcher stays inside `unpinned_line`, so a harness that extracts that function whole still runs it. The finder's `plant_r2.sh` does exactly that.
- **C3b, `tests/layout.py` and `tests/closure.py`.** Guard self-test cases pin M8 (the `layout:old=` end-of-path boundary) and M10 (the `.claude/rules/` and `.cursor/rules/` exemptions). A prune case pins Mc4: a closures key whose every entry was a phantom is kept, empty.
- **C4, `tools/audit/seat/record_row.py`.** The exit mapping is factored into `automerge_rc`. Self-test cases drive `automerge_check` over a stubbed check-runs read. They pin (i), no `pending:` beside a refusal, and (ii), a mixed list exits 1.
- **C6(1)(2), `tools/audit/seat/merge_train.py`.**
  - `batch/` cleanup now reads the delete's rc. A refused delete is logged `NOT deleted ...`, never `deleted`.
  - The proved-pair residual is documented in the docstring and in `INSTRUMENTS.md`. It is not in `orchestrator.md`, which keeps this PR non-policy.
- **Coordinator addition, `tools/audit/seat/tmp_paths.py`.** `--check` now refuses a temp, home or seat-directory path on a `tests/mutation_ledger/` line the diff adds.
  - It compares by line text against the merge base with origin/main, or the first parent on main. So main's 31-file stock is not charged, and a re-keyed row keeps its line.
  - It catches both instances reported today, #2025 and #2010 (Figures).
- **Coordinator addition, INERT READS in `ci_predict` and prepr 6d.**
  - A predicted INERT READS red now warns and does not set the rc. `closures-autofix` merges inert reads from CI's Linux `strace` recordings after the push (ci-autofix.md), and `derive_closures.sh --single` on a Mac records none. So the refusal could only be passed by hand-editing `tests/closures.json`, which is what #2025's fixer did.
  - UNDER-SCOPED and the other closures reds still refuse.
- **Coordinator addition, `tests/delivery_status.py` rows gate.** A two-parent first-parent commit that names no pull request now gets a disposition, listed as `exempt`:
  - `record-only` when its first-parent diff touches only delivery rows. Pre-lift row paths are read through the move map.
  - Otherwise, a line in the new tracked `dev/programme/delivery/direct-pushes.md` naming its sha.
  - An unknown file list stays UNCHECKED.
  - Over `v6.7.16..origin/main`, 4 of the 9 such commits are now record-only. The five code pushes (`618d014`, `f6ac991`, `077f53a`, `130c780`, `8107181`) stay UNCHECKED until the orchestrator adds their lines; this PR invents no disposition.
- **C1, C2, C3a: record and prompt text.**
  - `coverage_tree.sh` usage path.
  - `R9-RCA-2004.md`: #2012 is now recorded as merged; moved round and harness paths are noted where cited; #2014's `## Red checks` sentence is corrected.
  - The `audit-verify.js` rotation.json parenthetical is dropped, since `check-wave-script.mjs` passes without it.

Alternatives not taken:
- C9b, three distinct keys per mutant: the ledger disposes per anchor, so distinct keys would ask a body for three dispositions where one applies.
- The ledger arm, a whole-tree scan: it refuses main's 31 stock files on every branch. Rewriting those 31 recorded reasons would edit measurement records.
- A per-file allow list: fixer.md step 14's blind-key shape.

## Head

`de5f654977adcd15a870a5830c46b6c4126ff40c`, merging origin/main `0b89f781` (#2054; 2026-10-08T14:49Z). Every figure below was measured at this head unless it names another tree. A red demonstration on a "tests-only tree" is that item's test commit with its fix not yet applied.

## Mutation proof

Each fix was removed (the merge-base code is the fix-free state) or mutated, and the closure re-run:

- C9a/C9b: `tests/entities.py` on the tests-only tree prints `FAIL added_unpinned charges a twin line to the def that gained it ...` and `FAIL added_keys gives a line with three comparison mutants one key ...`, with `2 of 2214 ENTITY CHECKS FAILED`.
- C5: `tools/pr/prepr.sh --self-test` on the tests-only tree gives `214 passed, 4 failed`. The four FAILs:
  - `6d charges no branch that only edits the lane file with a script main already left unrecorded`
  - `and a line holding two comparison mutants is one key carrying its multiplicity`
  - `and its refusal names the heading it found and the one it expects`
  - `7d matches a key whole, never inside a longer key`
- M8: the `(?![\w./-])` boundary deleted. `layout.py --self-test` gives `FAIL guard self-test: a stale command whose marker names a longer path` and `1 case(s) FAILED`.
- M10: `.claude/rules/` and `.cursor/rules/` removed from `GUARD_EXEMPT`. `FAIL ... generated .claude/rules copy` and `FAIL ... generated .cursor/rules copy`, `2 case(s) FAILED`.
- Mc4: `or table_key == "closures"` deleted. `closure.py selftest` gives `FAIL prune keeps a closures key whose every entry was a phantom ...` and `1 of 40 closure shrink pins FAILED`.
- record_row (i): `if green and not why` changed to `if green`. `1 self-test check(s) failed: automerge_check lists no pending context beside a refusal`.
- record_row (ii): the exit changed to `3 if pending else 1`. `1 self-test check(s) failed: automerge_rc: a refusal beside a pending context exits 1, pending alone 3, nothing 0`.
- merge_train, with the new case on main's code: `FAIL a proof branch the remote would not delete is reported left, never deleted`, `81 checks, 1 failed`.
- tmp_paths:
  - With the new cases on main's code: 4 FAILs, all four `a ledger reason citing ... is refused`.
  - Mutant `if m and text.strip() not in was` changed to `if m`: both stock cases FAIL.
  - Mutant with the ledger call removed from `main`: the #1960 replay prints 0 ledger refusals, against 33 with it.

- INERT READS: on the test commit with the fix not applied, `prepr.sh --self-test` gives `FAIL and an INERT READS red warns, never refuses ... (got rc=1, wanted rc=0)` and `219 passed, 1 failed`.
- delivery_status: on the tests-only tree, `entities.py` gives `FAIL a direct-push merge commit is dispositioned ...` (`TypeError: collect() got an unexpected keyword argument 'allow'`) and `1 of 2215 ENTITY CHECKS FAILED`. Each mutant was then run alone, and each gives that same FAIL and `1 of 2215 ENTITY CHECKS FAILED`:
  - `classify` counts dispositioned entries as blind again.
  - `disposition` ignores the tracked lines.
  - `all` is weakened to `any` over the row files.

## Null control

- At the head, every touched instrument's own null controls stay ok, including `and an UNDER-SCOPED red still refuses` and the entities arms where code pushes without a line, rows plus a script, and an unknown file list all stay UNCHECKED. Examples: `7d passes keys written in backticks`, `and passes the same key named whole`, `6d still predicts NO RECORDING for a recording the lane edit drops`, `a ledger reason citing a tracked path passes`, `... the same pair on a green main is proved and merges`, `and lists the contexts not yet passed once nothing refused, none when all passed`.
- The finder's harness (`plant_r2.sh`, sha1 `a725cc4ea5c6ca732d41aaf8b86f745dfbbd1d9d`, run from `/Users/timmalmstrom/hpo-seats/review-2030-r2/evidence/` with `SRC` parameterised), at the merge base and at the head:
  - Arm B (the branch only comments `derive_closures.sh`): `NO RECORDING ... rc=1` at the base, `rc=0` at the head.
  - Arm C, the control (the branch's own unrecorded script): fires at both ends.
  - E2/E3 (a `(3)` suffix, a lower-case heading): refused at both ends; the head names the expected and the found heading.
  - E6 second arm (`:12 CONST` named only as `CONST_X`): `disposes of all 1` at the base, `omits` at the head.
  - E1/E4/E5: identical at both ends.
- `tmp_paths --check --ref <parent of #1960's merge>` prints 0 ledger refusals; `--ref HEAD` prints 0 (main's stock is not charged).

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL` (tests/closure.py changes the gate itself). The always-run scripts were run locally; the rest is CI's, at this head.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py selftest`: `ALL 40 closure shrink pins PASSED`.
- `python3 tests/layout.py`: `layout self-test: ok`.
- `python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`.
- `python3 tests/entities.py`: `ALL 2215 ENTITY CHECKS PASSED`.
- `python3 tools/audit/seat/record_row.py --self-test`: `all checks passed`.
- `python3 -I tools/audit/seat/tmp_paths.py --self-test`: `50 checks, 0 failed`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries at HEAD`.
- `python3 tools/audit/seat/merge_train.py --self-test`: `81 checks, 0 failed`.
- `node tools/policy/check-wave-script.mjs`: `170 passed, 0 failed`.
- `bash tools/pr/prepr.sh --self-test`: `220 passed, 0 failed`.
- `python3 tests/delivery_status.py --check`: `UNCHECKED`, with 4 `exempt ... record-only` lines and 5 `unread` lines (the five code pushes named above); rc=1 until their lines are added.
- `python3 tools/pr/ci_predict.py --base origin/main`: `no closures or fast red predicted`.
- Ledger arm replays, each rule being "lines `tmp_paths.py --check --ref <ref>` tags `ledger-machine-path`":
  - `python3 -I tools/audit/seat/tmp_paths.py --check --ref 00da22db5`, the #1960 merge that brought in the stock: 33. With `--ref 00da22db5^1`: 0.
  - At #2025's head `9c664109`: 1 (an equiv_6840 probe under a seat scratch directory).
  - At #2010's head `9a8255b3`: 1 (a probe_idle_codes probe under a seat scratch directory). Those heads were fetched as `pull/N/head`.
- Ledger stock on main: `git grep -l -I -E "/private/tmp|/tmp/|/Users/|/home/|hpo-seats" -- tests/mutation_ledger` lists 31 files.
- Moved-path citations in the RCA record. Rule: each `tools/audit/...` token in `dev/audit/rca/R9-RCA-2004.md` whose path `git ls-files` does not list. Each seam the rule returns is disposed:
  - Lines 105, 117 and 157 (round trees and harnesses, moved by #2015): annotated with the new home.
  - Line 53 (a quote of fixer.md step 18), lines 127-128 (the broken spawn as written), line 149 (the docstrings as quoted) and line 259 (the rule's old wording): kept as quotes.

## Unpinned sites

n/a: the diff changes no file under `custom_components/` (step 6d lists none).

## Red checks

- `delivery-status` was red at `cf84e0a4`. It grades `main`'s window since `v6.7.16`, not this diff. That window holds nine two-parent direct pushes that name no pull request, so the job reads UNCHECKED and `--check` exits 1; `python3 tests/delivery_status.py --check` prints the list at main. This PR's `delivery_status` change is the repair: four become `record-only`, and the five code pushes need the orchestrator's lines in `dev/programme/delivery/direct-pushes.md`.
  - Cheaper detector: none earlier than this job. A direct push bypasses every pull-request check by construction, and this job runs on the next pull request.
- `nightly-status` was red at `cf84e0a4`. It grades `main`'s nightly runs and reads no file this diff touches.

## Forward-carry

- C4's production confirmation that the author App token can dismiss reviews is a GitHub write, so it stays the orchestrator's.
- C6(3), the #2044 PR-body nits: that body is merged, so the orchestrator decides.
- C7(1)(2), the CI-1 pin drive and the `boost_drift_replay` driver timeout: left for a separate PR, per the brief.
- C7(3)/C8: dropped, fixed by #2051; the remaining throwaway-repo sites belong to open #2054.
- PR-body machine-path scanning: not built. fixer.md step 3 sanctions citing the finder's out-of-tree harness by path (this body does). A body arm would therefore need a policy change saying which body paths are legitimate. This is a recorded decision not to build it in this PR, not a carry to a later RO-9 stage: neither R9-RO-9b nor R9-RO-9c changes how it would be built. The orchestrator decides whether to raise it as a policy question.
- Once merged, the ledger arm refuses the machine paths that #2025 (an equiv_6840 probe under a seat scratch directory) and #2010 (a probe_idle_codes probe under a seat scratch directory) add to their triage reasons, after either merges main. Their fixers owe either the probe landing in the tree or a reason without the path.

## Friction

none
