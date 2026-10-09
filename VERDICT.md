Fix review: blocked e408b9a28fa04f5e5d732ff2c9c4e78435fca3fd other: round 2 deleted the from_dict isinstance line that mutation-autofix had pinned, so the stale pin d3b18734 turns mutation and entities.py red at this head; neither red is answered, and the body's block count is stale

bus-nonce: 3f279f3809f97fa1690017082803f675
seat: review-2065, round 2
measured and posted at: e408b9a28fa04f5e5d732ff2c9c4e78435fca3fd. It is still the live head, and every workflow at it has concluded. Round 2 is reviewed as its delta from 325960ef: becd4e383 (the bot's pins) plus e408b9a (the repairs).

## Blocking

1. **A stale ledger pin, which this diff created.** `tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.GUARD_OFF.d3b18734.json` was pinned by `mutation-autofix` in becd4e383. Its `old` line is `if not isinstance(data, dict):`, and e408b9a deleted that line from `DrawRange.from_dict` (`git grep` at the head: no match). The consequences at e408b9a:
   - `mutation` (job 113615566185): `MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic inventory: ... DrawRange.from_dict GUARD_OFF d3b18734: disposition names no site the inventory generates`.
   - `fast (3.14)` (job 113615566266): `tests/entities.py` fails 1 of 2227, on `--anchor re-drives one site ...`, which fails on the same refusal.

   The repair is to remove the stale pin, or re-key it with `python3 tests/mutation_table.py --pin-killed --base origin/main`, and run the ledger check locally before the push. A cheaper detector exists and costs seconds: the mutation table's inventory comparison, run after any edit to a line `mutation-autofix` has pinned. The body owes that answer.
2. **root-cause-unanswered at this head.** `## Red checks` answers the reds at 325960ef and becd4e383, not `mutation` and `fast (3.14)` at e408b9a. The later pr-contract (01:32:57Z) passed only because those check names already appear in the section; the reds it has to answer are new ones. I record this as an instrument note for the orchestrator: the body check keys on the check name, not on the head.

## Owed in the body (does not move the head)

- `## Figures` still reads "the new block alone: 32 of 32". At e408b9a the block has 39 checks, and I measured `ALL 39 DR BLOCK PASSED`. The rest of the local-run paragraph is also round 1's, with no round-2 marker. Re-take the figures.

## Verified at e408b9a (RESULT)

- RESULT contract drift: main changed `dev/governance/roles/`. I read the diff and applied the new step 15 (`fixer.md` 17 on added lines). No breach: `draw_range.py` owns the concept and is pure, takes values and has no HA import, and the coordinator gets one hook. The diagnostics use the existing registry, store version 1 is unchanged with additive keys, a missing config refuses rather than guessing, and the note is followed.
- RESULT privacy: no added line in `git diff 4dbe5aace...e408b9a` carries the install's figures, and neither do the tree's `custom_components`, `tests` or `dev/audit/harnesses`, nor the live body (grep of each: no match). The synthetic over-nameplate shape is 1-10 kW, asked U(3,10), drawing U(1.2,1.8). Per tvofi, the old commits keep the old figures, and I do not block on history.
- RESULT layout: `fast (3.14)` runs layout.py `ok`. Locally, `GUARD: 0 refusal(s)`. The harness is at `dev/audit/harnesses/draw_range_evidence.py` and is in `tests/closures.json`.
- RESULT block: `ALL 39 DR BLOCK PASSED` locally. CI features.py is `ok` (478 s), and so are optimality, stress, env_drift --all, card_drift, structure and arch_score_head.
- RESULT mutants: round 1's survivors now die. R1 (`bottom = low`) and R2 (`top = high`) each fail their 15 % check. R3 (`from_dict` keeping samples without a config) fails 3 checks. AGREE_TOLERANCE at 0.10 fails 1 and at 0.25 fails 1, so both sides of the boundary are pinned.
- RESULT harness: over 20/20, null 0/20, mild 0/20, mild-indep 20/20. Frequency-write is None on every shape, and duty-cycling keeps the configured min.
- RESULT structure: `tests/structure_budgets.json` is byte-identical to the merge base, with no budget move. The walrus is gone, and `power_frozen` is bound on its own line. The class is net 0 against the merge base, which the note's "net <= 0" allows.
- RESULT from_dict: a missing, unreadable or non-finite config now drops the record whole. A non-dict document still returns empty, because `data["config"]` raises TypeError and that is caught. This closes the #2066 seam I raised in round 1: `follows_ask` can no longer see samples without a config.
- RESULT merge-tree against origin/main 47b083b03 exits 0; the `LEDGER-MERGE` driver resolved `tests/closures.json`.
- RESULT version: no edit to VERSION, the manifest or the notes heading.
- RESULT `nightly-status`: red. The body attributes it to the heartbeat positive control. It is not this PR's red.
