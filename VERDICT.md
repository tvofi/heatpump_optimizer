Fix review: merge 1f8f23d14840e5c83d57f4519876768479382b82

bus-nonce: ace88e3c3c1c963bc8b2438ec303d08f

Round 1. Head reviewed: 1f8f23d14840e5c83d57f4519876768479382b82 (still the PR head when written). The diff against the merge base is two files: dev/programme/triage/s6-batch49.md and dev/programme/delivery/2928.md. No production code, VERSION, manifest, notes heading, golden or claim file is touched.

## Findings

- P239 ruling (V153, replan.py live-by-evidence and the scheduled binding chain) is not built by this PR. The ruling is the deliverable, and the held roster op carries it to R10-FLOW-TOOLKIT-MODEL. Carry: R10-FLOW-TOOLKIT-MODEL
- P241 ruling (V155, review_owed skips record/autofix, one sentence in standing-dispatch.md) is not built here, and that group merges only on tvofi's approving review. Carry: R10-RECORD-HOLD-APPROVE
- P241 forward-carry, the arm (c)4 dispatch-owed fixture with a record/autofix PR that mints nothing, is owed by BEATD's group. Carry: R10-ORCH-BEATD
- P242 ruling (V156, evidence only, no bot hold) is not built here. Carry: R10-RCA-HEADMOVED
- P247 ruling creates a new group, R10-FLY-MUTANT-RESTORE, that exists only once the held append-group op lands. Carry: dismissed: registered by the held append-group op after merge
- The body's roster figures are read at roster ref 8c57b43dd; the live roster ref has since moved (be898eae at my fetch), so the PR's counterfactual figures describe a past plan. Carry: dismissed: the file quotes its ref and date, and the rulings turn on the measured slack and slot mechanism, not on the live roster

## Evidence

- RESULT mutation proof, committed file (ev/mutation_proof.out): ruling_verdict reads P237 REJECT, P238 REJECT, P239 ACCEPT, P240 REJECT, P241 ACCEPT, P242 ACCEPT, P243 REJECT, P244 DEFER, P245 REJECT, P246 REJECT, P247 ACCEPT. triage_refusal on the P239, P241, P242, P247 citations returns None. This matches the body.
- RESULT mutant 1 (P241 ACCEPT rewritten to DEFER): refused, "#P241 is not an ACCEPT ruling (DEFER)". RESULT mutant 2 (heading P239 renamed): refused, "no such entry". Both fail as the body states.
- RESULT null control: file absent returns "the triage ruling ... is not on the roster branch or origin/main"; a cite to P240 (REJECT) is refused. Matches the body.
- RESULT merge: git merge-tree --write-tree origin/main (b6f6ceca4) exits 0, no conflict, no claim file involved (ev/merge-tree.txt).
- RESULT claim files, version, notes: untouched. Steps 4 and 5 hold vacuously. The metric step 14 has no moved instrument: no budget, closures, INERT or ledger change.
- RESULT outcome counts in the body: six REJECT (P237, P238, P240, P243, P245, P246), one DEFER (P244), four ACCEPT (P239, P241, P242, P247). Matches the file.
- RESULT replan re-derived at roster 8c57b43dd with the stated start: slots 6 gives 128.97 h at seats 7 and 20; slots 7 gives 110.57 h. Matches the body.
- Cited text checked: designer.md applies to size L or XL groups only; design-review.md lines 50-52 hold the re-cut rule at the third revise; ledger.py review_owed is at line 505; merge_train.py sweep_bots is at line 1078.
- CI on this head: 7 check runs, 1 skipped (arm) and 6 queued (prelude, refresh, cancel-superseded), none concluded and none red, so no red check owes a root-cause answer. Body says Red checks: none. Heavy lanes not re-run.
- Figures I could not re-derive and so do not vouch for: the slots 10 (82.2 h) and slots 14 (76.1 h) replans (my run printed seat-cap lines and I did not read the summary), the pipelined counterfactuals (129.48 h, 128.78 h), the r = 0.045 WIP correlation over 27 snapshots, the 101-of-102 record merges count (my git log returned 331 first-parent lines under a different filter), and the 3-of-8 and 17-harness counts. These sit in rulings whose verdicts rest on mechanisms I did verify (designer.md scope, design-review re-cut rule, split already in the design).
- Forward-carry check: the roster does not yet hold the carries, because the held ops are refused until this file is on main. The body names each carry text and group, and carry_audit reports 5 routed, 0 unrouted, 0 bad destination. Finding-propagation is satisfied by the held ops gated on this file.
- No finder's harness exists for a triage ruling; the gate in roster_edit.py is the consumer, and I drove it directly.
