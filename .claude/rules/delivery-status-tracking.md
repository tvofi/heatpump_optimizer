---
description: Keep programme Delivery-status and #3394 current after each merge
paths:
  - "dev/programme/plan*.md"
  - ".claude/workflows/*-groups.json"
  - "dev/programme/HANDOVER.md"
  - "dev/programme/delivery/**"
---
# Programme tracking discipline

After each programme merge — wave group, tooling the plan tracks, or a closed tracked issue — tracking is updated **at that merge**, never batched to session end, where an abort loses it:

1. **The record is the pull-request list and #3394**: `tools/audit/seat/postmerge.py` posts one #3394 line per merge from its fixed template. No seat writes a per-PR `dev/programme/delivery/<N>.md` row (card C5, tvofi 2026-11-05: the rows and the `governance / delivery-status` grader produced more blocked rounds than catches). Nightly's `record-autofix` beat still rows each merge from API facts, because `tools/release/stamp.py`'s flush and `--require-rows` read those rows (orchestrator ruling 2026-11-08, until R10-FLY-STAMP-FLUSH-COST retires them).
2. **`.claude/workflows/wave-*-groups.json` `resume` fields** — match measured `origin/main` (merged PR SHAs, open PR heads).
3. **Issue #3394** — before each PR, merge or release, coordinate here; not a heartbeat.
4. **Every PR the programme has opened**, not only the ones a roster predicted, is read from the pull-request list; hotfixes, instrument repairs and anything found *in passing* are never filed under a wave they do not belong to.
5. **Every open issue**, with a disposition: **scheduled** into a wave or group, **deferred** with a reason, or **refused** with a reason. **"Not mentioned" is not a disposition**: an issue absent from the plan is unscheduled work.

## Status stays true, not just present

- An issue **delivered** is closed naming the PR and the release that carried it, with its residuals recorded rather than swept.
- A PR's **body describes its current head**, not the head it was opened at; a stale body is a reviewer's note the orchestrator resolves at merge, not a block (card C5).
- An owner's ask in a verdict or a body goes into the roster at the merge (`roster_edit.py`), so a non-blocking carry note cannot drop it.

Do **not** wait for a stamp to truth the record. Measure from `origin/main`, merged pull requests and closed issues; never invent.
