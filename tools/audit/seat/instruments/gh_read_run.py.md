# `gh_read_run.py`

- `gh_read_run.py` — runs one `gh` read under `gh_read.py`'s rule, for a
  workflow step with no Python of its own: `python3 -I
  tools/audit/seat/gh_read_run.py gh api <path> --jq <filter>`. When: a
  `gh api` read in a workflow, which a pinned job restores from the base
  (`gh_read.py` beside it; pr-contract.yml's reads are its first users). It writes the answering read's
  stdout once, so a retried `--paginate` prints no page twice, and each
  settle on stderr. Refusal: a non-transient failure after its one read, or a
  spent budget, exits with the last read's code and writes its stderr, with
  the attempt count on the last line; an argv `gh_read.is_read` does not call
  a read is never run (exit 2). `--self-test` runs offline.
