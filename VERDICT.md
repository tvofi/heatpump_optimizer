Fix review: blocked 1965559c0ce814ee36c37fce9b5d41f55ec3e5ef introduced-red: governance / instrument-self-tests step "Render the sweep template, and the policy re-read predicate" is red at the head and green at the merge base; sweep_template.md declares a sweep_record placeholder the template never renders

bus-nonce: 19cdd355eb285a334fbd9b12a53202de

## Block

This is round 2, a delta review. Round 1 blocked c766208d486e with mutation-vacuous. The head is 1965559c0ce814ee36c37fce9b5d41f55ec3e5ef. It merges the repair handoff c77c5a836b (facf41d0d3 + c77c5a836b) over 76e0d320f3. That base merged main at fc2a7edcf2 and added the delivery row.

The six items from round 1 are all answered. See Evidence. A required check is still red, and that blocks the merge.

- `merge_train.py classify 1965559c0ce814ee36c37fce9b5d41f55ec3e5ef --pr 3502` exits 1: `RED ... gate red: none introduced: 1` / `INTRODUCED Render the sweep template, and the policy re-read predicate` (ev/classify.txt). Job 131173740365, `governance / instrument-self-tests`, concluded failure. Under fix-review.md step 11, an instrument-self-tests step that is red at the head and not at the merge base is a block.
- I reproduced it locally. `python3 -I tools/audit/seat/sweep_render.py --self-test` at the head exits 1 with `FAIL the tracked template renders from a complete overlay, every placeholder filled (null control)` (ev/sweep_render_head.txt). Then I put the merge base's sweep_template.md into the head tree and changed nothing else. The same self-test exits 0 (ev/sweep_render_base_template.txt). So the one line this PR adds to tools/audit/seat/sweep_template.md:54, the `sweep_record` overlay row, is the cause.
- Why it fails: `declared()` in sweep_render.py treats every row of that table as a placeholder. The null control at sweep_render.py:227 requires each declared name to appear as `<name>` in the rendered sweep, unless the name is in `OPTIONAL_FLAGS`. The template body never renders `{{sweep_record}}` (ev/sweep_record_refs.txt). beat_jobs.py reads `ctx.overlay["sweep_record"]` directly, so nothing references it in the template.
- How to repair it: the template declares the key and the body never uses it. Either make `sweep_record` an optional flag (add it to `OPTIONAL_FLAGS` together with a case), or have the sweep render it. Do whichever matches how the other overlay-only keys of beat rows are declared. Then re-run fixer.md steps 2-8.
- The body's `## Red checks` says `none`. It needs to name this check and give its answer. A cheaper detector existed: `sweep_render.py --self-test`, which takes about a second locally. It belongs to the sweep-template step, and that step's scope trigger is sweep_template.md, a file this PR touches. Round 1's local scope selection (scorecard, beat-job-rows, beatd) did not list that step, and my round-1 review missed this red as well.

## Findings

- Survivor of my own driver at the head: `mf_first_any_blocked` (scorecard.py:127, `v["kind"] == "blocked"` -> `v["kind"] != "merge"`) SURVIVED (ev/reviewer_mutants.txt). I judge it equivalent. The verdict grammar for a fix review has two kinds only, `Fix review: merge|blocked` (fix-review.md, first line), so on that domain "not merge" is exactly "blocked". The predicate is not new: round 1's `vs[0]` form was the same, and the delta only re-spells it. Carry: dismissed: equivalent on the two-kind fix-review verdict grammar; the re-cut may pin it with a non-merge, non-blocked kind case if verdicts.json can ever hold another kind

## Evidence

- RESULT round-1 items. Each one is KILLED by my own driver at the head (ev/harness/mut.py, ev/reviewer_mutants.txt):
  - gate_name_any is killed by "report: A_gate reads the job named gate".
  - report_record_dropped is killed by "report: K reads the sweep record".
  - first_by_input_not_t is killed by "Y_rev unordered" and "Y_rev unordered window".
  - named_regex_no_merged is killed by "Y_train named".
  - ratchet_rc_ignored is killed by "S: a ratchet that exits non-zero".
  - dedup_dropped: the de-duplication was deleted, so there is nothing left to mutate. Its replacement is `setdefault` over the list sorted by `t`. I tried the last-wins mutant and the reverse-sort mutant, and both are killed.
  - The ordering point is settled. line_review now sorts by `t`, and the docstring and instruments/scorecard.py.md say so.
  - Further targeted mutants on the rewritten line_review are all killed: window head instead of tail, and span swapped.
- RESULT `scorecard.py --self-test`: ok with mutants, every listed mutant killed (ev/scorecard_selftest.txt). `beat_jobs.py --self-test`: 203 checks, 0 failed (ev/beat_selftest.txt).
- RESULT `tests/structure.py` at the head: STRUCTURE RATCHET PASSED (ev/structure.txt).
- `git merge-tree --write-tree origin/main 1965559c0ce814ee36c37fce9b5d41f55ec3e5ef` (origin/main 6e100ef698) exits 0 with `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.txt). It merges cleanly.
- The delta c766208d..c77c5a836b is instrument and test only, plus tests/closures.json and a doc line. It touches no file under custom_components/, so nothing widens the review. VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched in `git diff fc2a7edcf2...1965559c0ce814ee36c37fce9b5d41f55ec3e5ef`.
- tests/closures.json: the `tests/entities.py` record moves from rc 1 to rc 0. This is a re-derivation (commit c77c5a836b). I could not re-derive it here, because entities.py needs homeassistant and takes about 870 s. CI's `tests / closures` job owes that check, and it was still in_progress when I last read the checks.
- The body's `## Head` names 1965559c0ce814ee36c37fce9b5d41f55ec3e5ef and the merged code head c77c5a836b. The packet render refused with `introduced-red: unreadable` while the job was still in_progress. The live checks are now concluded red for that step, and that is the block above. `tests / nightly-status` failure and the second-workflow `gate` failure are not in classify's owed set (`gate red: none`).
- Figures: the body says none. Forward-carry: the body says none. Friction: dismissed with a reason.
- Head re-read before return: refs/pull/3502/head = 1965559c0ce814ee36c37fce9b5d41f55ec3e5ef.
