Fix review: merge ddd88d3ede589217e60d8cefb06ff48c3f2fe75a

bus-nonce: e5b00531ed373ac71b0062bd89cb9968

Round 1. Head measured: ddd88d3ede589217e60d8cefb06ff48c3f2fe75a (the PR head at the time of review).

## Findings

- P292's mutation text names the second perturbed red `tests / delivery-status`, but the check-run is `governance / delivery-status` (ci.yml calls governance.yml from job `governance`; the ruling's own Instances section has it right). With the real three names the self-test also fails rc 1 (3 errors against the ruling's 2), so the verdict stands; the R10-FLY-RECORD-RED-NAMES fixer must take the names from the one definition, not from the mutation sentence. Carry: R10-FLY-RECORD-RED-NAMES | #2974 | O1 | dismissed: the ruling text is a prose slip in the perturbation; the fix clause 1-2 names the right form and the group brief carries the full names

## Evidence

- RESULT P292: record_row.py --self-test is rc 0 as committed; with reds set to the prefixed names it is rc 1 ("body check passes the generated body over the reporter reds"). Reproduced with both spellings (ev/perturbation.txt). review_packet.py gate_digest keys on r["name"] (the full name), confirmed in code; check-runs read `tests / nightly-status`, `governance / record`, `governance / delivery-status`.
- RESULT P291: R10-TRAIN-OVERLAP-GRADE carries 9, 13 and 15 (P129 predicate, P189 amendment, #2846 round-2) exist in wave-r10-groups.json. s6-batch26.md#P129 Verdict is ACCEPT; s6-batch32.md#P189 Verdict is "ACCEPT narrowed", which the ruling describes as "as amended". merge_train.py has no shared admission predicate: train_add (893) consults QUEUE_PENDING and the spool, queue_take (2672) consults only `seen`, Train.skip (2602) does not touch QUEUE_PENDING. The ruling's "unbuilt" claim holds at this head.
- RESULT ruling_verdict reads P291 and P292 as ACCEPT; triage_refusal returns None for citations of both; a DEFER perturbation is refused. The R10-FLY-RECORD-RED-NAMES brief is not in this diff (the roster op is held until merge), so triage_refusal was run on citation text of the same shape, not on that brief.
- Figures I could not re-derive: the live merge_train/train.log lines (13 ALREADY lines, batch 20261029-193537-b4, #2917/#2872/#2961/#2970 skips) live on the orchestrator's machine; the cited code paths that emit them match, the log text itself is unverified here.
- Diff is two files: the triage batch and the PR's own delivery row. The body's "one markdown file" line is covered by its ## Head section. No VERSION, manifest or notes change; no claim or golden file touched; no production code, so the mutation lane draws no mutant.
- CI at read time: `tests / nightly-status` is red. It grades main and the diff (two markdown files under dev/programme) reaches nothing it reads, so it is main's red, not this PR's. Several checks (fast, coverage, browser, closures, env-matrix, instrument-self-tests) were still running at read time; every concluded check besides nightly-status is success or skipped. review_packet refused red-unanswered on nightly-status because the body's ## Red checks says none; that is main's red per the brief.
- Merge: git merge-tree --write-tree origin/main exits 0, no conflict, no claim file involved. Commit bodies carry no footer or trailer.
