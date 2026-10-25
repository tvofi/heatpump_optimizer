Fix review: merge 72a2e211961462e577a0f2389ba000ffc4777c97

bus-nonce: e46fdbe75b8c0069fd90d4254a0f0dc7

Round 1. Measured head `72a2e211961462e577a0f2389ba000ffc4777c97` (still the PR head at verdict time). Merge base `da12aa37dee15b9e9567bd6c848493436f2592dd`.

## Findings

none

## Evidence

- Diff, three-dot against the merge base (`ev/diff.txt`, `ev/merge.txt`): two files only, `dev/governance/roles/proposal-triage.md` (lines 8-9) and the PR's own row `dev/programme/delivery/2821.md`. Wording: "keeps its own route" -> "keeps its route"; "One sonnet seat at medium effort: judgement with an oracle." -> "One opus seat at medium effort: rulings are checked against code." Matches the brief exactly. VERSION, manifest version and RELEASE_NOTES untouched; no claim file, no budget file touched.
- Caps (`ev/lint.txt`): `node tools/policy/policy_lint.mjs` exit 0 at head and at base, TOTAL 0 errors across 50 files. `--budgets` row for proposal-triage.md at head: 36 of 36 lines, 489 of 489 tokens (also 36/36, 489/489 at base). `git diff da12aa37d -- dev/governance/config/` is empty: no budget leaf raised.
- Null control (`ev/null_control.txt`): one line appended -> lint exit 1, "37 lines exceeds its cap of 36" and "about 493 tokens ... exceeds its cap of 489". Restored: exit 0.
- The body's "494 against 489" for the ruled wording re-derives: with "keeps its own route" plus "a ruling's claims are checked against the code", `--budgets` prints 494/489. With only the second clause ruled and "its route" trimmed, 493/489, so both trims were needed. The ruling text's "word count stays well under its cap of 489" was wrong; the body states the overrun and pays it by trimming, never by a raise.
- Revert mutant (base text restored): lint exit 0, rules_sync exit 0; no check pins the model word, as the body says. A wording change with no test claim; the only check keyed to the file is its cap, shown by the null control.
- Mirror: `node tools/policy/rules_sync.mjs --check` -> "RULES-SYNC ok" at head; `git grep proposal-triage -- .cursor .claude/rules tools/policy` returns nothing (`ev/mirrors.txt`), so nothing mirrors the file.
- Other model bindings (`ev/model_grep.txt`): `git grep` of every sonnet/opus file that mentions triage, then each live one read. `.claude/workflows/web-triage.js` is the issue re-measure workflow (opus judges), not proposal triage; nudge.md, architect-planner.md, plan-review.md, standing-roster.md bind other seats; orchestrator.md:113, decision 0015 item 4, roster_edit.py, sweep_template.md cite proposal-triage.md without a model. No place binds the triage seat to sonnet or disagrees with the contract.
- tests/entities.py (`ev/entities_b.txt`, `ev/entities_h.txt`, `ev/entities_named_*.txt`): in this container both ends print "2 of 2445 ENTITY CHECKS FAILED", and the top-level failing names (collected by wrapping harness.Results.check for the "Entities and platforms" recorder) are identical at base and head: the gate-sweep.yml U0c word-reader check and the graders-head-copy delivery_status step check, both of which execute workflow shell steps locally. The body's figure (4 failures, the hb:positive_control py-spy set) I could not re-derive: hb:positive_control passed here, and the failing set is a different, host-dependent one. The claim it supports, no difference between base and head, holds by name in my measurement.
- Approval: the `## Approval` section matches dev/programme/triage/s6-batch26.md#P127 on origin/triage/s6-batch26: Verdict ACCEPT, a one-line policy edit to proposal-triage.md merged under mandate 6329234399 as policy, source tvofi 2026-10-25 via `## V48`. The out-of-tree s6 proposals.md quote I did not open. The ruling file is on its branch, not yet on origin/main.
- Merge: `git merge-tree --write-tree` clean (exit 0) against da12aa37d and against origin/main dfcd8d9be1dab28cfe52f684764befd1e19291de.
- CI at head (`ev/ci_checkruns.txt`, 44 runs, all concluded): `gate` success, `pr-contract` success, every other run success or skipped except `governance / delivery-status`: OVERDUE on #2795 (102f749, 12 commits), main's backlog, not this PR's row (#2821 is not listed). Its log says it is NOT a required context and a red there blocks no merge. Body `## Red checks: none` is consistent with the gate.
- Head in body: names 72a2e211961462e577a0f2389ba000ffc4777c97 as the head and d62c9133f as the authored code head; matches.
