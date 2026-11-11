Fix review: merge 3bdc73b33650a4b40fd713d11e43c74c4e80272b

bus-nonce: 64472dfcb6f8f4a21fdb1b782e1460b9
pending-ci: tests / coverage, gate

## Evidence
- Confirm 1: dev/programme/triage/s6-batch130.md at the head is blob bacfa839a434, equal to main's copy at merge 444cf62f (blob bacfa839a434). RESULT: byte-equal.
- Confirm 2: the automatic merge of 6d347c73 and 444cf62f (merge-tree tree 8cef8779) differs from the head tree in that one file only. RESULT: no other hand edit.
- Confirm 3: roster diff 6d347c73..head is empty (0 lines); the roster snapshot is unchanged. The packet's handoff-not-applied refusal is the expected handoff-snapshot advisory, not a finding.
- Scope: the PR diff outside dev/programme/rosters/ and triage/ is only dev/programme/delivery/3377.md, its own delivery row.
- Merge: merge-tree origin/main head (7888005f) reports no conflict.
- Confirm 4: classify prints WAIT (gate red: none) after about an hour of polling; the packet showed tests / coverage in_progress. No red exists, so none is owed. owed-reds in this build takes no --pr/--head and I did not get a PR-scoped list; I could not confirm it empty, and nothing is red at this head. The relay posts this verdict only once CI is green.
