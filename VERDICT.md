Fix review: blocked a945275dd01d5a7ee100598315bd94e20652cb25 mutation-vacuous: running_signal.refresh tick-before-note survives the build's block and the whole features.py

bus-nonce: 04cbaba8e3db4be481a55168757ad651

## Block

- Survivor `own-tick-before-note`, at `custom_components/heatpump_optimizer/running_signal.py` in `refresh`, a line this round added (eddba039c3). The mutant swaps `note(sig, when)` and `read = running_now(sig) is True`, so each tick hears the class as it was before this refresh's re-read.
  - It survives the build's features.py block (`tools/audit/seat/mutant_run.py --spec`: `SURVIVED NULL`, `SURVIVED own-tick-before-note`; ev/own-mutants.txt).
  - It also survives the whole `tests/features.py`, applied in place at this head: `ALL 5709 FEATURE CHECKS PASSED`, the same as unmutated (ev/own-order-wholescript-manual.txt, ev/whole-unmutated.txt).
  - It changes behaviour. The probe ev/probe_order.py drives the production `running_signal` and `wear.StartCounter(hold=RiseHold())`: a confirmed meter rise is held through one refresh read running, the element latch is then read at the next refresh with no meter event, and the no-class change is then confirmed. The head prints `RESULT starts=0`; the mutant prints `RESULT starts=1`, a false start (ev/probe-order-head.txt, ev/probe-order-mutant.txt).
  - This is the case the module docstring and the coordinator name as the reason for the per-refresh re-read: "the element's latch and the commanded draw change there without a meter event". So the order matters on exactly the S7 path owner ruling D1 bought.
  - The tracked harness's `refresh-only-note` mutant deletes the note, and that is killed, but no check pins that the note comes before the read.
  - Owed: a features.py check in the build's block where a refresh's own re-read (latch or commanded draw, no state event) moves the class off running while a rise is held, plus the mutant in `dev/audit/harnesses/start_counter_edges_mutants.py`. Carry: R10-START-COUNTER-EDGES

## Findings

- Survivor own-tick-before-note (running_signal.refresh, tick read before the re-read): behavioural, unpinned by the build's block and by the whole features.py; owed a check and a tracked mutant (## Block). Carry: R10-START-COUNTER-EDGES

## Scope

This is a later round on PR #3598. The packet's `## Review scope` line reads `full` only because the previous draft at ca0e06eb3d (probe/rev-3598-76fd235e) was never posted. The brief scopes this round to `git diff ca0e06eb3d a945275dd0` plus that draft's findings, and I reviewed it that way.

The PR's own delta is six commits: fbe6b63a3a, eddba039c3, 87cb31b6d3, b9eab8044c, cd4cadad7a and 2c7f3694b2. They add the refresh-held start (owner ruling D1) in `wear.py` (`RiseHold`, `StartCounter.hear` and `StartCounter.refresh`), `running_signal.py` (`refresh`, ticks) and `coordinator.py` (2 lines), plus its tests, the harnesses and the structure record. The rest of the range is the merge of origin/main a39627da59.

The production delta puts at risk only the reviewed counter path it feeds (`StartCounter.fold` and its restore queue), and I read that path again. Role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. This is the second reviewer round on this group's code since its last block.

## Prior findings

- The draft's one finding, the S7 residual, is resolved. It was built in this PR under owner ruling D1. `s7_60s`, `s7_30s`, `s7r_60s` and `s7r_30s` read 5 at 092746903f and 0 at this head, and the null control `s7r_real` reads 6 at both ends (re-measured, below).

## Evidence

- RESULT mutation proof at the head: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/start_counter_edges_mutants.py` prints `BASELINE [(0, False), (0, False)]`, 42 KILLED and `RESULT survived=0` (ev/mutants-head.txt). This matches the body.
- RESULT own mutants over the build's block (ev/own-mutants.txt):
  - KILLED: the refresh release keeping the held rise, the tick reading `tracker.settled` and ignoring pending, a no-class edge keeping the hold, and a short run passing on from no class.
  - SURVIVED: `own-tick-before-note` (## Block).
  - The `mutant_run.py` whole-script runs, in a copy (ev/own-order-wholescript-copytree.txt) and with `--in-place` (ev/own-order-wholescript-inplace.txt), printed `KILLED NULL` and measured nothing. The manual in-place run above replaces them. The unmutated whole script passes when run directly (ev/whole-unmutated.txt).
- RESULT harness (the fixer's, disclosed as such; no finder harness exists): `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/start_counter_edges.py`.
  - At this head: control=3, perturbed=4, restored=8, s7_60s=0, s7_30s=0, s7r_60s=0, s7r_30s=0, s7r_real=6 (ev/harness-head.txt).
  - At a git-archive export of 092746903f with the head's harness: 3, 4, 8, 5, 5, 5, 5, 6 (ev/harness-092746903f.txt).
  - Every figure in the body's `## Null control` and `## Figures` for this round matches.
- Structure: `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED` (ev/structure-head.txt). The `coordinator_multiassigned_attrs` 105 -> 104 record on the merge is a lowering with its reason in the commit, and no budget is raised. Typing: `ALL 12 typing-ruler source checks PASSED` (ev/typing-head.txt).
- Claims and version: the three-dot diff touches neither `VERSION`, `manifest.json` nor `RELEASE_NOTES.md`, nor either claim file.
- Merge: `git merge-tree --write-tree origin/main a945275dd0` at origin/main exits 0 (ev/merge-tree.txt).
- Code read of the delta:
  - The hold is chosen by `compressor_freq_sensor`, the same config key `running_signal.source` reads, so the hold and the source cannot disagree.
  - `detach` clears the ticks.
  - A release queues through `fold` while the counter is unrestored.
  - Releasing at the rise's own time keeps the month.
- Credit: the body opens "Thanks to Bankaifan, who reported ..." and names the approved design and its review.
- CI at this head, read live: `tests / mutation` failed at 12:32 and `gate` failed as its roll-up. The body's `## Unpinned sites` leaves this round's 14 sites to `mutation-autofix`, and `tests / mutation-pins (1)` and `(2)` were still in progress (`ci-autofix.md`: wait for the bot commit). `governance / instrument-self-tests` concluded success, so no INTRODUCED red. `merge_train.py classify a945275dd0 --pr 3598`, polled from 12:51 onward, printed only `WAIT ... pending: gate red: none` (ev/classify.log).
- Owed-reds set: ev/owed-reds.txt. The body's `## Red checks` names `tests / mutation` (earlier heads) and the unpinned sites. The verdict is blocked on code, so no red answer is judged here.
