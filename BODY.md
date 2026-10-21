mrbatch result (markers-only re-reads; heads all unchanged at the listed values, merge-tree clean vs origin/main, carry_audit 0 unrouted over each verdict):
- #2571: probe/rev-2571-56cafa79 (3 items dismissed)
- #2580: probe/rev-2580-59942ae7 (2 items dismissed)
- #2578: probe/rev-2578-054b1614 (7 items dismissed, incl. the bus-nonce trailer line item efe82d0d)
- #2569: probe/rev-2569-f516a337 (2 items dismissed)
Notes: no GROUP routes used (none invented). Marker grammar needs 'dismissed:' with a colon, so markers read 'Carry: dismissed: <reason> (item <id>)'. gh pr view is blocked (GraphQL 403); heads read via REST pulls API. One red check-run, nightly-status, appears on all four heads; whether it is required was not established.
