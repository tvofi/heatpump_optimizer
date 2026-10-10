Fix review: blocked 3f82aba337d65d897440923a2503ca3ca467c91b carry-missing: finding 2 of the body's "## Forward-carry" ("the beat's reach is its window" -- the record beat corrects only its `<last tag>..HEAD` window, so 85 of the 103 stale rows are reached by no automatic run and need a seat to run `--since` back to v6.7.13) names no destination file and is in no in-tree file; `dev/programme/carries/carry-201.json` is the live destination for exactly this shape of record/owed-work finding (extended twice in round 9, by #2073), and the body's stated reason for declining a carry -- "a carry file needs a destination issue a fixer does not file" -- is contradicted by that file's existence.

bus-nonce: 35e54af98f094ad6722d0c7ae4e9964f

seat: review-2111 (fix-review.md). Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2111/ev
measured at: 3f82aba337d65d897440923a2503ca3ca467c91b (merge base 7cd5a588cbbbef354c00148040da2d720b8a888c; `origin/main` had advanced to d3dbf2c3fc42b87e6aad71d3de0c0885a10c750e, and `git merge-tree --write-tree origin/main HEAD` is rc=0, so nothing here is a conflict). The head has not moved. Contract read from `origin/main`; only `dev/governance/roles/fixer.md` moved on main since the merge base, `fix-review.md` is current.

## The fix itself is sound on every task this round set

I built my own harness (my scratch, not the fixer's `mutants.py`) and my own mutants. All four adversarial questions the dispatch names pass, plus the boundary.

- **(1) status-aware, and it REWRITES.** A stale `**open**` row for a merged PR is planned and the existing file is overwritten, byte-equal to `row_line()`. Mutating `plan_merges` back to `has_row` alone reddens 9 arms (my M1); mutating `_rewrite_granted` to `return False` reddens 6 (M3).
- **(2) idempotent.** A re-plan over a rewritten corpus is 0; a row already at the API's sha is left byte-identical; a row at a different sha is corrected to the API's. Dropping the sha comparison reddens 2 arms (M5).
- **(3) grammar untouched.** `row_line` is not in the diff; the generated row keeps the anchor, the `|`->`/` sanitising, one line, the group suffix, and no closing keyword, and `delivery_status.mentions()` / `anchored()` / `rowed_line()` read it.
- **(4) the planted controls.** A genuinely OPEN PR with an `open` row is untouched, and the row alone **does** read stale, so `plan_merges`'s `state == "open"` clause is what holds it (M2 reddens exactly that arm). A merge with no row still gets its row, and `self_row` still writes `**open**` (M9 reddens 9 arms).
- **Boundary.** The write set is still `dev/programme/delivery/<N>.md` only: the plan of record, `HANDOVER.md`, a `../` escape, a non-`.md` path and a rewrite aimed at another file's number are all `Refuse`d.
- **Both ends.** At `7cd5a588c` the stale row is skipped and stays `open`; at the head it is planned and rewritten.
- **Every quoted number re-derives.** 103 stale rows (and 103/103 API `merged`, 0 errors), 100 at `23d354970` with the roster's 24 as its `N >= 2040` subset, the census 502 = 248+103+151 (15 multi-line, 136 prose-status), 161 and 18 window merges with all 18 stale, `105 = 103 rewrites + 2 new` then `re-plan 0` and `0` rows reading `open`. I ran the corpus on a temp copy I own, never the shared checkout.
- **No metric is gamed.** Structure passed with no metric moved, the architecture score is +0.0000 NULL, the claim files are byte-identical to the merge base, and no `VERSION` / manifest / `RELEASE_NOTES` / budget file is in the 2-file diff.
- **Class closed.** The body's own rule returns the whole class (its 103 = every stale row); 0 multi-line files and 0 non-in-grant lines carry `**open**`, and no row URL carries a fragment. No un-dispositioned seam.
- **No red check to answer.** At the live head, 40 check-runs, **zero failed** (`coverage` and `Analyze (python)` still in progress). The eight "reds" at the authored head `ce70213ae` are all `cancelled`, superseded by the newer head, not failures, and `harness_headers`' scope is touched by 0 files of this diff.

## The one blocker: the second forward-carry is in no destination

The body's own words are "Two findings change what a later stage must do, both measured", so `finding-propagation.md` binds both. Finding 1 names its destination -- the module docstring beside `THE REVIEW IS A PREDICATE` -- and I opened it: the measured pair of guard answers is there. Finding 2 names no destination file; it says it is "recorded for whichever seat next does record upkeep (`delivery-status-tracking.md` item 1)". I searched: the branch's three-dot diff is two files and neither carries it, `dev/programme/HANDOVER.md` does not mention the beat's window reach, and no carry file does.

The rule is a merge gate -- "The PR does not merge until the carry is in the tree. Its body names the file and the stage that received it, so a reviewer opens the destination rather than taking the claim." The destination exists and is live: `dev/programme/carries/carry-201.json` is the standing carry file for record/governance findings at issue #201, and round 9 has extended it twice (PR #2073). Its `_comment` states the precondition the body asserts no destination can meet -- "no roster group in this tree claims it" -- and its entries are `narrows`/`removes` findings of exactly this owed-work shape. So the body's reason for declining the carry does not hold.

I am not overturning any measurement: the fix is correct and reverified. The one thing owed is the destination.

RESULT round: 1. Head measured `3f82aba337d65d897440923a2503ca3ca467c91b`; still the head when this is posted.
RESULT mutation proof: my own 10 mutants (M0 rc=0; M1 9, M2 1, M3 6, M4a 1, M5 2, M6 1, M7 1, M8 1, M9 9 failed), each restored. My first M7 was mis-built and survived; rebuilt against the bold's closing `**` it reddens the named arm. The body's M4 tally (3 failed) I could not reproduce -- my reconstruction of the same clause gives 2 -- so that one quoted number is unverified, not refuted.
RESULT finder's rule: 103 row files read `**open**` at the merge base; 103/103 confirmed MERGED by REST, 0 open, 0 closed-unmerged, 0 errors.
RESULT corpus: 105 planned = 103 rewrites + 2 new (1885, 1890); all 105 byte-equal to the plan after apply; re-plan 0; 0 rows reading `open`.
RESULT boundary: plan of record, HANDOVER.md, `../` escape, non-`.md` and cross-number rewrite all refused.
RESULT harness: 30/30 arms of my own harness pass on a temp delivery copy I own; the shared checkout was not written.
RESULT carry: `dev/programme/carries/carry-201.json` exists, is live and was extended in round 9; the body's finding 2 is not in it, nor in the docstring, `HANDOVER.md`, or any brief.
