R10-SEAT-IDENTITY-P5 (part 1 of 1: carries 0-4, 8). One writer per standing seat (generation token) and per orchestrator session (session lock), the `loop-cwd` beat row, and the mutant harness made runnable again. Functions touched in the shared seams: `beat_jobs.py` `loop_cwd` (new) and the `ROWS`/`RUN` tables; `beatd.jobs.json` one entry; `sweep_template.md` the Placeholders row `loop_cwd_patterns`, one sentence in (5b) and one in step (0); `roster_queue.py` `run_queue`; `merge_train.py` `train_add`; `bus.sh` `dispatch`; `handover_prompt.py` Resume steps; `pulse.py` `read_alive`/`judge_alive` (the SUPERSEDED arm). No edit to `beatd.py`.

## Re-cut

Round 4, body replaced. Cut: no code. Both reads the round-4 verdict named untested are kept and now pinned by a killing check, not removed: `pulse.py` `read_alive`'s `<seat>.gen` read by a `--seat-alive` CLI case run with `HPO_STATE_DIR` holding `merge.gen` (must print `SUPERSEDED merge: new still beats`; the same CLI without the env must not); `seat_gen.py` `ps_start` by `ps_start(os.getpid(), now)` lying in `(now - 600, now]`, with an absent pid (2**22+1, above Linux's maximum `pid_max`) giving 0. Removal lost to the tests: both reads feed built carries (the SUPERSEDED tick flag, the lock's start time), and a test was the cheaper sound fix. Every figure below was re-taken in this pass. `git merge-tree --write-tree origin/main` reported a conflict (`beat_jobs.py` `ROWS`/`RUN`: main added `scorecard`, this branch `loop-cwd`), so origin/main d1def1ea6307 was merged with both rows kept, then everything was re-run at the merged head. Round history deleted.

## Head

34dae66f17d5b511646ff51f3607d0fa6110bbfe

## Mutation proof

`python3 tools/audit/seat/mutant_run.py --spec spec.json --cmd 'bash cmd.sh'` (copy-tree mode) at the head, where `cmd.sh` is `python3 -I tools/audit/seat/pulse.py --self-test >/dev/null && python3 -I tools/audit/seat/seat_gen.py --self-test --no-mutants >/dev/null && python3 -I tools/audit/seat/beat_jobs.py --self-test >/dev/null` and `spec.json` is:

```json
[
{"name": "pulse_gen_read_off", "file": "tools/audit/seat/pulse.py", "old": "    if sd:  # the generation token", "new": "    if False:  # the generation token"},
{"name": "pulse_superseded_cmp", "file": "tools/audit/seat/pulse.py", "old": "launched is not None and launched < gen_t:", "new": "launched is not None and launched > gen_t:"},
{"name": "ps_start_zero", "file": "tools/audit/seat/seat_gen.py", "old": "    r = subprocess.run([\"ps\", \"-p\", str(pid), \"-o\", \"etimes=\"], capture_output=True, text=True)\n", "new": "    return 0\n"},
{"name": "lock_start_now", "file": "tools/audit/seat/seat_gen.py", "old": "tmp.write_text(f\"{mine} {start(mine, now)}\\n\")", "new": "tmp.write_text(f\"{mine} {int(now)}\\n\")"},
{"name": "gen_ge", "file": "tools/audit/seat/seat_gen.py", "old": "    if held is not None and held > gen:", "new": "    if held is not None and held >= gen:"},
{"name": "gen_le", "file": "tools/audit/seat/seat_gen.py", "old": "    if held is not None and held > gen:", "new": "    if held is not None and held < gen:"},
{"name": "lock_no_command_match", "file": "tools/audit/seat/seat_gen.py", "old": "    if held and held != mine and SESSION_RE.search(command(held)):", "new": "    if held and held != mine:"},
{"name": "lock_own_pid", "file": "tools/audit/seat/seat_gen.py", "old": "    if held and held != mine and SESSION_RE.search(command(held)):", "new": "    if held and SESSION_RE.search(command(held)):"},
{"name": "session_ppid", "file": "tools/audit/seat/seat_gen.py", "old": "        if SESSION_RE.search(command(pid)):\n            return pid\n", "new": "        if True:\n            return pid\n"},
{"name": "loopcwd_path_only", "file": "tools/audit/seat/beat_jobs.py", "old": "            if now != int(fields[\"i\"]):", "new": "            if now is None:"},
{"name": "loopcwd_empty_dead", "file": "tools/audit/seat/beat_jobs.py", "old": "lines.append(f\"loop-cwd: UNREADABLE {name} pid={pid} lsof returned no cwd\")", "new": "lines.append(f\"DEAD {name} pid={pid} cwd gone\")"}
]
```

Output, rc=0:

```
SURVIVED NULL
KILLED pulse_gen_read_off
KILLED pulse_superseded_cmp
KILLED ps_start_zero
KILLED lock_start_now
KILLED gen_ge
KILLED gen_le
KILLED lock_no_command_match
KILLED lock_own_pid
KILLED session_ppid
KILLED loopcwd_path_only
KILLED loopcwd_empty_dead
```

The two verdict items are `pulse_gen_read_off` (`if sd:` to `if False:`) and `ps_start_zero` (`ps_start` returns 0). Each was also SURVIVED at the reviewed head 7572aa0aa878 (round-4 verdict, reviewer's run), and is KILLED here. Further in-file proof: `seat_gen.py --self-test` (without `--no-mutants`) applies its own `MUTANTS` table and prints `ok` for each kill.
- `python3 -I dev/audit/harnesses/r10_open_driver_mutants.py` at the head: `RESULT mutants=24`, `RESULT survived=0`, rc 0, with its unmutated `M0` at `failed=0 verdict=null-ok`.

## Null control

- Mutation: the driver's automatic `NULL` run (no edit) is `SURVIVED NULL`, so the command is green on the unedited tree and each KILLED is the edit's.
- `read_alive`: the same `--seat-alive` CLI call without `HPO_STATE_DIR` prints no `SUPERSEDED` (the check asserts it); in `judge_alive`, a gen bump before the newest launch and no gen token are both `ok`.
- `ps_start`: an absent pid is 0.
- Generation: the current generation, a generation ahead of the file and a seat with no file all exit 0; unset `HPO_SEAT_GEN` leaves each wired writer (`run_queue`, `dispatch`, `train_add`) writing as before.
- Lock: a dead holder pid and a reused pid naming another command are both taken over; the session's own pid is not a duplicate.
- `loop-cwd`: a live directory writes nothing; an `lsof` returning nothing is UNREADABLE, never DEAD.

## Figures

All at head 34dae66f17d5, origin/main d1def1ea6307, 2026-11-12T21:39:05Z:
- `python3 -I tools/audit/seat/pulse.py --self-test`: prints its check count and `0 failed`.
- `python3 -I tools/audit/seat/seat_gen.py --self-test`: prints its check count and `0 failed`.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: `0 failed`.
- `python3 -I tools/audit/seat/open_driver.py --self-test`: `0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL` (`tests/closure.py` changes the gate), so the scope is CI's.
- `git merge-tree --write-tree origin/main HEAD`: rc 0 after the merge (rc 1, `beat_jobs.py`, before it).
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: rc 0, run under venv-ci (`/opt/hpo/venv-ci/bin/python3`).
- `bash tools/pr/prepr.sh <this body>` at the head: `PRE-PR: 34dae66f17d5 ... rc=0`.

## Red checks
- `tests / closures`: red at an earlier head because `seat_gen.py` and `seat_gen_selftest.py` sat on the INERT `tools/audit/seat/` prefix while `tests/entities.py` read them; repaired by excepting both in `tests/closure.py` `INERT_EXCEPT` and recording them into the `tests/entities.py` closure. Cheaper detector: `closure.py orphan_files()` locally, which `prepr.sh` runs; standing cost is the recording itself, so no new detector. Carry: dismissed: repaired in this diff
- `tests / fast (3.14)`: red on main's ancestry, not on a file this diff touches. Cheaper detector: none for a main-side red; the scoped gate runs only this diff's closure. Carry: dismissed: inherited from main, outside this diff

## Forward-carry

- Carry 0, Carry 1 and Carry 2 (generation token, session lock, their fold): built; `lock` is named in `handover_prompt.py` Resume steps and `sweep_template.md` step (0); `pulse.py` `judge_alive` prints `SUPERSEDED <seat>` when the newest launch predates the `<seat>.gen` bump, which DUPLICATE (two fresh ids) cannot see. Carry: dismissed: built in this diff
- Carry 3 (`loop-cwd` row): built; arm (b) recreated-at-same-path is decided by inode. Carry: dismissed: built in this diff
- Carry 4 (retire the session-local opener stand-in under `beatd.py`): `beatd.py` names no stand-in; the opener row is `beat_jobs.py` `opener`. Carry: dismissed: implemented at ba544faa2dd25b75b0129879112d6409affe9662
- A `HPO_SEAT_GEN` value is `<seat>=<gen>`; the orchestrator's seat prompts carry it after `seat_gen.py bump <seat>`, as the `seat_gen.py` docstring and its instruments entry state. Carry: dismissed: documented in the instrument, no later stage is narrowed
- Carry 5, Carry 6 and Carry 7: marked `[moved: R10-HOTFIX-OPENER-UNBLOCK]` on the roster. Carry: dismissed: moved to R10-HOTFIX-OPENER-UNBLOCK on the roster, not later parts of this group
- Carry 10 (harness-stale): built; M-exact and M-body plant in `topic_grammar.py` (see Mutation proof). Carry: dismissed: built in this diff
- Carry 9 (P603 opener live tip, `open_driver.py`): the same card as carry 7. Carry: dismissed: owned by R10-HOTFIX-OPENER-UNBLOCK

## Friction

- policy-loop: stale: `agreement_py`'s restore list is hand-written; importing `seat_gen` from `merge_train.py` and `roster_queue.py` put two files in its closure, which `agreement_py.py --restore` named. Carry: dismissed: the detector already ran in prepr
- selftest_wiring: contradiction: a selftest module spelling the self-test flag in text is predicted unwired; avoided by not spelling it (`"--self" "-test"`), as `open_driver_selftest.py` does. Carry: dismissed: existing convention
