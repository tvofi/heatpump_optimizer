# `offline_spy.py`

- `offline_spy.py` — runs a seat instrument's `--self-test` under a
  throwaway HOME and counts what it reaches outside: socket connects and DNS
  lookups (refused), gh/curl/wget/ssh/scp/nc calls on PATH (refused), git
  calls whose target resolves to a URL remote, and the Python process's
  subprocess creations. On macOS it also runs under `sandbox-exec`, denying
  outbound IP and writes outside the temp directories. When: before wiring a
  self-test into CI, and when reviewing one. Refusal: a non-zero exit, or any
  network or remote-git call, per file.
