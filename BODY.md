Part of #201.

Group: R10-FLOW-RELAY-HOLD (registered on origin/handoff/audit-r10-roster)

Pack file: dev/programme/flow-study/roster/groups/R10-FLOW-RELAY-HOLD.json at PACK_SHA f89bfb4e on branch claude/dazzling-gauss-7l3u2b.

`cloud_relay.sh`'s handoff arm updated every open PR whose `handoff/<topic>` tip was ahead of its head, and nothing could exclude one. The roster PR's topic is `audit-r10-roster`. Every `roster_edit.py` push lands on that branch, forward-carries included, so freezing the roster PR meant stopping every roster push (K13a). This PR adds the hold that the study specifies:

- `<state>/cloud-handoff-hold` lists PR numbers, one per line. Blank lines and `#` lines are allowed. Only the orchestrator writes it. A last line with no trailing newline is read like any other.
- A listed PR whose handoff is ahead is not updated. The pass prints `cloud_relay: HELD #<pr> <handoff tip>` once. Removing the number resumes it.
- A missing or empty file holds nothing. The whole handoff arm is refused for that pass by any line that is not a plain PR number, or by a file that is not a readable regular file. The refusal is rc 2, `refused: malformed hold file`, and `OWED <utc> handoff-hold-malformed <file> -` in `<log>.level`. That line stays until a pass reads the file well-formed. A malformed file never holds all and never holds none.
- `cloud_relay.sh held <pr>` reads the same file through the same parser: rc 0 held, 1 not held, 2 malformed. R10-ORCH-MACHINERY's `handoff` job can therefore use it unchanged, with the same path, grammar and refusal.

Some design choices here could look like bugs to a later seat. Each is pinned by a check and a mutant:

- The hold is checked after the "handoff already contained in the PR head" test, so a held PR with nothing to apply prints nothing (`cloud_relay-9`).
- It is checked before the failed-update ledger, so a hold outranks a recorded failure (`cloud_relay-8`).
- A refusal stops only the handoff arm. The probe arm of `pass` still runs.
- The grammar is strict: no leading zeros and no trailing text. A lenient parse is how "hold nothing" happens silently.
- The malformed-file refusal is a level line, never an event-log line. `orchestrator_tick.py`'s `relay_owed` (#2547) skips any log `OWED` line that names no PR (`cloud_relay-10`). Every well-formed pass clears it (`cloud_relay-11`).

Mutant ids are per file, `cloud_relay-1` to `cloud_relay-11`, never new S numbers. This is the P6 convention in this group's brief.

Code-owned: no. `grep -n "cloud_relay\|tools/audit/seat\|r10_seat" .github/CODEOWNERS` prints nothing for `tools/audit/seat/cloud_relay.sh`, `tools/audit/seat/INSTRUMENTS.md` and `dev/audit/harnesses/r10_seat_selftests_mutants.py`.

This round clears the review of f44296a6, which was blocked on the forward-carry alone (fix-review.md step 10). The roster ref is frozen until #2588 merges, so this seat cannot append to it. `## Forward-carry` now gives the exact text for each destination's roster `carry`, fenced and labelled `ROSTER-APPEND`, for the orchestrator to land with `roster_edit.py`. R10-FLOW-ROSTER-FREEZE was dismissed as "not yet registered", but it is registered and live, so it is now a carry with its own append text. The code is unchanged since f44296a6, apart from merging origin/main.

## Head

`0e4558f438c1febcbe1f5943e001790eeea4dc26` merges origin/main `49018a8bec8d03fd2df52874b9021d25ab93741a` (after #2584) into `187cec730` by hand, resolving one content conflict (see `## Main absorb`, third absorb). The PR's own code is unchanged. `git diff --stat $(git merge-base origin/main HEAD)...HEAD` gives 4 files, +130/-2. Measured 2026-10-22T16:40Z.

`187cec730000ae37c4191d642cf22c0422c7797e` merges main `738d950` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`25a22a315ed8d19b82f171e535c9dfcbb1d830f5` merges main `543c808` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`b8c6d6d5571614f5897413d77bf1476022830583` merges main `6c8903a` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`3567b14ffa876277878db238aa91c7cd70a83f11` merges main `cd4aaed` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`76bcb1ee313e9d5754f18658192eb81b8b9040cd` merges main `04c1dd7` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`808137a949c2c1ce64acc340cfd72ccfebc7a6b8` merges origin/main `8a4c438e7d9a6e2c492a1733d658d96b7b1eedcf` (after #2578) into the previous head `8aec46775`. The fixer seat made this merge by hand, resolving one content conflict (see `## Main absorb`, second absorb). The PR's own code is unchanged.

`8aec467755b2ec15635430e82c4002f3aea5d611` merges main `c616593` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`caac2c8dfb338b316803b94ba1df13aff02647e0` merges origin/main `16a8240f179d8a6a1ecaae2b284f6ec5a0f04eab` into the previous head `056776d87`. The fixer seat made this merge by hand, resolving one content conflict (see `## Main absorb`). The PR's own code is unchanged.

`056776d8754930075a030426dd807208e0fd2bc3` merges the authored code head `f78491bb28138e6318524da43f04abcdb1f3190b` and then merges origin/main `3976515a0` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

f78491bb28138e6318524da43f04abcdb1f3190b. It is f44296a61f42250b23c0f557a54c6295ab991dac (the reviewed head) with origin/main 93e6a63d2855651448a2b8f677b392feddc03c99 (`Merge pull request #2557`) merged in. That is a merge, never a rebase, with no conflict. It adds no commit of this PR's own. The PR's own diff against the merge base is unchanged: 4 files, +133/-3, by `git diff --stat $(git merge-base origin/main HEAD)...HEAD`. Every figure below was taken at this head, or at origin/main 93e6a63d2 where marked. `git merge-base --is-ancestor origin/main HEAD` held. Measured 2026-10-22T01:49Z.

The PR's commits, oldest first, excluding main's: cfa89d24f, 0ddbc0c21, a8a2778e1, 71a85d660, 255883803, ce4d12085, a54aed8b9, ed13f9a4f, bc313e7ca, 47a40f71f, 929ee1607, a43f68813, f44296a61, and new in this round f78491bb2 (the origin/main merge).

## Main absorb

`git merge origin/main` (16a8240f1) into `056776d87` conflicted in one file, `dev/audit/harnesses/r10_seat_selftests_mutants.py`, in the `MUTANTS` tail after `S38`. This PR adds `cloud_relay-1`..`cloud_relay-11`. Main's r10-flow-andon adds `tick_loop-1`, `tick_loop-2` and `heartbeat-1`..`heartbeat-4`. Choice: keep both sides' tuples unchanged, this PR's first. The docstring merged without a conflict and read `S01..S38 and the per-file ids (tick_loop-N, heartbeat-N)`. I added `cloud_relay-N` to that list so that it is true of the merged list. `cloud_relay.sh`, `INSTRUMENTS.md` and the delivery row merged without a conflict.

Re-taken at `caac2c8df` with origin/main at `16a8240f1` on 2026-10-22, using the seat venv shims:
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` with no names, so every mutant ran: M0 printed `0 seat step(s) red` and `RESULT survivors=0`, exit 0. `grep -c ': KILLED'` gives 59, which is the 53 above plus main's six new per-file mutants. A run of only the 17 per-file ids (`cloud_relay-1`..`-11`, `tick_loop-1`..`-2`, `heartbeat-1`..`-4`) killed each one. Each mutant's null control is the same step run on the unmutated file, and it passed first, because the harness prints `NOT RUN` otherwise.
- `cloud_relay.sh --self-test`: `189 checks, 0 failed`. `selftest_wiring.py --check`: `76 self-testing, 76 wired, 0 unwired`.
- `tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, with `PREPR_SKIP_CLOSURES=1`.
- `run_always`: `env_drift.py --claims-only <merge-base>`, `closure.py selftest`, `layout.py`, `harness_headers.py` and `structure.py` all exit 0.

Second absorb, `808137a94`. `git merge origin/main` (8a4c438e7) into `8aec46775` conflicted in the same file again, because #2578 added `body_patch-1` at the same tail and its own docstring id list. I took the union. `MUTANTS` runs `S38`, then `body_patch-1`, then `cloud_relay-1`..`-11`, then `tick_loop-1`..`-2` and `heartbeat-1`..`-4`, with every tuple unchanged. The docstring now lists `(body_patch-1, cloud_relay-N, tick_loop-N, heartbeat-N)`. Main did not touch `cloud_relay.sh` or the delivery row. `INSTRUMENTS.md` auto-merged, and `git diff --numstat origin/main HEAD` shows it +9/-0, so neither side lost a line.

Re-taken at `808137a94` with origin/main at `8a4c438e7` on 2026-10-22:
- The full mutants harness, with no names: `M0: 0 seat step(s) red` and `RESULT survivors=0`, exit 0. `grep -c ': KILLED'` gives 60, the 59 above plus main's `body_patch-1`, which fails 3 of 62 checks.
- `cloud_relay.sh --self-test`: `189 checks, 0 failed`. `selftest_wiring.py --check`: `77 self-testing, 77 wired, 0 unwired`.
- Gate scope: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, with `PREPR_SKIP_CLOSURES=1`. For run_always, `env_drift.py --claims-only 8a4c438e7` printed `ok`, `closure.py selftest` printed `ALL 112 closure shrink pins PASSED`, `layout.py` printed `ok` and `harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`. `structure.py` printed `STRUCTURE RATCHET PASSED`.

Third absorb, `0e4558f438c1febcbe1f5943e001790eeea4dc26`. `git merge origin/main` (49018a8be) into `187cec730` conflicted in the same file's docstring only: #2584 reworded the id sentence to `S01..S38, and each per-file id (<file>-<n>)`, and this head's text listed `body_patch-1, cloud_relay-N, tick_loop-N, heartbeat-N`. I took main's wording, which covers every per-file id, so the list is not carried. The `MUTANTS` list merged without a conflict: main's `merge_train-1`..`-14` sit with this PR's `cloud_relay-1`..`-11`, and `grep -oE '^    \("[A-Za-z0-9_-]+"' <harness> | sort | uniq -d` prints nothing, so no id repeats.

Re-taken at `0e4558f438c1febcbe1f5943e001790eeea4dc26` with origin/main at `49018a8be` on 2026-10-22, with `/opt/hpo/venv-ci/bin` first on PATH (the default `python3` has no numpy):
- The full mutants harness, no names: `RESULT survivors=0`, exit 0, every `M0` row `rc=0`, no `NOT RUN`. `grep -c KILLED` gives 83, covering `S01`..`S38`, `S04U`, the W rows and every per-file id of both sides.
- `cloud_relay.sh --self-test`: `189 checks, 0 failed`. `selftest_wiring.py --check`: `77 self-testing, 77 wired, 0 unwired`. `tmp_paths.py --check`: `0 refused`.
- Gate scope: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, with `PREPR_SKIP_CLOSURES=1`. For run_always, `env_drift.py --claims-only 49018a8be` printed `ok`, `closure.py selftest` printed `ALL 112 closure shrink pins PASSED`, `layout.py` printed `ok`, `harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`, `entities.py` printed `ALL 2388 ENTITY CHECKS PASSED` and `structure.py` printed `STRUCTURE RATCHET PASSED`.

Every figure below that this section does not name is still the one measured at its stated head.

## Mutation proof

This round adds no production line, so it has no new failing-test-first. The proof is re-taken at the merged head.

Each mutant below was planted alone in `tools/audit/seat/cloud_relay.sh` at f78491bb2, using the harness's own `MUTANTS` patterns, and run with `--self-test`. The unmutated count is 189 checks. The file was restored after each mutant, and `git status --short` printed nothing afterwards.

- `cloud_relay-6`: no level line is written on refusal. Result: `18 failed`. Failing checks: `and owes handoff-hold-malformed in the level file` and `once after two passes (rewritten, never appended)`.
- `cloud_relay-10`: the pre-#2547 form, `logline OWED` to the event log. Result: `27 failed`. Failing checks: the two above, plus `and the event log carries no refusal line`.
- `cloud_relay-11`: the clearing `level_set` is replaced by `rm -f`. Result: `1 failed`. Failing check: `a pass that reads the file well-formed drops the refusal from the level`.

The finder's harness was run at the head with no names, so every mutant ran: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`.

- M0 printed `0 seat step(s) red`.
- 53 mutant rows were `KILLED`, which is every row the harness defines. Main's rows are S01 to S38, S04U, and W1 to W3. This PR's rows are `cloud_relay-1` to `-11`.
- This PR's rows failed these self-test counts: `-2` 36, `-3` 49, `-4` 2, `-5` 3, `-6` 18, `-7` 2, `-8` 1, `-9` 1, `-10` 27 and `-11` 1. `-1` died on the self-test's own `updated` file.
- The run ended `RESULT survivors=0`, exit 0.

## Null control

- The finder's harness at origin/main 93e6a63d2, run from a detached worktree with the same command:
  - 42 `KILLED` rows: S01 to S38, S04U and W1 to W3. No mutant row survived.
  - M0 printed `1 seat step(s) red`, so the run ended `RESULT survivors=1`, exit 1. The harness adds M0 reds to the survivor count (`survivors += bad`).
  - The red step is `ref_privacy`. It refuses `dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md:3` as `home-directory`. That line names `dev/governance/roles/root-cause.md`, and this host's home directory is `/root`, which appears in it as `/root-cause.md`. `sed -n 3p ... | grep -o "/root[^ ]*"` printed `/root-cause.md`.
  - At main, the check judges the lines #2557 added since f24895c0c. At this head it judges only the lines added since 93e6a63d2, which prints `0 refused`. So the red belongs to this seat's host and main's own diff, not to this PR.
- `cloud_relay.sh --self-test` at origin/main printed `81 checks, 0 failed`. Main's `cloud_relay.sh` has no `HELD`, so a listed PR is updated on every pass.
- `a well-formed hold file owes no refusal (null control)` reads `<log>.level` and passes at the head. So the reds under `cloud_relay-6` and `-10` come from the mutated line.
- Each harness row runs its unmutated step first. No row printed NOT RUN.
- The in-head controls are kept:
  - a #99 hold leaves #41 updating;
  - #141 does not hold #41;
  - empty, comment-only and missing files hold nothing;
  - a newline-terminated `99\n41\n` holds #41.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test | tail -1`:
  - `189 checks, 0 failed` at the head.
  - `81 checks, 0 failed` at origin/main 93e6a63d2.
  - The rule is the script's own check count. CI requires it to be nonzero with 0 failed (`governance.yml` instrument-self-tests).
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`, run with no names so every mutant runs:
  - At the head: `grep -c ': KILLED'` gives 53, `RESULT survivors=0`, exit 0.
  - At origin/main: 42, `RESULT survivors=1`, exit 1, from the M0 host red explained under Null control.
  - The instrument is the harness. Its scope is every mutant it defines, M0, S04U and the W rows included.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, and `scope.run` was empty. Key on the mode line. The run used `PREPR_SKIP_CLOSURES=1`.
- Run at the head:
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - With `/opt/hpo/venv-ci/bin/python` and `PYTHONPATH=tests/hastub`: `tests/entities.py` ends `ALL 2382 ENTITY CHECKS PASSED`, `tests/harness_headers.py` ends `ALL 109 HARNESS HEADER CHECKS PASSED`, and `tests/layout.py` prints `layout self-test: ok`.
  - `python3 -I tools/audit/seat/tmp_paths.py --check` prints `0 refused`.
  - `python3 tests/throwaway_git.py --check` prints `0 raw git init or clone site(s) refused`.
  - `python3 tools/audit/seat/selftest_wiring.py --check` prints `73 self-testing, 73 wired, 0 unwired`. Main's `pulse.py` (#2557) is the 73rd.
- `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden | wc -l` prints 0. That diff would list any of those files this branch touched.
- `git merge-tree --write-tree origin/main HEAD` exits 0 with tree 9aa93118, at origin/main 93e6a63d2.
- Class seams (step 8). The seam is "a cloud_relay.sh writer of a log `OWED` line that the tick would skip as naming no PR". The instrument is `grep -n 'logline OWED\|owed "\|>> "$(relay_log)"' tools/audit/seat/cloud_relay.sh`, and the merge did not change that file. It returns `owed()` (PR first), `handoff-update $pr`, `approve-held-runs $pr`, two `dispatch $pr` lines and `OWED reviewer-fire <pr>`. Each has the PR in fields 2 to 4, where `relay_owed` looks, so each is already guarded. The hold refusal was the only log `OWED` line without a PR, and this diff closes it.
- Hold-file readers: `grep -rn "cloud-handoff-hold\|hold_list" tools/ .github/ dev/` returns `cloud_relay.sh`, `INSTRUMENTS.md` and the harness's `cloud_relay-2`, `-6`, `-10` and `-11` patterns. No second reader exists yet. R10-ORCH-MACHINERY's job will be the second, which is the carry below.
- Destination content on `origin/handoff/audit-r10-roster` 306a96d5f. For each group, `git show <ref>:dev/programme/rosters/wave-r10-groups.json | jq -r --arg g <group> '.groups[]|select(.group==$g)|[.brief]+.carry|join("\n")' | grep -cE 'cloud_relay\.sh held|cloud-handoff-hold|malformed'` gives:
  - R10-ORCH-MACHINERY 0, stage `not-started`;
  - R10-FLOW-ROSTER-FREEZE 0, stage `not-started`, `after` lists R10-FLOW-RELAY-HOLD.
  - Both groups are live and neither yet holds the text. This is the null control for the two appends below: once the appends land, the same command prints a nonzero count.
- `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` prints `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`. That routing is syntactic. The destination content is the line above, and it is pending the roster freeze.

## Red checks

Read from the check-runs API, per commit, for this PR's commits. `0e4558f43` has not run CI, because this seat pushes only `handoff/` refs. The history below is unchanged by the merge.

- Commits with no check-runs (`total_count` 0): cfa89d24f, 71a85d660, 255883803, ce4d12085, 47a40f71f, 929ee1607 and a43f68813. These are intermediate commits that were never a PR head.
- At a54aed8b9, ed13f9a4f, bc313e7ca and f44296a61 there were 32 success, 16 skipped and 1 failure. a8a2778e1 had 29 success, 16 skipped and 1 failure. The failure was `nightly-status` each time.
- 0ddbc0c21 had 13 cancelled checks (superseded by the next push), `CodeQL` neutral (`Error when processing the SARIF file`) and `nightly-status` failure. Its next push, a8a2778e1, ran the same contexts green apart from `nightly-status`.
- **`nightly-status`** is main's red, not this PR's. Job 119567199209 at f44296a61 printed `NIGHTLY FAILED: mutation-nightly, slow failed last night.` It read scheduled run 39563978649 on main c77f89d, and `tests/nightly_status.py` reads only `schedule`-triggered runs of the Tests workflow.
  - `slow`, job 119101702593, failed on `FAIL synthetic-dhw-only.json: cycle_cost  [1 offender(s): loop_cpu_ratio 0.1138 over its budget 0.111]`.
  - `mutation-nightly`, job 119101702662, failed on `10 survivor(s) of 23 evaluated = 39.1% (1 triaged equivalent, raw 43.5%), cap 30.0%`. All ten survivors are under `custom_components/heatpump_optimizer/`.
  - This diff touches neither `tests.yml`, `tests/replay.py`, nor anything under `custom_components/`, so it can neither cause nor clear either failure.
  - `loop_cpu_ratio` was re-recorded by #2548 (`290712ec0`), which this head carries. No scheduled run has concluded since.
  - The mutation cap breach is in production code this PR does not touch. It belongs to the mutation lane's owner.
  - No live roster group's brief or carry names `mutation-nightly`.
  - Cheaper detector: none. Both lanes run only on the runner class they budget against.
- Three more checks are red in the history, all at `76bcb1ee313e9d5754f18658192eb81b8b9040cd` (the merge of main `04c1dd7`, run 09:43Z), none this diff's. `pr-contract`'s red-history row names them. I read each job's log once. The cause is one: the installation's GitHub API quota, which #2606's RCA records as spent by the record job's burst at the 09Z hour. It is quoted in two jobs and inferred in the third.
  - **`arch-score`**, job `119753501292` (run 39757613203, 09:44:27Z): the step "Name the pull request and read its body" died on `gh: API rate limit exceeded for installation. If you reach out to GitHub Support for help, please include the request ID 1400:317D6A:263F6:784DA:6AD9DAFA and timestamp 2026-10-22 09:44:27 UTC. ... (HTTP 403)`, so the scoring step was skipped and no measurement ran. Cheaper detector: none exists for an external quota exhaustion; the budget is owned by R10-RECORD-API-BUDGET. Carry: dismissed: external installation quota, owned by R10-RECORD-API-BUDGET
  - **`validate-hacs`**, job `119753495288` (run 39757611530, 09:44:07Z): `aiogithubapi.exceptions.GitHubRatelimitException: API rate limit exceeded for installation.` raised from `aiogithubapi/namespaces/repos.py` `get` in the action's HACS validation step. Cheaper detector: none exists for an external quota exhaustion; the budget is owned by R10-RECORD-API-BUDGET. Carry: dismissed: external installation quota, owned by R10-RECORD-API-BUDGET
  - **`env-matrix`**, job `119753498136` (run 39757611884, 09:46:13Z): one outcome failed of 16, `pr / nothing skipped in a full clone -- skip required-contexts the GitHub API is unreachable (the fixture or the API failed: 1)`. Its log holds no rate-limit line, so the cause is inferred, not quoted: the same installation, two minutes after the two quoted limit failures. The other 15 outcomes held. Cheaper detector: none exists for an external quota exhaustion; the budget is owned by R10-RECORD-API-BUDGET. Carry: dismissed: external installation quota, owned by R10-RECORD-API-BUDGET

## Forward-carry

- R10-ORCH-MACHINERY (issue #2505): its `handoff` job must read `<state>/cloud-handoff-hold` only through `cloud_relay.sh held <pr>`, and must never re-parse it.
  - rc 0 skips that PR, rc 1 proceeds, and rc 2 refuses the job's whole pass.
  - Control: a held PR whose handoff is ahead is not updated.
  - Null control: the same pass with the line removed updates it.
  - The roster ref is frozen until #2588 merges, so this seat cannot append. The orchestrator lands the text below verbatim as one new entry in that group's `carry`, with `roster_edit.py`, once the freeze lifts. carry_audit routes this item now, but the destination content is pending the freeze (Figures, "Destination content").
  - Carry: R10-ORCH-MACHINERY

  ROSTER-APPEND R10-ORCH-MACHINERY carry:

  ```text
  Hold file (R10-FLOW-RELAY-HOLD, #2580): the beat's handoff job reads <state>/cloud-handoff-hold only through `tools/audit/seat/cloud_relay.sh held <pr>`, never by re-parsing the file, so it shares cloud_relay.sh's path, grammar and refusal. rc 0 (held): the job does not update that PR. rc 1 (not held): it proceeds. rc 2 (malformed file): the job refuses its whole handoff pass and updates no PR, the same refusal as cloud_relay.sh's handoff arm (`refused: malformed hold file`; `OWED <utc> handoff-hold-malformed <file> -` in <log>.level until a well-formed pass). Control: a fixture PR listed in the hold file whose handoff/<topic> tip is ahead of its head is not updated by the job. Null control: the same pass with that line removed updates it. Malformed control: a hold file holding `41x` makes the pass update no PR. Mutant: delete the job's `held` call; the control goes red.
  ```

- R10-FLOW-ROSTER-FREEZE: if its part (a) freezes the roster PR's head through the hold file, it must write only plain PR-number lines, and it must remove its own line when the review posts.
  - One malformed line refuses cloud_relay.sh's whole handoff arm for every PR. The pass returns rc 2 and writes `OWED <utc> handoff-hold-malformed <file> -` to <log>.level until a well-formed pass. A bad write would therefore freeze every relay update, not only the roster's.
  - Control: the self-test's nine malformed variants each refuse.
  - Null control: `a well-formed hold file owes no refusal`.
  - The earlier dismissal ("group not yet registered") was false. The group is on the handoff roster, live (`not-started`), its `after` lists R10-FLOW-RELAY-HOLD, and its brief and carry hold 0 matches for the grammar. The same freeze applies, and so does the same pending note.
  - Carry: R10-FLOW-ROSTER-FREEZE

  ROSTER-APPEND R10-FLOW-ROSTER-FREEZE carry:

  ```text
  Hold-file grammar (R10-FLOW-RELAY-HOLD, #2580): if part (a) freezes the roster pull request's head by writing <state>/cloud-handoff-hold, write only plain PR-number lines (digits, no leading zero, no trailing text; blank and `#` lines allowed), and remove only your own line when the review posts. One malformed line refuses cloud_relay.sh's whole handoff arm for every PR (rc 2, `refused: malformed hold file`, `OWED <utc> handoff-hold-malformed <file> -` in <log>.level until a well-formed pass), so a bad write freezes every relay update, not only the roster's. Read a hold back through `tools/audit/seat/cloud_relay.sh held <pr>` (rc 0 held, 1 not held, 2 malformed), never by re-parsing. Control: cloud_relay.sh --self-test's nine malformed variants each refuse. Null control: its `a well-formed hold file owes no refusal`. Own control: the freeze writer's fixture output read through `cloud_relay.sh held <pr>` returns rc 0, never 2.
  ```

## Friction

none

## Notes

- `cloud_relay-7`'s malformed-file CLI check cannot kill that mutant, because usage exits 2 too. The rc 0 and rc 1 CLI arms are what kill it. This is not a stated design choice.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01QDEyGCKxQsek7nsYMNPJfd

