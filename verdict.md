Fix review: merge ef456f2b24b622c928603b26d8d1ce37b9b75014

bus-nonce: 9389276a2785f008956b386202131c19

## Evidence

- Scope: round 9b body-only re-check. Head unchanged: `git ls-remote origin refs/pull/3078/head` = ef456f2b24b622c928603b26d8d1ce37b9b75014.
- (1) The live PR body carries the literal text `Carry: R10-REPLAY-OPEN-LOG`, ending the `## Forward-carry` bullet for the unpinned default-SQLite open line (#3078 r8 finding).
- (2) R10-REPLAY-OPEN-LOG is a group in wave-r10-groups.json at roster ref 5dc16bbe (`"group": "R10-REPLAY-OPEN-LOG"`, files tools/replay/export.py, tests/replay.py).
- carry_audit pr 3078 with that roster: "3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)"; bbc4cafa routed to R10-REPLAY-OPEN-LOG. Full output in ev/carry_audit.txt.
- Code, mutants, CodeQL and CI were not re-measured; round 9 settled them and the head is unchanged.
