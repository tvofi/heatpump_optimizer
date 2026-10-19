R10-ARCHSCORE-COVERAGE, final part: the card's dead-definition count registered as a gated census. This is the R10-RCA-STRUCTURE-BLIND precondition on part 4.

Part of #2259.
Part of #2235.

#2373 (part 4) closed empty, because #2401 (part 5) had already landed its code. The precondition #2415 carried onto part 4 was never delivered: RCA `dev/audit/rca/R10-N-structure-blind.md` section 5.3, and the group's `brief` and `carry` in `dev/programme/rosters/wave-r10-groups.json`. This branch delivers it. #2415 has since merged (`f0a4acac7`), so the branch is no longer stacked on it. The diff against `origin/main` is three files: `tools/policy/field_coverage.mjs`, `tests/ci_ratchet.py` and `dev/audit/config/bugclasses.json`.

What changes:

- **The census arm takes one instrument per census.** Before this branch, `censusCount` always ran `tests/structure.py` and read `FAIL <gate> `. Now each `CENSUSES` entry names an `instrument`: the `argv` it runs in the tree copy, and how that program refuses on the `gate` row.
  - `STRUCTURE_PY` is the old behaviour.
  - `ciRatchet(job)` runs the ci-ratchet job's own `tests/ci_ratchet.py` functions: `budget_problems` and `compare` over the real `tests/ci_budgets.json`. It takes the score vector from `archscore_metrics(only={job})`.
  - The tree copy also carries `tests/ci_ratchet.py`, `tests/ci_budgets.json` and `tools/audit/archscore/`.
  - A census with no instrument reads no count, so it is REFUSED.
- **`card_dead_definitions` is registered.** Its `gate` is the ci-ratchet row `archscore.card_dead_definitions`, which #2401 recorded. Its plant is one unused top-level card function appended to `www/heatpump-optimizer-card.js`.
- **The class's other unplanted rows are registered too.** Each takes an append plant that moves it by exactly one:
  - `archscore.dead_members`, job `structure`;
  - `archscore.public_unused`;
  - `archscore.unread_private_globals`;
  - `archscore.unused_boundary_imports`, job `layering`.
- **A census registry pass** (`censusRegistry`, run with the census arm).
  - A row in `tests/structure_budgets.json` or `tests/ci_budgets.json` whose key matches `LIVENESS_ROW` (`dead|kept|unused|unread|orphan`), with no census gating it, is REFUSED.
  - A census gating no row is REFUSED.
  - An exemption naming no row is DEAD.
  - The one exemption is `archscore.family_orphan_overrides`, with its reason. That count is family-override validity, not unreached definitions. The append plant cannot reach it either: `family_splits.overrides` reads only the first `ENTITY_FAMILY_OVERRIDES` assignment.
- **A ci-ratchet row is read by string comparison.** One fixed pattern parses the row line, and the key is compared literally. The CodeQL fix: no RegExp is built from the key any more.
- **`tests/ci_ratchet.py`: `archscore_metrics` takes `only`.** It passes the job filter through to `vector.measure`. With no argument the call is unchanged, so the ci-ratchet job still measures the whole vector.
- **`bugclasses.json`, N-structure-blind's `barrier`.** The card's `.js` is struck from `Not reached`. The census-arm sentence now names the card, which the arm reaches through `archscore.card_dead_definitions` (#2401), and the four rows above.
- **`UNGATED` line wording.** It now ends `no refusal on <row>`, because `FAIL` is only structure.py's spelling.

Alternatives, and why each lost (fixer.md step 17):

- **Run the full vector for each card census.** It costs about 45 s per `vector.measure`, twice per census. The `only` filter runs the same card job and the same `compare`.
- **Call `metrics/card.py` `measure` directly.** That skips `vector.py`'s wiring and ci_ratchet's key and comparison, so a vector that stopped deriving the card row would still read as gated (step 11).
- **Monkeypatch `vector.measure` inside the snippet.** It ties the census to `archscore_metrics`' internals. The parameter is the existing filter, exposed.
- **Escape every metacharacter in the key before building the RegExp.** A literal comparison has no escaping to get wrong.

Architecture score: no `custom_components/` file changes. Caps: `node tools/policy/policy_lint.mjs --budgets` rc=0. No ratchet row moves and no raise is made, so no constraint binds.

## Head

`73261ce9b5c636ed8aa9ef19118a12e745af27bd`, which merges `origin/main` at `c3530277373ddf87652858f9ecb0ee1cf36f4347`. That tip was fetched before 09:20 UTC on 2026-10-19, and every figure below was measured at this head. `main` has moved past it since.

## Mutation proof

Each mutant ran `node tools/policy/field_coverage.mjs --only census` from the worktree, then was restored with `git checkout -- <file>`. Afterwards `git status --short | wc -l` printed 0.

- **M1, the row uncapped.** `tests/ci_budgets.json` `archscore.card_dead_definitions` 0 -> 9999. Prints `BLIND census archscore card_dead_definitions: UNGATED, 0 -> 1 with one planted member and no refusal on archscore.card_dead_definitions`, then `FIELD COVERAGE REFUSED`. rc=1.
- **M2, a dead definition dropped.** `tools/audit/archscore/metrics/card.py` `definitions()`: `t in ("function", "class")` becomes `t in ("class",)`, so top-level functions are not enumerated. Prints `BLIND census archscore card_dead_definitions: one planted member moved the count 0 -> 0, not by one`, then `FIELD COVERAGE REFUSED`. rc=1.
- **M3, the card census unregistered.** The `card_dead_definitions` entry is deleted from `CENSUSES`. Prints `REFUSED census registry: row archscore.card_dead_definitions counts unreached definitions and no census plants it`, then `FIELD COVERAGE REFUSED`. rc=1.
- **M4, the escaping control.** The pre-fix `ratchetRow`, which escaped only dots and built a RegExp from the key, is put back. Under `node tools/policy/field_coverage.mjs --self-test` the arm `FAIL a row key holding regex metacharacters or a backslash matches only literally` fails: `SELF-TEST: 1 FAILED`. The arm reads the key `archscore.a\d+` against `archscore.a12` and `archscore.a\dd`, and the key `archscore.a.b` against `archscore.aXb`. The fixed reader matches each key literally, and only literally.
- **Self-test arms added**, all `ok` at the head. rc=0, `FIELD COVERAGE SELF-TEST ok`:
  - every registered census names a gate row, an instrument, a reader and a plant;
  - a census with no instrument is REFUSED;
  - the ci-ratchet refusal reader refuses on its own row only, and the row reader reads its own row only;
  - the four registry verdicts.

## Null control

At the head, unmutated, `node tools/policy/field_coverage.mjs --only census` prints `census archscore card_dead_definitions: 0 -> 1 with one planted member, refused on archscore.card_dead_definitions`, `RESULT read=8 ignored=0 declared_none=0 blind=0 dead=0 refused=0` and `FIELD COVERAGE ok`, rc=0. The card's unplanted count, 0, is #2401's recorded row.

At `1128c3937`, this branch's first base (#2415's head merged onto `913ce1ff5`), the same command printed `RESULT read=3`: the three `structure.py` censuses and no card line.

## Figures

- `node tools/policy/field_coverage.mjs --only census` at the head: 8 censuses read. The rule is one census arm run, which plants one member per registered census in a temporary tree copy and reads the gate row's count before and after the plant. Each is refused on its own row:
  - `dead_methods` 0 -> 1;
  - `dead_top_level_symbols` 1 -> 2;
  - `name_kept_members` 38 -> 39;
  - `archscore.card_dead_definitions` 0 -> 1;
  - `archscore.dead_members` 1 -> 2;
  - `archscore.public_unused` 1 -> 2;
  - `archscore.unread_private_globals` 0 -> 1;
  - `archscore.unused_boundary_imports` 1 -> 2.
  - The run's own `seconds=` field is the arm's cost.
- The class's seams (fixer.md step 8): `jq -r 'keys[]' tests/structure_budgets.json tests/ci_budgets.json | grep -iE 'dead|kept|unused|unread|orphan'` returns 9 rows.
  - 8 are gated by the censuses above. 3 were planted by #2415; 5 are closed in this diff.
  - `archscore.family_orphan_overrides` is exempt, with the reason in `CENSUS_EXEMPT`.
  - From now on the registry pass applies this rule itself, on every census run.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. Ran locally with `PYTHONPATH=tests/hastub`:
  - `env -u BASH_ENV python3 tests/entities.py`: `ALL 2349 ENTITY CHECKS PASSED`.
  - rc=0: `tests/structure.py`, `tests/layout.py`, `tests/closure.py selftest`, `tests/env_drift.py --claims-only <merge base>`, `python3 tools/audit/fold_ledger.py check` (`0 violation(s)`) and `node tools/policy/policy_lint.mjs --budgets`.
  - `tests/harness_headers.py`: `1 of 109 HARNESS HEADER CHECKS FAILED`. The failing check is `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py costs at most 50% of its CPU bound`, at cpu=245.8s against 240s. That is a CPU-time bound on a harness this diff does not touch. It passed at `fbcf5c3e8` on this branch, which ran the same diff over an older main, so this run is host load. CI's run is the authority.

## Red checks

The red check runs at the previous PR head `3797a7c9`, each named with its answer:

- **CodeQL** (check run 117947086079), "Incomplete string escaping or encoding" at `tools/policy/field_coverage.mjs` `ratchetRow`. A real defect in this branch's own code, fixed in this head: no RegExp is built from a key (`## Mutation proof` M4). Cheaper detector: the self-test arm that plants a key holding a backslash and a quantifier. Its standing cost is one in-process call. Carry: dismissed: fixed in this head
- **pr-contract** (check runs 117946599717, 117946735328, 117946942158, 117947971569, 117956179345, 117958071966, 117965425128, 117965678186). The last two printed `CARRY-AUDIT: 6 finding item(s): 0 routed, 6 unrouted`: the previous body's `## Forward-carry` and `## Friction` lines carried no `Carry:` marker. This body routes every item. Cheaper detector: `tools/audit/carry_audit.py check --body`, which `body_push.sh` does not run. That gap is answered under `## Friction`. Carry: dismissed: answered by this body
- **arch-score** (117946614574, 117946601899), **env-matrix** (117946599922), **nightly-status** (117946599045), **validate-hacs** (117946598843), all failed at 07:46-07:49Z; **Analyze (python)** (117946715427) cancelled.
  - The orchestrator attributes these to the 07:47Z API rate limit.
  - Analyze's own annotation names it: "API rate limit exceeded for installation".
  - This seat did not read the other five failed attempts' logs. The API's job log now serves the 08:35Z reruns, and this seat's own reads then hit the same limit.
  - The rate limit is a shared-quota event, not a defect of this diff; a rerun is the answer. Carry: dismissed: rate-limit reds, rerun

## Forward-carry

- R10-RCA-STRUCTURE-BLIND's ledger row `R10-N-structure-blind` in `bugclasses.json` still reads `card language arm carried to #2259 item 2 (#2373)`, with `landed: null`. It is a record, left as written. The record step at this PR's merge should name this PR as the arm's landing. Carry: R10-ARCHSCORE-COVERAGE
- `.github/workflows/governance.yml`'s field-coverage step runs on a pull request only when a listed input changes. `tests/ci_budgets.json`, `tests/ci_ratchet.py`, `tools/audit/archscore/` and the card's `.js` are not listed. So a pull request that uncaps a census's ci-ratchet row (M1's shape) is caught by the schedule run, not on its own run. Budget-raise-gate still refuses the raise itself. The workflow is owned, so the edit needs tvofi's review; the orchestrator routes it. Carry: R10-ARCHSCORE-COVERAGE
- `archscore.family_orphan_overrides` has no planted census; this PR exempts it with a reason. A finder planting it needs a plant that edits the `ENTITY_FAMILY_OVERRIDES` dict in place, which the arm's append-only plant cannot do. Carry: R10-BRIEFS-FOLD

## Friction

- body_push.sh: unenforced: its predictor (`tools/pr/ci_predict.py`) passed a body that pr-contract's carry_audit refused, with 6 items unrouted, so the refusal surfaced only after the PR was updated. Carry: R10-ARCHSCORE-COVERAGE
- hpo-main-checkout-guard: unclear: the user-level PreToolUse hook resolves its target from the tool call's cwd or a literal `git -C`, not a leading `cd`. So `cd <seat worktree> && git merge` was denied as the main checkout, and `git -C <seat worktree> merge`, the hook's own form, passed. Carry: dismissed: user-level hook outside the repository
