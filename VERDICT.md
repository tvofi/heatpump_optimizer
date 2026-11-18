Fix review: merge 30ae44cd94c646684357b486ade679a2f1270b98

bus-nonce: 90ff23fefd31b3219e55a9ef9de0f87a

This is round 2 of the review for #3723, a record PR with no production code. It reviews the delta `git diff 7f2ba2d2a7554eb4ce88b3484f80076d18a3dbd8 30ae44cd94c646684357b486ade679a2f1270b98` (fix-review.md step 12). The delta has two commits, `936c1178d5` and `30ae44cd94`. They touch only `dev/audit/rounds/round11/` (deletions only), `dev/governance/config/corpus_excluded.json` and `dev/governance/config/machinery_budgets.json`. No instrument, test, policy or production path is in the delta, so the scope is not widened. I re-read the head before return: `refs/pull/3723/head` is still `30ae44cd94c646684357b486ade679a2f1270b98`.

## Prior block: resolved

- The round-1 block was `metric-gamed: machinery_budgets churn_per_kilo_product_lines: raise omits a payment, 61 byte-identical duplicate evidence files`. The payment has now been made. `936c1178d5` deletes 41 non-`.pyc` files: the 38 `J/judge/` copies, `D12/s1/out/decl.json`, `D15/s2/REPORT.reply.md` and `D9/s2/results/olddriver/payload_synthetic_warp.out`. I checked each one: its blob at `7f2ba2d2a7` is still present at the head under another path, so 0 of 41 were lost (`ev/deleted_kept_twin.txt`). No reader on origin/main or at the head opens any deleted path (`ev/removed_path_readers.txt`). The one hit is noted under Findings.
- The 49 tracked `__pycache__/*.pyc` files are gone. `git ls-tree -r <head> -- dev/audit/rounds/` now lists 0 `.pyc` files.
- The cap was re-recorded at the new measurement. `machinery_ratchet.py --measure --base 8751943e17 --head <head> --pr 3723` prints `churn_per_kilo_product_lines` 34898, over 805126 nonproduct and 23071 product lines (`ev/machinery_measure_at_8751943.txt`). That matches the body and the budget file exactly. Round 1 estimated 34894 by its own formula, so the two agree to within 4 points.

## Raise judged on its merits (step 14)

- Remove the mechanism: without `936c1178d5` the measurement is round 1's 36124. The 1226-point drop comes from the deleted copies, and the cap follows the measurement down. The raise from 14797 is earned by about 480k lines of round-11 evidence under `dev/audit/`. `diff_stats` charges those lines as nonproduct, and no payment that keeps the record can remove them. Cap plus band is 18433, below the measurement, so a raise is still owed.
- Hunting for a missed payment: 20 byte-identical groups remain among the added paths (`ev/remaining_duplicate_blobs.txt`). By the counting rule's own `git diff -M -w --numstat` (`ev/remaining_dup_numstat.txt`), their second copies carry these counted lines:
  - `D10/s2/rules/tiers.json`: 70 lines. `D10/s2/enum_gold.py:16` reads it beside itself, as the body says.
  - `D1/s3/out/loc*/open_meteo.jsonl`: 4 lines.
  - The D11 s1/s3 ruleset and branch-rule JSONs: 4 lines.
  - The D3 `run`/`run_prev` reach JSONs: 3 lines.
  - The D9 `payload_owner.out` triple: 2 lines.
  - The D9 `payload_synthetic_warp.json` pair: 1 line.
  - The rest are binary screenshots or empty files, which count 0 lines.
- That leaves 14 counted lines that no reader needs, about 0.6 churn points against 23071 product lines. Each is an independent observation by a separate seat or a separate run, not a copied file. Dropping them would not make the tree sounder, so this is not a missed payment.
- Payments (2) to (4) in `## Raise justification` are judged sound:
  - (2) Tooling is frozen mid-round, and the body now correctly says that a `RECORD_PREFIXES` entry alone would not move churn.
  - (3) An exempt list hides lines rather than grading them.
  - (4) Trimming would delete the record.
- Architecture score: `score.py --diff 7f2ba2d2a7 <head>` prints `dS +0.0000 NULL`, and so does `--diff f567988b51 <head>` (`ev/archscore_delta.txt`, `ev/archscore_threedot.txt`). Both match the body's two lines.
- Approval: review 5962780454 is APPROVED by tvofi at `commit_id` 30ae44cd94, citing mandate 6893738184. That mandate is scope `all`, runs from 2026-11-15T11:38Z to 2026-12-15T12:00Z, and has no revocation on record. The revocation scan in round 1's evidence is dated 16:27Z today; I did not re-scan #3394 after that.

## Findings

- Note: body-claim: under payment (1), the body lists what was kept on purpose as `tiers.json`, the screenshots, the empty files and "two run outputs of 4 and 1 lines". It leaves out eight one-line JSON second copies:
  - D11 `s1/api` against `s3/data`: four files.
  - D3 `run` against `run_prev`: three files.
  - D9 `payload_synthetic_warp.json`: one file.
  - The `payload_owner.out` group also has three copies, not two.
  - The omitted lines total about 9 counted lines, under 0.5 churn point, so the raise is unaffected. Carry: dismissed: figure-level paperwork with no effect on the cap; no later stage reads it
- Note: stale-path: `dev/audit/rounds/round11/sweep-P2.md:5` cites `dev/audit/rounds/round11/J/judge`, which this head deletes. The citation is pinned to commit `5806e17d`, which still carries that path, and the same files sit at the round11 top level. Carry: dismissed: historical pointer pinned to a SHA that resolves; no reader parses it

## Evidence

- RESULT: `merge_train.py classify 30ae44cd94c646684357b486ade679a2f1270b98 --pr 3723` printed `GREEN 30ae44cd94c646684357b486ade679a2f1270b98 pending: none red: none` with rc 0 at 19:41:46Z (`ev/classify.txt`).
- RESULT: `git merge-tree --write-tree origin/main <head>` exits 0 against origin/main `107988b792` (`ev/merge_tree.txt`).
- RESULT: `machinery_ratchet.py --check --base origin/main --head <head> --pr 3723` at current origin/main `107988b792` gives rc 0, with `churn_per_kilo_product_lines 35277 <= 34898 + band 3636` (`ev/machinery_check_current_main.txt`). The rise from 34898 to 35277 comes from main's window sliding: product lines fell from 23071 to 22814. It is within the band, and the train re-proves it on its own main.
- RESULT: `VERSION`, the manifest, `RELEASE_NOTES.md`, `custom_components/` and `blueprints/` are untouched in the three-dot diff (0 paths).
- RESULT: steps 1 to 4 and 6 are n/a at this delta. It has no production line, no finder's harness (the packet says none named), no behavioural claim, and no golden or claim file.
- Red checks: the packet digest's only failure is `tests / nightly-status`. It is not in the `merge_train.py owed-reds` set (`ev/owed_reds.txt`), so no answer is owed. The body names it as inherited from main anyway.
- Figures I did not re-derive (round 1 left them open, and they are unchanged by the delta): the 86 scrubbed files and the 57 `not-started` stages. Neither bears on this delta.

## Friction

none
