Fix review: blocked bb9f93e8bc0d8ed6bf2a9b397c41d378c7d8cf5e body-stale: figures and item 6 describe round 1, not this head (corpus 62423 vs 62892, caps 46/666 and 35/521 vs 60/878 and 53/778, 0012 superseded-in-part vs revoked)

Round 2 of PR #2586 (R10-FLOW-DESIGN-POLICY), reviewed from a detached worktree at bb9f93e8bc0d8ed6bf2a9b397c41d378c7d8cf5e. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty (merge base is origin/main 57f0c9c77), so the contract I read is current. The head was re-read before writing and is still bb9f93e8bc0d8ed6bf2a9b397c41d378c7d8cf5e.

## Blocking

- The PR body's figures and description are round 1's and are not true at this head (fix-review steps 7 and 8). The body's `## Head` section says the figures were "measured" at 87c3672f, and the numbers it quotes are those of that commit:
  - `## Figures` and `## Red checks` (budget-raise-gate) quote `corpus_tokens` 61026 → 62423 and "about 62423 against a recorded cap of 62423". At this head `--budgets` prints `~62892 tokens, cap 62892`, and the budget file records 62892 (ev/budgets_head.txt).
  - `## Figures` quotes `designer.md` 46 / 666 and `design-review.md` 35 / 521. At this head they measure and are capped at 60 / 878 and 53 / 778.
  - Item 6 says decision 0012 gets a "Superseded in part (2026-10-21)" section and that "its cadence, its one enforcement point and D14's stop rule stand". The head says the opposite: 0012 is "Revoked ... kept as history", and its new section is "Revoked (2026-10-21)". `## Approval` still cites only R16's "voids", not the addendum (#201 comment 6322712314).
  - Item 1 and the spec line say the contracts come "from the drafts at the pack commit" ddacf98. The head re-derives them from pin 30c57744a (commit d2ba1e185).

  The `## Raise justification` therefore names a raise (62423) that is not the one in the diff. The owner's approving review at this head would approve a raise of 1866 tokens, while the body justifies one of 1397. The fix: re-take `## Figures`, `## Raise justification`, `## Red checks`, item 1, item 6 and `## Approval` at this head. The tree needs no change. Carry: dismissed: blocking this head, the fixer's body re-take

## Verified at this head

- **Item (1), 0012 revoked.** 0012's Status line reads "Revoked 2026-10-21 (owner addendum 6322712314); kept as history", with a new "Revoked (2026-10-21)" section, and the old "the rest of this record stands" sentence is gone. 0014 item 1 reads "0012 is revoked ... no part of it binds a seat, its moratorium included". The `policy_lint.mjs` comment now says "revoked 2026-10-21 by decision 0014 and kept as history: it recorded a process moratorium". I ran `git grep -iE 'moratorium|decision 0012|0012-process'` outside 0012, the release notes, delivery rows and audit rounds, and got 11 hits (ev/grep_0012.txt). Every one is history (an archived roster, rosters r9 and r10, the R9-RO-PC1 rca, the tmp_paths.py provenance note), 0014 itself, or the revoked-record comment. None describes a moratorium in force. Carry: dismissed: verified, no action needed
- **Item (2), contracts against pin 30c57744a.** The head has the pin's content in both files:
  - `designer.md` has "A note, not a stop" with the owner-reported, judge-verified and cannot-state branches.
  - `design-review.md` has "Notes for the fixer are findings, not revise points", "Decisions are routed, not revised" (`decision: orchestrator|owner`) and "Three notes at most".
  - Both state the Carry grammar `Carry: <group> (item <id>)` / `Carry: dismissed: <reason of two or more words> (item <id>)`, colon required.

  The deliberate changes are kept: the R17 threshold (every L/XL with no approved design, pre-study or prototype), the hard 1-h box, token counts, and `design-verdict/<group>`. The pin's draft lists `product-tradeoff-regression` among step 7's verdict words; the head keeps it in step 2 only, which is immaterial. Carry: dismissed: verified, no action needed
- **Item (3), caps and mutants.** At this head the per-file caps equal the measurements (60/60, 878/878 and 53/53, 778/778), and `corpus_tokens` 62892 equals the measured value. The mutants (ev/mutants.txt):
  - M1 (drop the two CLAUDE.md rows) gives 2 `[index]` errors, TOTAL 2.
  - M4: 62391 (measured minus band minus 1) gives one `[budgets] (whole corpus)` error, and 62392 gives TOTAL 0.
  - M2 (61026) gives one corpus error.

  `score.py --diff origin/main` gives `dS +0.0000 NULL`; the null control `--diff origin/main origin/main` gives `dS +0.0000 NULL` (ev/archscore.txt). Carry: dismissed: verified, no action needed
- **Item (4), red checks and merge.**
  - `budget-raise-gate` is red ×3 by design and is answered by name (with stale figures, blocked above).
  - `nightly-status` is red. The body answers it as main's scheduled-run red, and the diff touches nothing under `.github/` or any test lane (step 11).
  - The latest `pr-contract` (19:57:48Z) started after the last red concluded (19:52:17Z), and it is green.
  - `fast (3.14)`, `coverage` and `Analyze (python)` were still in progress when I read the checks.
  - `git merge-tree --write-tree origin/main bb9f93e8bc0d8ed6bf2a9b397c41d378c7d8cf5e` is clean: tree 25c64dc7, exit 0 (ev/merge_tree.txt).
  - VERSION, the manifest and the notes heading are untouched (ev/diffstat.txt).

  Carry: dismissed: verified, no action needed

## RESULT

RESULT policy_lint: TOTAL 0 error(s) across 43 policy file(s), FIXTURE ok
RESULT policy_lint --budgets: corpus ~62892 cap 62892 (+500); designer 60/878 cap 60/878; design-review 53/778 cap 53/778
RESULT mutant M1: TOTAL 2 [index]; M4 62391: TOTAL 1 [budgets]; 62392: TOTAL 0; M2 61026: TOTAL 1
RESULT archscore --diff origin/main: dS +0.0000 NULL (null control +0.0000 NULL)
RESULT merge-tree vs origin/main 57f0c9c77: clean, exit 0
RESULT 0012 revoked per addendum: PASS
RESULT spec-match vs pin 30c57744a: PASS
RESULT body figures at head: FAIL (62423 vs 62892; 46/666 vs 60/878; 35/521 vs 53/778; item 6 superseded-in-part vs revoked)
RESULT carry_audit --roster-ref origin/handoff/audit-r10-roster check: CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s) (a blocked verdict is all block sections, so no item ids; every bullet ends in a Carry: marker)

bus-nonce: ef107ce82343a8de954c5225807b79f7
