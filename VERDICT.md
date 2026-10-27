Fix review: blocked adf5ef473a74e4c25f654f01c4201244b771c147 claim-false: the four headings cite V132-V135, not the ruled V125-V128 (V133-V135 resolve nowhere, V132 is a different proposal); the body cites ruling_verdict at 456 and triage_refusal at 464, which are 455 and 466
bus-nonce: 129cf07d6d76b4c7861aca787823feb5

Round 2, re-cut after `Fix review: blocked 54ac455ab... claim-false`. Measured at head `adf5ef473a74e4c25f654f01c4201244b771c147` from a detached worktree at that head; live state re-read immediately before writing is `OPEN`, `mergeStateStatus BLOCKED`, head unchanged (`evidence/head.txt`). `git diff --name-status $(git merge-base origin/main HEAD)...HEAD` is exactly two added paths, and no production line is written, so no mutant is drawn and the gate and mutation table were not re-run. `git merge-tree --write-tree origin/main HEAD` exits 0.

## The four prior findings: all answered

- **B1 answered.** `conflicting_claims_message` is gone from the record. It now names `merge_claim_refusal`, which is at `tests/env_drift.py:1844`, and its CONFLICTING CLAIMS text is verbatim at 1851-1857. `git grep conflicting_claims_message` matches only the triage file's own self-correction, and `git log --all -S conflicting_claims_message -- tests/env_drift.py` is empty, so the self-correction's statement re-derives (`evidence/prior-findings.txt`).
  Carry: R10-996-RUNNER-CLAIMS
- **B2 answered.** The 45-minute figure is retracted as one no window holds, and every replacement re-derives. `git log --format=%cI origin/handoff/audit-r10-roster` gives `5ffe924ae` 18:31:07Z to `9aed78e0e` 20:23:46Z, 1 h 52 m 39 s over 12 commits (6.39/h); the three tips `32b938f3e` 18:32:41Z to `d61e2834c` 20:17:47Z, 1 h 45 m 06 s; the ledger reads 18:34:13Z to 20:18:55Z, 1 h 44 m 42 s (`evidence/churn.txt`). The ledger read times are not in a file I can read; see C1.
  Carry: dismissed: no implementing group (P212 is REJECT); the figure is corrected in place
- **B3 answered.** `R10-996-RUNNER-CLAIMS` owns `tests/env_drift.py` and `tests/golden/claimed_drift.txt` and nothing else; `tools/pr/merge_main_bot.py` and `tools/pr/head_note.py` have no owner across all 212 groups, over `files` and `hot_files`. P214 now names the `edit-brief` that takes `merge_main_bot.py` into the group's `files`, and P213 states its exclusion as unmeasured benefit plus an unowned file, so the batch answers ownership one way: it pays the brief where the benefit is measured and does not where it is not (`evidence/roster.txt`).
  Carry: R10-996-RUNNER-CLAIMS
- **B4 answered.** `append-group` moved to the direct-callable set, and `nudge.md:105` runs it directly and is unchanged. The structural set is `wire-issue`, `unwire-issue`, `edit-brief`, `append-carry`, `set-after`, `drop-carry`; `roster_edit.py:703-705` lists all nine ops, and the instance's op, `wire-issue`, is inside the guarded set. `set-resume` appears in no role or template (`evidence/prior-findings.txt`).
  Carry: R10-ROSTER-OPS

## Block

- **N1: all four headings cite a proposal id that resolves nowhere or to a different proposal.** `dev/programme/triage/s6-batch41.md:16` `(V132)`, `:54` `(V133)`, `:97` `(V134)`, `:145` `(V135)`, each beside a `Source:` line naming `proposals.md` V125, V126, V127, V128. Measured in `~/hpo-orch/r10s6/proposals.md`: `grep -c '^## V133 '` = 0, `'^## V134 '` = 0, `'^## V135 '` = 0; `'^## V132 '` = 1, but that entry is "triage rulings cite a V-number seven above their source" (line 731), not P212's subject. The three correct ids do resolve: `## V125`..`## V128` carry exactly P212-P215's titles, and both this PR's delivery row (`dev/programme/delivery/2890.md`) and the PR body say V125-V128. The headings are `Source + 7` — a P minus 80 counter where the ledger is P minus 87 (212-132=80, 212-125=87) — and batch40, already merged in origin/main, has the same shape: heading `(V131)`, Source V124, and `body-b40-correct.md` uses V124. A raw `grep -c V135` is now 2, not 0, because V132's own text quotes the string at proposals.md:741-742, which is why the resolvability test is the heading, not the bare string. Smallest change: `(V132)`->`(V125)`, `(V133)`->`(V126)`, `(V134)`->`(V127)`, `(V135)`->`(V128)` (`evidence/headings.txt`).
  Carry: dismissed: the ruling text itself is the defect; no group owns a wrong citation
- **N2: the body cites two def lines that are not where it says.** PR 2890, `## Mutation proof` (body line 23), writes "`ruling_verdict` at 456, `triage_refusal` at 464". `grep -n 'def ruling_verdict\|def triage_refusal' tools/audit/seat/roster_edit.py` gives 455 and 466 at the head, at the authored head `adf011c8f`, and at the base `ea36188c`; line 464 is a blank line, not inside `triage_refusal`. Smallest change: 456 to 455, 464 to 466 (`evidence/headings.txt`).
  Carry: dismissed: body text; correct in place
- **N3: "`nudge.md` steps 12 and 18 require set-stage" is false for step 18.** `nudge.md:89`, step 12, runs `roster_edit.py set-stage`. Step 18 (`nudge.md:111-115`, the file's last section) contains no `set-stage` and no `roster_edit`, and `state_docs.py`, which step 18 does name, has no `set-stage`. The claim is inherited from `sweep_template.md:63`'s own parenthetical, so cite that or cite step 12 alone; the narrowing still holds on step 12 and `nudge.md:105`. Re-cut lines 164 and 186 (`evidence/headings.txt`).
  Carry: dismissed: the justification stands on step 12; drop "and 18"

## Verified

- **V1: the gate reads this file as the carries will cite it.** Re-ran the reader the body names, `roster_edit.ruling_verdict`: P212 REJECT, P213 ACCEPT, P214 ACCEPT, P215 ACCEPT, matching the body's own output (`evidence/citations.txt`). The reader is the seat's, not the author's; this is the only instrument I built.
- **V2: every code citation resolves.** `merge_main_bot.py:139` is `"skip-driver-refused " + ",".join(driver_conflicts or text_conflicts)`; `review_packet.py:289` is the head-note refusal and `:411` its self-test arm; `roster_edit.py:703-705` lists the nine ops; `roster_queue.py:94-102` builds the child `env`; `head_note.py` holds `head_offset` (20) and `prefix` (39); `bus.sh:479` writes the dispatch record and `:313` matches on pr, head and nonce; `update_pr.sh`'s usage is `updatepr.sh <branch> <code-sha|-> <body-file>` (`evidence/citations.txt`).
- **V3: the three destinations exist, own what the rulings say, and are at the stated stages.** At `origin/handoff/audit-r10-roster` `9aed78e0e`, 212 groups: `R10-ORCH-REVIEW-PACKET` done, 10 carries; `R10-996-RUNNER-CLAIMS` carries-open, 2; `R10-ROSTER-OPS` done, 6 (`evidence/roster.txt`).
- **V4: record discipline holds.** The diff is two added paths; no `VERSION`, `RELEASE_NOTES.md` or manifest version moves; the new delivery row is under `dev/programme/`, which `closure.py` keeps INERT; `python3 tools/audit/carry_audit.py pr 2890` is `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` (`evidence/carry-audit.txt`, `evidence/head.txt`).
- **V5: no concluded red owes an answer.** The head's check runs are green or skipped, or still queued or in progress (`env-matrix`, `instrument-self-tests`, `fast (3.14)`, `arch-instrument`, `browser`, `closures`, `coverage`, `typing`); no failure exists to answer. `tests / mutation` is completed success, but this diff writes no production line, so it draws no mutant (`evidence/checks.txt`).
- **V6: the head is the one the body names.** The live `## Head` is `adf5ef473a74e4c25f654f01c4201244b771c147`, the head measured.

## Could not establish

- **C1: the ledger's three read timestamps** (18:34:13Z, 19:47:47Z, 20:18:55Z). Their arithmetic re-derives to 1 h 44 m 42 s, but no accessible file carries those reads. It is corroborating only; B2's load-bearing window re-derives from the ref itself.
  Carry: dismissed: B2 re-derives from the ref; the reads are corroboration
- **C2: the exact head-note refusal text behind P213's #2883/#2889 instance.** Both pull requests are real and OPEN, but the refusal is a dispatch-time event I cannot re-observe from the tree; the instance is consistent with `review_packet.py:289`, not independently reproduced.
  Carry: dismissed: consistent with the code, not re-observable

The REJECT of P212 stands on its in-head argument, and the three ACCEPTs are correctly routed to groups that own the files. The block is only on the record's citations.
