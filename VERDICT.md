Fix review: merge f7aec2be4ec5cb31d40ae141b536de3c2dcbdff6

bus-nonce: be82af6fda5106556cd899e3329a6695
pending-ci: pending: gate red: none

## Summary

This round is a delta re-review over the blocked head e04a759e943b5fcf01dfd39487d2454c47dd927b. The prior block, test-red on the `_PG_PLAN` scratch fixture, is resolved. Fix commit 92d719ab7f746bd985b8a139fe169e8dbed9d1bd changes only `tests/entities.py`. The `_PG_PLAN` fixture is now a bare `origin.git` cloned from a source repository that holds v1.9.0, v1.10.0 and x9. The release step runs in a `--depth 1 --no-tags` clone of that origin. The v1.10.0 assertion is unchanged. One in-tree null control is added: the release step with `--sort=-v:refname` swapped for `--sort=-refname` must take v1.9.0 and be refused. PR head f7aec2be4ec5cb31d40ae141b536de3c2dcbdff6 is update_pr's merge of 92d719ab with main. Its `tests/entities.py` and `.github/workflows/pages.yml` are byte-identical to 92d719ab's (`git diff 92d719ab f7aec2be -- tests/entities.py .github/workflows/pages.yml` prints nothing). The delta touches no production code, so the scope does not widen (fix-review.md step 12).

## Evidence

- Head reviewed: f7aec2be4ec5cb31d40ae141b536de3c2dcbdff6 (ev/HEAD.txt). Code head: 92d719ab7f746bd985b8a139fe169e8dbed9d1bd. The delta e04a759e..92d719ab is one file, `tests/entities.py`, +21/-8 (ev/delta-stat.txt).
- Merge with main: `git merge-tree --write-tree origin/main f7aec2be` exits 0 with tree 36ad2b8f and no conflict, against origin/main d3d66c40 (ev/merge-tree.txt).
- I wrote my own harness, not the fixer's rehearsal scripts (ev/h/pages_section.py). It slices the Pages section of `tests/entities.py` out of each head's own file, from the line `_PG_WF = Path(".github/workflows/pages.yml")` onward. It pulls in each missing top-level dependency by AST from the same file, then execs the slice with a recording `R`, with the cwd at a detached worktree of that head.
  - Over the section up to the "Classified as its siblings" comment (ev/pages_section_heads.txt, ev/run-*.out): e04a759e gives 3 checks with 1 failing (`the release checkout took 'x9' (rc=128), not v1.10.0`). 92d719ab and f7aec2be each give 4 of 4 checks passing.
  - Over the wider range the body cites (to line 42948 at the new heads, 42935 at e04a759e; ev/pages_section_wide.txt): e04a759e gives 5 of 6, with `_PG_PLAN` the red check. 92d719ab and f7aec2be each give 7 of 7. These match the body's figures.
  - The expected null control holds: red at e04a759e and green at the new head, under my harness.
- Mutation, my own six mutants of the head's `pages.yml` release step, each run through the whole Pages section (ev/mutants.txt, ev/h/mut_pages.sh). All six are KILLED by the `_PG_PLAN` check:
  - `--sort=-refname` took v1.9.0.
  - Dropping the `refs/tags/v*` glob took x9.
  - Reverting to local `git tag --list` took x9, because a no-tags clone holds no tags.
  - Replacing the tag fetch with `true` took x9 at rc 1.
  - Replacing the checkout with `true` took x9.
  - `tail` for `head` took v1.9.0.
  - The fixer's claimed five mutants overlap these. Their rehearsal scripts were not used.
- The in-tree null control is sound. Under the `refs/tags/v*` glob, x9 is excluded, so a string sort over the remaining v1.10.0 and v1.9.0 does take v1.9.0. The check also asserts that the anchor `--sort=-v:refname` is present in the real workflow, so it cannot pass vacuously if the step is respelled.
- The fixture's shape matches the runner. `throwaway_git_clone` (tests/throwaway_git.py:158) builds origin as `--bare`, and the working repository is a `file://` clone with `--depth 1 --no-tags`. The step's `git ls-remote origin` and `git fetch --depth 1 origin +refs/tags/...` therefore run against a real remote.
- Prior findings: the previous verdict's one block, test-red on `_PG_PLAN`, is resolved, as shown above. Its Findings section was `none`.
- The full `tests/entities.py` cannot run in this container, because the HA venv lacks `paho` and `homeassistant`. The section harness above is therefore the evidence. Its skipped imports are recorded in ev/run-*.err.
- CI: `merge_train.py classify f7aec2be... --pr 3894` printed `WAIT f7aec2be4ec5cb31d40ae141b536de3c2dcbdff6 pending: gate red: none` (rc 3) on all 33 runs from about 13:00 to 13:31 UTC (ev/classify.log). It never named a pending context, so the `pending-ci:` line carries the printed text verbatim. The relay posts this verdict only once CI is green at this head. The orchestrator's #3885 expedite waives own-CI, but this verdict does not rely on that waiver.
- Body figures: the 7/7 at 92d719ab, the 5/6 at e04a759e and the `_PG_PLAN` red were re-derived above. The Actions-window figures (139.8/181.8 min, 171 dispatches, 6.7 min) were reviewed in the prior round. They are unchanged and not re-derivable from the tree.

## Findings

none
