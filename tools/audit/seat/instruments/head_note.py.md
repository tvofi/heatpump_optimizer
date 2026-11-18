# `head_note.py`

- `head_note.py` (tools/pr/) — prefixes a note under a body's `## Head`
  heading, found as `checkPrBody`'s `sections()` reads it (outside a fence,
  `##`, whitespace, `Head`), never the first substring `## Head`.
  `app_push.sh --recarry`, `open_pr.sh`, `update_pr.sh` and `handoff_push.sh`
  write every head note through it. When: any new writer of a `## Head`
  note. Refusal: a body with no `## Head` heading exits 1, file untouched.
