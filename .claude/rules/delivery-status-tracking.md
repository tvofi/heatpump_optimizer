---
description: Keep programme Delivery-status and #201 current after each merge
paths:
  - "docs/plan*.md"
  - ".claude/workflows/*-groups.json"
  - "docs/HANDOVER.md"
---
# Programme tracking discipline

After each programme merge — wave group, tooling the plan tracks, or a closed tracked issue — update tracking in the **same session** or an **immediate record PR**:

1. **The Delivery-status record** — the plan's frozen table plus one `docs/delivery/<N>.md` per PR; authoritative vs wave body; if they disagree, fix it first.
2. **`.claude/workflows/wave-*-groups.json` `resume` fields** — match measured `origin/main` (merged PR SHAs, open PR heads).
3. **GitHub issue #201** — before each PR, merge or release, coordinate here; not a heartbeat.
4. **Every PR the programme has opened**, not only the ones a roster predicted. Wave stages and their records already have a home. Hotfixes, instrument repairs, harness lanes, policy, and anything found *in passing* have none. Give that kind **its own row and section**; do not force it into a wave it does not belong to.
5. **Every open issue**, with a disposition: **scheduled** into a wave or group, **deferred** with a reason, or **refused** with a reason. **"Not mentioned" is not a disposition** — an issue absent from the plan is work nobody has scheduled, refused or deferred on the record. Re-check the whole list at each record: list open issues, grep the plan for each number.

## Status stays true, not just present

- An issue **delivered** is closed naming the PR and the release that carried it, with its residuals recorded rather than swept.
- A PR's **body describes its current head**, not the head it was opened at.
- **Continuously means at each merge**, not at session end; batching to the end is how an abort loses it. A pull request writes its **own** row before the handoff, once its number exists, as `docs/delivery/<N>.md`: a line `- [#N](…/pull/N)` and its state. Never at the table's end: it conflicts every open branch, and past the freeze `policy_lint` refuses it. `fixer.md`'s freeze forbids a row added after, not before. A record pull request is for merges no branch rowed.

Do **not** wait for a stamp to truth the record. Never touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading in a branch.

Measure with `git fetch origin main`, `git log origin/main`, the merged pull requests and closed issues — do not invent.
