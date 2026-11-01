Triage batch 106 rules one queue proposal from the orchestrator s10 (2026-11-01T19:35:45Z): the opener maps a part topic (`-p<N>` or `-<N>`) to no roster group, so every part handoff waits for a hand-written title override. It is the rolling batch after batch 105.

- **P363: ACCEPT, narrowed, as one carry amending rule (3) of P337's open driver, on R10-OPENER-REUSE.**
  - **The instances.** The session-local opener's log, 2026-10-31T17:36Z to 2026-11-01T19:27Z, has 69 `RESULT` lines and 7 `NEEDS-TITLE` lines. Three of the seven are part topics: `r10-fly-train-defaults-p2`, `r10-roster-ops-2-p1` and `r10-sav-comfort-p2`. The last of these is the critical-path head, which waited 14 minutes (19:21Z to 19:35Z). A fourth part topic, `r10-ux-health-p3`, needed a title override, and `r10-prepr-cap-2` has been dispatched under the same shape.
  - **The rule.** Try the exact uppercased topic first, then the topic with one `-p<N>` removed, then with one `-<N>` removed. A stripped match opens only when the handoff body's first three lines name that group as a whole name.
  - **Why exact match comes first.** R10-ROSTER-OPS-2, R10-CI-LAYOUT-P1 and R10-CI-LAYOUT-P2 are real groups.
  - **Rejected half.** Taking the title from the body's first line is rejected: `r10-roster-ops-2-p1`'s first line is a sentence of over 200 characters.
- **Re-route.** P337 and P350, which specify the open driver, have their only copies as carries 9 and 10 of R10-FLY-OPENPR-ATOMIC, a `done` group.
  - Its fold note's claims do not hold on roster `41268f418`. P337 is not R10-FLY-STANDING-CONTRACTS carry 6. P350 was ruled after #2989 merged.
  - So both are re-routed verbatim to R10-OPENER-REUSE, which is not started, has no `after`, and owns `open_pr.sh`, the script the driver launches.

The roster ops are queued `#held` and released when this file is on main: three `append-carry R10-OPENER-REUSE` lines (P337, P350, then P363). No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`b7092a69aebda0ffee5feffc4c4be1efe56f1256`; the file is the whole diff against `c88d552c7`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `triage_refusal` passes all three carries.
- With P363's verdict flipped to `REJECT`, it is refused: `dev/programme/triage/s6-batch106.md#P363 is not an ACCEPT ruling (REJECT)`.
- On roster branch `41268f418`, `op_append_carry` applies all three: R10-OPENER-REUSE goes from 6 carries to 9.

## Null control

- With the file absent, the carry is refused: `the triage ruling dev/programme/triage/s6-batch106.md is not on the roster branch or origin/main`.

## Figures

- `node tools/policy/brief_lint.mjs` on the roster after the three ops: `TOTAL: 0 error(s)`.
- No capped file is touched (`grep -ln 'open_pr\|opener' tests/*_budgets.json` prints nothing).
- `tools/audit/seat/open_pr.sh` is not in `review_packet.py`'s `HOT_FILES`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
