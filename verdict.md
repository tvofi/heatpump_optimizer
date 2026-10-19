Fix review: blocked 733ac35089522bac79c89fe7d28c4860d9f0c0a6 carry-missing: not carried to R10-BRIEFS-FOLD

bus-nonce: 1b25298706096471210b7f1c50656467

Round 1: the PR has no earlier `Fix review:` comments. Measured head `733ac35089522bac79c89fe7d28c4860d9f0c0a6` (ev/HEAD), which is still the PR head and `origin/fix/r10-archscore-census` at verdict time. Merge base `90557e39e`; origin/main is `05c39d3a6`. The role contract has not changed between the merge base and origin/main.

## Blocking

**Step 10: the forward-carry is not in the tree.** `## Forward-carry` item 3 routes the finding "`archscore.family_orphan_overrides` needs an in-place `ENTITY_FAMILY_OVERRIDES` plant, which the append-only plant cannot do" to `Carry: R10-BRIEFS-FOLD`. At roster head `1283f9087` (`handoff/audit-r10-roster`, ev/roster-head.txt, ev/roster-1283f9087.json):
- R10-BRIEFS-FOLD's `brief` (4587 chars) and `carry` (6780 chars) contain no `family_orphan` and no `ENTITY_FAMILY_OVERRIDES`.
- `git grep` finds neither string under `dev/programme` or `.claude/workflows` on the roster branch, on origin/main or at this head.
- The body names no roster SHA, which `finding-propagation.md` "Enforcement" requires for a roster carry.

So the carry exists only in this PR's body. That is `fix-review.md` step 10's `carry-missing`.

Item 2, the `governance.yml` field-coverage path filter, is routed to `Carry: R10-ARCHSCORE-COVERAGE`. That group's own brief does not hold it either: no `governance.yml` string is in its brief or carry. The body calls this PR the group's final part, so once it merges the group is `done`, and `finding-propagation.md` says a done group is not a destination. The claim itself checks out at this head: `.github/workflows/governance.yml:222` lists none of `tests/ci_budgets.json`, `tests/ci_ratchet.py`, `tools/audit/archscore` or the card's `.js`. It also omits `tools/policy/field_coverage.mjs` itself; the step runs the base's pinned copy. Carry this item to a live destination (a later group's brief, or a `dev/programme/carries/carry-<N>.json`), with its control: M1's uncap shape staying green on a PR run. Carry: R10-ARCHSCORE-COVERAGE

## Non-blocking: a mutant survived on a line the body names

**R2** (ev/R2.patch) unwires `censusRegistry` from `main()` and also deletes the card census entry (M3). Result: `--only census` gives `RESULT read=7 ... refused=0`, `FIELD COVERAGE ok`, rc=0 (ev/R2-census.txt). The self-test also passes, rc=0 (ev/R2-selftest.txt).

The registry's four self-test arms call `censusRegistry` directly, so nothing pins the wiring line "`censusRegistry`, run with the census arm". M3 shows the registry refusing only while that line is present. A self-test arm that drives `main`'s census branch with a stub `censusRun` would pin it. Carry: R10-ARCHSCORE-COVERAGE

## Verified at this head (finder's instrument: `node tools/policy/field_coverage.mjs --only census`, PYTHONPATH=tests/hastub)

- RESULT head null: `read=8 ignored=0 declared_none=0 blind=0 dead=0 refused=0 seconds=101.0`, `FIELD COVERAGE ok`, rc=0. All 8 per-row figures match the body exactly: 0->1, 1->2, 38->39, 0->1, 1->2, 1->2, 0->1, 1->2 (ev/null-head-census.txt).
- RESULT base `90557e39e`: `read=3`, the three structure.py censuses only (ev/null-base-census.txt). This matches the body's account of the base, measured here at the current merge base rather than at `1128c3937`.
- RESULT M1 (`ci_budgets.json` card row 0->9999): `BLIND ... UNGATED, 0 -> 1 ... no refusal on archscore.card_dead_definitions`, REFUSED, rc=1. Matches the body.
- RESULT M2 (`card.py:238` `("class",)`): `moved the count 0 -> 0, not by one`, REFUSED, rc=1. Matches the body.
- RESULT M3 (card entry deleted): `REFUSED census registry: row archscore.card_dead_definitions ...`, rc=1. Matches the body.
- RESULT M4 (pre-fix RegExp `ratchetRow`), `--self-test`: `FAIL a row key holding regex metacharacters or a backslash matches only literally`, `SELF-TEST: 1 FAILED`, rc=1. Matches the body.
- RESULT R1 (my mutant: ci-ratchet `refuses` always false): the self-test arm fails, and the census run prints UNGATED for all five archscore censuses (ev/R1-*).
- RESULT R4 (my mutant: `LIVENESS_ROW` narrowed to `dead|kept`): self-test arm `a liveness row no census gates is REFUSED` fails.
- RESULT R5 (my mutant: no-instrument guard removed): the self-test crashes, rc=1.
- Self-test at head: `FIELD COVERAGE SELF-TEST ok`, rc=0, 31 ok lines.
- Class rule: `jq -r 'keys[]' tests/structure_budgets.json tests/ci_budgets.json | grep -iE 'dead|kept|unused|unread|orphan'` returns 9 rows (ev/class-rule.txt). That is 8 gated plus `family_orphan_overrides` exempt, the same 9 case-sensitively. No seam is open beyond the body's disposition.
- The merge with origin/main is clean: `git merge-tree --write-tree origin/main 733ac35089522bac79c89fe7d28c4860d9f0c0a6`, rc=0, no conflict.
- `VERSION`, the manifest version, the notes heading and `tests/golden` are untouched: the three-dot diff is empty, and pr-contract printed "no version edit". No claim file is touched and no fixture moves, so step 4 is vacuous.
- Step 14: no budget, closure, INERT or score file moves.

## Not verified

- The body's local-gate figures (`ALL 2349 ENTITY CHECKS PASSED`, `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, harness_headers `1 of 109`). I did not re-run them, so I report none of them as confirmed.

## CI at this head (check-runs API, ev/check-runs.txt)

Red: arch-score and validate-hacs (both an installation API rate limit, before any measurement), pr-contract twice (`carry_audit` FileNotFoundError: the body was never fetched), env-matrix (1 of 16 declared outcomes failed; I did not read which arm), and nightly-status, which is not this PR's. Still running at read time: coverage and Analyze (python).

The body answers reds at the previous head `3797a7c9`, not these. No pr-contract run has yet checked this body, so step 11's `root-cause-unanswered` cannot be posted yet. I am not using it as the verdict class. Needed on the re-cut: re-runs of arch-score, validate-hacs and pr-contract, and the env-matrix failing arm named and answered in the body. Carry: R10-ARCHSCORE-COVERAGE
