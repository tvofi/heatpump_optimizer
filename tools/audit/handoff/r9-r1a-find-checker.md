_Requested by **tvofi**_

Readiness PR R1a of audit round 9 (the round-9 plan, section 3, row R1, first half). It lands what the find driver (R1, stacked on this branch as `handoff/r9-r1-find-driver`) is graded against, because `wave-script` restores `.claude/workflows/check-wave-script.mjs` from the pull request's **base** before it grades (decision 0013; `governance.yml`, "Restore the check source from the base commit"). The base checker pins `planSeats`, `WAVES`, a 19-seat round 9 and D5 off in round 9, so a scopes-driven driver proposed against it is red on a required context whatever it does. This pull request teaches the checker the scoped shape first; the driver's pull request is then graded by this checker and drops the `planSeats` arm.

- `tools/audit/scopes.json` and `tools/audit/check_scopes.py` move in-tree from the plan's folder. `scopes.json` is byte-identical to the plan's copy. `check_scopes.py` gains `--seat <D<k>-s<n>>`, which prints one seat's cells with `rest` resolved, so a finder is handed files rather than a rule; its default output at a ref is byte-identical to the plan copy's.
- `tools/audit/finding.schema.json`: a finding requires `scope` (its seat, `^D<k>-s<n>$`) and `class_guess`, an enum of exactly the `bugclasses.json` ids plus `new`. That is a design choice: a class the judge adds must land in both files in one pull request, and the checker fails until it does; a report requires `leads`, each `{owner_seat, file, symbol, what}`, the scope wall `COMMON.md` already states (merged in #1627).
- `check-wave-script.mjs`: two blocks that run whichever driver is on the tree (the finder report schema; the scopes held to every brief's numbered steps through `tools/audit/rotation.json`), and `the scoped round driver`, which runs only when `audit-find.js` carries a `DISPATCH:BEGIN` block. The existing `planSeats` pins run only while it does not, unchanged, and the ledger-vs-briefs half of `the rotation` now runs for both.

Both new files sit under the `tools/audit/` prefix `tests/closure.py` lists `INERT`, so no classification edit is owed: `closure.is_inert` returns True for both and `orphan_files()` is empty (Figures).

Not policy: no file here is under a `CODEOWNERS` pattern. The delivery row `docs/delivery/1633.md` is the Mac seat's, already on the pull-request branch, and is not touched here.

## Head

`c6ca4132`

## Mutation proof

Tests first: at `81ca1603` (the checker alone, before the schema and scopes landed) `node .claude/workflows/check-wave-script.mjs` exited 1 with 5 FAIL: `a finding must carry its seat (scope) and a class guess`, `a report must carry its leads, each {owner_seat, file, symbol, what}`, `scope admits a scopes.json seat id and refuses a bare dimension (D1-s3 yes, D1 no)`, `class_guess admits every tools/audit/bugclasses.json id and "new", and refuses anything else (null control)`, `the scopes threw: ENOENT`.

Schema mutants, each exits 1:
- `scope` removed from the finding's `required` → `a finding must carry its seat (scope) and a class guess` (measured at `a897272a`; that check is unchanged since).
- `symbol` removed from a lead's `required` → `a report must carry its leads, each {owner_seat, file, symbol, what}` (the same).
- at `c6ca4132`: owner_seat's pattern `.*` → `a lead's owner_seat admits a seat id or unknown, and refuses a bare dimension, a file, or anything else (null control)`.
- at `c6ca4132`: `P99` added to class_guess's enum, or the enum replaced by the old shape pattern `^([PI][0-9]+|new)$` → `class_guess is exactly the tools/audit/bugclasses.json ids plus "new": a well-formed id the ledger lacks (P99) is refused`.
- at `c6ca4132`: the leads fixture's path set back to the production path → `codeowners_gap.py --check` rc 1, `uncovered_files=2`, `REFUSED`.

The scoped-driver block at this head against the base driver with an empty `DISPATCH:BEGIN`/`END` pair appended exits 1: `and no planSeats: seats come from the scopes, not a rotation over the ledger`, `the scoped round driver threw: CADENCE is not defined`. Its per-mutant proof is in the driver's pull request, where the block has a driver to grade.

## Null control

The unmodified driver at this head: `node .claude/workflows/check-wave-script.mjs` exits 0, every pre-existing `planSeats`/`WAVES` pin still passing (`the driver dispatches exactly the SEATS table for round 9, one agent per seat` among them). The schema check's own null control is its refusal of `X1`, `P1 ` and the empty string; the scopes check's is `scopeGaps({}, {}, [])` returning a gap.

## Figures

- `node .claude/workflows/check-wave-script.mjs` at `c6ca4132`: rc 0, `N passed, 0 failed` (the instrument's own tally line; the deliberate `(probe, expected)` FAIL line is discounted by the checker).
- The same checker (`c6ca4132`) run against `handoff/r9-r1-find-driver`'s driver (`06851b14`): rc 0, 0 failed. This checker grades the R1 driver green.
- `python3 tools/audit/round6/D11/fix/codeowners_gap.py --check` at `c6ca4132`: rc 0, `RESULT uncovered_files=0`. At base `81f2c18c`, the null control: rc 0, `uncovered_files=0`.
- `python3 tools/audit/check_scopes.py --repo . --ref HEAD` at `c6ca4132`: rc 0, one `ok` line per dimension of `scopes.json`, 0 `FAIL` lines. `--self-test`: rc 0, `SELF-TEST passed (perturbed scopes refused)`.
- Parity with the plan's copy: `python3 tools/audit/check_scopes.py --repo /home/claude/heatpump_optimizer --ref 81f2c18c > new.out; python3 /mnt/project-files/audit-r9/check_scopes.py --repo /home/claude/heatpump_optimizer --ref 81f2c18c --scopes tools/audit/scopes.json > old.out; diff old.out new.out && echo IDENTICAL` printed `IDENTICAL` (plan copy sha1 `16569938883a256435dbe7dfa3c9d9cb39f5be2d`, unverified in-tree). `sha1sum` of the plan's `scopes.json` and `tools/audit/scopes.json` are both `954641ac0f06173edb1d5710dd4df0f849f7a8e2`.
- `check_scopes.py --seat D1-s9`: rc 2, `no seat D1-s9 in ...`.
- Classification: `PYTHONPATH=tests python3 -c "import closure as c; print(c.is_inert('tools/audit/scopes.json'), c.is_inert('tools/audit/check_scopes.py'), c.orphan_files())"` printed `True True []`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run`; nothing to run locally, CI runs the same selection.
- `python3 tests/structure.py`: rc 0, `STRUCTURE RATCHET PASSED`. `node .claude/workflows/policy_lint.mjs`: rc 0, `TOTAL: 0 error(s)`.

## Red checks

- No check went red on the pull request, but the review (`blocked 1a19dd9f codeowners_gap`) found one that would have gone red on `main`. At `a897272a`, the leads fixture in `check-wave-script.mjs` quoted a production path. `codeowners_gap.py` reads a path quoted in a file that calls `new Function` as one a workflow executes, so `python3 tools/audit/round6/D11/fix/codeowners_gap.py --check` printed `REFUSED` with `uncovered_files=2` (the base printed 0). `policy-docs` stayed green on the pull request only because it restores `.claude/workflows/*.mjs` from the base. On the push to `main` it grades this copy and goes red. That is the #1589 class. **Cheaper detector:** the same `codeowners_gap.py --check` run locally, under a second of wall time on this container, and it could have run before the handoff. Neither `tools/audit/prepr.sh` nor `fixer.md` step 5 runs it: `grep -c codeowners_gap tools/audit/prepr.sh` prints 0. So the detector exists and was in no local path, which is the first worked example in `defect-root-cause.md`. The countermeasure (adding it to `prepr.sh`, or a pre-edit hook on `.claude/workflows/*.mjs`) is the root-cause seat's to price, not built here.

## Forward-carry

none

## Friction

- decision-0013: cost: a pinned grader that pins a graded artifact's shape makes any change to that shape two pull requests (checker first, artifact second); this is the first of them.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
