# `tmp_paths.py`

- `tmp_paths.py` — refuses a tracked script, workflow or decision record that
  depends on a temp or machine path (`--check`, `--self-test`). When: after
  touching anything under `tools/`, `tests/`, `.claude/`, or before pushing.
  Refusal: every match on its own line — a `/tmp` state name, a `$TMPDIR`
  with a fixed name, a home path, an instrument run from `~/`; the 2026-10-03
  temp cleanup deleted three tracked tools' state and one decision's design
  note. It also refuses a temp, home or seat-directory path on a
  `tests/mutation_ledger/` line the diff adds (a triage citing a probe no
  other seat can run); main's stock is not charged.
