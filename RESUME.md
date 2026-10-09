# R9-DBG-2 — resume

State at 2026-10-09, seat worktree `/Users/timmalmstrom/hpo-seats/dbg2/wt`,
branch `handoff/r9-dbg-2` from `origin/main` `a8ce87571`, head
`c901f8f34f0b566033202c1a10f0387a3c205099` after two merges of `origin/main`
(`d8a4bd36f`, then `23d354970`). Neither moves `debugger.py` or
`tests/debug_collect.py`, so the evidence recorded under them describes the head;
`store.py`, `accuracy.py`, `coordinator.py` and `diagnostics.py` did move, and the
drift catchers were re-run at `c901f8f34`.

## Where this group actually stands

R9-DBG-2 landed once already: **#2041** (merged 2026-10-08, and #1940 went over with
it), then **#2056** took it forward (merged). Both delivery rows still read `open`
and the roster's `R9-DBG-2` row still reads `not-started`, so this seat was
dispatched against a stale register. Re-measured against the tree, everything the
brief named is on main: the five priced self-tests under `run_self_tests` inside
`SELF_TEST_BUDGET`, the 8 MiB inline cap and summary fallback
(`debugger.capped`/`download_bytes`, called from `diagnostics.py`), the finalize
button (DBG-1), the translations, and the nightly A16 size check (now the nightly
lane's).

The one line of the pre-study's section 4 table no shipped self-test reported is
row 5's `_tibber_outage_cycles`. Fixed here, plus the ring-gap half of the same row.

## What this branch adds

- `feed_health` gains `row_gaps_h` (the ring's stamps through the existing `spread`:
  median is the install's cadence, max is its worst silence) and
  `tibber_outage_cycles` (the live streak read through the coordinator's published
  `diagnostics_state()` view).
- `debugger._ending_streak` — renamed from `_outage` because
  `tests/closure.py no-copies` refused a production symbol a test already defines
  (`tests/dst_checks.py:2168`).
- `tests/debug_collect.py` +6 checks (64 → 70), `docs/configuration.md` one clause,
  two ledger pins (`_ending_streak.GUARD_OFF`, `_ending_streak.RETURN_DEL`).
- No row field, no `DOMAINS` change, no new store key, no cap change, no export
  change — the architect note's lines all stay the other lane's.

## Next actions for the orchestrator

1. Open the pull request from `refs/heads/handoff/r9-dbg-2` =
   `c901f8f34f0b566033202c1a10f0387a3c205099` (pushed as a fast-forward over the merged
   `a5e969565`; the body and this note ride `refs/heads/handoff-body/r9-dbg-2`).
   `handoff_push.sh` re-derives `## Head` at open, so a main merge before then is
   expected and is not a stale body.
2. Dispatch the fix reviewer at that head (`fix-review.md`, detached worktree, the
   finder's harness — here `tests/debug_collect.py` and the seat probe
   `/Users/timmalmstrom/hpo-seats/dbg2/evidence/outage_probe.py`).
3. Decide the two owed section-4 rows. Neither is buildable in the package:
   `reference_solve` lives in `tests/`, and a per-store `as_dict -> from_dict` round
   trip needs a store-name-to-loader map that does not exist (`DOMAINS` declares field
   domains, `store.py:280`; the loaders are hand-rolled in the coordinator's restore
   path `coordinator.py:3689`/`:7752`). Both are one harness stage repo-side. If they
   are to be worked, they need a new roster group — the roster is not tracked on main,
   so a seat cannot carry them itself.
4. The register: rows `2041.md`, `2056.md` and `plan-table-live.md` are stale (merged
   rows reading `open`, a delivered group reading `not-started`).
   `tools/audit/seat/state_docs.py` owns that; it is the orchestrator's, not a fixer's
   PR.
5. This box cannot run `tests/features.py` honestly: at `origin/main` `d8a4bd36f`, in a
   clean worktree, it fails `R9-F2.1 P3` with `[shipped 110.4366, seeded 110.1297]`
   (1 of 3879), a margin the suite documents as BLAS-dependent. Any prepr run here
   refuses `closures` for that reason alone, on a branch that touches no solver path.

## Traps this seat hit

- `tests/closure.py select --workdir <the worktree>` writes `scope.json`, `scope.run`,
  `scope.skip` and `scope.txt` **into** that directory, and the next run reads them as
  changed files, so it answers `MODE: FULL -- no recorded closure mentions scope.json`.
  Point `--workdir` at scratch outside the worktree and delete the four files if a run
  left them in it.
- macOS zsh has no `timeout` binary; `timeout 3000 python3 ...` exits 127 and the
  background job reports success on the swallowed shell error.
- `policy_lint.mjs` reads `## Forward-carry` with `isNone`, which is
  `^(none|n/a)\b[^\n]*$` on the WHOLE trimmed section: a `n/a:` paragraph is a refusal,
  a `n/a:` line is not. And a body that *mentions* `## Friction` in prose must not be
  spliced by heading name — `s.index("## Friction")` finds the mention, not the section.
- `## Friction` entries must be exactly `<rule_id>: <class>: <evidence>`; `--` in place
  of the second colon is a parse refusal, and a backticked `MODE: FULL` inside the
  evidence is read as a new entry.
