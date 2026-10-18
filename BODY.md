R10-RCA-HARNESS-FRICTION: the root-cause analysis for four friction issues the governance cron filed in `v7.0.0..origin/main`: #2331 (`harness`), #2353 (`class-open`), #2409 (`mutation-vacuous`) and #2410 (`mutation (family)`). Record: `dev/audit/rca/R10-RCA-HARNESS-FRICTION.md`.

Cause: a contract step that defines a block class does not teach the word `VERDICT_CLASSES` carries for it, so one obligation keys under several friction words. `fix-review.md` step 6 taught `blocked <sha> harness: class-open <seam>` (#1414, `6bc932db`), which keys `harness`: 18 of the 21 `harness` entries open with `class-open`, and the cron filed one obligation twice (#2331, #2353). Step 1 taught no word ("the test is vacuous and the PR is blocked"): the mutation obligation keyed on 7 PRs under four words, 3 of them `mutation-vacuous` (#2409). Process state (c): reviewers followed the examples, and `check-wave-script.mjs`'s example arm passed them, its unit the first class word only.

The commits:

- `99df2e90` (**policy**): step 6 reads `blocked <sha> class-open: <seam>`.
- `38051413` (**policy**): step 1 reads `blocked <sha> mutation-vacuous: <mutant>`; step 8 drops a clause restating its own lead, to pay the tokens.
- `f1ff6d27`, `a1e12b86`: the record, its evidence and the `bugclasses.json` `_rca` entry, re-taken at current main.

The detector (an arm refusing a contract example whose reason opens with another taught class) is **not** in this PR: open #2390 edits `tools/policy/check-wave-script.mjs`, and the orchestrator ruled this group leaves that file alone. It is held as `dev/audit/rca/harness-friction/detector.patch`, shown failing at main and passing at the head (below).

#2410 is not this record's cause: the family arm in `tools/policy/policy_lint.mjs` fires when one member alone carries the whole union (the family's 3 PRs are `mutation-vacuous`'s 3), contrary to its own comment. Record section 6; owner named under Forward-carry.

Closes #2331. #2353 and #2409 close on this record; the orchestrator closes them by hand after merge.

## Head

4cfac180dfb762d27ee7c50e23e529e4b6c6de84, merge base 07a09406a1cc97076a6f28581f87f313b322a6b6 (2026-10-18). The last commit is a merge of origin/main touching none of this PR's files; the checks above were re-run on it (`check-wave-script.mjs` 189/0, `--budgets` 2444/2451, `tests/structure.py` passed).

## Approval

`dev/governance/roles/fix-review.md` is policy. Steps 1 and 6 each change one example spelling, and step 8 loses one restating clause; the edits address state (c). tvofi approves at merge under mandate 6175172275. This seat approves nothing.

## Mutation proof

`node tools/policy/check-wave-script.mjs`, each on a scratch copy of the tree named:

- This head with step 1's word misspelt `mutation-vacous`: rc=1, `188 passed, 1 failed`: `FAIL fix-review.md teaches block class "mutation-vacous", and VERDICT_CLASSES carries it`. The existing arm pins the spelling.
- This head with step 1 restored to main's prose: rc=0, `187 passed, 0 failed`. No arm pins that a step teaches its word; that arm belongs in `check-wave-script.mjs` and is carried with the detector.
- origin/main plus `detector.patch`: rc=1, `189 passed, 1 failed`: `FAIL fix-review.md teaches "class-open" as a reason under another class: blocked <sha> harness: class-open <seam>`.
- This head plus `detector.patch` with its predicate mutated to `return null`: rc=1, `190 passed, 1 failed`: `FAIL the shadow predicate fires on the #1414 spelling (negative control)`. The arm cannot go green by finding nothing.

## Null control

This head: rc=0, `189 passed, 0 failed`. This head plus `detector.patch`: rc=0, `191 passed, 0 failed`; the arm's null control (`harness: class-rule-missing`, an untaught reason) passes, and over every example in `dev/governance/roles/` and `dev/governance/dimensions/` the arm fires nowhere. The `FAIL (probe, expected) threw: deliberate` line prints on every run and is not counted.

## Figures

- `harness` 13 PRs / 21 entries, `class-open` 4 / 5, `mutation-vacuous` 3 / 3, `mutation (family)` 3 / 3, `test-vacuous` 2 / 2, `vacuous-check` and `mutant-survives` 1 / 1: printed by `node tools/policy/policy_lint.mjs --stats --since v7.0.0` (at `176851e9`, 129 merged PRs, 67 with a parsable verdict), saved as `dev/audit/rca/harness-friction/stats_v7.0.0.txt`.
- 48 blocked verdicts over the 125 first-parent merges at `106af95a`; the step-6 refusal 23 of them over 13 PRs, the `harness` residue 2 PRs (#2283, #2329), median 131 min to the next verdict: printed by `python3 dev/audit/rca/harness-friction/rounds.py <dir>` over the per-PR first lines, output `dev/audit/rca/harness-friction/blocked_rounds.tsv`.
- 8 of 17 `VERDICT_CLASSES` words taught by a contract example at this head: the `node -e` read in record section 4.
- `fix-review.md` at 140/140 lines, 2444/2451 tokens (was 2449): printed by `node tools/policy/policy_lint.mjs --budgets`.

## Red checks

none

## Forward-carry

- The detector and the step-presence arm go to the first group that edits `tools/policy/check-wave-script.mjs` after #2390 merges: owed as an orchestrator roster carry (a fixer writes no roster), with `detector.patch` and record section 7 as the control.
- #2410 (the `policy_lint.mjs` family arm re-filing a member's own occasions, and its member list missing the step-1 synonyms) goes to a new group on `tools/policy/policy_lint.mjs`; R10-POLICY-LINT-STATS is done, and open #2406 and #2408 edit that file.
- #2409's substance (6 of its 7 PRs are tooling-only diffs where the CI `mutation` lane draws no mutant) is already in O10-policy-fixer-md's brief, item 1.

## Friction

none
