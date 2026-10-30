Fix review: merge 882da1e01b3d209cf7f8b6c02427166e7c0c7655

bus-nonce: 9821f24cbb8e81bc751dc8392e011cc6

## Round

Round 3 (round 1 blocked on the X1-X7 findings, round 2 = verdict 298161016 blocked body-stale). Measured at 882da1e01b3d209cf7f8b6c02427166e7c0c7655, in a detached worktree at that SHA; the head was re-read from origin (branch and refs/pull/2978/head) after measuring and is unchanged (ev/head-recheck.txt). Roles diff `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty: the contract read is current.

## Findings

- `BRANCH-POLICY` same-verdict re-admission has no bound: a PR refused for a missing code-owner approval can be re-added and burn `merge_tries` refusals per re-add. The body names it and routes it to the group's open roster carry 2 (#2577 park-before-attempt); not built in this part. Carry: R10-TRAIN-OVERLAP-GRADE
- `review_packet.train_boarded` reads `queue.pending.json` without `QUEUE_LOCK` against a non-atomic `write_text`; pre-existing, and the reader's output is an advisory packet line. Carry: dismissed: pre-existing unlocked reader of an advisory line; a torn read drops boarded entries for one render only, not a defect of this diff
- No committed finder's harness is named (packet: "Finder's harness: none named"); the field instance (triage P291, train pid 34197 batch 20261029-193537-b4) is replayed by the committed self-test arm `P291 batch-4 replay`, which I ran, and the mutant harness is the fixer's own and is disclosed as such in the body. Carry: dismissed: the P291 field instance is pinned by a committed self-test arm in the tree; no out-of-tree instrument exists to land

## Evidence

- RESULT: `merge_train self-test: 355 checks, 0 failed`, rc 0 (ev/selftest.txt) -- matches the body's 355.
- RESULT: mutation harness, M0 PASS and M1-M19 all KILLED, none STALE or SURVIVED (ev/mutants.txt for M0-M15, ev/mutants-M16-M19.txt for M0 and M16-M19, exit 0). My first full run was cut at my own 230 s cap after M15 (exit=124 in ev/mutants.txt), so M16-M19 were re-run by name; together the body's `MUTANTS: 20 run, 0 not as required` is re-derived. The red arms I saw match the body's (e.g. M1 red on live queue / P291 batch-4 replay / P189 HOLDER arm / drained-entry arm; M3 red on P291 batch-4 replay).
- RESULT: my own mutants, outside the PR's set (ev/own-mutants.txt, script ev/own-mutants.py): R1 `already_held`'s merged/ran branch returns None -> KILLED (live queue, P291 replay, P189 null control); R2 `BRANCH_POLICY_SAID` never matches -> KILLED (P291 replay, merge-skip class arm); R3 the cure accepts any recorded state instead of `merged` -> KILLED (--skip-bad arms, skip class arm). R4 (ran admitted, merged held) did not complete inside my timeout and is unmeasured.
- RESULT: `STRUCTURE RATCHET PASSED` (ev/structure.txt); no `*_budgets.json` touched.
- RESULT: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` from `tests/closure.py select` on a clean tree (ev/clean-before-select.txt empty, ev/closure-select.txt); an earlier select of mine ran while mutant copies sat in the tree and is superseded. `ALL 2479 ENTITY CHECKS PASSED`, rc 0 (ev/entities.txt); its FAIL lines are the suite's own negative controls (sensor.x, sensor.not_ours).
- Class: the body's rule `git grep -n "QUEUE_PENDING\|QUEUE_SEEN\|already_held(\|queue_seen_read(" -- tools/ .github/ tests/` returns only tools/audit/seat/merge_train.py and tools/audit/seat/review_packet.py (ev/class-grep.txt, harness file excluded); both are dispositioned in the body. No class-open seam.
- Body figures re-derived: merge base 26c9d22a3c37a1b48f8561d061ae58b03eef5b54; `git diff --name-only 2b8468aea 882da1e01` lists only the four dev/programme files named; `git rev-list --count 882da1e0..origin/main` = 52 with origin/main at 1148ee635.
- Merge: `git merge-tree --write-tree origin/main 882da1e0` exit 0, tree c78facc3; `LEDGER-MERGE: resolved tests/closures.json` (inert_reads merged as a set). No MERGE-CLAIM marker: no claim file touched (ev/merge-tree.txt).
- VERSION, manifest, RELEASE_NOTES.md and tests/golden/ untouched in the three-dot diff (ev/version-untouched.txt empty); no claim-file change.
- CI on this head, read from the check-runs API (68 runs): every run completed; the only failure is `tests / nightly-status`. pr-contract run 123946377414 started 07:30:09Z, after the last red concluded (02:47Z), and is green: that is the body check. gate runs green; `tests / mutation` green.
- Red checks: `tests / nightly-status` is answered in the body as main's; it reads Actions metadata on nightly runs (.github/workflows/tests.yml nightly-status job), which this diff (merge_train.py, its instrument page, the harness, closures.json, the delivery row) does not reach, so it is not this PR's (defect-root-cause.md).
- Forward-carry: body says none; the round-1 items are each answered in `## Review round 1` and the roster carries 9, 13, 15, 20 closed with named arms and mutants, which I saw fail under their mutants.
