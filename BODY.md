Triage batch 65 rules the orchestrator's P296 message of 2026-10-30. `carry_audit.py` has no way to supersede a bad `Carry:` destination that an older verdict comment records, and that parks two merge-verdicted pull requests, #2925 and #2962. It is the next rolling batch under V182, after batch 64 (#2980). It holds one ruling, marked URGENT in its text: the orchestrator counts 4 carry parks this sweep. Whether to open the batch early is the orchestrator's call.
- **P296: ACCEPT option (a), narrowed, as one carry on R10-FLY-CARRY-DISPOSITION.**
  - The new grammar is `Carry: <dest> (item <id>, supersedes <old>)`. It retires `<old>` for that item only, and only when `<old>` fails `Dests.check`. A `supersedes` naming a valid destination is refused. The item must keep a valid destination, and the retired token prints as a NOTE.
  - Reproduced on the live body and comments. Each PR has exactly one non-routed row: #2925 `a3103224` (R10-RCA-PREPR-HEAD-GRADERS, not a roster group) and #2962 `75f08830` (#2959, no owner). Each item also routes to a live group. `audit()` unions destinations and marks a row bad on any invalid token, so a re-route can never cure it.
  - Option (b), approver-key edits of App verdict comments, is rejected: the comment would carry text its reviewer never wrote, and it would disagree with the bus-signed `verdict/<pr>` ref.
  - Option (c), a fresh verdict where the newest one supersedes, is rejected as the class fix: it costs a reviewer seat per instance, drops findings the newer reviewer did not restate, and does not cure today's PRs.
  - For #2925 and #2962 now: a train of their own without `--pre-flight`, under the orchestrator's ruling, as #2683 was. The pre-flight facts are checked by hand first and each waiver is recorded. Each body also gets the `supersedes` line.
  - One held roster op (`append-carry R10-FLY-CARRY-DISPOSITION`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`42eb592c65463d96cb3bc5166bfdb5710caec21e`; the file is the whole diff against `1148ee635`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P296 as `ACCEPT`. `triage_refusal` passes the carry text: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same text is refused: `dev/programme/triage/s6-batch65.md#P296 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the carry's citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- `carry_audit.audit(body, comments, carry_audit.load_dests())` was run at `1148ee635` with round roster `origin/handoff/audit-r10-roster`, over the live body and comments of each PR (one `gh api` read each).
  - #2925 gives one non-routed row, `a3103224 bad`, from review 6495961723.
  - #2962 gives one non-routed row, `75f08830 bad`, from review 6506038459.
  - With the orchestrator's patched comment substituted, each gives 0 non-routed rows.
  - Under a simulated rule that ignores a bad token on a row holding a valid destination, each also gives 0.
- The carry was appended to a copy of the roster at the `handoff/audit-r10-roster` tip and linted: `TOTAL: 0 error(s)`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
