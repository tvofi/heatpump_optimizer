Round-11 record: the round-10 round-end proposal triage, as `proposal-triage.md` (on main since #3451) shapes it: one consolidated batch, ruled once per instrument, over three inputs together (tvofi, 2026-11-15: "it should triage all its instrument groups together with your proposals and local prototypes before starting instrument work, some might be unnecessary"), plus one root-cause record per tooling-friction family (loop card L8). tvofi ruled every decision card the batch raised on 2026-11-15; the rulings are recorded in the entries. It adds record files only and closes nothing by keyword.

## Summary

- **The batch.** `dev/programme/triage/r10-round-end.md`, entries P742-P795 (54). Inputs: the 47 unfinished groups on `origin/handoff/audit-r10-roster` `80c1fb32c7` (every instrument group among them, the eight `deferred` ones, #3551, #3566, and the instrument carries on R10-PROCESS-SLIM, R10-SEAT-IDENTITY-P5, R10-OUTSIDE-CONTRIBUTOR-CYCLE and R11-INTAKE-R10-RESIDUE); the round-10 orchestrator's proposals (PC-1113-01 to -23 and the unnumbered sweep candidates after the 2026-11-13 triage seat); the local prototypes and workarounds (HANDOVER's inventory, the landing chains, the wake filter, the closure runbook, the dispatch seats' scripts); the pickup seat's proposal, read as a lead. Rulings are checked against the code at `origin/main` `a39627da59`, not the logs' accounts.
- **Outcome.** Thirteen existing groups kept (several narrowed or widened by merged items), four new S groups (three hotfixes, each with a freeze ground, and R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3 as outside work), five deferred groups `absorbed` into kept ones, R10-TICK-RESIDUE-P3 `refused` with all 34 carries re-homed by index, R11-PRE-OBJECTIVE-FUNCTION closed as done (#3575), R11-INTAKE-R10-RESIDUE's instrument carries split by seam (P768), and every PC-1113 proposal ruled or shown owned.
- **Owner rulings.** tvofi answered all cards (C1-C15, O1, O2, Q1, Q2) on 2026-11-15 about 09:50-09:57Z; 18 entries carry an `Owner:` line with his verbatim choice. All took the recommended option except C9 ("Keep them locally and benchmark them against the train"), which changed P789 and P790 from a drop to a DEFER: the landing chains and `land.sh` stay session-local and R11-PRE-PARALLEL-PIPELINE owes a benchmark of per-pull-request merge wait (verdict-and-GREEN to the merge commit), chain against train, with the train's own entries as the null control and a decision rule fixed in advance. P750 and the scratch-instruments record were corrected to match. O1 admits the two kept round-10 groups (P755, P761) into the pre-finder set; Q1 and Q2 are production rulings recorded in the batch's header for findability.
- **Root-cause records.** Seven under `dev/audit/rca/`, one per friction family with three or more instances: `R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md`, `-POLICY-DOCS-TIMEOUT.md`, `-FIGURE-BLOCK-STALE.md`, `-PIPEFAIL-SIGPIPE.md`, `-FLAKY-SELFTEST.md`, `-RELAY-SERIAL-UPDATE.md`, `-SCRATCH-INSTRUMENTS.md`. Each names the cause, the process state with its evidence, a cost test with numbers and a countermeasure or a recorded refusal. Three of the families turned the required `gate` red (policy-docs timeout, figure block, flaky self-test). Families under the threshold get one line each in the batch's Part E; one count the round-10 orchestrator stated ("relay release line not honoured") did not reproduce and is recorded as such.
- **Classification.** Both new paths sit under prefixes on `INERT` in `tests/closure.py` (`dev/programme/`, `dev/audit/`) and under `tests/layout.json` globs (`dev/programme/triage/*.md`, `dev/audit/rca/**`).
- **Nothing built.** No production, test or instrument code; no roster edit. The orchestrator routes each ACCEPT through `roster_edit.py`, citing `triage: dev/programme/triage/r10-round-end.md#P<n>`.

## Head

`caa32492bc7a7b0512957f8df4f5d6153349dd6d` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`2e17928032f2d9b662cf5d771a4e0192f5a2def5`. Two commits on `origin/main` `a39627da59`: the batch with the seven records, then the owner rulings. Read the diff three-dot.

## Mutation proof

n/a: record files only (a triage batch and root-cause records); no production, test or instrument code.

## Null control

The rulings are checked against the tree, and where the tree already answers a carry the batch says so rather than ruling it: R10-SEAT-IDENTITY-P5 carries 0-3 are on main (`tools/audit/seat/seat_gen.py`, the `loop-cwd` row in `tools/audit/seat/beat_jobs.py`), the scorecard's beat row is on main (`beat_jobs.py`, row `scorecard`), and R10-PREPR-DARWIN-SELFTEST-LANE's lane is replaced by the `darwin-selftest` row already merged by #3565. Of the 26 cards P1-P14, R1-R3 and L1-L9 checked, P13 alone reads fully built (`beat_jobs.py`, `0bfec38fa3`).

## Figures

- Rulings: `grep -c '^## P' dev/programme/triage/r10-round-end.md` printed 54.
- Verdicts: `grep -c '^Verdict: ACCEPT' dev/programme/triage/r10-round-end.md` printed 40; `grep -c '^Verdict: REJECT'` 1; `grep -c '^Verdict: DEFER'` 5; `grep -c '^Verdict: LOG'` 6; `grep -c '^Verdict: per line'` 2.
- Owner lines: `grep -c '^Owner:' dev/programme/triage/r10-round-end.md` printed 18 (one per ruled entry).
- Machinery window: `python3 tools/audit/machinery_ratchet.py --measure --head origin/main` printed `nonproduction_merges 477`, `production 103`, `window 580`.
- Field coverage cost: `node tools/policy/field_coverage.mjs` ran 170 s wall, 196 s user CPU, rc 0, on an 8-core Mac at load 7-11.
- Files changed: `git diff --stat origin/main...HEAD` printed 8 files.
- Lints: `node tools/policy/brief_lint.mjs` exit 0; `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s) across 52 policy file(s)`; `node tools/policy/policy_lint.mjs --budgets` exit 0.

## Red checks

none known at this head; the orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none

