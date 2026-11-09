Fix review: merge 1d6414078555e396b0fa5e23327be31050c5ce2a

bus-nonce: 631c583596af69d0cad5467ec5b52dd2

Round 1 (first review of this PR). Measured at 1d6414078555e396b0fa5e23327be31050c5ce2a in a detached worktree.

## Evidence

- Head: `ev/HEAD.txt`. The body's figures were taken at 566ff8352; `review_carry.py 566ff8352 1d6414078555e396b0fa5e23327be31050c5ce2a` prints CARRY, and the three-dot diff excluding the delivery row hashes identically at both, so the figures carry.
- `python3 -I tools/pr/figure_block.py --self-test`: RESULT figure_block self-test: 11 checks, 0 failed.
- Mutants on figure_block.py (`ev/mut1.txt`..`mut3.txt`): verify never flagging a typed block fails "hand-typed value"; reading the registry from HEAD instead of base fails "registered only by the head"; dropping the stale head/mb check fails "another head" and "moved head". None vacuous.
- `body_push.sh --self-test`: 34 checks, 0 failed, including the mutant with the `# mut:keep` refresh deleted (`ev/body_push.txt`).
- All three registered instruments render at the head (`ev/render.txt`): merge-base, structure-ratchet (STRUCTURE RATCHET PASSED), scope-line (MODE: FULL). Run with --base HEAD because the base has no registry yet, the PR's own bootstrap, which its body discloses.
- `git merge-tree --write-tree origin/main 1d6414078555e396b0fa5e23327be31050c5ce2a` (main at fdc8d21ad): rc 0, no conflict.
- VERSION, manifest, RELEASE_NOTES, golden and claim files: untouched (name-only three-dot diff of 15 files has none).
- Security read: pr-contract's job holds read-only grants; the registry and program come from base (restored tools/pr/*.py, `git checkout base -- files`), and the author names a registered instrument, not a command. The head's tree is only measured. Head code already runs in the ci.yml units, so this widens nothing.
- Class rule: the diff adds one grammar with one parser (figure_block.parse) and one offline mirror (figureBlockProblems); the body names no enumeration rule and its issue states one seam, so the class is one seam.
- Red checks: governance / policy-docs went red earlier and the body's Red checks section answers it (base's pending entry, #3312). The packet's digest has no other red check at this head.
- CI classify: `merge_train.py classify 1d6414078555e396b0fa5e23327be31050c5ce2a --pr 3355` exits 1, "red: gate", on three polls. The cause is the check suite of the earlier CI edit run 42528917546 (body edit, 22:10Z, gate job 128881063522, failure), which latest_runs keeps as the worst gate. The later CI edit run 42529336031 and CI code run 42528917224 both concluded success, with gate jobs 128904020574 and 128902445699 success, and every other check in the packet digest is success or skipped. I judge the head green on its code run and read the rc 1 as a stale deferred edit-run gate that gate-sweep has not re-run. It is not a defect of this diff. The orchestrator's train will read the same rc 1 until the sweep re-runs it.
- Not re-derived: the entities (2668 checks) and field_coverage counts in the body; I took the packet's figure_lint "8 resolved" and CI's green `tests / closures`, `governance / policy-docs` and `tests / mutation` instead.

## Findings

- Follow-up: classify reads RED on the superseded edit-run gate suite 115199371570 although a later edit run and the code run are green; the orchestrator must see gate-sweep re-run it, or re-run it, before the train merges. Carry: dismissed: orchestrator-side CI mechanics, not a defect in this diff
