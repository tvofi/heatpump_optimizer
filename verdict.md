Fix review: blocked 11e8075d7975f34ab4baa8f2eb84220223443552 root-cause-detectable: pr-contract / pr-contract is red at this head (preflight refuses 'Closes #2506', which the roster lists in issues and in no group's fixes), so the required gate is red, and the body's Red checks does not name it; tools/pr/preflight.sh reproduces it locally in seconds

bus-nonce: 57fc2f09f6dd5e6a333bf8c0c60e1ca4

## Round

Round 2: a delta review of 2cfb8b96..11e8075d. The code delta is 59c744f4 (two card CSS rules plus `reveal()` and the tspan selector in `tests/card_browser.mjs`). The rest is a merge of origin/main 7d205697. I measured from detached worktrees at the head and at the merge base 7d2056970e08135bdc7c2cab4063427a2efa1c30. `git diff 7d205697...origin/main -- dev/governance/roles/` is empty, so the role files are current. Before writing, `git ls-remote` gave 11e8075d7975f34ab4baa8f2eb84220223443552 for both refs/pull/2841/head and fix/r10-card-voice.

## Block

- `pr-contract / pr-contract` concluded **failure** on this head in both runs: 121382577420, and 121383146856, which started 03:29:02Z after every other workflow had concluded. The one required check, `gate`, is therefore red too (121382733183, 121383314617; its log reads `FAIL pr-contract / pr-contract: failure`).
- The failing step is `Pre-flight the body for unmeasured claims`: `REFUSE 'Closes #2506' closes #2506; not in the intended list`.
  - The workflow builds the intended list as the body's closes minus the roster's `issues` that no group names in `fixes`. R10-CARD-VOICE has `issues: [2506], fixes: []` at both origin/main and the head, and no group lists 2506 in `fixes`. So #2506 is a "Part of" issue, and a closing keyword on it is refused.
  - Reproduced in this seat with the workflow's own jq derivation over the head's rosters and the live body: `INTENDED=''`, then `bash tools/pr/preflight.sh` gave rc=1 with the same REFUSE line.
  - Null control: the same body with `Closes #2506` changed to `Part of #2506` gives rc=0.
- This refusal is not new. It is identical at the previous head 2cfb8b96 (pr-contract 121344531377 and 121344052741 failed, and both `gate` runs failed), and neither the body nor the round-1 verdict names it.
- The body's `## Red checks` does not name `pr-contract` or `gate`. A cheaper detector exists: `tools/pr/preflight.sh <roster fixes> < body` (prepr.sh's preflight step) runs in seconds before the handoff.
- Two ways to clear it: the author can edit the body (`Part of #2506`, which needs no code push), or the orchestrator can, if the roster really intends this group to close #2506, move 2506 into the group's `fixes` with roster_edit. Either way the body then owes its red-check line. The code delta itself passes every check below.

## Findings

- The required `gate` is red at this head on the pr-contract refusal of `Closes #2506` (see Block). Severity: blocking. Carry: R10-CARD-VOICE
- The head no longer merges cleanly with the current origin/main 28800999. `git merge-tree --write-tree origin/main 11e8075d` exits 1 with `MERGE-CLAIM: refused tests/golden/claimed_drift.txt`. Main has since merged #2753, which claims `config_flow` (R10 thermal power option), and this branch rewrote the list to its own five coordinator claims. Per fix-review.md step 13, a refused claim file goes to the orchestrator to resolve by hand and is not a defect in the authored work. The resolution keeps this branch's five lines plus main's `config_flow` line only if #2753's drift is in the merged tree's diff; otherwise this branch's five alone. tests/closures.json resolved through its LEDGER-MERGE driver. Carry: R10-CARD-VOICE
- The round-2 rule `dialog.expanded .tooltip { font-size: 0.78em; }` (<=600 px) renders the phone dialog's tooltip at 10.92 px. That is under the ramp's 12 px floor (HARMONY.md V3) and 0.12 px under the merge base's 11.04 px. It equals the tile's own tooltip (10.92 px at both ends), so V1 holds.
  - The harmony study's census, and my re-run of it, count no hover pop-up, so "0 HTML text nodes under 12 px" does not cover tooltips at either end. On the tile, tooltips sat under 12 px before this PR.
  - Whether a phone pop-up may sit under the 12 px step to stay inside its chart (R9-UX-1) is a design call this PR did not have to make.
  - Carry: #201
- carry_audit.py prints `1 unrouted` for this PR. The item is in the round-1 verdict comment 6405898036 (item 4f705cf3, its `- **C1 (H1):**` measurement bullet under `## Evidence`), not in the PR body. The body's own items are 4 routed and 0 unrouted (pr-contract's CARRY-AUDIT line agrees). This PR cannot edit that comment. Carry: dismissed: the item is a prior reviewer's measurement bullet that hands nothing on; the body itself has 0 unrouted

## Evidence

- **P9 grid, the finder's harness** (`HPO_BROWSER_SCOPE=full node tests/card_browser.mjs` after `PYTHONPATH=tests/hastub python3 tests/plan_view.py`, in each worktree):
  - Head 11e8075d: rc=0, `ALL BROWSER CHECKS PASSED`, `P9 grid: 324 cells, 20375 text runs, 850 box-intersecting pairs inked, 105 colour rules`. Both of round 1's checks pass: 0 cells threw and 0 pop-ups outside (ev/browser_head.txt). The body's figures (324 / 20375 / 850) match exactly.
  - Merge base 7d205697: rc=0, `ALL BROWSER CHECKS PASSED`, `324 cells, 19736 text runs, 660 box-intersecting pairs inked, 102 colour rules` (ev/browser_base.txt).
  - CI: `tests / browser` concluded success on this head (check run 121371418761, 02:57:54Z).
- **Null control.** The head with 59c744f4's two card CSS hunks reverted (`.slot-menu` width rule and the phone `.tooltip` 0.78em rule), with the harness left as at the head, gives rc=1: `FAIL P9 grid: no pop-up leaves the viewport or its chart`, `10: div.slot-menu 6.7px outside | div.tooltip 4.5px outside | div.slot-menu 5.3px outside`. That is round 1's exact failure (ev/browser_null_control.txt). So the card fix, not the harness change, clears the pop-up check.
  - The `threw` check stays green in that control because `reveal()` is a harness change. I read it as sound: a pair it cannot bring into the viewport, or whose runs scrolled apart, is pushed to `bad.threw` and fails the check, so it does not stop measuring anything.
  - The tspan selector adds ink and cannot hide a shared pair. The body's MH1/MH2 mutants cover both.
- **C1 is not weakened.** I re-measured with the study's own harness (6aea0d10 `harness.html` and `states.js`, copied untracked into each worktree), using my own driver (ev/harmony_measure.cjs; disclosed as mine, not the finder's), at 375/768/1280 and in light and dark (ev/harmony_study_harness_*.txt):
  - Dialog base: head 14.00 / 14.00 / 14.00 px; base 12.00 / 12.00 / 12.90.
  - HTML text nodes under 12 px at the head: 0 on every page (tile, plan, setup, savings, advisor, health), at every width and theme.
  - Base, by page at 375 / 768 / 1280: plan 21/22/22, setup 3, advisor 8, health 13, savings 0, tile 5.
  - wi-hint: head 12.00 at every width; base 10.20 / 10.20 / 10.96.
  - wi-group-title: head 12.60 at every width; base 10.80 / 10.80 / 11.61.
  - None of these moved from the round-1 verdict's values. The study's own driver, `r10_card_harmony.mjs`, I did not re-run; the body reports it byte-identical across 2cfb8b96 and 59c744f4.
- **Tooltip font-size**, computed on the study harness, plan page (ev/tooltip_*.txt): head 10.92 / 12.88 / 12.88 px; base 11.04 / 11.04 / 11.87 px. The tile's tooltip is 10.92 px at both ends.
- **CI at this head** (check-runs API, every run concluded):
  - Green: tests / browser, fast (3.14), coverage, coverage-ratchet, closures, closure-scope, mutation, typing, briefs, arch-instrument, graders-head-copy, lane-proofs, nightly-status; governance / env-matrix, instrument-self-tests, policy-docs, wave-script; arch-score; budget-raise-gate; hassfest; validate-hacs; codeql (actions, javascript-typescript, python).
  - Red: pr-contract / pr-contract and gate (see Block), and governance / delivery-status.
  - delivery-status is red on programme-wide OVERDUE rows for other PRs (#2795 … #2812). This PR's diff adds only its own row `dev/programme/delivery/2841.md`, and its log says it is not a required context and blocks no merge. Under defect-root-cause.md it is main's, not this PR's.
  - pr-contract's body checks otherwise read `PR-BODY: 0 error(s)`, `FIGURES: 20 resolved, 7 not verified, 0 refused`, and `no version edit`.
- **Merge and claims.**
  - merge-tree against origin/main 28800999 exits 1, with the claim-file refusal recorded under Findings (ev/merge_tree.txt). Against the PR's own base 7d205697 the merge is clean (the body's statement).
  - VERSION, the manifest version and RELEASE_NOTES are untouched in the three-dot diff. `claims-for: 7.0.4` in both claim files equals VERSION 7.0.4.
  - `dev/programme/delivery/2841.md` is in the three-dot diff.
- **Carries 1–6.** The delta touches only the tooltip size at <=600 px and the slot menu's width. It changes none of the H1–H4 or C1–C3 answers from round 1, which I did not reopen beyond C1's re-measure above.
- **Figures I did not re-derive:** the body's MB/MC/MH1/MH2 mutant outputs, its 231 px / 51 px pop-up heights at 2cfb8b96, and card_drift's `44 state(s) moved and claimed` at 59c744f4.
