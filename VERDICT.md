Fix review: blocked 54ac455ab7e34dc6842bbddba672619e797dfed7 claim-false: env_drift.py has no `conflicting_claims_message`, the 45-minute churn figure does not re-derive, P214's destination does not own the file its fix is in, and P215 guards an op the written procedure runs directly
bus-nonce: 54baac714084ec48f2abfe668bc8e506

Round 1. Measured at head `54ac455ab7e34dc6842bbddba672619e797dfed7` from a detached worktree at that head; re-read live immediately before writing: `OPEN` at that head, `mergeStateStatus BLOCKED` (`evidence/head.txt`). `git diff --name-status a0e7664ea...HEAD` is exactly two added paths, `dev/programme/delivery/2890.md` and `dev/programme/triage/s6-batch41.md`; no production line is written, so no mutant is drawn and the full `prepr.sh`, the gate and the mutation table were not run, per the cost discipline. The three ACCEPT destinations exist at the pinned roster ref; the four rulings are readable by the gate they feed. The block is on three facts in the record and one inconsistency between two of its rulings.

## Block

- **B1: the record and the body name a function that does not exist.** `dev/programme/triage/s6-batch41.md:100` writes "`tests/env_drift.py`'s `conflicting_claims_message` (around 1845-1857)", and the body repeats it at the P214 paragraph and in `## Figures`. `git grep conflicting_claims_message HEAD` matches only the triage file itself, and `git log --all -S conflicting_claims_message -- tests/env_drift.py` is empty: the name never existed. The function at 1844-1857 is `merge_claim_refusal`, and its message is the verbatim text the ruling quotes; the quote is right, the identifier is invented. The reader this file exists for is `R10-996-RUNNER-CLAIMS`, which owns `tests/env_drift.py` and will search for the name. `figure_lint.mjs` passes it because it resolves paths, not symbols (`evidence/symbols.txt`).
  Carry: R10-996-RUNNER-CLAIMS

- **B2: the roster-churn figure does not re-derive.** The record (lines 29-31) and the body say the ref "moved `32b938f3e` → `8f7e252fe` → `d61e2834c` inside 45 minutes", timed "(19:0xZ)", "(20:0xZ)", "(20:3xZ)". `git log origin/handoff/audit-r10-roster` gives the three tips at `18:32:41Z`, `19:35:59Z` and `20:17:47Z` — a 1 h 45 m span; the seat's own reads in `seat-ledger.md` are `18:34:13Z`, `19:47:47Z` and `20:18:55Z` — a 1 h 44 m span. No 45-minute window holds all three, and none of the three times matches either the commit time or the read time. The conclusion is if anything understated: the ref took 10 commits between `18:32:41Z` and `20:23:46Z`, about 5.4 an hour, so "several times an hour" is supported and the REJECT stands on its in-head argument; the interval and the three clock times are false as written. `evidence/churn.txt`.
  Carry: dismissed: no implementing group (P212 is REJECT); correct the figure and times in the record

- **B3: P214 carries a change into a group that does not own the file the change is in, and P213 refuses exactly that shape.** The carried fix is `tools/pr/merge_main_bot.py:138-139`: `decide()` returns `"skip-driver-refused " + ",".join(driver_conflicts or text_conflicts)`, and `driver_err` is already a parameter, so carrying the driver's message is a bot edit. Across all 212 groups at `d61e2834c`, `files`/`hot_files` give `tools/pr/merge_main_bot.py` **NO OWNER**, and the destination `R10-996-RUNNER-CLAIMS` owns only `tests/env_drift.py` and `tests/golden/claimed_drift.txt`. P213 (lines 67-70) refuses the `head_note.py` rewrite because it and `merge_main_bot.py` are unowned — so one batch answers the same ownership question two ways. Either the destination takes `merge_main_bot.py` into its `files` (an `edit-brief` op the ruling does not name), or P214's destination is wrong. As written the fixer edits an unowned file outside its group's declared set with no disposition (`evidence/roster.txt`, `evidence/citations.txt`).
  Carry: R10-996-RUNNER-CLAIMS

- **B4: P215's narrow guards `append-group`, which the tree's own written procedure runs directly — the fault it cites for exempting `set-stage`.** `dev/governance/roles/nudge.md:105`: "Register a fly-in at dispatch with `tools/audit/seat/roster_edit.py` append-group". The ruling's justification (lines 136-141) checks only `set-stage`, and names `set-resume`, which neither a role nor the sweep template mentions (`grep set-resume dev/governance/roles/ tools/audit/seat/sweep_template.md` is empty). A guard on `append-group` refuses nudge.md:105 unless `append-group` moves to the direct-callable set, or nudge.md:105 is changed in the same group (policy, owner approval). Neither is carried, so the narrow as drawn still "refuses the tree's own written procedure — the next slip, built by the fix" (`evidence/citations.txt`).
  Carry: R10-ROSTER-OPS

## Verified

- **V1: the triage gate reads this file as the carry it will be.** Re-ran the proof with the seat's own reader (`roster_edit.triage_refusal`/`ruling_verdict`, `evidence/mutation_proof.py`, `evidence/mutation_proof.out`): the ACCEPT entries at P213/P214/P215 resolve; a citation to P212 is refused as `REJECT`; changing the `## P213:` heading refuses it as `no such entry`; changing P213's verdict to `DEFER` refuses it as `DEFER`. The null control refuses both `triage P213` and `proposal P215` text with no citation. The harness is mine, built from the tool the ruling names, not the author's. This is the only instrument I built.
  Carry: dismissed: instrument is the seat's own gate, run at the head

- **V2: the three destinations exist and mean what the rulings say, at the pinned ref.** At `origin/handoff/audit-r10-roster` `d61e2834c`, 212 groups: `R10-ORCH-REVIEW-PACKET` `done` with `review_packet.py` in `files`; `R10-996-RUNNER-CLAIMS` `carries-open` with `tests/env_drift.py` and `tests/golden/claimed_drift.txt`; `R10-ROSTER-OPS` `done` with `roster_edit.py` and `r10_roster_ops_mutants.py`; `R10-RCA-FRICTION-RESIDUE` `fixes` `[2410, 2593]` exactly as the ruling states. `2597`/`2660`/`2784` are queued to `roster-queue-s7.txt` (now `#done`). No group owns `tools/pr/head_note.py` or `tools/pr/merge_main_bot.py`, which is what P213's not-carried arm claims (`evidence/roster.txt`).
  Carry: dismissed: destination arms verified at d61e2834c

- **V3: the line and symbol citations that do resolve, resolve as claimed.** `review_packet.py:289` is the `head-note` refusal string and `:411` its self-test arm; `bus.sh:479` writes `<pr> <head> <reviewer> <nonce> <date> <model>` and `dispatched_to` (line 313) matches on `pr`, `head` and the nonce; `update_pr.sh`'s usage block is `updatepr.sh <branch> <code-sha|-> <body-file>`; `head_note.py` holds `head_offset` (20) and `prefix` (39); `roster_edit.py:703-705` lists the nine ops; `roster_queue.py:94-102` builds the child `env`; `sweep_template.md:63` (and so nudge steps 12/18) runs `set-stage`; `merge_main_bot.py:139` and the `env_drift` message text are as quoted (`evidence/citations.txt`).
  Carry: dismissed: citations re-derived at this head

- **V4: the #2886 instance is as stated.** #2886 merged at `20:41:20+01:00` = `19:41Z`; the bus dispatch record for round 2 is `0f779c2dc` at `19:12:20Z` and the posted verdict merges `0f779c2dc`; `#2888`'s verdict merges `b00a5d3ef` and the correction commit `1a6365f16` is inside the reviewed head. The ruled file's blob did not change between round-2 dispatch and merge, so a digest of it would be equal and the instance is outside the candidate's reach, as the ruling argues. #2872 is `DIRTY` at `fe964895e`; #2889's head is `88b452c6a`.
  Carry: dismissed: instance re-observed at the head

- **V5: record discipline holds.** The diff is two added paths only — the triage file and `dev/programme/delivery/2890.md`, a one-line `**open**` row; no budget file, neither claim file, no `VERSION`/`RELEASE_NOTES.md`; `git merge-tree --write-tree origin/main HEAD` exits 0; `carry_audit.py check` on the body is 0 unrouted; `figure_lint` is 5 resolved (`evidence/diff.txt`, `evidence/merge-tree.txt`).
  Carry: dismissed: record arms clean at this head

- **V6: no red check owes an answer.** The head's check runs are all completed green/skipped, with `instrument-self-tests`, `closures`, `coverage` and `fast (3.14)` still in progress; no failure exists to answer, and none is cited as green (`evidence/checks.txt`).
  Carry: dismissed: no concluded red at the head

## Could not establish

- **C1:** the exact text of the two `head-note` refusals the P213 instance rests on. Both PRs are real and OPEN (`#2883` head `d218ef37`, `#2889` head `88b452c6a`), but the refusal is a dispatch-time event I cannot re-observe from the tree; the instance is consistent with `review_packet.py:289`, not independently reproduced.
  Carry: dismissed: instance consistent, refusal not re-observable

- **C2:** a 45-minute window holding the three named roster tips or the three ledger reads. I searched the commit times and every ledger line naming the three SHAs and found none; the ledger's read times are given in B2.
  Carry: dismissed: searched and not found; reported in B2
