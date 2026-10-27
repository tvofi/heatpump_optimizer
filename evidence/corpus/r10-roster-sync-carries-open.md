R10-ROSTER-SYNC-CARRIES-OPEN: `tools/audit/seat/roster_sync.py` did not classify the roster stage `carries-open` (a group whose code is done but which still owns open carries). Its self-test refuses a roster stage that `DERIVABLE_STAGES` and `PROTECTED_STAGES` together do not cover, so `governance` / `instrument-self-tests` went red on #2710, whose roster uses the stage. Part of #201.

Fix: `carries-open` joins `PROTECTED_STAGES`, with a comment saying what it means. It is a human disposition, so a merged PR must not rewrite it to `done`.

Per-site decision (every reader of a stage list, from `git grep -n "DERIVABLE_STAGES\|PROTECTED_STAGES\|DONE_STAGES\|WIP_STAGE" -- tools`):
- `roster_sync.py` `PROTECTED_STAGES`: add. (The skip rule itself is `stage not in DERIVABLE_STAGES`, so the group was already left alone at runtime; only the classification check was red. The tuple is documentation plus that check.)
- `roster_lib.DONE_STAGES` (`done`, `rca-done`): unchanged. A `carries-open` group still owes work, so it is not done (`replan.py` and `resume_doc.py` read this).
- `pr_cap.py` `WIP_STAGE`: unchanged. WIP is the exact stage `in-progress`, so a `carries-open` group does not count toward the WIP cap. This is the intended answer: the code is done and no seat is working on it, the carries are tracked by `carry_audit`.
- `brief_lint.mjs`: reads no stage list (the grep returns nothing there).

Decision stated for a later seat: the self-test's tree-roster check only fires once a roster carries the stage. This diff adds a roster-independent check that pins the classification, so the protection does not wait for a roster to use it.

## Head

Code head `05d056931b54d9226e2af4bd8611622fd5963812`, cut from origin/main `e97f5749b441b282e43bd99dbcbb762e9d10a369` (the merge base).

## Mutation proof

Production line mutated: the `PROTECTED_STAGES` entry `"carries-open"` removed. `python3 tools/audit/seat/roster_sync.py --self-test` then prints `FAIL carries-open is classified protected and not derivable ...` and `roster_sync self-test: 55 checks, 1 failed`; restored, `55 checks, 0 failed`. The existing `python3 tools/audit/seat/r10_roster_sync_mutants.py` (M1 to M20) still kills every plant and ends `restored`.

## Null control

The defect as it appeared on #2710, reproduced: origin/main exported (`git archive origin/main`) into a temp dir with one `dev/programme/rosters/wave-r9-groups.json` group set to `carries-open`. `python3 tools/audit/seat/roster_sync.py --self-test` there prints `FAIL every stage the tree's rosters carry is classified (derivable or protected) (got: {'carries-open': 'wave-r9-groups.json'})` and `53 checks, 1 failed`. With this diff's `roster_sync.py` copied over, the same roster prints `55 checks, 0 failed`. Honest note on the new fixture row (merged PR on a `carries-open` group, stage unchanged): it passes at the base too, because the skip rule already protects any non-derivable stage. It pins that behaviour; the classification check is the one that reddens.

## Figures

- `python3 tools/audit/seat/roster_sync.py --self-test` at head: `roster_sync self-test: 55 checks, 0 failed` (53 at base; 2 checks added).
- `python3 tools/audit/seat/r10_roster_sync_mutants.py`: every plant rc=1, ends `restored`.
- `python3 tools/audit/seat/pr_cap.py --self-test`: `pr_cap self-test: 21 checks, 0 failed`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `scope.run` names `tests/entities.py` only.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against e97f5749b441`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- Class census (fixer.md step 8), rule: `git grep -n "DERIVABLE_STAGES\|PROTECTED_STAGES\|DONE_STAGES\|WIP_STAGE" -- tools` lists every stage-list reader; dispositions in the per-site list above.

## Architecture score

`Architecture score: dS +0.0000 NULL`; no metric moved.

## Unpinned sites

none: the one production edit (a tuple entry) is killed by the added classification check.

## Red checks

`governance` / `instrument-self-tests` on #2710: `roster_sync.py --self-test` failed `every stage the tree's rosters carry is classified`. Cheaper detector: the check is already the detector, at standing cost zero beyond the self-test run, but it only runs once a roster carries the new word, so it fires on the PR that introduces the word. Earlier detection would need the roster-writing seat to run `roster_sync.py --self-test` after `roster_edit.py` adds a stage; that edit path already runs the lint gate, not this self-test. Countermeasure: not built here. A single instance; recurrence (a second new stage word) owes the root-cause path (`defect-root-cause.md`), whose natural form is `roster_edit.py` invoking the classification. Process state: gap (detector exists, wired only at the PR).

## Forward-carry

none.

## Friction

none.
