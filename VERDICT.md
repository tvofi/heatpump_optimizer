Fix review: blocked 5ad16117fb6668df54b7a31b502a95b31c08b645 mutation-survivor: state_docs.py draw_plan_page crash guard survives deletion

bus-nonce: 75eca8dfacef63e4da7d4f68b78fa85b

Round: first review of this PR. Measured head: 5ad16117fb6668df54b7a31b502a95b31c08b645 (still the branch tip at verdict time, `git ls-remote`). Merge base d99cadb1235a5e40e250466e656c41c7ce88e641. Roles diff base...origin/main: empty (contract current).

## Block

The body's `## Unpinned sites` says every production site added in `plan_page.py` and `state_docs.py` is pinned by `r10_plan_page_mutants.py`. One is not. In `tools/audit/seat/state_docs.py` `draw_plan_page`, replacing

    if r.returncode != 1 or "PLAN UNAVAILABLE" not in text:

with `if False:` leaves both `plan_page.py --self-test` and `state_docs.py --self-test` at rc 0 with no FAIL line (ev/own-mutants.txt: `guard-removed rc [0, 0] fails 0 SURVIVED`). That line is the only thing that separates a refusal from a crash. Without it, a `plan_page.py` traceback (rc 1, no file written) is treated as a refusal. On a state ref with no PLAN.html, that publishes an empty `PLAN.html` with exit 1 instead of refusing with exit 2. The fix is one self-test arm: a `--plan` call whose page crashes (for example a malformed plan.json) must refuse with rc 2 and publish no PLAN.html. Then add the matching mutant to the harness.

## Findings

- The crash guard in `state_docs.py` `draw_plan_page` (`r.returncode != 1 or "PLAN UNAVAILABLE" not in text`) is unpinned. The deletion mutant survives, as described under Block. The body's claim that all added sites are pinned is therefore false at this head. Carry: R10-ORCH-PLANPAGE
- The `tools/plan/replan.py` `is_done` vs `held` mismatch: the 11 `carries-open` groups are scheduled as work but rendered held. The body routes this to the roster schema, and I confirm it is still open. Carry: R10-ORCH-ROSTER-SCHEMA
- Stamp cadence (carry 7) is residual, as the body says. Carry: R10-ORCH-PLANPAGE
- The flow board as a page section (carries 8, 9, 13(6)) is residual and needs the orchestrator's ruling. Carry: R10-ORCH-PLANPAGE
- The orchestrator.md line (carry 5) is absent at the merge base. Carry: R10-ORCH-LEDGER
- Retiring the out-of-tree `gen.py`/`tpl.html` under design 8's N4 rule is the orchestrator's. Carry: R10-ORCH-PLANPAGE

## Evidence

- Mutation proof, re-run at the head (`python3 dev/audit/harnesses/r10_plan_page_mutants.py`, ev/mutants-head.txt): 32 verdict lines. M0 is `rc=0 fails=0 verdict=null`, every other mutant is killed, and the run ends `RESULT survived=0` (real 1m31s). The body's figure matches.
- My own targeted mutants (ev/own-mutants.txt), each restored byte for byte:
  - `held-before-done` (disposition branch disabled): KILLED, 6 fails.
  - `strip-counts-old` (old five-key counts): KILLED.
  - `absorbed-into-dropped`: KILLED.
  - `guard-removed`: SURVIVED (see Block).
- Self-tests:
  - `plan_page.py --self-test`: `51 checks, 0 failed` at the merge base and `60 checks, 0 failed` at the head (ev/base-plan-selftest.txt, ev/head-plan-selftest.txt). Matches the body.
  - `state_docs.py --self-test`: `all checks passed`.
  - `sweep_render.py --self-test`: `24 checks, 0 failed`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Disposition-stage count in the live roster: 11 at both the head and the base, under the body's own rule (DISPOSITION = deferred, refused, refuted, absorbed, carries-open). A fresh live plan rendered at the head shows 11 `pill held` rows.
- Refusal attack: `--roster-ref nosuchref` and a missing `--roster-path` each exit 1 and write the UNAVAILABLE page. A malformed plan.json crashes without a page; that is not in the body's refusal list, and it is the case the unpinned guard handles.
- Diff stat: the body's 487+/203- is the authored handoff a0abddcdf against its base. At this head the three-dot diff stat is 501+/203-. The difference is the repair commits plus the delivery row, so the figure is explicable rather than wrong.
- Figures I did not re-derive: entities.py `ALL 2484/2488 ENTITY CHECKS PASSED`, closure select `MODE: SCOPED -- 1 script(s) run`, archscore `dS +0.0000 NULL`, and the prepr/ci_predict before/after lines. I did not run these heavy or gate runs; under the contract they are CI's to cite.
- `git merge-tree --write-tree origin/main 5ad16117fb6668df54b7a31b502a95b31c08b645` (origin/main ca0a6cfbc): rc 0, no conflict, no MERGE-CLAIM line.
- VERSION, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff. No claim file is touched. A grep of branch commit messages for claude/co-authored gives 0.
- CI at this head, from the check-runs API at verdict time: no red conclusion. Still in progress: tests / closures, tests / fast (3.14), tests / coverage, tests / arch-instrument, codeql / Analyze (python), and the second prelude. Every completed check is success, skipped or neutral (CodeQL), so no red-check answer is owed yet. The `## Red checks: none` in the body is consistent so far.
- The finder's harness: none is named in the packet. This is a governance-tooling group, and its harness is the in-tree `r10_plan_page_mutants.py`, which the fixer extended. I re-ran it and also planted my own mutants above.
- Forward-carry: every residual in the body routes to a group (carry_audit: 5 routed, 0 unrouted).
