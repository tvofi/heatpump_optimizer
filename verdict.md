Fix review: merge 0238b7c7cfb176d5ffbb66068ba93ff2bc8f264f

bus-nonce: 9f0e9c65a8ee3b0fb86ab7ccf69ad03d

## Scope

Round 1 of fix review for #2908 (triage s10 batch 48, P236/V150). Measured at head `0238b7c7cfb176d5ffbb66068ba93ff2bc8f264f`, merge base and origin/main `6d86acc909f7fc465e5736771daf8fa45c1373a4`, roster `handoff/audit-r10-roster` `ba973babd`. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract read is current. I re-read the head before writing, and it is unchanged. The diff is two files: `dev/programme/triage/s6-batch48.md` (one `## P236:` entry) and the delivery row. No production code, policy file, claim file, `VERSION`, manifest version or notes heading is touched. The rendered packet reported no refusals and no advisories. `carry_audit` gave 1 item, 1 routed (R10-ORCH-BEATD).

## Mutation proof (step 1)

I re-ran it on the triage gate, the file's only consumer: `roster_edit.py` `ruling_verdict` and `triage_refusal` at origin/main, driven with a `From triage P236 ... triage: dev/programme/triage/s6-batch48.md#P236` carry.
- RESULT committed: `ACCEPT`, refusal `None`. The carry lands.
- RESULT mutant 1 (`Verdict: ACCEPT narrowed` changed to `Verdict: DEFER`): refused, `... #P236 is not an ACCEPT ruling (DEFER)`.
- RESULT mutant 2 (`## P236:` changed to `## P237:`): refused, `(no such entry)`.
- RESULT mutant 3, my own (verdict changed to `REJECT`): refused, `(REJECT)`.
- RESULT null controls: the file absent gives `not on the roster branch or origin/main`; the carry with its cite removed gives `proposal-sourced text cites no triage ruling`.

All of these match the body.

## The three narrowings, against the tree

- **The owning group.** R10-ORCH-BEATD is `not-started` with 35 carries at origin/main and at the roster. Its brief owns "single-instance locks" and "the double start the design names cannot occur". Carry 22 is P97 (`DUPLICATE seat` in `pulse.py --seat-alive`), which covers standing seats only. `design/R10-ORCH-BEATD` is at round 3 (`f0f046929`), consistent with "design re-cut in progress". So it is verified that the orchestrator session is the one process neither the brief nor carry 22 names.
- **Narrowing 1** (liveness from the pid matched by command, never from stop lines). No stop-line mechanism exists in the tree (`git grep "stop line"` over tools and dev/governance finds nothing). The quoted header "A crash leaves no stop line" is in the out-of-tree `seat-launch.sh`. That one sentence of the premise I cannot re-derive. The logic holds independently: a reboot ends processes without running their exit paths.
- **Narrowing 2** (not `$PPID`). The measurement, four `sup=` pids dead while s10 lives, is from the out-of-tree launch ledger and `ps`. **Not re-derivable from this seat** (step 8).
- **Narrowing 3** (at resume, before the first dispatch). Its premise is the queue-file times: 10472 started 08:16Z and dispatched about 08:38Z, so the first dispatch came about 22 min after start. The arithmetic is consistent. The times themselves are out of tree and not re-derivable.
- **The P230 precedent.** `s6-batch45.md:208` rules DEFER to R10-ORCH-BEATD and says the out-of-tree sweep edit "is the orchestrator's to make (sent to it, not carried)". That matches this ruling's treatment of the same script. `git ls-files | grep -c 'seat-launch\|orch_sweep'` = 0, re-derived.

## Forward-carry (step 10)

The body routes `Carry: R10-ORCH-BEATD` with carry text that states the control as a precondition: before the first dispatch; liveness by pid and command; not stop lines or `$PPID`; the second session refuses and stops. That text is not yet on the roster, and this is by construction. `proposal-triage.md` says the triage seat does not edit the roster: the orchestrator routes an ACCEPT through `roster_edit.py`, and its triage gate refuses until this ruling is on origin/main or the roster branch, as the null control above shows. The orchestrator should append it at merge.

## Red checks (step 11)

All 55 check runs at the head are completed, and none is a failure (`ev/ci.txt`). The body's `none` holds.

## Not verified

The figures from the orchestrator's state directory are out of tree and not re-derivable by this seat (step 8): ORCH-QUEUE.md:5002, launch-ledger lines 53-61, seat-ledger.md:1058, and the `ps` readings. "Every other id up to V149 has a ruling" rests on `proposals.md`, which is not in the tree. Not verified.

## Findings

- "About 28 minutes of two live sessions (08:16 to 08:44Z)": by the entry's own times the overlap is 08:19 to 08:44, about 25 minutes. The 28 includes 10472's first 3 minutes alone. The binding is unaffected. Carry: dismissed: wording only; the cost conclusion does not move

## Evidence

- `ev/head.txt`: the head, branch tip re-read, merge base, merge-tree rc=0, diff stat.
- `ev/mutation.txt`: the RESULT lines above.
- `ev/tree-claims.txt`: the R10-ORCH-BEATD stage, carries, brief phrases and carry 22; the `ls-files` count; P230; the design branch.
- `ev/ci.txt`: every check run at the head.
