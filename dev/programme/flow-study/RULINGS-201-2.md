Posted as #201 comment 6319292851 (2026-10-21T15:05:45Z, read back identical).

Owner rulings R10-R15, round-10 flow plan, second set (tvofi, 2026-10-21), taken after the orchestrator's evidence. They extend comment 6318002897 (R1-R9). Basis: the study pack on branch claude/dazzling-gauss-7l3u2b, dev/programme/flow-study, FUTURE-STATE.md section 8 and STUDY.md K14-K17.

R10 Mandate: extended to round 10's stamp plus 48 h, by the separate MANDATE comment posted with this one. The mandate grammar needs a timestamp, so that comment carries a fixed date; the owner withdraws it 48 h after the round-10 stamp if that comes first.

R11 Andon watcher: once R10-FLOW-ANDON lands, the study session sets up a cloud scheduled task that checks the heartbeat ref every 15 min and notifies the owner when it is older than 20 min, with the owner's approval at that time.

R12 R10-ORCH-MACHINERY's design amendments in STUDY K17 are approved in its brief: two beat jobs (heartbeat, pitch), the ledger kind postmerge-owed, the handoff job carrying the body-only path and a freeze for every head with a live reviewer, dispatch recorded through bus.sh dispatch and workers.json, one is-main-red classifier, and one plan model shared with R10-PLAN-ARTIFACT. The fix reviewer checks them at build; no design round 4.

R13 The fall in real-catch blocks per reviewed PR (0.52 over the round's first six days, 0.15 in the 48 h before adoption) is investigated before any threshold relies on it: R10-FLOW-YIELD-PROBE, expedite. Until it reports, the review-strength guardrail reports the rate and trips on nothing.

R14 Stranded-handoff aging in the obligations ledger: 4 h to a DISPATCH line, 12 h to an owner flag.

R15 Standing cloud triggers: once R10-FLOW-DISPATCH lands, the orchestrator drafts the three per-role trigger prompts (Opus fixer, Opus reviewer, Sonnet fixer); the owner creates them.
