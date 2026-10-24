**Carry — the critical-path set must be republished at each wave edge.**

#2526 makes the local gate lease's priority **derived**: a ticket whose group is in
`dev/programme/rosters/critical-path.json` on the roster branch takes first place in the lease queue, with no
per-pull-request decision. The lease itself stays generic; `prepr.sh` derives the default.

That creates a standing duty on this issue, which the producing pull request routes as `Carry: #201`:

- **Republish `critical-path.json` whenever the wave edge moves** — a group completes, a wave opens, or the
  critical path changes for any other reason. The file carries an `at` ISO timestamp; the derivation does not
  read it today, so a stale-but-present file keeps granting priority 1 indefinitely. Age is the human check.
- **State the set on this issue at the same moment.** The file is what the tool reads; the comment is what a
  resuming session reads, and the reviewer confirmed this carry had no comment behind it until now.
- Malformed, unreadable or missing inputs already resolve to priority 0 — that direction is safe. The unsafe
  direction is a well-formed set that is simply out of date.

Raised by the round-10 review of #2526 (head `baa75f58`), which recorded it as a merge boundary rather than a
blocking defect: the mechanism is sound, the staleness is an operating discipline.
