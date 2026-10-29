# `ref_privacy.py`

- `ref_privacy.py` — the one owner of what a push may say about the host
  (#2310): `slug <path>` names a local path for a ref (`<root>-<rest>` under
  a named root, else `ext-<leaf>-<hash>`); `guard --ref R [--message M]
  [--commits REV [--over BASE] -C DIR]` refuses a ref name or commit message carrying the
  home directory, an account name, the uid, a session temp root or a host
  path, or a message carrying a tool's attribution (exit 3, the class named,
  the text not echoed); `--commits` reads what the push publishes first,
  `--over BASE` every commit REV adds over BASE; `--check` refuses a
  tracked file with a push site its `PUSHERS` registry does not name, and a
  `guarded` entry that calls no guard. When: before every push an instrument
  composes; a new pusher registers in `PUSHERS` in the same diff. Refusal: a
  push that would publish the host never runs.
