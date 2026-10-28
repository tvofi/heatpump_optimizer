Triage batch 56 rules V181 as P267: ACCEPT narrowed, into R10-TRAIN-OVERLAP-GRADE, which owns `merge_train.py`. V181 is owner-directed (2026-10-28T19:43:00Z): when the account's concurrent-job limit binds, pause the lowest-priority PR's CI so runners go to main and the train head. The owner added three amendments, at 19:44:50Z, 19:47:33Z and 19:48:44Z, which make the priority one configurable setting for every queue. The batch also checks three archived review findings the orchestrator asked to route, and finds all three already resolved.

- **Why the train owns it.** Only `merge_train.py` knows queue position. Its `--overlap` recarry starts every queued entry's CI at once, which is the contention. It already POSTs `actions/runs/<id>/rerun` in `unstale` (line 2452).
- **The pause.**
  - It triggers when a head or main job has been `queued` for at least 5 min, read on `wait_ci`'s existing poll.
  - It takes one victim per pass, the lowest-ranked first.
  - It cancels the victim's runs at its live head and records them in `paused.json`.
  - It resumes with `rerun-failed-jobs`, which keeps finished jobs, once the queue clears and on every exit path. Each train start resumes leftovers first.
- **The setting.** It is one tracked file, `dev/audit/config/ci_priority.json`, read through one parser, `tools/audit/seat/ci_priority.py --self-test`.
  - The owner's default order: main push > CP and hotfix > train head > production > instrument saving at least 12 h (by savings) > other instrument (by savings).
  - `major_savings_h` is 12, and each `savings_h` entry carries the source of its measurement.
  - Classification is mechanical. `production` means the diff touches `custom_components/`, and CP comes from `roster_lib`.
  - The reader refuses rc 2 any config that would let CP, hotfix or main be paused.
  - The setting is read by the train's pause and queue order, P266's sweep (`never_cancel`), R10-FLOW-WIP's dispatch ranking and R10-ORCH-LEDGER's owed-PR order, each through a carry.
- **review/2528, review/2545 and review/2577 are already resolved, so no carry is owed.**
  - 2528's prepr steps 3-3h were carried in R10-FLOW-JIDOKA's brief (`2ce054264`) and delivered as `heavy_run` (`1b9a86266`, `prepr.sh:767-779`).
  - 2545's merged record states that `b38c6431a` landed the fix (`N-orphaned-handoff.md:48`, `:55`), and no roster carry holds the stale instruction.
  - 2577's two survivors are pinned in `cloud_dispatch.py`'s self-test at lines 535, 544 and 585.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`86d399b5012cb1839178a88bac3c42ed60e6b3e9`; the file is the whole diff against `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P267 as `ACCEPT`.
- The gate passes all four texts that cite `#P267`: the carries for R10-TRAIN-OVERLAP-GRADE, R10-FLOW-WIP and R10-ORCH-LEDGER, and the held R10-FLY-CANCEL-SWEEP brief, which also cites `#P266`.
- Mutant (the verdict rewritten to `DEFER` in a copy): the R10-FLOW-WIP carry is refused, `#P267 is not an ACCEPT ruling (DEFER)`, so the gate reads this line.

## Null control

With the file absent, a carry citing `#P267` returns `the triage ruling dev/programme/triage/s6-batch56.md is not on the roster branch or origin/main`. So the sweep's `append-group` waits for both batch 55 and batch 56 on main.

## Figures

- `tools/audit/seat/merge_train.py`: 5831 lines; `wait_ci` at line 1142, `unstale` at line 2452.
- `git ls-tree origin/main dev/audit/config/`: `bugclasses.json`, `finding.schema.json`, `rotation.json`, `scopes.json`.
- Roster `be898eaef` kinds: instrument 105, defect 29, production 8; one hotfix-prefixed group, `R10-HOTFIX-BATCH-ERREXIT`.
- Archive tags: `archive/review-2528` `103da8f7b`, `archive/review-2545` `728c633ef`, `archive/review-2577` `16ed57ce7`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P267 ACCEPT narrowed (V181): the train pauses the lowest-ranked PR's CI when its head or main waits for a runner, and resumes it on every exit. It adds the one priority setting and its reader (`tools/audit/seat/merge_train.py`; roster `dev/programme/rosters/wave-r10-groups.json`). Carry: R10-TRAIN-OVERLAP-GRADE
- P267 ACCEPT narrowed (V181): the ranked dispatch list orders by the shared priority setting (`tools/audit/seat/pr_cap.py`). Carry: R10-FLOW-WIP
- P267 ACCEPT narrowed (V181): the owed-PR lines order by the shared priority setting, and an unresumed CI pause older than 60 min is an owed bucket (`tools/audit/seat/orchestrator_tick.py`). Carry: R10-ORCH-LEDGER

## Friction

none
