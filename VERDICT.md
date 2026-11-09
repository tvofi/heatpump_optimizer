Fix review: blocked 18656e4c23a664ca9c58de75f3c5589078631a1c ci-red: gate: the older gate suite (run 42536799957, kind edit, 00:01Z) is red "still being judged" and merge_train classify keeps the worst suite; the body answers neither it nor why it is benign

bus-nonce: d32bf28dc7db8ac6ad167210f3bedbd1

Round 1 for this PR in this seat. Head measured: 18656e4c23a664ca9c58de75f3c5589078631a1c (still the PR head at 00:3xZ per ls-remote refs/pull/3352/head). The substance of the PR (RCA record, class row, detector) reads sound; the block is the head's CI state, which the next head or a rerun of that gate job clears.

## Block

- `python3 tools/audit/seat/merge_train.py classify 18656e4c23a664ca9c58de75f3c5589078631a1c --pr 3352` exits 1: "RED ... pending: none red: gate" (re-run four times over ~25 min, same line). Cause read in the job log: run 42536799957's `gate` (WORKSET arch-score budget-raise-gate, KIND edit) printed "FAIL run(s) [42536798615] at this head are still being judged; their gate decides" at 00:01Z and was never re-run. The code run 42536798615's own `gate` (id 128911681714) is success at 00:22Z, `pr-contract / pr-contract` (128911383206) is success at 00:21Z, and every other required job in the packet is success or skipped. `latest_runs` keeps the worst gate suite by design (A5), so the stale deferral red stands.
- Role step 11: this red is not in the body's `## Red checks` (which answers the 22:05 cancellation at fae447091 only). It is a premature-deferral red from a second workflow run. Cheaper detector: none (the gate line names the cause); the body should say so. Re-running the failed 42536799957 gate job (or a new head) and one line in the body clears this block. I read it as `root-cause-unanswered`, not a branch defect.

## Findings

- Surviving mutant in the detector's null control: inverting the LATE test (`flag = lag is not None and lag > a.limit` to `<`) leaves `--self-test` at rc 0, because self_test() asserts only the lag values (2, 40, None) and never the LATE flag or the exit code. The body and the RCA say the control shows "LATE at 15m / red on the defect"; that claim is printed, not tested. The detector is unwired, so this has no live effect today. Carry: dismissed: detector is unwired and its wiring is an owner/fixer proposal in the RCA (section 5.3); the control is to cover the flag and exit code when it is wired.
- Figure not re-derivable: the body's lag table (9 LATE of 10 carried, 4 uncarried, 717..9 min, #3308 at 61 min) is a sliding-window reading at 2026-11-08T10:24Z. Re-run at this head it prints 22 LATE and 6 uncarried-or-ok rows in the visible tail (ev/lag-table.txt); #3308 and the other named rows are not in my window, so the 61 min figure is not re-derived. The body says as much. Carry: dismissed: body already marks it a sliding window and an upper bound.
- Body says the scoped gate is "0 script(s) run, 33 scoped out"; against the merge base `closure.py select` here selects `tests/entities.py` ("1 script(s) run, 32 scoped out"), which is expected for a new tracked file. Not a defect. Carry: dismissed: count differs only because the base moved.

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main 18656e4c23a664ca9c58de75f3c5589078631a1c` rc 0 (tree 5dbe97236), no conflict, no MERGE-CLAIM lines.
- VERSION, manifest version, RELEASE_NOTES heading: not in the three-dot diff.
- `bugclasses.json` parses; `python3 tools/audit/fold_ledger.py check` prints "fold_ledger: 0 violation(s)"; `node tools/policy/agreement.mjs` prints divergent=0 refused=6 here, the same six refusals (no --py-json) at the merge base, so not this PR's.
- `--self-test`: "self-test ok: fast=2m (green), slow=40m (LATE at 15m), never=uncarried (not scored)" (ev/selftest.txt). Mutants in ev/mutants.txt: 2 of 3 killed, the LATE-flag mutant survives.
- Mutation proof and finder's harness: none named, no production code line changed (the PR says n/a); mutation lane success, no ledger diff. Forward-carry: body says none; the RCA's proposals name no later stage. Class-rule enumeration: not applicable, no seam fix.
- Claim files and goldens: untouched in the diff. Budgets: none touched; `budget-raise-gate` and `arch-score` success.
- CI at the head: gate (code run) success, pr-contract success, tests/fast, coverage, mutation, browser, typing, closures-completed per the later poll, codeql, hassfest, validate, governance jobs success; the red is the 00:01Z gate in run 42536799957 only.
- Not run by me: the full gate and mutation table (cited from CI, per role).
