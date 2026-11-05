# BLOCKED: body_push.sh cannot complete without a roster-branch write

Code head 5471917b846176500a023b1e9816afd5e4416bd3 is on handoff/r10-body-contract (origin/main 6125b263d merged; prepr: only the environmental `closures` REFUSE, red on main too).
The body (PR-BODY.md here) passes the pr-body lint, figures and ref_privacy. It is refused at the carry-landing step:
`CARRY-LANDED: 11 missing` -- each Forward-carry item and each unbuilt "Carry N" line must be in R10-BODY-CONTRACT's brief on handoff/audit-r10-roster (cfe7c09b0), by `carry_audit.py land-ops`. This seat may not write that branch.
Question for the orchestrator: land the 11 items (run `python3 tools/audit/carry_audit.py land-ops` against PR-BODY.md), then re-run `bash tools/audit/seat/body_push.sh r10-body-contract PR-BODY.md`; or rule that the unbuilt items be restated as `Carry: <other live group>`.
The refused body is also kept at refs/heads/handoff-wip/r10-body-contract-body (the new keep-ref working as built).
