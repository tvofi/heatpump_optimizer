# `gh_calls.py`

- `gh_calls.py` — the reader of the `shims/seat-gh` log. `--top [--since <utc>]
  [--limit N] [--log PATH]` ranks parent commands and `gh` endpoints by count
  over the log and its `.1`; a malformed `--since` is refused (rc 2). `--coverage
  [PID ...]` reads `/proc/<pid>/environ` (Linux) of each pid, or of every known
  daemon process, and says whether the first `gh` on its `PATH` is the shim.
  `--self-test` drives the shim against a stub gh: the byte, stderr and status
  arms, no value in the log, an unwritable-log null control, rotation, and the
  mutant with the exec pass-through dropped. Blind spots: cloud seats share the
  token from another host; `record_row.py`'s direct urllib read is not counted.
