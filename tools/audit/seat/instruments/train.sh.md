# `train.sh`

- `train.sh` — one invocation shape for `merge_train.py batch`: the seat
  venv first on PATH — an absent venv refuses (naming `seat_venv.sh` to
  build it), it never falls back to ambient python, which on 3.11 refuses
  main's own nested-quote f-strings under `no-copies` — the child python
  unbuffered (`-u`, so a detached caller's log shows stops and SKIP/OVERLAP
  lines in real time), a pidfile refusing a second live train on the same
  state dir, log and exit code under the state dir (`train.log`, `rc`), and
  the recommended set (`RECOMMENDED` in `merge_train.py`: `--overlap`,
  `--approval-carry`, `--skip-bad`, `--free-holders`, `--bot-prs`,
  `--pre-flight`) on by default, each off with `--no-<flag>` (the old
  `--<flag>` spelling is a no-op), `--main-moved-tries N` passed through, the
  mandate from `--mandate`, else the state dir's one-line `mandate` file
  (`--no-mandate` turns it off), the effective set and mandate printed on the
  launch line, and the child run from the repository root when `--checkout` is
  absent (it once resolved to `tools/`). Foreground: the caller
  detaches and owns the schedule. When: every merge queue — the per-session
  scratch drivers this replaces duplicated the invocation, and one session's
  copy ran prepr under the wrong interpreter and refused a clean branch.
  Refusal: a live pidfile (take over only by removing it after checking the
  pid is dead). `--self-test` drives the five refusals and the child argv
  shape offline (missing required arg, live pidfile, unknown argument, the
  `--ignore-red` argv shape, the absent-venv refusal), the child's cwd on a
  launch without `--checkout`, and a bare launch's argv carrying no flag.
  `train.sh add <pr> <verdict> --repo R --state-dir D [--verdict-comment ID]
  [flags]` loads one pull request into that state dir's live train (its next
  batch) or, with none live, starts one with those flags. When: whenever a
  merge verdict is confirmed. Refusal: `ADD REFUSED #<pr> <rule>: <why>` from
  `Train.admit_add` (shape, open, base, carry, row, budget-raise, policy),
  and `one-train` beside a train.sh still closing; a pull request already
  queued is `ALREADY`, rc 0. One fcntl lock (`queue.lock`) orders every add
  against the train's drains and its close; never a second train.
