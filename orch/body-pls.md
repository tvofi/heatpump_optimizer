Three defects in the statistics half of `tools/policy/policy_lint.mjs` (roster group R10-POLICY-LINT-STATS). Each one gave a `--stats` row two definitions, or none.

- **D13-s2-02 (I4, medium).** `statsHistogram` bumped every re-verification of a moved head into the verdict map, under the same `head-moved` key a reviewer writes as a block class. Over `v6.7.16..17f1c55fad1b`, that row held 133 entries against 4 blocked verdicts naming the class. Fix: the verdict map now holds only the verdicts it parsed, so its entries sum to the parsable verdicts. The rework row is `rounds.reverify` itself, the same object the STATS ROUNDS line already counts, under the new export `REWORK_KEY` (`head-moved (rework)`). It prints as its own table and CENSUS kind (`rework`), and `statsFindings` proposes it as its own arm. The key carries a suffix, like a family row (`<name> (family)`). Without it the census would hold one key on two rows, and `friction_issues.mjs` refuses a census whose row count disagrees with its summary.
- **D13-s2-51 (I4, low).** `frictionKey` looked its id up in an index built from the corpus's canonical spellings without canonicalising the id. So `dev/governance/roles/fixer.md` and `tools/audit/briefs/fixer.md` got two keys for one contract. Fix: one `canon()` around the stripped id, before all three lookups (bare, no-extension, stem). `canon` is the one `counts.mjs` already exports and `trackedFiles` already uses.
- **D13-s1-01 (I3, weakened low).** The coverage line gave the merges with no parsable verdict as one capped list. A record-autofix merge, which `delivery-status-tracking.md` exempts from review, could not be told apart from a `fix` merged without one. Fix: `statsHistogram`'s `coverage.byClass` splits the window by the title's conventional type (`type(scope)!:`). An untyped title is `(untyped)` and a merge that was never fetched is `(unfetched)`; neither is guessed. The new `statsCoverageClassLine` prints the split under `STATS COVERAGE`. `fetchWindow` keeps `title` from the `/pulls/<n>` answer it already fetches, so this costs no extra request.

Alternatives considered:
- Rename the rework row inside the verdict map (for example `head-moved (rework)` as a verdict-class key). Rejected: the verdict table would still mix a non-verdict row into the verdict population, and its entries would not sum to the parsable verdicts.
- Keep a separate rework counter beside `rounds.reverify`. Rejected: that is a second definition of one count. The row is that object, which the check `and the rework row is the rounds line's re-verification part, one object` pins.
- Delete the rework row and rely on the STATS ROUNDS line. Rejected: it would remove #1405's working proposal arm ("[policy] recurring friction" for rework).
- D13-s1-01's other fix scope, requiring a verdict before a record merge, is a policy decision for the owner and is not taken here. The split makes the gap readable.

`policy_lint.mjs` is pinned: `governance.yml` restores it from the base before each pull-request job. So this change takes effect for later pull requests, not this one's own policy jobs (roster carry).

Part of #2220. That issue's other finding, D11-s1-01, belongs to roster group R10-PRE-EDIT-HOOK.

Closes #2221.

## Head

`e6f3837585f0aa83952eb4828c4576587fd50c07` merges the authored code head `c5079e654bc2fdaab2f3caa2ffe6a8d51d0abf36` and then merges origin/main `74cf47b9c` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`c5079e654bc2fdaab2f3caa2ffe6a8d51d0abf36`, the round-1 repair on top of `48d926c1c`, the bot's `ci: merge main` of `8747bbfc4`. `tools/policy/` and the round-10 D13/D14 harnesses are unchanged between the cut and that merge base (`git diff --quiet 694120d5a 8747bbfc4 -- tools/policy/ dev/audit/rounds/round10/D13 dev/audit/rounds/round10/D14`), so the harness figures below still hold. The branch was cut from `694120d5a`. Its commits are:
- the failing test `086ea61e6`;
- the fix `8dcce67d5`;
- the layout repair `8c13fd59e`, which points the new check at `tools/policy/policy_lint.mjs` because `tests/layout.py` refused the retired `.claude/workflows/` spelling;
- merges of main (`70706527e`, `12aa30386`, the delivery row `47f766f04`, and `48d926c1c`);
- the round-1 repair `c5079e654`, which answers review comment 6200939369 (`docs-code-mismatch`). It rewrites the `REWORK_CLASS` comment in `policy_lint.mjs` so the `head-moved` row has one definition (the deleted bump is described only as history). It also rewrites the `friction_issues.mjs` header, which now says rework files as `head-moved (rework)` and that the bare `head-moved` is the verdict-class row. The same commit updates that file's self-test sample line to the current passing-verdict text. Comments and one self-test string only; `node tools/policy/friction_issues.mjs --self-test` printed `102 passed, 0 failed`.

## Mutation proof

Each mutation was applied to `tools/policy/policy_lint.mjs` at `8dcce67d5`. Then `PYTHONPATH=tests/hastub python3 tests/entities.py` ran (seat venv python 3.14), and the file was restored. The script is `R10-POLICY-LINT-STATS-ev/mutants.py` in the seat scratch.
- M1: restore the deleted line `if (kind === 'reverify' && cur.word !== REWORK_CLASS) bump(verdicts, REWORK_CLASS, pr)`. Result: `3 of 2324 ENTITY CHECKS FAILED`. The failing checks are `the verdict table's head-moved row holds only the verdicts whose class word a reviewer wrote, and its rows partition the parsable verdicts (#2221)` (cell [3, 3], 12 entries), `and the passing row is left exactly as it was, and the verdict row the wave's head-moved word keys holds no rework round ...`, and `and the split tracks the verdict before the round rather than a constant`.
- M2: drop `canon(` from `frictionKey`'s `bare`. Result: `1 of 2324` failed: `a moved policy file named at its live path and at its canonical spelling reaches one friction key, the canonical path (#2221)` (34 moved corpus files split).
- M3: make the class function return `'(untyped)'` for every pull request. Result: `2 of 2324` failed: `the stats mode splits the merges carrying no parsable verdict by the title's type ... (#2220)` and `and the split tracks the titles rather than a constant`.
- M4: make the rework row an empty Map. Result: `5 of 2324` failed: the two #1405 rework-cell checks, `the rework row counts a re-verification ... (#1549)`, `and the rework row is the rounds line's re-verification part, one object ... (#2221)`, and the flipped null control.
- Failing test first: at `086ea61e6` (the test, no fix), `10 of 2324 ENTITY CHECKS FAILED`, and these are exactly the ten checks above. The other `FAIL` lines in that log (`a3:`, `a4:`, `hb:` and the like) are self-test demonstrations inside passing checks. They print at every head, the merge base included.

## Null control

- `sameHead` and `noFirstHead`: two verdicts on one head, or a first line the grammar refuses, put nothing in the rework row (check `and a verdict naming the same head twice, or a first line the grammar refuses, is not rework`).
- `not-a-policy-file.md` keeps its own spelling as its friction key.
- With every fetched merge carrying a verdict, the class line reads `record 0 of 2` and `fix 0 of 2`, and the never-fetched merge still reads `(unfetched) 1 of 1 (#6)`.
- The unmodified tree (`694120d5a`) prints all ten new or retargeted checks red, as listed above.

## Figures

The finder's window payload is `window.json` (sha1 `8c4de8e205f9ec8cdc2916cbe011a94a2d4156b8`), from `python3 dev/audit/rounds/round10/D13/s2/fetch_window.py v6.7.16 17f1c55fad1b`: 185 PRs, `api_failures` 0. The harnesses below are the tree's files, byte-identical to the finder's at `d23205d13` (sha1 checked). Each was run at the cut `694120d5a`, whose `tools/policy/` equals the merge base `586455741`'s (the base's `policy_lint.mjs` checked out over the branch's) and at the head.
- `HPO_PLANDATA=$(mktemp -d) node dev/audit/rounds/round10/D13/s2/blocks_friction.mjs window.json` (sha1 `fce9a961`). Base: `PROD verdict_row[head-moved] prs=71 entries=133` against `RESULT block_class[head-moved]=4`. Head: `prs=4 entries=4`, with the same `block_class[head-moved]=4` and `blocked_verdicts=124`. Its friction arm moves one entry onto a budget file (`friction_prod_key_is_budget_file` 66 -> 67), the #2063 live-path `fixer.md` entry. The two remaining `DISAGREE` rows (`fixer` and `budgets`) are the role-name carve-out documented above `policyKeyIndex` and a basename the harness's looser rule maps onto a fixture file. Both are deliberate, not this finding.
- `node dev/audit/rounds/round10/D13/leads/friction_key_split.mjs` (sha1 `e1a54186`). Base: `split_keys=34` of `moved_corpus_files=34`, with `--perturb` giving 0. Head: `split_keys=0` of 34.
- `node dev/audit/harnesses/r10_stats_window.mjs window.json` (new, step 18, re-derives D13-s1-01 and D13-s2-02 offline from the production symbols). Base: `verdict_head_moved=133`, `verdict_total=563` against `parsable_total=434`, `rework_entries=absent`, and `STATS COVERAGE BY CLASS: (absent)`. Head: `verdict_head_moved=4` = `blocked_head_moved=4`, `verdict_total=434` = `parsable_total=434`, and `rework_entries=130` = `reverify_entries=130`. The class line reads `record 16 of 32`, `fix 2 of 66 (#2173 #2203)`, `closure 1 of 2 (#2196)`, `docs 1 of 14 (#2197)`, `policy 1 of 6 (#2005)` and `test 1 of 6 (#2179)`, with 0 in every other class. That is the finder's 22, which `STATS COVERAGE` also prints at both ends (`163 of 185`). The finder's `dev/audit/rounds/round10/D13/s1/yield.mjs` reads a live `<since>..origin/main` window and crashes in `verdictsOf` at a moved main (the verifier's V1), so this harness replaces it as the re-runnable arm.
- Live, the full printing and census path: `GITHUB_TOKEN=$(gh auth token) node tools/policy/policy_lint.mjs --stats --since 17f1c55fa` at the head (26 merges). It prints `rework (PRs / entries): 2 / 2 head-moved (rework)` and `CENSUS rework 2 2 head-moved (rework)`, plus the class line `record 11 of 12 ...; fix 0 of 5 ...`. `CENSUS: 9 key(s)` equals the 9 distinct `CENSUS` row keys, which is the equality `friction_issues.mjs`'s `parseHistogram` requires.
- Class seams (step 8): `python3 dev/audit/rounds/round10/D14/sweep-I4/enumerate.py .` (the #2221 enumerator).
  - Base: `SEAMS 29 hist_mixed 2 canon_unguarded 25`.
  - Head: `SEAMS 30 hist_mixed 0 canon_unguarded 21`.
  - Clean fixture: `hist_mixed 0 canon_unguarded 0`.
  - Dispositions:
    - The two `MIXED` `bump(verdicts, ...)` rows: closed here (now `single`).
    - The six `frictionKey` `POLICY_KEY_INDEX` rows: closed here (now `guarded`).
    - The 19 remaining policy_lint and budget_raise_gate rows: the same seams `dev/audit/rounds/round10/sweep-I4.md` dispositions as guarded or not applicable, shifted +39 lines by this diff.
    - The 2 new `tests/entities.py` `_FK_MOVED` rows: not applicable. They are the new check's own enumeration over `(live, canon(live))` pairs.
  - #2220's I3 enumerator arm B is `yield.mjs`, replaced as above. Its arm A (`hook_shape_seams.py`) belongs to R10-PRE-EDIT-HOOK.
  - One reader per concept: the enumeration returns one production reader for each of the two concepts (`statsHistogram`'s verdict rows and `frictionKey`), so there is no reader pair to register in `tools/policy/agreement.mjs`. The invariants are pinned in `tests/entities.py` instead. The sweep's proposed agreement registration is the owed I4 class RCA's countermeasure decision.
- Scoped gate: `python3 tests/closure.py select --diff <merge base>` printed `MODE: SCOPED -- 2 script(s) run` (`tests/entities.py`, `tests/harness_headers.py`). At the head, `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2325 ENTITY CHECKS PASSED` and `tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`. The `run_always` lines printed: `tests/env_drift.py --claims-only 586455741` (at `12aa30386`; the round-1 repair re-ran entities, harness_headers, policy_lint, structure and layout at the head, layout reporting `GUARD: 0 refusal(s)` against `8747bbfc4`) `claims hygiene: ... ok`, `tests/closure.py selftest` `ALL 115 closure shrink pins PASSED`, and `tests/layout.py` `GUARD: 0 refusal(s)`. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)` and `FIXTURE ok: 92 error(s) hold 243 pins`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff <merge base>`: `dS +0.0000 NULL`. `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- Inert read: the new harness is added by hand to `tests/harness_headers.py`'s `inert_reads` in `tests/closures.json` (one line, as in 387128bb).

## Unpinned sites

none: `prepr.sh` step 6d reports that the diff adds no unpinned mutation site.

## Red checks

none

## Forward-carry

none. No later stage's work changes. The `head-moved (rework)` key changes the title of any future rework friction issue. Every earlier `[policy] recurring friction: head-moved` issue is closed, and `friction_issues.mjs` keys on the title as printed, so nothing has to follow.

## Friction

none
