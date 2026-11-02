Triage batch 109 records one ruling, P367, from the orchestrator s10's queue line of 2026-11-02T00:10:47Z. The proposal: the cloud reviewer and fixer brief should require foreground polling until the verdict posts, because #3155's reviewer (`cse_0189ZDZ9h5aHcURZsv2BSqoN`) ended its session with a background CI poll still running and posted no verdict. It is the rolling batch after batch 108, and the first ruling under the owner's LOG class.

- **P367: DEFER, written as LOG under the owner's 2026-11-01 ~19:50Z rule.** No carry and no group.
  - **No production merge is held.** #3155 is `record/autofix`, delivery rows only; none of its six files is under `custom_components/`. Its cost was the stamp's flush, which timed out after 3000 s; v7.1.1 was stamped at `78dd34354` with `--no-flush`.
  - **No rate is measured.** One instance in the window gives no figure above 10% on any of the four measures.
  - **The background wording is deliberate.** `tools/audit/seat/cloud_dispatch.py` lines 193 and 207 tell seats to run heavy work and the CI poll in the background, and `WAIT_LINE` (line 132) already caps a single call at 240 s.
  - **What re-opens it.** A count of cloud sessions that ended with no verdict or no return push, over all cloud dispatches in a stated window, at more than 10% of review rounds or review tokens. Or this friction holding a `custom_components/` pull request.
  - **The grammar has no LOG verdict.** `roster_edit.py` reads only ACCEPT, REJECT and DEFER, so LOG is written as DEFER, naming what would change it.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. No roster op is queued.

## Head

`3edc5da0b1dd9247357ee7323b0a5a8a1651da7b`; the file is the whole diff against `78dd34354`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P367 as `DEFER`, and a text citing `s6-batch109.md#P367` is refused: `is not an ACCEPT ruling (DEFER)`.
- With the verdict flipped to ACCEPT, it reads `ACCEPT`.
- P368 reads `None`: no such entry.

## Null control

- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch109.md is not on the roster branch or origin/main`.

## Figures

- `gh pr view 3155 --json files`: 6 files, all under `dev/programme/delivery/`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
