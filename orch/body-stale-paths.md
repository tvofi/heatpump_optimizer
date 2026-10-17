D13-s3-01 (#2227, class N-move-stale-path): a file move left a program that live text tells a seat to run unable to run. `dev/governance/dimensions/D13.md` step 4's `dev/audit/rounds/round4/D11/dora_keys.py` imported a `d11lib` the move left under `tools/`, and opened `cfr_exclusions.json` at its pre-move home. `dev/audit/rca/R10-N-move-stale-path.md` names the cause, process state (c): the move checks ask whether a cited path exists, never whether the cited program runs. It prices countermeasure form (ii), a narrow arm, and this pull request ships it. It fixes every instance that arm finds, in both halves of the class: a cited program broken by a move, and a carry command spelled at a moved path.

What changes:
- `dev/audit/rounds/round4/D11/dora_keys.py` and `dev/audit/rounds/round5/D11/seat-b/corpus_churn.py` open what moved through `tests/layout.py`'s own resolvers (`canon`, `locate`), not hand-patched paths.
- `dev/programme/carries/carry-201.json`: every `remeasure` path spelled at a moved location is re-pointed to where the file lives. That is 8 executables across `/carries/0`-`/carries/2`, among them "run the D13 instrument (`dev/audit/rounds/round5/D13/seat-a/dora_cfr.py`)" and the `node tools/policy/policy_lint*.mjs` commands. The other retired paths on those same lines move too (`cfr_exclusions.json`, `field_coverage.mjs`, `prepr.sh`, and the restore globs `tools/policy/*.mjs`, `*.py` and `vendor`), because `tests/layout.py --guard` reads a touched line as a new citation of each retired path on it. Record fields that recount what was run stay as written.
- `tests/entities.py`, the cited-program arm:
  - Sources: every executable a policy file cites (`policy_lint.mjs`'s `policyFiles()`, now exported), and every executable path token in a carry's `remeasure`, whatever verb or bracket surrounds it. Both are read from the git index, as `tests/layout.py` reads INERT prose (#357).
  - Probe: each source that lands under a `layout.json` `historical` prefix is loaded in a fresh interpreter, the way a seat runs it. Every repository path it opens must resolve.
  - Opens: the check is keyed on the open (a literal in `open`/`Path`/`join`/a subprocess or existence call, directly or through an assigned name), not on every literal. `codeowners_gap.py` holds retired classifier inputs it never opens.
  - Spelling: separately, any `remeasure` path token spelled where the move map says a file no longer lives is refused, under a historical prefix or not, because a seat pastes the spelling.
- `tests/closure.py`: `corpus_churn.py` joins `INERT_EXCEPT` by name, beside `dora_cfr.py`. This is a gate file, so the scope is `MODE: FULL`.
- `tests/closures.json`:
  - `tests/entities.py` was re-recorded with `--single`.
  - The three reads CI's Linux recording named were added by hand: `round4/D12/cells.py` and `d12lib.py` for `entities.py`, and `corpus_churn.py` for `harness_headers.py`.
  - `corpus_churn.py` left both `inert_reads` lists.

Alternatives considered:
- Moving `dora_keys.py` back to `tools/audit/round4/`: refused. It is a retired prefix, and the move would force a policy edit.
- Hand-patching code paths: refused, because it breaks on the next move. Carry commands are the exception, since a seat pastes them as written.
- Keying the probe on every literal: refused, because it over-fires on `codeowners_gap.py`.
- The whole-tree enumerator as a gate (form (i)): refused by the RCA's cost test.

Part of #201.

Closes #2227.

## Head

`60c4b9b13e5a02bf54199b707c961e29bfe321a6` merges the authored code head `69fc404530ad81e477de0562c8906619d147780e` and then merges origin/main `d4c94f9a4` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`69fc404530ad81e477de0562c8906619d147780e`. It merges `origin/main` `39b77a467`, the merge base, into `918f24e3f`. The merge had no conflict; main's side was `services.py`, `tests/features.py`, 4 lines of `tests/entities.py` and delivery rows. Figures below marked "at `74cf47b9c`" were taken before that merge; the gate lines were re-run at this head. This round's commits:
- `aea9c5e96`: merges main; no conflict, and the ledger driver merged `tests/closures.json` as a set. The three hand entries were re-checked after it.
- `db1aa6583`: the widened reader, failing first.
- `918f24e3f`: carry-201's remaining spellings.

## Mutation proof

The arm block was driven alone, an `exec` of the `tests/entities.py` block between `# --- N-move-stale-path (#2227)` and `# --- D11-04 (#1194)`. Each mutation was restored with `git checkout`.
- M1, `corpus_churn.py`'s budgets read reverted to the bare literal: FAIL `every program live policy or a carry's remeasure tells a seat to run, under a historical prefix, loads and resolves the paths it opens (#2227)`.
- M4, `dora_keys.py`'s library line reverted: FAIL, `ModuleNotFoundError: No module named 'd11lib'`.
- M5, `CFR_EXCLUSIONS` bare: FAIL, `dora_keys.py:118 opens '.claude/workflows/cfr_exclusions.json'`.
- M2, every held literal instead of opens: both checks FAIL.
- M9, `/carries/1`'s "run the D13 instrument (`tools/audit/round5/...`)" restored and staged: FAIL, `commands naming no file [... tools/audit/round5/D13/seat-a/dora_cfr.py ...]`.
- Failing first:
  - The widened-reader commit fails on the three moved spellings round 2 found (`dora_cfr.py`, `policy_lint_mutants.mjs`, `policy_lint.mjs`).
  - The earlier arms failed on `dora_keys.py` (`8d5b657e1`) and `corpus_churn.py` (`cccf2f932`).

## Null control

- `units.py` (cited by `COMMON.md`) loads and resolves at both ends.
- `codeowners_gap.py` holds more than 0 stale literals and has 0 opened faults.
- Planted spellings: "run the D12 instrument (`<canon(units.py)>`) with its fixtures" and `python3 <canon(units.py)>` are refused. `python3 <units.py>` is not.
- Planted opens:
  - `open(<retired>)` and `os.path.join('.', _P)` are refused.
  - `open(locate(<retired>))` and a held `(<retired>,)` are accepted.
- Floors: at least 20 policy files, 1 carry and 3 cited programs. The head reads 41 policy files and 8 carries, and cites 5 programs, all `runs`.

## Figures

Taken at `918f24e3f` against a detached worktree at `74cf47b9c` (the merge of `39b77a467` touches none of these instruments' inputs), except the gate lines, which were re-run at the head:
- `python3 dev/audit/rounds/round5/D11/seat-b/corpus_churn.py`: rc 1 at the base (`FileNotFoundError .claude/workflows/policy_budgets.json`), rc 0 at the head.
- `dora_instrument_check()` from the finder's `dev/audit/rounds/round10/D13/s3/d13_s3.py`, driven alone with `PYTHONPATH=tests/hastub`: `RESULT dora_keys_loads=0` at the base, `1` at the head.
- `python3 -I dev/audit/rounds/round10/D14/sweep-N-move-stale-path/enumerate.py .`: `seams=2876 broken=368` at the base, `seams=2882 broken=367` at the head. It does not scan `.json`. The `diff` of the sorted outputs:
  - `dora_keys.py` 89 (import) and 103: gone, closed here.
  - `dora_keys.py` 118 and `corpus_churn.py` 74/106/139: guarded, the same literals as `locate()`'s argument, which the enumerator does not read.
  - `tests/closure.py` 3844/3845 -> 3850/3851 and the `tests/entities.py` lines: shifted only, in the sweep's `tests/` bucket.
- Seams by this arm's rule:
  - 5 cited programs. `dora_keys.py` and `corpus_churn.py` are closed here; 3 already ran.
  - Moved `remeasure` spellings over all 8 carries: 0 at the head, from the arm's own `_sp_moved_spellings`. carry-201 was the only carry with any.
- Gate, scope `MODE: FULL`, seat venv python 3.14:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2321 ENTITY CHECKS PASSED`.
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`.
  - `python3 tests/layout.py --guard`: `GUARD: 0 refusal(s)`.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

At `fc75984b2`:
- `closures` (116584227429) was `UNDER-SCOPED`. CI's Linux recording saw three reads: `entities.py` reading the `units.py` probe child's `cells.py` and `d12lib.py`, and `harness_headers.py` reading `corpus_churn.py`, which left INERT here.
- `closures-autofix` (116595179899) returned `skip-classifier-disagrees`, so no bot commit came.
- `pr-contract` (116606752470) refused the body that said `none`.

`cf477e3c7` adds the three reads by hand; `closures` was green at `5014df139`. The local predictor missed them because Darwin's `--single` audit hook does not follow a child process. Checking every `inert_reads` list for a file added to `INERT_EXCEPT` would have caught the `harness_headers.py` read for one `json` read. No tool does that today; whether to build one is left to the root-cause seat.

At `5014df139`, `Analyze (python)` (116625518165) was cancelled after 30 minutes. Nothing in this diff explains it: the CodeQL aggregate passed. The orchestrator re-ran it, and the re-run (116655047872) passed.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`, group R10-STALE-PATHS's `carry`: the 35 evidence-only seams under D2 go to R10-BRIEFS-FOLD. The reviewer's F1 and F2 are routed by the orchestrator, not carried here.

## Friction

none
