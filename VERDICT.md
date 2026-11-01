Fix review: blocked ec36f34aa4af4d940c54aa82d40a847cc74dd0a8 class-open: approval_owed reads APPROVAL-OWED when gate is red with no red unit (a required unit SKIPPED, ABSENT or PENDING), so a real gate red hides behind the raise

bus-nonce: 36c19f2d58ce2ef2f2f15d6b6f4a045b

Round 1 of this review (the fixer's round 2 of P345 + P348). Head measured: ec36f34aa4af4d940c54aa82d40a847cc74dd0a8, from detached worktrees at that SHA and at the merge base 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f.

## Block

The brief's step (2) asks for proof that approval_owed fires only when EVERY reason the aggregate `gate` is red is a raise's owed approval. It does not. `approval_owed` (tools/audit/seat/merge_train.py, after `RAISE_GATE`) tests only the *red set*, `classify(latest_runs(runs), gating_names(req))[2]`, and needs that set to be `{gate, budget-raise-gate / budget-raise-gate}`. But `gate` (tools/ci/gate.py, `gate()`) fails for reasons that never put any unit into that red set:
- `<unit> / <job>: SKIPPED`. gate.py fails any conclusion other than `success` (`elif st[1] != "success"`), but merge_train's `GREEN = ("success", "skipped", "neutral")` reads a skipped unit as green.
- `<unit> / <job>: ABSENT`. No check run, so classify lists it as pending, never red.
- `<unit> / <job>: PENDING`, the deferral bound (`FAIL run(s) [...] still being judged`), the prelude cross-check, a fork head, and the attempt cap. Each of these fails `gate` with no unit red.

Reviewer's own probe (ev/overfire.py, run with `classify --pr 3045` against the head's merge_train and stubbed in the same way as the self-test's `owed_cli`; it is not the fixer's harness). It plants #3045's shape (gate and budget-raise-gate failed, one unheld raise, the owner's approval on an older head) plus one extra unit:
- `tests / browser` concluded `skipped`: rc=4 APPROVAL-OWED (base: rc 1 RED)
- a gate unit with no check run (ABSENT): rc=4 APPROVAL-OWED (base: rc 1 RED)
- `tests / browser` `in_progress` under a concluded red gate: rc=4 APPROVAL-OWED (base: rc 1 RED)
- `tests / browser` concluded `failure`: rc=1 RED, which is correct.

Every reader inherits this, because each one asks the same function. `bus.sh dispatch` mints a reviewer. `orchestrator_tick` prints "RAISE APPROVAL OWED ... review it, then approve" in place of NOT REVIEWABLE. `review_packet` drops the required-red refusal. `cloud_dispatch`'s prompt tells the reviewer to "judge the head as GREEN". The merge itself stays safe, because the train and the ruleset still need a green `gate`. But the head is dispatched and the orchestrator is told to approve while it is red for a reason that is not the raise. That is the over-fire this change was required to exclude. The body's claim that the red is "only budget-raise-gate" is therefore not true over this domain.

To close it, something must read why `gate` is red, not just which units are red. One way is to read the `gate` check run's own output (its first token is `FAIL <reason>`; read every listed reason) and require each reason to name `budget-raise-gate / budget-raise-gate`. Another is to require every unit gate.py owes at this head's kind, other than RAISE_GATE, to have a latest run that completed with `success` exactly. Either fix wants a self-test row for each shape above (SKIPPED, ABSENT, PENDING) that stays RED, rc 1.

## Findings

- The approval_owed over-fire above (gate red for a SKIPPED, ABSENT or PENDING unit, or for a FAIL reason that names no unit, reads as APPROVAL-OWED). It is the block. Carry: R10-FLY-RAISE-REVIEWABLE | #3073 | O1 | dismissed: blocks this head; the fixer repairs it on this PR
- Surviving mutant R5: dropping `if code: return None` after approval_owed's `git diff --no-renames --name-only` survives `merge_train.py --self-test` (388, 0 failed). It is probably equivalent: a failed diff's stderr text names no budget file, so `raise_hold` answers held and the function returns None. Still, the docstring's "a read that fails ... is None" has no row for the diff read. A row with the diff stub at rc 128 would pin it. Carry: R10-FLY-RAISE-REVIEWABLE | #3073 | O2 | dismissed: the fixer adds the row in the repair round this block already requires

## Evidence

- RESULT CI at the head: `merge_train.py classify ec36f34a...` prints `GREEN ... pending: none red: none`, rc=0 (ev/ci_classify.txt). The commit's check-runs API, read in full, returns total_count 55 and 55 runs, every one `success` or `skipped`, none red (ev/check_runs.txt). This agrees with the body's `## Red checks: none`. The rendered packet has no refusals and one advisory (hot-file, HPO_BUS_TRAIN_STATE unset in this seat).
- RESULT merge: `git merge-tree --write-tree origin/main(61b0076f) ec36f34a` gives rc=0, tree 7f8d6519, no conflict (ev/tree_checks.txt).
- RESULT finder's harness, real-head control #3045 at 9ef51b8215dd7216950f177386fb2f5a8f010a47 (dev/audit/harnesses/r10_fly_raise_reviewable.py, which is the body's own control, so it was also re-run independently): base `RED ... red: gate` rc 1. Head with `--pr 3045`: `APPROVAL-OWED ... tests/ci_budgets.json: critical_path_minutes_band: None -> 1.3 ... tvofi's approval is on b02ffd170d50, not this head` rc 4. Head without `--pr`: `RED ... red: gate` rc 1 (ev/control_3045.txt). Null #3055 at 6a988a237f91a853d006f7908e41cfbd30bc9bc9: RED rc 1 at both ends (ev/null_3055.txt). No second real raise PR was located in this seat.
- RESULT null controls, from the reviewer's probe at the head (ev/overfire_head.txt; base in ev/overfire_base.txt, all RED rc 1). Each of these stays RED rc 1:
  - a red head with no raise
  - a raise with `tests / fast` red
  - a raise with `tests / fast` cancelled
  - a raise with another unit failed
  - a raise approved at the head (held)
  - a red gate whose raise unit is green
  - no `--pr`
- The brief lists "approval at an older head" as a shape that must refuse. It reads APPROVAL-OWED rc 4, and that is the designed owed state: it is #3045's own shape, since an approval on b02ffd17 does not hold at 9ef51b82. Judged correct.
- `governance / instrument-self-tests` red plus a raise reads APPROVAL-OWED. That context is neither in the ruleset nor among gate.py's units, so it does not redden `gate` and is not this predicate's to judge.
- RESULT mutants, merge_train.py (ev/mutants_merge_train.txt):
  - M1 KILLED (P345 row 3, held null)
  - M2 KILLED (row 2)
  - R1 (classify rc 4 to 0) KILLED (row 1)
  - R2 (raise_hold given another head) KILLED
  - R3 (ignore held, so any approval passes) KILLED
  - R4 (red set over req, not gating_names) KILLED (row 1)
  - R6 (Stop fails open) KILLED (row 4)
  - R5 SURVIVED (see Findings)
- RESULT mutants, bus.sh, baseline `115 checks, 0 failed` on Linux bash (ev/mutants_bus.txt):
  - M7, M8, M9, M10, M11 KILLED, each by the P348 row the body names
  - M3, M4 and the reviewer's own R7 (rc 1 dispatches) KILLED
- RESULT mutants, readers (ev/mutants_readers.txt):
  - tick M5a (owed=None) and M5b (red over req) KILLED
  - packet M6a (`if False`) and M6b (rc 4 dropped) KILLED
  - R8 (cloud prompt drops `--pr`) KILLED
- Self-tests at the head: tick 241/0, packet 53/0, cloud_dispatch 124/0, review_carry 26/0, merge_train 388/0, bus.sh 115/0. These match the body's F3. The body's macOS figure of 14 bash-3.2 orphans failures does not reproduce on Linux bash, where all 115 pass.
- RESULT P348 real refs (ev/carry_control.txt), base 8fec54ee to head:
  - #3045 at 9ef51b82: REFUSED (CARRY) to MINTS, "was blocked, so a fresh review is owed"
  - #2962 at 9ce0179f (latest verdict merge): REFUSED at both ends
- verdict_at reads the verdict naming `rh` (sha-anchored, newest first through `head -n 1`), not the newest verdict on the ref. M10 and M8 pin this.
- Two verdicts at one head: the later one wins. A merge then a blocked verdict at A mints, which is safe, because the later review superseded the merge and nothing carries. A blocked then a merge verdict at A refuses (CARRY), which is the ruling's case. An unreadable ref refuses and records nothing (M9's row).
- orchestrator.md's changed sentence ("a reviewed head whose verdict was merge") states exactly what dispatch now does. It is POLICY, and it merges only on an approving review at its head: the owner's, or the orchestrator's under mandate 6329234399. That is recorded here and is not part of the block.
- Item (4), the tick on a held raise: approval_owed returns None when raise_hold reads held (killed mutants R3 and M1), so the tick cannot print RAISE APPROVAL OWED for a raise already approved at its head. Nothing in this diff touches classify without `--pr`, the train (`wait_ci`, `main_green`) or budget-raise-gate: the three-dot diff edits only approval_owed, the classify CLI's `--pr` branch and the readers. So a reviewer's merge verdict on an owed head still cannot merge before the approval.
- Gate:
  - `tests/structure.py`: STRUCTURE RATCHET PASSED. No `*_budgets.json` is in the diff, so there is no raise (F7).
  - Scoped-gate line: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`.
  - `policy_lint --budgets`: orchestrator.md at 294/295 lines and 4245/4251 tokens, matching F7. `policy_lint` rc 0, RULES-SYNC ok.
  - tests/closures.json adds exactly the two new harnesses to INERT.
  - Delivery row dev/programme/delivery/3073.md is present in the three-dot diff.
  - The claim files, VERSION, the manifest and RELEASE_NOTES are untouched against origin/main.
  - All five instrument pages are updated (merge_train, orchestrator_tick, bus.sh, review_packet, review_carry).
  - ev/gate_checks.txt, ev/tree_checks.txt
- Not re-derived: the body's macOS entities figure (44 FAIL lines at both ends) and F8's archscore dS +0.0000. CI's green `arch-score` and `tests / closures` runs stand for them.
- The fork-head, attempt-cap and deferral FAIL reasons in the Block are taken from reading gate.py; only SKIPPED, ABSENT and PENDING were planted.
