# `session_yield.py`

- `session_yield.py` — decision 0018 section 3's three session reads
  (R11-NO-READ-BUILDERS-C, part C of the R11-PRE-NO-READ-BUILDERS design):
  loads per rule (card E11-N-RULE-YIELD), each instrument refusal with its
  outcome (card E11-N-INSTRUMENT-YIELD), and a run line per Workflow call
  (card E11-N-GATE-CAUSE). It walks the transcripts through
  `token_ledger.sessions()`, subagent files included, and writes nothing. Its
  rules and null controls are the script's docstring; the command is:

      python3 -I tools/audit/seat/session_yield.py --projects <claude project dir> \
        [--cloud-projects <dir>] [--since ISO] [--until ISO] [--repo <checkout>]

  A refusal is an attributed non-zero exit or a hook denial, never a wording;
  `usage`, `crash`, `not-run`, `killed`, `deferred`, `unread`, `masked` and
  `marked at exit 0` are scope rows beside it, each counted. A class given no
  directory prints `NO-READ`, never 0: on the host that is the cloud class.
