Fix review: blocked 80a62d9a7bba087c216e5370c31efb216581bf92 figure-unverified: the body's null control says the file lacks P52, but this head rules P52 REJECT; P52 also misstates three commit times and its comparison class's trigger

bus-nonce: 3709b45283483ed7bd14eb45c1d2c273

Round 1 of review for #2689. Measured head 80a62d9a7bba087c216e5370c31efb216581bf92 (the body's `## Head` names it). Reviewed in a worktree at that head, against merge base origin/main 50af6174f.

## Block

- The body's `## Null control` says: "`roster_edit.ruling_verdict` on a pid the file lacks (`P52`) returns None". At this head the file has `## P52` (added in e06c58981), and `ruling_verdict(src, "P52")` returns `REJECT` (ev/checks.txt). So the stated control does not reproduce. The control still works with a pid the file really lacks (`P53` returns None), so the fix is to update the body. The PR title and `dev/programme/delivery/2689.md` still say "(P45-P51)" for a file with eight entries, P45-P52.
- P52's `Instances:` dates the three P2b fixes "09:29Z-09:53Z". Their commit times in UTC are 07:29:46Z, 07:31:44Z and 07:53:28Z: `git log` shows +02:00 local time, and the ruling read that local time as Z. The ruling's conclusion still holds (all three come before b927f431a at 23:53Z), but the stated times are wrong in a record that later seats read as fact. It also says `d5dc3e26a` was "(02:36Z)". That commit is at 02:05:44Z. 02:36 is the time of its ci-ratchet grade (RCA line 19), so the entry should say which one it means.
- P52 says that `N-postreview-merge-red` has "`trigger` all false". In `dev/audit/config/bugclasses.json` at this head, `trigger.class_rca_on_record` is `true`. The other three trigger fields are false. P52 also says the class's `kind` is "process", but it is `instrument`. The sentence can be read as describing the new row rather than this class, but then it should say so. The trigger misstatement is part of the argument that the three-instance trigger "has not fired", so the entry should state it correctly.

## Findings

- R10-ORCH-BEATD's roster `files` are `daemonize.py` and `tick_loop.sh`, and its brief is a re-cut of an approved design (concern B, the supervised beat). The shared carry adds a policy rewrite to four `standing-*.md` contracts, `sweep_template.md` and `pulse.py`. The ruling says this widens the group and plans a possible split into `R10-FLY-STANDING-SEATS`, so the destination is valid under proposal-triage.md (an existing group with carry text). The widening still belongs in that group's design-review pass. Carry: R10-ORCH-BEATD
- P49's destination R10-FLOW-RECORD-PITCH lists `.github/workflows/tests.yml` and `tools/audit/seat/record_row.py` as its files. The record-autofix step that P49 cites is in `.github/workflows/nightly.yml` (lines 492-515 at this head), and the carry does not add it. The group's brief already says the step is moving with R10-CI-LAYOUT-P1, so whoever lands this carry should confirm where the step is then. Carry: R10-FLOW-RECORD-PITCH

## Evidence

- Merge check: `git merge-tree --write-tree origin/main 80a62d9a7bba087c216e5370c31efb216581bf92` exits 0, so the head merges cleanly. The diff from merge base 50af6174f (three-dot) is `dev/programme/delivery/2689.md` and `dev/programme/triage/s6-batch2.md` only. VERSION, the manifest and RELEASE_NOTES are untouched.
- INERT: `tests/closure.py` INERT has the prefix `dev/programme/`, which covers both files. Neither file is in INERT_EXCEPT. `tests/entities.py` could not run locally because the `homeassistant` module is missing, so the classification was checked by importing closure.py.
- ref_privacy: `ref_privacy.py --check` at this head reports 281 added lines judged and 0 refused. This settles the red `instrument-self-tests` at 44ee0e5f that the body answers. The body's answer is that a cheaper detector existed (`handoff_push.sh`'s guard), with its cost given, so the red-check trigger is answered.
- Verdicts: `ruling_verdict` reads P45, P46, P49 and P51 as ACCEPT, P47 and P48 as DEFER, and P50 and P52 as REJECT. That matches the body's 4/2/2 count over 8 entries. `triage_refusal` accepts a carry citing #P49 or #P46 and refuses one citing #P47 (DEFER). So the carry gate tells the verdicts apart.
- Roster groups: every named group exists in `wave-r10-groups.json`, both at origin/main and at origin/handoff/audit-r10-roster (now 0b19947d0; the file cites 4c54758d7). The groups are R10-ORCH-BEATD, R10-ORCH-ROSTER-SCHEMA, R10-FLOW-TOOLKIT-MODEL, R10-FLOW-RECORD-PITCH, R10-FLY-PRUNE-REFS, R10-FLOW-DESIGN-STAGES, R10-FLY-INERT-LOAD-TIME, R10-FLOW-MQ-PROBE, R10-FLY-RELAY-REVIEW-FF and R10-CI-LAYOUT-P2. R10-ORCH-BEATD and R10-FLOW-RECORD-PITCH are not-started at both refs. R10-FLY-RELAY-REVIEW-FF is carries-open on the roster branch, as P47 says. R10-FLY-INERT-LOAD-TIME, which P52 calls in-progress, is in-progress at origin/main and done (#2666) on the roster branch. R10-FLY-STANDING-SEATS does not exist, and the ruling names it only as a possible split.
- Cost/benefit, checked against proposal-triage.md:
  - The four ACCEPTs each cite measured instances, an S or S-to-M cost and a binding constraint.
  - P49 is ACCEPT (measure first). Its benefit is measured: 14 of 48 first-parent merges since 2026-10-23T00:00Z are record/autofix merges (re-derived at 50af6174f), and #2685's row names #2684. Only the mechanism is unmeasured, and the carry's first step measures it. I judge this ACCEPT rather than DEFER.
  - The DEFERs name their owning groups and what would change the answer.
  - The REJECTs name the binding cost.
- Figures re-derived at 50af6174f:
  - sweep_template.md line 61 names `train.sh`, and b16084794 is the template's last commit.
  - orchestrator.md line 109 reads "Four standing seats".
  - pulse.py has `STANDING` at line 91 and `judge_queue` at line 183. The queue format is at lines 47-52, and there is no file-liveness arm.
  - `roster_sync.chosen` works as described, and `carries-open` is outside `DERIVABLE_STAGES` (lines 88-89; the file cites 84-92).
  - replan.py's `touches_coordinator` is at lines 204-206.
  - `norm_head` exists (line 201).
  - standing-tick.md:8 is the one hit for wait/background.
  - The seven record merges each add their own `delivery/<N>.md`.
  - The RCA at 776d37392 (an ancestor of the branch tip f5b2f4624) states 6.0 h, 21 600 s, 129 s/day and 167 days.
  - I did not re-derive the out-of-tree session log figures (r10s5/r10s6 ledgers and reports): they are not in the tree.
- CI on this head: no check run has concluded red. The following were still in progress when read: tests / browser, tests / closures, tests / fast (3.14), governance / instrument-self-tests, governance / env-matrix and one prelude. The PR is a draft, and its mergeable_state is blocked.
