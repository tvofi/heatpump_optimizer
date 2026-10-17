Fix review: blocked 95f31d5e869c52a0298a05966cfc90af4cb50563 figures-false: the body's round-5 re-record account and the M21 mutation claim are false about rt_36_layer_getattr_chain

bus-nonce: d785c8b1b8212eb4949c32f8ec113931

Round 5 (the dispatch's "round 3" miscounts: this head merges the round-5 closure
`9bab2b6ea` into the PR's previous head; the body's own chain and "## Friction" name rounds 4 and 5).
Reviewed from a fresh detached worktree at the head.

## Verified correct (re-run, not taken on the body's word)

- Enumerator `python3 tools/audit/archscore/calibrate.py` at the head, exit 0:
  RESULT calibration 95/124 labelled cases classify as their label says
  RESULT redteam 74/74 attempts read NULL or inadmissible; IMPROVES: none
  RESULT known-open 1 (rt_04zz1_dup_wrapsplit_uncharged)
  RESULT sensitivity none
- The three round-3 spellings read NULL at the head: rt_28, rt_29, rt_31 (and rt_30) each `dS +0.0000 NULL`.
- rt_41_layer_chain_past_module reads NULL at the head (the round-5 seam, closed).
- KNOWN-OPEN disposition judged correct: `rt_04zz1_dup_wrapsplit_uncharged` is counter C3's
  (gapped-clones) known block-split limit, recorded in `planted/cases.py` `KNOWN_OPEN` and
  dispositioned in `ABOUT.md` "Interleaved junk" / "Known limits". It is not a layering seam, so it
  does not open the C17/C18/C19 class.
- Mutation proof re-run (in-place predicate edits, restored with `git checkout --`):
  RESULT M0 14/14 NULL or inadmissible, IMPROVES none
  RESULT M18 (read arm private-only) 11/14, IMPROVES rt_38 rt_39 rt_41
  RESULT M19 (_ends_chain always true) 14/14, IMPROVES none; rt_29 rt_32 rt_35 rt_41 -> WORSENS
  RESULT M20 (_module_const ast.Assign only) 13/14, IMPROVES rt_40
  RESULT M21 (_reached outermost-only) 13/14, IMPROVES rt_41
  RESULT M14 (_namespaced descendant-only) 6/14, IMPROVES rt_32..36 rt_38 rt_39 rt_41
  Every load-bearing predicate reopens its attempt when removed — the mechanism is real, not a spelling list.
- Step 14 (metric-gamed): removing each mechanism (M18/M19/M20/M21/M14) returns the IMPROVES the body
  names, and none survives the removal.
- Head's layering values equal the ci_budgets rows: `vector.py` reads
  RESULT layer_violations 22
  RESULT private_cross_module 17
  RESULT unused_boundary_imports 1
  Three NEW rows only; no existing ci_budgets value moves.
- Step 5: VERSION, manifest `version` and RELEASE_NOTES.md heading untouched (all `7.0.0`, no diff).
- Step 4: `env_drift.py --all` -> `NO UNCLAIMED DRIFT`, `NO STALE FIXTURE` (no golden touches anyway).
- Step 13: `git merge-tree --write-tree origin/main HEAD` exits 0; only `tests/closures.json` conflicts
  and the ledger merge driver resolves it (`LEDGER-MERGE: resolved tests/closures.json`). No claim-file
  conflict. The GitHub `BLOCKED` state is the claim-driver DIRTY artifact, not a real conflict.
- Step 11: the only red check at the head is `coverage-ratchet` (early_cutoff.py, a custom_components
  module not in this PR's diff); the body names and answers it, and every other gate check is green or
  answered. `budget-raise-gate` is green at the head (owner approval posted).

## Block: false figures in the body

The body states, in "## Figures", that the round-5 `--record` printed
`rt_36_layer_getattr_chain NULL -> WORSENS`, "the four cases this round adds", and "19 insertions,
1 deletion", and, in "## Mutation proof" M21, that "rt_36 moves off its recorded verdict". All four are
false; I re-derived each:

- Round-4 closure `fa7859b6a` already records `rt_36_layer_getattr_chain` as WORSENS (expected.json,
  `admissible: false`). Running `calibrate.py --only rt_36_layer_getattr_chain` at `fa7859b6a` prints
  `rt_36_layer_getattr_chain WORSENS layer_violations 3->4`. Round 5's outside-in `_reached` did not
  move rt_36; round 4's `_ends_chain` + getattr arm already did.
- `git diff fa7859b6a 612ecd2cf -- expected.json` (and vs HEAD) is 6 insertions, 0 deletions, adding
  only `rt_41_layer_chain_past_module`. There are no "four cases" and no "1 deletion".
- Under M21 (the exact inverse of round 5's `a8183d2f7` diff to `layering.py`), rt_36 stays WORSENS,
  it does not "move off its recorded verdict".

The fix's substance is sound — rt_41 closes, the class is closed, and the mutation proof is load-bearing
— but the body's account of what round 5 did is not. The fixer owes the correction (`fixer.md` step 9:
a claim that is wrong must be corrected): restate the round-5 re-record as the 6-insertion rt_41-only
diff it was, and drop the rt_36 "NULL -> WORSENS" / "moves off its recorded verdict" claims.

## Note for the orchestrator (not the fixer's block)

The "## Forward-carry" first bullet names D7.md via R10-BRIEFS-FOLD and says the seat cannot write the
roster. `R10-BRIEFS-FOLD`'s `carry` list in `dev/programme/rosters/wave-r10-groups.json` carries part 1's
counters (C1b/C6b/C14, "#2293") but not part 3's layering boundary; the boundary itself is in-tree at
`tools/audit/archscore/ABOUT.md` "What it does not see", so the fold can cite it, but the roster pointer
is not yet written. Confirm that lands before the fold runs.
