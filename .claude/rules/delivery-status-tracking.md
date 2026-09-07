---
description: Keep programme Delivery-status and #201 current after each merge
paths:
  - "docs/plan*.md"
  - ".claude/workflows/*-groups.json"
  - "docs/HANDOVER.md"
---
# Programme tracking discipline

After each programme merge — wave group, tooling the plan tracks, or a closed tracked issue — update tracking in the **same session** or an **immediate record PR**:

1. **`docs/plan-2026-09-open-issues.md` Delivery-status table** — authoritative vs wave body; if they disagree, fix the table first.
2. **`.claude/workflows/wave-*-groups.json` `resume` fields** — match measured `origin/main` (merged PR SHAs, open PR heads).
3. **GitHub issue #201** — one comment per meaningful state change (merge, block, wave start); not a heartbeat.
4. **Every PR the programme has opened**, not only the ones a roster predicted. Wave stages and their records already have a home. Hotfixes, instrument repairs, harness lanes, policy, and anything found *while doing something else* have none — and they are often the most consequential work of a session. Give that kind **its own row and section**; do not force it into a wave it does not belong to.
5. **Every open issue**, with a disposition: **scheduled** into a wave or group, **deferred** with a reason, or **refused** with a reason. **"Not mentioned" is not a disposition** — an issue absent from the plan is work nobody has scheduled, refused or deferred on the record. Re-check the whole list at each record, not only when this session filed something: list open issues, grep the plan for each number.

## Status stays true, not just present

- An issue **delivered** is closed naming the PR and the release that carried it, with its residuals recorded rather than swept.
- A PR's **body describes its current head**, not the head it was opened at. A stale body has blocked a review here for paperwork alone.
- **Continuously means at each merge**, not at session end. The record PR that carries a merge carries this too, so it costs no extra PR — and batching to the end is how an abort loses it.

Do **not** wait for a stamp to truth the table. Never touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading in a branch.

Measure with `git fetch origin main`, `gh pr list --state merged`, `git log origin/main`, and closed issues — do not invent.
