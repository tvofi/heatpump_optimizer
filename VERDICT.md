Fix review: merge 3dd5a3556fde58a9bc46961ef19e6724e2b6d567

bus-nonce: 5f8927dccc38fbf64fca5142a6b89001

## Summary

First round of review. The head reviewed is 3dd5a3556fde58a9bc46961ef19e6724e2b6d567, which is still `refs/pull/3302/head` at verdict time. The base is 7c9c4c154cda514f938fd503cde2779716caf251 and origin/main is e36e5327d. The check is the three-dot diff. The role files are current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

The finder's recording reproduces at the head:
- `tests / arch-instrument` reads no row.
- policy_lint, the reader shared by the other three lanes, opens every row.
- The control lane reproduces its expected RESULT.

The row-blind rule ignores only the pull request's own row, and every null control holds. The transition path fails closed, and LANE_GATE drift at the job level is pinned by mutation. The runner-minute figure is not claimed beyond what was measured. One surviving mutant on the ci.yml call-site wiring is carried below. It is not a block: it is outside the job text that the body's pin covers, and a push to main still runs every lane.

## Findings

- Follow-up: R8 survives the self-test. If ci.yml's `machinery:` lines (190 and 216) pass `needs.prelude.outputs.machinery_rowblind` into tests.yml and governance.yml, the three row-reading lanes would idle on a package-plus-own-row pull request, and `prelude.py --self-test` still prints 76 checks, 0 failed (ev/R8-ci-wiring.diff). `lane_gates` pins only the callee job's text, so the body's sentence "A lane that reads rows therefore cannot drift to the row-blind input unseen" holds for the workflow jobs, not for the ci.yml call sites. The harm is bounded: a push to main forces machinery=true, so main runs the lane within one merge. Countermeasure: extend `lane_gates` to read ci.yml's `with:` mapping of each called workflow, `machinery` to `outputs.machinery` and `machinery_rowblind` to `outputs.machinery_rowblind`. Carry: R10-CI-EDIT-RUNNER

## Evidence

- RESULT arch_instrument_rows_read=0. `python3 dev/audit/harnesses/lane_reads_delivery.py --lanes arch-instrument --out <dir>` at the head printed `lane arch-instrument: 3 run step(s), 2 uses: step(s) listed, 0 exited non-zero, 533882 trace lines, 0 step(s) read a row, 1011 s`, rc=0 (ev/arch-instrument-recording.tail.txt). This matches the recording.json verdict `reads no row`.
- RESULT control_hits=3 copy_reader=True fixture_reader=False. `--lanes control` at the head reproduced the line the body quotes (ev/control.log).
- RESULT policy_lint_reads_rows=yes. Under `strace -f -e openat,getdents64`, `node tools/policy/policy_lint.mjs` at the head produced 358820 trace lines naming dev/programme/delivery and opened each row, e.g. 1059.md and 1065.md (ev/policy_lint_strace.txt). policy_lint is the reader the recording names for closures, env-matrix and instrument-self-tests. I did not re-run those three full lanes: instrument-self-tests alone has about 100 steps. I re-derived the shared reader only. The committed recording's verdicts for those lanes are the fixer's measurement, cross-checked by this trace, not re-taken lane by lane.
- Self-test at the head: `python3 tools/ci/prelude.py --self-test` prints `76 checks, 0 failed`, matching the body.
- Null controls, read in the self-test and live under the mutants:
  - Another pull request's row runs the lanes. R5, which exempts every row, is killed by two checks.
  - A row when the event names no number runs the lanes, and so does the own row alone.
  - An empty or unread list runs the lanes, and so does an unreadable script table.
  - Product plus another row runs both lanes, and a push runs both.
  - Product plus a tools/ file plus the own row runs the lanes.
  - A product-only pull request idles both outputs, which matches the pre-existing C7(a) behaviour.
- Mutants, all mine (ev/mutants.txt): R1, R2, R3, R5 and R7 are killed. R4 survives in the fail-safe direction: arch-instrument gets the strict output, which loses only the saving. R6 survives as an equivalent mutant: the isdigit guard only stops `delivery/.md` from being the own row, a name no real row has. R8 is under Findings. The body's M1 to M5 match R5, R7 and R1-class kills of my own.
- Transition: ci.yml:120 checks out `tools/ci/*.py` from the base before the prelude runs, so the base prelude emits no `machinery_rowblind`. tests.yml declares the input with `default: ""` and every arch-instrument step tests `!= 'false'`, so it runs. This matches CI at this head: `tests / arch-instrument` concluded success and was not idled.
- The PR number fed in is the one `derive(ctx)` returns (prelude.py:343, :353). On a non-pull_request event both outputs are forced to "true".
- Runner minutes: the body says the brief's 1,380 runner-minutes a day does not carry over, and claims no re-measured figure. That is honest: no number is claimed beyond what was measured.
- Repair round (`tests / fast (3.14)` red): at the head, `harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED` and `inline_scan()` exits 0 (ev/cheap-checks.txt). The body answers the red check with a cheaper detector (inline_scan, 0.7 s), names prepr.sh as where the countermeasure would go, and dismisses building it as out of this group's scope. That satisfies step 11's requirement that the red be answered. `pr-contract / pr-contract` is success at the head.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. No budget file is touched, and the closures.json change only adds the new harness to harness_headers' inert reads.
- Untouched at the head: VERSION, the manifest version, RELEASE_NOTES.md, tests/golden/claimed_drift.txt and card_claimed_drift.txt. No claim is owed.
- Merge: `git merge-tree --write-tree origin/main HEAD` exits 0 (ev/merge-tree.txt). It prints `LEDGER-MERGE: resolved tests/closures.json`, a set merge of inert_reads, with no conflict.
- CI: `merge_train.py classify 3dd5a3556fde58a9bc46961ef19e6724e2b6d567 --pr 3302` prints `GREEN ... pending: none red: none`, rc=0 (ev/classify.txt). The review packet's digest lists every check run at the head; none is red.
- Architecture: the change is confined to the C7(a) functions (`machinery`, a new `LANE_GATE` table and `lane_gates`) and the arch-instrument step gates. That matches the brief's overlap note about R10-CI-EDIT-RUNNER. The split follows the recording rather than a guess, as the brief required.
- Figures I could not re-derive: the per-lane verdicts for closures, env-matrix and instrument-self-tests, and `--refresh-index`'s `open=128508 list=18`, were not re-taken lane by lane; see the policy_lint line above. The 19-mutant/5-survivor `mutant_run.py` count was not re-run either, because CI's heavy runs are cited rather than repeated. The `tests / mutation` check at the head is success.
