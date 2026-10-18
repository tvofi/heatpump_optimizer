Fix review: merge 417ec846221f9a0c99fcbebaa5c835daf9473ba7
bus-nonce: 76ae508e12abe5d342287cb7875795f9

Round 2. Reviewer: review-2375. Round 1 blocked a5de7df1f (review commit 7f6ee976c) because
_bound_instants walked into a trie Domain when a stored key was "" or "~", so the whole store was dropped.
Scope, per the orchestrator: the round-1 delta a5de7df1f..ee964f0db, the main-merge delta ee964f0db..8755e99dd,
and the bot pin 8755e99dd..417ec846 (the verdict head; dispatched by the orchestrator).

## Round-1 delta (36f0f5cbe fix, ee964f0db ledger drop), measured at ee964f0db

My probe (ev/rev_probe2.py, my instrument, disclosed as such; ev/r2_probe.txt) loads eight corrupt
stores: four shapes ("" at an instant leaf, "" holding a list, "~" holding an instant, "~" holding
an instant 50 h ahead), each in the accuracy store and in a snapshot ring that embeds it.
Each goes through QuarantiningStore.async_load and load_mapping:
    a5de7df1f (control): RESULT cells_dropped=8
    ee964f0db:           RESULT cells_dropped=0   ("~" value 50 h ahead bounded to 0.0 h)
Lead rows are unchanged at ee964f0db. In the accuracy store a due 10 h ahead reads 10.0 h and one
30 h ahead reads 24.0 h, and a sample t at +1 h and evidence_since at +2 h read 0.0 h. In the
snapshot ring a due 10 h ahead reads 10.0 h and taken_at at +3 h reads 0.0 h.

tests/finite_boundary.py (ev/r2_mutants.txt, ev/r2_fb_*.txt), run by me:
- unmutated ee964f0db: ALL 89 PASSED. Round 1's null mutant, a comment-only edit, also passed (ev/fb_m0.txt).
- M6 (fixer's: `_child` back to `node.get(key, node.get(wildcard, {}))`): 1 FAIL. The new
  '"" or "~" key is data' row fails with all six of its cells "the store was dropped".
- M6b (fixer's: `_child` accepts any non-None entry): the same FAIL.
- ma (mine: `_child` loses its wildcard fallback): 4 FAIL, including lead_lost=['accuracy (writer
  round trip)', 'snapshots (writer round trip)'] and the healthy round-trip null control.
- mb (mine: store.py:537 GUARD_OFF, `if False:` on the rewritten `_fields` line): 2 FAIL
  (quarantines foreign=['x','y/0'], and the planted-undeclared-field control).

Class (fix-review.md 6). The rule: every reader of `_tries()`. Its output is `_bound_instants` (store.py:680)
and `_fields` (via stored_fields, which feeds admitted and off_domain). Both now descend only
through `_child`, and `_scalar_domain` receives only a node. Nothing else in custom_components/ or
tools/replay walks a DOMAINS pattern (grep: stored_fields|_tries|DOMAINS[|.split("/")). No seam is left open.
The pre-existing "~" variant at the base is closed in the same guard, so nothing is owed for filing.

The dropped ledger pin (store.py:_fields GUARD_OFF 7642fc84) is earned. Its recorded `old` line,
`if key not in node:`, no longer exists in the tree (git grep is empty). The replacement line, store.py:537, is
killed by tests/finite_boundary.py (my mb), so removing the pin hides nothing. The site
is now unpinned and named in the body for mutation-autofix.

Finder harnesses at ee964f0db (ev/r2_finder_harnesses.txt), with the same blobs as round 1:
- snapshot_bound: 0/0/0, control 0, --perturb 0.
- future_clamp_seams: instant_leaves=55 flagged_leaves=0 pairs=0.
- load_prelude: raising_seams=0.
- store_report_equiv: pairs=36279 mismatches=0, and --perturb gives 1764, so forward-carry (1) holds after the _fields change.

## Main-merge delta ee964f0db..8755e99dd

- 8755e99dd is a merge of b22590b18 (a5de7df1f plus ee964f0db) with origin/main 994695e06.
  `git merge-tree --write-tree ee964f0db 994695e06` gives rc=0 and tree 6d3bc5553200, which is byte-identical
  to the head's tree. That makes it a pure automatic merge with no hand resolution.
- No file this PR touches differs between ee964f0db and the head. Main's own delta touches no
  custom_components/, tests/finite_boundary.py, tests/features.py, tests/hastub or
  structure_budgets.json file. It touches only 31 mutation-ledger `reason` strings (host-path scrubs). So every
  round-2 figure above holds at the head unchanged.
- `git merge-tree --write-tree origin/main 8755e99dd` gives rc=0.
- VERSION, manifest.json, RELEASE_NOTES.md and tests/golden/ are untouched (three-dot).
- The closing keyword is unchanged since round 1: "Closes #2224" in prose, and closingIssuesReferences is [2224].

## Checks at 8755e99dd (check-runs API; ev/r2_checkruns.txt)

`mutation` concluded failure: `MUTATION TABLE REFUSED -- ... 3 of them added by this diff`. The 3 are
store.py:514 GUARD_OFF, 516 RETURN_DEL and 537 GUARD_OFF (ev/r2_mutation_job.log). The body's
`## Unpinned sites` names all three for mutation-autofix, and 537's killer is measured (my mb above).
That is the same answered-by-naming trigger as round 1 (850825263 -> bot pin a5de7df1f). A bot
`ci: pin killed mutants` commit on top carries this verdict (fix-review.md 12, #1667).

## Bot pin 8755e99dd..417ec846 (github-actions[bot], "ci: pin killed mutants")

It adds exactly 3 files under tests/mutation_ledger/killed_by/store.py/, and they are the 3 red sites above:
_child GUARD_OFF 8c460066 (killed_by tests/debug_collect.py), _child RETURN_DEL 4a8a66af
(tests/debug_collect.py), and _fields GUARD_OFF 72779c4e (tests/finite_boundary.py, matching my mb).
It touches no other path, so every figure above holds at 417ec846.

## Checks at 417ec846 (check-runs API, all concluded; ev/r2_checkruns_417ec846.txt)

38 success, 28 skipped, 0 failure, 0 in progress. Among the successes are fast (3.14), closures, coverage,
coverage-ratchet, typing, briefs, nightly-status, pr-contract, hassfest and mutation.
The green mutation is a real pass, not an empty one. Its log (ev/r2_mutation_117628078276.log) reads
"4327 unpinned site(s) ... 4341 at the ratchet base 994695e06", with no ADDED UNPINNED and no INCONCLUSIVE.
Workflow runs: Governance and one Hassfest run are `action_required`. They are held for run approval
(hpo-runs) on the bot push, have not run, and are not red. That approval is the orchestrator's to give before merge.
No red check is left unanswered at this head.

Not re-derived by me: archscore dS, closure select counts and ci_predict. These are cited from the body and CI.
