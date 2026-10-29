Fix review: merge 739af07abd7c2188da56c9c269691e0d394c3515

bus-nonce: 1e6358d67fdcc2e238eb070a6064dccf

First review of #2956 (R10-FRICTION-CLAIM-FALSE), head 739af07abd7c2188da56c9c269691e0d394c3515. The PR is a root-cause record plus one triage-contract sentence. It changes no production code and moves no budget.

## Findings

(none: the three body items are carried `dismissed:` with reasons, and `carry_audit` reports 3 routed, 0 unrouted, 0 bad destinations.)

## Evidence

- RESULT head: PR head and branch tip both read 739af07abd7c2188da56c9c269691e0d394c3515 (`ev/head-recheck.txt`). The measured tree is that head.
- RESULT step 1/3 (mutation, null control): n/a. No check, test or production line changes, and the sentence is an instruction, so no fail-then-pass demonstration is owed (`defect-root-cause.md`). The diff has six files, all under `dev/`.
- RESULT step 4 (claims): the diff touches no golden or claim file.
- RESULT step 5 (version): `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (`ev/checks.txt`).
- RESULT step 13 (merge): `git merge-tree --write-tree origin/main 739af07a...` returns rc=0, tree 42b96dad, no conflict. origin/main is 279578074, which is the PR base.
- RESULT step 14 (numbers earned): `policy_lint.mjs --budgets` prints `proposal-triage.md 36 36 489 489`. The file is 1956 bytes at the merge base and at the head, so the contract edit is paid inside its cap with no raise. CLAUDE.md reads `3605 3605`, untouched. `tests/structure.py` prints STRUCTURE RATCHET PASSED. `fold_ledger.py check` prints 130 rca entries, 0 violations. `bugclasses.json` parses.
- RESULT figures re-derived at this head: `items.tsv` gives F5 T5 V2 O2 R2 C1 B1 = 18 items, and 12 without #2883 (T5 V2 O2 R2 C1), as the body states. The 8 block-to-verdict gaps sum to 1492 min with median 221 min, and the R/C rounds 62+51+174 sum to 287 min. `roster_edit.py` has the two `def`s at 455 and 466, not 456 and 464. `git log --all -S conflicting_claims_message -- tests/env_drift.py` returns 0 commits, and `merge_claim_refusal` is at 1844. `tools/ci/gate.py:224` reads `f"FAIL {why[0]}"` and `:295` reads `"\n".join([outcome] + why[1:])`. P219 holds: 0 of 52 headings in batches 45-59 carry a V-id, against 13 in batches 35-43, which is the control. The packet's `figure_lint` reports 7 resolved, 0 not verified.
- Not re-derived: the 4 PRs / 8 entries count (`policy_lint --stats`, 2 min of GitHub API) is taken from the committed `stats_v7.0.5.txt` and the PR's comment timestamps. The #2900 job log is not re-read here (the record says so itself, section 6).
- RESULT root cause (`root-cause.md`): the record names a cause (a ruling's rule never run on its own instance, and a `Cost:` that reads no cap), a process state ((a) for R/C, (b) for T, (d) for V, already countermeasured by P219) and a cost test with numbers that re-derive at the merge base. The landed countermeasure is an instruction, not a check. The refused lint for typed citations is recorded with its numbers (at most 1 round saved in the window).
- RESULT step 10 (forward-carry): the sentence lands in the contract the triage seat opens, and no other stage's brief is owed a change.
- Class rule (step 6): a root-cause record with no code change, so there is no seam class to enumerate.
- Red checks at this head (check-runs, all pages, 40 runs): `tests / nightly-status` is the only failure. The body answers it: it grades main's Nightly and this diff reaches nothing it reads, so it owes no answer here. Every other completed run is success or skipped.
- CI state: when read, `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `governance / instrument-self-tests` and `prelude` were still in_progress, and no `pr-contract` run had started. This verdict rests on my own checks above. The merge train must still see those runs conclude green before it merges, and I have not seen them conclude.
- Round: first review of this PR.
