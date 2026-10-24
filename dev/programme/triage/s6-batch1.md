# Proposal triage, session s6, batch 1 (P42-P44)

The s5 orchestrator's untriaged batch 3 (items N, O, P of the s6 orchestrator's
out-of-tree `proposals.md`), ruled in order as P42-P44 from
`dev/governance/roles/proposal-triage.md`. O is a defect in an instrument (a
false refusal), ruled only to set its route, as `s5-batch2.md#P34` did.

Base: origin/main `50af6174f`; roster origin/handoff/audit-r10-roster
`4c54758d7`, read with
`git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`.
Logs cited by file name are in the s5 orchestrator's scratch directory
(`/Users/timmalmstrom/hpo-orch/r10s5/`, out of tree). GitHub calls: 0.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P42: the relay skips a handoff with a live update_pr lock; tick_loop takes --no-relay
Verdict: DEFER -> owned by R10-FLOW-BODY-ONLY (its carry (c) rewrites the relay's handoff arm)
Source: s6 proposals.md item N (s5 measurement).
Instances: 3 -- `update-2675.log` records `update_pr: BUSY` at
2026-10-23T23:25Z, 2026-10-24T00:30Z and 00:56Z for `fix/r10-livestate-pr`,
each time another run (pids 34294, 75208, 77510) held the branch worktree, and
`dispatch-report.txt` lines 48, 56 and 63 say the holder was a cloud-body run
at the same code head. In all three the dispatch run waited and then completed
(`update-2675.log` ends in `HEAD=a9e26e07...` and `HEAD=2845e545...`). The log
shows delay, not a wrong write; whether the relay's body was older than the
fixer's is not recorded anywhere (the three body hashes differ, no log says
which was newer).
Cost: S for the skip -- a lock probe in `cloud_relay.sh`'s handoff arm, one
fixture row, one mutant; the flag is a `tick_loop.sh` argument. The group
`R10-FLOW-BODY-ONLY` is not-started and already edits that arm.
Binding: the harm is unmeasured. `update_pr.sh` already exits 75 on a held
lock, and the relay retries on its next pass (`rg -n 'urc.*75' tools/audit/seat/cloud_relay.sh`),
so the cost is one wait of a few minutes per race, three times in about four
hours, with a working override already in use (`HPO_TICK_RELAY`, read at
`tick_loop.sh` line 76). A proposal whose benefit is a few minutes and whose
existing workaround is one environment variable is not "clearly" better. What
would change the answer: a log showing the relay applying a body older than the
fixer's (a stale write), or the race recurring after `R10-FLOW-BODY-ONLY`
moves the relay to body-only updates, which removes most of its collisions
(a body move would no longer run `update_pr.sh`'s worktree path at all). Route
the observation to that group's fixer; no new carry.

## P43: queue_pre_flight's findings arm refuses a PR that adds its own carry file
Verdict: ACCEPT -> R10-FLY-CARRY-DISPOSITION (new carry; a defect, route set here)
Source: s6 proposals.md item O (s5 run16).
Instances: 1 direct -- `merge-report.txt` 2026-10-24T02:06:48Z parked #2675 in
run16: "#2674 has no owner: no live roster group lists it and there is no
dev/programme/carries/carry-2674.json", though #2675's head `2845e545` adds
that file (the orchestrator's 02:18:14Z line records the ruling and the direct
merge). The line still holds on origin/main `50af6174f`:
`rg -n 'load_dests' tools/audit/seat/queue_pre_flight.py` prints line 196,
`ca.load_dests(self.checkout, "origin/main", issue_state=self.issue_state)`;
`load_dests` (`rg -n 'def load_dests' -A12 tools/audit/carry_audit.py`) lists
`dev/programme/carries/` with `git ls-tree` at that one ref, so a carry file
the pull request adds is invisible, and `self.dests` is cached for the whole
train. Class size: `git log origin/main --since=2026-10-14 --diff-filter=A
--name-only --format= -- dev/programme/carries/ | sort -u | wc -l` prints 1
this round, so the route is rare; but `finding-propagation.md` sends a finding
for a stage with no live group to exactly that file, so every use of the
documented route is refused here.
Cost: S -- `load_dests` takes an optional `extra_ref` and unions the
`issue` numbers of that ref's carry files; `findings_gate` passes the PR head
and stops caching one set for every pull request (a per-pull-request union of
the cached main set with one `ls-tree`, local git, no API call); two fixture
rows with a null control; one mutant. All inside `carry_audit.py`, which this
group already edits, plus about 3 lines in `queue_pre_flight.py`.
Binding: the refusal is a false park of a PR that the documented route
produced, and its only cure is a hand-written `direct` merge line under the
mandate (about 12 minutes on #2675: 02:06Z park, 02:18Z direct). Controls the
fixer owes: #2675's head refuses before and passes after; a body citing a
carry file in neither main nor the head still refuses. The carry names
`queue_pre_flight.py` explicitly because the group's `files` do not list it.

## P44: brief_lint lints a roster group's `carry[]` strings
Verdict: DEFER -> no owning group; re-triage on a measured stale carry
Source: s6 proposals.md item P (s5 #2683 fixer).
Instances: 1 constructed, 0 incidents. Reproduced at origin/main `50af6174f`:
a scratch copy of the roster with a carry holding a nonexistent file, symbol and
line (`no_such_file_zzz.py`, `plant_nonexistent_symbol_qqq()`,
`merge_train.py:99999`), run as
`node tools/policy/brief_lint.mjs <scratch wave-*-groups.json>`, gave
`TOTAL: 0 error(s)` for both the base and the planted copy. The cause is
`tools/policy/brief_lint.mjs` lines 987-988, which pass only `g.brief` to
`lintBrief`. No cited case where a stale carry citation cost a fixer a round.
A lower bound on the exposure, measured with a path-existence grep at
origin/main: 557 carries in 125 of 171 groups, 62 backticked repo paths, 4
missing (`R10-FAHRENHEIT` 0, `R10-BRIEFS-FOLD` 19, `R10-CI-LAYOUT` 11 and 14),
at least two of them paths a later group creates.
Cost: M -- a loop over `g.carry` in `brief_lint.mjs`, a fixture pair in both
directions (the file's own convention, `fixtures/shape-defects.json`), a
mutant, and the existing roster's real errors to clear or whitelist before the
roster seat's lint gate passes again; every `roster_edit.py` append runs that
gate, so a false error there blocks the orchestrator's carry route. The
`brief-citations.md` rule itself says a linter that cries wolf gets bypassed.
Binding: the benefit is unmeasured (0 stale-carry incidents against 557
carries) and the cost includes a new false-positive surface on the one file
every seat edits under contention. What would change the answer: one incident
where a fixer or reviewer acted on a carry's wrong citation, or a full run of
the carry lint over the roster showing that most of the errors are real (more
than a handful of the 4 above) and none are future-file references. Until then
`brief-citations.md` is accurate as written (it says carry FILES, not
`carry[]`), so no doc claim is false.
