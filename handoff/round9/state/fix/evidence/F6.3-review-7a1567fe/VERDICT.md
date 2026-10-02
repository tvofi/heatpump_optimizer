Fix review: merge 7a1567fe3eba60b7127c183c56006e0f2deb5397

F6.3 (#1802), fix review round 2. Reviewer: opus, cloud session, detached worktrees at the head.
Measured head 7a1567fe3eba60b7127c183c56006e0f2deb5397: the live head of fix/r9-f6-card-3 at posting, and the head the body names.
Merge base 6793659caed93f5a47bc7cc940f119b9e2abcbeb, which is still origin/main. The round-1 head 6d9a0f3d is an ancestor. The transport tip c398b468 is not in the head's ancestry.
Delta since round 1: 4 files, +50 -19 (card.mjs, card_browser.mjs, carry-1757.json, bugclasses.json). The card source is unchanged.

Round-1 remedies:
1. Non-overlap pinned. tests/card.mjs now checks slotHitExtents over three crowded lanes: each target covers its own ink, and no two targets in a lane overlap.
   RESULT head: card.mjs ALL CARD CHECKS PASSED, rc 0 (card_head.log).
   RESULT M2 (round 1's survivor, M2.diff applied to this head): rc 1, 2 failures, "boxed_in: no two hit targets in the lane overlap" and "shared_steps_like: no two hit targets in the lane overlap" (card_M2.log).
   M2 is now killed.
2. Scope built from the measured closure. gridScope reads tests/plan_view.py's closure from tests/closures.json at HEAD, plus the card files and the grid scripts. The reviewer's scope_probe.mjs gives (scope_probes.txt):
   solver-only, profiles-only, hastub-only and card diffs -> SCOPED -- RUN
   docs-only and empty diffs -> SCOPED -- SKIPPED, NOT A PASS
   a closures.json missing the plan_view.py entry -> FULL
   A push and a git failure still give FULL (unchanged code paths). tests/closures.json is itself on the surface, so a re-recorded closure runs the grid.
3. Body updated: it names this head, adds M2 with its pin and the scope probe, and answers red checks (none at the round-1 head).

The carry-1757 brief and the P9 barrier text now describe the closure-based scope; the carry keeps its control and its re-measure instruction. No budget raise. VERSION, the manifest and the notes heading are untouched.

CI on #1802 at this head: started at 07:27Z and still in progress at review time, nothing red. The body reports every completed check green at round-1 head 6d9a0f3d, including browser, fast (3.14), closures and mutation; I saw the finished ones green at round-1 review time and did not re-read the rest. Merge on CI green at this head, per the merge seat's rule; I re-ran no CI job here.
