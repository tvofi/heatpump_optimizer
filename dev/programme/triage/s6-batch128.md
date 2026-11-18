# Proposal triage, session s12, batch 128 (P399)

The rolling batch after batch 127. Facts were read at origin/main `f2a015142`, at the roster branch `649f3ed84` and in the dispatch seat's ledger. The ledger is host-local, so another seat re-runs these commands only on the host that holds it.

## P399: fire-without-sources, cloud fires hand-built without session_context.sources

Verdict: ACCEPT narrowed. The benefit is measured, and one incident costs more than the build. The proposed form is changed. A renderer the orchestrator must remember to call fails exactly as the incident did: after a compaction, the orchestrator did not use the body `cloud_dispatch.py` already publishes. The check moves to where every fire passes, a PreToolUse hook on the `RemoteTrigger` tool. Destination R10-POLICY-ROLE-PACK (carries-open), which already owns `.claude/hooks/session-start.sh` and the rendered cloud prompt. This ACCEPT is not taken on the >10 % exemption.

Source: the orchestrator's queue line `s12-fire-without-sources`, 2026-11-07.

Instances (ledger `s9/seat-dispatch/ledger-standin.txt`):
- **Sourceless fires:** `grep -c REFIRED <ledger>` gives 7, all at 2026-11-07T01:55:33Z, each "first fire had no repo". Their first fires are ledger lines 357 to 363, from 00:28:48Z to 01:40:21Z: f-3262-r1, f-3241-merge, f-3264-r4, f-tml2-resume, f-3244-r6, f-3265-r2 and f-3232-body.
  - That is 7 of the 7 fires in that window, and 7 of the 12 `FIRED` lines dated 2026-11-07.
  - The queue line's "7 of 8" denominator was not found in the ledger.
- **Wall clock lost:** for each seat, the refire time minus the first fire time. The losses are 86.8, 86.8, 50.9, 49.7, 37.8, 15.7 and 15.2 min, which sum to 342.7 min, or 5.7 seat-hours. That corrects the queue line's "30-85 min, about 6.5 seat-hours".
  - The "about 20 s, last_run SUCCEEDED" detail is the queue line's. It was not re-read, because doing so needs the API.
- **Window rate:** the ledger has 342 `FIRED` lines since 2026-10-31. The 7 above are the only sourceless fires it records, 2.0 % of fires. The trigger is a compaction, which recurs: the rate is low across the window and 58 % on the day the trigger fired.
- **The body already exists:** `tools/audit/seat/cloud_dispatch.py` `render` at `f2a015142`, lines 320 to 325, builds `session_context` with `allowed_tools`, `model` and `sources`. Its self-test checks those three keys and the repo URL (lines 994 to 1015). So the defect is in the hand path, not in the renderer.

Cost:
- One hook script under `.claude/hooks/` of about 30 lines, plus a `RemoteTrigger` matcher in `.claude/settings.json`. It refuses a `create` or `update` whose `job_config.ccr.session_context` lacks a non-empty `sources` or a `model`. A driver test refuses a no-sources body, admits the `cloud_dispatch.py` render, and kills a mutant that drops the check.
- An S-sized part inside an existing group. There is no API call, and the standing cost is one local process per `RemoteTrigger` call.
- Both files are code-owned (`/.claude/hooks/` and `/.claude/settings.json` are `@tvofi` in CODEOWNERS), so the pull request needs the owner's review, or a mandate in force. Neither is a `policy_lint.mjs --budgets` row, and no `tests/structure_budgets.json` row covers them.
- Against that build cost, one incident lost 5.7 seat-hours.

Binding:
- Carry text: `From triage batch 128 (triage: dev/programme/triage/s6-batch128.md#P399 at <roster sha>): a PreToolUse hook on RemoteTrigger (matcher in .claude/settings.json, script under .claude/hooks/) refuses a create or update whose job_config.ccr.session_context has no non-empty sources or no model, and names the dispatch/<role>-<topic> PAYLOAD.json that cloud_dispatch.py publishes as the body to send. Driver test: a no-sources body refused, a no-model body refused, the cloud_dispatch.py render admitted; a mutant that drops the check is killed. First step: prove the orchestrator session loads the repo hook by a refused no-sources call in that session. Not a cloud_fire.py renderer: the published PAYLOAD.json is that renderer already.`
- The fixer re-reads the ledger figures at its own base and does not carry them.
