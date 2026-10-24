Fix review: merge 228d5e48d352f3a38b0a89437baa040f4d3021e9

bus-nonce: 7216a12d22840554e7bd204ca9b2867e

## Scope

Round 1 review of PR #2693 (proposal-triage ruling P53, s6 batch 3) at head `228d5e48d352f3a38b0a89437baa040f4d3021e9`, merge base `50af6174f53c0f9bec3f705c3a4bb99615f71acc`. The diff (three-dot) adds two files, both under `dev/programme/`: `triage/s6-batch3.md` (52 lines) and `delivery/2693.md` (the one-line row). It changes no code, check, budget, closure, claim file, VERSION, manifest or notes heading. `dev/governance/roles/` and `.claude/rules/` are unchanged between the merge base and origin/main, so this contract is current.

## Findings

- The ACCEPT ruling still has to reach the roster: `R10-FLY-OPENPR-ATOMIC` (on `handoff/audit-r10-roster` at 7cad554c7: stage not-started, three carries, files `tools/audit/seat/open_pr.sh`) does not yet hold a carry saying that `open_pr.sh`'s second push (line 71) takes `--row-only`. It also needs the self-test row: a row push passes the flag, and as the null control the code push (line 58) does not. `roster_edit.py` reads the ruling only from the roster branch or origin/main, so the roster op is owed after this merges, citing `triage: dev/programme/triage/s6-batch3.md#P53`. Carry: R10-FLY-OPENPR-ATOMIC
- One figure in the ruling is imprecise. P53 calls `tools/pr/app_push.sh` "a hot file of about 1000 lines", but at this head it has 1228 lines (`wc -l`). The real size only makes the M-L cost estimate for deferring candidate (a) stronger, so the verdict does not change. Carry: dismissed: understates the cost behind the DEFER; no ruling changes

## Evidence

- RESULT ruling_verdict(P53) = ACCEPT. Null control: ruling_verdict(P54) = None. Mutant (the Verdict line renamed) = unreadable. Mutant (ACCEPT changed to DEFER) = DEFER. triage_refusal accepts a #P53 cite and refuses a #P54 cite ("no such entry"). See ev/ruling.txt. The "ACCEPT NARROWED" form matches `VERDICT_LINE_RE` (`^Verdict:\s*(ACCEPT|REJECT|DEFER)\b`).
- Figure re-derived: the rg count of Verdict lines is 1 (ACCEPT), as the body says.
- Cited lines re-derived at the head (ev/claims.txt): `open_pr.sh` line 58 is the p1 push and line 71 the p2 push, and neither passes `--row-only`. `update_pr.sh` line 74 is the `--row-only` arm. `tools/pr/app_push.sh` lines 107-120 are the `--row-only` comment block with conditions (a)-(d) and the "30+ minutes" reason. `pr_args.sh` lines 840-854 are the row-only self-test rows (the arm, mutant `mut:rowonly`, and the null control). `open_pr.sh` has two `head_note` heredocs (E0 at lines 49-54, E at lines 64-69); the row is written by `commit_row` at line 62 and followed by a `## Head` prefix, which is the shape conditions (a)-(d) describe.
- Numbering: #2689's `s6-batch2.md` holds P45-P52, and no `## P53` exists on origin/main or on #2689, so P53 does not collide with another entry.
- Mutation proof: n/a, because the diff writes no production code line. The consumer is `roster_edit.ruling_verdict`, and the mutants above show that it reads this entry.
- Class: one seam (one push in one opener). The body names no enumeration rule, and the issue states only one seam.
- Claims: the diff leaves both claim files, VERSION, the manifest and RELEASE_NOTES.md untouched (ev/merge_and_scope.txt).
- Merge: `git merge-tree --write-tree origin/main 228d5e48d` exits 0 (tree 3da0406e6) against origin/main 0c3640761.
- CI at this head (ev/ci.txt): 0 failures among 33 check runs. tests / coverage and governance / instrument-self-tests were still in progress when I read them. No check went red, so there is no red-check trigger to answer, and the body's "Red checks: none" holds.
- Head: the body's `## Head` names 228d5e48d, the head I measured. A re-check before returning gave the same head (ev/head_recheck.txt).
- Not re-run here: `tests/entities.py` timed out locally under the hastub (killed at 300 s). I cite CI's tests / fast (3.14) and closures, which both passed.
- The observed queue (09:30Z, four heavy slots held) is the proposal's own measurement and is not in the tree. I could not re-derive it, and the ruling does not depend on it.
