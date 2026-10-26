Triage batch 35 rules the five proposals appended after batch 34 (V119-V123) and answers the five measure-first issues whose bodies defer their size to a measurement. Three proposals are accepted as narrowed carries of live `not-started` groups, two are rejected with the binding cost named, and no product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`c73d8984afc4bcf4e885a02eb59e849ad2a4825d`; the file is the whole diff against `6fe5170cd7ce01e60ffebfc93e598c216e628fa3`.

## Mutation proof

`tools/audit/seat/roster_edit.py`'s triage gate refuses a carry whose cited ruling is not an ACCEPT, and that gate is this file's only consumer. Rewriting P199's `Verdict: ACCEPT` to `Verdict: DEFER` in a copy and re-running the gate prints:

```
dev/programme/triage/s6-batch35.md#P199 is not an ACCEPT ruling (DEFER)
```

On the committed file the same call returns `None` (no refusal) for all three carries, `ruling_verdict` prints ACCEPT for P199, P200 and P203 and REJECT for P201 and P202, and the gate resolves every cited ruling.

## Null control

At the merge base the file does not exist, and the gate prints `the triage ruling dev/programme/triage/s6-batch35.md is not on the roster branch or origin/main`. An entry that does not exist (`P999`) resolves to `None` and is refused the same way.

## Figures

One line per figure, with the command that printed it.

- 3 of 27 train directories carry no end line (s38, s44, s60): `for d in train/s*/; do grep -qE "TRAIN (DONE|STOPPED)" "$d"/* || echo "$d"; done`, run in the orchestrator state directory.
- 79 minutes blind and 88 minutes on the critical path: `sed -n '1124,1125p' seat-ledger.md`, in the same directory.
- `fix-review.md` at 140 of 140 lines and 2448 of 2451 tokens: `node tools/policy/policy_lint.mjs --budgets`.
- 180 of 180 agreement probes held: `node tools/policy/agreement.mjs --self-test`.
- the commit behind #2494's fix: `git log -S"shell continuation line is refused" --oneline -- tools/policy/agreement.mjs`.
- 383 first-parent commits past `07a09406`: `git log --first-parent --oneline 07a09406a1cc97076a6f28581f87f313b322a6b6..origin/main | wc -l`; from the same list, 370 are merges in the host's shape, 0 squash-shaped, and 13 are single-parent (stamps and `ci:` records).
- 73 open issues (72 besides #201) and 6 open pull requests, read at 22:20Z: `gh issue list -R tvofi/heatpump_optimizer --state open --limit 200` and `gh pr list -R tvofi/heatpump_optimizer --state open`.
- 70 open groups and 34 gated at roster tip `9937317d8`: `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`, fed to `roster_lib.open_groups`.

## Red checks

`none`. A ref with no pull request has no checks; locally the scoped gate prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out` (a markdown file is in no test's measured closure) and `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Forward-carry

- P199 ACCEPT (V119): dead-train detection and the stale-wiring flag in `tools/audit/seat/orchestrator_tick.py`'s `train()`, tick arm only. Carry: R10-FLOW-WIP
- P200 ACCEPT (V120): the four unchecked relay items stated in `dev/governance/roles/fix-review.md`, paid by deleting prose to stay inside its caps. Carry: R10-ORCH-REVIEW-PACKET
- P201 REJECT (V121): duplicate of the open #2733; its only delta, the pull-request half, is a few lines inside the tick line #2733 builds. Carry: #2733
- P202 REJECT (V122): newest-per-name inverts A5; the diagnostic that would name the red suite's id and age is worth having either way and belongs where `merge_train.py` is owned. Carry: R10-TRAIN-OVERLAP-GRADE
- P203 ACCEPT (V123): `roster_lib.gate_kind` and the tick's call site. Carry: R10-ORCH-ROSTER-SCHEMA
- MF1 (#2800): the pool-line measurement is satisfied — no pool handling exists at main, so the brief's premise holds and its deferral clause can be replaced. Carry: #2800
- MF2 (#2801): the `updated-for:` measurement is answered — three checks, the tick and nightly read it, so the deferral's premise is false. Carry: #2801
- MF3 (#2494): already fixed at `09b1d002c` and its group is done on both rosters. Leaves #2494 open for the orchestrator to close on that evidence. Carry: #2494
- MF4 (#2509): not measurable from this seat; the group's own first step is the measurement and PR #2749 carries it. Leaves #2509 open. Carry: #2509
- MF5 (#2501): not measurable from this seat; its fixer's first step is the measurement. Leaves #2501 open. Carry: #2501
- the 22 other issues a done or absorbed group still lists: close-out queue, one read per merged PR. Carry: dismissed: orchestrator close-out queue, one read per merged PR

## Friction

- seat-brief-hold: contradiction: the standing brief holds triage until tag v7.0.5 exists (`git ls-remote --tags origin 'v7.0.5*'` prints nothing) while the dispatch and proposals V119-V123 direct this batch; the rulings are written and the tag is still owed Carry: dismissed: the dispatch supersedes the standing hold
- roster-moves-under-a-count: stale: the same loader gives 71 open groups at 21:53Z and 70 at 22:20Z, so a roster figure is a reading and every one here names its time Carry: R10-ORCH-ROSTER-SCHEMA
- policy-cap: cost: fix-review.md is at 140 of 140 lines and 2448 of 2451 tokens (`node tools/policy/policy_lint.mjs --budgets`), so P200's prose must be paid by deletion Carry: R10-ORCH-REVIEW-PACKET
- duplicate-proposal: cost: V121 restated open #2733 and would have dispatched a second builder of one tick line Carry: #2733
- out-of-tree-wiring: stale: the tick's --train-log/--queue symlinks resolved to s58 while six trains ran after it, so the board described a five-hour-old train at 21:53Z Carry: dismissed: out-of-tree state, re-pointed at each launch
