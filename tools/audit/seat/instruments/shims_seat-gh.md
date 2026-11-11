# `shims/seat-gh`

- `shims/seat-gh` — installed as `gh` by `seat_venv.sh --install-shims <dir>`.
  Appends `<utc> <parent pid> <parent, 80 chars> <subcommand> <target>`
  to `$HPO_STATE_DIR/gh-calls.log` (target: the api path with its query cut, or
  the `pr`/`run` verb), never a flag's value or a body. The parent is the caller's argv[0] basename and, for a shell or interpreter, at most one more word: its script or `-m <module>` as given, or the flag name alone of a `-c`, `-e`, `-s`, `--eval`, `--print` or `--command` option, attached code cut off. Known no-value letters are passed over; a known value-taking one (python `-W`/`-X`, shell `-o`/`-O`) ends the field unlogged, as does any other option, so a script after such an option is not named. The field is cleaned and cut to 80 characters. Residual, by design: argv[0] and a script path are logged, so a value placed in a path is logged too (`sh ./T=v/s` logs `sh ./T?v/s`). A token outside
  `[A-Za-z0-9_./:-]` is logged `?`. Then execs the first real `gh` on `PATH`
  (a regular executable without the line-2 marker `# hpo-gh-shim`): stdin,
  stdout, status and signals are its own. A missing state directory is created 0700 and the log is kept 0600; a log it cannot write is skipped. Past
  `HPO_GH_LOG_MAX` bytes (default 1 MiB) the log moves to `gh-calls.log.1`.
  Refusal: no real gh, `gh shim: no real gh on PATH`, rc 127. When: the shared
  token's core bucket is spent and no host log names the caller (P284). Tested by
  `gh_calls.py --self-test`.
  Comment guard (R10-RAISE-GATE-SHIM), deny by default: any call that could write a comment on a record
  issue (#201 or #3394: `budget_raise_gate.RECORD_ISSUES`, the shim's `trackers`, pinned by the self-test)
  is refused unless the caller is python running the tree's own `tools/pr/gh_comment.py`, resolved by
  real path (the installer bakes the path into the copy). Let through without it: a call on an explicit
  list of calls that cannot. `issue` view/list/status/create; `issue` comment/close/reopen/edit/delete/
  lock/unlock/pin/unpin/transfer/develop only with one target read as a plain number other than a tracker,
  under gh's own flag table (an unknown flag, a short-flag cluster or a second target is refused, so
  `close`/`reopen` `--comment`/`-c` are covered by the rule, not by name); `pr` unless a word reads as
  a tracker; `api` as a read (no field, no `--input`, GET, only an Accept header) or as a write that is not at
  `issues/<tracker>/comments`, not at an unreadable path, not at `issues/comments/<id>` and not graphql unless
  the document holds no `mutation`/`subscription` and is not read from a file; gh command groups with no
  issue-comment surface; everything else (an unknown subcommand, an alias, an extension, a leading flag
  but `--version`/`--help`) is refused. The number is read after dropping leading zeros, trailing
  slashes, query, anchor, one %-decoding, dot segments and upper-case letters (path segments are matched in lower case).
  Residual, by design (Carry: R10-RAISE-GATE-SHIM): the caller test reads `ps` args, which a caller
  writes, so `exec -a 'python3 <tree>/tools/pr/gh_comment.py' ...` passes as the poster. That is
  deliberate evasion, not a seat's habit, and has no fix in a ps-based parent check.
