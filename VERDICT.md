Fix review: merge c424aabf74362aacddd1ecf9a8e2f752bc19bc59

bus-nonce: 80f8331ac6af6d9f54b2bf8439f7b3a3

Round 3 of R10-STALE-PATHS-2 (#2344), reviewing the round-3 commit
`1f3100237` (global/nonlocal re-routing + the attribute census) at the merge
head `c424aabf`. Every number below is re-derived at that head, not read from
the body.

## What the round-2 block was, and what closed it

Round 2 blocked `class-open`: `_sp_scope_map`/`_sp_reach` did not resolve a
name bound through a `global`/`nonlocal` declaration. The round-3 diff closes
it two ways: `_sp_bindings` gained an `eff(scope, name)` re-router that binds a
`global` name at the module root and a `nonlocal` name at the nearest enclosing
function scope (walking past `ClassDef`), and the attribute-bound-in-one-scope-
opened-in-another shape (`self._p`, `C.P`) is dispositioned `already-guarded`
by the new `_sp_attr_bound` census. I verified the re-router's semantics are
Python-correct and the disposition's premise is real.

## Verification (my own RESULT lines; the arm's functions were extracted
verbatim from tests/entities.py via ast and driven directly)

RESULT minimal-global-resolves=True
RESULT minimal-nonlocal-resolves=True
RESULT escapes-count=25 missed=[]
RESULT held-count=3 held-open=[]
RESULT census-planted=2 planted=[(3, '_p'), (2, 'P')]
RESULT census-benign=0
RESULT cross-scope self._p open=False (the dispositioned seam, genuinely missed)
RESULT cross-scope C.P open=False (genuinely missed)
RESULT same-scope self._P open=True (the caught escape still caught)
RESULT census over 5 cited programs: all [] (0 live sites)

M7 (re-router removed, `eff` returns its textual scope), full run:
  FAIL the cited-program arm follows ... [shapes that still escape ['global binding', 'nonlocal binding']; no longer read as opens []]
  1 of 2346 ENTITY CHECKS FAILED  (exit 1)  -- the two declarations flip to MISS, the 3 held controls still hold, the 23 other escapes still fire.

M8 (`_sp_attr_bound` returns []), full run:
  FAIL no cited program binds ... [attribute-bound path sites []]
  1 of 2346 ENTITY CHECKS FAILED  (exit 1)  -- planted drops 2->0, so len(_sp_attr_planted) >= 2 reads false.

Clean head: tests/entities.py exits 0 (all checks pass).

## Hygiene and metrics

RESULT VERSION/manifest/RELEASE_NOTES diff empty (untouched)
RESULT golden/claim files diff empty (untouched)
RESULT fixer-authored diff = 5 files: entities.py, closure.py, closures.json, carry-201.json, delivery/2344.md
RESULT structure.py -> STRUCTURE RATCHET PASSED
RESULT closure.py selftest -> ALL 115 closure shrink pins PASSED
RESULT layout.py --guard -> 0 refusal(s); orphan_files -> []

## Check-runs

No check-run has gone red at this head: 29 success, 15 skipped, 1 still
in_progress (`composed-proof`) at review time; no failure/timed_out/cancelled.
Nothing to answer under defect-root-cause.md's red-check trigger.

## Notes (non-blocking, for the record)

1. The body quotes `ALL 2341 ENTITY CHECKS PASSED`; I re-derive 2346 at this
   head. The body's own Head section says its figures were taken at the code
   head `1f3100237`, before the origin/main merge, so 2341 is a stale (code-head)
   figure, not a misreport -- the 5-check delta is origin/main's newer checks.
2. The body says "This head has not been pushed yet"; it has since been pushed
   and CI ran green. The head SHA in the body matches the PR's live head, so
   this is a stale note, not a defect.
3. `nudge.md` in my seat worktree lags origin/main by one commit (the prepr-slot
   lease wording); it is the orchestrator's contract, not `fix-review.md`, which
   is current.

## Forward-carry

The one open seam (attribute-bound-in-one-scope-opened-in-another) is
dispositioned `already-guarded` by the census and is not a change to a later
stage; no new finding changes a later stage's brief. Carry requirement met.

RESULT merge clean
