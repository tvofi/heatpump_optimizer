R10-SEAT-IDENTITY-P5 (part 1 of 1: carries 0-4, 8). One writer per standing seat (generation token) and per orchestrator session (session lock), the `loop-cwd` beat row, and the mutant harness made runnable again. Functions touched in the shared seams: `beat_jobs.py` `loop_cwd` (new) and the `ROWS`/`RUN` tables; `beatd.jobs.json` one entry; `sweep_template.md` the Placeholders row `loop_cwd_patterns`, one sentence in (5b) and one in step (0); `roster_queue.py` `run_queue`; `merge_train.py` `train_add`; `bus.sh` `dispatch`; `handover_prompt.py` Resume steps; `pulse.py` `read_alive`/`judge_alive` (the SUPERSEDED arm). No edit to `beatd.py`.

Issue #3134 (R10-SEAT-SINGLE-WRITER's tracking issue) is wired by the roster to this group's `issues`, not its `fixes`. That makes it a never-close number for pr-contract, so this body names it and does not close it. Both of its items, the generation token per standing seat and the session lock per orchestrator session, are files of this pull request: `tools/audit/seat/seat_gen.py` (`bump`/`check` and `lock`) with `seat_gen_selftest.py`. Its three named seam files, `handover_prompt.py` (Resume steps), `sweep_template.md` (step (0)) and `INSTRUMENTS.md`, are edited here too.

## Re-cut

Round 4, body replaced. Cut: no code. Both reads the round-4 verdict named untested are kept and now pinned by a killing check, not removed: `pulse.py` `read_alive`'s `<seat>.gen` read by a `--seat-alive` CLI case run with `HPO_STATE_DIR` holding `merge.gen` (must print `SUPERSEDED merge: new still beats`; the same CLI without the env must not); `seat_gen.py` `ps_start` by `ps_start(os.getpid(), now)` lying in `(now - 600, now]`, with an absent pid (2**22+1, above Linux's maximum `pid_max`) giving 0. Removal lost to the tests: both reads feed built carries (the SUPERSEDED tick flag, the lock's start time), and a test was the cheaper sound fix. Every figure below was re-taken in this pass. `git merge-tree --write-tree origin/main` reported a conflict (`beat_jobs.py` `ROWS`/`RUN`: main added `scorecard`, this branch `loop-cwd`), so origin/main d1def1ea6307 was merged with both rows kept, then everything was re-run at the merged head. Round history deleted.

## Head

`75d6b5fe8243474b5a22cda7ee2a666372653d1e` is one commit on `9b7d8d36820e7c8a4100d4186378b1c8abb3663c` that repairs `seat_gen.py` `ps_start` on macOS. Nothing else changed: `git diff 9b7d8d36 75d6b5fe --stat` names only `tools/audit/seat/seat_gen.py` and `tools/audit/seat/seat_gen_selftest.py`. `ps_start` read `ps -o etimes=`, which is procps-only, so on Darwin it returned 0. It now reads `ps -o lstart=` under `LC_ALL=C` and parses it as a local-time epoch in the new `parse_lstart`. That is the kernel's absolute start, so two reads of one live pid agree, where an elapsed time is subtracted from a clock read at another instant. `ps_start` and `lock` drop their `now` argument, whose only use was that subtraction. The self-test pins the parser offline, read as UTC: a recorded procps line, a padded macOS line, a space-padded day, and a null control in which an etimes figure, a localised line and an empty string each read as 0. It also checks that two live reads agree, and it runs a CLI case, `lock --pid <self>`, that must record this pid's live start and never 0. Two in-tree parser mutants are added: `lstart_strip` is killed by the padded macOS line, `lstart_utc` by the procps line. Re-run at 75d6b5fe, 2026-11-14T23:13Z, against origin/main 6abf88e617ee (merge base still d7004eaa775d; `git merge-tree --write-tree origin/main HEAD` rc 0), macOS host:
- `python3 tools/audit/seat/seat_gen.py --self-test`: `seat_gen self-test: 33 checks, 0 failed` (at 9b7d8d36: `25 checks, 1 failed`, the `ps_start` check). Linux is left to CI.
- `python3 tools/audit/seat/mutant_run.py --diff 9b7d8d36...HEAD --cmd 'python3 tools/audit/seat/seat_gen.py --self-test'` (this commit only): 0 survivors in `seat_gen.py`. All 17 survivors are in `seat_gen_selftest.py`, and each deletes a passing `check(...)` or loosens a bound that the green tree satisfies either way. Over the whole branch (`--diff d7004eaa...HEAD`), `seat_gen.py` survivors fall from 40, at this commit's first cut before the CLI case, to 35, and none is on a line this commit adds. 9b7d8d36 cannot be measured here: its baseline self-test fails on this host, so the driver could read nothing from it. `seat_gen.py:159` STMT_DEL (the `lock` CLI call) is now killed by the CLI case.
- `bare_array.py --check` rc 0, `selftest_wiring.py --check` `0 index gap(s)`, `node tools/policy/policy_lint.mjs` `TOTAL: 0 error(s) across 51 policy file(s)`, `python3 tests/structure.py` `STRUCTURE RATCHET PASSED`, `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` `PRE-PR: 75d6b5fe8243474b5a22cda7ee2a666372653d1e 0000000000 rc=0`.
The 9b7d8d36 note below stands for every file other than these two. Its `seat_gen` line describes 9b7d8d36, not this head.

`9b7d8d36820e7c8a4100d4186378b1c8abb3663c` merges origin/main `d7004eaa775dd7b42aa392df0eb53aeec198b2b0` into the reviewed head `a720d3ed6381bbf7f5771d33b000a2cf02fa84d4` (merge verdict, round 6), because the pull request was `DIRTY`: `git merge-tree --write-tree origin/main a720d3ed` exited 1 at that tip. The handoff tip `bc06133f86bd` is an ancestor of a720d3ed, so no handoff merge was needed. Resolution, file by file:
- `tests/closure.py` (the one conflict, `INERT_EXCEPT`): a union. Main's R10-CI-PRIORITY-PAUSE block (`dev/audit/config/ci_priority.json`, `tools/audit/seat/ci_priority.py`, `tools/audit/seat/ci_pause.py`) stays where main put it, next to `orchestrator_tick.py`, whose self-test its comment means by "that self-test". This branch's R10-SEAT-IDENTITY-P5 block (`seat_gen.py`, `seat_gen_selftest.py`) moves below the `pr_cap.py`/`budget_raise_gate.py`/`app_approve.sh` trio, so main's "... and that self-test reads these three" chain stays unbroken. Its comment names its own route and does not depend on where it sits. No entry was dropped: all five paths are in the merged tuple.
- `tests/closures.json`: merged by the `LEDGER-MERGE` driver (`closures.tests/entities.py` and `inert_reads.tests/entities.py` merged as sets). No hand edit.
- `.github/workflows/governance.yml`, `tools/audit/seat/INSTRUMENTS.md`, `beat_jobs.py`, `beat_jobs_selftest.py`, `bus.sh`, `merge_train.py`, `sweep_template.md`, `tools/ci/selftest_closures.json`: git merged these automatically, with no hand edit.
The PR's own patch is unchanged by this merge. For each of the 19 files of `git diff $(git merge-base origin/main HEAD) HEAD`, the ordered `+`/`-` lines hash the same at a720d3ed (merge base 6858b4abc194) and at 9b7d8d36 (merge base d7004eaa775d): 19 of 19 `same`, where an edited hunk would print `DIFF`. The only hand edit is the `tests/closure.py` placement above, and that block's lines are unchanged in content and order. Re-run at 9b7d8d36, 2026-11-14T21:34Z, against origin/main d7004eaa775d (macOS host):
- `python3 -I tools/audit/seat/pulse.py --self-test`: `pulse self-test: 70 checks, 0 failed`.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: `beat_jobs self-test: 251 checks, 0 failed`.
- `python3 -I tools/audit/seat/open_driver.py --self-test`: `open_driver self-test: 93 checks, 0 failed`.
- `python3 -I tools/audit/seat/roster_queue.py --self-test`: `roster_queue self-test: 67 checks, 0 failed`.
- `python3 -I tools/audit/seat/handover_prompt.py --self-test`: `handover_prompt self-test: 20 checks, 0 failed`.
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 760 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_open_driver_mutants.py`: `RESULT mutants=24`, `RESULT survived=0`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 51 policy file(s)`. `node tools/policy/brief_lint.mjs`: rc 0, last line `PLAYBOOK ok: ...`.
- `python3 -I tools/audit/seat/seat_gen.py --self-test`: `seat_gen self-test: 25 checks, 1 failed`. The failure is `FAIL ps_start: this process's start time is now less its ps etimes, never 0`, and it is Darwin-only: macOS `ps` has no `etimes` keyword (`ps -o etimes= -p $$` prints `ps: etimes: keyword not found`), so `ps_start` returns 0 here. Neither file is touched by this merge (`git diff a720d3ed 9b7d8d36 -- tools/audit/seat/seat_gen.py tools/audit/seat/seat_gen_selftest.py` is empty). CI runs the step on Linux, and the round-6 review recorded `seat_gen 25 checks, 0 failed`. The defect is reported to the orchestrator and is not fixed in this merge-only round.
- `bash tools/audit/seat/bus.sh --self-test`: `bus self-test: 232 checks, 1 failed`, the same at a720d3ed and at 9b7d8d36 when the two ran side by side, each copy carrying two added `echo` lines to stderr around the `HPO_SEAT_GEN` checks, with `python3` resolving to the system interpreter. The one failure, `FAIL push-verdict refuses evidence names that differ only by case, naming both`, is main's own and comes from the case-insensitive macOS filesystem. Origin/main d7004eaa775d fails the same check alone, at `230 checks, 1 failed`. Two caveats about this host, neither of them a CI condition. First, with this host's `python3` shim first on `PATH`, the two `HPO_SEAT_GEN` dispatch checks also fail: the shim looks for a pinned venv under the fixture's `HPO_STATE_DIR`/`HOME` and prints `python3: no pinned interpreter at ...`. Second, one earlier run without the shim failed the null-control `HPO_SEAT_GEN` check once, and that did not reproduce in the two runs after it.
- `git merge-tree --write-tree origin/main HEAD`: rc 0 (rc 1 at a720d3ed, on `tests/closure.py`).

Previous head: `a720d3ed6381bbf7f5771d33b000a2cf02fa84d4` merges the authored code head `bc06133f86bdb0ccd62db8fbef2f5c80f32678e8` and then merges origin/main `6858b4abc1` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

bc06133f86bdb0ccd62db8fbef2f5c80f32678e8 — origin/main merged into the PR head 09fac908; the one conflict, tools/audit/seat/beat_jobs.py, resolved as a union (loop-cwd from this branch, darwin-selftest from main, in ROWS and RUN); no other file touched by hand. The merge verdict at 34dae66f does not carry; a delta review follows.

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
- `bash tools/pr/prepr.sh <this body>` at the head: `PRE-PR: bc06133f86bd ... rc=0` (hotfix-scoped: `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`).

## Red checks
- `tests / briefs`: red at ece5ee3b, a merge of origin/main into this branch, on `carry-1067.json` carry controls (`lift_consistency.py` not in the tree) that main itself carried in; not this diff's content, and `brief_lint.mjs` is clean at the current head. Cheaper detector: `brief_lint.mjs`, which `prepr.sh` runs; its standing cost is one local run, so no new detector. Carry: dismissed: inherited from main, clean at head
- `tests / closures`: red at an earlier head because `seat_gen.py` and `seat_gen_selftest.py` sat on the INERT `tools/audit/seat/` prefix while `tests/entities.py` read them; repaired by excepting both in `tests/closure.py` `INERT_EXCEPT` and recording them into the `tests/entities.py` closure. Cheaper detector: `closure.py orphan_files()` locally, which `prepr.sh` runs; standing cost is the recording itself, so no new detector. Carry: dismissed: repaired in this diff
- `tests / fast (3.14)`: red on main's ancestry, not on a file this diff touches. Cheaper detector: none for a main-side red; the scoped gate runs only this diff's closure. Carry: dismissed: inherited from main, outside this diff

## Forward-carry

- Carry 0, Carry 1 and Carry 2 (generation token, session lock, their fold): built; `lock` is named in `handover_prompt.py` Resume steps and `sweep_template.md` step (0); `pulse.py` `judge_alive` prints `SUPERSEDED <seat>` when the newest launch predates the `<seat>.gen` bump, which DUPLICATE (two fresh ids) cannot see. Carry: dismissed: built in this diff
- Carry 3 (`loop-cwd` row): built; arm (b) recreated-at-same-path is decided by inode. Carry: dismissed: built in this diff
- Carry 4 (retire the session-local opener stand-in under `beatd.py`): `beatd.py` names no stand-in; the opener row is `beat_jobs.py` `opener`. Carry: dismissed: implemented at ba544faa2dd25b75b0129879112d6409affe9662
- A `HPO_SEAT_GEN` value is `<seat>=<gen>`; the orchestrator's seat prompts carry it after `seat_gen.py bump <seat>`, as the `seat_gen.py` docstring and its instruments entry state. Carry: dismissed: documented in the instrument, no later stage is narrowed
- Carry 5, Carry 6 and Carry 7: marked `[moved: R10-HOTFIX-OPENER-UNBLOCK]` on the roster. Carry: dismissed: moved to R10-HOTFIX-OPENER-UNBLOCK on the roster, not later parts of this group
- Carry 8 and Carry 10 (harness-stale; carry 10 restates carry 8's card): built; M-exact and M-body plant in `topic_grammar.py` (see Mutation proof). Carry: dismissed: built in this diff
- Carry 9 (P603 opener live tip, `open_driver.py`): the same card as carry 7. Carry: dismissed: owned by R10-HOTFIX-OPENER-UNBLOCK

## Friction

- policy-loop: stale: `agreement_py`'s restore list is hand-written; importing `seat_gen` from `merge_train.py` and `roster_queue.py` put two files in its closure, which `agreement_py.py --restore` named. Carry: dismissed: the detector already ran in prepr
- selftest_wiring: contradiction: a selftest module spelling the self-test flag in text is predicted unwired; avoided by not spelling it (`"--self" "-test"`), as `open_driver_selftest.py` does. Carry: dismissed: existing convention

## Resolution note

Merging origin/main into 09fac908 conflicted only in `tools/audit/seat/beat_jobs.py` (`ROWS` and `RUN`): resolved as a union of `loop-cwd` (this branch) and `darwin-selftest` (main). Re-run: `beat_jobs.py --self-test` 250 checks 0 failed; `r10_open_driver_mutants.py` 24 mutants, 0 survived; `tests/structure.py` passed; policy_lint and brief_lint clean.

Merging origin/main d7004eaa775d into a720d3ed conflicted only in `tests/closure.py` `INERT_EXCEPT`, resolved as a union (see Head). The merged tree was read back for each side's clauses: main's three paths and their two comments, this branch's two paths and their comment, each present once.
