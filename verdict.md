Fix review: merge bd0f383b52f98d73c15d9619ae4efeaa59024070

bus-nonce: 4359792571aff51856b1187008f34216
pending-ci: gate

## Evidence

- **Scope.** The packet's `## Review scope` line reads `delta`, over the reviewed head 467f58500d12be0b6907839a17be76432555851b. The previous verdict was `blocked introduced-red` (verdict/3451 ae4e0a50).
- **The PR's own delta.** I compared the `+`/`-` line set of the PR's own diff at 467f5850 (base e23124ff6e) with the one at bd0f383b (base 8af37bdf44) (ev/own_delta_vs_467f5850.txt). It differs in two places:
  - **`dev/README.md`.** Two lines are gone: the mermaid edge `post -->|"runs"| docs` and the table row `| postmerge.py | runs | state_docs.py | ...`. They came out in commit 91e79d897a.
  - **`tools/ci/selftest_closures.json`.** Lines differ where main moved under the branch. The PR's own diff against main is now only the `handoff-push` entry:
    - a new `run_sha` (f0f6cb2c...);
    - `tools/audit/seat/delivery_row.sh` dropped from `files`;
    - `dirs: []`.

  The body's repair-10 note describes exactly this. Every other file in the two-dot range 467f5850..bd0f383b, including all of the `custom_components/` changes, comes from main's merges (#3531, #3557, #3572, and the v7.1.16 stamp). None of it is this PR's. The delta writes no production line, so the review does not widen.
- **The block is resolved.**
  - At the head (detached worktree at bd0f383b), `python3 tests/doc_claims.py` prints `ALL 348 checks PASSED`, rc 0, in 14 s (ev/doc_claims_head.log).
  - **Mutant.** I restored 467f5850's `dev/README.md` at the head. The script then printed `2 of 348 checks FAILED` with the same two FAILs the block named (the `postmerge.py -runs-> state_docs.py` citation, and the anchor arm `[45 of 45]`), rc 1 (ev/doc_claims_mutant_restore.log). So the repair is exactly what turns it green.
  - Line 281 (`docs["state_docs.py"]`) is the mermaid node label. Its remaining edge is `jobs -->|"runs"| docs`, which is the plan-beat ownership this diff states, so it stays correctly.
- **No earlier finding reopened.** The previous verdict had no `## Findings`. carry_audit at the head prints `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)` (packet).
- **The selftest_closures resolution.**
  - `python3 tools/ci/selftest_scope.py static` prints `114 gated step(s), 0 problem(s)`, and `--self-test` prints `120 checks, 0 failed` (ev/checks.txt).
  - **Mutant.** With main's old `handoff-push` run_sha put back, `static` prints `STALE ... ['handoff-push']` and `1 problem(s)` (ev/selftest_static_mutant_runsha.txt). So the re-record is load-bearing and checked.
  - `handoff_push.sh` holds no `delivery_row` reference, which matches the `files` and `dirs` removal. `bash tools/audit/seat/handoff_push.sh --self-test` prints `6 checks, 0 failed`.
- **Other checks at the head** (ev/checks.txt):
  - `postmerge.py --self-test`: `18 checks, 0 failed`.
  - `policy_lint.mjs` and `--budgets`: rc 0.
  - `rules_sync.mjs --check`: `RULES-SYNC ok`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- **Merge with main.** `git merge-tree --write-tree origin/main bd0f383b` exits 0 at origin/main 0f37833e21, with tree 761363b605 (ev/merge_tree.txt).
- **Body.** `## Head` names bd0f383b52f98d73c15d9619ae4efeaa59024070, and the PR's head reads the same (ev/body.md). `## Red checks` answers the introduced `tests / fast (3.14)` red at 467f58500d and its repair.
- **Versions.** The PR's own diff touches no `VERSION`, manifest, `RELEASE_NOTES.md` or claim file. The two-dot range changes those files only through main's stamp merge.
- **CI.**
  - `merge_train.py classify bd0f383b52f98d73c15d9619ae4efeaa59024070 --pr 3451` printed `WAIT ... pending: gate red: none` from 04:07Z to 04:33:13Z, every 90 s (ev/classify.txt). That is about 30 minutes of polling, so I return the verdict with `pending-ci: gate`.
  - No red was present at this head while I polled. The owed-reds set is in ev/owed_reds.txt.
  - The budget-raise-gate refusal for the removed `proposal-triage.md` key remains the designed approval answered under `## Raise justification`, as in the previous rounds.
