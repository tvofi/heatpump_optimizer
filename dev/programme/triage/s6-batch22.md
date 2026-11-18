# Proposal triage, session s6, batch 22 (P101-)

Rulings from the s6 `proposals.md`, collected 4 or 5 to a pull request under
tvofi's batching rule of 2026-10-24 (one PR per ruling only when it unblocks
critical-path work). Numbering continues after `s6-batch21.md` (P97-P100,
#2790, merged).

## P101: set-stage done does not check open PRs' Carry: lines that name the group (S6-V35)
Verdict: DEFER -> R10-ORCH-ROSTER-SCHEMA (the group #2733's R10-ROUTING-INVARIANTS is being folded into). Round 1 ruled ACCEPT to R10-FLOW-POSTMERGE; the fix review (verdict/2804 at c7817c1e) blocked it as misrouted, and this re-ruling takes its three points.
Source: s6 `proposals.md` `## V35`.
Instances: 4 blocks on 3 pull requests, as the orchestrator's memory and V35 record them; I did not open the PRs.
- #2404 at r5, r7 and r8, 2026-10-19: three review blocks, each a carry aimed at a group already set done.
- #2762, 2026-10-25: body item c8bac42d carries to R10-POLICY-FIXER-MD after that group was set done, so `carry_audit` reports BAD-DEST at train preflight and the merge is parked.
Considered:
- R10-FLOW-POSTMERGE (round 1's destination): its files are `merge_pr.sh`, `merge_train.py` and `INSTRUMENTS.md`; it owns neither `roster_edit.py` nor `carry_audit.py`, the only files the fix edits. Does not fit.
- R10-ROUTING-INVARIANTS (#2733): owns the class (invariant 1, "every carry not yet implemented routes to a roster group that is not done") and lists `carry_audit.py` and `roster_edit.py` as files, but is folded into R10-ORCH-ROSTER-SCHEMA, so the carry goes to the survivor.
- R10-ORCH-ROSTER-SCHEMA: lists `roster_lib.py`, `roster_sync.py` and `roster_edit.py`, and the folded roster-queue lines 291-306 are being applied to it. It is the owner of the seam.
Measured on main:
- `op_set_stage` (`roster_edit.py`, line 153) is not the routine route to `done`: `roster_sync.derive` (`roster_sync.py`, lines 263-301, run every pass by `state_docs.py beat --apply`) sets `done` itself when a group's pull request merges. A refusal inside `op_set_stage` alone would miss that path, so the round 1 premise that the cause "sits in one function" was wrong, and its cost estimate (about 25 lines, one API call per merge) was for the wrong site.
- #2733's owner brief, section (b), chose "roster_sync sets the existing `carries-open` stage instead of `done` when pending carries remain; no set-stage refusal, so the factual sync at every merge is unchanged". That covers carries already on the roster. The open-PR-body case is different: the carry is in a body not yet merged, so it is not on the roster to be seen, and covering it would put a bulk read of open bodies into every beat pass, not once per merge. The ruling cannot bound that cost: the figure is unmeasured.
Cost: not estimated for an accept. The corrected site (`roster_sync.derive`, run every pass) multiplies the API read by the pass count, against the owner's stated wish to leave the factual sync unchanged.
Binding: an owner design decision (b) that chose `carries-open` over a set-stage refusal, and an unmeasured benefit, which is a DEFER and never an ACCEPT.
What would change the answer: R10-ORCH-ROSTER-SCHEMA lands `carries-open`, and a carry to a group set done while a pull request body still names it recurs after that. The carry would then be: `roster_sync.derive` holds a transitioning group at `carries-open` while an open pull request body's `carry_audit.carry_dests` names it, reading the open bodies in a call the beat already makes if one exists, with a null control of a body carrying to another group. Until then `done-before-reroute` (memory) is the step, and the train preflight's BAD-DEST is the backstop.

## P102: dispatch watcher has no single-instance guard (S6-V36)
Verdict: ACCEPT NARROWED -> R10-ORCH-DISPATCH-REG (owns `tools/audit/seat/bus.sh`, size S). `bus.sh watch` takes an exclusive lock for its state directory and refuses to start a second instance, naming the holder's pid. The persistent baseline V36 asks for already exists, so no new instrument is built.
- REJECTED: a new in-tree watcher instrument beside `bus.sh watch`. It would duplicate the existing watcher, and the baseline half of the ask is already met by `bus.sh`.
- REJECTED: a seat-brief rule ("check for a running watcher before launching"). It is the manual step that has slipped twice, and the repo prefers a wired check to policy where an affordable script exists.
Source: s6 `proposals.md` `## V36`.
Instances: 3 slips, 2 kinds.
- Stray second detached watcher launched by dispatch w27 at about 08:05Z and again at about 08:15Z on 2026-10-25, each killed by PID; V36 cites dispatch-report.txt. I did not re-read it for the PIDs.
- Missed baseline: a relaunch re-baselined and missed handoff ea464fe6 (#2780 r4) for 0.6 h. Read: `dispatch-report.txt` line 357, "Watcher miss cause: relaunch re-baselined; watch2.sh uses persistent acted.txt".
- Related, already ruled: V31 in `s6-batch21.md` (a restarted standing seat leaves its predecessor running) is the same family but concerns seats, not the watcher process.
Measured on main:
- `bus.sh watch` (line 433) keeps its baseline in `$S/refs` and rewrites it after each pass (`mv "$S/refs.new" "$S/refs"`), so a relaunch does not re-baseline. The miss was in the seat's hand-rolled `watch-w26.sh`, not in `bus.sh`.
- `bus.sh` contains no lock, `flock` or pidfile (grep for `lock|flock|pidfile` found none), so two `watch` runs also race on `$S/refs`.
Cost:
- About 10 to 15 lines in `bus.sh watch`: a `mkdir`-based lock (portable to macOS, which has no `flock`) holding the pid, a stale-lock check by `kill -0`, release on exit by trap.
- A self-test case: a second `watch --once` while the first holds the lock refuses; the null control, a lock whose pid is dead, is taken over. Mutation proof: removing the refusal fails the first case.
- No standing CPU, no API call; bus.sh is a hot file already named by this group, so no new file.
- Seats then call `bus.sh watch` instead of a scratch script. Whether `bus.sh watch` covers non-handoff PR heads (the dispatch seat's second duty) is unmeasured here; that part is DEFER, not accepted.
Binding: three slips in one day on the dispatch path, each costing a kill by PID or 0.6 h of lost review start, against a lock of about 15 lines in a file the group already owns. The new-instrument half is rejected because the existing watcher already persists its baseline.
What would change the answer: if R10-ORCH-BEATD makes beatd the only host of the watcher under `daemonize.py`, the lock belongs there and this carry is dropped.
Carry text (for `roster_edit.py append-carry R10-ORCH-DISPATCH-REG`, citing `triage: dev/programme/triage/s6-batch22.md#P102`): "In tools/audit/seat/bus.sh `watch`, take a single-instance lock on the state directory with `mkdir` holding the pid; a second instance refuses and names the holder; a lock whose pid is dead is taken over; the trap releases it on exit. Self-test: a second `watch --once` under a live lock refuses; the null control, a dead-pid lock, runs. Mutation proof: dropping the refusal fails the first case. Basis: dispatch w27 launched stray watchers at about 08:05Z and 08:15Z on 2026-10-25, and a relaunch re-baselined and missed #2780 r4 for 0.6 h."

## P103: pulse's verdict arm names only the oldest unconsumed verdict (S6-V37)
Verdict: ACCEPT -> R10-ORCH-BEATD (carry; it already owns `tools/audit/seat/pulse.py` under P46 and P93). `judge_verdict` prints one line per unconsumed verdict (PR, verdict word, head, age), oldest first, and the arm's seat routing is judged per verdict. The count-plus-oldest summary is dropped.
- REJECTED: a separate tick-board change. The hiding is in the arm's one-line summary, and the tick reads the same arm.
- REJECTED: raising the verdict bound so fewer verdicts qualify. A MERGE verdict is actionable at once, and the bound only decides when it is called owed.
Source: s6 `proposals.md` `## V37`.
Instances: 1 slip, one 3.8 h loss, from the orchestrator's account in V37: pulse printed "oldest #2780 blocked" with N = 2 or 3 from about 06:00Z to 09:20Z while #2749's MERGE verdict (b4fdc4f38, live head 3581be11) sat unqueued. I did not re-run pulse for the sweeps. The class is a second instance of "an aggregate hides an actionable item" (memory `never-ignore-waiting-work`); the barrier is a code change, not another memory rule.
Measured on main:
- `judge_verdict` (pulse.py, lines 145-165) sorts the owed verdicts by age and formats only `owed[0]`, so every entry after the first appears only inside the count.
- The seat routing at lines 201-210 picks the seat from the oldest owed verdict alone: "merge" if that one is a merge, else "dispatch". With a blocked verdict oldest and a merge verdict behind it, the merge seat is never named. This is the same defect in a second place.
Cost:
- About 10 to 15 lines in `pulse.py`: loop over `owed` for the detail, and name the merge seat when any owed verdict is a merge, dispatch when any is not (both when mixed).
- A self-test with two owed verdicts, a blocked one older than a merge one: the output names both PRs and both seats. Null control: one owed verdict prints one line as before. Mutation proof: restoring `owed[0]`-only fails the two-verdict case.
- No new API call and no new file; the verdict list is already read. Output grows by one line per owed verdict, normally 0 to 3.
Binding: a 3.8 h loss of a ready merge on the critical path, in a function of about 20 lines that the group already owns, against a few lines of output. The detail is already in hand.
What would change the answer: nothing found; a long list of owed verdicts would want a cap on printed lines, not a return to one.
Carry text (for `roster_edit.py append-carry R10-ORCH-BEATD`, citing `triage: dev/programme/triage/s6-batch22.md#P103`): "In tools/audit/seat/pulse.py, make the verdict arm name every unconsumed verdict, not only the oldest: `judge_verdict` prints one line per owed verdict (PR, verdict word, head, age), and the standing-seat routing names the merge seat when any owed verdict is a merge and dispatch when any is not. Self-test: a blocked verdict older than a merge verdict names both PRs and both seats; the null control, one owed verdict, prints one line. Mutation proof: restoring the oldest-only summary fails the two-verdict case. Basis: #2749's MERGE verdict sat unqueued for 3.8 h behind #2780's blocked verdict on 2026-10-25."

## P104: recurring friction on gate-scoping.md, count 5 (issue #2768, re-files #2746)
Verdict: REJECT the issue as a defect to fix in the rule: the orchestrator closes it with this reason. Of the five counted entries, three are P81's, and the two new ones (#2707, #2698) have a cause in the cloud container's environment, which the rule's text does not decide. P81's reopening condition ("a friction line naming the rule in a pull request merged after c686fe36 whose cause is the rule's text") is not met by either.
- REJECTED: a rule-text change. `dev/governance/rules/gate-scoping.md` is at its token cap (794/794, #2700), and naming the container trap there would add a sentence for a transitional condition that `INSTRUMENTS.md` already documents.
- REJECTED: a new group for the container trap. Its fix is `cloud-setup.sh`'s profile (see Measured), which the pasted setup script already owns.
Source: bot issue #2768 (filed 2026-10-24T21:38Z by the governance `record` job), re-filing #2746; the orchestrator's re-triage request.
Instances: the bot's window is `v7.0.4..origin/main` (v7.0.4 stamped 2026-10-22T15:48+02:00) and its count is 5 distinct pull requests. `policy_lint.mjs --stats` prints no pull request numbers, so I took them as P81 did: the merged bodies that carry a `gate-scoping` friction line, from one `gh pr list --state merged --search 'gate-scoping in:body merged:>=2026-10-22'` and then `gh pr view` of #2698 and #2707. #2572 and #2582 also carry a line but were merged on 2026-10-22 before the v7.0.4 stamp, so they are outside the window. The five:
- #2622, #2627 and #2700, as P81 counted them (an interpreter, a skipped check, a token-cap observation).
- #2707, merged 2026-10-24T21:35Z (after c686fe36, `git merge-base --is-ancestor c686fe36 origin/main` succeeds): `gate-scoping: cost`, the cloud seat's `prepr.sh` closures step refuses any diff reaching `tests/entities.py`, because the strace recording exits 1 at the base as at the head. Its body measures the same two failing checks at both ends (`2 of 2425 ENTITY CHECKS FAILED`), which makes the cause the seat's environment and not the diff. About 19 min per occurrence; round 1 of that PR carried the same.
- #2698, merged 2026-10-25T03:28Z: `gate-scoping: unenforced`, `mutation_table.py --pin-killed` inherits the container's `BASH_ENV`, so the `tests/entities.py` baseline goes red on two shell-step checks that plant a fake `python3`. Its disposition: `Carry: dismissed: a documented container trap, no tree change owed by this group`.
Measured on main:
- `tools/audit/seat/INSTRUMENTS.md` (lines 236-240) documents the trap and its end: until the pasted setup script writes `cloud-setup.sh`'s idempotent profile, the container's `BASH_ENV` puts the venv python ahead of the test stubs, so a cloud seat runs `tests/entities.py` with `env -u BASH_ENV`. The cure is documented where cloud seats read, and it is transitional.
- `dev/governance/rules/gate-scoping.md` says nothing about `BASH_ENV` or the cloud container (`git show origin/main:dev/governance/rules/gate-scoping.md | grep -n -i 'BASH_ENV'` is empty), and its interpreter paragraph is #2627's answer. Neither new line asks the rule to say something different about the gate; both are about the seat environment the gate ran in.
- The two entries are one family, not two causes under one tag, but the family is the container, not the rule. That is one cause across two PRs, short of the third instance that owes a barrier.
Cost: not applicable; no instrument.
Binding: the threshold counts the rule id a body writes after `gate-scoping:`, a tag seats use for any gate-adjacent friction. The three older entries are three causes, answered or owned under P81; the two new entries share a fourth cause that sits in the container profile, documented and transitional. Changing the rule would address none of them.
What would change the answer: a third entry from the BASH_ENV family after the profile lands (then a cloud-setup or recorder defect, owed `env -u BASH_ENV` inside `derive_closures.sh`'s recorder), or a friction line whose cause is the rule's text.
Unverified: that #2707's two failing checks are the same two shell-step checks as #2698's. #2707 names them by title, #2698 by behaviour, and I did not run `tests/entities.py` under a cloud container. If a seat shows they differ, #2707 is a separate cause (a recorder defect) and is DEFER to R10-FLOW-JIDOKA with that proof, not a rule-text finding.
Disposition note: the bot's body updates in place while the window stands, so #2768 will keep reporting a count at or above 3 until the next stamp resets the window. Closing it with this reason is the orchestrator's to do; the bot never closes.
