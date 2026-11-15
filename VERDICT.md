Fix review: merge 60073e460b9b8af16596edf7d2739c4dd326d0fc

bus-nonce: 3502eaf4951388bbd21df406721a0b5a

Round 1 (first review; full scope).

## Summary

Nine dimension briefs now name the command that prints each step's universe, and `text_ledger.py` gains an `outline` mode. The only code is `outline`. I re-ran the PR's two named mutants and both are killed by its self-test. Every figure in the body re-derives at the head (`ev/figures.txt`). No fixture, `VERSION`, manifest or release-notes heading is touched. The head merges cleanly with origin/main.

## Findings

- Survivor of my own targeted mutants on `outline`: dropping `sorted()` from the HTML branch survives the self-test, because the fixture's heading already comes before its links. The cost is row order only, and the rows are still all printed. Carry: dismissed: presentation order only; no seat's count or coverage depends on it.
- Survivor: the CLI `--dim` relaxation (`not a.dim and a.cmd != "outline"` changed to `not a.dim`) survives the self-test, because the self-test calls `outline()` directly and never the CLI. I ran `outline --seat D5-s2 --repo . --ref HEAD` myself and it printed 9 document, 207 heading and 174 link rows, so the path works today. Carry: dismissed: the CLI route is exercised by the body's own figure command and by every D5 seat at use; a regression would refuse loudly.

## Notes

Note: stale-guide: `tools/audit/seat/instruments/text_ledger.py.md` and its INSTRUMENTS.md line still describe only `units` and `check`, not the new `outline` mode.
Note: root-cause-unanswered: `pr-contract / pr-contract` and `gate` concluded cancelled at 60073e46 and are not named under `## Red checks`. Both were cancelled by supersession when 20d348b0 was pushed, and neither failed.

## Evidence

- Mutation proof (`ev/mutants.txt`, `python3 tools/audit/text_ledger.py --self-test`):
  - fence-toggle → `19 checks, 1 failed`; suffix-guard → `1 failed` (both are the PR's named mutants, both killed).
  - My extra mutants: ref-link alternative removed → `1 failed`; closing-hash strip → `1 failed`; HTML tag strip → `1 failed`; document row dropped → `2 failed`.
  - Survivors: html-sort and cli-outline-dim (see Findings).
  - Restored: `19 checks, 0 failed`.
- Figures re-derived at 60073e46 (`ev/figures.txt`):
  - `brief_lint.mjs` exits 0, `check-wave-script.mjs` exits 0, `policy_lint.mjs` prints `TOTAL: 0 error(s) across 52 policy file(s)`, and `rules_sync.mjs --check` is ok.
  - `--budgets`: every raised row sits exactly at its measured value. D3 is 46/46 lines and 605/607 tokens, paid inside its caps. The corpus is ~69740 against 69333 + band 500, so inside the band and not re-recorded, as the body says.
  - `archscore --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- Carry 173: the union of the D6-s1..s7 cell files is 351 and the union of files yielding a unit is 351, with `comm -3` printing 0 lines. All six named files are in the unit set. Null control: removing README.md from the unit set makes the comparison print `README.md`.
- Universe commands, all non-empty:
  - `card_drift.mjs --list`: 45 states.
  - `--population` language row: `de,en,sv`.
  - The D7 `git diff --diff-filter=A 17f1c55fad1b 26dbf7c43e`: 16 files, and `17f1c55fad1b` is the `baseline_sha` of round 10's `reports-B1.json`.
  - The `jq` open-class filter: 19 classes.
- `env_drift.py --all`: `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`. The claim files are untouched.
- Budget raise (step 14): the payments the body lists are real in the diff. The D3 step 1 rewrite keeps the old line count, D4's install recipe and `all contention-immune` are cut, and D7's hand list is deleted. I found no further payment that keeps every step, input and criterion. The D11/D13 twin paragraph is the owner's ruling. This is policy under mandate 6893738184, and `budget-raise-gate` stays the owner's or mandate's stop.
- `git merge-tree --write-tree origin/main 60073e46` exits 0 (`ev/merge-tree.txt`), so there is no conflict.
- `git diff b3831ff64e...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Head move: the PR head is now 20d348b0967db8c7a3f050f35359bb3661deed66, which adds only `dev/programme/delivery/3618.md`. `review_carry.py 60073e46 20d348b0` prints `CARRY` (`ev/carry.txt`). All my numbers were taken at 60073e46.
- CI on the dispatched head: `merge_train.py classify 60073e460b9b8af16596edf7d2739c4dd326d0fc --pr 3618` prints `RED 60073e460b9b8af16596edf7d2739c4dd326d0fc pending: none red: gate` (rc 1). Check run 132863043763 (`gate`) concluded `cancelled` with empty output, and `pr-contract / pr-contract` and `sweep-self` were cancelled with it. This is supersession by the 20d348b0 push, not a failing test. On the new head the same instrument prints `WAIT 20d348b0967db8c7a3f050f35359bb3661deed66 pending: gate red: none` (rc 3). The relay should judge the merge on 20d348b0's gate, to which this verdict carries.
- `budget-raise-gate`: red by design until an approving review lands. It is answered under the body's `## Red checks`.
