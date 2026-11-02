# `mutant_run.py`

- `mutant_run.py` — the tracked mutant driver. `--spec mutants.json --cmd
  '<argv>'` takes a list of {name, file, old, new}, runs an automatic NULL
  mutant first (it must print `SURVIVED NULL`; `KILLED NULL` is a broken
  command, rc 3) and prints one `KILLED|SURVIVED name` line per mutant.
  `--diff <base>...HEAD --cmd '<argv>'` mutates the ADDED Python lines with
  GUARD_OFF, RETURN_DEL, CMP_BOUND, CALL_DEL and CONST_SWAP, and prints one
  `SURVIVED file:line OPERATOR` line per survivor (rc 1; `--report-only` rc 0;
  `--max-mutants N` caps the pass; `--list` prints the mutants without running).
  Mutants run in a `git archive` copy by default (`--copy-tree`), so a kill
  cannot leave production mutated; `--in-place` writes into the working tree
  under `dev/audit/harnesses/mutant_guard.py` for a command the #363
  `recorded_at` check would fail in a copy. SIGTERM and SIGINT kill the
  command's process group and restore. When: a mutation proof over several
  mutants, or a fixer checking that the group's self-test pins the lines the
  diff adds; `tools/pr/prepr.sh` runs the diff arm report-only when
  `MUTANT_CMD` is set. Refusal, rc 2, before anything runs: a malformed spec, a
  repeated name, an `old` not occurring exactly once, a target differing from
  HEAD. A survivor is answered in the PR body; an equivalent one still owes a
  `survivor_triage` record. `--self-test` builds throwaway repositories.
