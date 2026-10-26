Fix review: merge 52f7d33a3213f2757c0cc368340d936e160a97cf

bus-nonce: 49ba13e4e3d5dd410d9521deb0593110

Round 2, narrow. Head measured `52f7d33a3213f2757c0cc368340d936e160a97cf` by `git ls-remote origin refs/pull/2858/head` at start and before writing: unchanged from round 1 (probe/rev-2858-7540ca11 `31033ab8e728d1570c55e8226862b5f8b43d9bd5`). Round 1's code checks, findings and their Carry markers stand by reference; not re-run.

## Round 1's block (carry-missing, carry 11 / V64) is cleared

- Roster: `handoff/audit-r10-roster` `4d44dcbf0005b3e35c789c832121d752630824f2` (append-carry) and `2adcc52871409939e3c9adcc880966845b6f6332` (set-after). `ev/roster.diff` (071c715da..2adcc5287) touches only R10-FLOW-BODY-ONLY: `after` gains `R10-FLY-OPENPR-ATOMIC`; `carry` gains one entry whose text after the provenance prefix "From #2858's fix review (blocked at 52f7d33a, probe/rev-2858-7540ca11 31033ab8): " equals body item 11's text byte-for-byte up to its routing suffix (" Carried into ... Carry: R10-FLOW-BODY-ONLY"), controls included (one PR per topic, second concurrent pass exits 75, handoff-to-open latency before and after).
- Body: `ev/body.diff` (GitHub userContentEdits, round-1 body edited 2026-10-26T08:22:12Z vs latest 16:28:24Z) changes exactly lines 103 and 111, each only appending "Carried into `dev/programme/rosters/wave-r10-groups.json`, stage R10-FLOW-BODY-ONLY (carry index 11), on handoff/audit-r10-roster at 2adcc52871409939e3c9adcc880966845b6f6332." before its marker. The live body (`ev/body-live.md`) equals the latest edit apart from one trailing newline.
- RESULT `tools/audit/carry_audit.py pr 2858` (from origin/main): `1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc 0.
- RESULT `pr-contract / pr-contract` at the head, run started 2026-10-26T16:29:55Z after the body edit: completed success (actions run 40359465765).

Residual from round 1, unchanged: the ROWLESS repair drops the row's group suffix. Carry: R10-FLY-OPENPR-ATOMIC
