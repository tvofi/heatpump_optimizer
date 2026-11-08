Fix review: merge dbf79f836ea9acf89f3a076a94fa5c45962e2e88

bus-nonce: 8e2f58ddd5c09abc8753ef883421151b

## Round

This is round 2 of the fix review of PR 3274 (R10-WHY-NOW-WIDGET). It re-reviews the head after repair rounds 5 and 6, which answered the round-1 verdict at refs/heads/verdict/3274 (blocked 97786d25 class-open).

- I reviewed from a detached worktree at dbf79f836ea9acf89f3a076a94fa5c45962e2e88. The merge base is 8a1358e8448e6734ed16982f25da6aae223ba8b9, and I checked by the three-dot diff.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- `tools/audit/seat/review_carry.py 97786d25 dbf79f83` prints FRESH-REVIEW. So I re-reviewed the four branch-only commits since 97786d25: 9cde30560, 0765b49d9, e51073c67 and 69f76c2b3. The main merges are b550ba375, 4f8ab9654 and dbf79f836. Per the brief, the merge of main is not a finding.

## Findings

- The why-now metric text now departs from the brief's string. Design note 60d61fcf line 73 says the block "carry the brief's metric explanation as `title`, en and sv, verbatim". Repair round 5 (9cde30560) rewrote the explanation's last sentences in en and sv. The old text, "A high share means that reason mostly decides the hour", became "A high share means that reason pushes hardest; the plan weighs the whole day's hours together, so the heat pump can still do the opposite this hour."
  - Why it changed: round 1's finding 1 measured the arrows disagreeing with the solver's run/idle choice more often than an always-idle guess, and the rewording is one of the two remedies that verdict named.
  - Disclosure: the body raises the departure under "Brief carries".
  - Pinned: my mutant restoring the old sentence fails `why-now: every en string has its sv twin, and every driver code has a label and an explanation` (ev/mut_metric_text_card.log).
  - The new text is true to round 1's measurement. It no longer claims that the rows decide the hour.
  - What is left is the owner's call on the user-facing copy. The card is a code-owned path, so tvofi's approving review at merge is that ruling. Carry: dismissed: the departure is raised in the PR body and settled by the owner's code-owner review of the card at merge, which the merge requires anyway
- `## Red checks` does not name this head's two concluded `gate` reds:
  - job 128591043210 (run 42434593486, 01:33Z);
  - job 128592666076 (run 42435141123, 01:41Z).
  - Both print `FAIL run(s) [42434593342] at this head are still being judged; their gate decides` (ev/gate_edit_deferrals.txt). That is the mutual edit-run deferral (R10-HOTFIX-GATE-BUSY-DEFER), and code run 42434593342 decides.
  - The body was last set at 01:38Z by the orchestrator's script without a push, so the second red came after it.
  - The brief's ruling is that a gate red which only defers to the in-progress code run never blocks. Carry: dismissed: edit-run deferral to code run 42434593342, whose gate decides (brief GATE DEFERRAL ruling); the next body edit names both

## Evidence

Each of round 1's blocking findings is closed at this head:

- Block, class-open, r10_demand_overbook.py:245: closed.
  - The harness now reads the comfort bounds through `comfort_schedule()`, which unpacks the 4-tuple.
  - `PYTHONPATH=tests/hastub:tests python3 dev/audit/harnesses/r10_demand_overbook.py --one owner_i01 dp` exits rc 0 at the head with `dp_learned.gap -0.0006, dp_true.gap -0.0012`. That is identical to the base 8a1358e8 run (ev/overbook_dp_head.log, ev/overbook_dp_base.log), and it was rc 1 with a ValueError at 97786d25.
  - The class census `git grep -n '_build_comfort_bounds(' -- custom_components tools tests dev ':!*.tsv'` returns 12 lines, the body's count, and every caller reads four elements (ev/census.txt). The non-call matches are a docstring and matrix.tsv rows only.
  - My mutant H, which puts the 3-tuple unpack back in the harness, is killed by `r10_demand_overbook.comfort_schedule reads the solve's (target, floor, ceiling)` (ev/mut_H_harness_3tuple.log). The class now has a red check.
- Finding 1, metric over-claims: reworded; see the first Findings bullet.
- Finding 2, why_now recorded: closed. `"why_now"` is now in `_PlanSensorBase._unrecorded_attributes`.
  - My mutant removing it moves tests/entities.py from 3 to 4 failures. The new one is `the space plan keeps why_now out of the recorder (R10-WHY-NOW-WIDGET)`; the other 3 are the workflow probes the body names under Null control (ev/mut_S_unrecorded_entities.log).
- Findings 3–5, the surviving mutants C, D and E: closed. Each is re-applied alone in its own worktree at the head, and each is killed by the named check:
  - C (sort by signed weight): killed by `at every step the rows run largest magnitude first...`, with 126 crossed steps of 480 (ev/mut_C_sort_signed.log).
  - D (`away_floor_drop_c=None` in `_solve_record`): killed by `_solve_record hands the solve away.floor_drop_c while away, None at home`, which reads `away None (want 3.0)` (ev/mut_D_coord_away_none.log).
  - E (delete `comfort_floors = temp_min_bounds`): killed by `the drivers' comfort floor is the margined floor, below the mold floor's raise` (ev/mut_E_margin_floor_del.log).
- Finding 6, `## Red checks` incomplete: the body now answers the 4f8ab9654 reds (closures, closures-autofix, pr-contract, gate) and carries the earlier ones. This head's edit-run deferrals are the second Findings bullet.

Round 5 added a check pinning four bounds (0765b49d9). My own mutants of slot_drivers.py are each killed by `the forecast window floors at one step and clips at -1; comfort clips at -1; step_reasons past the end is None`:

- B1, span floor removed: reads nan.
- B2, forecast clip widened: reads -2.625.
- B3, comfort clip widened: reads -90.9.
- B4, `<` changed to `<=` at step_reasons' end: raises IndexError.
- B5, away sign flipped: 3 checks fail.

The logs are ev/mut_B*.log.

Round 6, the closure classification (e51073c67, 69f76c2b3):

- tests/closure.py's `INERT_EXCEPT` gains `dev/audit/harnesses/r10_demand_overbook.py`, with its reason. tests/closures.json adds it to the closures of tests/features.py and tests/harness_headers.py.
- This mirrors the record_burst_replay.py precedent, and it is the sound choice. A harness that features.py imports is no longer INERT, and an edit to it selects features.py.
- CI's `tests / closures` (job 128590875258) and `tests / closure-scope` (job 128590758019) read success at this head.
- I did not re-run the body's own `closure.py check --in-dir $REC` mutation, which needs a 10-minute recording. I cite CI's closures lane instead.

Suite and figures at the head:

- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4937 FEATURE CHECKS PASSED` (ev/features_head.log), which matches the body's 4937.
- The why-now block alone, run with the body's MUTANT_CMD: `ALL 25 FEATURES BLOCK PASSED` (ev/block_head.log, ev/block.sh).
- `node tests/card.mjs`, after `tests/plan_view.py`: ALL CARD CHECKS PASSED. `node tests/card_drift.mjs origin/main`: `1 state(s) moved and claimed, 44 identical` (ev/card_mjs.log, ev/card_drift.log).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure.log).
- The three-dot name-only diff over VERSION, manifest.json, RELEASE_NOTES.md, tests/golden/claimed_drift.txt and `*_budgets.json` is empty (ev/untouched.txt). dev/programme/delivery/3274.md is in the diff.
- Production code since 97786d25 changes in one place only, the sensor.py unrecorded entry. The card change is strings only. I found no formula change.

Merge and head:

- `git merge-tree --write-tree origin/main dbf79f83` returns rc 0, with `LEDGER-MERGE: resolved tests/closures.json` and no conflict (ev/merge_tree.txt). origin/main at review is in ev/main_at_review.txt.
- The body's `## Head` names dbf79f836ea9acf89f3a076a94fa5c45962e2e88, which is the head I measured (ev/HEAD.txt).

Figures I did not re-derive, cited from the body:

- the 66-mutant diff-mutant run and its 3 survivors (the two equivalents are sound by reading: type-only imports under `from __future__ import annotations`, and `>=` after the neutral return);
- archscore `dS +0.0000 NULL`;
- the harness rc census of 65 scripts;
- prepr.sh rc 0.

Instruments: ev/mut.sh, ev/block.sh and the inline entities and card mutants are my own instruments, not the finder's. No finder harness exists for this feature group, and round 1 and the note already record that. Carry: dismissed: evidence, not a finding

## CI state

- `python3 tools/audit/seat/merge_train.py classify dbf79f836ea9acf89f3a076a94fa5c45962e2e88 --pr 3274` exited 0 at 02:24:47Z with `GREEN dbf79f836ea9acf89f3a076a94fa5c45962e2e88 pending: none red: none` (ev/classify_final.txt, ev/classify_history.txt).
- From 01:37Z to 02:23Z it read RED on `gate`. The two edit-run gate reds named under Findings deferred to code run 42434593342, and that run's gate (job 128601732603) concluded success at 02:23:10Z.
- `tests / mutation` (job 128590758021), `tests / closures`, `tests / fast (3.14)`, `tests / browser` and `tests / coverage` all read success at this head. I cite CI's heavy runs and did not re-run them.
- `tests / nightly-status` read success at this head (job 128590757984).

## Closing

- I re-read the head just before return. `git ls-remote origin refs/heads/fix/r10-why-now-widget` gives dbf79f836ea9acf89f3a076a94fa5c45962e2e88, which is the head I measured.
- origin/main at return was 48af0864a43052a43e9125fa31c2822bac99165d. `git merge-tree --write-tree` against it returns rc 0, with `LEDGER-MERGE: resolved tests/closures.json` and no conflict (ev/merge_tree_final.txt).
- `python3 -I tools/audit/carry_audit.py check` was run on this verdict and the PR body; its result is in ev/carry_audit.txt. It returns rc 0 with `3 finding item(s): 3 routed, 0 unrouted`. It counts neither of the two `## Findings` bullets, although each ends in a `Carry: dismissed:`. Round 1 saw the same. I report this here and did not work around it.
