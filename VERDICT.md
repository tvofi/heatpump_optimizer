Fix review: blocked 4e5181094ec1c84b7d2552cfd3f184972be9c687 root-cause-unanswered: arch-score and typing went red on this head and the body names neither

bus-nonce: 6f56e1f2ca8cc93a1351b259f5770efc

Measured head: `4e5181094ec1c84b7d2552cfd3f184972be9c687` (detached worktree
`/Users/timmalmstrom/hpo-seats/r9rev-2110/wt`; confirmed still the head of
`refs/heads/fix/r9-dbg-2` by `git ls-remote` immediately before this file was written).
Baseline: the merge base `23d354970fcaababe8e67a5c04c326cc8bc79e49`. Evidence:
`/Users/timmalmstrom/hpo-seats/r9rev-2110/evidence/`.

## Why blocked — two red gate checks the body does not name

The body's `## Red checks` reads: *"None has been read, because this head has no pull
request: the seat hands off the head and does not open or drive a PR, so no check-run
exists to read."* That was true when written and is false at the head as pushed. From the
check-runs API for this head:

- **`arch-score` — failure** (job `114230934131`). Its log:
  `Architecture score: dS -0.0017 WORSENS (inadmissible: coord_footprint 2586->2589)` then
  `FAIL: dS -0.0017 WORSENS; unexplained: coord_footprint 2586->2589. Add a '## Architecture
  score' section with one line per metric: its name and why it rises`. The body has no
  `## Architecture score` section.
- **`typing` — failure** (job `114230992265`). Its uploaded `typing-census.json` artifact
  (id `11672230519`) reads `{"errors": 1, "by_code": {"no-any-return": 1}, "by_module":
  {"debugger.py": 1}}`, against `tests/typing_budgets.json`'s census budget of `errors: 0`.

Both are this diff's, not inherited: `origin/main`'s tip (`c729bb32e`) carries no
`arch-score`/`typing` run at all (both jobs are pull-request-only), and each red is
traceable to the added code — the new module-level `_ending_streak(coordinator)` is a
function whose parameter carries the coordinator, which is what `coord_footprint` charges
(+3 logic statements = the 2586->2589), and
`return coordinator.diagnostics_state().tibber_outage_cycles` from a `coordinator: Any`
parameter under a `-> int | None` annotation is the one new mypy `--strict` `no-any-return`,
in `debugger.py`.

The repository's own contract check reaches the same conclusion and refuses the body for
it — the `pr-contract` job (failure, job `114231116735`) prints:

```
  record   red-history           8 commit(s) between origin/main and this head, every failure conclusion across them: arch-score, typing
  ERROR   [pr-body] /tmp/pr-body.md: check `arch-score` is red and `## Red checks` does not name it.
  ERROR   [pr-body] /tmp/pr-body.md: check `typing` is red and `## Red checks` does not name it.
PR-BODY: 2 error(s) in /tmp/pr-body.md
```

So this is not a reviewer's judgement call: two independent gate checks and the body
linter all say the same thing. Per `fix-review.md` step 11 the trigger is unanswered.

## The fix itself is sound — which is why the class is `root-cause-unanswered`

I looked for a defect in the change and did not find one. `web-fix-wave.js` teaches this
class for exactly this shape: *"the fix itself is sound but the branch turned a check red
and the body does not name the cheaper detector or record that none exists."*

- **The failing-first arm really goes red when the fix is reverted.** Reverting
  `custom_components/heatpump_optimizer/debugger.py` to the merge base and re-running
  `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` exits 1 with
  `KeyError: 'row_gaps_h'` at `tests/debug_collect.py:473`; restored, `git status` clean,
  and the unmutated head prints `ALL 70 DEBUG COLLECT CHECKS PASSED`, rc 0. The test pins
  added behaviour, it is not vacuous.
- **The finder's harness, both ends** (`dev/audit/harnesses/r9_dbg2_selftest_price.py`,
  identical at base and head, over the pre-study's own bundle, sha1
  `cb6e9e3357648afc41adcadaff218f135908cc3d`): five `ok` at both ends, the four untouched
  self-tests flat, `bundle_inline=1` at both, budget 900000 ms against ~93 ms. The
  companion `--repeat 40` crosses the cap as the body says (`bundle_inline=0`).
- **The demonstration re-derives at both ends** with the fixer's own seat probe
  (disclosed as such in the body, not the finder's instrument): base
  `fields_naming_the_silence=0`; head `row_gaps_h {'n': 35, 'min': 0.5, 'median': 0.5,
  'max': 6.5}` and `tibber_outage_cycles 0`, `fields_naming_the_silence=2 # reported`.
  The body's figures reproduce.
- **Spec trace.** Pre-study section 4 row 5 names three feed facts for "was a bad plan
  caused by a starved feed"; the row the body says was missing (`_tibber_outage_cycles`)
  now lands, read through `CoordinatorDiagnostics.diagnostics_state()` (coordinator.py:3090)
  rather than the private member, matching section 7's DBG-2 file set (`debugger.py`).
  Class enumeration: the row states one seam, and the body's rule is the mutation engine's
  (`both sites in the reader`); I found no seam the rule returns that the diff leaves
  undispositioned and the two owed rows of section 4 are named rather than dropped.
- Claim files byte-identical (`git diff --name-only <merge-base>...HEAD -- tests/golden/`
  empty; `env_drift.py --claims-only <merge-base>` -> `ok`). `VERSION`, the manifest
  version and the notes heading are untouched (pr-contract: `no version edit`).
  `git merge-tree --write-tree origin/main <head>` exits 0, no conflict.

## What I did not block on

- The macOS-local `tests/features.py` red the dispatch names: not this diff's, and I did
  not block on it. I could not yet confirm it green from check-runs — CI's `closures` job
  was still `pending` at every pass I made — so I record `closures` as *not concluded*
  rather than green. The diff touches no solver path.
- `nightly-status` and `delivery-status`: both green at this head.
- One figure I could not re-derive: the body's `bundle_bytes=588446` / +202 B. I measured
  588245 (base) -> 588448 (head), +203 B. Direction and magnitude agree; the exact byte
  figure did not reproduce on this box.
- Two dispatch notes, neither a block: the brief path `tools/audit/briefs/fix-review.md`
  no longer exists at `origin/main` (its content was lifted to
  `dev/governance/roles/fix-review.md` by `bc0f17ddb`), which I read; and the debugger
  pre-study itself is not in the tree at this head (it lives at
  `tools/audit/round9/prestudy/debugger-prestudy.md` on `handoff/r9-dbg-0` = `eae236d66`),
  so "re-read at this head" resolves to the handoff ref, whose blob matches what the body
  cites.

## Round

This is the second pass of R9-DBG-2, below `fixer.md`'s three-round re-cut threshold.
