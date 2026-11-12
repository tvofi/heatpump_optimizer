Fix review: blocked 9d3da28204b0683981252bff8651c19b8f89f3f7 evidence-cut: two sole-copy cuts against the merge base remain, the owner's instrument-window release of the machinery freeze and where round2/HARNESSES.md is final

bus-nonce: 4268073153fe45f3af7d56e00e2d1174

## Block

This is round 2 of the review of #3510. It is a delta round over the head `11a6c579bb8e354b4f76209b1b4c472ddfee5c19` that round 1 blocked as evidence-cut. I measured head `9d3da28204b0683981252bff8651c19b8f89f3f7` against merge base `8c10361eb1fea539dc5acb8f7442eac2810faa47`.

All five items round 1 named are restored, and each matches the merge base in number and constraint (`ev/sole-copy-grep.txt`, `ev/delta-policy.diff`):
- `load1` is 1.86 (best of ten: 1.55).
- `thread_factor` is 1.27–1.30 over four re-takes.
- `c398fc84`.
- `web-phase0.js` and `triage-quiet-judges.json` are at `d5d8c4a`, with the "read them before re-deriving" constraint.
- "says which they could not separate".
- "twenty had no disposition".

Each of the six new payments survives where the body says it does. I checked each one in the tree:
- `tests/closure.py:586` `"tools/pr/preflight.sh"` in `INERT_EXCEPT`.
- `CLAUDE.md:48` for `stamp.py`.
- `R10-RCA-FRICTION-RESIDUE.md` §1 for `rounds.py`.
- `tests/README.md:430-431` and `tests/closure.py:427` for `../setup-qa/`.
- README:31-33 and :295 for the workflows and the register.
- README:74 for the orchestrator's 500 k rotation.

The full merge-base diff of `dev/audit/README.md` still cuts two items whose only copy was the deleted text. Round 1 did not list either, and the body's statement "No measurement or downstream constraint is cut" does not hold for them:

- **A decision on downstream seats: how the freeze is released.** The base README:81 Production share (tvofi, 2026-11-01) says "the rest waits for an instrument window the owner opens". The head replaces it with "is frozen", which keeps the freeze but drops the release mechanism: only the owner opens an instrument window. `git grep -i "instrument window\|window the owner\|owner opens"` at the head finds nothing outside JSON. Carry 29 asks for the freeze to be written in and does not ask for the window to be removed.
- **A constraint the head now states wrongly: where round 2's harness list is read.** The base README said "Which of those harnesses still run is `round2/HARNESSES.md` at `d5d8c4a`, final at that commit only". The head says "Round 2's harnesses are at `757e164` (`round2/HARNESSES.md` says which run)". At `757e164`, `tools/audit/round2/HARNESSES.md` does not exist (`git show` prints `fatal: path ... does not exist in '757e164'`). It exists only at `d5d8c4a`. A reader who follows the parenthetical lands on a missing file, and the "final at that commit only" constraint has no other copy (only `plan-2026-09-open-issues.md:1257` and a `policy_lint.mjs` comment name the file).

To repair, keep both sentences: put back "the rest waits for an instrument window the owner opens" (or name where it survives), and tie `round2/HARNESSES.md` to `d5d8c4a`. If this costs tokens, pay with prose that has a surviving copy, as the six payments above do. README is at 6050/6059, so 9 tokens of headroom remain. If no such payment exists, ask the owner for the raise before pushing (CLAUDE.md rule 2).

## Evidence

- Head and base: `ev/HEAD.txt`. `dev/governance/roles/` is unchanged between the merge base and origin/main: 0 diff lines (`ev/roles-current.txt`), so the contract is current. The body's head line names `9d3da28204b0683981252bff8651c19b8f89f3f7`, the head reviewed. The body was read from `handoff-body/r10-round-playbook-final` at `610f2ba65804135850d37b3484a5de649ffa6e2f`.
- Scope, by fix-review.md step 12:
  - The delta 11a6c579..9d3da282 is the two policy hunks (README, `orchestrator.md`) plus the merge of origin/main.
  - The merge adds only mutation-ledger JSON under the inherited main history. No `custom_components/` line is in this PR's diff, so the scope does not widen.
  - The round-1 finding was re-checked against the whole merge-base diff, as the dispatch asked.
- `git merge-tree --write-tree origin/main 9d3da282…`: rc 0, clean (`ev/merge-tree.txt`).
- `node tools/policy/policy_lint.mjs --budgets` at the head: rc 0 (`ev/budgets-head.txt`). Columns are lines/cap and ~tokens/cap; every row equals the body's Figures:

  | file | lines/cap | ~tokens/cap |
  |---|---|---|
  | `tools/audit/README.md` key | 315/321 | 6050/6059 |
  | `CLAUDE.md` | 214/221 | 3604/3605 |
  | `fixer.md` | 315/315 | 5215/5216 |
  | `orchestrator.md` | 295/295 | 4246/4251 |
  | `architect-planner.md` | 84/85 | 1261/1261 |
  | `plan-review.md` | 24/24 | 304/304 |
  | `proposal-triage.md` | 36/36 | 488/489 |
  | `D13.md` | 79/79 | 1149/1149 |
  | `D11.md` | 99/103 | 1494/1499 |
- No cap is raised. The diff touches no `*budgets.json` and nothing under `dev/governance/config/` (`ev/budget-files.txt`), so there is no Raise justification to report. Carry 31 is left unlanded, and the body puts it to the owner as a raise question.
- Not re-derived: the body's cap null control (README 322/321, 6163/6059 and `orchestrator.md` 295/295, 4261/4251 with the six payment hunks reversed). It is an uncommitted tree state.
- Mutation proof, re-run (`ev/selftest-head.txt`, `ev/selftest-mutant.txt`):
  - At the head: `roster_edit self-test: 281 checks, 0 failed`.
  - With `LOG` removed from `VERDICT_LINE_RE` (line 208): `281 checks, 1 failed` and `FAIL triage gate: a LOG ruling is refused as LOG, never routed (got: )`.
  - Restored afterwards, with a clean worktree.
- `brief_lint.mjs`: rc 0, and `PLAYBOOK ok: the renamed fixture is refused for its 7 moved instruments and the null fixture lints clean`. The error counts come from its deliberate fixtures (`ev/brief_lint.txt`).
- `rules_sync.mjs --check`: `RULES-SYNC ok` (`ev/rules_sync.txt`).
- VERSION, the manifest and `RELEASE_NOTES.md` are untouched (`ev/version.txt`).
- Carries 41 and 42 were read on roster `handoff/audit-r10-roster` at `d10e9b2a1c1930a18386b9ca9e33524742e376c6`.
  - The README answers carry 41 by pointer ("as written there").
  - Carry 42's re-read is owed only after this group merges. The body assigns it to the final pass, so nothing is owed at this head.
- Other merge-base cuts I checked and judged duplicated or spent:
  - The process_time/thread_time mechanism survives at `dev/audit/rounds/round4/D9/h2_cycle.py:55` and `d9common.py:130`.
  - "do not wait for 1.5" survives as "`load1` is quoted, not gated".
  - The `j5_gil.py`/FakeHass reason points to the first trap.
  - The out-of-tree "Lean flow pre-study, section K9" pointer is partly kept at `.github/workflows/ci.yml:42`.
- CI: there is no review packet, and no CI to wait on before the PR opens. The handoff head `9d3da282` has no PR run yet; PR #3510 still points at `11a6c579`. `merge_train.py owed-reds` (rc 0) prints `tests / fast (3.14)`, `tests / mutation`, `tests / typing` and `validate / validate-hacs` (`ev/owed-reds.txt`). No owed red is read at this head, so the body's `## Red checks: none` is not contradicted.
- Finder's harness: none is named, and none is owed for a playbook prose group. The executable change's harness is the self-test above.
