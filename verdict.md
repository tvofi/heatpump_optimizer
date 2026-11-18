Design review: approve 15dd4f5b3aae9534603cca9939774200d8ad7911

Reviewed design/R11-SEAM-comments-production at 15dd4f5b3aae9534603cca9939774200d8ad7911 (round 1) from a detached worktree. Code read at the note's base origin/main bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f. Plan read at plan/r11 819aa2e354b4e5baaf824b8568fd72bea8168a75 (ADR-010, PLAN.md "Hot-file order", the D5-s3 and D5-s4 harnesses). Roster row read on handoff/audit-r10-roster (size XL, no after edge, findings D5-s4-01 and D5-s3-02, with D5-s3-03 merged in).

Checked with no point raised:
- Seam. The group edits only comment and docstring text, plus one new ratchet script, which ADR-010 part 2 assigns to this group. The scope is the 96 top-level package modules and the card's script. At bc658f9 the package has no .py below the top level, so the scope is complete. tools/ is out of scope, which matches the owner's 2026-11-18 deferral of comment-only edits to instruments to round 12.
- Shape. Parts by seam, each released per file, are ADR-010 parts 2 and 3. The derived ratchet (merge base against HEAD, nothing stored) is the "count landed as a ratchet" that ADR-010 asks for. It avoids the two-sided structure_budgets row and a budget-raise review. Every change is named by D5-s4-01, D5-s3-03 or D5-s3-02.
- Sibling sites. The two harnesses' cells are disjoint and cover the scope between them: c5_long.py reads [_a-i]*.py, and comments.py reads [j-z]*.py plus www/*.js. 372 + 559 = 931 against the note's 936, and section 6 makes the script reconcile that to the unit. I re-ran the release command against the roster: 21 RELEASED and 76 HELD, with comfort_band.py held by R11-SEAM-inputs-guards and the card held by card and product-text, as the note states. The roster's only wildcard patterns belong to the two comment groups, which the command excludes. The grep for D5-s3-02's class finds only comfort_band.py:17, which is false, and coordinator.py:7664, which is past tense and true.
- Evidence plan. The self-test's plants fail on today's tree, because no script exists. The harnesses are the finders' and their --perturb controls move. slider_ceiling.py builds the real climate entity. The goldens and both claim files stay byte-identical.
- Sibling designs. No open design/* note claims a C5 detector or this text. design/R11-CARRY-DRAWMAP's "C5" is a different label.
- Cost. One script plus 13 text-only parts, one PR each, fits XL. No split.

Rulings on the designer's open points:
1. D5-s3-02 rides the first part dispatched after R11-SEAM-inputs-guards merges, not part 1. This deviation from ADR-010 part 4 is accepted. Part 4 assumed that no group of this round names comfort_band.py, but inputs-guards does. ADR-010's own file-order rule and its acceptance line ("touches no file whose row ... still has an open group") then decide the placement.
2. The ratchet is derived rather than stored, and it is accepted as ADR-010's ratchet. No row is added to tests/structure_budgets.json or to any *_budgets.json.
3. The carry to R11-SEAM-comments-tests (one-sentence-ratchet) stands. The two dismissals (inflight-red, part-by-seam) are accepted. The comments-tests extension adds tests/ to the scope and never tools/, under the same round-12 deferral.

Notes for the fixer:
- The script imports tools/audit/text_ledger.py, which tests/closure.py declares INERT (the tools/audit/ prefix, :309). Add it to INERT_EXCEPT with the reason, and record the closure with --single, or the closures job refuses the INERT-and-read pair (#357). Carry: R11-SEAM-comments-production (item text-ledger-inert-except)
- Do not import strip_js_comments or anything else from dev/audit/rounds/round11/. That directory is write-once round evidence. Put the JS stripper in the script or in text_ledger.py. Carry: R11-SEAM-comments-production (item no-round-dir-import)
- A new selectable script adds one recording to a full-case run. At part 1's handoff, read ci-ratchet's script_runs_per_push and script_runs_full_case_pr against tests/ci_budgets.json (54 and 68). If either reads past its row, make the ratchet an arm of an existing gate script rather than raise the row. Carry: R11-SEAM-comments-production (item script-runs-row)
- The ratchet base needs the merge-base commit's blobs. Check that the fetch depth in the tests lanes reaches it, as tests/mutation_table.py's ratchet_base callers already do, so a shallow checkout fails closed rather than passing. Carry: R11-SEAM-comments-production (item base-depth)

Seat token count: not reported by this harness.
