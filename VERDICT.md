Fix review: blocked 06a3478fdbf386278952d741985e5da5ee28bd5c ci-red: gate

bus-nonce: b659fae0ba18fa95cac6f4ee6dd5190e

Round: first review of this head (no earlier verdict seen by this seat).

## Block
merge_train.py classify at 06a3478fdbf386278952d741985e5da5ee28bd5c exits 1: `RED 06a3478fdbf386278952d741985e5da5ee28bd5c pending: none red: gate`, re-run twice, 60 s apart. Cause: classify keeps the worst gate per check suite (A5). Gate runs failed in three older suites at this same head (128975188431 in run 42553904519, 128956599985 in run 42554006009, 128956031126 in run 42553904840). The log of 128975188431 reads `FAIL pr-contract / pr-contract: failure (this run)`, which is the pr-contract failure that the body's Red checks section now answers. The newest suite (run 42567567162) is green: gate 128998167411, pr-contract 128997891670, budget-raise-gate and arch-score success. The code is not at fault. The head cannot go GREEN for the train unless a fresh CI run supersedes those suites. I did not get a green classify, so this is a RED, not a merge. Re-dispatch at a new head whose runs are all green, for example after a no-op main merge. If the orchestrator judges the stale suites superseded, `review_carry.py` should print CARRY for that head, and the code review below carries to it.

## Findings
- Follow-up: the class-open half of the new rule (fix-review.md step 6, every seam in one block) has no mechanical check, only the mutation-vacuous half is enforced by survivor_list.py. The body discloses this as the brief asked. Carry: dismissed: disclosed in the body and what the owner ruling asked for.

## Evidence
- Head reviewed: 06a3478fdbf386278952d741985e5da5ee28bd5c (ev/HEAD.txt). It is the API head and the `refs/pull/3341/head` tip. The body's `## Head` names it.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 06a3478fdbf386278952d741985e5da5ee28bd5c` rc 0 (only `LEDGER-MERGE: resolved tests/closures.json`).
- RESULT survivor_list self-test: 20 checks, 0 failed at the head.
- RESULT mutation proof, re-run by me with the self-test as the command. Seven mutants of survivor_list.py were each killed: triaged-subtraction dropped, LIVES regex dropped, left token boundary dropped, class guard forced off, NULL exclusion dropped, spec-mode regex dropped, survivor_sites call dropped. The null control was the unmutated file, 0 failed. Production file restored (git status clean).
- RESULT bus.sh mutant: deleting the survivor_list.py call from push_verdict makes the bus self-test arm "push-verdict refuses a mutation-vacuous verdict naming one of two survivors, and review/7 does not move" FAIL. The arm "proposes it once it lists both" stays ok. The file was restored.
- RESULT end-to-end: check on a verdict naming a.py:1 against evidence with a.py:1 and b.py:2 prints `UNLISTED b.py:2` and exits 1.
- RESULT structure: `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED; no budget raised (body says so).
- VERSION, manifest and RELEASE_NOTES are untouched by the three-dot diff (8 files, none of them those).
- Claim files and goldens untouched (no env_drift movement possible: the diff has no production or fixture change).
- The finder's harness is none named. The instrument is the fixer's own, disclosed as such by the body.
- Packet carry_audit at head: 0 findings. Forward-carry and Friction in the body are "none". A role-contract change binds the reviewer seat and is in the tree.
- governance / delivery-status red (128955414223): grades main (OVERDUE #3318). The diff touches neither its scripts nor any row but its own new one, and the body names and answers it.
- Sibling merge-tree: the body reports dispatch-at-handoff-p2 conflicts on fix-review.md with this diff; I did not re-derive it. The second to land merges main.
- Not re-derived: the body's closure.py `select --files` MODE: FULL versus `--diff` SCOPED -- 3 figure (the body itself withdraws a cause). I ran no gate or mutation table (CI's heavy runs cited).
