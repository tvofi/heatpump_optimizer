Adds `dev/programme/triage/s6-batch20.md`: four rulings, P93-P96 (S6-V28 to S6-V30, including V29's third instance), under `dev/governance/roles/proposal-triage.md`. They are batched under tvofi's 4-5-per-PR rule of 2026-10-24. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the same route the earlier batches took.

Verdicts:
- **P93 (V28) DEFER -> R10-ORCH-BEATD (P46 `--seat-alive`).** The seat queue files are append logs with `#` lines and ISO stamps, not pulse's epoch format. Teaching pulse that format is REJECTED. Interim: drop `--seat-queue` from the sweep.
- **P94 (V29) ACCEPT NARROWED.**
  - (a) Carry into R10-ORCH-BEATD: pin the sweep template's `git` reads with `-C`, plus a `sweep_render.py` fixture.
  - (b) No-code fix to the roster seat's out-of-tree `gh pr view` line: add `--repo` and print UNREADABLE.
  - A general wrapper is REJECTED.
- **P95 (V29, third instance) ACCEPT (barrier) -> R10-ORCH-BEATD.**
  - Each `standing-*.md` names the cwd-safe instrument for each read its seat makes, and a hand-written pipeline is never a check result.
  - Measured from outside any repository: `policy_lint.mjs --pr-body` and `carry_audit.py check --body` still judge correctly, while `git diff ... | wc -l` printed 0 with exit 0.
  - Rejected: a state reader, because those instruments already exist, and a PreToolUse hook, because it over-fires and the harness is the owner's to set.
- **P96 (V30) ACCEPT NARROWED.** `merge_pr.sh --carry` is REJECTED: `merge_train.py` already runs `app_approve.sh --carry` at admission and at the head, so a one-entry `run` queue carries #2762 with no new code. A merge beside a live train only moves the wait onto the train, as a main-moved CI wait of about 40 min.
  - (a) Carry into R10-FLOW-POSTMERGE: `merge_pr.sh` refuses a carried head before posting anything, and names the train route.
  - (b) Carry into R10-TRAIN-UPGRADE arm (3): a carried single added to a running train lands at that train's next batch.

## Head

`3783fe271cc524fd1fd97fb5dccfc66a4b55f4bf` merges origin/main `9d0ddf8af` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2782.md`.

`fff81a1470dad1f9801b71558771afaa7c3c71f8`, on merge base `0810d5b8f`.

## Mutation proof

n/a: there are no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads each entry (P93 DEFER, P94 ACCEPT, P95 ACCEPT, P96 ACCEPT).

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P99`) returns None. Each carry text (P94 (a), P95, P96 (a), P96 (b)) was linted by `node tools/policy/brief_lint.mjs` as the brief and carry of a not-started group in a scratch copy of the roster, with 0 errors each. The same copies, with one cited tools path made unresolvable, each gave at least 1 error, so the linter does read those texts.

## Figures

- Entries and verdicts: `grep -oE '^Verdict: (ACCEPT|DEFER|REJECT)' dev/programme/triage/s6-batch20.md | sort | uniq -c` (3 ACCEPT, 1 DEFER).

## Red checks

none

## Forward-carry

n/a: once this file is on main, the orchestrator routes each carry through `roster_edit.py`, citing this file.

## Friction

none
