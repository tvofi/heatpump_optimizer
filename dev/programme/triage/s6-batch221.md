# Proposal triage, session s14, batch 221

Sources: triage queue line 351 (orchestrator, 2026-11-11T23:37:14Z), ruled as P674. Line numbers
are at origin/main 61afd4f2db. Roster read at handoff/audit-r10-roster fa165de969.

## P674: Dependabot #3483 red on typing; seat-no-return fires on dispatch refs never fired

Verdict: ACCEPT (a) a new group R10-DEPENDABOT-3483-COMPAT, which re-locks #3483 with homeassistant-stubs held and makes Dependabot ignore the two typing-ruler pins; REJECT (b) a fired-record ledger for the no-return arm.

Source: triage queue line 351. (a) Dependabot #3483 (pip group in /tests, 8 updates, head
08d58a81bc) is red on `tests / typing`. Does it owe a compat group, as #3323 and #3414 did, or
should the bump be refused? (b) Four `seat-no-return` lines at 23:26Z came from continuations the
dispatch seat rendered and published at about 21Z, which the orchestrator never fired because
the handoffs had already succeeded. Proposed: key the arm on a FIRED record, or delete a render
that is not fired. Stopgap: OWED-ACK ttl=12.

Instances:
- (a) Typing job 130852340607 (`gh api .../actions/jobs/130852340607/logs`, line 467):
  `FAIL homeassistant-stubs is pinned at 2026.9.3 [found 2026.10.0]`, then `REFUSING to
  measure`, `1 of 5 typing-ruler checks FAILED`. The pin is `ruler.homeassistant_stubs` in
  tests/typing_budgets.json :42 (with `ruler.mypy` :41), enforced by tests/typing_ruler.py
  :467-472. The PR's diff moves homeassistant-stubs 2026.9.3 to 2026.10.0. Its other 7 bumps are
  minor: bleak, cronsim, httpcore2, httpx2, regex, truststore, zeroconf.
  `tests / nightly-status` is also red. Its cause was not examined here, and this ruling
  claims nothing about it.
- (a) The class: this is the third compat replacement of the /tests pip group. #3323 was
  re-applied as a555d52ae8 (R10-DEPENDABOT-3323-COMPAT, done). #3414 was re-locked as f402c1e8a9
  (R10-DEPENDABOT-3414-COMPAT, carries-open); its brief reads "the bot moved
  homeassistant-stubs past the deliberate hold that tests/typing_ruler.py enforces". #3483
  repeats that cause. Neither compat commit moved the stubs pin: `git show <c> --
  tests/requirements-typing.txt | grep '^[-+]homeassistant-stubs'` is empty for both. The hold
  is deliberate, because only CI can measure the census against the pinned pair (#504).
- (a) .github/dependabot.yml :26-33 (the `/tests` pip entry) has `groups: pip: patterns: ["*"]`
  and no `ignore`, so every weekly run may move the pair again.
- (b) `grep -h 'SEAT ENDED NO RETURN' cloud-relay.log*` gives 4 lines in the relay log. The log
  starts 2026-10-28T01:30Z and is 4727 lines long. All 4 are the four topics on line 351, and
  each was published but never fired. The arm (tools/audit/seat/cloud_relay.sh :751-801) keys on
  the dispatch ref's age. Its header (:759) already names the disposal: "Deleting the dispatch
  ref disposes it." `cloud_dispatch.py --publish` (:1503) pushes the ref at render time. Firing
  is the orchestrator's RemoteTrigger call, outside the tree. No fixer fire record exists; the
  ledger opens only `reviewer-fire` (cloud_dispatch.py :672-673).

Duplicate check:
- (a) No live group owns .github/dependabot.yml. R10-DEPENDABOT-3323-COMPAT is done and
  R10-DEPENDABOT-3414-COMPAT is carries-open, so neither can receive a carry (roster
  fa165de969).
- (b) P376 (s6-batch115.md) narrowed the arm to split-part topics. Nothing has ruled on unfired
  renders.

Accepted change: (a) a new group R10-DEPENDABOT-3483-COMPAT, severity medium as for its two
predecessors. The orchestrator adds it. Brief:
1. Re-lock tests/requirements-typing.txt through its header's compile with the 7 non-stub bumps
   of #3483. Hold homeassistant-stubs at 2026.9.3.
2. In .github/dependabot.yml's `/tests` pip entry, add `ignore` for `homeassistant-stubs` and
   `mypy`, the two pins `ruler` in tests/typing_budgets.json records. Add a comment saying
   moving either is a deliberate re-record of the typing census (#504), never a bot bump.
3. Close #3483 as superseded after the merge.

Demonstration: `tests / typing` is green at the head with the ruler printing `ok
homeassistant-stubs is pinned at 2026.9.3`. Null control: the same compile without the hold
reproduces this FAIL line.

Cost:
- (a) One lock file and about 6 config lines. tests/requirements-typing.txt and
  .github/dependabot.yml have no row in tests/structure_budgets.json. One fixer plus a sonnet
  review, as for #3414.
- (b) Rejected design: a fixer fire record means a new ledger kind, a write on the orchestrator's
  fire path and a read in cloud_relay.sh, a hot file, plus self-test arms. That is about 40 or
  more lines across two files and the orchestrator's procedure.

Binding:
- (a) The destination's severity is medium, which skips the 20% bar. On the bar alone, the
  `ignore` passes as the class barrier: it is the third compat replacement of one Dependabot
  group (#3323, #3414, #3483), and each cost a fixer and a review seat. Refusing the bump
  instead would leave the 7 minor bumps to recur weekly with the same stubs move. Under the
  over-20 rule this group is not critical path, hotfix or outside, so it waits for a slot.
  That is the orchestrator's to schedule.
- (b) The measured harm is 4 false lines in 14 days, each cleared by deleting its dispatch ref
  (one `git push origin --delete`). That disposal is already the arm's documented one. The
  ledger costs more than it saves. The rule that costs nothing: a render the orchestrator
  decides not to fire has its dispatch ref deleted at that decision. Delete the four refs above
  now; the OWED-ACK ttl=12 stopgap is then moot.
