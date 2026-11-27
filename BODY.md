R11-OWNER-FEATURES-SPLIT, design revision 5 (branch `design/r11-owner-features-split` at 3d8a5c1af923aa8e0b0881138ae0408a995e1b3c, `Design review: approve 3d8a5c1a…` on `design-verdict/r11-owner-features-split` 4ee63e99aa). This freezes `tests/features.py` in place instead of splitting it. Nothing is re-keyed: every span stays and every `tests/mutation_ledger` row keeps `killed_by: tests/features.py`. `tests/entities.py` now refuses a tree where `tests/features.py` has a span id that `tests/features_frozen_budgets.json` does not list, or more lines than the manifest records. It also refuses a span in a `tests/features_<seam>.py` seam script that is not at its home seam. New tests go to the seam scripts, and the first PR that needs a seam script creates it.

**decision: owner.** Freezing instead of splitting is the owner's call. The orchestrator took it under mandate 6893738184 by its 5-minute rule, and it stays pending owner confirmation. To reverse it, the owner authorises the fork-drive re-key above its 150000 CPU-s cap.

**The split's price is a biased-low sample estimate, not a bound.** The spike (`handoff-wip/r11-owner-features-split-spike` ef2d5cd716) prices the re-key at an expected 372156 CPU-s. That figure is a point estimate, biased low by truncation. It comes from n=6 for stratum E (three runs finished, three stopped in flight) and n=4 for MOD. `strata.json` records no seed, phase C's x2 is assumed rather than measured, and strata M and L count 0. It bounds nothing about the population mean. The figure that exceeds the cap on its own is 166731 CPU-s: stratum E's find pass (phase F) over the 340 rows first reached in spans 0-2, on the same samples.

**How a seam-script budget raise merges.** Each seam script adds 2 to `script_runs_per_push` and 2 to `script_runs_full_case_pr` in `tests/ci_budgets.json`. Both are MAX keys, so the PR that creates the script raises a budget. That raise merges only on the owner's approving review at its head, or, under a mandate in force scoped `budget-raise` or `all`, with a `## Raise justification` that lists the payments tried and carries an `Architecture score: dS` line (CLAUDE.md rule 2, decision 0013). Mandate 6893738184 ends 2026-12-15T12:00Z. After that, every such raise is the owner's. This PR's payment tried does not carry over to those PRs. The harness docstring (`dev/audit/harnesses/features_freeze.py`) states the same rule in the tree.

**What the freeze costs, beyond the design note's section 6.** The line cap also binds a production change whose existing `tests/features.py` test needs one more line. That PR must net the line out elsewhere in the file, move the test to a seam script, or raise `lines` through budget-raise-gate. D5's s7 units cannot grow by lines, but they can still grow at a constant line count.

**At the merge.** The manifest records the merge base 43ec8e3273. If `origin/main` adds a span or a line to `tests/features.py` before this PR lands, `tests/entities.py` goes red on the merged head until `--record` is re-run there. That re-record is also a FROZEN change, which budget-raise-gate reads.

Changes:
- `dev/audit/harnesses/features_freeze.py` (new): the seam rule (the spike's `rev3/swap_run.py` `partition`, with its module table), `refusals` over the three conditions, `tree_refusals`, and `--check`, `--seam FILE` and `--record`.
- `tests/features_frozen_budgets.json` (new): `lines`, `seam_pins` (empty) and `spans`, recorded by `--record` at merge base 43ec8e3273, not at the design's base e84856520d (carry manifest-base).
- `tests/entities.py`: one new section, "The tests/features.py freeze (R11-OWNER-FEATURES-SPLIT)", with the live check, a shape check, and null controls for each condition and for laundering.
- `tests/closure.py`: the harness goes on `INERT_EXCEPT`, because `tests/entities.py` imports it.
- `tests/closures.json`: `tests/entities.py`'s closure is re-recorded with `derive_closures.sh --single` on Darwin (partial), and now holds the harness and the manifest.

Reviewer carries (verdict 4ee63e99aa), each built here:
- manifest-laundering: the manifest is named `*_budgets.json` and has no SCHEMA entry, so every leaf is FROZEN. The laundering null control is below, under the gate's own `file_raises`.
- three-conditions: all three conditions (span set, lines, seam home), plus the seam-header and seam-name refusals, are each mutation-proven (below).
- seam-table-drift: a span pinned in the manifest's `seam_pins` under its script keeps that script, whatever the module table later says. The PR that edits the table pins the spans it would move. A pin is a manifest edit, so budget-raise-gate reads it. A module the table does not list counts as `surface`, so adding a module moves no placed span. Renaming one is caught in the renaming PR, which must update the spans' imports anyway.
- seam-raise-path: stated above and in the harness docstring. It still has to reach the appending groups' briefs (Forward-carry).
- undone-honesty: stated above and in the harness docstring.
- spike-wording: stated above and in the harness docstring.
- seam-header (design note): a seam script that imports or names `tests/features.py` is refused (`header:`).
- open-branch-port (design note): routed (Forward-carry).

## Head

0c4af77ec948441dc55a1b8b0f21e1c0fa89a7da

## Mutation proof

The checks were run as the new span alone (`PYTHONPATH=tests/hastub python3 tests/case_select.py run tests/entities.py --plan <file naming the section>`). Each mutant was applied to `dev/audit/harnesses/features_freeze.py` in turn and then restored (`cmp` confirmed it).
- Failing first: before `tests/features_frozen_budgets.json` existed, the span raised `FileNotFoundError: ... tests/features_frozen_budgets.json`.
- M1, span condition `if sid not in known:` -> `if False:`: FAIL `null control (span ids): a section appended, inserted mid-file, or repeating an existing title is refused by name; ...` (1 of 6 ENTITY CHECKS FAILED)
- M2, lines condition `if got["lines"] > manifest["lines"]:` -> `if False:`: FAIL `null control (lines): one line added inside an existing span is refused on `lines` alone; ...` (1 of 6)
- M3, seam-home condition `if h != seam and sid not in pinned:` -> `if False:`: FAIL `null control (seam home): ...` (1 of 6)
- M4, pins ignored, `if h != seam and sid not in pinned:` -> `if h != seam:`: FAIL `null control (seam home): ...` (1 of 6)
- M5, header condition `if _names_frozen(text):` -> `if False:`: FAIL `null control (seam home): ...` (1 of 6)
- M6, seam-name condition `if seam not in ALL_SEAMS:` -> `if False:`: FAIL `null control (seam home): ...` (1 of 6)
- Unmutated: `ALL 6 ENTITY CHECKS PASSED`.

## Null control

- On the tree: one `R.section("planted tree probe")` plus one `R.check` was planted before `tests/features.py`'s closing line. `python3 dev/audit/harnesses/features_freeze.py --check` then printed `span: ... 'planted tree probe' ...` and `lines: tests/features.py has 104575 lines, above the 104573 ...`, followed by `FEATURES FREEZE: REFUSED (2 refusal(s))`, rc=1. After restoring the file (`git diff --quiet`), it printed `FEATURES FREEZE: HOLDS (0 refusal(s))`, rc=0.
- In `tests/entities.py`, each arm runs against scratch copies of the live text. An appended, an inserted and a repeated-title section are each refused by name. The live text under the same manifest passes. One added line is refused on `lines` alone, and one removed line passes. A dhw span in `features_model.py` is refused, naming `features_dhw.py`. The same span passes in `features_dhw.py`, or when pinned. A header importing `features` is refused, and so is a script named for no seam.
- Laundering, through the gate's own `budget_raise_gate.file_raises`: when a span is appended and the manifest re-recorded in the same diff, `lines` and `spans` both come back as raises. An unchanged manifest returns `[]`.
- On this PR's own diff, adding the manifest is a raise that budget-raise-gate reads. Every leaf is FROZEN, and FROZEN counts an added leaf as a raise. That is why this body carries `## Raise justification`. Run against a body without that section, `python3 tools/policy/budget_raise_gate.py --check-body <body> --base origin/main --head HEAD` exits 1 and names the raise (Figures).

## Figures

- Lines of `tests/features.py` at merge base 43ec8e3273: `wc -l tests/features.py`, equal to the manifest's `lines`.
- Spans: `PYTHONPATH=tests python3 -c "import ast,case_select as cs; s=open('tests/features.py').read(); print(len(cs.split(s, ast.parse(s))[2]))"`, equal to the length of the manifest's `spans`.
- Home seams of the frozen spans, by the step-A rule: `python3 dev/audit/harnesses/features_freeze.py --seam tests/features.py | cut -f1 | sort | uniq -c`. The seven seam counts sum to the span count above, which is the null control on the rule (every span gets exactly one home).
- Freeze on the tree: `python3 dev/audit/harnesses/features_freeze.py --check`.
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` printed `Architecture score: dS +0.0000 NULL`.
- Structure ratchet: `PYTHONPATH=tests/hastub python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"`. It prints `MODE: FULL -- every test script runs, nothing is scoped out.` because `tests/closure.py` changes the gate itself. That is a diff the gate cannot scope, so the scripts this diff reaches were run instead: `tests/entities.py` in full and `tests/structure.py`.
- Raise reading of this diff: `python3 tools/policy/budget_raise_gate.py --check-body BODY.md --base origin/main --head HEAD`. Against a body with no raise section, it exits 1 and names `tests/features_frozen_budgets.json: lines: None -> 104573 (a pinned value the gate cannot sign as routine)` and the `spans` leaf. Against this body, it is quoted under Red checks.

## Raise justification

The raise is the creation of `tests/features_frozen_budgets.json`. All of its leaves are FROZEN, so creating it is a raise. No cap on any existing budget moves. Approval is sought under mandate 6893738184 (scope all, open to 2026-12-15T12:00Z).
Payments tried: (1) a manifest under a non-budget name (`tests/features_frozen.json`, the design note's own name): refused, because a PR could then append a span and re-record the manifest with no gate (the design review's manifest-laundering point); (2) no manifest, with the frozen span set and line count as constants in `tests/entities.py`: refused, because editing those constants is the same laundering, outside budget-raise-gate; (3) the split itself: refused on cost, since the re-key's sample estimate exceeds the cap (above). The code it adds is one harness and one `tests/entities.py` section, with no production line.
Architecture score: dS +0.0000 NULL

## Red checks

- `budget-raise-gate`: red until a review approves at the head. Creating `tests/features_frozen_budgets.json` adds two FROZEN leaves, `lines` and `spans`, which the gate reads as raises. That is deliberate: the manifest is under the gate so that a span cannot be laundered in (reviewer carry manifest-laundering). It clears with the owner's approving review, or with a mandated approval under 6893738184, using this body's `## Raise justification`. `budget_raise_gate.py --check-body` passes this body (`the body's arch_score figure is the measured one, dS +0.0000 NULL`). No cheaper detector is owed: `prepr.sh` and `--check-body` already predict the red locally, before CI.
- `tests / mutation`, predicted by `ci_predict.py` as `STALE PIN ON MAIN (not this diff's)`: `custom_components/heatpump_optimizer/flow_lift.py:FlowCurveBias.observe_temps BOOLOP 04143c3f`. That pin is on `origin/main`, and this diff touches no `custom_components/` line. Its repair belongs to main's own mutation lane.
- A local full `tests/entities.py` run on Darwin at 62d50e9 printed `3 of 2799 ENTITY CHECKS FAILED`. The first failure was the orphan census, which named the two new files: the closure commit repairs it, and `closure.orphan_files()` is now `[]`. The other two are timing checks on this machine. One is `hb:positive_control survives one hung py-spy sample` (py-spy sampling). The other is `a measured script's late-writing descendant is waited for, not recorded as nodata` (the coverage stage's late-writer wait). This diff touches neither the heartbeat sampler nor `tools/coverage/`. CI's Linux run is the authority on both.

## Unpinned sites

none: every added `.py` line is under `tests/` or `dev/`, which `prepr.sh`'s mutant draw excludes. The harness's refusals are pinned by the six mutants above.

## Forward-carry

- open-branch-port and seam-raise-path for R11-OUTSIDE-HONEST-DHW-RUNS: once this PR merges, `tests/features.py` refuses new spans and line growth. Move each new span unchanged to the seam script `python3 dev/audit/harnesses/features_freeze.py --seam <file>` names, and re-pin its own rows with `mutation_table.py --pin-killed` (design revision 5, section 3). A new seam script raises `script_runs_per_push` and `script_runs_full_case_pr` in `tests/ci_budgets.json`. That raise merges only on the owner's approving review at its head, or under a mandate in force with `## Raise justification` and an `Architecture score: dS` line. Mandate 6893738184 ends 2026-12-15T12:00Z. Carry: R11-OUTSIDE-HONEST-DHW-RUNS
- open-branch-port and seam-raise-path for R11-LATE-P2-ZONE-GATE: once this PR merges, `tests/features.py` refuses new spans and line growth. Move each new span unchanged to the seam script `python3 dev/audit/harnesses/features_freeze.py --seam <file>` names, and re-pin its own rows with `mutation_table.py --pin-killed` (design revision 5, section 3). A new seam script raises `script_runs_per_push` and `script_runs_full_case_pr` in `tests/ci_budgets.json`. That raise merges only on the owner's approving review at its head, or under a mandate in force with `## Raise justification` and an `Architecture score: dS` line. Mandate 6893738184 ends 2026-12-15T12:00Z. Carry: R11-LATE-P2-ZONE-GATE
- open-branch-port and seam-raise-path for the other groups that append to `tests/features.py`: R11-PRE-SHARED-FILES and R11-OWNER-CARD-EXTERNAL-HEAT (both carries-open, so neither is a carry destination), and R11-SEAM-inputs-freshness, R11-SEAM-learners, R11-ARCH-fabric-learner and R11-SEAM-wallclock-dst (`carry_audit.py`'s group-token pattern reads upper case only, so it cannot name them). Each needs the same text in its brief: once this PR merges, `tests/features.py` refuses new spans and line growth. Move each new span unchanged to the seam script `python3 dev/audit/harnesses/features_freeze.py --seam <file>` names, and re-pin its own rows with `mutation_table.py --pin-killed` (design revision 5, section 3). A new seam script raises `script_runs_per_push` and `script_runs_full_case_pr` in `tests/ci_budgets.json`. That raise merges only on the owner's approving review at its head, or under a mandate in force with `## Raise justification` and an `Architecture score: dS` line. Mandate 6893738184 ends 2026-12-15T12:00Z. This group keeps the item. The design note asks for these briefs to be written at this group's merge, and the orchestrator writes them on the roster's records branch. Carry: R11-OWNER-FEATURES-SPLIT
- Carry 0 (the third item above, which this group keeps): written to the briefs of R11-SEAM-inputs-freshness (roster commit e27959ad0f), R11-ARCH-fabric-learner (e59596b14b) and R11-SEAM-wallclock-dst (05883d286a, read back on the roster branch), alongside R11-OUTSIDE-HONEST-DHW-RUNS (bba003a81d), R11-LATE-P2-ZONE-GATE (b978c4c0ee) and this group's own entry (d99d3877ab). R11-PRE-SHARED-FILES, R11-OWNER-CARD-EXTERNAL-HEAT and R11-SEAM-learners are carries-open, and `roster_edit.py append-carry` refused each ("a carry goes to the live group owning the seam, else the producing group keeps the fix"), so this group keeps that part: it is not built in this PR and stays open on this group's carry, to be written to those briefs when they leave carries-open. Carry: R11-OWNER-FEATURES-SPLIT

## Friction

none
