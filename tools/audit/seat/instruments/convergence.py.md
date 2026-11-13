# `convergence.py`

- `convergence.py` — the round's convergence record: per dimension found,
  fixed, injected and escaped, each over its denominator, from
  `rotation.json` and the roster's `cause` field. Path:
  `tools/audit/convergence.py`. When: closing a round (`record` writes
  `dev/audit/config/convergence.json`; `orchestrator.md` section 13), or
  reading whether a barriered class recurred (`recurrence`). Refusal:
  `check` and `record` exit 1 on a done defect group with no well-formed
  `cause`; `record` refuses a differing overwrite without `--replace`.
  `--self-test` plants each refusal beside its passing twin.
