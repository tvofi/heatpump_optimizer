Fix review: merge e9ac63c18510614713f6fc0329c5c24593d2179d

bus-nonce: 609e158126eec3f759d262fc2e8fcab7

Round 3 delta review of #2838 (R10-FLOW-JIDOKA), measured at head `e9ac63c18510614713f6fc0329c5c24593d2179d` from detached worktrees. The prior verdict blocked at `042c60c8a`. This review covers the delta `042c60c8a..e9ac63c1`: the PR's own commits are `72fab10e4` (step 7 derives the intended list; 7e adjacency pin) and `4cf87d2e9` (usage line re-pointed), plus two main merges. The role contract at the merge base is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. The head was re-read with `git ls-remote` before writing, and it is unchanged: `refs/pull/2838/head` = `fix/r10-flow-jidoka` = `e9ac63c18510614713f6fc0329c5c24593d2179d`.

## Findings

none

## Evidence

- **1a, the retired path.** The layout guard and the CI predictor now pass at the head:
  - `python3 -I tests/layout.py --guard --base 7d2056970e08` prints `layout: GUARD: 0 refusal(s)` and exits 0. The control at `72fab10e4`, the refused r2 handoff, prints `new-reference: tools/pr/prepr.sh cites retired path tools/audit/prepr.sh` and exits 1 (`ev/layout.txt`).
  - `tools/pr/ci_predict.py --base 7d2056970e08 --body <PR body>` at the head prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted` with rc 0, in 23 s. At `72fab10e4` it prints `PREDICT tests / fast (3.14) LAYOUT new-reference ...` with rc 1 (`ev/ci_predict*.txt`).
  - `git grep tools/audit/prepr.sh -- tools/pr` still matches 5 lines (`ev/grep_retired.txt`). Every one exists at origin/main too: `test -f` fallbacks in push.sh and prepr.sh, and comments in gh_comment.py and prepr.sh. None is a new reference, and the guard reads it that way.
  - CI `tests / fast (3.14)` is success at the head (check run 121370797528).
- **1b, the closing keyword.** The body says `Refs #2428`, and no closing keyword names #2428 (grep of the live body). CI `pr-contract / pr-contract` is success at the head in run 121379084911, which started 03:13:22Z, after the last red concluded at 02:40:54Z. Its preflight step prints `clean    no refusal` and no REFUSE line. Its carry step prints `2 routed, 0 unrouted, 0 bad destination(s)`. Locally, `prepr.sh --body-check <live body>` prints `pr-body ok`, `carry ok` and `preflight ok`, rc 0, in 2 s (`ev/body-check.txt`).
- **1c, the two carried findings from the prior verdict.**
  - The intended-list mismatch is closed in this PR. `preflight_body` derives the list with pr-contract.yml's own jq program. The parity row's `grep -cF` prints 1 at the head. The finder's instance: round 1's body (`3a106cff3:BODY.md`, `Closes #2428`) passes the old form `preflight.sh 2428` with `ok closes #2428 -- intended`, rc 0. At the head, `preflight_body` refuses it with `REFUSE 'Closes #2428' closes #2428; not in the intended list` after the `note forwarded issue number(s) 2428 ignored` line, rc 1. `--body-check` on that body also prints `REFUSE preflight`, rc 1 (`ev/finder_instance.txt`).
  - X2 is killed. RESULT X2 (a `:` line between the 7e call and `step "carry"`): 383 passed, 1 failed, `FAIL the body step runs carry_line on the body and refuses on its rc`. RESULT X2' (`CARRY_RC=0` in the same position): 383 passed, 1 failed, the same row. My own mutant X3 (main-flow `step "preflight" 0`): 383 passed, 1 failed, `FAIL step 7's preflight derives the intended list and refuses on its rc` (`ev/selftest-X2.log`, `selftest-X2b.log`, `selftest-X3.log`). The body's M10 to M12 were not re-planted. X3 covers the same main-flow call-site pin as M12.
- **2, figures.** The body's `## Figures` is stamped with origin/main `5261ba841` and the date, 2026-10-26 00:30Z to 02:10Z. I re-took these at the head, against origin/main `28800999b` at 2026-10-26T02:42Z (`ev/figures.txt`):
  - `bash tools/pr/prepr.sh --self-test`: `384 passed, 0 failed`, rc 0, 283 s. This matches the body's 384. The `st` source rows went from 216 at `35c4fb0e9` to 223 at the head, which is +7, as the body states (`ev/st_rows.txt`).
  - `structure.py`: `STRUCTURE RATCHET PASSED`.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - `rules_sync --check`: ok.
  - `ref_privacy --check`: 0 refused.
  - `tmp_paths --check`: 0 refused.
  - `throwaway_git --check`: 0 refused.
  - `fold_ledger check`: `0 violation(s)`, `122 rca entries`.

  All match the body. CI's figure_lint prints `FIGURES: 15 resolved, 0 not verified, 0 refused`. I did not re-take the full-prepr wall time (29 min 24 s) or the entities `2 of 2445` box result. CI `tests / closures` is success at the head, which settles the entities question for this tree.
- **3, the merge and the protected files.**
  - `git merge-tree --write-tree origin/main e9ac63c1` exits 0 against origin/main `28800999b` (`ev/merge_tree.txt`).
  - Claim files: `card_claimed_drift.txt` is byte-identical to origin/main. `claimed_drift.txt` is byte-identical to the merge base `7d2056970`. It differs from the current origin/main tip only by a line main added after that base, so the branch claims nothing (`ev/claims.txt`).
  - VERSION, the manifest and RELEASE_NOTES.md have an empty three-dot diff. CI version-edit prints `no version edit`.
  - `dev/programme/delivery/2838.md` is in the three-dot diff.
- **4, CI at the head** (`ev/check-runs.tsv`). Every check concluded. The only failure is `governance / delivery-status` (job 121370129857). Its overdue list is #2697, #2820, #2821, #2823, #2822, #2818, #2773, #2812, #2813, #2712, #2807, #2804, #2798, #2799, #2780, #2749, #2775, #2797, #2762 and #2795, and #2838 is not among them (`ev/delivery-status.txt`). It is not a required check and does not block. The body's `## Red checks` names it, and pr-contract's red list (`governance / delivery-status`) passed the body check. Everything else is success or skipped, including fast (3.14), closures, coverage, mutation, instrument-self-tests, policy-docs, wave-script, env-matrix, arch-score, budget-raise-gate and gate.
- **5, carries.** `python3 -I tools/audit/carry_audit.py pr 2838` prints `2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry_audit_pr.txt`). The delta touches only step 7's preflight, the 7e pin and comments, and it does not change any round-1 answer to roster carries 1 to 21.
- **Approval scope.** The diff edits `dev/governance/roles/fixer.md`, which is policy, and code-owned paths: prepr.sh, app_push.sh, tmp_paths.py, and a comment in pr-contract.yml. main-protect-checks requires the owner's approving review for those paths. That gate belongs to the owner, not to this verdict, and the body's `## Approval` names it.
- **Rounds.** Under fix-review.md's closing line, this verdict is on the PR's third reviewed head: round 1 at `2b0eb9d85`, the block at `042c60c8a`, and now `e9ac63c1`.
