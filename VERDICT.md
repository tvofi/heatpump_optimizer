Fix review: merge fe6676d8e461569d5924aaea4b26f3f86af85c1c

bus-nonce: b93c64647e917974e941acbd9a9e1bc2

Round: later (delta over the reviewed head 73797a573acd73668d17d0fc965d33a4b287ad8b, whose verdict was `blocked ... mutation-vacuous`). Scope: the packet's `## Review scope: delta`; no widening, because the PR's own `custom_components/` hunks are byte-identical at both heads (below), so the delta puts no already-reviewed production code at new risk.

## Evidence

- Delta, first-parent: `4532880b25` (ci: pin killed mutants, 3 ledger files), `09fc4b9c43` (merges the repair `768417ad3f`, `tests/entities.py` +20 lines only), `fe6676d8e4` (automatic merge of origin/main `9276ddf6b1`). The PR's own production diff, `git diff e3cb5c019b 73797a5 -- custom_components` against `git diff 9276ddf6b1 fe6676d -- custom_components`, compared on its +/- lines: IDENTICAL (50 lines each).
- Previous block resolved. The new `tests/entities.py` check drives a real coordinator through `async_set_mode(MODE_BOOST)` then `async_set_mode(MODE_COMFORT)` and reads both `diagnostics_state().mode` and the download's `coordinator.mode`. Run through a slice of `tests/entities.py` holding its header, `dt_util`, `strings`, the `_CRED_DATA`/`_CONF_TOKEN` lines and the whole `Diagnostics (D10-12)` section through the new check (`ev/ent_slice.py`, `PYTHONPATH=tests/hastub:tests`):
  - head: `ALL 17 ENTITY CHECKS PASSED`, the new check ok (`ev/slice_head.txt`).
  - M8 `CoordinatorDiagnostics.of(self, self.mode)` -> `of(self)`: FAIL `{'boost': (None, None), 'comfort': (None, None)}`, `1 of 17 ENTITY CHECKS FAILED` (`ev/slice_M8.txt`). This is the mutant that blocked 73797a5; it is now killed.
  - M9 -> `of(self, "boost")` (a constant): FAIL `{'boost': ('boost', 'boost'), 'comfort': ('boost', 'boost')}` (`ev/slice_M9-const-boost.txt`).
  - M10 -> `of(self, "auto")` (the reset value): FAIL `{'boost': ('auto', 'auto'), 'comfort': ('auto', 'auto')}` (`ev/slice_M10-const-auto.txt`). M9 and M10 confirm the two-mode null control: a constant fails one of the two modes.
- A full local `tests/entities.py` run was started and stopped after 40 min on a host at load average 70-160 (I/O-bound in `policy_lint.mjs` git greps); the slice above replaced it for the mutants. The head's full run is CI's: `tests / fast (3.14)` job 137418530820 at this head printed `MODE: SCOPED -- 22 script(s) run, 11 scoped out`, the new check `ok`, `ALL 2762 ENTITY CHECKS PASSED` and `ALL 164 DEBUG COLLECT CHECKS PASSED` (`ev/ci-fast-137418530820.txt`), which matches the body's `ALL 2762` and `1 of 2762` figures (the latter for M8; my slice shows the same single failing check).
- The previous verdict's finding (the body naming `tests/features.py` as the old `killed_by` of pins 700af26e and 3e0e5f0c) is corrected: `## Unpinned sites` now names `tests/entities.py` for both, matching the deleted ledger files.
- The new check leaves the coordinator in `MODE_AUTO` afterwards; `async_set_mode` also voids pending accuracy promises for boost/comfort, and every later check in the file still passes in CI at this head.
- Merge with main: `git merge-tree --write-tree origin/main fe6676d` exit 0 against origin/main 24e3f37620 (`ev/merge-tree.txt`).
- Role file: `fix-review.md` changed on main since this head's merge base (rewording, the selftest-absorb paragraph); this review follows main's text.
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/` and both claim files: no change in the three-dot diff.
- CI: `merge_train.py classify fe6676d --pr 3873` printed `WAIT ... pending: gate red: none` from 00:51Z to 01:10Z, then exit 2 (unreadable): `REFUSE selftests: the head's governance / instrument-self-tests job 137417353350 concluded cancelled, which reads no step: re-run it` (`ev/classify.log`). That job needs a re-run before the merge; this seat posts nothing to GitHub and does not re-run it.
- The one red is `tests / mutation` (job 137417353504), which is in the `owed-reds` set: `MUTATION TABLE REFUSED -- 1922 unpinned site(s) against 1919 ... 3 of them added by this diff`, the three ADDED UNPINNED sites being `boost.py:369 RETURN_DEL`, `coordinator.py:4137 RETURN_DEL`, `coordinator.py:10429 GUARD_OFF` (`ev/ci-mutation-137417353504.txt`). These are the sites the body lists under `## Unpinned sites` as pinned by `mutation-autofix`, and its `## Red checks` answers the red (predicted by `prepr.sh` step 6d; the lane's repair mechanism, `ci-autofix.md`). `tests / mutation-autofix` (137433422807) was queued at 02:30Z. Its pins-only commit will move the head; `review_carry.py` covers that move.

## Findings

- The body's `## Head` section holds two "merges the authored code head" lines, one for fe6676d and one for ee847e2481, a commit that is not an ancestor of this head (a superseded merge). Paperwork, not a block. Carry: dismissed: body paperwork; the next body render at a moved head rewrites the section
