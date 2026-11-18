# `daemonize.py`

- `daemonize.py` — detaches one long-running instrument from the session that
  started it: fork/setsid/dup2/execvp around any `-- CMD`, with the log's
  first line a banner naming the child pid, UTC time and full argv (the #2180
  lessons: banner first, unbuffered), append mode so relaunches extend one
  attributable file. When: a watch or sweep that must outlive its session —
  round 9 re-derived the wrapper in /tmp four times before this existed.
  Refusal: `--log` is mandatory and a non-existent `--cwd` aborts; no lock or
  pid bookkeeping — the printed pid and `kill` are the stop story.
