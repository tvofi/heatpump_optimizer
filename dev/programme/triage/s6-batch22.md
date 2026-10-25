# Proposal triage, session s6, batch 22 (P101-)

Rulings from the s6 `proposals.md`, collected 4 or 5 to a pull request under
tvofi's batching rule of 2026-10-24 (one PR per ruling only when it unblocks
critical-path work). Numbering continues after `s6-batch21.md` (P97-P100,
#2790, merged).

## P101: set-stage done does not check open PRs' Carry: lines that name the group (S6-V35)
Verdict: ACCEPT (barrier) -> R10-FLOW-POSTMERGE. `tools/audit/seat/roster_edit.py set-stage <group> done` refuses, and writes nothing, while any open pull request body carries a `Carry:` marker naming that group, and prints the pull requests to re-point. Every other stage is unchanged.
- REJECTED: running the whole `carry_audit.py` over every open body. Only the destinations matter here, and `carry_audit.carry_dests` already reads them.
- REJECTED: leaving it to the memory rule (`done-before-reroute`). It is a manual step of the post-merge beat, and it has been skipped four times.
Source: s6 `proposals.md` `## V35`.
Instances: 4 blocks on 3 pull requests, as the orchestrator's memory and V35 record them; I did not open the PRs.
- #2404 at r5, r7 and r8, 2026-10-19: three review blocks, each a carry aimed at a group already set done.
- #2762, 2026-10-25: body item c8bac42d carries to R10-POLICY-FIXER-MD after that group was set done, so `carry_audit` reports BAD-DEST at train preflight and the merge is parked.
This is past the third instance of one class, so a barrier is owed, not a note.
Measured on main:
- `op_set_stage` sets `resume.stage` and checks nothing about the group's other readers (`roster_edit.py`, line 153).
- `carry_audit.carry_dests(text)` returns every destination token of a body's `Carry:` markers, and needs no network. The only network read is the list of open pull request bodies.
- Main's roster lags the roster branch, so `pr-contract` stays green on the stale destination and only the reviewer or the train preflight catches it (memory `done-before-reroute`, recorded 2026-10-19).
Cost:
- About 25 lines in `roster_edit.py`: when the stage is `done`, one bulk read of the open pull requests' bodies (`gh pr list --state open --json number,body`, a single call and not one per pull request), `carry_dests` over each, and a refusal naming the numbers.
- `set-stage done` runs about once per merged group, so the call count is about one per merge.
- Fail closed, the repository's usual rule: if the listing cannot be read, the stage is not set, and the refusal says so.
- A self-test with a stub listing: a body carrying to the group refuses; the null control, a body carrying to another group, sets the stage; a body with no `Carry:` also sets it.
- The cost of not doing it: a parked merge (#2762 is at train preflight now) and a fixer round to re-point the carry, once per hit.
Binding: four instances of one class, a cause that sits in one function, and a fix of about 25 lines and one API call per merge, against a manual step that has failed four times.
What would change the answer: a legitimate `done` while a carry still names the group (a deliberate dismissal in the same step). That would want an explicit `--allow-open-carry <reason>` flag; it would not change the refusal.
Carry text (for `roster_edit.py append-carry R10-FLOW-POSTMERGE`, citing `triage: dev/programme/triage/s6-batch22.md#P101`): "In tools/audit/seat/roster_edit.py `op_set_stage`, when the stage is `done`, list the open pull requests' bodies with one `gh pr list --state open --json number,body` call, take `carry_audit.carry_dests` of each body, and refuse without writing when any destination equals the group, printing the pull request numbers to re-point; if the listing cannot be read, refuse too. Every other stage is unchanged. Self-test with a stub listing: a body carrying to the group refuses; the null control, a body carrying to another group, sets `done`; a body with no Carry: sets it. Mutation proof: dropping the destination comparison fails the refusal case. Basis: carries to a group already set done produced BAD-DEST blocks on #2404 (r5, r7, r8, 2026-10-19) and #2762 (2026-10-25, parked at train preflight)."

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
