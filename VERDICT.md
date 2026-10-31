Fix review: merge 6c320041c597210781189b2414cae58fbb04989f

bus-nonce: d86224471bb6d9dbdbc52d8f4f5e4131

## Evidence
- Round 1. Docs-only triage PR: the three-dot diff against origin/main (b646e8306) is two files, `dev/programme/triage/s6-batch68.md` and `dev/programme/delivery/2985.md`, 118 added lines. No VERSION, manifest, notes, claim, budget or closure file is touched. Head measured: 6c320041c597210781189b2414cae58fbb04989f, equal to the PR head.
- Mutation proof re-run (ev/mutation.txt). `ruling_verdict` reads P299 as ACCEPT, and `triage_refusal` passes the carry (None). With the verdict changed to REJECT it refuses: "is not an ACCEPT ruling (REJECT)". Null control, file absent: "not on the roster branch or origin/main". The body's three figures reproduce.
- `git merge-tree --write-tree origin/main <head>` exits 0 with no conflict (ev/merge-tree.txt). `tests/structure.py` at the head prints STRUCTURE RATCHET PASSED. Packet carry_audit: 0 findings; no refusals.
- Cited rulings P46, P51, P63, P97, P188, P204 and P236 exist at origin/main in the cited batch files. `R10-ORCH-BEATD` is in the roster and `#2916` (arm a) is merged. `git ls-files | grep -c 'orch_sweep\|seat-launch'` = 0, as the body says.
- Out-of-tree facts (seat-ledger lines, launch-ledger timestamps, pid 29401, `--dup` output, `sweep.md:47`) I could not re-derive from the tree; they are the orchestrator's state, not mine to verify. `tools/audit/seat/pulse.py` has no `--seat-alive` arm yet, which is consistent with a carry onto an in-progress group.
- CI (check-runs API at the head): all completed checks are success or skipped; no red. Still running when read: tests / fast, closures, coverage and browser, governance / env-matrix and instrument-self-tests, and prelude. None of them can be red for a markdown-only diff. These are not required checks I waited on, and they do not block this verdict. The body's "Red checks: none" holds so far.
- No code, so there is no finder's harness, class rule, null control beyond the above, or architecture-step-17 surface. The forward-carry is the body's carry onto R10-ORCH-BEATD, written by roster_edit after merge; the body names "Forward-carry: none", which matches a ruling whose carry the orchestrator applies.
