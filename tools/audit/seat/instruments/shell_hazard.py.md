# `shell_hazard.py`

- `shell_hazard.py` — refuses three shell hazards on the lines a branch ADDS to a
  tracked `tools/**/*.sh` (`--check [--base <ref>] [--head <ref>]`, `--self-test`).
  When: `prepr.sh` step 3f8 runs `--check` on every run (milliseconds); CI's
  `governance / instrument-self-tests` runs `--self-test`. Rules, each printed
  `path:line: rule: text -- repair`:
  `wc-compare`, a `wc -l|-c|-w` substitution compared as a string without
  `| tr -d ' '` (BSD `wc` on macOS pads; marker `# wc-raw: <reason>` for a compare
  that asserts the raw count on purpose);
  `wc-stub`, a stub script text (a `#!` line) calling `/usr/bin/wc` without
  stripping its padding first, so a self-test stub is host-independent: its output
  may not depend on how the host's program formats;
  `early-pipe`, in a `pipefail` file a pipe into `grep -q`, `grep -m` or `head`
  (SIGPIPE: the writer dies once it outgrows the pipe buffer, the pipeline reads
  141). Repair: a here-string; `|| true` or `# pipe-small: <reason>` passes.
  Existing lines are never judged. Limit: a count assigned to a variable and
  compared later is not seen, and the `pr_args.sh` GNU-only `sed -i` sites are not
  covered (macOS-only checks run on local seats; the paid macOS lane is refused).
