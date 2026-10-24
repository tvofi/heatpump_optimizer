# R9-ROW-STALE: the delivery row's status decayed while the record beat could not legally rewrite it

**Instances (three in round 9).** #2111 established that a merged pull
request's row kept reading `**open**` (the row's status is part of what it
records); #2150 regenerated three drifted rows from REST facts; #2176 found
12 merged rows reading `**open**` with `tests/delivery_status.py` counting
them as rowed.

**Named cause.** `automerge_refusals` refused every file whose status was not
`added`, so a beat carrying the open→merged rewrites its own planner produced
could never automerge; because the hold in `tests.yml`'s record job engages
only on a guard pass, every push to main rebuilt and force-pushed
`record/autofix` (25 rebuilds, one dismissed approver review), and the stale
rows accumulated under a green reporter.

**Process state: (c)** — the process was followed and did not produce the
intended result. The guard was obeyed; it pinned the wrong shape (it refused
the exact rewrite the beat was designed to plan).

**Cost test.** cost(countermeasure) = the `modified_lines`/`_rewrite_refusal`
pair in `tools/audit/seat/record_row.py`, no new check, no standing CI cost —
it runs only inside the beat that already runs. cost(defect) = one manual
docs pull request per stale-row batch (#2150, #2177) plus a red `delivery-status`
on main per occurrence, P(recurrence) = 3 instances in one round and rising
with merge rate. The countermeasure pays: the beat now clears its own rows
(#2151's 12 rewrites landed under the fixed guard; #2182 regenerated the
27 pre-beat rows).

**Countermeasure and demonstration.** The rewrite arms are mutation-proven
both ways in #2176's body (each arm reddened by reverting exactly its own
fix; the live null control showed the guard refusing origin/main's shape on
#2151's real head and passing at the fix). The reporter half
(`tests/delivery_status.py`'s `open_anchored`/`classify`) is demonstrated by
the live before/after count: 49 rowed/8 pending/1 overdue unfixed → 37 rowed/
12 pending/9 overdue fixed — the red that followed was the fix working.

**Class citation.** Add an `R9-ROW-STALE` class to `dev/audit/config/bugclasses.json`
citing this file; the three-instance threshold is met and the audit-class
rule asks for the barrier to be named, not just built.
