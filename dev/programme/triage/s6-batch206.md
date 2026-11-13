# Proposal triage, session s14, batch 206 (P637)

Sources:
- The live merge-train log, `~/.local/state/hpo/merge_train/train.log` (20364 lines at
  2026-11-11T15:15Z).
- `tools/audit/merge_fastpath.py` (`grader_specs`, `file_class`) and the workflows at origin/main.
- First-parent merge commits on origin/main.

## P637: batch grader-touching PRs that only add checks or ledger rows

Verdict: REJECT.

Source: triage queue line 314, 2026-11-11T15:08:27Z, PROPOSAL train batching is almost never
used (owner 2026-11-11: "the train can use batching with combined ci proof where possible").

Instances:
- Share routed serial, since the first `proof batch/20261108` line of train.log (`tail -n +F`,
  then distinct `#N admitted at` together with distinct `#N serial:`, conflicts excluded): 108 PRs
  routed, 61 serial (56%), 47 free. By class among the 61 serial: grader 55, workflow 18, budget 11,
  claim 6. Grader alone: 31.
- Over the whole log, the same count gives 394 PRs, 217 serial, grader on 185 of them, grader
  alone on 113.
- Batching is in use for free entries. The log holds 83 `proof batch/` lines. For example,
  batch `20261111-002834-b3` admitted #3405, #3384, #3392, #3389 and #3426, and #3355 alone went
  serial.
- Which files make `grader` fire. `grader_specs(workflow_texts(origin/main))` names 57 restore
  pathspecs. For each of the 31 grader-only PRs, its merge diff (`git diff M^1 M`) was matched
  against them. The pathspecs hit, by number of PRs:
  - `tools/audit/*.sh`: 11
  - `tools/pr/*.sh`: 7
  - `tools/audit/seat/merge_train.py`: 7
  - `tools/audit/seat/roster_lib.py`: 6
  - `tools/pr/*.py`: 4
  - `tests/entities.py`: 4
  - `tools/ci/*.py`: 3
  - `dev/audit/*.sh`, `tools/policy/*.mjs`, `tools/audit/seat/ledger.py`: 2 each

  `tests/features.py` and `tests/mutation_ledger/` are not among them.
- The proposed narrower rule (a PR that only adds rows to a grader's data batches). Of the 31
  grader-only PRs, 0 have every grader hit in a data file (`.json`, `.txt`, `.md` or `.csv`). All
  31 change grader program code. The rule therefore applies to 0 of 31 measured instances.

Cost:
- Building it means a diff-shape classifier in `merge_fastpath.py`, a hot instrument file, plus
  its self-tests and a review round. Telling "adds a check" from "changes grader logic" in `.py`
  or `.sh` source cannot be decided soundly from the diff, and a wrong free routing lets a PR
  grade itself.
- The benefit on the measured window is 0 entries moved from serial to batch.

Binding: the measured benefit is zero (0 of 31 grader-only serial PRs touch only grader data),
against a non-zero cost in a hot file and in soundness risk. The serial share comes from fixes
that edit the graders' own code. Interleaving those with what they grade is exactly what
`file_class` exists to refuse. What would reopen it: a window in which grader-only serial
entries that touch only data files reach at least 20% of serial entries.
