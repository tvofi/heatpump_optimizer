Fix review: blocked e199f727b44059611092c141d1d04edb8dee219a carry-dismissal-unsupported: carry 16 part (1), judge every loop, is dismissed as implemented at f0c6bbfd7 but only part (2) is on main

bus-nonce: b911ee2a918f844ea97b3703f6772c34

## Block

Round 1 (handoff review, no pull request yet). The build of carry 15 is sound and its control bites; the block is one dismissal. Roster carry 16 (0-based; handoff/audit-r10-roster 4dd28829) has two parts: (1) JUDGE EVERY LOOP, a live-usage review with one row per out-of-tree loop and a verdict fold / keep-as-is / drop, and (2) HOOKS. The body dismisses carry 16 whole as "implemented at f0c6bbfd7" and cites only part (2) files. On main, f0c6bbfd7 is the hooks commit, and its pull request #3294 says in its own body "Carry 19: delivered for its section (2) only; section (1) stays open" (old index 19 is this carry). #3197's live-usage review records the loop judgement as a gap, and no tracked fold/keep/drop record exists on main (ev/carry16.txt). Cure: answer carry 16 part (1) in this part (the per-loop rows), or keep it open on the roster to the part that owns it with a valid Carry: line; dismiss only part (2) as implemented at f0c6bbfd7.

## Findings

- Survivor: the self-test pins only step (3) (the carry asks one mutant, so not a block); restoring main's steps (2), (4) or (6) verbatim leaves sweep_render --self-test at 37 checks, 0 failed (ev/mutants.txt), so a regression of the dispatch-seat and merge-seat routing in those steps would land unseen. Carry: dismissed: the carry's control names one mutant; optional hardening, a "no update_pr.sh/open_pr.sh/bus.sh confirm/worktree_gc.sh run by the orchestrator" check, at the fixer's discretion

## Evidence

- Head reviewed: e199f727b44059611092c141d1d04edb8dee219a (ev/HEAD.txt); the handoff body's ## Head names the same SHA. No pull request exists, so there is no review packet and no CI to read; no check runs exist at this head. owed-reds set: ev/owed_reds.txt; no red to answer.
- Merge with main: git merge-tree --write-tree origin/main e199f727b44059611092c141d1d04edb8dee219a exits 0, tree 92ba34d2 (ev/merge_tree.txt); 0 commits behind main.
- Policy currency: git diff merge-base...origin/main -- dev/governance/roles/ is empty.
- Diff: tools/audit/seat/sweep_render.py (+5, self-test only) and tools/audit/seat/sweep_template.md (steps 2, 3, 4, 6; orch_scratch row removed). VERSION, manifest version, RELEASE_NOTES heading, claim files and budget files untouched.
- Figure "37 checks, 0 failed": re-derived at head (ev/sweep_render_selftest_head.txt); 35 at merge base.
- Mutation proof: step (3) restored from main with its placeholder neutralised fails the two named checks (35 checks, 2 failed); restored verbatim it is refused earlier by the unknown-placeholder check. Killed.
- orch_scratch: no remaining reference at head (git grep empty), so the row removal is safe.
- Carry 15 routing re-checked against the seats' contracts on main: standing-dispatch.md:16 (bus.sh confirm), :28-30 (open_pr.sh, update_pr.sh); standing-merge.md:8-10 (train.sh recommended defaults, joins the live train). The rewrite sends each step to a seat that owns it.
- Carries 17, 18, 19: dismissals confirmed on main (ev/carry16.txt, last lines).
- Carry 16 part (2): hooks/liveness.py, seat_interpreter.py, git_identity.py, hooks_setup.py, instruments/hooks_setup.py.md present on main; confirmed.
- Carries 0-14, 20-27: not judged here, per the dispatch (roster markings or other parts).
