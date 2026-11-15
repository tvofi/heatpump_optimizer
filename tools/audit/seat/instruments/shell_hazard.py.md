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

## The stub host-independence rule

A shell self-test stub of a host program (`wc`) first on `PATH` asserts on what the
stub prints, so the stub's output may not depend on the host's formatting: BSD `wc`
already pads its count to width 8, and a stub that prefixed padding to the host's
output doubled it on macOS and not on Linux CI (`R10-RCA-PREPR-DARWIN-SELFTEST`).
A stub normalises the host's output (`| tr -d ' '`) and then shapes it. A stub that
calls the host program by absolute path is out of reach of a `PATH`-level emulation of
another host; bind-mount over `/usr/bin/wc` to emulate BSD. `wc-stub` and `wc-compare`
refuse the two shapes on added lines.
