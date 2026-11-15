Design review: approve 375ce7ff3f820a3d8b529ad6de60114f68d00289

Round 2. Design tip 375ce7ff3f820a3d8b529ad6de60114f68d00289 (one file, design.md), answering design-verdict c51f65059e (revise d1a4ae6a74 architecture-unsound, one point). The note's base e0ad8b2bd3 is an ancestor of the judging base e75ad291ff, 24 commits behind; between them, of the files the note cites, only tools/audit/seat/merge_pr.sh and merge_train.py move, and merge_pr.sh:379 (`ALREADY POSTED`) and the `posted-verdict` reading the note relies on still hold. cloud_dispatch.py, bus.sh, orchestrator_tick.py, roster_lib.py and ledger.py are byte-identical between the two; every citation below is at e75ad291ff.

## Round-1 point 1: answered

- The shared setup (cloud_dispatch.py:238) and tail (:377-378) now name no ref; each role's stop channel is its own return ref, stated in its body (design.md section 2 table, K6). Checked per row against the tree:
  - fixer: BLOCKED.md on handoff-wip/<topic> widens :332 and keeps :337-338 CARRY-LANDED; the fixer already holds that licence (:376, pinned :1421).
  - reviewer: unchanged, :316-320, pinned :1401-1405.
  - designer: `bus.sh push-design` (bus.sh:2540-2546) admits any non-empty note, so a `Design blocked:` note needs no new push licence; "You may push only to that ref" (:349) holds.
  - design reviewer: `Design review: revise <sha> seat-refused` matches push_design_verdict's grammar (bus.sh:2553); the commit subject carries the first line (:2559), so the round-count exclusion at :683 is implementable from the subject alone. The other design-verdict readers key only on `approve` (ledger.py:123 design_builds, orchestrator_tick.py:1737-1754, cloud_dispatch.py:599-610 design_approved), so a seat-refused verdict is never read as an approval or a build.
  - probe: :371 keeps its meaning; the note no longer claims a byte-identical probe render.
- The three base nulls the note names (:1412, :1435, :1438) are read correctly: round 1's shape would have turned :1435 and :1438 red; :1412's re-key from the bare token to the reviewer's sentence is stated with its reason.

## Checked and sound (no point)

- Seam (step 1): unchanged from round 1 and still sound; the new "Stop channels" bullet puts each grammar with its existing reader. No new write path into another module's state.
- Shape (step 2): the two consumer changes (design-reviewer route refuses a `Design blocked:` tip; a seat-refused verdict is not a round) are not named by a carry, but the note says why they move with carry 10's "every stop": without them a stop note would be reviewed as a design and a stop verdict would spend one of design-review.md's three rounds.
- Sibling sites (step 3): `git grep -n "your result" -- tools/audit/seat/` returns exactly :238, :371, :378. Readers of design-verdict/ across tools/ are the four named above plus prune_refs.py and closeout.py, which read ref names only.
- Evidence (step 4): (a) fails on the base at :238 and :378 in every role; (b)'s reviewer row is a stated positive control; (e) uses the throwaway-origin pattern at :861-878.
- Siblings in flight (step 5): open design/* refs read at their tips. R11-PRE-TOOLCHAIN-PIN (df3267eba7) cites beatd.jobs.json and beat_jobs.py (serialised, item dr1-beatd-jobs-hot), and orchestrator_tick.py at :1814/:1846 only, a count edit with no arm that cites this design's L5 ruling. R11-PRE-SECURITY-PRIVACY (3637ac0015, no verdict yet) touches bus.sh's ref_privacy class, not push_design or push_design_verdict. R11-PRE-SHARED-FILES (20cafac7df) cites bus.sh:2421 only. R11-PRE-PARALLEL-PIPELINE cites standing-merge.md; part 4 is ordered after it. No two designs claim one seam.
- Cost (step 6): part 2 stays one file plus its self-test.

## Notes for the fixer

- Part 2, test (c): the tail is not byte-identical across roles at the base or after the fix: the fixer's first tail sentence carries its step-ref licence (cloud_dispatch.py:376, `refs/heads/{WIP_NS}/{topic}`, pinned at :1421). Assert (c) over the tail's second sentence, or exempt the fixer's licence clause by name; a `refs/heads/` regex over the whole tail fails on the fix, or tempts dropping the licence and turns :1421 red. Carry: R11-PRE-STANDING-SCRIPTS (item dr2-tail-licence)
- Part 2, round_context (:581-590) and the verdict tuple (:677-683): when design-verdict's tip is a seat-refused commit, the re-dispatched design reviewer is told that commit as "the previous verdict" with no diff range (its design SHA equals the tip). Take the verdict tuple from the newest commit whose subject does not end ` seat-refused`, the same predicate as the count, so a later round still points at the last substantive verdict. Null: with no seat-refused commit, the tuple is the tip, as today. Carry: R11-PRE-STANDING-SCRIPTS (item dr2-round-context)
- Part 1, cp-owed DESIGN-REVIEW OWED: a design tip whose line 1 is `Design blocked:` is a designer stop the dispatch drain already reports as EXCEPTION seat-stopped (section 2, part 3). Unless the arm excludes that tip, it fires on it every pass past 10 min as a review owed that no reviewer can take (the route refuses it). Exclude it in the arm and plant it as a null in the part 1 self-test. Carry: R11-PRE-STANDING-SCRIPTS (item dr2-blocked-tip-owed)
