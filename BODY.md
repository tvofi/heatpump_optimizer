Part C of the duty-switch work, the carries left open when pull request 3526 merged; with thanks again to Bankaifan and pull request 3420, whose finding this part prices. Two changes: `Direction.decay` in `custom_components/heatpump_optimizer/duty_switch.py` holds `n` at `N_CAP` as booking already did, so a record stored over the cap (a part A record, written before the cap existed, is one) is held to it by the first pass instead of pricing switches for extra half-lives; and the design note records the planner's reader in its "Part A as built" section, where carries 3656875b and 036facc8 land.

## Head

cc65ca009eceba278583378afe7ae8375aa5f6ef, cut from `origin/main` e23124ff6e45 (`date -u`: 2026-11-13). The section, the mutant, the ratchet and the scoped gate were taken at its parent 5647cf9bb902; cc65ca009ece adds only the ledger rows under Unpinned sites (`git diff --stat 5647cf9bb902 cc65ca009ece` lists three files under `tests/mutation_ledger/` and nothing else), which no script those runs named reads as a test input.

## Brief carries

- Carry 0 (item 3656875b) and Carry 1 (item 036facc8), the same finding. The code was built by pull request 3526: `duty_switch.planner_fields` is the module-level reader and its one caller is `_solve_hubs` in `coordinator.py` (`git grep -n "duty_switch.planner_fields" origin/main -- custom_components` prints that one line), so `dead_top_level_symbols` does not move (`python3 tests/structure.py`, Figures). It reads `DutySwitchLearner.planner_pairs` from the in-memory learner and never a published key, so a conditional key's absence cannot reach the solve as zero; an unlatched, empty or never-arbitrated learner reads zeros, which price nothing. Pinned by the part C section's checks "the read returns zeros while a direction is unlatched, its off times with it" and "null controls from learner state: an empty learner, one under its on-threshold and an install whose every switch was kept each read a plan identical to today's on all three install classes", and by the part A section's "the coordinator names it once, for the planner's read". What this pull request adds is the landing the carries name: a bullet in `docs/design/2026-11-10-duty-switch-restart-learning/design.md`, section "Part A as built: where the code departs from this note".
- Carry 2 (item c3ad1545), two halves. **The cap on decay** is built here: `decay` scales by `min(weights(when)[1], N_CAP) / n`, the same line `handoff/r10-duty-switch-restart-learning-pr-b-p2` carries at 29370fdbb59a, so that branch's merge of this one meets an identical change on that line. **The leg order and the whole-step decision fed by `DutySwitchLearner.split`** are not built here: `split` exists only on that sibling branch (`git grep -c "def split" origin/main -- custom_components/heatpump_optimizer/duty_switch.py` prints nothing; null control, the same grep at 29370fdbb59a prints 1), and the carry's own rule gives the resolution to whichever of the two merges second, which is now the sibling, since 3526 is on `main`. The roster already binds it there: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B's carries hold "The leg order and the minimum share of a both step have one owner now, `duty_legs.py`…" undismissed, and the sibling's own body states c3ad1545.

## Mutation proof

The mutant "ceiling on decay dropped": `decay`'s factor back to `self.weights(when)[1] / n`, the section run by `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'from types import SimpleNamespace as _DspNS'` (the part C section, its first line to the script's close):

- at the head: `ALL 95 FEATURES BLOCK PASSED`, exit 0;
- with the mutant: `1 of 95 FEATURES BLOCK FAILED`, exit 1, the one red being `FAIL the cap is held on decay as well as at booking: a record stored at four times the cap is held to it by the first pass, p unchanged, and is off a day past the 28 a capped direction stays latched (control: that capped direction is still latched at 28 days)`; restored from a copy, `git diff --stat` then showing the three changed files of this commit and no more.

The design-note bullet is prose and has no mutant.

## Null control

The new check carries its own: a direction held at exactly `N_CAP` is still latched 28 days after its decay, so the check's "off a day past the 28" reads the cap and not the half-life alone. Without the fix (the mutant above) a record stored at four times the cap still weighs over `N_OFF` at 29 days and stays latched, which is the red. The 94 other checks of the section, the planner's null controls among them (empty learner, below-threshold learner, every switch kept, flat prices), pass at the head and with the mutant alike, so the change moves no plan where no record exceeds the cap.

## Figures

<!-- figure-block: scope-line mb=e23124ff6e45bac1d48b4a775dad555a37965355 head=cc65ca009eceba278583378afe7ae8375aa5f6ef -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->

- The section: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'from types import SimpleNamespace as _DspNS'`, all passed at the head; with the mutant, one failed (Mutation proof).
- The ratchet: `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED`.
- The scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`, its mode line `MODE: SCOPED`, ending `24 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN`, exit 0.
- Goldens and claim files: `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- tests/golden` prints nothing.

## Unpinned sites

None at this head. `tools/pr/prepr.sh` at 5647cf9bb902 named two added sites, `duty_switch.py:196 CLAMP_DROP` and `duty_switch.py:196 CMP_BOUND`, and a stale pin, `Direction.decay CMP_BOUND 50222946`, on the line this diff replaced. The stale row is removed, and `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` ended `PIN KILLED: 2 pinned, 0 left unpinned`, both killed by `tests/features.py`; the rows are in cc65ca009ece. CLAMP_DROP is the mutation proof's mutant.

## Red checks

none

## Forward-carry

none

## Friction

- fixer.md: cost: `features_block.py`'s marker must sit on a statement's first line; the part C section opens with a bare `R.section(` line shared by every section, so the block is started from its first import instead, which the instrument guide does not say. Carry: dismissed: one extra lookup, the refusal (a traceback naming the missing or mis-indented block) is loud
