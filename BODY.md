Triage batch 84 rules the orchestrator s8's slip proposal of 2026-10-31 (02:42Z, #3016). `cloud_relay.sh` ran `update_pr` as soon as `handoff/<topic>` moved and read the previous round's body before the fixer's `body_push.sh` landed the new one, so prepr refused a head the new body answered. This is the next rolling batch under V182, after batch 83. It holds one ruling and one held roster op.

- **P321: ACCEPT as already carried, with a priority flag, on R10-FLOW-BODY-ONLY.**
  - P233 (`s6-batch46.md`, 2026-10-28) is this fix: a `Code: <head>` trailer written by `body_push.sh`, and `cloud_relay.sh`'s `handoff_arm` refusing to update on a body that names another head (`handoff-body-stale`, retried next pass).
  - It is unbuilt: no `Code:` line in either file at `861f949ae`. The group's `next_step` has read "DISPATCH NOW" since 2026-10-27, so the roster op raises it to dispatch next.
  - REJECTED: the filing's timestamp form (body commit older than code commit). A re-body of an unchanged head is newer and correct, and clocks skew between runner and host, whereas the trailer names the head exactly.
  - DEFER, with a re-open condition: "BUSY on a dead lock, no retry for 4 minutes". `update_pr.sh` exits 75 on a held lock and the relay retries next pass. One instance, cause unmeasured. It re-opens on this group if a relay BUSY persists more than two passes on a lock whose holder pid is dead.
  - Instances: #3016 now, after #2890, #2891 and #2894 in P233. That makes it an audit class whose barrier is carried and unbuilt.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`9145ad65e8cb2b288aabf8235895b3001b56cb07`; the file is the whole diff against `861f949ae`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P321 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch84.md#P321`: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch84.md#P321 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main. The carry, appended to the live roster, gives `brief_lint.mjs` `TOTAL: 0 error(s)`.

## Figures

- `git grep -n 'Code:' 861f949ae -- tools/audit/seat/body_push.sh tools/audit/seat/cloud_relay.sh` prints nothing.
- `git log --diff-filter=A --format=%cI -- dev/programme/triage/s6-batch46.md` gives `2026-10-28T04:49:07+01:00`.
- `git show origin/main:tools/audit/seat/update_pr.sh` lines 12-16 describe exit 75 (BUSY) on a held branch lock, retried by `cloud_relay.sh` on its next pass.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
