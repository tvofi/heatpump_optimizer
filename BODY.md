Root-cause countermeasure for the recurring `mutation` red "a fix edited, moved or deleted a
line the ledger pinned" (three stale-pin PRs on 2026-10-08/09: #2065, #2066, #2070; process
state (c) — step 6d existed, ran and passed on all of them, its unit covering one of the two
directions the CI check refuses). Step 6d (`tools/pr/ci_predict.py`) predicted the forward
direction only — a site the diff adds with no pin, as a warning — not the backward direction
`mutation` refuses: a pin whose site the diff edited, moved or deleted. Its
`completeness_problems` lines now print as a refusing `PREDICT ledger STALE PIN ...` arm,
scoped to the diff like every refusing arm: a stale pin main already carries prints
`STALE PIN ON MAIN` and warns, because no branch can fix it. The remedy line names the only
repair — `mutation-autofix` adds pins and never drops one, so the stale ledger file is deleted
by hand. Full analysis in `dev/audit/rca/R9-RCA-stale-pins.md`, added by this PR.

## Head

`e2821b6dcaa9a00e74b20df6713f5cb5a1f445e6` — the resolution head: `origin/main` `b2b6acd64`
merged in, its two step-6d conflicts resolved so both sides survive: `unpinned()` keeps this
PR's stale-pin prefix extended over main's `added_keys` multiplicity refactor (the ADDED
UNPINNED line now carries the `*N` key), and the 6d self-test keeps main's `0 < x < 3` pmut
plant — its `CMP_BOUND*2` arm needs it — alongside this PR's `pstale`/`pstaleun` plants. The
reviewed code is otherwise unchanged from `63e4eba355`: the three record/delivery paths are
blob-identical to it, `git diff origin/main HEAD` is the same five files (188 insertions, 6
deletions), and both claim files are byte-identical to `origin/main` (`62bf9eaba2`,
`c683379daf`).

## Mutation proof

The planted stale pin and its controls live in the merged `--self-test`, which drives them in a
throwaway clone of this tree: `bash tools/pr/prepr.sh --self-test` → `223 passed, 0 failed`,
including (exact `ok` lines) —

- `6d predicts STALE PIN for a pinned line the diff edits, and refuses on it (rc=1)`
- `a stale pin refuses, unlike an unpinned site: mutation-autofix never drops a pin`
- `a stale pin main already carries warns and names main, never refuses an unrelated branch (null control)`

and the arms main added, which the resolution did not revert:

- `6d still predicts NO RECORDING for a recording the lane edit drops (null control)`
- `and a line holding two comparison mutants is one key carrying its multiplicity`
- `pr-body exempts a main-graded red when the diff only ADDS its own delivery row`
- `7d matches a key whole, never inside a longer key`

Deleting the planted pin's ledger file — the remedy the new line names — returns rc 0 (the
`edit + ledger delete` arm of the round-2 reviewer's harness; the self-test's own delete arm is
the same plant with `pstaleun`).

## Null control

At this head: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`
prints `CI PREDICT: no closures or fast red predicted against b2b6acd64cde (a data-file read is
not seen)`, rc 0 — the merged tree predicts no refusal of its own diff. The planted-side nulls
are in the self-test: `6d predicts ADDED UNPINNED for a guard the diff adds with no pin` at rc
0, and `a stale pin main already carries warns and names main` (above).

## Figures

Rules stated with values; every command run at `e2821b6dc` with `python3` = the 3.14.7 venv on
PATH (`system` 3.11 mis-parses `no-copies`' f-strings).

- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
  --workdir "$D"` → `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (keyed on the mode line,
  not the count; `scope.run` is empty because none of the five changed files sits in any
  script's recorded closure — the remainder is CI's, per `tests/README.md`).
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `bash tools/pr/prepr.sh --self-test` → `223 passed, 0 failed`.
- Standing cost of the new arm at this head: `completeness_problems(load_budgets(),
  inventory())` in isolation times 0.0068 s on the clean tree (0 problem lines); `unpinned()`
  already built the inventory before this PR, so nothing else is added per run. Whole
  predictor on the null tree at this head: `real 3.10` (`/usr/bin/time -p` over the command in
  Null control).
- Check-runs census: this head has no CI run (it is not yet the pull-request head; the current
  one has 0 check-runs — a DIRTY pull request queues no workflow, steward S2, so the merged
  result is settled by CI at the head that includes this merge, not by any run cited here). The
  last head CI ran was `5bcf9d2b20` (blob-identical reviewed code, pre-conflict): `gh api
  repos/tvofi/heatpump_optimizer/commits/5bcf9d2b201951ff8dfb0e414c633546f1bef453/check-runs?per_page=100
  --jq '.check_runs[] | "\(.name)|\(.status)|\(.conclusion)"'` returns 40 lines, all
  `completed`: 25 `success`, 14 `skipped`, exactly one `failure`, `nightly-status`. That
  command's output at this head would return nothing for a commit GitHub has never seen;
  `git merge-tree --write-tree origin/main HEAD` at this head exits 0 (no conflict, no
  `MERGE-CLAIM` marker) — the block the round-3 review named is what this merge resolves.

## Red checks

none turned by this branch, at any head of its range. The one red in the census above,
`nightly-status` at `5bcf9d2b20`, is main's: the check reads nightly kill records this diff
does not reach, and it is the class #2028's `--existing-file` exemption (in this merge's
`body_check`) exists for — the cheaper detector is the census command itself in Figures, run at
each head. This head ran nothing (see Figures).

## Forward-carry

`dev/programme/carries/carry-201.json`: two entries from this PR — the brief_lint
`wood_share:1152` frozen fixture, and the CI-never-runs-`--perturb` gap, a different class
(an instrument CI never exercises) left for D11/D13.

## Friction

`defect-root-cause`: stale: the rule's worked example says a cheaper detector runs an existing
check sooner; here the check existed in CI and only half of it was ported to 6d, so the example
does not say a half-ported check is state (c).

## Cost test

cost(countermeasure, recurring) is 0.0068 s per prepr run at this head (Figures: the
completeness comparison alone; the inventory was already built). cost(defect) is one CI fast +
mutation cycle, about 30 minutes plus the fixer's re-push and re-review — three stale-pin PRs
in one night. 0.0068 s against 3 x 30 min leaves no case for refusing it.

Two arms of the assignment were costed and not built: brief_lint on every production diff
(1 m 45 s measured in round 1 under load, for one frozen fixture that broke in one of three
incidents — refused, the fixture carried instead) and pr-contract Red-checks naming the head
(recorded as an owner decision: the check matches names by design and one stale answer is not a
measured class frequency).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
