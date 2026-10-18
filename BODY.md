R10-TRAIN-RAISE-HOLD. Part of #201.

`merge_train.py`'s approve and `queue_pre_flight.py` decided that a pull request was a budget raise when any changed path ended `_budgets.json`. #2401 only added rows to `tests/ci_budgets.json`, and CI's `budget-raise-gate` printed `budget_raises=0` and passed it. Trains t11, t12 and t13 still stopped at approve. The Stop dropped the gate's own reason (`_owner_at_head` returned `why if ok else None`). Pre-flight kept a second copy of the reading that called `approval()` without the justification, so it admitted what approve stopped.

- **One reader.** `Train.raise_hold(pr, h, files)` calls `budget_raise_gate.raises_between`, which is extracted from `gate()`, and `gate()` now calls it too. It reads from the merge base with origin/main.
  - No raise: the ordinary mandate approval path.
  - A raise: `approval(..., justify=justification(body))`, with the mandate judged at the merge.
  - A failed read stops, and so does a budget path the diff names that neither tree lists.
  - `queue_pre_flight.entry` calls the same method. It reads the body on the raise branch only. Its `budget_gate` copy is deleted.
- **The Stop and the PARK carry the gate's `why`.** Docstrings are updated at merge_train's step 6 and batch step 1, and at pre-flight's `budget` line.
- **Fixtures.** The budget self-test fixtures are real raises now: blobs at both ends (`RAISE_FIXTURE`, `NEW_ROWS_FIXTURE`, `budget_fixture`), so a budget path and a raise are separate facts in every budget arm (the ones naming a `*_budgets.json` file).
- **RCA.** `dev/audit/rca/R10-RCA-TRAIN-RAISE-HOLD.md` holds state (c), the cost test and the demonstration table. It is registered under class I4 in `dev/audit/config/bugclasses.json` (`rca` and `_rca`). I4's barrier gains the `budget-raise` pair in `tools/policy/agreement.mjs` and `agreement_py.py`: the gate restored from the base against the PR's train, over eight edits of every tracked budget file.
- **merge_pr.sh (the orchestrator's added item, in its own commit `0ed4aceb2`).**
  - Owner mode no longer hard-codes the expired 2026-09-24 mandate. It takes `--mandate <comment-id>` and reads that comment live through the gate's `_mandate` and `mandate_state` (judged now, scope `code-owned` or `all`).
  - It refuses before posting anything when no mandate is given or the one given is not in force.
  - A draft refuses before any post unless `--ready` marks it ready.
  - `--self-test` added. `proof_watch.py` passes `--mandate` through (`dcd012deb`), and `INSTRUMENTS.md` says so.

Alternatives (step 17):
- (a) Keep the train's path filter and add `file_raises` beside it. Lost: two loops over the budget files, which is the I4 shape again.
- (b) Copy `gate()`'s path loop (canon, locate, head_has) into the train. Lost: the third copy of the reading that this defect is about.
- (c) Taken: extract `raises_between` into the gate, the module that owns the concept, so CI, the train and pre-flight run one function. The cost is that the PR touches the code-owned `budget_raise_gate.py`. `gate()`'s behaviour is unchanged: `budget_raise_gate --self-test` passes 235 of 235, including its end-to-end git arms.

## Head

b3c1d0477e63815c23b707b08656086dea8526d6. It adds one commit to 3172a36ca (the merge of origin/main 07a09406a into the branch, 2026-10-18), and that commit only records the two new harnesses in `tests/closures.json` (`python3 tools/pr/ci_predict.py --apply-inert`). The figures below were taken at 3172a36ca except where marked; no code changed after it.

## Mutation proof

`bash dev/audit/harnesses/r10_train_raise_hold_mutants.sh` (each mutant removes one predicate, runs both self-tests, restores). Run at 3a334c65f for R1 and at dad8e723c/570311da9 for the rest, whose code those mutants touch is unchanged at the head:

- P1 (the defect: `raises = raises or [budget paths]`): merge_train FAIL "#2401's shape: a budget file that only gains rows is no raise ..." and "... with #2401's own reviews ... it still merges"; pre-flight FAIL "#2401's shape ... passes with no owner review" and "... reads no body".
- J1 (drop `justify=`): merge_train FAIL "#2209's shape MUTATION (the gate's own justification)" and "a planted raise ... deficient ... naming the raise and BOTH missing lines"; pre-flight FAIL "a planted raise ... deficient ... PARKS" and "a planted raise whose body cannot be read PARKS".
- W1 (Stop without `why`): merge_train FAIL "... BOTH missing lines", "a planted raise with no owner review stops, and the Stop carries the gate's why", "... the mandate is judged AT THE MERGE".
- H1 (a held raise ignored): merge_train FAIL both "#2209's shape (approval-carry on/off)", "approval-carry with no recarry ...", "a planted raise with a healthy body under the mandate in force lands as the owner's".
- U1 (no unseen-path check): merge_train FAIL "fail closed: a budget path the diff names that neither tree holds is a Stop".
- R1 (a failed read returns its text): merge_train FAIL "fail closed: a budget blob the tree lists but git cannot read is a Stop even under the owner's approval". It survived the first drive, masked by U1 on the ls-tree path; that arm was added in 3a334c65f, and it is killed there.
- T1 (mandate judged at review, not merge): merge_train FAIL "... the mandate is judged AT THE MERGE, not at the review".
- B1 (body read before the raise branch): pre-flight FAIL "... and reads no body: the justification is read on the raise branch only".
- Q1 (pre-flight ignores `held`): pre-flight FAIL "a budget raise without the owner's review ... PARKS", "a budget raise whose mandate was revoked PARKS", "a planted raise ... deficient ... PARKS".
- The agreement pair: with P1 planted, `python3 -I tools/policy/agreement_py.py --out F && node tools/policy/agreement.mjs --py-json F` prints `pair budget-raise: 2 readers, 56 items, 20 divergent` and exits 1. Restored, 0 divergent.
- merge_pr.sh, by hand at 0ed4aceb2. Each mutant is a python replace, run with `bash tools/audit/seat/merge_pr.sh --self-test`, then restored from the index:
  - D1 (the draft guard → `true`): FAIL "a draft refuses without --ready".
  - D2 (no ready owed): FAIL "... and owes the ready mark".
  - M1 (mandate refusal → `|| true`): FAIL "owner mode under an expired mandate refuses" and "... a mandate that does not exist refuses".
  - M2 (id guard → `|| true`): FAIL "owner mode with no --mandate refuses, never a default" and "... a non-id --mandate refuses".
  - B1' (body without `mandate %s`): FAIL "the owner body declares an agent and cites exactly the mandate given".
  - M3, the separate empty-id guard, survived as redundant with M2's regex. It was deleted rather than kept as dead code.

## Null control

- Unmutated, at the head: merge_train 189 of 189, pre-flight 36 of 36, merge_pr 12 of 12.
- Before the fix (the arms at dad8e723c^ code with the new tests): merge_train 187 checks with 6 failed, all new arms. Pre-flight 36 checks with 7 failed: 4 new arms, plus 3 existing budget arms reworded to approve's step and wording.
- `#2311`, a real raise with a healthy body and an owner review, holds under both the old reading and the new one (the RCA demonstration table, last control row). The fix does not loosen a real raise.
- The replay's control is a real raise that still stops at the head: `python3 dev/audit/harnesses/r10_train_raise_hold_replay.py 2401:176851e950a8bea29b0c06f1891b8ce4b83b8836 2373 2368`. #2368 prints `2 raise(s), STOPS ... coverage_floor_override.calls_floor: None -> 6 ... no decisive review`.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test`: 189 checks, 0 failed (the baseline at 176851e95 was 180).
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: 36 checks, 0 failed (baseline 32).
- `python3 tools/policy/budget_raise_gate.py --self-test`: 235 checks, 0 failed (baseline 235).
- `bash tools/audit/seat/merge_pr.sh --self-test`: 12 checks, 0 failed (new).
- `python3 tools/audit/seat/proof_watch.py --self-test`: 34 checks, 0 failed.
- `python3 -I tools/policy/agreement_py.py --out F && node tools/policy/agreement.mjs --py-json F`: `pair budget-raise: 2 readers, 56 items, 0 divergent`, `AGREEMENT ok`. The rule: 7 tracked budget files × 8 edits.
- `node tools/policy/agreement.mjs --self-test`: 13 of 13 probes held.
- `python3 dev/audit/harnesses/r10_train_raise_hold_replay.py 2401:176851e950a8bea29b0c06f1891b8ce4b83b8836 2373 2368`: the live readings.
  - #2401 (merged since, at 07a09406a; read against its pre-merge base) and #2373 print `path : RAISE` against `gate : 0 raise(s), HOLDS`.
  - #2368 prints `path : RAISE` against `gate : 2 raise(s), STOPS`.
  - On the RCA's evidence the old path reading is wrong on 2 of these 3 rows.
- The RCA's own demonstration (`demo.py` + `cases_all.py`, demo.out sha1 fa78eecc28a5) is the root-cause seat's. It stays out of the tree, as the replay harness above re-derives its live rows.
- The class seams (step 8). The rule is `git grep -n '_budgets.json' -- 'tools/audit/seat/*.py' 'tools/audit/*.py' 'tools/policy/*.py'`; every site it returns:
  - merge_train approve and queue_pre_flight: closed here (only docstrings and fixtures remain).
  - merge_train `raise_hold`'s cheap no-budget-file test (through `g.SUFFIX`): exact, because an unchanged file has equal text, so `file_raises` returns nothing.
  - merge_fastpath `file_class` SERIAL routing: a routing, not a raise reading (declared in the agreement pair's `what` and in the batch docstring).
  - orchestrator_tick: reads `tests/ci_budgets.json`'s critical-path value, not a raise reading.
  - budget_raise_gate `SUFFIX` and SCHEMA: the owner.
- `python3 tools/audit/fold_ledger.py check`: 0 violations.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`: ALL 109 HARNESS HEADER CHECKS PASSED.
- `python3 tools/pr/ci_predict.py`: no closures or fast red predicted against 07a09406a1cc, at b3c1d0477.
- `PYTHONPATH=tests/hastub python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED`, runs `tests/entities.py`. It is heavy, so it is left to CI (heavy-to-ci); cite its check-run at the head.
- Architecture score: n/a. No `custom_components/` file changes.

## Unpinned sites

n/a: the diff adds no production (`custom_components/`) line; the mutation lane's scope excludes `tools/`, which is why the harness above carries the proof.

## Red checks

none known at the head; CI not yet run on it.

## Forward-carry

- `tools/audit/seat/INSTRUMENTS.md` (merge_pr.sh's `--mandate` and `--ready`).
- `dev/audit/config/bugclasses.json` I4 `barrier` (the `budget-raise` pair, and that its train reader is the PR's copy).
- Not carried: merge_pr.sh's self-test is not wired into a workflow. `.github/workflows/` is code-owned, so wiring it is the orchestrator's to dispatch: `bash tools/audit/seat/merge_pr.sh --self-test` beside `train.sh --self-test` in governance.yml.

## Friction

none
