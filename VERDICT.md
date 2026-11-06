Fix review: blocked 84a7c456f2a682f76e285921c26d4b05044391e6 beyond-card: C7c pins_due skips mutation-pins on a non-product delta though the previous head's pins never completed, in 3 of 3 skips in the PR's own sample

bus-nonce: 743943f24c6bbb6c163fd2a7caafff24

Round 1 (first-round fix review of R10-CI-SLIM, PR #3230). Measured head 84a7c456f2a682f76e285921c26d4b05044391e6, a merge commit whose tree is identical to the authored head 4ae9f7596 (`git diff --stat 4ae9f7596 84a7c456f` is empty). Merge base 785c2b604. The role files are current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Block

**C7(c) skips measurements that never happened.** `prelude.pins_due` gates `tests / mutation-pins` and `tests / mutation-autofix` on the push's own delta (`before...head`). Its docstring states the premise: "the sites still unpinned were measured at the head before". The rule never checks that premise. Cancel-superseded cancels a previous head's run, and its pins shards with it. When the next push is non-product (a delivery row, a body fix-up, a tooling commit), those sites go unmeasured.

Measurement, on the PR's own recorded sample (`dev/audit/harnesses/r10_ci_slim/sample.json`, my script `ev/c7c_probe.py`, output `ev/c7c_probe.txt`, `ev/c7c_three_runs.txt`):
- C7(c) changes behaviour only where `pins_due` is False AND `tests / mutation` failed, because the pins job's `if:` already needs a failed `mutation`. That is 3 runs, which are the body's "3 runs" and its whole 479-minute saving (re-derived: `ev/c7_replay_head.txt`).
- In all 3, the previous head's survivors were never pinned:
  - PR 3219, run 41937668180: the previous run 41937637106 had `tests / mutation-pins` **cancelled**. Its own pins succeeded in reality, and that was the only completed measurement of those sites. C7(c) removes it.
  - PR 3220, run 41951544787: the previous run 41951503566 had pins **cancelled**. Its own 7 pin shards succeeded, the only completed measurement. C7(c) removes it.
  - PR 3219, run 41951472711: the previous run's pins succeeded, but its autofix **failed**, so nothing was pinned.
- Control: runs where `pins_due` is True keep today's behaviour by construction. The planted production defect below shows `pins_due` True on a product diff at the head.

Consequence: at such a head, `mutation` stays red with no pins table and no autofix. The seat cannot re-trigger the measurement. A dispatch never runs pins (`github.event_name == 'pull_request'`), and an empty commit or a close-and-reopen is forbidden. Only a later push touching the package does. This does not weaken production quality, because `mutation` still fails closed. It is a throughput risk: in this window every C7(c) skip hits it.

Card sentence it contradicts: C7 (c) "mutation-pins runs once when the PR is review-ready, not at every head", with the accepted risk "(c) A survivor is found at review-ready instead of per head". The implementation guarantees no single measurement. A survivor whose only measurement was superseded is not found at review-ready or at any later non-product head. That goes beyond the card.

Minimal sound repair (the fixer's call): `pins_due` is False only when the head the delta starts from actually concluded `mutation-pins` (success, or skipped because `mutation` passed). Otherwise, measure. Equivalently, take the delta from the last head whose pins concluded, not from `before`. Add a self-test whose previous head's pins were cancelled. Re-run `c7_replay.py`: on this sample (c)'s saving becomes 0, so report it honestly.

## Owner constraint

Each change, the production path it touches, and the check that still guards it:
- **C2** (`tests/ci_ratchet.py`, `tests/ci_budgets.json`, `budget_raise_gate.py`): no production path. Every other ci_budgets row is still graded at zero tolerance (the body's planted `script_runs_per_push` 54 -> 55 is GREW at the head). This is an owner-approved loosening under card C2 as written. The body states the acceptable risk.
- **C3** (`prelude.defer_to`, `gate.deferring`, ci.yml `WORKSET`): no production path is skipped. The code run's gate still judges every production unit, and its `pr-contract` reads the latest body. This matches card C3 option A. No opus review dispatch is touched.
- **C7(a)** (`prelude.machinery`; arch-instrument, the closures recording, env-matrix and instrument-self-tests stand down on an all-product PR): these lanes measure machinery. `tests / fast`, `tests / mutation`, goldens, features, CodeQL and review still run on a production diff.
- **C7(b)** (`codeql_scope.ANALYZED_PREFIXES`): any PR reaching `custom_components/` or `.github/` analyzes as before, and every push to main analyzes. This matches the card as written.
- **C7(c)**: production code is still guarded by the required `tests / mutation`. The defect is the throughput risk under `## Block`, not a weaker production check.
- **Planted production defect** (`ev/planted_defect.txt`): `total += v * seconds` -> `* 2` at `custom_components/heatpump_optimizer/open_meteo.py:156`.
  - At the head, `tests/solar_alignment.py` gives rc=1, 5 CHECK(S) FAILED. Every CodeQL leg reads `analyze`, `machinery` is False (only machinery lanes idle) and `pins_due` is True.
  - Null control at origin/main 750a6001a: the same rc=1, 5 CHECK(S) FAILED, with every leg `analyze`. Production refusal is unchanged.
- The body states, per change, why the risk is acceptable, with a before and after: yes, for C2, C3, C7a, C7b and C7c. C7c's statement rests on the premise refuted above.

## Findings

- C7(b) figure not re-derivable as quoted. The body reads "105 analyzed legs now skipped; 2955 -> 1797, saving 1159 (4.1%)" with 27 diffs unreadable. At this head with full history, `c7_replay.py` reads 0 unreadable, "150 analyzed legs now skipped: 2955 -> 1764 (saving 1191, 4.2%)". The fixer should retake the figure with every diff readable when re-cutting. Carry: R10-CI-SLIM
- C7(a)'s product set counts every test script `tests/closures.json` measures as product, so a PR that edits a measured script and the package idles the closures recording. A closure that edit under-approximates is caught only by main's forced-full push, as CLAUDE.md rule 1 designs. Card C7's POLICY line foresees this change to the gate-scoping contract, so it is not a block. Carry: dismissed: card C7 POLICY foresees it; rule 1's main push is the backstop
- The body names a cheaper detector for last round's `tests / fast` red: harness_headers' depth-seam scan, absent from `prepr.sh`. It leaves the contract change to the owner. Carry: dismissed: answered in the body as defect-root-cause.md requires; the contract edit is the owner's

## Evidence

- RESULT mutation proof (`ev/mutants.txt`): six mutants, each restored after the run, each killed.
  - C2 `if key in REPORT_ONLY:` -> `if False:`: 2 of 65 failed.
  - C3 `bound = 0` -> no-op: 1 of 57 failed.
  - C3 `defer_to` branch -> `if False:`: 3 of 70 failed.
  - C7b `ANALYZED_PREFIXES` skip -> `if False:`: 2 of 94 failed.
  - C7c `pins_due` -> `return True`: 2 of 70 failed.
  - C7a `machinery` -> `return True`: 3 of 70 failed.
  - Every count matches the body.
- RESULT self-tests at the head (`ev/checks.txt`): ci_ratchet 65/0, budget_raise_gate 273/0, prelude 70/0, gate 57/0, codeql_scope 94/0.
- RESULT gate satisfiability (`ev/checks.txt`): `gate_satisfiable.py` reads GATE SATISFIABLE. The production-only, machinery-only and mixed diffs each give gate PASS. The job-level null control gives FAIL SKIPPED. No required name ends SKIPPED.
- RESULT C3 (`ev/edit_runs_head.txt`): 127 runs, 117 deferred, 4438 -> 660 job-minutes, as the body says. Null control: 156 code runs, 20 deferred, saving 13.
- RESULT C7(c) (`ev/c7_replay_head.txt`): 3 runs, 2234 -> 1756 (479), as the body says. (a): 0 idled, as the body says.
- `git merge-tree --write-tree origin/main HEAD` rc=0, so it merges cleanly with origin/main 750a6001a.
- Claim files are byte-identical to origin/main. VERSION, the manifest and RELEASE_NOTES are untouched (three-dot, empty). `tests/structure.py` passes.
- Budget-raise gate: `RAISE tests/ci_budgets.json: critical_path_minutes_band: 1.3 -> None`, `RESULT budget_raises=1 count`. This is the one C2 loosening the owner approved, stated under `## Raise justification`. Its red waits on tvofi's review.
- CI at this head (`ev/classify.txt`): `merge_train.py classify` rc=1, `RED 84a7c456f2a682f76e285921c26d4b05044391e6 pending: none red: gate`.
  - The gate job 127668840956 and job 127667663510 log one reason: `FAIL budget-raise-gate / budget-raise-gate: failure (run 42145816190)`. That is the approval-owed C2 loosening, so in substance this head is APPROVAL-OWED, although classify printed RED (rc=1), not rc=4.
  - All 55 check runs were read (one page; page 2 is empty). Every other required unit is success: fast, coverage, closures, arch-instrument, mutation, browser, typing, briefs, closure-scope, the three CodeQL legs, env-matrix, policy-docs, hassfest, validate, arch-score and pr-contract.
  - `tests / nightly-status` is red: main's slow lane, not this diff. The body measures it unchanged at both ends.
  - `pr-contract` (job 127668247900) started 02:16:37Z, after the last red to conclude (budget-raise-gate, 02:16:08Z), and is green. So the body answers each red, as rule 11 requires.
- I built `ev/c7c_probe.py` myself. It is not the finder's harness: this group names none (packet: "Finder's harness: none named").
