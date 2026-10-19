R10-ARCHSCORE-COVERAGE, final part: the card's dead-definition count registered as a gated census. This is the R10-RCA-STRUCTURE-BLIND precondition on part 4.

Part of #2259.
Part of #2235.

#2373 (part 4) closed empty, because #2401 (part 5) had already landed its code. The precondition #2415 carried onto part 4 was never delivered: RCA `dev/audit/rca/R10-N-structure-blind.md` section 5.3, and the group's `brief` and `carry` in `dev/programme/rosters/wave-r10-groups.json`. This branch delivers it.

The diff against `origin/main` is three files: `tools/policy/field_coverage.mjs`, `tests/ci_ratchet.py` and `dev/audit/config/bugclasses.json`.

What changes:

- **The census arm takes one instrument per census.** Each `CENSUSES` entry names an `instrument`: the `argv` it runs in the tree copy, and how that program refuses on the `gate` row.
  - `STRUCTURE_PY` is the previous behaviour.
  - `ciRatchet(job)` runs the ci-ratchet job's own `tests/ci_ratchet.py` functions, `budget_problems` and `compare`, over the real `tests/ci_budgets.json`, with the score vector from `archscore_metrics(only={job})`.
  - A census with no instrument reads no count, so it is REFUSED.
- **`card_dead_definitions` is registered.** Its `gate` is the ci-ratchet row `archscore.card_dead_definitions`, which #2401 recorded. Its plant is one unused top-level card function appended to `www/heatpump-optimizer-card.js`.
- **The class's other unplanted rows are registered too.** Each has an append plant that moves it by exactly one:
  - `archscore.dead_members`, job `structure`;
  - `archscore.public_unused`;
  - `archscore.unread_private_globals`;
  - `archscore.unused_boundary_imports`, job `layering`.
- **A census registry pass, `censusRegistry`.**
  - A row in `tests/structure_budgets.json` or `tests/ci_budgets.json` whose key matches `LIVENESS_ROW` (`dead|kept|unused|unread|orphan`) and that no census gates is REFUSED.
  - A census that gates no existing row is REFUSED.
  - An exemption that names no existing row is DEAD.
  - There is one exemption, `archscore.family_orphan_overrides`, with its reason in `CENSUS_EXEMPT`.
- **`main()` runs its arms from one table, `RUNS`, in the old order.** `--only` names a key of that table. `RUNS.census` is the registry pass followed by the planted runs. The self-test drives `RUNS.census` itself with a stub run (the review's R2).
- **A ci-ratchet row is read by string comparison.** One fixed pattern parses the line, and the key is compared literally. No RegExp is built from a key, which was the CodeQL alert.
- **`tests/ci_ratchet.py`: `archscore_metrics` takes `only`.** The filter is passed to `vector.measure`'s existing job filter. With no argument the call is unchanged.
- **`bugclasses.json`, N-structure-blind's `barrier`.** The card's `.js` is struck from `Not reached`. The census-arm sentence now names the card, reached through `archscore.card_dead_definitions` (#2401), and the four rows above.

Alternatives, and why each lost (fixer.md step 17):

- Run the full vector for each census: about 45 s per `vector.measure`, and each census runs it twice.
- Call `metrics/card.py` directly. That skips `vector.py`'s wiring and ci_ratchet's key handling and `compare`, so a vector that stopped deriving the row would still read as gated (step 11).
- Monkeypatch `vector.measure` inside the snippet. That couples the census to `archscore_metrics`' internals.
- Escape every metacharacter in the key. A literal comparison leaves nothing to escape.
- Pin the wiring by spawning `main()` in a subprocess. The arm table gives the self-test the same entry `main()` runs, in process.

Architecture score: no `custom_components/` file changes. Caps: `node tools/policy/policy_lint.mjs --budgets` rc=0. No ratchet row moves and no raise is made, so no constraint binds.

## Head

`da6b4520059abb628c8582719df6ec867ae1eab4`, which merges `origin/main` at `05c39d3a6597e02c81f07e771a058da90f8ebb46`. The figures below were taken at this head between 10:20 and 10:47 UTC on 2026-10-19. Main has moved since.

## Mutation proof

Each mutant was run from the worktree and restored with `git checkout -- <file>`. Afterwards `git status --short | wc -l` printed 0.

- **M1, the row uncapped**, measured at `73261ce9b` with the same census code. `tests/ci_budgets.json` `archscore.card_dead_definitions` goes 0 -> 9999.
  - `--only census` prints `BLIND census archscore card_dead_definitions: UNGATED, 0 -> 1 with one planted member and no refusal on archscore.card_dead_definitions`, then `FIELD COVERAGE REFUSED`. rc=1.
  - The round-1 review reproduced it at `733ac350`.
- **M2, a dead definition dropped**, at `73261ce9b`. In `metrics/card.py` `definitions()`, `t in ("function", "class")` becomes `("class",)`.
  - It prints `one planted member moved the count 0 -> 0, not by one`, then `FIELD COVERAGE REFUSED`. rc=1.
  - The review reproduced it at `733ac350`.
- **M3, the card census unregistered**, at this head.
  - It prints `REFUSED census registry: row archscore.card_dead_definitions counts unreached definitions and no census plants it`, then `FIELD COVERAGE REFUSED`. rc=1.
- **R2, the review's surviving mutant**, at this head: M3, plus `censusRegistry` dropped from `RUNS.census`.
  - `node tools/policy/field_coverage.mjs --self-test` prints `FAIL main's census arm runs the registry pass (an ungated row is REFUSED) and then the planted runs`, then `FIELD COVERAGE SELF-TEST: 1 FAILED`. rc=1.
  - Null at this head: `FIELD COVERAGE SELF-TEST ok`, rc=0.
- **M4, the escaping control**, at `73261ce9b`. The pre-fix `ratchetRow` (a RegExp with only the dots escaped) is restored.
  - The self-test prints `FAIL a row key holding regex metacharacters or a backslash matches only literally`, then `SELF-TEST: 1 FAILED`.
  - The review reproduced it at `733ac350`.

## Null control

At this head, unmutated:

- `node tools/policy/field_coverage.mjs --only census` prints `census archscore card_dead_definitions: 0 -> 1 with one planted member, refused on archscore.card_dead_definitions`, `RESULT read=8 ignored=0 declared_none=0 blind=0 dead=0 refused=0` and `FIELD COVERAGE ok`. rc=0.
- The other arms, now run from `RUNS`, are each rc=0 with `blind=0 dead=0 refused=0`: `--only hooks`, `--only budgets`, `--only approvals` and `--only registry`.
- `--only bogus` prints `--only bogus: no such arm`, rc=2.

At the merge base, the round-1 review measured `read=3` at `90557e39e`: the three `structure.py` censuses and no card line.

## Figures

- `node tools/policy/field_coverage.mjs --only census` at this head: 8 censuses read, each refused on its own row. The rule: one census-arm run, which plants one member per registered census in a temporary tree copy and reads the gate row before and after.
  - `dead_methods` 0 -> 1;
  - `dead_top_level_symbols` 1 -> 2;
  - `name_kept_members` 38 -> 39;
  - `archscore.card_dead_definitions` 0 -> 1;
  - `archscore.dead_members` 1 -> 2;
  - `archscore.public_unused` 1 -> 2;
  - `archscore.unread_private_globals` 0 -> 1;
  - `archscore.unused_boundary_imports` 1 -> 2.
- The class's seams (fixer.md step 8): `jq -r 'keys[]' tests/structure_budgets.json tests/ci_budgets.json | grep -iE 'dead|kept|unused|unread|orphan'` returns 9 rows.
  - 8 are gated by the censuses above: 3 planted by #2415, 5 closed in this diff.
  - `archscore.family_orphan_overrides` is exempt, with its reason in `CENSUS_EXEMPT`.
  - `censusRegistry` now applies this rule on every census run.
- Roster read-back: `git show cbdfc9e08395c0e40826b7660175f41825d39fda:dev/programme/rosters/wave-r10-groups.json` shows R10-STAMP and R10-BRIEFS-FOLD at stage `not-started`, holding `R10-N-structure-blind` and `family_orphan` respectively. `git show 557f75372c12d2f9514c21fb20bd4b8df03b5140:dev/programme/rosters/wave-r10-groups.json` shows R10-CI-LAYOUT at `not-started`, holding `governance.yml` and `ci_predict`/`body_push`. Both SHAs are on `handoff/audit-r10-roster`, and 557f7537 is its tip. All three groups are on origin/main's in-tree roster, each `not-started`. `python3 -I tools/audit/carry_audit.py check --body <this body>`, run against that in-tree roster, reads every item routed with 0 bad destinations.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. Run locally with `PYTHONPATH=tests/hastub`:
  - `env -u BASH_ENV python3 tests/entities.py`: `ALL 2350 ENTITY CHECKS PASSED`;
  - each rc=0: `tests/structure.py`, `tests/layout.py`, `tests/closure.py selftest`, `tests/env_drift.py --claims-only <merge base>`, `python3 tools/audit/fold_ledger.py check` and `node tools/policy/policy_lint.mjs --budgets`.

## Red checks

The reds at the round-1 head `733ac350`, read from the check-runs API and the job logs:

- **arch-score** (check run 117997756849). The log prints `gh: API rate limit exceeded for installation` in "Name the pull request and read its body", before any measurement. It is a shared-quota event, and the answer is a rerun. Carry: dismissed: rate limit, rerun
- **validate-hacs** (117997757623). The log prints `aiogithubapi.exceptions.GitHubRatelimitException: API rate limit exceeded for installation`. Carry: dismissed: rate limit, rerun
- **pr-contract** (117997910965, 117998113853, 117998838728). The log prints `gh: API rate limit exceeded` in "Read the body off the API", and then `carry_audit` fails with `FileNotFoundError: /tmp/pr-body.md`. The body was never fetched. Carry: dismissed: rate limit, rerun
- **env-matrix** (117997758266). The failing arm is `pr / nothing skipped in a full clone -- skip required-contexts the GitHub API is unreachable`: the required-contexts read could not reach the API in that window. This diff touches no file that arm reads. Carry: dismissed: rate limit, rerun
- **nightly-status** (117997758338). Its log printed no failing line this seat could read. The round-1 review attributes it to `main` and not to this PR: it reports the nightly runs. Carry: dismissed: not this diff
- **CodeQL**: neutral at `733ac350`. The earlier high alert at `3797a7c9`, in `ratchetRow`, is fixed by the literal row reader (M4). Carry: dismissed: fixed in this branch
- **coverage** and **Analyze (python)** were still running when read.

The CodeQL alert at `3797a7c9` is this branch's own defect. Its cheaper detector is now in the tree: the self-test arm that plants a key holding a backslash and a quantifier, at a standing cost of one in-process call.

## Forward-carry

- **The ledger record row.** `bugclasses.json`'s R10-N-structure-blind RCA row still reads `card language arm carried to #2259 item 2 (#2373)`, with `landed: null`. It is a record and is left as written. The stamp's record step names this PR as the landing. Roster at cbdfc9e0. Carry: R10-STAMP
- **The field-coverage path filter.** `.github/workflows/governance.yml`'s field-coverage step lists none of `tests/ci_budgets.json`, `tests/ci_ratchet.py`, `tools/audit/archscore/`, the card's `.js` or `tools/policy/field_coverage.mjs`. So a pull request that uncaps a census's ci-ratchet row (M1's shape) is not caught on its own run. The control is M1 going red on a PR run. A sibling fold of #2441 already widens that filter on R10-SEAT-SELFTESTS-CI's branch. Roster at 557f7537. Carry: R10-CI-LAYOUT
- **`archscore.family_orphan_overrides`.** A planted census for it needs a plant that edits `ENTITY_FAMILY_OVERRIDES` in place, which the arm's append-only plant cannot do. This PR exempts it, with its reason. Roster at cbdfc9e0. Carry: R10-BRIEFS-FOLD

## Friction

- body_push.sh: unenforced: its predictor `tools/pr/ci_predict.py` passed a body that pr-contract's `carry_audit` then refused, with 6 items unrouted, so the refusal surfaced only after the PR was updated. Roster at 557f7537. Carry: R10-CI-LAYOUT
- hpo-main-checkout-guard: unclear: the user-level PreToolUse hook resolves its target from the tool call's cwd or a literal `git -C`, not from a leading `cd`. `cd <seat worktree> && git merge` was denied as if it ran in the main checkout, and `git -C <seat worktree> merge`, the hook's own form, passed. Carry: dismissed: user-level hook outside the repository
