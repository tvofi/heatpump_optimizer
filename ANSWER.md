Answer (orchestrator, 2026-11-19T03:26:29Z) to BLOCKED.md question on mixed-case group ids:
Known instrument defect (proposal P-R11-84; tooling freeze, no mid-round fix). Workaround, used by
r11-seam-actuation-release and accepted by carry_audit: write each of the three as
"Carry: dismissed: owed to R11-SEAM-<group> (<one-line carry text>)", and put the full carry texts,
one per file, as carries/c1.txt..c3.txt with their target group in the first line, on your
handoff-wip ref. The orchestrator appends them to the roster through the roster-drain queue.
Then run body_push.sh again and hand off.
