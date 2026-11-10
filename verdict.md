Fix review: blocked 46f0637251e85de671f9870b60fbb852515c0989 ci-red: required checks tests / fast (3.14), governance / wave-script and pr-contract are red at this head on re-run; the delta has no defect

bus-nonce: cf217dc431acf153efedbcdfe687630e

Delta review since 0a02619939e72e83cd52702aaf319e98049c4ba9 (the previous merge verdict). Third review by this seat of this PR, so a fourth review of the PR is not yet reached; `fixer.md`'s re-cut is owed from the fourth. Measured at 46f0637251e85de671f9870b60fbb852515c0989.

## Block

`merge_train.py classify 46f0637251e85de671f9870b60fbb852515c0989 --pr 3355` read WAIT (rc 3) from 07:04Z to 07:41Z, then RED (rc 1), "red: gate" (ev/classify.txt). Required contexts red at this head, from `merge_train.py owed-reds` (ev/owed-reds.txt), all on re-runs started 07:04Z:

- `tests / fast (3.14)` (job 129684174444), "Run the suite": `FAIL the probed scenarios' memory peaks stay within their recorded budgets [typical_slab/shoulder traced peak 3.9 MiB vs recorded 1.8 MiB (x1.5)]`, `1 of 114 STRESS CHECKS FAILED`. The same reading, 3.9 MiB, as the red the earlier verdict at this head (verdict/3355 cca1a31a) recorded; locally the probe reads 2.1 MiB. That is two CI readings of 3.9 MiB, not one.
- `governance / wave-script` (job 129684183721): `UNREGISTERED "\A[0-9a-f]{7,40}\Z" in tools/audit/seat/roster_edit.py, tools/audit/seat/roster_lib.py`, `AGREEMENT REFUSED`. At this head only roster_edit.py (line 180) carries that grammar; against current origin/main only roster_lib.py (line 550) does, and `git merge-tree --write-tree origin/main 46f0637251e85de671f9870b60fbb852515c0989` carries one (ev/merge-tree.txt). The PR touches neither file; the CI merge ref read both, which I cannot reproduce on any tree I can build. The first run of this job at the same head (job 129684175721, 01:06Z) was success.
- `pr-contract / pr-contract` (job 129693289304, 129689707117), step "Check the body against the contract" exits 1. It runs after the head's other workflows conclude red, so I read it as the body's `## Red checks` not yet naming the fast and wave-script reds above (the packet refusal: `red-unanswered: concluded red check governance / wave-script is not named in ## Red checks`).

Neither red is inherited from main: main at ddd2f8b27 has `tests / fast (3.14)` and `governance / wave-script` both success (ev/main-state.txt). Neither is caused by the delta (below). A required red is not mine to waive and I cannot re-run it. Action: the orchestrator re-runs `tests / fast (3.14)` and `governance / wave-script` on a fresh merge ref (a push or update-branch, since a job re-run reuses the stale ref), then re-classifies; the body then answers whichever stays red (`root-cause-detectable` / `root-cause-unrecorded` applies if the memory red recurs: see the first finding).

## Findings

- Resolved (previous block at 0a026199, `selftest-scope-ungated`): the step has `id: figure-block` and `if: steps.scope.outputs.figure-block == 'true'`; the closure is recorded; `governance / instrument-self-tests` re-ran success at this head (job 129684183674, 07:19Z). Carry: dismissed: resolved at this head, nothing owed
- Follow-up: `tests / fast (3.14)` has now read typical_slab/shoulder at 3.9 MiB against a 1.8 MiB record twice in CI on identical code, and 2.1 MiB locally; the memory pass probes 6 budgets from one reading each. This is the second instance of one class and the cost test of `defect-root-cause.md` owes its numbers if it recurs on a third head. Carry: dismissed: orchestrator-side CI mechanics and an instrument question outside this diff (tests/stress.py is untouched); the third instance is the trigger
- Residual (carried unchanged from the two earlier verdicts, outside this delta and not re-reviewed): the surviving mutant on figure_block.py's base-overlay line (`_git(wt, "checkout", base, "--", f)`), and the partial base-program guarantee of the pr-contract wiring. Carry: dismissed: not in this delta per the owner's scope ruling; carried to this PR's re-cut by the 0a026199 block

## Evidence

- Head reviewed: ev/HEAD.txt. Delta scope: `review_carry.py 0a026199 46f0637251e85de671f9870b60fbb852515c0989` prints FRESH-REVIEW (content commit 69f652ae1 and three main merges). The branch's own diff moved by 69f652ae1 only: the `id:`, the new `if:`, and the `figure-block` closure entry (line-multiset difference of the two three-dot diffs, checked). No `custom_components/` path is in the branch's own three-dot diff, so no production-code risk to extend over.
- Hunk 1, governance.yml: `python3 -I tools/ci/selftest_scope.py static` at the head prints `108 gated step(s), 0 problem(s)` (ev/head.txt). Null control, reverting only the `if:` to `${{ !cancelled() }}`: static prints `UNGATED step 'Show the figure-block renderer refusing its own fixtures'` and `STALE ... extra ['figure-block']`, 107 steps, 2 problems (ev/null_control.txt); restored. `selftest_scope.py --self-test`: 90 checks, 0 failed.
- Hunk 2, selftest_closures.json: `python3 -I tools/ci/selftest_scope.py record --step figure-block` re-measures and leaves the tree byte-identical (git status empty), so files [tests/throwaway_git.py, tools/pr/figure_block.py] and the run_sha are current. With the entry removed, `stale()` reports `missing ['figure-block']`.
- The gated command: `python3 -I tools/pr/figure_block.py --self-test` prints `figure_block self-test: 11 checks, 0 failed` (ev/head.txt), matching the step's grep.
- Merge with main: `git merge-tree --write-tree origin/main 46f0637251e85de671f9870b60fbb852515c0989` rc 0, only the `LEDGER-MERGE: resolved tests/closures.json` auto-resolution, no conflict.
- Packet at read time: `CARRY-AUDIT: 0 finding item(s)`, `FIGURES: 8 resolved, 0 not verified, 0 refused`. VERSION, manifest and notes untouched (the branch's own diff has none).
- Not re-derived: the body's figures beyond the packet's resolution; the mutation lane's log (CI's mutation is success at this head and cited, not re-run).
