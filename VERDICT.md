Fix review: blocked 170ac598748d4cf54e21a56a294eb747464b4f6d head-moved: measured 170ac598748d4cf54e21a56a294eb747464b4f6d, head is fa851d7ea2768c25a89a4a9820864d4a1b5fc458 (closures-autofix bot commit "ci: re-record closures", tests/closures.json only)

head: 170ac598748d4cf54e21a56a294eb747464b4f6d (branch head when this review began; measured throughout)
bus-nonce: 1bef0af3a3b8737d7e32d0bc82688e27


Round 3 (delta). Every claim this pass made was verified at 170ac5987; the
head then moved under the review, which is the block.

## What was verified at 170ac5987 (all reproduced by this reviewer, own runs)

1. Arch-score gate, the check's own command, base 23d354970 -> head
   170ac5987:
       Architecture score: dS +0.0000 NULL
       PASS: dS +0.0000 NULL, no gate metric rose
   footprint.measure at the head reads coord_footprint 2586 (flat at the
   merge base) and its charged list holds no _ending_streak entry.
   CI agrees: arch-score success at 170ac5987.
2. Typing ruler, pinned pair (mypy 2.3.1, homeassistant-stubs 2026.9.3,
   verified against tests/typing_ruler.py --print-requirements before the
   run), run from this reviewer's worktree at 170ac5987:
       ALL 9 typing-ruler checks PASSED
   CI agrees: typing success at 170ac5987.
3. Sound-fix arms re-run at 170ac5987:
   - Revert arm: debugger.py checked out from 23d354970, then
     PYTHONPATH=tests/hastub python3 tests/debug_collect.py exits 1 with
     KeyError: 'row_gaps_h' at tests/debug_collect.py:473; restored clean;
     the unmutated head prints ALL 70 DEBUG COLLECT CHECKS PASSED.
   - Finder's harness (dev/audit/harnesses/r9_dbg2_selftest_price.py, the
     pre-study's oracle, bundle sha1 cb6e9e3357648afc41adcadaff218f135908cc3d
     from origin/handoff/r9-dbg-0), run by this reviewer at both ends:
     five ok rows at 23d354970 and five ok rows at 170ac5987, inline=1 at
     both, bundle 588243 B -> 588446 B (+203 B), far under the 8 MiB cap.
   The moved read changes nothing a probe sees.
4. The two deleted killed_by rows are genuinely stale: with 4e5181094's tree
   and only the accessor deleted (rows kept), completeness_problems = 2,
   both naming debugger.py:_ending_streak (GUARD_OFF 7b428e6a, RETURN_DEL
   9e6cd1b7). At 1e60f1861 and at 23d354970, driven in isolation from
   tests/mutation_table.py: candidate sites 5943, unpinned 4620,
   completeness problems 0 at both ends -- the body's figures reproduce
   exactly. grep finds no _ending_streak anywhere at the head. At the merge
   head 170ac5987 the counts are 5983/4608/0 (main's own newer pins arrived
   with the merge; completeness still 0). The branch's net three-dot diff
   carries no ledger file.
5. Claims and versions: against the current merge base 969c3a5c8 (main moved;
   170ac5987 merged it), claimed_drift.txt and card_claimed_drift.txt are
   byte-identical to the base, as are VERSION, the manifest and
   RELEASE_NOTES.md. The authored three-dot diff is the four named files.
   git merge-tree --write-tree origin/main 170ac5987 exits 0, no conflicts.
6. Red checks: scanning every commit's check-runs in 23d354970..170ac5987 and
   keeping only the branch's own commits, the only reds are pr-contract,
   arch-score, typing (at c901f8f34 and 4e5181094) -- all three named and
   answered in the body's ## Red checks. All other red SHAs are main's own
   commits pulled in by the merges.

## The dispatch's item 4, answered honestly: closures was NOT green on CI

At 170ac5987 the CI closures check FAILED (exit 1):

    INERT READS UNDER-APPROXIMATED: a recording opened an INERT file the
    committed `inert_reads` does not list for it; the merge fast path
    would treat a change to it as unread (R9-F10.9d).
      tests/harness_headers.py: dev/audit/rounds/round9/prestudy/boost_drift_refit.py

The named file landed on main via #2109 (b24adb766), not by this branch's
authored diff; the branch inherited the gap by merging main. Per
ci-autofix.md the closures-autofix lane then repaired it: at 16:52:56Z
closures-autofix completed and the bot pushed fa851d7ea "ci: re-record
closures" (tests/closures.json +3/-2, nothing else), which is the head move
this verdict blocks on. The body, which names 170ac5987 as its head, is now
one bot commit behind and does not answer the closures red. The closures run
at fa851d7e was still in progress when this verdict was published.

## Why blocked rather than re-measured

The handoff froze the branch at 170ac5987; it moved. Re-measuring is offered,
not owed: the bot commit touches only tests/closures.json, so the fixer's
re-take should be a body/head update plus whatever figures prepr re-derives,
not a repair. Cheapest next step: fixer re-cuts the body at fa851d7e naming
the closures red and the bot repair, then re-dispatches this review; all six
verified blocks above survive a closures.json-only move except where a
re-derivation says otherwise.

Evidence: evidence/ in this verdict's directory (pr-body.md, typing-head.txt,
revert-arm.txt, oracle-head.txt, oracle-base.txt, closures-ci.log,
mergetree.txt, gate-and-ledger.txt).
