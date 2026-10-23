Fix review: merge 4547d59da65e6548c76b1d6291e078d8823ea174
bus-nonce: 933687ba87372c41ad57866753493fb2

Round 1. Measured at head `4547d59da65e6548c76b1d6291e078d8823ea174` (still the head at post), detached worktree; merge base `d7cb63508`, origin/main `25816d5eb`, roster origin/handoff/audit-r10-roster `e267cd102` (body read `222cd5278`). Role contracts under `dev/governance/roles/` unchanged between merge base and origin/main.

## RESULT lines

- RESULT diff: 2 files, `dev/programme/triage/s5-batch2.md` (new, under INERT `dev/programme/`) and `dev/programme/delivery/2672.md` (own row). VERSION, manifest and notes heading untouched.
- RESULT shape: 8 entries P34-P41, each with `Verdict:`, `Source:`, `Instances:`, `Cost:`, `Binding:` per `proposal-triage.md`; 3 ACCEPT / 3 DEFER / 2 REJECT (body's enumerator, re-run).
- RESULT gate: `roster_edit.ruling_verdict` reads P34..P41 as ACCEPT, ACCEPT, DEFER, DEFER, REJECT, REJECT, ACCEPT, DEFER; P42 None. `triage_refusal` passes `#P34`, `#P35`, `#P40`; refuses `#P36` (DEFER) and `#P38` (REJECT). Mutant P34 ACCEPT->DEFER: refused. Null control and mutation claim in the body reproduce.
- RESULT destinations: every ACCEPT/DEFER group exists and is not done at both `222cd5278` and `e267cd102`: R10-TRAIN-OVERLAP-GRADE (queued), R10-ORCH-ROSTER-SCHEMA, R10-FLY-CARRY-DISPOSITION, R10-FLY-OPENPR-ATOMIC, R10-FLOW-TOOLKIT-MODEL, R10-ORCH-BEATD (not-started), R10-UPDATE-PR-SIGNALS (in-progress). Cited carry indices match their text at `222cd5278` (TRAIN-OVERLAP-GRADE 1-2 park on "base branch policy prohibits"; ORCH-ROSTER-SCHEMA 3 stage set, 5 triage gate in roster_edit.py; ORCH-BEATD 0 supervisor; OPENPR-ATOMIC 1 / UPDATE-PR-SIGNALS 2 worktree detach at source; FLOW-TOOLKIT-MODEL 6 XS; CARRY-DISPOSITION 0 bus.sh dispatch, 1 lost-ask, 3 carry_audit items(); its brief carries the orchestrator `Carry: dismissed` route P41 relies on).
- RESULT carries: the three ACCEPT carries are not yet on the roster (0 `s5-batch2.md#P` citations at `e267cd102`), as the file states: `roster_edit.ruling_reader` resolves a ruling only from the roster branch or origin/main, so routing follows this merge by the orchestrator (`proposal-triage.md`: "The orchestrator routes an ACCEPT"). Not a finding-propagation miss.
- RESULT tree claims re-derived: `self.required()` default `pr_head=False` at merge_train.py:1279 (`one`) and :1830 (`_batch`); only `main`'s `classify` passes `pr_head` (:3991); `PR_ONLY` and its "green at every head the batch admits" comment at :417-421; `freeable` requires HEAD == origin/<br> (:728); `rg carry_audit bus.sh` empty; `finding_rows` reads every VERDICT comment; `sizes_hours` = L,M,S,XL and replan.py:325 indexes with no fallback; `fetch_origin` has no retry; `HEARTBEAT_SECONDS` present.
- RESULT P39 count: 28 of 283 first-parent merges since 2026-10-16 at `d7cb63508` touch a reporter input (body's loop, re-run): matches.
- RESULT not re-derived: log-cited instances (`merge-report.txt`, `state-beat.log`, `roster-report.txt`, `wt-sync.log`, `plan.json`, `patch-6371729358/`) are out of tree in the s5 scratch directory; I could not read them.
- RESULT contract: `carry_audit.py pr 2672`: 3 items, 3 routed, 0 unrouted, 0 bad, rc 0. `pr-contract` success at 20:11:20Z, after the last red concluded.
- RESULT checks: one red, `delivery-status` (OVERDUE, 6 overdue rows #2647, #2655, #2652, #2651, #2650, ...): main's, since the diff touches only its own added row and no reporter input; no answer owed. Same red at the prior head `cb479c42b`.
- RESULT merge-tree vs origin/main: rc 0, no conflict.

## Non-blocking notes

- P34 names `Train.batch`; the caller at :1830 is `Train._batch`. Location is otherwise exact. Carry: dismissed: naming slip, the cited `rg` command finds both call sites
- P37 rules DEFER while the ruling it cites, `s5-batch1.md#P23`, is ACCEPT (carry 6; no op owed); both route to R10-FLOW-TOOLKIT-MODEL carry 6 and neither owes a roster op, so the gate outcome is the same. Carry: dismissed: no routing difference, nothing cites #P37 as an ACCEPT
