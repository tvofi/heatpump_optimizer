Policy change on two owner rulings (tvofi, 2026-11-08, chat to the orchestrator): the bar for a new process, tooling or instrument proposal and for the owner's exemption moves from over 10% to over 20% improvement (CI time, programme completion time, right-first-time, token usage); an already planned instrument or machinery group, or an existing non-production CI lane or seat, stays only on a measured improvement of at least 10% (was 5%, in no policy file; its only statement was `dev/programme/triage/s6-batch126.md`, a record left as written); a minor or low defect repair in instrument or machinery code takes the same bars. Approval: mandate 6715477401 (scope all) covers the owner's approving review.

Sites changed: `dev/governance/roles/proposal-triage.md` (exemption sentence, keep test, minor-defect rule; `severity` is the roster group's field, an unclassified defect is classified first), `dev/governance/rules/ratchet-budgets.md` plus its generated `.claude/rules/` and `.cursor/rules/` copies (`node tools/policy/rules_sync.mjs`), `tools/audit/machinery_ratchet.py` (docstring, `THRESHOLD`, self-test cases at exactly 20%), `tools/audit/seat/instruments/machinery_ratchet.py.md`. Left alone: unrelated percentages (docs solver/furnace figures, round 9 perf-gate noise, D0 price figures, rate-limit floors) and the older `dev/programme/triage/s6-batch*.md` records that recount the 10% bar as applied then.

## Head

c7f4535dc12384e9f25e5a75ae31d3b573c87010 (main unmoved by conflict: `git merge-tree --write-tree origin/main HEAD` printed a tree, no conflict).

## Mutation proof

Mutant: `THRESHOLD = Fraction(1, 5)` restored to `Fraction(1, 10)` in `tools/audit/machinery_ratchet.py`; `python3 tools/audit/machinery_ratchet.py --self-test` printed `FAIL exemption: exactly 20% refuses: got 0, want 1` and `FAIL exemption: exactly 20% as floats refuses`, `54 checks, 2 failed`. Restored: `54 checks, 0 failed`.

## Null control

At the base the self-test passes with exact 10% refusing; at the head, 21% passes (`ex-11` case) and 20% refuses, so the cases separate the two thresholds.

## Figures

- `python3 tools/audit/machinery_ratchet.py --self-test`: `54 checks, 0 failed`.
- `node tools/policy/policy_lint.mjs --budgets`: `proposal-triage.md` 35 lines / 487 words against caps 36 / 489 (paid by cutting prose, no raise); `rules_sync.mjs --check` ok.
- Diff mutants: `MUTANT_CMD` was unset; the added Python lines are one constant and test literals, killed by the proof above. No survivor run, wall time not measured.

## Red checks

`prepr.sh` step 6b REFUSE `closures failed while being recorded: tests/entities.py`. Cause is environmental, not this diff: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `3 of 2656 ENTITY CHECKS FAILED` identically at the base 48af0864 (worktree) and at the head (the coverage-job, release-ZIP build and Pages-workflow probes; `GIT_CONFIG_GLOBAL=/dev/null` leaves the same three). Cheaper detector: none; the failures are in the cloud container. Every other prepr line before that step was ok. Closures recording and `harness_headers.py` left to CI.

## Forward-carry

none

## Friction

none

## Approval

Owner rulings quoted in the opening paragraph (tvofi, 2026-11-08, two chat messages to the orchestrator); the owner's approving review at the head is covered by mandate 6715477401, scope all.
