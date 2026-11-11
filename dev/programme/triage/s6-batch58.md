# Proposal triage, session s7, batch 58 (P271-P272)

Two records, owed since batch 57 (#2932) closed to new rulings. Each records an owner decision
taken on 2026-10-28 against a ruling already made, P266 (`s6-batch55.md`) and P270
(`s6-batch57.md`). Neither moves those files, and neither depends on #2932's review. Facts were
read at origin/main `b0b2d7697f8c5baaef2c082d9bf3242b57249e68` and at the live roster
`origin/handoff/audit-r10-roster` `54bd827cff96326accff903d1ce159df725df855`.

## P271: P266 owner answer: superseded-run cancelling covers CP and hotfix PRs

Verdict: ACCEPT, as P266 ruled it. The owner's answer confirms P266's scope, and no carry changes.

Source: the orchestrator's DECISION-OWED on P266, answered by tvofi on 2026-10-28, verbatim:
"keep cancelling them, yes". The question was whether the superseded-run sweep cancels the
superseded runs of critical-path and hotfix PRs too.

Instances:
- The answer as relayed: `~/hpo-orch/r10s6/proposals.md`, the `## P266 owner ruling` line after
  the V184 entries, and `seat-ledger.md:2094` (triage s7, 20:50:35Z, NOTED).
- What it binds. The sweep cancels a superseded run on any open PR, CP and hotfix included. A
  run at a PR's live head is never superseded, so it is never cancelled. A run on main is never
  cancelled. This is what P266, P267 and P268 already say: the sweep honours only the setting's
  `never_cancel` for the main push, and the R10-FLY-CANCEL-SWEEP brief reads that same field.
- Held texts unchanged: `groups/R10-FLY-CANCEL-SWEEP.json` (append-group, held until batches 55,
  56 and 57 are on main) and the b56/b57 carry files under `s7/carries/` already state that scope.

Cost: none. No carry, no roster op and no code.

Binding: owner-directed. The answer closes the DECISION-OWED without changing a ruling.

## P272: P270 owner order: the V184 cache gaps are built as four owner-ordered fly-ins

Verdict: REJECT, for P270's own candidate carry (reorder the cloud prompt, stable text first,
into R10-FLOW-DESIGN-STAGES). The V184 measurement refutes it. The fixes that are built are
owner-ordered and do not rest on this file.

Source: `proposals.md` V184 and its measurement (cache-gap seat, 2026-10-28T20:40Z, raw in the
orchestrator's `scratchpad/cache/`). The owner order (tvofi, 2026-10-28), verbatim: "fix cache
proposals 1-6 asap" and "also fix the side defects".

Instances:
- **The measurement (`~/hpo-orch/r10s6/proposals.md:1009-1011`).** It ranks the gaps in input-token
  equivalents per day:
  1. Seat waits of 5-15 min outlast the 5-min subagent cache TTL: ~45-55M. Fix: cap in-seat waits
     at 270 s or less. The 300 s defaults sit at `tools/audit/seat/ci-watch.sh:290` (`sleep 300`),
     `tools/audit/seat/merge_train.py:486` (`POLL_SECONDS = 300`) and `tools/pr/prepr.sh:2549`
     and `:3285`.
  2. The orchestrator runs near the 900k autoCompactWindow: ~20-25M. Fix: compact at ~400k.
  3. The plugin catalog, ~35k tokens, is written into every seat: ~20-25M. Fix: a tools
     allowlist on seat agents, and unused plugins disabled.
  4. RemoteTrigger echoes each payload 7 times: ~5.8M. Fix: a haiku seat fires it, or a pointer
     prompt to `dispatch/<role>-<topic>`.
  5. Large tool outputs (prepr, whole-file `cat`): ~3-5M avoidable.
  6. Seats re-read `CLAUDE.md` and `INSTRUMENTS.md`: ~2M.
  - Refuted: fixed brief boilerplate and brief ordering. That is P270's candidate carry.
  - Side defects: plugin hooks exit 127 (an unquoted path with a space), and the project Stop
    hook never runs for the orchestrator (a relative hook path).
- **The four fly-ins the owner ordered.** As queued, `s7/roster-queue-s7.txt:175-178`:
  - R10-FLY-CACHE-PROMPTS (S): "owner order 2026-10-28 cache gaps 1,4,6 + stop hook".
  - R10-FLY-PREPR-SUMMARY (S): "owner order 2026-10-28 cache gap 5".
  - R10-FLY-INSTRUMENTS-SPLIT (M): "owner order 2026-10-28 cache gap 6".
  - R10-FLY-SWEEP-DEFAULTS (S): "owner-ruling 2026-10-28 sweep defaults into sweep_template.md".
- **Their briefs cite the owner order, not this file.** `roster_edit.py`'s triage gate
  (`triage_refusal`, line 466) refuses a text citing a ruling whose `Verdict:` is not ACCEPT.
  P270 reads DEFER and P272 reads REJECT, so a brief citing either would be refused. A brief
  that names the owner order cites no ruling and passes.
- **Not on the roster yet.** None of the four groups is on roster `54bd827cf`. All four queued
  `append-group` lines are `#refused`: each passes free text where the op takes a group JSON path
  (`seat-ledger.md:2088-2089`, "unreadable JSON: [Errno 2] No such file or directory"). This is
  the roster seat's to repair, with a group JSON per fly-in.
- **Overlap.** R10-FLY-CACHE-PROMPTS shares `tools/audit/seat/cloud_dispatch.py` with
  R10-FLOW-DESIGN-STAGES. They work different seams of it: the prompt text and dispatch pointer
  against the design-stage templates. By this ruling, R10-FLOW-DESIGN-STAGES takes no reorder
  carry from P270.
- **Not in any queued text.** Gap 2 (compaction) and gap 3 (plugin allowlist) are session and
  harness settings, not tree changes. The plugin-hook exit 127 lives in a plugin's own path. The
  orchestrator holds all three under the owner order.

Cost: none from triage. The reorder carry it rejects was estimated in P270 at about 30 lines and
one prefix-identity check.

Binding: the measurement. The ordering arm's benefit is refuted, so it fails the bar, while the
measured gaps are already owner-ordered.
