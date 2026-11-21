Fix review: merge 0bfce347d8aa2d26f8401f656576a044ef6e815f

bus-nonce: a5fc23aeda3564f97ee8c5266dfe49ec
pending-ci: gate

## Scope

Round 3. This is a delta review over the last head that got a merge verdict, 8e9886731eac90a687b0207c82a40431fa67ed24 (probe/rev-3728-41a1c9b8, `pending-ci: gate`). The gate went red there on the comment ratchet. `review_carry.py 8e988673 0bfce347` prints FRESH-REVIEW because the authored commit 00b60ee41 changes content. The delta has three commits. 7725103872 merges origin/main a8efe1d1; its remerge-diff resolves only `tests/closures.json`, which the ledger driver merged as a set. 00b60ee41 changes `drift.utc_instant`'s docstring and `plan_step.covering_index`'s docstring, sentence splits only, with no code token changed (ev/delta_00b60ee4.diff). 0bfce347 merges that commit and has an empty remerge-diff. Nothing was widened: the production delta is docstring text only. Main's merged code was checked only for interaction with this PR, by re-running the PR's class rules and its check blocks at the head. I measured from detached worktrees at 0bfce347d8aa2d26f8401f656576a044ef6e815f (merge base a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b). I re-read the head before returning (refs/pull/3728/head) and it has not moved.

## Evidence

- RESULT prior-red: the 8e988673 `tests / fast (3.14)` red, the doc_claims comment ratchet (`long units` on drift.py and plan_step.py), is repaired by 00b60ee41. `python3 tests/doc_claims.py` at the head reads ALL 441 checks PASSED, rc 0 (ev/doc_claims_head.txt).
- RESULT reviewer-mutants at the head (ev/reviewer_mutant_driver.py, ev/mutants_head.txt, ev/mutants_head_R3_rerun.txt; bytecode off, each file restored, tree clean afterwards). Two controls pass: M0 ALL 9 FEATURES BLOCK PASSED (the ADR-001 block, through `features_block.py` with an emitted prelude) and M0w ALL 26 wood-advisor checks PASSED. 9 of 9 mutants are killed:
  - R1, covering_index's end rule: 4 of 9 red.
  - R2, plan_step_index without last_span: the last-step width check red.
  - R3, utc_instant's naive branch: naive instant check red, `drift` False. The first R3 run was a malformed mutant (IndentationError); this is the re-run.
  - R4, payload_number's finite guard: finite check red.
  - R5, EVIDENCE_KEEP 7: D7-s1-05 note check red.
  - R6, sensor's 4.187/3600: water check red.
  - R7, manual_plan._instant to when.timestamp(): naive instant check red, `manual_plan` False.
  - R8, _in_zone without utc_instant: 1 of 26 wood-advisor checks red.
  - R9, replay_doc.numeric's bool guard dropped: 1 of 164 debug_collect checks red.
- RESULT finder-harness (m8_agree.py sha1 aaef9a3b34b9c3d8a523eb24410ff97f7ce6b0d1, git archive of 819aa2e354b4e5baaf824b8568fd72bea8168a75, through the in-tree adapter sha1 a3ceb0fa51ea48fd46d3ccbe43fae05c4278918b, which I copied into the base tree for the base run; ev/finder_water_both_ends.txt, ev/finder_harness_head.txt):
  - Base: step_covering_now 4, naive_instant 2, finite_number 9.
  - Head: 0, 0, 2. The 2 are the text probes, as the body states.
  - no_value_state reads 3 at both ends.
  - water_heat errors at both ends (`ZeroDivisionError`, reads -1); see the Note under Findings. With the reviewer's one-line adaptation (ev/m8_agree_dhw_reviewer_adaptation.py, an instrument I built, not the finder's), it reads 1 at the base (sensor 0.0011631 against 0.0011600) and 0 at the head.
- RESULT class rules at the head (ev/class_rules_head.txt, ev/seams_head.txt):
  - `bisect_right(` has 2 code sites, `plan_step.py:69` (the owner) and `coordinator.py:7334` (`_weather_series`, dispositioned by `_R10_COVERING_ALLOWED`).
  - `git grep 'astimezone('` returns the same 9 sites the body dispositions; `astimezone()` returns 0.
  - `--seams` reads total 53: aware 8, utc_instant-first 1, as_utc 16, naive test 16, aligned 7, stripped 4, relabel 1. Every count equals the body's. The main merge added no site.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 0bfce347` (origin/main a8efe1d1) exits 0 (ev/mergetree_version_budgets.txt).
- RESULT version-files: VERSION, manifest.json, RELEASE_NOTES.md, claimed_drift.txt and card_claimed_drift.txt are untouched three-dot against a8efe1d1.
- RESULT budgets: three-dot `structure_budgets.json` moves down only (class_excess_loc 17322 -> 17317, duplication_copies 7 -> 5, max_class_loc 7873 -> 7868). `python3 tests/structure.py` reads STRUCTURE RATCHET PASSED (ev/structure_head.txt). The delta moves no budget.
- RESULT body head: `## Head` names 0bfce347d8aa2d26f8401f656576a044ef6e815f, the head measured here.
- RESULT red-history: the owed reds (ev/owed_reds.txt) on this range's heads are named in `## Red checks`: `tests / fast (3.14)`, `pr-contract` and `gate` at 8e988673, and earlier heads as the round-2 verdicts recorded. Answered (but see the body-stale note).
- RESULT figures not re-derived: the whole-suite counts (`ALL 5939 FEATURE CHECKS PASSED` and the like) were not re-run. CI's `tests / fast` at this head is the authority (fix-review.md step 11).
- RESULT CI: see `## CI`.

## Findings

- Note: body-stale: `## Red checks` still says the `tests / fast (3.14)` red at 8e988673 is "Not yet repaired: it needs a fixer commit that splits those sentences". 00b60ee41 is that commit, and doc_claims passes at the head. Carry: dismissed: body paperwork, which the fixer's next body refresh settles; no stage changes
- Note: figure: `## Figures` gives `water_heat_disagreements 0` at the head (and 1 at the base) from the finder's m8_agree.py. The finder's harness as archived no longer measures that family. `fam_water_heat` calls `sensor._gap_probe_terms({}, ...)`, and main's D8-s1-01 gate (kept by 2385016abd) prices no DHW-coast term without hot water. So the term is 0.0 and the family raises ZeroDivisionError at both a8efe1d1 and the head. This is the same cause as the 4fd8d2a2 features red. With `{CONF_DHW_ENABLED: True}` (the reviewer's adaptation) it reads 1 -> 0. The finding stays pinned in the tree by features.py's `D7-s3-04 water` check, which drives hot water on and which R6 kills. Carry: dismissed: the finder's harness is an out-of-tree round-11 artifact on plan/r11; the committed pin measures the finding, and no later stage reads that family

## CI

- RESULT classify, polled every ~90 s from 18:17Z to 18:48Z (ev/classify.log): last line `WAIT 0bfce347d8aa2d26f8401f656576a044ef6e815f pending: gate red: none`. No required check is red at this head, and only `gate` is pending. The packet's `introduced-red` refusal came from `governance / instrument-self-tests` still being in progress when the packet rendered. Classify shows no red, so classify decides. The relay posts this verdict only once the head is GREEN.
- RESULT live checks (get_check_runs, re-read): one `gate` run (job 136937205840) concluded failure at 18:13Z, an early aggregate while its inputs were still running. Classify reads `gate` as pending, not red; it decides.
