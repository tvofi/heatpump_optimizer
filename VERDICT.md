Fix review: blocked 204ffce804bbf0f602ad258b42c6fea0c9ddbf15 released-early: P133's carries-open rule plus P137's set-stage releases R10-FLOW-BODY-ONLY, R10-FLOW-ROSTER-FREEZE, R10-FLY-ORPHANS-REWRITTEN and R10-FLY-OPENPR-ATOMIC from R10-UPDATE-PR-SIGNALS, whose owed carries edit the same update_pr.sh, pr_args.sh and cloud_relay.sh those edges exist to sequence

bus-nonce: 3ac21dce537c5c1da2d95df4bb916978

## Round

Round 1 for this reviewer seat on #2822. Reviewed at head 204ffce804bbf0f602ad258b42c6fea0c9ddbf15, merge base da12aa37dee15b9e9567bd6c848493436f2592dd (origin/main at read time). The roles diff from the merge base to origin/main is empty, so the contracts I read are current. Roster read at aa679f28b (the ruling's ref) and at the roster tip 558125209.

## Block

P133 releases dependents that still need the carries it treats as unrelated.

- P133's Binding rests on one premise: "a merged group's leftover carries holding unrelated work is a schedule defect". Its Instances list only the dependents of the five carries-open groups at aa679f28b.
- P137, in the same file, moves R10-UPDATE-PR-SIGNALS to carries-open. Its Verdict says: "P133 then releases its dependents except the round-closing ones." The orchestrator has already made that move on the roster (d87475fe1, `set-stage R10-UPDATE-PR-SIGNALS`, stage `carries-open`, commit `fd9914851`).
- That makes a sixth carries-open group. It has four not-started dependents that are not round-closing, and P133's enumeration never considers them (ev/roster.txt):
  - R10-FLOW-BODY-ONLY shares `update_pr.sh`, `pr_args.sh`, `cloud_relay.sh` and `INSTRUMENTS.md`.
  - R10-FLOW-ROSTER-FREEZE shares `cloud_relay.sh`. Its own roster text gives the reason for the edge: "R10-UPDATE-PR-SIGNALS (in-progress) also edits cloud_relay.sh; add it as an after-edge for ROSTER-FREEZE".
  - R10-FLY-ORPHANS-REWRITTEN shares `cloud_relay.sh`.
  - R10-FLY-OPENPR-ATOMIC's carry reads "Rebase on R10-UPDATE-PR-SIGNALS (also edits pr_args.sh)".
- The carries R10-UPDATE-PR-SIGNALS still owes are in exactly those files:
  - carry 0, the SIGKILL drain of `update_pr.sh`'s lock;
  - carry 1, self-test isolation and lock ownership;
  - carry 2, `update_pr.sh`'s worktree on exit;
  - carry 4, the process-group residual in `cloud_relay.sh` and `update_pr.sh`.
  #2524's own Forward-carry keeps the SIGKILL clause and the isolation owed, and #2502 is still open.
- So for this group the leftover carries are not unrelated work. They are the work these edges sequence. Once ROSTER-SCHEMA lands the `blocks()` predicate as carried, four groups start editing the seam the owed follow-on edits, which is the conflict the edges were added to prevent. The brief asks me to check that P133 releases no group early. These four are released early.
- The defect is in the ruling text: the P133 carry has no exception for this case, and P137 relies on the release.

What would settle it is a revision of P133 and P137 in this file. Two shapes would work:
1. Narrow `blocks()`. A carries-open group still blocks a dependent whose `files` intersect its own while it has carries left. The `closes_round` exception stays. Add a control: a dependent that shares a file with a carries-open group stays blocked (null: one with no shared file is released).
2. Or have P137 name those four dependents and keep them blocked by an explicit edge.

Either way, P133's Instances must enumerate the dependents at the roster the rule will run on, R10-UPDATE-PR-SIGNALS included.

No other ruling blocks.

## Findings

- P139's operational premise was overtaken before the head was cut. It says "No `design-verdict/R10-HEAT-METER` ref exists". But `fabd19b8a`, "design-verdict R10-HEAT-METER: revise 04de6ae7f (round 1)", is dated 17:40:56+01:00, one minute before 840fab86f (17:41:57+01:00). `636a85b36` (revise e23ace899, round 2) followed. The carry's "First use" cites `design/R10-HEAT-METER at 04de6ae7f`, a note that has been revised. When the carry is appended, `set-size` should cite the head that `Design review: approve` names. The revised note e23ace899 still reads "Size verdict: L, conditional on #2753" (line 33). Carry: R10-ORCH-ROSTER-SCHEMA
- P136's carry tells R10-ORCH-LEDGER to edit `ledger.py` `review_owed`. That group's roster `files` are `cloud_relay.sh` and `orchestrator_tick.py`, and no group lists `ledger.py`, although #2671 created it ("ledger.py is the one module"). Add `ledger.py` to R10-ORCH-LEDGER's files when the carry lands, or the scope gate may refuse the edit. R10-ORCH-DISPATCH-REG's carry 4 can also move REVIEW OWED's dispatch arm "in the same PR", and P133 has removed its edge on ORCH-LEDGER. The two groups now edit the same function with no ordering between them. Carry: R10-ORCH-LEDGER
- The carries for P131(a) and P133 to R10-ORCH-ROSTER-SCHEMA edit `tools/plan/replan.py`, `orchestrator_tick.py`, `plan_page.py`, `plan_table.py` and `handover_prompt.py`. That group's `files` are `roster_lib.py`, `roster_sync.py` and `roster_edit.py`. P133 names the hot-file overlap, but neither ruling widens the files list. Widen it when the carries are appended. Carry: R10-ORCH-ROSTER-SCHEMA
- P130's Cost says "two `set-after` ops, one `edit-brief` and one carry", and arm C says "plus the brief edit in the carry text below". The file gives only `append-carry` text and no `edit-brief` text. In the meantime the roster has already dropped CLOSEOUT's edges on ARCH-DOCS and PLAYBOOK (3b5942aac). Until the P130 carry is appended, nothing on the roster says that `--apply` must run last. Append the carry together with the edge change, as one step. Carry: R10-CLOSEOUT-CLEANUP
- P137 says "Set R10-UPDATE-PR-SIGNALS to carries-open with pr 2524". The roster at 558125209 has `resume.pr` null (commit `fd9914851`). The tick and ledger rules key on the PR, so the record should carry 2524. Carry: R10-ORCH-ROSTER-SCHEMA
- Several line citations are off by one. LIVE_STAGES is read at `replan.py:322`, not 319-321, and the P131 carry repeats the error. The ALREADY test in `train_add` is at `merge_train.py:808-810`, not 806-809. The symbols are named, so a fixer finds them. Carry: dismissed: symbol names resolve each citation; line numbers drift with main anyway
- P127's ACCEPT names a policy edit opened by the orchestrator (#2821), not a roster group or a new group as `proposal-triage.md` asks. The ruling says why: no open group owns that contract, and a group for one word costs more than the edit. #2821 is open. Carry: dismissed: the destination is named (#2821) and the contract's group form would add a brief, a fixer and a review for one word
- The PR title is a merge-commit subject. The delivery row repeats it: "Merge remote-tracking branch 'origin/main' into triage/s6-batch26". Carry: dismissed: the orchestrator sets the title at merge; no ruling change follows

## Evidence

- ev/HEAD.txt holds the head reviewed, 204ffce804bbf0f602ad258b42c6fea0c9ddbf15.
- ev/head_and_merge.txt:
  - `git merge-tree --write-tree origin/main 204ffce804bbf0f602ad258b42c6fea0c9ddbf15` returns tree 92960f783, rc 0.
  - The three-dot diff adds only `dev/programme/triage/s6-batch26.md` and `dev/programme/delivery/2822.md`, and 204ffce80 touches only the row (1 file, +1).
  - There are no host or home paths (grep rc 1).
  - `^Verdict:` counts 13 ACCEPT, which matches the body.
- ev/ruling_verdict.txt: `roster_edit.ruling_verdict` at the head returns ACCEPT for P127-P139 and None for P140, the body's null control, which I re-ran.
- ev/ci.txt: the check-runs API shows 7 runs on the head: `arm` skipped, and `prelude`, `refresh` and `cancel-superseded` queued in two runs. No run concluded red, so there is no red check to answer. `gate` had not reported at read time.
- Destinations at the roster tip 558125209 (ev/roster.txt) and open PRs (ev/github_reads.txt):
  - R10-FLOW-DESIGN-STAGES: not-started, holds `cloud_dispatch.py` and `orchestrator_tick.py`. P128 and P132 route there.
  - R10-TRAIN-OVERLAP-GRADE: queued, holds `merge_train.py`. P129 routes there.
  - R10-ORCH-ROSTER-SCHEMA: not-started, every after-group done, holds `roster_edit.py`. P131(a), P133 and P139 route there.
  - R10-FLOW-TOOLKIT-MODEL: not-started, holds `replan.py`. P131 routes there.
  - R10-ORCH-LEDGER: carries-open (#2671 merged), holds `orchestrator_tick.py`. P132, P136 and P137 route there.
  - R10-ORCH-DISPATCH-REG: not-started, holds `bus.sh`. P134 and P138 route there.
  - R10-ORCH-REVIEW-PACKET: not-started, holds `bus.sh` and `review_packet.py`. P135 routes there.
  - R10-CLOSEOUT-CLEANUP: not-started. P130 routes there.
  - None of these groups is done or absorbed, and none has an open PR. I did not find a destination that is done or closing. The merge-train spool and merge-STATE live on the orchestrator machine, so I could not read them.
- Roster edits already made since aa679f28b (ev/roster.txt):
  - 29b0b8ff2: DISPATCH-REG after `[]`.
  - 3b5942aac: CLOSEOUT after PRUNE-REFS and WORKTREE-GC.
  - d87475fe1: UPDATE-PR-SIGNALS carries-open.
  - 558125209: PLAYBOOK loses ARCH-DOCS.
  - These match P130 B/C, P133 and P137 as written. ARCH-DOCS keeps its after list, so the owner's constraint holds. Nothing orphans CLOSEOUT, PLAYBOOK or ARCH-DOCS: each keeps its other edges, and no group lists CLOSEOUT in its after list.
  - DISPATCH-REG's release is sound. The need behind its only edge is on main (`ledger.py:108` `OPS = ("open", "close", "attempt")`, the 542 command path, the 655-657 `reviewer-fire` closes), and it shares no file with ORCH-LEDGER.
- Facts re-derived at da12aa37d (ev/code_reads.txt), at least one per ruling:
  - P127: `proposal-triage.md:8-9`, "One sonnet seat at / medium effort: judgement with an oracle.", is 36 lines and 294 words against caps of 36 and 489. Comment 6399377608 is the ruling-refuted block on P117, and 6399500180 is the merge at ac6c53581.
  - P128: `cloud_dispatch.py:122` "read CI on this head from the check-runs API" (no wait instruction), refusal at 182, `dispatch/reviewer-r10-x` at 391, `self_test` at 503. In `merge_train.py`: `NOT_GATING` at 328, `classify` at 417, the classify parser at 5471 (rc 0/1/3/2), `wait_ci` at 1103 with all-completed at 1134-1136. `ci.yml:74` is `prelude:`. `ci-watch.sh:2` is "alerts only on NEW states".
  - P129: `train_add` at 787, the pending/spool ALREADY test at 808-810, ADDED at 817-819, `skip` at 2286-2296 with a row of pr, phase and reason and no head, `seen` seeded at 2317, the `queue_take` drop at 2367-2370. I could not read the s40 `train.log` (not in the tree).
  - P130: the CLOSEOUT brief carries the quoted halves sentence. ARCH-DOCS files are `docs/architecture.md` and `README.md`, and PLAYBOOK files are `dev/audit/README.md` and `CLAUDE.md`, so the two share no file. I did not re-derive the -15.7 h and -13.7 h figures (card V49 is out of tree).
  - P131: `replan.py:174-175` `is_done` in ("done", "rca-done"), against `roster_lib.py:33`. aa679f28b has 4 absorbed and 5 carries-open groups. ROSTER-SCHEMA carry 14 is the replan phantom-work carry and carry 1 the absorbed-edge closure (0-indexed). `durations.json` sizes_hours are S 13.1, M 11.4, L 20.1, XL 30.2. `replan.py` has no inflow term, `--slots` is at 1292, `--durations` at 1281, the default of 6 at 97 with "the owner's cap", and "No network" at 13. I did not re-derive card V50's figures.
  - P132: tick UNBLOCKED line at 1161-1163; `critical_path` at `roster_lib.py:239`. I did not re-derive card V52's ages.
  - P133: `is_open` at 205-206. Tick blockers at 1154 via `open_groups` at 1148. `depth_of` at 232. Openness tests at `plan_page.py:189`, `plan_table.py:81` and `handover_prompt.py:49`. #2671 merged at 2026-10-23T23:20:07Z. I did not re-derive card V57's -3.1 h.
  - P134: `bus.sh:22-32` ordering note, `dispatch()` at 382, `open_pr.sh:48` automatic merge, `app_approve.sh:243`. I did not re-derive card V53's figures.
  - P135: `carry_audit.py:414-418` returns 1 on unrouted or bad items; `head_note.py:20` is `head_offset`. I did not re-derive card V54's counts.
  - P136: `ledger.py:505-515` `review_owed` with no carry test; `tick_loop.sh:16-18`; `sweep_template.md:41-44`; `orchestrator.md:109`; `CLAUDE.md:122`.
  - P137: #2524 merged at 2026-10-22T20:16:54Z, and its Forward-carry keeps the stage in-progress for the SIGKILL clause and the isolation. `dispatch/fixer-r10-flow-jidoka` now exists (7d3e293b8, after the head), so the dispatch has happened.
  - P138: `fixer.md:307-314`, `bus.sh:23`, `fix-review.md:140`. I did not re-derive card V56's counts.
  - P139: in `roster_edit.py` the op choices at 655-657 have no size op, and "size" occurs 0 times. 04de6ae7f's note has the size verdict at line 20 and the XL fallback at line 5. HEAT-METER's after list has four groups done and three in progress.
