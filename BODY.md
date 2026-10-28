Triage batch 44 rules V132-V135 and V137-V140 as P219-P226: **V132 → P219 REJECT**, **V133 → P220 DEFER → `R10-TRAIN-OVERLAP-GRADE`** (reopen queued), **V134 → P221 REJECT**, **V135 → P222 REJECT**, **V137 → P223 ACCEPT narrowed → `R10-FLY-WORKTREE-GC`**, **V138 → P224 REJECT**, **V139 → P225 DEFER**, **V140 → P226 DEFER → `R10-ORCH-BEATD`**. V136 is unassigned in `proposals.md`; #2891's citation of it is corrected to V129 on that branch. It also corrects the headings P219 measures in the merged batches 36-40, with no verdict moving.

**P219 / V132 — REJECT (the instrument).** The heading ids run exactly seven ahead because two writers allocated one id space: the seven relays ruled as P204-P210 carried ids V124-V130 that `proposals.md` never held, and `proposals.md` later numbered different proposals from V124. A pre-commit check against `proposals.md` cannot run: its only input is out of the tree. The defect needs no check once a heading carries no id, which is the contract's form (`## P<n>: <title>`); this batch adopts it, and batches 41-43 are corrected on their own branches.

**P220 / V133 — DEFER to `R10-TRAIN-OVERLAP-GRADE`.** Carries 9 (P129), 13 (P189) and 15 already rule this. The group reads `done` while `queue_take` still drops any PR in `seen` (`merge_train.py:2516`, `:2567-2569`) and its PR #2882 touched no `seen` line, so the route is a reopen, queued for the roster seat once this file is on main. The filing's `REPLACED` line and its replacement of a still-queued entry are not carried.

**P221 / V134 — REJECT.** The `LEFT` line already names `--bot-prs`. The repair the candidate would print, "run a batch with --bot-prs", is the move that failed for #2893: the batch held the approver beat off the record PR, `sweep_bots` cannot approve, and the PR merged 49 s after the train released its hold. The mechanism goes to the orchestrator as a defect.

**P222 / V135 — REJECT.** No file in the tree produces the refusal (`git grep` finds only prose; the one repository `PreToolUse` hook has no worktree logic). It is the session host's own guard, and no roster group can change it.

**P223 / V137 — ACCEPT narrowed → `R10-FLY-WORKTREE-GC`.** A clean detached worktree whose head a remote-tracking ref or tag holds is removed as `on-remote`, after one `git fetch --prune origin` per run (the script fetches nothing today) and only when no process has its cwd inside; `locked`, dirty and young keep first. The benefit is the filer's measured rotation: 130 worktrees, 5.4 GiB free, 72 clean on remote refs (about 10 GiB).

**P224 / V138 — REJECT.** The check is a host-tool read on every sweep (about 20 KB of context a sweep, by V139's own echo size) for a failure that is already exact at the first dispatch (404, then `environment_not_found`).

**P225 / V139 — DEFER.** `cloud_dispatch.py:19-23` already publishes each payload on `dispatch/<role>-<topic>` for a standing trigger to fetch. The token benefit is an estimate, and a bodiless run must pick its dispatch by the pool claim whose failures V107 and V114 recorded. Flips on one measured update+run against one pool run, with the claim's concurrent-run refusal shown.

**P226 / V140 — DEFER → `R10-ORCH-BEATD`**, the owner of the generated orchestrator handover (P197). No cost of the misread is recorded, and the hand-kept prompt is not what `handover_prompt.py` writes.

The diff is markdown under `dev/programme/triage/` (INERT for `tests/closure.py`). Nothing is implemented and no roster file is edited.

## Head

`92138b4a717918db070c2fdaea68de90617007f8`; six files, the whole diff against `e8cb7e683`.

## Mutation proof

The gate this file feeds is `tools/audit/seat/roster_edit.py`'s `triage_refusal` (`ruling_verdict` at 455, `triage_refusal` at 466). On the committed tree, with the seat library on `sys.path`, a proposal-sourced text citing each entry:

```
s6-batch44#P219 -> dev/programme/triage/s6-batch44.md#P219 is not an ACCEPT ruling (REJECT)
s6-batch44#P220 -> dev/programme/triage/s6-batch44.md#P220 is not an ACCEPT ruling (DEFER)
s6-batch44#P221 -> dev/programme/triage/s6-batch44.md#P221 is not an ACCEPT ruling (REJECT)
s6-batch44#P222 -> dev/programme/triage/s6-batch44.md#P222 is not an ACCEPT ruling (REJECT)
s6-batch38#P206 -> None
s6-batch39#P207 -> None
s6-batch39#P208 -> None
s6-batch39#P209 -> None
s6-batch40#P211 -> None
mutant P220 DEFER->ACCEPT -> None
b44-P223.txt -> None
mutant P223 ACCEPT->DEFER -> dev/programme/triage/s6-batch44.md#P223 is not an ACCEPT ruling (DEFER)
P224 -> dev/programme/triage/s6-batch44.md#P224 is not an ACCEPT ruling (REJECT)
P225 -> dev/programme/triage/s6-batch44.md#P225 is not an ACCEPT ruling (DEFER)
P226 -> dev/programme/triage/s6-batch44.md#P226 is not an ACCEPT ruling (DEFER)
```

The mutant changes P220's `Verdict: DEFER` to `ACCEPT` in memory and the same citation passes, so the refusal reads this entry's verdict, not the file's presence. P223's carry text (the file the roster op appends, ending `triage: dev/programme/triage/s6-batch44.md#P223`) lands, and the same text against P223 mutated to `DEFER` is refused. The five `None` lines are the ACCEPT entries of the batches whose headings this PR rewrites: carries that cite them still land. `ruling_verdict` on each of P204-P211 reads the same before (origin/main) and after (this head): P204 DEFER, P205 DEFER, P206 ACCEPT, P207 ACCEPT, P208 ACCEPT, P209 ACCEPT, P210 DEFER, P211 ACCEPT.

## Null control

```
P999 -> dev/programme/triage/s6-batch44.md#P999 is not an ACCEPT ruling (no such entry)
missing -> the triage ruling dev/programme/triage/s6-batch99.md is not on the roster branch or origin/main
uncited -> proposal-sourced text cites no triage ruling (`triage: dev/programme/triage/<file>.md#P<n>`): 'proposal P3 changes a lane'
```

## Figures

- `git log --format=%cI --diff-filter=A -- dev/programme/triage/s6-batch3<n>.md`: 09:47:20Z (36), 11:33:59Z (37), 12:41:42Z (38), 17:18:24Z (39), all before `proposals.md`'s `## V124` (18:53Z).
- `tools/audit/seat/merge_train.py` at `e8cb7e683`: 5,831 lines; `seen` seeded at 2516, dropped at 2567-2569; the record branch left at 2037-2038; `git diff 4db1d3e28^1 4db1d3e28 -- tools/audit/seat/merge_train.py | grep -c seen` = 0.
- Roster at `origin/handoff/audit-r10-roster` `de410e4c9` (212 groups): `R10-TRAIN-OVERLAP-GRADE` `done`, PR 2882, 15 carries; carries 9, 13 and 15 are P129, P189 and the #2846 application of P189.
- `tools/audit/seat/INSTRUMENTS.md:516-519`: `sweep` adds "each head `queue` admits".
- `tools/audit/worktree_gc.sh` at `e8cb7e683`: 701 lines; `locked` at 529, `head_is_merged_ancestor` 388-392, `unmerged-head` 562-563; `grep -c fetch` and `grep -c lsof` both 0. `git worktree list | wc -l` = 65 and `df -h` 10 GiB free (95 %) at this seat's start.
- `tools/audit/seat/cloud_dispatch.py`: overlay environment at 32-36 and 334-341; dispatch ref and standing trigger at 19-23; update+run at 25-29. `git ls-files | grep -c orch_sweep` = 0.
- Roster `de410e4c9`: `R10-FLY-WORKTREE-GC` `not-started`, files `tools/audit/worktree_gc.sh`, 1 carry; `R10-ORCH-BEATD` `not-started`, 35 carries; `R10-FLOW-DISPATCH` `done`.
- `git grep -n "isolated git worktree\|base repo checkout"` at `e8cb7e683`: one match, `dev/audit/rounds/round7/D3/REPORT.md:4`; `grep -c worktree .claude/hooks/pre-edit.sh` = 0.

## Red checks

none

## Forward-carry

none

## Friction

none
