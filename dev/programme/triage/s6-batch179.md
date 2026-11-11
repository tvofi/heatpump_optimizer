# Proposal triage, session s14, batch 179 (P598)

This batch rules queue line 277 (the orchestrator's intake), 2026-11-11.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster branch at `2ff0ab30e0` or later.
- The installed shim `$HOME/.local/state/hpo/bin/gh`, whose flag tables match main's
  `tools/audit/seat/shims/seat-gh:240-241`.
- `$HOME/.local/state/hpo/gh-calls.log`.
- Four reads of job `130415790006`, made through the shim and around it.

## P598: SHIM-ESCAPES-FLAG

Verdict: ACCEPT, narrowed from "add the log paths to the read arm" to the flag table, as the new
hotfix group R10-HOTFIX-SHIM-ESCAPES (S, severity high, no `after`).

Why a hotfix group:
- The defect degrades the live merge train now, so it is not left queued behind
  R10-GH-READ-RESIDUE-P3. That group runs after R10-TICK-RESIDUE (#3425 open) and
  R10-GH-READ-RESIDUE (p2 in flight).

Source: queue line 277. After the shim was reinstalled at 08:42Z, a haiku's job-log read was
refused with the record-issue comment-write message. The orchestrator suspected that the read arm
did not know the path.

The path premise is refuted. These plain GET forms all reached GitHub through the shim and
answered `gh: Not Found (HTTP 404)`, not a shim refusal:
- `repos/<o>/<r>/actions/jobs/1/logs`, plain.
- The same with `-X GET`.
- The same with `-H Accept:...`.
- The same with a leading `/`.
- The same with `-i`.
- `repos/<o>/<r>/actions/runs/1/logs` with `--method GET`.

`api_gate` (`seat-gh:275-277`) returns 0 for any GET with no write flag, whatever the path.

The measured cause:
1. The haiku made three plain reads of `actions/jobs/130415790006/logs` at 09:11:20Z, 09:11:36Z
   and 09:11:44Z (`gh-calls.log`).
2. Replayed through the shim, the plain read gives rc=1 and 0 bytes. The stderr is gh 2.98.0's own
   refusal: "the response contains terminal escape sequences; pass --allow-escape-sequences".
3. The same read with `--allow-escape-sequences` is refused by the shim: "gh shim: a comment write
   on a record issue (#201, #3394) ... refused".
4. The reason is that `--allow-escape-sequences` is in neither `API_VAL` nor `API_BOOL`
   (`seat-gh:240-241`, unchanged since `1d4ed28e4f`, 2026-11-05). So the unknown-flag arm
   (`seat-gh:268-270`) returns 1, and `gate` prints the one refusal message it has.

Impact, measured:
- `merge_train.job_log` (`merge_train.py:648`) is the tree's only Actions job-log reader. It always
  passes `ESCAPES_FLAG` (`:645`, added by `5c1bc399dd`, 2026-11-06). It falls back to a flagless
  read only on gh's "unknown flag", which is not the shim's text.
- `python3 tools/audit/seat/merge_train.py job-log 130415790006 tvofi/heatpump_optimizer` with
  the shim on PATH gives rc=1 and 0 bytes.
- The same command with the real gh first on PATH gives 1,093,937 bytes.
- `job_log`'s callers:
  - `failure_logs.sh`, which reads through `merge_train.py job-log` (`failure_logs.sh:42`).
  - `gate_raise_only` (`:675`).
  - The failed-script culprit read (`:3370`).
  - The infra rerun (`:3633`).
- On a None these callers read a raise-only gate red as a plain red, name no culprit and fire no
  infra rerun. None of them refuses or warns.
- The live train, `merge_train.py batch`, pid 90809, has `venv-ci/bin` and then
  `$HOME/.local/state/hpo/bin` on its PATH. `venv-ci/bin` has no `gh`. So the train resolves `gh`
  to the shim.
- Every shim-era read through `job_log` fails, which is 100% of them.

The fix, in `tools/audit/seat/shims/seat-gh`:
1. Add `--allow-escape-sequences` to `API_BOOL`. It is output-only, with no request body and no
   method.
2. When `api_gate` refuses an unknown flag, the shim names that flag ("gh shim: unknown gh api
   flag <x>; refused"), instead of the record-issue comment-write message. A tracker-comment write
   keeps its own message.
   - Why this part: the wrong message sent a seat and the orchestrator after a path cause that does
     not exist.

Self-test, in the shim's existing self-test home (`gh_calls.py`):
- `gh api --allow-escape-sequences repos/o/r/actions/jobs/7/logs` passes the gate.
- `gh api --allow-escape-sequences -f body=x repos/o/r/issues/201/comments` is still refused, with
  the comment-write message.
- An unknown flag (`--bogus`) is refused with the unknown-flag message.
- Mutation: dropping the flag from `API_BOOL` fails the first case.
- Null control: a plain GET of a non-tracker path passes, as today.

Cost:
- About 3 changed lines in `seat-gh` and 3 self-test cases.
- Neither file has a row in `tests/structure_budgets.json` at `cbd23f1c8b`.
- Interim workaround, the orchestrator's call: put the real gh's directory ahead of
  `$HOME/.local/state/hpo/bin` for the train, or read logs by the real gh's absolute path.

Binding: this is a defect fix on a non-production instrument, at severity high. It restores 100%
of the tree's job-log reads under the shim, against 0% today. The machinery bar does not apply.
No ratchet exemption is claimed.
