Triage batch 179 rules queue line 277, 2026-11-11. It holds one ruling.

- **P598, ACCEPT, narrowed: SHIM-ESCAPES-FLAG, as the new hotfix group R10-HOTFIX-SHIM-ESCAPES.**
  - The shim's read arm already passes every GET path. Six log-path variants reached GitHub and answered 404, so the proposed path fix is refuted.
  - The real cause: gh 2.98.0 needs `--allow-escape-sequences` for a job log, and the shim refuses that flag as unknown, printing its record-issue comment-write message.
  - `merge_train.job_log`, the tree's one job-log reader, always passes the flag. Under the shim it reads 0 bytes, against 1,093,937 with the real gh. failure_logs.sh and the live train's gate_raise_only, culprit and infra-rerun reads are blind.
  - The fix adds the flag to `API_BOOL` and gives an unknown flag its own refusal message.

The diff is one file against the merge base: `dev/programme/triage/s6-batch179.md`, the ruling. No product behaviour changes.

## Head

`9f07ed05dd4b4c05523700432a42a237e9ed40c3`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P598 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P598 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P599 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...9f07ed05dd4b4c05523700432a42a237e9ed40c3`: 1 file, 1 commit.
- The figures come from `gh-calls.log`, from four reads of job 130415790006 made through the shim and around it, from the train process's PATH, and from `seat-gh` and `merge_train.py` at `cbd23f1c8b`. Each is cited beside its command in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
