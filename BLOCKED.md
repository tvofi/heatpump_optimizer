# BLOCKED: r10-body-contract-p2 body push

Code is complete and pushed to handoff/r10-body-contract-p2 at 95a5cca4fe03875b2bcf02fd882db327d2aa9744
(prepr.sh rc=0 on that head with the body). The body is kept at refs/heads/handoff-wip/r10-body-contract-p2-body.

`body_push.sh` refuses it: three Forward-carry items (card 7 remainder, fold-grammar `pr` wiring, legacy
control files) name `Carry: R10-BODY-CONTRACT`, and CARRY-MISSING says they are not yet in that group's carries.
Landing them is a write to the round's roster branch, which this seat may not make.

Question for the orchestrator: run `carry_audit.py land-ops --body <body> --topic r10-body-contract-p2`
(three `append-carry R10-BODY-CONTRACT` ops) on the roster branch, then re-run
`bash tools/audit/seat/body_push.sh r10-body-contract-p2 <body from the kept ref>`.
Owner ruling carried by item 1: may pr-contract run PR-authored figure commands.
