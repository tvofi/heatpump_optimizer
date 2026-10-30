Fix review: blocked 5832ceb58e6f1e79aba0f6273f50d1b4a928819a carry-missing: not carried to R10-FLY-CIPREDICT-GAPS or R10-UX-HEALTH, the null_for pre-check carry is on no roster group

bus-nonce: 7ece814279f518ef8c268f3785c3d3ab

## Block

- Under fix-review step 10, the forward-carry for the cheaper detector this body names is missing. That detector is a `null_for` pre-check in `tools/pr/ci_predict.py` (`prepr.sh` step 6d), and `## Red checks` gives it as the answer to the `tests / mutation` red at feacede17. Neither the body's destination nor the brief's re-route holds it.
  - Body: "the R10-UX-HEALTH group's `carry` list ... at 84ddbfbcf..., which does not hold it yet; the orchestrator writes it". At 84ddbfbcf the R10-UX-HEALTH group has 20 carries, and none of them names `null_for`, `null_control`, `NO NULL CONTROL` or #2997.
  - Brief: "moved to the new group R10-FLY-CIPREDICT-GAPS". No group of that name exists on `handoff/audit-r10-roster` at 84ddbfbcf, at 237e1aae4 or at the tip a8344f5a5 (re-read 2026-10-30T23:52Z). The only CIPREDICT groups are R10-FLY-CIPREDICT-LAYOUT and R10-FLY-CIPREDICT-RESTORING, and neither carries it. The whole roster file has 0 lines matching `null_for|NO NULL CONTROL|#2997|null_control|CIPREDICT-GAPS` (ev/carry_and_merge.txt, ev/recheck.txt).
  - Round 2 blocked on the same missing roster entry. The finding still lives only in this PR's body and comments, which step 10 says is not a carry.
- What clears this: the orchestrator writes the carry, with its control, to a roster group: R10-FLY-CIPREDICT-GAPS (a re-route the brief accepts) or R10-UX-HEALTH. The control as the body gives it: on a pool of only `flow_meter.py`, the pre-check prints `PREDICT tests / mutation NO NULL CONTROL`; on this head's pool (`button.py`, null control at line 37) it prints nothing. Then the body's Carry line names that group. No code change is owed. Everything else I checked at this head holds (Evidence), so a re-review should only need to confirm the carry, plus CI if it has concluded by then.

## Findings

- The `null_for` pre-check in `tools/pr/ci_predict.py` is not built, so a pool with no whole-line comment first shows red in CI. After this PR that pool is `flow_meter.py`, `silent_mode.py` and `wood_fuel.py`, by the body's census. It is not on the roster (Block). Carry: R10-UX-HEALTH
- P9 grid storage reset and the 375-px collision it hides are withheld. Carry 17 holds the leak and its reset control at 84ddbfbcf. Carry: R10-UX-HEALTH
- The "driving scale" widget is not built and waits on the orchestrator's confirmation. Carry 14 holds the owner's spec and the confirmation step. Carry: R10-UX-HEALTH
- #2499, no-meter over-booking (body: plan/deliv 1.908), is not met. Carries 11 and 20 hold the residual and its harness. I did not re-derive the 1.908. Carry: #2499
- `tests/mutation_table.py` is code-owned, so tvofi's approving review is owed at merge. That is flagged here, not a block. Carry: R10-UX-HEALTH

## Evidence

- Round 3 of #2997. Head measured: 5832ceb58e6f1e79aba0f6273f50d1b4a928819a, which is still `refs/pull/2997/head` and `fix/r10-ux-health-p2` at 23:52Z. Code head: 525e20691. `dev/governance/roles/` does not differ between the merge base and origin/main.
- `git merge-tree --write-tree origin/main 5832ceb58e6f1e79aba0f6273f50d1b4a928819a` (origin/main 5d4e0bcfb): rc=0, tree cd080778c, no conflict.
- Three-dot diff: VERSION, the manifest, RELEASE_NOTES and both claim files are untouched.
- RESULT `PYTHONPATH=tests/hastub python3 tests/entities.py`, each run in its own worktree at the head:
  - Unmutated: `ALL 2489 ENTITY CHECKS PASSED`, rc=0. The `hb:` FAIL lines in the output are retry diagnostics that the passing totals absorb.
  - Mutant A (the `len(lines[ln - 1]) < 60` cap restored): `1 of 2489 ENTITY CHECKS FAILED`, the new check, `long=None none=None pool-none=None`.
  - Mutant B (`if tok.type == tokenize.COMMENT:`): `3 of 2489 ENTITY CHECKS FAILED`, namely the new check (its null arm picks `Y = 1  # trailing`), `the null control edits a whole-line comment and nothing else`, and the shard null-control check.
  - All three match the body (ev/entities_*.out, ev/entities_*.diff).
- RESULT `tests/debug_collect.py` at the head, button.py hand mutants (ev/button_mutants.txt):
  - Baseline: ALL 159 PASSED.
  - 226 GUARD_OFF: AttributeError, rc=1.
  - 228 GUARD_OFF: 1 of 159 FAILED.
  - 230 RETURN_DEL: 2 of 159 FAILED.
  - Final branch returns `debug_collect`: 1 of 159 FAILED.
  - Null control button.py:37 + ` (null control)`: ALL 159 PASSED.
  - These match the three new `killed_by` rows' reasons and the body's null control.
- Figure: button.py:37 is 75 characters, so 90 with the suffix. The body says 91, which I take to count the newline. Its point stands: the line is far past 60.
- The card tests and the hover/fallback/openSetupSlot mutants were verified at 7c43d8fb1 in round 1. Between 7c43d8fb1 and 525e20691, `tests/card.mjs`, `button.py` and `tests/debug_collect.py` are unchanged. The card JS moved only through main merges.
- Authorship: baf2c4c00 and 525e20691 are authored and committed by hpo-fixer. 077a87b02 and 700f21c18 are not fetchable from origin, so I could not confirm the claim that the tree differs from 077a87b02 only in docstring wording. Earlier commits 855d1bbac, 31da5f026 and 7fed51072 (rounds 1 and 2) still carry the author `Claude <noreply@anthropic.com>` in branch history. The brief names only the two re-made commits.
- Roster carries 11, 14, 17 and 20 of R10-UX-HEALTH each state their finding and control at 84ddbfbcf and at the tip.
- CI at this head: `merge_train.py classify` printed `WAIT ... pending: gate red: none` (rc=3) on every run from 23:21Z to 23:52Z (ev/classify.log, ev/recheck.txt). Not concluded, so I have not read `tests / mutation`'s `MUTATION TABLE PASSED` in CI, nor the Linux runs of the macOS-only workarounds (task-port, scratch venv, card.mjs heap). No check was red when read.
- Not re-derived: the null-control census (84/13/11/3), the scoped-gate count (16 run, 17 scoped out), the #2499 harness figures and the P9 grid counts.
- No finder's harness is named. I built no instrument; the mutants are one-line edits in throwaway worktrees.
