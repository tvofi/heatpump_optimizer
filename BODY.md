ci-ratchet stops failing the gate on a push to main (owner ruling, triage batch 244 P734/P735; study review Q1 and plan B2). It still runs and shows its own result; coverage-ratchet stays required. On a push gate.py prints one report-only machinery line in the step summary and changes no exit code.

Merge note: this changes no workflow file (tests.yml is untouched: its ci-ratchet job already runs only on push to main, so the gate alone decides what fails). tools/release/stamp.py is code-owned: tvofi's review or a mandate covering code-owned paths. The diff to tools/ci/gate.py is confined to the push-only set, its self-test and the summary line, so it is disjoint from R10-GATE-DEFER-BARRIER's deferral logic; whichever merges second merges main.

## Head

ef4556bb4241560de9862a5b856153aab4ff5584 (base 0b276e8c0cd4ddbcf5c5e0adfe179af00441e7f3).

## Mutation proof

Predicate mutated: gate.py PUSH_ONLY put back to ("coverage", "coverage-ratchet", "ci-ratchet"). `python3 -I tools/ci/gate.py --self-test` then reports `gate self-test: 91 checks, 3 failed`: "B3: push owes coverage-ratchet and no longer ci-ratchet (report-only)", "fixture gate_required == REQUIRED's union", "a push with ci-ratchet red passes and reports it in the one machinery line". Restored: 91 checks, 0 failed.

## Null control

Push with every job green: self-test check "null: a push with every job green prints the machinery line and passes" gives PASS with the line `machinery (report-only, never gating): no other job listed`. A push with coverage-ratchet red still returns `FAIL tests / coverage-ratchet: failure (this run)`. On a pull request the notes stay one line per job and no machinery line is printed (ci-ratchet never runs on a pull request, so its grading there is unchanged). Parity harness: `python3 dev/audit/harnesses/r10_ci_gate_core.py b3` reads GREEN; with `--plant` (now dropping coverage-ratchet) it reads RED.

## Figures

- `python3 -I tools/ci/gate.py --self-test` at the head: 0 failed.
- `python3 dev/audit/harnesses/r10_ci_gate_core.py b3` and `... b3 --plant`: GREEN, RED.
- `python3 -I tools/release/stamp.py --self-test`: RESULT stamp_self_test=pass.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: FULL (tools/ci/gate.py changes the gate itself); CI runs the whole suite, not run locally.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh`: rc=0 at the head.

## Red checks

none

## Forward-carry

none

## Friction

none
