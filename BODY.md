Root-cause record for the recurring-friction key `ci-red` (#3156), the one `R10-RCA-FRICTION-SWEEP.md` section 4b left to its own group. It re-derives the count at this merge base, names each of the 18 entries' PR and red check, and finds one verdict word covering four mechanisms. It lands a record, its evidence and one reader script, and changes neither the keying rule nor the gate. Disposes #3156

## Head

`809d977725797d0eae4339a9b5507eec41f0a159` (code head; `origin/main` `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76` merged in, measured 2026-11-07).

## Mutation proof

n/a: no production line changes; the diff is one record, its evidence under `dev/audit/rca/ci-red/` and `entries.py`, a reader. The reader's own control: asked for the misspelt key `ci-redd` it prints `ENTRIES 0 PRS 0`, against `ENTRIES 18 PRS 14` for `ci-red`.

## Null control

The unmodified tree has no `ci-red` record. The histogram row (14 / 18) is the control for the reader: `entries.py` returns the same two numbers independently, and its (PR, head, gap) columns were identical across two runs at `b4ec2f332` and `4b5d771bd`.

## Figures

- `node tools/policy/policy_lint.mjs --stats --since v7.1.2`: 93 merged PRs, `ci-red` 14 PRs / 18 entries (`dev/audit/rca/ci-red/stats_v7.1.2.txt`).
- `python3 -I dev/audit/rca/ci-red/entries.py W.json ci-red`, W.json written by the `--window-cache` flag of the command above: `ENTRIES 18 PRS 14` (`dev/audit/rca/ci-red/entries_v7.1.2.tsv`).
- Four causes (8 / 4 / 4 / 2 entries) are read from the verdict first lines in that table; groups and their mean minutes (212, 110, 297) are sums of its fourth column.
- `python3 -c "import sys; sys.path.insert(0,'tests'); import harness_headers as h; print(h.inline_scan())"` with `PYTHONPATH=tests/hastub`: prints `0`, 0.55 s; `python3 tests/harness_headers.py`: 1m59s, "ALL 112 HARNESS HEADER CHECKS PASSED".
- `bash tools/pr/prepr.sh` on a committed tree: `rc=0` at `49141f365`; main then moved by a triage-only merge (`git diff --stat b4ec2f332..origin/main`: delivery and triage notes), so it was merged in and prepr is rerun with this body.

## Red checks

none

## Forward-carry


- B, a `prepr.sh` step running `harness_headers.inline_scan()` (0.55 s) when the diff touches `dev/audit/harnesses/`, with the red/green demonstration the root-cause rule requires. Carry: #3156 (the carrier for all three until the orchestrator opens their groups; not to close on this record)
- C, teach `ci-cancelled` and route unnamed-red blocks to `root-cause-detectable` / `-unrecorded` in the reviewer vocabulary (`.claude/workflows/web-fix-wave.js` `VERDICT_CLASSES`): policy, waits for the owner's approving review. Carry: #3156
- The cause of the cross-run gate deferral (#3240, #3244) is not established. Carry: #3156

## Friction

none
