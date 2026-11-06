# BLOCKED: r10-ext-3226 round-4 fixer (superseded mid-run)

Question for the orchestrator: should the reply-frame SIZE bound below go into #3232 as a follow-up delta on the PR head, or be split into its own PR? This seat did not push `handoff/r10-ext-3226` or run `body_push.sh`, for two reasons. At 13:51Z `handoff/r10-ext-3226` was set to `9a54629e1`, and `dispatch/fixer-r10-ext-3226-recut` ordered a body-only re-cut ("NO CODE CHANGES"). Its body landed on `handoff-body/r10-ext-3226` at 14:30Z. Moving the handoff now would change a head under review (`fixer.md` step 6).

## What this ref holds (code, `handoff-wip/r10-ext-3226`, parent of this commit)

- `4eddf95fe1c7ebebc59b1257fb01a95553390f32`. It descends from `9a54629e1` (the reviewed handoff) and from PR head `6e048afc6`, and merges origin/main `4b7e1770b`. It does not contain `a6591432e`, the PR head's merge commit, whose tree is `9a54629e1`'s plus the delivery row.
- New beyond `9a54629e1`: commit `518971396`, `_REPLY_FRAME_MAX_BYTES` (256 MiB), which the frame reader checks on the requested length before `os.read` allocates it. The brief's SECURITY item asked for "a bound on the frame size as well as its time", and `9a54629e1` has only the time bound. Also new: three checks and a design-value check in `tests/features.py`, and two ledger pins (`_frame_reader.read.GUARD_OFF.821e5720`, `_frame_reader.read.CMP_BOUND.821e5720`).
- Measured at `4eddf95fe`: `ALL 4902 FEATURE CHECKS PASSED`, `ALL 2637 ENTITY CHECKS PASSED` (with `ok   R10 N-log-flood barrier`), `STRUCTURE RATCHET PASSED`, `MODE: SCOPED -- 26 script(s) run, 7 scoped out.`, and `PRE-PR: 4eddf95fe... rc=0`. The scoped gate read `28 TEST SCRIPT(S) PASSED; 6 SCOPED OUT AND NOT RUN` at `d3c5afc43`.
- Mutants run on `1b40b2058`:
  - m4 and m6: `1 of 4902 FAILED` each, on `two off-loop timeouts of one job warn once, naming it, and its next completion logs the recovery`.
  - Frame bound removed: 2 checks failed.
  - Size guard off: 2 checks failed.
  - Diagnosis translation removed: 2 checks failed.
  - Null control green.
- Reply sizes over one full feature run: the largest real reply was 22,913 bytes (`optimize_in_process`). A 50 MB round trip took a median of 0.148 s at the head and 0.095 s at origin/main.

## Proposed body

`handoff-wip/r10-ext-3226-body` holds `PR-BODY.md` for `4eddf95fe`. It passed `prepr.sh` with `rc=0`. Its `## Red checks` names `codeql / Analyze (python)`: cancelled at `timeout-minutes: 45`, job 127737658362, which needs a re-run.

## Also noted

- `handoff-wip/r10-ext-3226` was moved by a second `seat` session at 13:11Z (`9a54629e1`). This seat replayed its own work onto it, so the ref stayed fast-forward.
- Round-3 seat commits carry the `seat` identity, because the environment exports it. This seat's commits are `hpo-fixer`.
