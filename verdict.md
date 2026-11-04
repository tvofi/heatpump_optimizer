Fix review: merge e5381d941c448e63fd3a6215378e0d3adb53e3bb

bus-nonce: 8a0a94d0f4e298840a99d98a90523456

Round 2. Round 1 blocked on a gate cancelled by the orchestrator's stand-in; the head is unmoved and the block is withdrawn.

## Evidence
- RESULT classify e5381d941c448e63fd3a6215378e0d3adb53e3bb --pr 3204: GREEN, exit 0 (pending none, red none). The only red check in the packet, tests / nightly-status, is not this PR's: the diff is one triage file and one delivery row, which it does not read.
- RESULT diff at the head, three-dot against the merge base: only dev/programme/triage/s6-batch118.md and dev/programme/delivery/3204.md. VERSION, manifest and notes untouched. No claim, budget, closure or golden file moved.
- RESULT merge-tree --write-tree origin/main head: exit 0, tree a2ab69d77, no conflict.
- Ruling shape against proposal-triage.md: one P382 entry carrying Verdict, Source, Instances, Cost and Binding. Each figure sits beside its command or ledger line. The ACCEPT runs its rule on all 76 tips with a null control. The cost names the files and records that no capped policy file is touched.
- ACCEPT destination: group R10-TICK-LEVELS exists on origin/handoff/audit-r10-roster (wave-r10-groups.json). Its file list omits cloud_dispatch.py, as the ruling says, and the ruling asks for a set-files op. The carry text cites triage: dev/programme/triage/s6-batch118.md#P382.
- Re-derived on main: grep -c BOOTSTRAP tools/pr/ci_predict.py is 0. git grep BLOCKED.md over tools, dev/governance and .claude is empty. cloud_relay.sh lines 610 to 616 are the noreturn handoff-wip arm. tick_loop.sh line 54 is the 300 s interval comment. orchestrator_tick.py is 4352 lines. d7e67e0d7 and 9bc39aede resolve. s6-batch113 P371 exists. handoff-wip tips now number 78 against the ruling's 76, which is the drift since it was written.
- Could not re-derive: the seat-ledger line numbers and timings, and the 776 fires in cloud-sessions.tsv. Both are local files of the orchestrator that this seat does not have. The 7 h 47 m bound follows arithmetically from 5 x 5 m off the 8 h 12 m but rests on the ledger.
- Stale state: dispatch/fixer-r10-rca-ci-critpath-3 now exists on origin, so the ruling's "still unanswered" has since been answered. That was true at ruling time and is not a defect.
- No mutation or both-ends step applies: the diff writes no production code, and the carry's mutants belong to R10-TICK-LEVELS.

## Findings
- Residual: the ruling cites blind_spots.py (and "a stand-in arm in blind_spots.py") but no such tracked file exists on origin/main, so "has no such arm" holds vacuously. R10-TICK-LEVELS' fixer should check where the instrument lives before acting on that line. Carry: R10-TICK-LEVELS
