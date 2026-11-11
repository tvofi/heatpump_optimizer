# Proposal triage, session s8, batch 88 (P325)

The rolling batch after batch 87 (handoff `triage-s8-batch87`). Facts were read at origin/main
`4822c8f9b` and on the roster branch.

## P325: `review_carry` prints FRESH-REVIEW when main only moved context lines around a branch's edits

Verdict: REJECT, for code files. A near-duplicate ruling already exists and stands: **P17**, the
brief of **R10-FLY-CARRY-DOC-CONTEXT** (`not-started`, S, `tools/pr/app_approve.sh`).
- **What P17 already settles.**
  - P17 carries a context-only difference in `*.md` files, where only ` `-prefixed lines differ
    and their count is unchanged.
  - It keeps code files strict, with `py-context no` as one of its fixture controls.
  - This proposal would reverse that control for every file.
- **The hunk-header half is already built.** The comparison the proposal targets is
  `app_approve.sh` `carry()`'s `norm()` (line 390). It already drops each `@@` header (offsets and
  function line) and each `index` line, so a pure line shift compares equal today. What it still
  compares is the context.
- **Why code context stays strict.** #3014's difference is two hunks of context in code files,
  where main rewrote lines that sit next to the branch's edits:
  - `tests/closure.py`: main replaced two list entries beside the branch's added entries.
  - `tests/doc_claims.py`: main replaced the calls `check_image_dimensions()` and
    `check_doc_wiring()` with `check_marker_census()` and `check_card_figures()`, directly beside
    the call list the branch extends.
  - A reviewer at `42b228ec` never saw the branch's checks run beside main's replacements. That
    adjacency is where a merge that git resolves automatically can still change behaviour, and it
    is why P17 kept code strict. Byte-identical change lines do not show the branch's code means
    the same thing in its new surroundings.
- **The filing's `git range-diff` evidence is vacuous for this shape.** A merge-forward keeps the
  branch's commits as they were, so `range-diff` prints `=` for every merge-forward, including one
  with a real semantic interaction.
- **Benefit, measured by triage** over merged PRs since 2026-10-17. V is the head the
  `verdict/<N>` tip names and H is the merged head (`<merge>^2`):

  | Class | Count |
  |---|---|
  | V equals H | 231 |
  | Branch-own commits in V..H | 12 |
  | Merges only, compared equal under today's `norm()` | 153 |
  | Merges only, differing in context lines only (the class this proposal would carry) | 9 |
  | Merges only, a real change-line difference | 7 |

  - The 9 context-only PRs are #2669, #2622, #2584, #2589, #2585, #2577, #2558, #2444 and #2368.
  - All 9 predate 2026-10-24. Since then the only instance is #3014, about 1 a week, at one delta
    review of about 20 minutes each.
  - The probe did not apply `carry()`'s driver-file and bot-path exclusions, so the 7 "real" rows
    may include claim-file rows. That does not change the context-only count.
- **The trade is marginal.** The benefit is about one delta review a week. The cost is giving up
  the one check that makes a reviewer look at main's code written beside the branch's code.
- **Re-open trigger.** Re-open for code files only with evidence that strictness buys nothing:
  delta reviews of context-only code heads that found no defect in the adjacent lines, across at
  least 5 such heads. P17's `.md` arm is unaffected and remains its group's work.

Source: the orchestrator s8's message of 2026-10-31 06:30Z (slip, #3014).

Instances: #3014 (`42b228ec` to `c41c4053`, 2026-10-31). The 9 earlier context-only merged heads
listed above were found by this ruling's probe, not filed.

Cost: as filed, S in `app_approve.sh`'s `norm()`, plus fixtures. The real cost is the review
coverage that P17's code control buys, which this ruling keeps.

Binding:
- P17 already ruled this line, carry prose context and keep code strict, and #3014 is a code
  instance that shows why.
- About one 20-minute delta review a week does not clearly pay for losing review of main's
  adjacent code.
