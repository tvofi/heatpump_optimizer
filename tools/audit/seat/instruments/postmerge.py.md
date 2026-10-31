# `postmerge.py`

- `postmerge.py` — the bookkeeping after a merge, run by `merge_pr.sh` and
  by the train's landing: the #201 line (`record_beat.py`), the roster stage
  (`roster_sync.py --apply`; a refusal prints `set-stage owed <group> <merge sha>`),
  `state_docs.py --push`, and main's suite state (`merge_train.py classify --main`).
  When: automatically after each merge; by hand with `--retry` once an OWED
  cause is gone, which closes the ledger event on a clean run. Refusals: a step
  that fails is printed `OWED <step>: <why>`, opens `postmerge-owed` for the pull
  request and its full merge sha, never undoes the merge, and makes the exit
  non-zero after every step ran. `--dry-run` prints the exact comment and commands.
