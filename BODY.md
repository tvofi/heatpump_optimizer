Hotfix part 1 of R10-HOTFIX-SELFTEST-SCOPE-UNION (P584, triage batch 169). Main a7628041dc is red on governance / instrument-self-tests step `drift`, with 6 UNDER-SCOPED refusals (job 130352715261, run 42968587919). This PR adds each measured miss to its existing entry in `tools/ci/selftest_closures.json`, as diagnosis section 5 lists them. It is a union written through `selftest_scope.write_table`. Prepr's `tools/policy/fixtures/required-contexts.json` and git `fetch` stay, and no other entry moves. Part 2 (`record` union, the pre-merge detector, and whether drift can run on pull_request) is a separate later seat. This diff touches neither `selftest_scope.py` nor `governance.yml`.

The drift step runs only on a Linux main push under strace, so it cannot run before the merge. The proof below runs the production predicate `selftest_scope.drift()` instead. It takes the measurement to be the base entry plus the diagnosis's measured ADD set, with prepr's REM applied as the artifact shows. Against the base table, `drift()` prints the same 6 lines as main's log. Against this head, it prints none.

The diagnosis also orders `prepr git += branch`, and that line is applied. `drift()` compares only `files`, `probes`, `dirs`, `index` and `objects`, never `git` (selftest_scope.py, `drift`). The `git` field is written by `fold`/`record` and is read by no gate, so this one line is recorded state that no check pins. Its mutant survives, as shown below.

## Head

532b51350bdd2dc8cc5e6cf4221f2714c4500e4a (origin/main a7628041dc02e298c5399003d4c0576391dd5c4e, which is also this branch's merge base; measured 2026-11-11T07:20:51Z).

## Mutation proof

Each of the 9 added items was removed from the head table one at a time, and `drift()` was rerun with the measurement described above (scratch driver, printed below). 8 of 9 are KILLED, and each prints exactly its own main-log line, e.g. `UNDER-SCOPED step prepr: files misses ['tests/env_drift.py']`. The `-prepr.git:branch` mutant SURVIVED because `drift` reads no `git` field, as disclosed above. Removing all 9 at once is the base table, which prints the 6 refusals (see Null control).

    for each (step, field, item) in the 9 additions:
        t = deepcopy(head); t["steps"][step][field].remove(item)
        drift(t, measured, workflow_steps(Path("."))) restricted to the 6 steps

## Null control

- The unmodified table at the base, judged by the same `drift()` call, gives `drift@base: 6 refusal(s) over the 6 steps`. Those are the 6 UNDER-SCOPED lines of main's job log, verbatim. The head gives `drift@head: 0 refusal(s)`.
- Untouched entries: `105/105 untouched entries identical`, compared by canonical JSON. The step-id sets of base and head are equal.
- Set check, for each of the 7 (step, field) pairs: diagnosis ADD set minus the head entry is `[]`, and minus the base entry is the full ADD list.

## Figures

- `git diff --stat origin/main...HEAD`: 1 file, 9 insertions, 0 deletions.
- `python3 -I tools/ci/selftest_scope.py static`: `111 gated step(s), 0 problem(s)`.
- `python3 -I tools/ci/selftest_scope.py --self-test`: `117 checks, 0 failed` (strace-dependent checks skip off a traced host).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Gate scope (`tests/closure.py select`): `MODE: FULL`, because the table is a gate file. Left to CI per fixer.md step 5.
- Drift proof and mutants: a scratch driver, not in the tree, because this seat's scope is the JSON alone. It imports `tools/ci/selftest_scope`, loads the base table with `git show origin/main:tools/ci/selftest_closures.json`, and calls `load_table`, `workflow_steps` and `drift` as described above.
- Class seams: diagnosis section 5's artifact-minus-table set diff over the 6 steps is the enumerating rule. Every seam it returns is closed in this diff, except prepr's REM (`required-contexts.json`, `fetch`), which is deliberately kept per the brief: it is an over-scoped note, not a refusal. The final proof is the next main push's drift step printing `0 refusal(s)`.

## Red checks

none

## Forward-carry

none

## Friction

none
