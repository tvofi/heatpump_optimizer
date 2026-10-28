Fix review: merge 569849cf18f65ef58a45e85036d4e0544d79f1bc

bus-nonce: a416e91192b032739e4dc6e5fca60559

Round 2 is a delta review. I reviewed from a detached worktree at 569849cf18f65ef58a45e85036d4e0544d79f1bc and re-read the head with `git ls-remote origin refs/pull/2846/head` just before writing. It had not moved (ev/ls-remote.txt). The delta 7b271b551..head touches only `dev/programme/triage/s6-batch32.md`, 9 lines added and 11 removed, and all of them are in P189 (ev/delta.diff). The other seven rulings are unchanged since round 1, and I do not re-rule them.

## Findings

- P189's carry replaces two parts of carry 9: the skipped-PR admission sentence and the null control. It leaves carry 9's predicate sentence as it is: "a PR is ALREADY when it is still to run in this train or spooled, when this train merged it, or when it entered this train at the same verdict head". Read word for word, that clause still refuses a HOLDER-skipped PR re-added at the same verdict head, and the amended admission sentence admits that PR. The carry places its addition "after P129's predicate sentence", so it reads naturally as an exception to the rule. That is why I do not block. But the fixer has to build the HOLDER exception into the one shared predicate that `train_add` and `queue_take` both call, not into a second check that only one of them calls. If it lands in only one place, the two sides will disagree again, which is the V50 defect itself. The fixer should treat the predicate's same-verdict-head clause as "unless that entry's skip class was HOLDER". Carry: R10-TRAIN-OVERLAP-GRADE
- The delivery row `dev/programme/delivery/2846.md` reads "triage: batch 32, P191 (V111 record PR swept on a refused merge attempt)", and so does the PR title. Batch 28-31 rows give the range: "triage: batch 31, P176-P183 (V94-V103 quality series)". This row should read "triage: batch 32, P184-P191 (V104-V111)". It is record text, not a block. Carry: dismissed: record text the orchestrator rewrites when it updates the row at merge (delivery-status-tracking.md); it hands nothing to a later stage

## Evidence

- Check 1, the round-1 block item. Each change round 1 asked for is done:
  - The verdict line now reads "ACCEPT narrowed, amending P129 (carry 9 of R10-TRAIN-OVERLAP-GRADE, `s6-batch26.md#P129`)".
  - Arm (a), `Train.skip` taking the PR out of `QUEUE_PENDING`, is kept.
  - Arm (b), the HOLDER same-verdict exception, is written as a replacement for carry 9's null control. The carry quotes "add at the same head is ALREADY on both sides" and replaces it with "... after a skip of any class but HOLDER ...".
  - The s40 #2753 instance is marked "Already counted by P129's carry ... Not counted here".
  - The log words are reconciled: "The log words stay carry 9's (ADDED and ALREADY, the same on both sides)". The `SKIPPED` word is gone.
  - The carry text names what it replaces: "replaces two parts of that carry and adds one sentence". It quotes both replaced passages verbatim. Both quotes match the live carry 9 at origin/main d181d014a (ev/carry9-origin-main.txt; the group has 11 carries, and carry 9 is P129's text, `triage: dev/programme/triage/s6-batch26.md#P129`) and P129 in s6-batch26.md (ev/P129-s6-batch26.txt).
- Check 2, two specs for one predicate. The remaining overlap is the predicate sentence, under Findings. Every other rule now has one spec. The log words are the same, the verdict-head key is the same (P189 adds the skip class beside the head in P129's `seen` map), and the drain cause (b) is left to P129 ("is P129's and is not re-ruled").
  - I re-derived the "two new to P129" split from the code at origin/main (ev/merge_train-citations.txt). `train_add` writes `ALREADY #N: queued in the live train (pid ...)` (merge_train.py:809), and `queue_take` writes `ALREADY #N: in this train already; not queued twice` (:2368).
  - So the s41 and s42 lines P189 quotes come from the pending layer, which P129 does not address. The s40 line comes from the `seen` layer, which P129 counted. That gives 2 new instances and 1 already counted, as P189 states.
  - I could not re-derive the line numbers in the train logs (s40:143/326, s41:74/103, s42:12/93). They are in the orchestrator's state directory, not the tree.
  - Other citations re-read at origin/main: `Train.skip` 2286-2296 (no removal from pending), `_queue_pending` 2352, `train_add` pending check 805-810, `queue_take` `seen` test 2366-2370, and `seen` seeded at 2317.
- Check 3, figures. The file has 6 ACCEPT, 1 DEFER and 1 REJECT verdicts and 8 `Instances:` lines. These match the body's ## Figures (ev/verdict-counts.txt).
  - `roster_edit.ruling_verdict` reads P184, P185, P187, P189, P190 and P191 as ACCEPT, P186 as REJECT and P188 as DEFER. It returns None for P192, the null control.
  - P189's new verdict line, which has no `->`, still parses as ACCEPT, and `triage_refusal` accepts a carry citing `s6-batch32.md#P189` (ev/ruling_verdict.txt).
  - `python3 -I tools/audit/carry_audit.py pr 2846` printed `CARRY-AUDIT #2846: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit.txt). That matches the orchestrator's 6 of 6.
  - The body's ## Red checks now says "This diff adds one row, its own `dev/programme/delivery/2846.md`". The round-1 stale sentence is gone.
- Check 4, scope and merge.
  - The three-dot diff against origin/main touches only `dev/programme/triage/s6-batch32.md` (+116) and `dev/programme/delivery/2846.md` (+1) (ev/threedot.txt).
  - A grep of both files for `/Users/`, `/home/`, `~/`, `.local` and `.lan` found nothing.
  - `git merge-tree --write-tree origin/main 569849cf18f65ef58a45e85036d4e0544d79f1bc` exits 0 with no conflict (ev/merge-tree.txt).
  - `VERSION`, the manifest and the notes are untouched.
- CI at 569849cf18f65ef58a45e85036d4e0544d79f1bc, read from the check-runs API (37 runs). No run has concluded red.
  - Green: delivery-status, nightly-status, policy-docs, briefs, mutation (no production line, so no mutant is drawn), arch-score, budget-raise-gate, closure-scope, typing, arch-instrument, wave-script, codeql and hassfest.
  - Skipped: `governance / record`, which the body answers as main's own, plus replay, nightly-ha, mutation-pins, mutation-autofix and kernel-points.
  - Still in progress when I read them: tests / fast (3.14), browser, closures and coverage; governance / env-matrix and instrument-self-tests; and one prelude. None has red to answer yet, and none reads anything this diff changes beyond two INERT record files.
- Mutation proof and finder's harness: n/a. This is a ruling record with no code, as the body says. The consumer check is `ruling_verdict`, which I re-ran above.
- Rulings I would change: none. P189 as re-cut is sound, subject to the predicate finding above, which goes to the same group's fixer.
