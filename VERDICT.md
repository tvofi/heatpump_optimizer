Fix review: blocked e40e45eeb9509e44bb93d43373cf777cc62f40d8 claims: P139 dates the three design-verdict commits 17:40Z, 17:48Z and 17:51Z, but in UTC they are 16:40Z, 16:48Z and 16:51Z (committed at 17:xx+01:00)

bus-nonce: e9262f0997080aec766c9e26ec2bc314

Round 2 (a delta review of #2822; round 1 blocked released-early at 204ffce804bbf0f602ad258b42c6fea0c9ddbf15, comment 6400503903). Measured head: e40e45eeb9509e44bb93d43373cf777cc62f40d8.

## Block

- P139, lines 192-194 at the head: "revise 04de6ae7f (fabd19b8a, 17:40Z)", "revise e23ace899 (636a85b36, 17:48Z)", "approve 21f4fbfe9 (ad376684f, 17:51Z, round 3)". The commits read `2026-10-25T17:40:56+01:00`, `17:48:41+01:00` and `17:51:54+01:00`, which are 16:40:56Z, 16:48:41Z and 16:51:54Z (`ev/p139-times.txt`). The same entry gives the design commit 04de6ae7f correctly as 16:34Z (17:34:27+01:00), so the record now says 66 minutes passed between delivery and the first review, when the real gap was 6 minutes. These are local times labelled as UTC in a durable record that later seats will read as fact. The fix is to replace the three times with 16:40Z, 16:48Z and 16:51Z. Nothing else in the entry depends on them: the cite `design-verdict/R10-HEAT-METER@ad376684f`, the approved head 21f4fbfe9 and the note's line 39 ("## Size verdict: L, conditional on #2753") all hold.

## Findings

- The PR title, and the delivery row `dev/programme/delivery/2822.md` that copies it, read "Merge remote-tracking branch 'origin/main' into triage/s6-batch26". That is a merge-commit subject, not a description of the batch. It was the same at the round-1 head, so it lies outside this round's delta and is not part of the block. Carry: dismissed: outside the round-2 delta and no ruling depends on it; the orchestrator can retitle the PR and re-render its row with the repair push.
- The DISPATCH-REG release is still owed. P133 rules that `set-after R10-ORCH-DISPATCH-REG -`, already applied on the roster branch (DISPATCH-REG `after: []` at origin/handoff/audit-r10-roster), holds only with a seam-split architect note naming R10-ORCH-LEDGER. No group carries one at any of the three rosters read (`ev/p133-test.txt`, seam_note_names_P=False everywhere). If no note exists, the edge goes back. This is an orchestrator task owed after the merge. Carry: R10-ORCH-DISPATCH-REG
- After the merge, P137 says the follow-on fixer must still set `resume.pr` 2524 on R10-UPDATE-PR-SIGNALS, which is `pr: None` at origin/main and at the roster tip. A follow-on dispatch ref now exists: `dispatch/fixer-r10-update-pr-signals`, 2026-10-25T16:53Z. Carry: R10-UPDATE-PR-SIGNALS

## Evidence

- Merge: `git merge-tree --write-tree origin/main <head>` exited 0, and no claim driver ran (`ev/merge-tree.txt`).
- Scope: the PR changes only `dev/programme/triage/s6-batch26.md` and `dev/programme/delivery/2822.md` (`ev/pr-stat.txt`). The round-2 delta touches only the batch file (`ev/delta-stat.txt`). No host or home path appears in the diff, and no Claude or Co-Authored-By trailer appears in the commits.
- Body figure: `grep -oE '^Verdict: (ACCEPT|DEFER|REJECT)' ... | sort | uniq -c` gives 13 ACCEPT, matching the body (`ev/verdict-count.txt`). The body's per-ruling summaries match the file, and so do its Head and Null-control sections (P140 is absent from the file).
- Rulings outside the four the coordinator named (`ev/rulings-delta.txt`): P127, P128, P132, P135 and P138 are byte-identical to the round-1 head. Four others moved, all as round-1 repairs that the body's Head section names:
  - P129: the `merge_train.py` citations went from 806-809 and 817-819 to 808-809 and 819. At da12aa37d and origin/main, 808 is `if str(pr).isdigit() and int(pr) in pending | {...}:`, 809 is `t.log(f"ALREADY #{pr}: ...")` and 819 is `t.log(f"ADDED #{pr} to the live train ...")`. Correct.
  - P131: `:319-321` became `:322`. replan.py 322 is `is_live = stage in LIVE_STAGES`. Correct.
  - P130: Cost now says one carry that is the brief addition, with no separate edit-brief, appended alongside CLOSEOUT's edge change. The roster tip confirms CLOSEOUT-CLEANUP `after` is `[R10-FLY-PRUNE-REFS, R10-FLY-WORKTREE-GC]` and no longer names ARCH-DOCS or PLAYBOOK.
  - P134: the verdict line now ties the DISPATCH-REG release to P133's seam note. Its destination is unchanged.
- Released-early is closed (check 1). I wrote my own harness, `ev/p133_reviewer_harness.py`, which implements P133's file test from the ruling text: `files` plus carry tokens under the seven prefixes, bare *.py/*.sh/*.mjs names matched by basename, INSTRUMENTS.md excluded, and the seam note and `closes_round` checks. At origin/main 20e9f0219, at 1ac59f510 and at the roster tip 9e5f5cf1c, it blocks each of the four named dependents on R10-UPDATE-PR-SIGNALS:
  - FLOW-ROSTER-FREEZE: cloud_relay.sh, pr_args.sh, update_pr.sh
  - FLOW-BODY-ONLY: the same three
  - FLY-OPENPR-ATOMIC: merge_train.py, open_pr.sh, pr_args.sh, update_pr.sh
  - FLY-ORPHANS-REWRITTEN: cloud_relay.sh
  
  All four still name R10-UPDATE-PR-SIGNALS in `after`. UPDATE-PR-SIGNALS itself is `in-progress` at origin/main and at the roster tip, so no stage releases anything. Every other P133 instance reproduces exactly: GH-READ-RETRY blocks CARRY-DOC-CONTEXT on `tools/pr/app_approve.sh`; LEDGER and RELAY-REVIEW-FF block ARCH-DOCS; ROUND-PLAYBOOK shares no file; LEDGER and DISPATCH-REG share ledger.py, orchestrator_tick.py, bus.sh and cloud_relay.sh at origin/main, where the edge is still present; SUITE-ENV-FLAKES and NO-FOOTERS have no open dependent.
- Mutant on that harness: with the carry arm dropped from touched() (`ev/p133-mutant-nocarry.txt`), FLY-OPENPR-ATOMIC and FLY-GH-READ-RETRY are released from UPDATE-PR-SIGNALS. So the carry arm the ruling adds is load-bearing, not vacuous, and the carry text's control "drop the carries from touched()" has a real target.
- Destinations (check 2), at the roster tip and at origin/main:
  - R10-ORCH-ROSTER-SCHEMA (P133, P139): not-started, every after-group done.
  - R10-ORCH-DISPATCH-REG (P136): not-started.
  - R10-ORCH-LEDGER (P137): carries-open, its PR #2671 merged.
  
  None is done or absorbed, and no open PR names any of them (search of the 15 open PRs, `ev/github.txt`). I could not read the merge-train spool, because it lives on the orchestrator's machine; with no open PR for these groups, there is nothing that could be spooled.
- Verdict words: P133 ACCEPT narrowed, P136 ACCEPT on (a) and DEFER on (b), P137 ACCEPT narrowed, P139 ACCEPT narrowed. Each carries Source, Instances, Cost, Binding and carry text with a `triage: dev/programme/triage/s6-batch26.md#P<n>` citation, and each carry names controls and a mutant.
- File:line claims at origin/main f54f40cc1 (check 3), quoted in `ev/line-claims-origin-main.txt`. All hold at da12aa37d and origin/main:
  - `roster_lib.py:33` `DONE_STAGES = ("done", "rca-done")`
  - 205-206 `def is_open` ... `not in DONE_STAGES`
  - 232 `oa = [a for a in g.get("after") or [] if is_open(G[a])]`
  - `orchestrator_tick.py:1154` `blockers = [a for a in (g.get("after") or []) if a in open_g]`
  - 704 `def _dispatched(self, S: str)`
  - `plan_page.py:189`, `plan_table.py:81`, `handover_prompt.py:49` each test openness themselves
  - `replan.py:175` `in ("done", "rca-done")`
  - `ledger.py:108` `OPS = ("open", "close", "attempt")`, 542 the open/close arm, 655-657 the close self-test
  - 505-515 `def review_owed` ... `REVIEW OWED: #{n} {head[:12]}`
  - `tick_loop.sh:16-18` `$HPO_STATE_DIR/tick.txt, written whole then renamed`
  - `sweep_template.md:41-44` the tick_alive/tick_log/tick_brief/tick_stale_min rows
  - `roster_sync.py:392` `...setdefault("resume", {})["pr"] = c.pr`
  - `orchestrator.md:109` the four standing seats, `CLAUDE.md:122` the `standing-tick.md` row
  - `roster_edit.py` op choices (655-657): exactly the nine P139 lists. `size` occurs 0 times. `set-resume --field <stage|commit|branch|last_step|next_step|note>` has no `pr`.
- Other figures re-derived:
  - #2524 merged_at 2026-10-22T20:16:54Z (fd9914851); #2502 open; #2753 open.
  - The `archive/handoff/r10-pusher-reap` tag (a0cb0cdd7) is an ancestor of main.
  - `dispatch/fixer-r10-pusher-reap` dates from 2026-10-22T18:32Z.
  - HEAT-METER is after seven groups, four done. PARAMS-OWNER (#2817) and ARCH-SHAPES (#2819) are in-progress at the roster tip (still not-started at origin/main's older roster copy); THERMAL-POWER-OPTION is in-progress with #2753.
  - P137's "no ref matches `jidoka`" held when it was written. `dispatch/fixer-r10-flow-jidoka` appeared at 2026-10-25T16:47Z, before this head was committed at 17:03Z, and is the operational step the ruling asks for (`ev/refs.txt`).
- Figures I did not re-derive: the card figures (P133's -3.1 h and C0 161.58 -> 158.50 h, P136's 5.4M cache-read per hour, P137's -3.1 h, P139's -13.9 h) are the cards' own and are cited as such.
- CI on the head, from the check-runs API (`ev/github.txt`): 7 runs. Six are queued (prelude, refresh and cancel-superseded, twice each) and arm is skipped. None has concluded red, so step 11 owes nothing. The body's "Red checks: none" stands for now.
- Mutation proof: n/a. The diff writes no production code line.
