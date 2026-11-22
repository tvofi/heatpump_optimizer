# `token_ledger.py`

- `token_ledger.py` — decision 0018 section 2's token ledger: every usage field
  of every seat, apart, keyed by group, role, dimension, model and seat
  (R11-PRE-TOKEN-LEDGER; the process convergence audit d5d7ff81, section 6 row
  a4). Its rules and null controls are the script's docstring; the commands are:
  - **The key a dispatch writes** (`cloud_dispatch.py` ends every prompt's first
    line with it; a local spawn writes it as its brief's first line):

        python3 -I tools/audit/seat/token_ledger.py header --role <role> --group <G> --model <m> \
          [--dimension <D>] [--seat <name>]

  - **The ledger** (the beat's `scorecard` row runs it daily before
    `round_metrics.py produce`, into the file `round_metrics.py`'s `tokens`
    line reads):

        python3 -I tools/audit/seat/token_ledger.py collect --projects <claude project dir> \
          --out <state>/scorecard/tokens.tsv

    `--seat-class cloud`, run inside a cloud seat on its own project dir, reads
    that session: the cloud class has no row on the host, so the `tokens` line
    prints unread, never a partial.
  - **Each field apart, per seat class and role:**

        python3 -I tools/audit/seat/token_ledger.py summary --ledger <state>/scorecard/tokens.tsv \
          [--since ISO] [--until ISO]

  - **Importable:** `sessions(project_dir)` yields each session's id, its own
    transcript and its subagent transcripts.
