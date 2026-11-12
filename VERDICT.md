Fix review: merge 34dae66f17d5b511646ff51f3607d0fa6110bbfe

bus-nonce: 273b4935bcd5ca46366a97ad3328ef58

## Scope

Round 5 (later round over reviewed head 7572aa0aa878e55d8480264d8f0bcd927c6280aa, blocked findings-unresolved). Scope is the delta `git diff 7572aa0aa878 34dae66f17d5` and the previous verdict's two findings. The delta is one branch commit (20f47ffe1b, test-only: `pulse.py` self-test case, `seat_gen_selftest.py` two checks) and a merge of origin/main d1def1ea6307 whose only conflict, `beat_jobs.py` `ROWS`/`RUN`, is resolved by keeping both `loop-cwd` and `scorecard`. The delta touches no `custom_components/` path, so nothing widens the scope (fix-review.md step 12). The re-cut owed from the fourth round is present: `## Re-cut` in BODY.md.

## Findings

- Follow-up: the new `ps_start` check runs on `os.getpid()`, a process about 0 s old, so `ps -o etimes=` is 0 and a sign-flip mutant (`int(now) + int(etimes)`) survives (`ev/extra_mutants.txt`, `SURVIVED ps_start_plus`). The previous verdict's named mutant (`ps_start_zero`) is killed, and the start field `lock` writes into `session.lock` has no in-tree reader (`lock` parses only `split()[0]`), so no behaviour hangs on the sign today; a check on a long-lived pid (`os.getppid()` or pid 1) would kill it. Carry: dismissed: the start field has no in-tree reader and the named mutant is killed; a reader that consumes it must pin the sign with it

## Evidence

- Previous findings: both resolved by a killing test, as the round-4 block allowed. `mutant_run.py --spec` (copy-tree) with the body's `cmd.sh`: at 34dae66f17d5 `SURVIVED NULL`, `KILLED pulse_gen_read_off`, `KILLED ps_start_zero`; at 7572aa0aa878 `SURVIVED NULL`, `SURVIVED pulse_gen_read_off`, `SURVIVED ps_start_zero` (`ev/mutants.txt`). The repair is what moved them.
- The body's full 11-mutant spec, re-run by me at the head: NULL survived, all 11 KILLED, rc 0 (`ev/fullspec_mutants.txt`); matches the body's Mutation proof output line for line, so the proof is taken at this head.
- Adversarial extra mutant on the `read_alive` gen read (`sd = None` before `if sd:`): KILLED (`ev/extra_mutants.txt`).
- Self-tests at the head (`ev/selftests.txt`): pulse 70 checks 0 failed; seat_gen 25 checks 0 failed; beat_jobs 211 checks 0 failed (covers the merge-resolved `ROWS`/`RUN` tables); open_driver 93 checks 0 failed; `tests/structure.py` STRUCTURE RATCHET PASSED.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` at the head under venv-ci: `ALL 2709 ENTITY CHECKS PASSED`, rc 0 (`ev/entities.log`; its 50 `  FAIL` lines name planted fixtures (`sensor.x`, `secret-token`) and the run's own summary and exit code count them as passing controls).
- `git merge-tree --write-tree origin/main 34dae66f17d5` with origin/main 19a8e11a29b5: rc 0; the claim/ledger driver printed `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge_tree.txt`).
- VERSION, `custom_components/` and RELEASE_NOTES.md untouched by the delta (count 0, `ev/selftests.txt`).
- Body head line names 34dae66f17d5b511646ff51f3607d0fa6110bbfe, the head measured; the Re-cut note is present.
- CI: no pull request exists and there is no review packet, so there are no check runs to read and no CI to wait on; the `## Red checks` answers in the body could not be checked against live runs. `merge_train.py owed-reds` set: tests / coverage-ratchet, tests / fast (3.14), tests / mutation, tests / typing, validate / validate-hacs (tail; full output in `ev/selftests.txt`).
- Figures not re-derived: the body's `prepr.sh rc=0` and `r10_open_driver_mutants.py` `RESULT mutants=24 survived=0` were not re-run in this round (outside the delta's scope).
