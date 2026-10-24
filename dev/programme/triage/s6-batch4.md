# Proposal triage, session s6, batch 4 (P54)

Proposals S6-U (P54) and S6-V1 to V6 (P55 to P59) of the s6 orchestrator's out-of-tree `proposals.md` (2026-10-24
~12:58Z), ruled as P54 from `dev/governance/roles/proposal-triage.md`. Numbering
continues after `s6-batch3.md` (P53). GitHub calls: 0.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P54: the tick's owner-gated line counts groups a mandate already covers
Verdict: DEFER -> owned by R10-ORCH-ROSTER-SCHEMA (it owns `roster_lib.py` and the group schema); re-triage when `owner_gate` has a structured form
Source: s6 proposals.md item S6-U (tick.txt REPLAN line 172, "38 group(s) blocked on owner disposition").
Instances: 1 recurring line, on every tick board. The count is real: on
`origin/handoff/audit-r10-roster` `bbe44258e`, 38 groups with a non-empty
`owner_gate` and `resume.stage` other than `done` (a python3 filter over
`wave-r10-groups.json` at that ref). 35 name a 10-digit mandate id in the text
(19 `6175172275`, 9 `6319294694`, 7 `6329234399`); 3 name none
(R10-REPLAY-SCOPED, R10-MERGE-SUBJECT-HARDEN, R10-STRUCTURE-ALIAS). The
mechanism: `orchestrator_tick.py` lines 1804-1823 count every open group whose
`owner_gate` is truthy and set `flag=True`.
Cost: S -- about 15 lines in `orchestrator_tick.py` plus a self-test arm, as
the item says; but the classifier it needs is a parse of free text, which is
where the cost is not S (see Binding).
Binding: `owner_gate` is free prose, and the one group the item names as
needing the owner, R10-FLOW-MQ-PROBE, reads "owner decision after the probe;
the probe ruleset itself under 6175172275": it cites a mandate id and still
needs tvofi. A rule "a cited mandate in force means not owner-blocked" would
therefore silence exactly the item that is real, the null control the proposal
cannot pass (35 of 38 cite an id; the true owner items are among them). A rule
that parses the prose further (which words mean "covered") is a regex over
sentences like "the mandate 6175172275 covers it until 2026-10-28T18:14Z, after
which a fresh grant is needed", which is a lapse date, not a cover. The sound
form is a structured field (for example `owner_gate.covered_by`, set by the
roster op that records the grant), which is a roster-schema change owned by
`R10-ORCH-ROSTER-SCHEMA`, not a tick edit; the benefit today is one constant
line per tick that the orchestrator already reads past, and it is unmeasured
in time or tokens, so the bar ("clearly") is not met. What would change the
answer: a missed owner item traced to this line's constant noise, or the
schema group landing a structured gate.

## P55: pool claim hygiene in cloud_dispatch (S6-V1 stale claims, S6-V2 hidden push errors)
Verdict: ACCEPT -> R10-FLY-CLOUD-SETUP-TOOLCHAIN (cloud_dispatch); carry: clear a claim ref whose handoff ref has not moved since the claim when appending the pool line; stop discarding stderr on the pool push, read back and refuse on mismatch
Source: s6 proposals.md S6-V1, S6-V2 (2026-10-24 ~13:25Z).
Instances: V1 3 (#2692, #2697, sav-comfort; each a POOL EMPTY run); V2 1, 2 lost runs (`2>/dev/null` on the POOL push). Source: orchestrator's account in proposals.md; not re-counted from logs.
Cost: S, about 15 lines in one existing script, no new file, no API calls.
Binding: the narrow form wins: an N-minute reclaim in the routine prompt is a timing heuristic that can race a live fixer, and a new pool_push.sh is a file for one call site. Null control: a claim whose handoff ref moved after the claim is left alone.

## P56: seat-owned background jobs killed at rotation (S6-V3)
Verdict: DEFER -> R10-FLY-DAEMONIZE-ARGV owns daemonize; re-triage on a second kill
Source: s6 proposals.md S6-V3.
Instances: 1 (roster app_push rc=143, one PR cycle).
Cost: app_push self-detaching is process-management code in a hot instrument.
Binding: one instance; the cheap form is one contract line, not worth a policy edit yet.

## P57: two writers on one queue or branch across rotation (S6-V4)
Verdict: DEFER; re-triage on a third instance
Source: s6 proposals.md S6-V4.
Instances: 2 (roster w5/w6; #2698 fixer vs update).
Cost: a flock named in a brief is prose.
Binding: rotated seats share no process, so the lock binds only a seat that remembers it. The enforceable form is atomic rename of the queue to an .inflight file in the queue readers; unmeasured benefit beyond one PR cycle.

## P58: carries routed to done groups (S6-V5)
Verdict: DEFER -> R10-ROUTING-INVARIANTS; judge the consumed-vs-pending marker design when it lands
Source: s6 proposals.md S6-V5; owner note that V5 is already being built.
Instances: 3 today plus 38 audit candidates, per the proposal; not re-counted.
Cost: none here.
Binding: the design is not yet in the tree.

## P59: fake liveness from a detached toucher (S6-V6)
Verdict: DEFER; re-triage on a second instance
Source: s6 proposals.md S6-V6.
Instances: 1; the toucher was killed.
Cost: pulse.py change in R10-ORCH-BEATD.
Binding: a log mtime is as forgeable and an idle polling seat writes no log; the stronger form (process CPU or children) is unmeasured.
