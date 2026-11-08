Adopts outside pull request 3292 (contributor Bankaifan, fork head f20c98084b179c85d2c834adc4caf49dc05631d8): a configured input the cycle finds `missing_entity` or `unavailable` is re-read as soon as its entity reports a value, not one `optimization_interval` later. The contributor's four commits are kept with their authorship; their trailers naming an assistant session were dropped from the messages, and the contributor is credited by the Co-authored-by trailer below. The fork's `dev/programme/carries/carry-201.json` hunk is dropped (a programme record; the orchestrator rules it in or not). One added commit drops a stale mutation-ledger pin that the `has_value` helper made unreachable. Independent review: read from the merged tree; the design matches `away.watch_away_inputs` (debounced `async_request_refresh`), `inputs.py` imports no Home Assistant, the watch reads nothing itself so every guard applies, and release latches (#236).

Closes #3292 on merge (close it with thanks once this merges). The fork's archscore-gap carry rode in the dropped carry-201 hunk; the orchestrator decides whether to land it. Plan page link for the outside-intake ruling: owed on 3292 by the orchestrator.

Co-authored-by: Daniel <476059+Bankaifan@users.noreply.github.com>

## Head

1adbc478ca787862482a4697309ef908ef159f2d (merge head: PR head 7d1554cfc3017d0cdc95c44084c62492f8ccba98 merged with origin/main 48af0864a430, measured 2026-11-08T02:11Z; the first merge, 1c06fbab6931 against e36e5327dde8, carried the one conflict below and the second, onto 48af0864a430, was clean and touched no file under `custom_components/` or `tests/features.py`). The earlier handoff 71c249c81fd1 differs from 7d1554cf only by the mutation-autofix pin commit. Main moved under the head, so this branch is merged with it (fixer.md step 6), not re-cut.

## Resolution delta: coordinator.py

One conflict, the `from .inputs import (...)` list. Merge base dee8b413fd7d. Main's side added `InputReading`; the head's side added `InputReturnWatch`. Resolved as the union: both names, in sorted order. Read back against both parents: `InputReading` is used 2 times at `origin/main` and 2 at the merged tree; `InputReturnWatch` is used 3 times at 7d1554cf and 3 at the merged tree; both classes are defined in `inputs.py`. No other line of the file was edited by the resolution.

## Mutation proof

Mutant: the predicate line `self._input_returns.arm(reader.health)` in `_update_current_state` replaced by `pass`, `PYTHONPATH=tests/hastub python3 tests/features.py` run from a `git archive` copy of the first merge head 1c06fbab6931 (re-run there; the second merge changed no production code). Red section checks: the read that found it absent watches exactly that entity; the entity reporting a value asks for one refresh; that refresh re-reads it; a return one second short of an interval; a return exactly one interval after; the in-flight precondition; the next report after a dropped request; a rejected returned value keeps learners frozen; an input read as unavailable is watched. (The `recorded_at` check also reads red in any archive copy: #1713, the runner's.) The fork's own mutant table (spacing guard, release latch, `has_value`, hold start) is the contributor's and was not re-run here.

## Null control

Unmutated head, same command, from the worktree: `ALL 4941 FEATURE CHECKS PASSED`. Mutant: `10 of 4941 FEATURE CHECKS FAILED`. Flat-price null control: kept, not applicable (no cost figure). The new watch-level checks have their own null: an unchanged watched set neither re-registers nor drops the listener, and a settled request is stamped once.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/structure.py` at 1c06fbab6931 and in prepr's `merged structure` step: `STRUCTURE RATCHET PASSED`, no budget re-recorded.
- Scoped gate: not re-run on the merged head; the group's own block, `PYTHONPATH=tests/hastub python3 tests/features.py`, ran in full at 1c06fbab6931 (`ALL 4941 FEATURE CHECKS PASSED`) and the remaining scripts are left to CI.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` at 1c06fbab6931 and again at 1adbc478ca78: `PRE-PR ... rc=0` (closures skipped by the brief; `closures-autofix` is CI's).
- Diff-mutant run (`tools/audit/seat/mutant_run.py --diff origin/main...HEAD`, `MUTANT_CMD` = the new feature block through `features_block.py`, 20 checks): wall time 34 s; first run 4 survivors, after the added test 1 survivor (equivalent, below).

## Unpinned sites

Step 6d lists these 12; mutation-autofix pins the killed ones after the push. The mutant run above killed all but one.

- custom_components/heatpump_optimizer/coordinator.py:641 RETURN_DEL: killed by the feature block (the watch registers through it); pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:910 GUARD_OFF: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1113 BOOLOP: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1113 RETURN_DEL: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1166 GUARD_OFF: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1175 BOOLOP: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1177 GUARD_OFF: survived at first, now killed by "an unchanged watched set neither re-registers nor drops the listener"; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1181 GUARD_OFF: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1194 BOOLOP: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1194 CMP_BOUND: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1194 GUARD_OFF: killed by the feature block; pinned by mutation-autofix.
- custom_components/heatpump_optimizer/inputs.py:1201 GUARD_OFF: killed by the feature block; pinned by mutation-autofix.

Survivor with no key above (the diff mutator's `CALL_DEL`, not in step 6d's list): inputs.py:1209 CALL_DEL (`self._pending.clear()` in `release`) is equivalent: after `release`, `arm` returns at its first line and `_on_event` returns on `self.released`, so `_pending` is never read again. inputs.py:1171 CALL_DEL (`self._pending.clear()` in `arm`) and :1178 RETURN_DEL were survivors too and are killed by the two added checks.

## Red checks

Concluded reds at head 7d1554cfc3017d0cdc95c44084c62492f8ccba98, listed from the check-runs API over all pages:

- `tests / mutation` (red at 71c249c81fd1, green at 7d1554cf): cause, the killed-mutant pins for the 12 sites under `## Unpinned sites` were missing from the handoff; `mutation-autofix` wrote them in 7d1554cf and the check is now success. Root-cause state (a)-(d): (c), the process ran as designed. The ordering is by design: the pins can only be written after the push, from the mutant run in CI. Cheaper detector: the diff-mutant step of `tools/pr/prepr.sh` already stands and ran here (34 s, `## Figures`); it finds the sites but the pin file is written only by CI, so a red-then-autofix round is the standing cost, about one CI cycle with no seat time. Finding: no cheaper detector exists for the pin write itself, since the pins need the CI mutant run. Nothing is built.
- `pr-contract / pr-contract`: red at this head because this body named the head 71c249c8 and `## Red checks` did not name `tests / mutation`. Cheaper detector: `tools/pr/prepr.sh --body-check`, which ran locally before this body was pushed; the first body was written before the bot commit existed, so the red could not be seen then. Answered by this section and the new `## Head`.
- `gate`: the aggregate over the required contexts, red only because `pr-contract` above is red; it has no cause of its own.

## Forward-carry

none

## Friction

none
