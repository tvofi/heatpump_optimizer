# `shims/seat-gh`

- `shims/seat-gh` — installed as `gh` by `seat_venv.sh --install-shims <dir>`.
  Appends `<utc> <parent pid> <parent command, 80 chars> <subcommand> <target>`
  to `$HPO_STATE_DIR/gh-calls.log` (target: the api path with its query cut, or
  the `pr`/`run` verb), never a flag's value or a body (the parent command is redacted from its first value-bearing flag, `-f`, `--body`, `--field` and the rest of the census, to the end of the line, the flag name kept); a token outside
  `[A-Za-z0-9_./:-]` is logged `?`. Then execs the first real `gh` on `PATH`
  (a regular executable without the line-2 marker `# hpo-gh-shim`): stdin,
  stdout, status and signals are its own. A missing state directory is created; a log it cannot write is skipped. Past
  `HPO_GH_LOG_MAX` bytes (default 1 MiB) the log moves to `gh-calls.log.1`.
  Refusal: no real gh, `gh shim: no real gh on PATH`, rc 127. When: the shared
  token's core bucket is spent and no host log names the caller (P284). Tested by
  `gh_calls.py --self-test`.
