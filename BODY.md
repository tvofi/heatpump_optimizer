Triage batch 55 rules V180 as P266. V180 was filed at 2026-10-28T19:22:17Z and is owner-directed: tvofi said the account's concurrent-job limit is the CI bottleneck, so cancel superseded runs. The ruling is ACCEPT narrowed: a `sweep` subcommand of the existing `tools/pr/cancel_superseded.py`, in a new fly-in, R10-FLY-CANCEL-SWEEP. No group on the live roster owns that file.

- **Why the existing canceller misses these runs.** `cancel_superseded.py run` runs inside the newer run (`ci.yml` line 154). While that run waits for a runner, it cancels nothing. Two Actions listings show it:
  - #2927: runs at `dad80f255` (19:09Z) stayed active while the live head's run was `queued`, until the manual pass at 19:21Z.
  - #2928: the same at `582d0e694`.
  - Each pair is the first push of `open_pr.sh`'s two-push open (lines 70 and 84).
- **The shape.**
  - One predicate source: `candidates()`, line 48, reused.
  - Each pass makes one open-PR listing and one runs listing per active status.
  - It never cancels a run at the live head, a run on `main`, or a `push`, `workflow_run`, `schedule` or `pull_request_target` event, so train-hold, beat and record pushes are safe by construction.
  - It skips a branch whose live head is authored by `github-actions[bot]`. That is the existing autofix rule.
  - It reports ghost runs and never cancels them, and it fails soft.
- **Policy.** The file is code-owned (`.github/CODEOWNERS:75`), so the group's PR merges on tvofi's approving review.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`385c6cde5688319e8b4d6783a202acdde6435fe9`; the file is the whole diff against `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P266 as `ACCEPT`, and the new group's brief, which cites `#P266`, passes.
- Mutant (the verdict rewritten to `DEFER` in a copy): the brief is refused, `#P266 is not an ACCEPT ruling (DEFER)`, so the gate reads this line.

## Null control

With the file absent, the same call returns `the triage ruling dev/programme/triage/s6-batch55.md is not on the roster branch or origin/main`.

## Figures

- `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?branch=fix/triage-s7-batch54&per_page=30'`: runs 40751731241 and 40751736668 at `dad80f255`, conclusion `cancelled`, `updated_at` 19:21:29Z and 19:21:30Z; 40751761625 at `b9c96f4fa`, `queued`.
- The same for `fix/triage-s7-batch49`: 40752875163 and 40752880041 at `582d0e694` cancelled at 19:21:42Z and 19:21:11Z; 40752909198 at `1f8f23d14`, `queued`.
- `tools/pr/cancel_superseded.py`: 219 lines; `candidates` at line 48; `092861f05` (2026-10-18). `grep -c R10-CI-CONCURRENCY` on the roster file at `be898eaef`: 0.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P266 ACCEPT narrowed (V180): the new fly-in R10-FLY-CANCEL-SWEEP adds `cancel_superseded.py sweep`, reusing `candidates()` (`tools/pr/cancel_superseded.py`). The group does not exist until its held `append-group` op lands, and the roster gate refuses that op until this file is on main. Carry: dismissed: registered by the held append-group op after merge

## Friction

none
