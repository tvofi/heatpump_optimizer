Fix review: merge 92a57dd44cb9d137d6faa86a2fd281011c26d0d7

bus-nonce: 38c07b7f1c7364987610b661778b1c2a

Round: 2, the second review of this PR. The round-1 block was `mutation-survivor` at 5ad16117f (verdict/3001 02508be7f). Measured head: 92a57dd44cb9d137d6faa86a2fd281011c26d0d7. At verdict time this is still `refs/heads/fix/r10-orch-planpage` and `refs/pull/3001/head` (`git ls-remote`). Merge base: ca0a6cfbc2e5538e6e2220793831443719ff6e98. The roles diff from the base to origin/main is empty, so the contract is current.

## Findings

- The PR body's `## Mutation proof` and `## Figures` are stale at this head. They say `RESULT survived=0` "over its 32 entries (M0 plus 31 mutants)", and the new-mutant list does not name `state-crash-guard`. At this head the harness prints 33 verdict lines (M0 plus 32 mutants), and the extra one is the round-2 `state-crash-guard` mutant (killed). `## Head` names 59598f9b7 but does not say what it changes. The count is explained by the round-2 commit, so it is not a false claim about the code. The body should still name the mutant and 33 entries before the merge. Carry: R10-ORCH-PLANPAGE
- The round-1 findings are re-checked at this head, and none is settled by this PR. Each is still routed as in the body's `## Forward-carry` (carry_audit at the head: 5 routed, 0 unrouted).
  - The `replan.py` `is_done` vs `held` mismatch remains. Carry: R10-ORCH-ROSTER-SCHEMA
  - Stamp cadence (carry 7) is residual. Carry: R10-ORCH-PLANPAGE
  - The flow board as a page section (carries 8, 9 and 13(6)) is residual and needs the orchestrator's ruling. Carry: R10-ORCH-PLANPAGE
  - The orchestrator.md line (carry 5) is absent. Carry: R10-ORCH-LEDGER
  - Retiring the out-of-tree `gen.py`/`tpl.html` under design 8's N4 rule is the orchestrator's. Carry: R10-ORCH-PLANPAGE

## Evidence

- **Round-1 block resolved.** 59598f9b7 adds the self-test arm `plan page: a crashing page refuses with rc 2 and publishes no PLAN.html`. It runs a `--plan` call over a malformed `bad-plan.json` (`{`) and requires three things: rc == 2, no `crash-state` ref at the bare remote, and `plan_page.py failed rc 1` on stderr.
- **The harness pins the `if False:` mutant.** `r10_plan_page_mutants.py` gains `state-crash-guard` (`if r.returncode != 1 or "PLAN UNAVAILABLE" not in text:` → `if False:`). Re-run at the head (ev/mutants_head.txt): `RESULT mutant=state-crash-guard rc=1 fails=1 verdict=killed`, with FAIL `plan page: a crashing page refuses with rc 2 and publishes no PLAN.html`.
- **Full harness at the head (ev/mutants_head.txt).** M0 is `rc=0 fails=0 verdict=null`. All 32 other mutants are killed, and the run ends `RESULT survived=0` with exit 0.
- **Null control: a real refusal still yields rc 1 and UNAVAILABLE.** The pre-existing arms still pass at the head (`state_docs self-test: all checks passed`, ev/selftest_head.txt):
  - `a stale plan keeps the last good page at the ref, exit 1`
  - `with no page at the ref, the UNAVAILABLE page is published`
- **The null-control arms bite.** My own mutant `guard-always` (`if True:`, ev/own_mutants.txt) makes every refusal a crash. It fails exactly those two arms with rc 2, so they distinguish a refusal from a crash.
- **My own mutants on the guard (ev/own_mutants.txt), each restored byte for byte, worktree clean afterwards:**
  - `guard-rc-only` (drops the text test): killed by the crash arm. It got rc 1 and published the UNAVAILABLE page over a traceback.
  - `guard-and` (`or` → `and`): killed by the crash arm.
  - `guard-always`: killed, 2 fails, as above.
  - `guard-text-only` (drops `r.returncode != 1`): passes the self-test, but it is an equivalent mutant, not a survivor.
- **Why `guard-text-only` is equivalent.** Staging is a fresh `tempfile.TemporaryDirectory()` per call (state_docs.py:547). `plan_page.py` writes `--html` only before returning 0 or returning 1 via `_refuse`. Every other exit writes no page: argparse/`p.error` rc 2, and uncaught exceptions rc 1. So "PLAN UNAVAILABLE" in the staged text already implies rc 0 or 1. I located this with a read-only scout and confirmed it against the code it quoted. This is evidence only. The redundant disjunct is harmless.
- **Self-tests at the head:**
  - `plan_page.py --self-test`: `60 checks, 0 failed`, which matches the body.
  - `state_docs.py --self-test`: `all checks passed`.
- **Ratchet and hygiene:**
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tests/env_drift.py --claims-only`: `claims hygiene: origin/main ok`.
  - VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched in the three-dot diff (0 paths).
  - `git log --format=%B` over the branch, grepped for claude/co-authored, gives 0.
- **Merge check.** `git merge-tree --write-tree origin/main 92a57dd44…` (origin/main cf4f6b7a6) exits rc 0, with no conflict and no MERGE-CLAIM line (ev/merge-tree.txt, ev/merge-tree.err).
- **Round-2 commit scope.** The diff between round 1 and round 2 in authored code is 59598f9b7 alone: 15 lines across `state_docs.py` and the harness. 92a57dd44 and d2bbb2322 are merges of that commit and of origin/main ca0a6cfbc. The three-dot diff shows only the PR's 10 files.
- **CI at this head (check-runs API, 16:50 UTC).**
  - No check run has a red conclusion. Every completed run is success, skipped or neutral (CodeQL). That includes `tests / mutation`, `arch-score`, `budget-raise-gate`, `tests / closure-scope`, `governance / delivery-status` and `governance / env-matrix`.
  - Still in progress: `tests / closures`, `tests / fast (3.14)`, `tests / coverage`, `tests / arch-instrument`, `governance / instrument-self-tests`, `codeql / Analyze (python)`, and the second `prelude`.
  - So no red-check answer is owed yet, and the body's `## Red checks: none` is consistent so far.
  - Under the contract I cite CI's heavy runs and did not re-run the gate.
  - The commit-status API shows 0 statuses, so I saw no `pr-contract` run on this head.
- **Figures I did not re-derive** (heavy or gate runs, CI's to cite):
  - entities.py `ALL 2484/2488 ENTITY CHECKS PASSED`
  - closure select `MODE: SCOPED -- 1 script(s) run`
  - archscore `dS +0.0000 NULL`
  - the prepr/ci_predict before/after lines
- **Finder's harness.** None is named in the packet. This is a governance-tooling group, and its harness is the in-tree `r10_plan_page_mutants.py`. I re-ran it and planted my own mutants above, and I disclose those mutants as mine.
- The review packet was rendered at this head: no refusals, no advisories, FIGURES 17 resolved, 2 not verified, 0 refused (ev/review-packet.md).
