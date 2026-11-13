Fix review: blocked ea298df445835b20bb2f7d3e85dd1036f26b8ab1 evidence-comment: four claim rows rest on a comment or blank line at the merge base, and services.py:1196-1197 still ships the false "nothing was changed" its rows mark fixed

bus-nonce: 30ca6840e83f6657a3ca7e460c888da0

## Block

Round 1 of this group's review. Measured head `ea298df445835b20bb2f7d3e85dd1036f26b8ab1`, which is the body's `## Head` (handoff review: the handoff tip). Merge base `90c6bc3b0756475e28d4ace8d8e31c4788474933`.

1. **evidence-comment** (the owner ruling of 2026-11-13 in the brief: a row whose evidence is a code comment or docstring is a block). RECORD.md says each row's evidence is `file:line` at the merge base. I resolved every `.py` citation in `verdicts.json` at the merge base (`ev/evidence-line-kinds.txt`, `ev/comment-cites-at-merge-base.txt`). Four judged rows cite only a comment or a blank line:
   - `entity.sensor.heat_pump_action.state.off`, true: `optimizer.py:6312` is `# a step where only DHW books a draw is hot_water.`
   - `entity.sensor.plan_narrative.state.terminal_value`, true: `optimizer.py:2038` is `# Nothing more specific applies: ...`. That comment is about `REASON_SCHEDULED`, not the terminal value.
   - `entity.sensor.plan_narrative.state.cheap_price`, true: `optimizer.py:2043` is a blank line.
   - `entity.sensor.learning_model_status.state_attributes.pump_max_power_source.state.configured`, true: `draw_range.py:655` is a blank line.

   These four citations, and 132 citations in all, are absolute paths into an out-of-tree checkout (`/home/user/wt/...`), not repository paths. They resolve at the merge base: the `false` rows' `/home/user/wt/optimizer.py:2089` is `if i < len(in_window) and in_window[i]:` there. The re-cut owes a code citation for each of the four rows and repository-relative paths for all 132.
2. **class-open: `custom_components/heatpump_optimizer/services.py:1196-1197`.** The `HomeAssistantError` raised for `factory_reset_not_applied` still passes the literal English message `"... refused to unload the entry; nothing was changed"`. The body's rule is `enumerate.py`'s `PY_RE`, and it reads lines, so it returned only lines 1199 (`translation_key=`) and 1200 (`translation_placeholders=`). Both rows are `verdict: false, fixed: true`, with the truth "the text is exceptions.factory_reset_not_applied, corrected there". strings.json was corrected, but this literal was not. HA's `HomeAssistantError.__str__` returns an explicit message, so logs, script and automation traces and API callers still read the false sentence. The two rows' `fixed: true` is therefore wrong, and the body's `[]` for false-and-unfixed rows rests on it. Of the raises that pass `translation_key` (scout AST scan, ~31 at the head), only `services.py:565` has a plain-literal first argument. The others are f-strings or expressions, which the rule never reads. Their English fallbacks are unjudged, and neither the diff nor the body dispositions them. The re-cut owes this literal corrected, and a rule that reads a raise's message argument, or a disposition of those fallbacks.
   - Separate from this block and owned by R10-CONFIG-FLOW-TEXT-VERIFY: `options.abort.factory_reset_not_applied` (strings.json:1612, en.json) carries the same false "nothing was changed" through `config_flow.py:3509`.

## Findings

- Mechanically checkable corrected claims not pinned (brief addition 3): the rain thresholds the corrected `rain_heat_loss_multiplier` text quotes ("2 mm/h", "0.1 mm/h") could be pinned behaviourally through `effective_heat_loss_coefficient` at 0.1 and 2 mm/h. The run_optimization "four price steps" could be pinned by calling the handler with three prices. The body files both as prose-only because their literals are inline, but a behavioural pin needs no named constant. Carry: R11-INTAKE-R10-RESIDUE
- Reverting `narrative.py` to the merge base survives `tests/entities.py` (`ev/mutants-summary.txt`, `narr`). The body discloses this as prose-only. The corrected `dhw_window`/`dhw_preheat` sentences have no pin. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- RESULT head: `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head prints `ALL 2720 ENTITY CHECKS PASSED`, rc 0 (`ev/entities-head.txt.gz`).
- RESULT mutants (`ev/mutants.diff`, `ev/mutants-summary.txt`, full logs `ev/mutant-*.txt.gz`). Each ran in its own worktree at the head. Planted `a3:*` controls are excluded because they print FAIL on every run. The five mutants:
  - services.yaml wood price min 1 -> 0: KILLED by `simulate_plan's wood price selector minimum ... [min 0]`.
  - `CAPACITY_FLOOR_FRACTION` 0.6 -> 0.5: KILLED by the 27-numbers row.
  - `pump_arbiter.RETRY_MINUTES` 5.0 -> 10.0: KILLED by the 27-numbers row.
  - `DHW_DISINFECTION_LOST_MINUTES` 30 -> 45: KILLED by the 27-numbers row.
  - narrative.py back to the merge base: SURVIVED, as the body discloses.
  The body's own four mutants were not re-run beyond these overlaps.
- Verdict counts re-derived with the body's rule at the head: strings.json 227/23/0/1/176, services.yaml 219/1/0/10/48, python 138/2/0/2/25, templates 51/6/0/0/0. These equal RECORD.md's table. Total 929 rows. The false-and-not-fixed listing prints `[]`, but see block item 2 for why that is not the truth for the two python rows.
- Docstring sample: only the two python factory-reset rows quote a docstring in `truth` (`ev/comment-evidence-rows.txt`). Their evidence also cites code, `coordinator.py:1497-1500` (snapshot take and `_async_save_snapshots`) and `1478-1479` (unload refusal), which I read and which decides the claim, so they do not rest on the docstring. The four rows in block item 1 do.
- `dhw_window`/`dhw_preheat` truth verified against code at the merge base: `optimizer.py:2083-2092` classifies by `in_window[i]` and falls through to `REASON_DHW_PREHEAT` with no price or clock read.
- `git merge-tree --write-tree origin/main ea298df` exits 0 with one tree, so the head merges cleanly (`ev/merge-tree.txt`). origin/main is at `e23124ff6e45bac1d48b4a775dad555a37965355`.
- `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current. VERSION, manifest and RELEASE_NOTES.md are untouched by the diff.
- No pull request exists yet, so there is no review packet and no CI run to read. No red check is owed an answer: none exists at this head, and the owed-reds set is `merge_train.py owed-reds`.
- Forward-carry destination `R11-INTAKE-R10-RESIDUE` exists on origin/main's `dev/programme/rosters/wave-r10-groups.json`.
- Not re-derived: the scoped gate, `structure.py`, the archscore `dS +0.0000`, `mutant_run.py --diff` and the null-control judge-seat run. CI's heavy runs are cited by policy, and none exist before the PR opens. The judge-seat null control is a seat's reading that I cannot re-run.
