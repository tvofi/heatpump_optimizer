# `gh_calls.py`

- `gh_calls.py` — the reader of the `shims/seat-gh` log. `--top [--since <utc>]
  [--limit N] [--log PATH]` ranks parent commands and `gh` endpoints by count
  over the host-wide log the shim writes (`$HOME/.local/state/hpo/gh-calls.log`) and a distinct `$HPO_STATE_DIR/gh-calls.log` an older shim left, each with its `.1`, ending in a `sources:` table of each log's count when more than one holds calls; a malformed `--since` is refused (rc 2). `--coverage
  [PID ...]` reads `/proc/<pid>/environ` (Linux) of each pid, or of every known
  daemon process, and says whether the first `gh` on its `PATH` is the shim.
  `--self-test` drives the shim against a stub gh: the byte, stderr and status
  arms, no value in the log, exact parent-field arms over the real `ps` and over a fake `ps` (code, stdin-script, value-taking and unknown options, `=` cleaning, the 80-character cut) with a mutant per field rule, an unwritable-log null control, rotation, and the
  mutant with the exec pass-through dropped. Blind spots: cloud seats share the
  token from another host; `record_row.py`'s direct urllib read is not counted.
