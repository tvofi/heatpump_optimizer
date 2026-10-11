Fix review: merge e81055d4b1830148e1ae0eaccebeababe642d981
bus-nonce: 30a0a147d8c52fa96efd6232a520c137

Round-9 fix wave, PR #2131 (`fix/r9-closures-lane-runner` -- the dispatch
brief's branch name `fix/closures-lane-runner` does not exist).

## Head (rule 12, disclosed in full)

The dispatch named head 80331a05a19928e927c0943deb827eda12045147. The branch
was ALREADY at e81055d4b1830148e1ae0eaccebeababe642d981 when my first command
ran (the record commit is dated 2026-10-11T07:24:03Z): a stale dispatch, not a
head that moved under me. `git diff --name-only 80331a05a..e81055d4b` is
exactly `dev/programme/delivery/2131.md`, one line, authored by tvofi -- the
standard delivery row. All five gate files (tests/closure.py,
tests/derive_closures.sh, tests/entities.py, tools/pr/prepr.sh,
.github/workflows/tests.yml) are byte-identical between the two SHAs
(verified per file). Every deep measurement below was taken at 80331a05a and
survives verbatim; entities and structure were re-run at e81055d4b (see
evidence/RESULT-head-delta.txt). The verdict names e81055d4b because that is
the head whose tree I re-verified; if the orchestrator prefers the literal
dispatch head, this same verdict against 80331a05a carries by
`app_approve.sh --carry` (the delta file misses the branch's own diff and the
claim files equal main's).

## What I re-measured myself (RESULT lines in evidence/)

1. Byte-identity of recordings. Five real recordings (wood_advisor,
   doc_claims, plan_view, layout, structure) taken three ways: five `--single`
   runs, a second identical serial pass, and one `--scripts-from` lanes run
   (DERIVE_LANES=3, real 15.42s, "3 lane(s)"). Normalized (seconds removed,
   scratch paths inside `spawned` normalized): four scripts IDENTICAL across
   all three dirs; layout.py differs in `spawned` only -- the per-run mktemp
   path in `git grep -f` argv -- and the two SERIAL runs differ from each
   other in exactly that way too (null control reproduced). `check --partial`
   verdicts byte-identical over all three dirs, all green. The .mjs card pair
   cannot be recorded on this box (strace/Linux); its constraint is covered
   structurally and by the selftest's live-table pin, not by a local
   recording -- stated, not measured.
2. No script dropped. A stub lane-plan that drops `tests/p2.py` from its lane
   file: at the head the derive refuses rc=1 naming it ("no recording this run
   for: tests/p2.py ..."). Guard-deleted mutant (the body's sed): rc=0 with
   five of six recordings -- the exact silent hole, reproduced.
3. Ordering constraint. 4000 randomized adversarial seconds tables (extremes,
   zeros, legacy non-dict shapes, shuffled orders, lane counts 1-9) plus a
   handcrafted worst case (producer 1e6s): zero split pairs, zero coverage
   failures. I could NOT split a constrained pair, and the structure explains
   why: `lane_edges` pairs are union-found into one atomic group placed whole
   into one lane, `_lane_ordered` re-sorts each lane edge-stably, and the
   planner reads the live PRODUCERS/DRIVEN_BY_OTHERS maps, so a future seam
   added to either map is enforced by construction (the body's class rule,
   verified against the maps: 2 producer edges, 1 driver edge).
4. Lane caps. `lane_request` clamps to 3 under CI=true, 4 otherwise;
   `--lanes`/`$DERIVE_LANES` can only go DOWN (min with cap, floor 1). Neither
   call site passes a lane count: tests.yml's scoped step relies on the
   runner's CI=true (bound 3), prepr 6b on the local bound (4, cpu-floored).
   Zero DERIVE_LANES/--lanes hits in both call sites.
5. File list. Exactly five files: tests/closure.py, tests/derive_closures.sh,
   tests/entities.py (comment-only), tools/pr/prepr.sh,
   .github/workflows/tests.yml -- the only workflow, and only the scoped
   branch; no lane count or new data is passed to CI. No VERSION, manifest,
   RELEASE_NOTES, claim files or budget files in the diff.
6. Mutation proofs re-run. Mutant 1 (`wait $!` after each lane spawn): head
   4.43s / serial control 12.27s / mutant 12.31s -- regressed to the serial
   SUM (fixer: 4.43/12.20/12.18). Mutant 3 (guard deleted): rc=0 silent, as
   above. Mutant 2's refusal is my item 2. Selftests at head: closure 76
   pins, prepr 249/0 (both new 6b arms ok), STRUCTURE RATCHET PASSED,
   ALL 2250 ENTITY CHECKS PASSED.

## Contract notes

- Red checks: none at the head (commits check-runs API; no failure
  conclusions). NOTE for the orchestrator, not a block: the Tests run at this
  head (38121234701) was CANCELLED ~3.5 min in and never rerun, so
  closures/fast/coverage sit cancelled -- the merge gate needs a rerun, and
  the body's 52m->~31m prediction is by its own statement confirmed only by
  the first non-gate-file PR after this merges, on two runs.
- Sibling #2129 touches the same files but textually disjoint hunks (checked
  against both diffs at the common base); the body's non-overlap claim holds.
- The cited spec (merge-path-wallclock-prestudy.md) is not yet in this tree;
  it is in flight on the R9-RO docs branch. Its finding's mechanism is what I
  measured above, independently.
- Numbers I could not re-derive: the CI walls (51m18s scoped, 27m57s full)
  are the pre-study's job-log figures, cited by the body as cited-not-derived;
  I verified the mechanism they price, not the walls.
- Forward-carry: none owed -- the pre-study's (a1)-coupling is discharged by
  this change itself; acceptance obligation restated in the body.

Verdict: the safety property holds as claimed -- which lane records a script
changes WHEN, never WHAT; a dropped script is loud; the ordering pairs cannot
be split by any seconds table I could construct. Merge.
