Fix review: merge 559277673d196b1655ff0e57a5cb771b7ca56ceb
bus-nonce: 819e21f3020d56a03d20aa823a71a15c

Round 1, full scope: three-dot diff `cb8edb65a5...559277673d`, 2 files (`tests/features.py`, the PR's own row `dev/programme/delivery/3815.md`), from a detached worktree at the head. `fix-review.md` at the merge base equals main's.

## Evidence

- Test-only: no file under `custom_components/`; `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and both budget files are untouched. The check's name is unchanged.
- Mutation, re-run by me with `features_block.py` over the changed block (`ev/block_runs.txt`): headroom mutant (`- margins - 0.1`) gives `2 of 2 FEATURES BLOCK FAILED`, floor 19.899940 misses `20 - 1e-3` by about 0.1 K; clip mutant (`band * 0.5`) gives `2 of 2 FEATURES BLOCK FAILED`, its peak equals the unlifted one (20.241412) so the strict `> none + 1e-3` clause fails, and its floor 19.583225 fails too. The changed check goes red under both mutants on its own, not only through the gap check. Unmutated head: `ALL 2 FEATURES BLOCK PASSED`.
- Tolerance justified: with a probe tolerance of 1.0 K the unmutated head prints `lift min past 3 h=19.999999`, so the solver holds the floor only to about 1e-6 K, which is the old `20.0 - 1e-6` bound itself. The old clause sat on the solver's convergence edge, and a kernel-level float change explains the SkylakeX reds without a product change. 1e-3 K is 100 times under the headroom mutant's effect and about 240 times under the 0.24 K peak rise, so it hides no physical defect.
- Null control: `max |zeros-none|=0 K` locally; the allclose relaxation only absorbs a cross-kernel difference, and the peak clause became stricter (`+ tol`), not looser.
- Head and author: live head 559277673d196b1655ff0e57a5cb771b7ca56ceb, author `hpo-author[bot]`. `git merge-tree --write-tree origin/main` rc 0.
- Checks: `tests / fast (3.14)` was still queued when read; this verdict cites CI for the suite and asserts nothing about it.

## Notes (non-blocking)

- Note: unverified-environment: the local BLAS is Accelerate, not OpenBLAS SkylakeX; which clause failed on SkylakeX is inferred from the 1e-6 edge above, and this PR's own fast run prints the 6-decimal figures. Carry: dismissed: evidence, not a finding
