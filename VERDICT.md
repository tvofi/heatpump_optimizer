Fix review: blocked 7f2ba2d2a7554eb4ce88b3484f80076d18a3dbd8 metric-gamed: machinery_budgets churn_per_kilo_product_lines: raise omits a payment, 61 byte-identical duplicate evidence files (28376 nonproduct lines) the counting rule charges twice

bus-nonce: 772926a057065f2d0d3fc32c907c4ca1

Round 1 of review for #3723 (record PR, no production code). Reviewed at head 7f2ba2d2a7554eb4ce88b3484f80076d18a3dbd8, which is still the PR head (refs/pull/3723/head, re-read before return).

## Block

- fix-review.md step 14 says to judge each payment the raise lists and to look for one it missed. A missed payment that really improves the tree is `metric-gamed`. Here is the one I found. The diff adds 61 groups of byte-identical blobs (`ev/duplicate_blobs.txt`, built from `git rev-parse <head>:<path>` over every added path). 38 of the groups pair `dev/audit/rounds/round11/J/judge/*` with the same file at the round11 top level, for example `JUDGE-INPUT.json` (10231 lines), `judge-batch-1.json` (6552), `JUDGE.json` (2299) and `judge-batch-1-s*.json`.
- The counting rule (`git diff -M -w --numstat`, with no `-C`) charges each copy in full. The second copies add 28376 nonproduct lines, 26618 of them under `J/judge/`.
- Re-derived with the program's own formula over 833419 nonproduct and 23071 product lines in the window: churn is 34894 without the duplicates and 34970 with only the `J/judge/` copies removed, against the 36124 measured and raised to. A raise is still needed: cap 14797 plus band 3636 is 18433. But the raise is about 1230 points larger than the diff earns.
- Removing the copies loses none of the record, because one identical blob stays. On origin/main no tool or workflow reads `J/judge/`: every judge reader (`fold_ledger.py`, `judge_batch.py`, `finder_overlap.py`, `plant_recall.py`, `audit-*.js`) reads the round's top-level files. Round 10 has no `J/` directory. A single copy also cannot drift from its twin, so it is the sounder tree.
- Owed in the re-cut: drop the duplicate copies, or justify each one that a reader needs at its second path; re-measure; re-record the cap at the new measurement. The re-cut should also drop the 49 tracked `__pycache__/*.pyc` files under round11 (`ev/tracked_pyc.txt`). `.gitignore:2` ignores `__pycache__/` and origin/main tracks none under `dev/audit/rounds/`. They are binary, so they move no counted line, but they were force-added past the ignore rule.

## Findings

- Note: body-claim: `## Raise justification` says the counting rule charges every line outside `dev/programme/` as nonproduct. `machinery_ratchet.py` (`diff_stats`) charges every line outside `PRODUCT_PREFIXES` (`custom_components/`, `blueprints/`) as nonproduct, `dev/programme/` included. `RECORD_PREFIXES` sets only a merge's kind. So payment (1), adding `dev/audit/rounds/` to `RECORD_PREFIXES`, would not move `churn_per_kilo_product_lines` at all. It would move only `nonproduction_merges`'s kind split, and nothing for this PR, which also touches `tests/` and `.claude/`. The round-end proposal it cites rests on the same misreading. Carry: dismissed: corrected in this PR's own re-cut body; no later stage depends on it

## Evidence

- RESULT: machinery_ratchet `--check --base origin/main --head <head> --pr 3723` at origin/main 8751943e17 gives churn 36124 and rc 0 (`ev/machinery_ratchet_check.txt`). That re-derives the body's 36124.
- RESULT: `tools/audit/archscore/score.py --diff <merge-base> <head>` gives `Architecture score: dS +0.0000 NULL` (`ev/archscore_diff.txt`). `budget_raise_gate.check_body` on the live body with that figure returns True (`ev/budget_raise_gate_check_body.txt`).
- RESULT: mandate 6893738184 is by tvofi on #3394, created 2026-11-15T11:38:02Z and never edited. It reads scope `all`, from 2026-11-15T11:38Z until 2026-12-15T12:00Z. No later tvofi comment names it (`ev/mandate_*`). It was in force at review time.
- RESULT: `git merge-tree --write-tree origin/main <head>` exits 0 with no conflict (`ev/merge_tree.txt`).
- RESULT: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. No path under `custom_components/` or `blueprints/` is in the three-dot diff. Outside `dev/audit/` the diff touches only `.claude/workflows/audit-find.js`, `dev/governance/config/{corpus_excluded,machinery_budgets,policy_known_bad}.json`, `dev/programme/register/audit-2026-09.md`, `tests/closures.json` and `tests/layout.json`.
- RESULT: steps 1 to 3 and 6 are n/a: there is no production line to mutate, no finder's harness (the packet says none named) and no behavioural claim. Step 4: the diff carries no golden or claim file.
- CI: `merge_train.py classify` was still WAIT (`pending: gate red: none`) at 16:26:22Z when I stopped. The block does not depend on CI, so I did not wait for green (`ev/classify.log`). The packet's `introduced-red` refusal was the queued `instrument-self-tests` and is unresolved at return. Owed-reds set: `ev/owed_reds.txt`.
- Figures I could not re-derive: the body's 86 scrubbed files and 57 `not-started` stages were not re-derived, and neither bears on the block.

## Friction

none
