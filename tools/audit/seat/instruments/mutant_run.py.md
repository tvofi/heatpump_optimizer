# `mutant_run.py`

- `mutant_run.py` — the tracked mutant driver. `--spec mutants.json --cmd
  '<argv>'` takes a list of {name, file, old, new}, runs an automatic NULL
  mutant first (it must print `SURVIVED NULL`; `KILLED NULL` is a broken
  command, rc 3) and prints one `KILLED|SURVIVED name` line per mutant.
  `--diff <base>...HEAD --cmd '<argv>'` mutates the ADDED Python lines with
  GUARD_OFF, RETURN_DEL, CMP_BOUND, CALL_DEL, CONST_SWAP and STMT_DEL (a whole simple
  statement, however many lines, becomes `pass`), and prints one
  `SURVIVED file:line OPERATOR` line per survivor (rc 1; `--report-only` rc 0;
  `--max-mutants N` caps the pass; `--list` prints the mutants without running).
  Mutants run in a `git archive` copy by default (`--copy-tree`), so a kill
  cannot leave production mutated; `--in-place` writes into the working tree
  under `dev/audit/harnesses/mutant_guard.py` for a command the #363
  `recorded_at` check would fail in a copy. SIGTERM and SIGINT kill the
  command's process group and restore. When: a mutation proof over several
  mutants, or a fixer checking that the group's self-test pins the lines the
  diff adds; `tools/pr/prepr.sh` runs the diff arm report-only when
  `MUTANT_CMD` is set (`--in-place` under `MUTANT_IN_PLACE=1`), and refuses a
  run that measured nothing (rc 2 or 3) rather than reading it as no survivor. Refusal, rc 2, before anything runs: a malformed spec, a
  repeated name, an `old` not occurring exactly once, a target differing from
  HEAD. A survivor is answered in the PR body; an equivalent one still owes a
  `survivor_triage` record. The command's family (its session, its process group, any
  process carrying the run's `MUTANT_RUN_TOKEN` environment mark, and every descendant of
  the driver, which is a child subreaper while the command runs, so a descendant that left
  the session, cleared its environment or was orphaned is still counted) is polled every 0.5 s and SIGKILLed whole, also at the
  command's exit and on a signal, past `--fork-cap` processes (default 256): `FORKCAP name` or
  `FORKCAP file:line OPERATOR`, never KILLED (the cap proves no test pins the
  mutant); a diff run with one exits 1. `--self-test` builds throwaway repositories.
