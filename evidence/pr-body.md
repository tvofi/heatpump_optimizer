prepr's `closures` step (6b) default-skips off Linux, since CI's required `closures` context and
`closures-autofix` own the check, with `PREPR_RECORD_CLOSURES=1` as the opt-in for a lane that needs a
first-green head. The recorder also dies with the prepr. Step 6b runs `closures_line` as a job the prepr
`wait`s on (`closures_step`), and a `$$` watchdog reaps the recorder's process group. Linux is unchanged.
The policy half is `dev/governance/rules/gate-scoping.md` and its two generated copies, unchanged since
round 2.

Round 3 changes only the self-test's reap arms, which fixes the review's two blocks:

- The sleeper that stands for the recorder now forks one lane, `( sleep 300 ) &`, as
  `derive_closures.sh` forks its recording lanes. Every reap arm requires the prepr, the recorder and
  the lane to be gone. Each is read as gone by its `ps -o stat=` state (absent or `Z`), never by
  `kill -0`, which counts a zombie the container's PID 1 leaves unreaped as alive. (item 61eab2a5)
- The driver no longer calls `closures_step` itself. The self-test copies step 6b's own block out of
  `prepr.sh` at its `# --- 6b.` marker into the driver's text. A change to that call site is therefore
  what the arms run. It is copied and never `eval`ed: under `eval`, bash runs a trap at once even inside
  a command substitution. An eval'd copy left M9 and M4sub at 323/0 (first pass, `c5355e08f`), and a
  probe showed the same (`## Figures`). (item 3fc47a16)

## Head

`10f85c3ee7065d31230e292d7438e105efb9ff57` merges the authored code head `df97bd4463fe39029386ef8e608e492feb6ce686` and then merges origin/main `5a755f53e` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Code head `df97bd446`, pushed to `handoff/r10-prepr-closures`. It is the PR head `5332c59f9` plus two
merges of origin/main (never a rebase) and this round's commits `c5355e08f` and `c87bd1b27`. The merges
took main at `500668757` and then at `1ebc737e7` (read 2026-10-21T21:16:35Z). The second merge brought
only delivery rows, and `git diff --quiet c87bd1b27 df97bd446 -- tools/pr/prepr.sh` exits 0, so the
mutation table, taken at `c87bd1b27`, measures the same `prepr.sh`. M0 and the cheap checks were re-taken
at `df97bd446`. The merge base is `1ebc737e7`.

## Mutation proof

Rule: each mutant is a detached worktree at `c87bd1b27` with one literal edit to `tools/pr/prepr.sh`,
asserted to match exactly once. The run is `bash tools/pr/prepr.sh --self-test` under
`/etc/profile.d/hpo-toolchain.sh`. The count is the totals line, and the names are every `^  FAIL` line.
The driver is a scratch seat script.

- **M7** (review): `kill -TERM -- -"$rpid"` becomes `kill -TERM "$rpid"`. Result 320/3. All three
  reap arms fail with `got gone:gone:alive`: the lane is orphaned. This is the failing-first run for
  item 61eab2a5. At round 2's head the result was 323/0.
- **M9** (review): 6b's `closures_step "$BASE"` becomes `CLOSURES_LINE=$(closures_line "$BASE")`.
  Result 321/2. The TERM-alone arm and the group arm fail with `got alive:alive:alive`. This is the
  failing-first run for item 3fc47a16. At round 2's head the result was 323/0.
- **M4sub**: `closures_step` goes back to `$(closures_line ...)`. Result 321/2, the same two arms.
- **M3wd**: the watchdog body becomes `( : ) & wpid=$!`. Result 320/3, all three reap arms
  (`gone:alive:alive`).
- **M3setm**: delete `set -m`. Result 321/2, the KILL arm and the TERM-alone arm.
- **M1**: delete `closures_records_here`'s `return 1`. Result 319/4, the off-Linux default arm, its two skip-line arms and the `=0` arm.
- **M2**: delete the `PREPR_RECORD_CLOSURES` override line. Result 321/2, the opt-in arm and its
  refusal arm.
- **M6**: the override goes back to `[ -n ... ]`. Result 322/1, `PREPR_RECORD_CLOSURES=0 is no opt-in`.
- **M4** and **M5** stay at 323/0. Both are the equivalent mutants the review accepted (items 25985327
  and 7362c299), unchanged by this round.

## Null control

M0 (unmodified) gives 323 passed, 0 failed, at `c87bd1b27` and again at `df97bd446`. So every failure
above belongs to its mutant. The first pass, at `c5355e08f`, is the null for the copy-not-eval choice:
with the 6b block `eval`ed, M9 and M4sub each gave 323/0, and M7 already gave 320/3.

## Figures

- Self-test at `df97bd446`: `bash tools/pr/prepr.sh --self-test` printed `323 passed, 0 failed`.
- eval probe: a script with `trap 'exit 143' TERM` runs `X=$(g)`, where `g` waits on a job that forks
  `( sleep 300 )` and on a `$$` watchdog over that job's group. TERMed after 1 s and read 3 s later, the
  script printed `direct: prepr S lane S`, `ifonly: prepr S lane S`, `evalplain: prepr gone lane gone`
  and `evalif: prepr gone lane gone`.
- At `df97bd446`, under the seat toolchain with `PYTHONPATH=tests/hastub`, each rc 0:
  `node tools/policy/rules_sync.mjs --check` (`RULES-SYNC ok`).
  `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` printed
  `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, with `scope.run` = `tests/entities.py`.
  `python3 tests/entities.py` (`ALL 2382 ENTITY CHECKS PASSED`), `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`
  (`claims hygiene: 1ebc737e7... ok`), `python3 tests/closure.py selftest`, `python3 tests/layout.py`, `python3 tests/harness_headers.py`,
  `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`).
  `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` printed
  `Architecture score: dS +0.0000 NULL`.
- Class enumeration (step 8). `grep -n 'PREPR_RECORD:-' tools/pr/prepr.sh` returns one production line,
  in `closures_line`, which is closed. The sibling-seam rule from round 2 still returns 18 lines (steps 3
  to 3h), and this round leaves them as they were. See `## Forward-carry`.
- nightly-status filter: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -E '^(custom_components/|tests/replay|tests/hastub/|tools/replay/|tests/mutation)'`
  prints nothing (rc 1).

## Red checks

- `nightly-status` (job 119339580088 at the PR head). It grades main's last scheduled `Tests` run,
  39563978649 at `c77f89dc6`, which is still the latest scheduled run. On that run `slow` and
  `mutation-nightly` are red, and this diff reaches nothing either lane reads (the filter in
  `## Figures`). The red is main's, and no detector on this branch could catch or fix it.
- No other check is red at the PR head `5332c59f9` (check-runs API, 49 runs). This code head has not run
  CI yet.

## Forward-carry

- Sibling seams of the orphaned-recorder class: prepr's foreground heavy steps 3 to 3h, the 18 lines the
  round-2 rule returns. A KILL to the prepr orphans them, and a TERM to the prepr alone waits behind
  them. They lie outside this group's recorder scope. The fix shape is this diff's `closures_step`. They
  go to the programme's standing tracking issue, whose carry file is
  `dev/programme/carries/carry-201.json`. This seat writes no carry file, so the orchestrator owes the
  entry there, or the group or issue it cuts.
  Carry: #201 (item 11113f3e)
- Review items fixed at this head. Carry: dismissed: fixed at this head (item 61eab2a5).
  Carry: dismissed: fixed at this head (item 3fc47a16)

## Friction

none

## Approval

Policy half: `dev/governance/rules/gate-scoping.md` and its generated copies, which are unchanged since
round 2. They carry tvofi's 2026-10-20 ruling ("yes, do that": default-skip off Linux, CI's gate plus
`closures-autofix` as the owner, and an opt-in for a lane that needs a first-green head), made under
mandate 6175172275. It still owes tvofi's approving review at the head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_012q68Cp15toMHsw7DCRBPyM

