Fix review: merge d37fea157d55bdd82fb5b7dc39937b25d954d669

bus-nonce: 9495f9804a8d78349af75acd73d5a526

Round 1 (sonnet), record PR #3272, triage batch 128 (P399 ACCEPT narrowed). Head measured: d37fea157d55bdd82fb5b7dc39937b25d954d669 (ev/HEAD.txt).

## Findings

None this PR settles. The P399 build is owed by R10-POLICY-ROLE-PACK, already carried (see Evidence).

## Evidence

- Three-dot diff: two added files, dev/programme/triage/s6-batch128.md and dev/programme/delivery/3272.md. VERSION, manifest, RELEASE_NOTES.md untouched (name-only diff greps none).
- Ruling handoff: handoff/triage-s12-batch128 at 17a48e8e8 adds only s6-batch128.md; cmp against the head's copy is IDENTICAL (ev/handoff-diff.txt). The delivery row is the record PR's own, one line, present. The roster's copy at a35c87f4 is also byte-identical to the head's.
- Carry landed: a35c87f4a is an ancestor of cab343ebe; cab343ebe's own diff (ev/carry-commit.txt) appends exactly one carry to R10-POLICY-ROLE-PACK, citing "s6-batch128.md#P399 at a35c87f4a871", with the control (driver test: no-sources and no-model refused, cloud_dispatch.py render admitted, killed mutant) and first step. origin handoff/audit-r10-roster tip is cab343ebe (ls-remote).
- Triage gate: r10_triage_gate_replay.py on the roster at cab343ebe with --cite s6-batch128.md prints "GATE R10-POLICY-ROLE-PACK[5] passes" for the P399 carry (ev/triage-gate-p399.txt); roster_edit.py --self-test: "roster_edit self-test: 242 checks, 0 failed". The replay's one other POLICY-ROLE-PACK line, [4] (P398), refuses because s6-batch127.md is not in this head's tree; that is not this PR's carry.
- Ledger figures (7 REFIRED, 342.7 min, 342 FIRED) are host-local; I could not re-derive them and they are unverified here. The ruling itself tells the fixer to re-read them at its base.
- Merge: git merge-tree --write-tree origin/main head exits 0 (ev/merge-tree.txt).
- CI: merge_train.py classify prints "GREEN d37fea157d55bdd82fb5b7dc39937b25d954d669 pending: none red: none", rc 0. No gate check red, so no root-cause answer owed. Mutation, fix harness and null control do not apply: the diff writes no production code.
- Head re-read: origin fix/triage-s12-batch128 is still d37fea157d55bdd82fb5b7dc39937b25d954d669.
