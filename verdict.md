Fix review: merge 6353b624ff2f3c049bc0762df0fba889f60cac95

bus-nonce: 112258ff763c8ddf52662c8bc34bb98a

Round 2 of this review (delta round). Measured head `6353b624ff2f3c049bc0762df0fba889f60cac95`, merge base `5fb8339304e10b2b1416d9c439587ae1806d820e`, from a detached worktree at the head. Before writing, `git ls-remote origin refs/pull/2852/head` still returned `6353b624ff2f3c049bc0762df0fba889f60cac95` (`ev/head_reread.txt`). The role files and finding-propagation.md on origin/main (`510787b76`) match the head's merge base.

## Block

none

## Findings

none

## Evidence

- Round-1 block (carry-missing) is resolved. The body's three `## Forward-carry` items all name `Carry: R10-RECORD-API-O1` at roster `62b01c7a96203df31282eefed66dae94304f6333`. That commit exists and is an ancestor of origin/handoff/audit-r10-roster. In `dev/programme/rosters/wave-r10-groups.json`, both there and at the roster tip, R10-RECORD-API-O1 is a live group: `resume.stage: not-started`, `after: [R10-RCA-RATELIMIT-RECUR]`. It is distinct from the group this PR closes. Its `carry` list holds three entries, each prefixed `From #2852 (...)`:
  - Carry 1 is the O-1/M3 decision. It states its precondition (met by measurement) and a control: demand counts as record + enumerate + rest, `record_burst_replay.py` underreads, both harnesses are named with expected counts, and a null control is given. It also tells the dispatching seat to re-measure at its own merge base.
  - Carry 2 is the second M0 pair around the enumerate step, with its control and a re-measure instruction.
  - Carry 3 is the ref_privacy home-match instrument finding, with its control.
  So the destination is a stage that will act, and each item carries its control as a precondition, as fix-review.md step 10 and finding-propagation.md require. The question the brief raised, whether "the seat that dispatches O-1" is an acceptable destination, does not arise: the orchestrator has since minted a roster group for it (`ev/roster_carry_check.txt`). `python3 tools/audit/carry_audit.py pr 2852` prints `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`. All four resolve to R10-RECORD-API-O1 on origin/handoff/audit-r10-roster: the three body items plus round-1 review item bcdde943 (`ev/carry_audit.txt`).
- The round-1 finding on record section 3 is corrected. `git grep -l -E "describe.*--tags|--match.*v\*" b281d0325 -- '*.py' '*.mjs' '*.sh'` returns exactly the 7 files the record now lists (`ev/class_rule2_b281.txt`). I checked each disposition:
  - sweep.mjs's `gh()` helper runs `execFileSync('gh', ['api', ...])` (sweep.mjs:133–136). The record now calls it an API reader. Its only CI call is `--self-test` (governance.yml:322), as stated.
  - agreement_py.py runs in CI as `--self-test` and `--restore` (governance.yml:538/542), plus `--out` at governance.yml:1184. None of the three calls walks the window.
  - tests/delivery_status.py's `_gh` (line 491) has no caller.
  - The delivery-status step "Regenerate the ledger and put it in #201's region" makes one `gh issue view 201` and at most one `gh issue edit 201`. That is two fixed calls, as the record now says.
  - No workflow names conformance.py, report_step_driver.py or record_api_calls.sh.
- At the head, the same rule returns 8 files (`ev/class_rule2_head.txt`). The 8th is this PR's own `dev/audit/harnesses/enumerate_api_calls.py`. It answers from a logging stub ("no request leaves the host"), and no workflow names it (`git grep -c` over `.github` returns nothing). The record pins the rule to `b281d0325`, so its list of 7 is correct as written. The added file is an offline harness, not a CI reader, so the class stays closed.
- The delta moved none of the round-1 evidence. `git diff --stat 23e6f7130 6353b624` over record_row.py, enumerate_api_calls.py, delivery/2852.md and the record shows only `dev/audit/rca/ratelimit-recur.md` (24+/6−, section 3 only). Every other path in that two-commit diff comes from main's own merges. The three-dot diff against the merge base is still the same 5 files: record, harness, delivery row, `tests/closures.json` (the one INERT entry for enumerate_api_calls.py) and record_row.py. VERSION, the manifest, RELEASE_NOTES.md, both claim files and `.github/` are untouched (`ev/scope.txt`). Round 1's cause attribution, per-push counts, ledger, M4 at both ends and cost test therefore stand as measured at `23e6f7130`.
- I re-ran the mutation proof at this head. `python3 tools/audit/seat/record_row.py --self-test` prints `record_row self-test: all checks passed`, rc 0. I then reverted line 938 `pr = matched[0]` to `pr = _api(repo, f"/pulls/{matched[0]['number']}", token)`. With that change it prints `1 self-test check(s) failed: enumerate_merges reads one map per merge and nothing else`, rc 1. I restored the file and the worktree is clean (`ev/selftest_head.txt`, `ev/selftest_mutant.txt`).
- Merge: `git merge-tree --write-tree origin/main 6353b624` exits 0 against origin/main `510787b76`, so there are no conflicts and no claim-driver lines (`ev/merge_tree.txt`).
- CI on the head, from the check-runs API: 68 runs, every one completed success or skipped, and none red. gate succeeded in all three runs. pr-contract last ran 09:18:02–09:18:43Z, after the body edit, and passed. The body's `## Red checks: none` matches (`ev/check_runs_summary.txt`). `tests / mutation` is green. I did not read its log, because this delta adds no production code line.
- `## Head` names `6353b624ff2f3c049bc0762df0fba889f60cac95` and states that it is the code head `bcacef98c` merged with origin/main `5fb833930`. That matches `git log origin/main..6353b624`.
- Figures I did not re-derive in this round: the scan of 43 bucket-hours, the 91-merge figure and the 17.0-min recovery. Round 1 could not re-derive them either, and this delta does not touch them.
