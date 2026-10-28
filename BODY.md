Triage batch 45 rules V141-V145 as P227-P231: **V141 → P227 ACCEPT narrowed → `R10-FLY-OPENPR-ATOMIC`**, **V142 → P228 ACCEPT narrowed → `R10-FLOW-MAIN-GATE`**, **V143 → P229 ACCEPT narrowed → `R10-ORCH-REVIEW-PACKET`**, **V144 → P230 DEFER → `R10-ORCH-BEATD`**, **V145 → P231 ACCEPT narrowed (a) → `R10-TRAIN-OVERLAP-GRADE`; (b) owned by `R10-RECORD-HOLD-APPROVE`**. Nothing is deferred outside round 10: the one DEFER names the round-10 group that already carries it. Headings carry no proposal id (P219). Round 1 (review of `75cfbce6f`) blocked on P228: the every-failed-job rule excluded its own instance's aggregating `gate` job, and the 23:43Z re-run time did not follow from the clock rule as written. Repaired at `8622b108d`; the 2 h 24 min figure is corrected to 2 h 30 min from the first failure. Round 2 (review of `ebbc01eaa`) blocked P228 claim-false: the gate rule read only `FAIL`-prefixed lines, but `tools/ci/gate.py:224` prefixes only the first reason and `:295` prints reasons 2..n bare, and the instance's own gate log names `validate / validate-hacs` on an unprefixed line (4373) after `FAIL governance / env-matrix: failure (this run)` (4372). Repaired at `2d296452f`: rule, Instances line, stamp fixture and absent-job null control now follow the two-reason shape, order-independent.

**P227 / V141 — ACCEPT narrowed → `R10-FLY-OPENPR-ATOMIC`** (done, 11 carries; reopen queued). Both openers run `git worktree add -q -b "$BR"` (`open_pr.sh:55`, `handoff_push.sh:198`) and `pr_release_wt` keeps the local branch after a successful push, so the next open of a reused topic stops on `fatal: a branch named ... already exists`. Measured: four opener logs with that line (two from each script), seven hand-numbered roster branches `-pr10`..`-pr16` among 47 roster-topic merges, and 18 of 22 local `fix/*-pr` branches absent on origin with tips in origin/main. Narrowed: one `pr_args.sh` helper called by both scripts, after their fetch, deleting the branch only when origin lacks it, a remote-tracking ref contains its tip, and no worktree holds it.

**P228 / V142 — ACCEPT narrowed → `R10-FLOW-MAIN-GATE`** (done, 1 carry; reopen queued). At the v7.0.5 stamp `e8cb7e683` `CI code` run 40596083060 attempt 1 has three failed jobs: validate-hacs (`GitHubRatelimitException`, 22:37:27Z) and env-matrix (`the GitHub API is unreachable`, 22:43:03Z) on the installation rate limit, and the aggregating `gate` (job 122526090837) on two reasons, `FAIL governance / env-matrix: failure (this run)` and the unprefixed `validate / validate-hacs: failure (this run)` on the next log line (4372-4373), which stayed red from 23:10:21Z until the hand re-run went green at 01:17:17Z (2 h 30 min from the first failure). Same class on 2026-10-26 at `b281d0325` (`dev/audit/rca/ratelimit-recur.md`). Narrowed: in the train's `main_green` (both modes), re-run failed jobs once only when every failed job other than `gate` matches one of three strings this tree's tools print and a failed `gate` qualifies: its reasons are the text after `FAIL ` on its outcome line (`tools/ci/gate.py:224`) plus each following unprefixed line up to `##[error]` (`:295`), read as a set; each must read `<job>: failure (this run)` naming a failed, matching job of the run (a `RATE-LIMITED reset_epoch=` gate, `:288-290`, is itself a matching job), only at attempt 1 (the counter is the bound, no state), and no sooner than the printed reset or 3600 s after the last matching non-`gate` job (23:43:03Z at the stamp). Controls: the two-reason stamp fixture is re-run in either reason order. Null controls: a `gate` whose first reason is a non-infra job, and a `gate` whose second, unprefixed reason names a job absent from the run's failures, are not re-run; a mutant reading only the `FAIL` line fails the second. The sweep-prompt block is not carried.

**P229 / V143 — ACCEPT narrowed → `R10-ORCH-REVIEW-PACKET`** (reopen already queued from batch 41). #2887's head `fdf33f466` is the bot's merge of the old head `fc841f51d` with main and `git merge-base --is-ancestor a5f40d84c fdf33f466` fails. A new packet signal `handoff-not-applied` refuses the dispatch, reading the head branch from the pull request the packet already fetches (no new API call). The sweep half is not carried: `bus.sh orphans` already prints `repair=update` (`bus.sh:692`).

**P230 / V144 — DEFER → `R10-ORCH-BEATD`** (not-started, 35 carries): carry 1 makes the relay a supervised beat job, carry 5 registers `heartbeat.sh`, carry 28 owns detection of a must-run loop that died unnoticed. `handover_prompt.py` has no loop list (`grep -c -i loop` = 0); the sweep script named is the orchestrator's own state file, not in the tree.

**P231 / V145 — ACCEPT narrowed.** (a) `merge_train.py:1110` discards `gh pr merge`'s return in `sweep_bots`, so #2893 logged only `(OPEN null)`: the carry puts `gh`'s refusal line into the `BOT` line. (b) The held approver beat is `R10-RECORD-HOLD-APPROVE`'s brief (move `nightly.yml`'s hold block after the approval, no `merge_train.py` change); a second approval path in the train is not carried.

The diff is one markdown file under `dev/programme/triage/` (INERT for `tests/closure.py`). Nothing is implemented and no roster file is edited; the roster ops are queued for the roster seat, held until this file is on main.

## Head

`2d296452f6db74afc8f8dd590f34daf27cb0d6dc`; the authored diff against merge base `53c4b9cb0` is one file, `dev/programme/triage/s6-batch45.md` (269 lines), plus this PR's delivery row `dev/programme/delivery/2900.md`. Round-2 re-cut: P228 only (Instances, Binding, carry text); P227, P229, P230, P231 byte-identical.

## Mutation proof

The gate this file feeds is `tools/audit/seat/roster_edit.py`'s `triage_refusal` (`ruling_verdict` at 455). On the committed tree, with the seat library on `sys.path`, the four carry texts the queued ops append (each ending `triage: dev/programme/triage/s6-batch45.md#P<n>`):

```
P227 ACCEPT / P228 ACCEPT / P229 ACCEPT / P230 DEFER / P231 ACCEPT / P999 None
carry P227 None
carry P228 None
carry P229 None
carry P231 None
mutant heading -> dev/programme/triage/s6-batch45.md#P228 is not an ACCEPT ruling (no such entry)
mutant DEFER -> dev/programme/triage/s6-batch45.md#P228 is not an ACCEPT ruling (DEFER)
```

The heading mutant renames `## P228:` to `## P228 (V142):` and the verdict mutant turns P228's `ACCEPT` into `DEFER`, both in memory; each refuses the same carry, so the gate reads this entry's heading and verdict.

## Null control

```
missing file -> the triage ruling dev/programme/triage/s6-batch45.md is not on the roster branch or origin/main
uncited -> proposal-sourced text cites no triage ruling (`triage: dev/programme/triage/<file>.md#P<n>`): 'proposal V142 text with no cite, triage P228'
```

## Figures

- `tools/audit/seat/open_pr.sh` at `07295d4ea`: rename to `-pr` at 37, `git worktree add -q -b` at 55; `handoff_push.sh` the same at 198, sources `pr_args.sh` at 114; `pr_release_wt` at `pr_args.sh:141-152`.
- `git log origin/main --merges --format=%s | grep -c 'tvofi/fix/audit-r10-roster'` = 47; `-pr10`..`-pr16` are #2812, #2823, #2842, #2851, #2857, #2861, #2864.
- Run 40596083060 attempt 1 failed jobs: 122512384418 validate-hacs 22:36:42Z-22:37:27Z, 122512384452 env-matrix 22:37:08Z-22:43:03Z, 122526090837 gate 23:09:58Z-23:10:21Z; attempt 2 `run_started_at` 01:07:45Z, `updated_at` 01:17:17Z. Per-job `grep -c -F` of the three strings: validate-hacs 1/0/0, env-matrix 0/0/1, gate 0/0/0; gate's reasons at 23:10:18Z, log lines 4372-4373: `FAIL governance / env-matrix: failure (this run)`, then `validate / validate-hacs: failure (this run)` unprefixed. The re-cut rule, run as a parser over that log (`shape.py`, seat scratch): reasons = both lines, qualifies = True; reasons swapped, True; second reason replaced by `tests / browser: SKIPPED (this run)`, False, while the FAIL-line-only mutant says True; env-matrix not a matching job, False.
- `tools/audit/seat/merge_train.py` at `07295d4ea`: 5,831 lines; `main_green` 2422-2450; `sweep_bots`'s `gh pr merge` at 1110.
- `tools/audit/seat/review_packet.py`: `SIGNALS` at 122, `pulls/<pr>` read at 324; `bus.sh` dispatch refusal on a packet REFUSE at 467.
- Roster at `origin/handoff/audit-r10-roster` `de410e4c9` (212 groups): `R10-FLY-OPENPR-ATOMIC` done, 11 carries; `R10-FLOW-MAIN-GATE` done, 1; `R10-ORCH-REVIEW-PACKET` done, 10; `R10-ORCH-BEATD` not-started, 35; `R10-TRAIN-OVERLAP-GRADE` done, 15; `R10-RECORD-HOLD-APPROVE` not-started, 0.

## Red checks

none

## Forward-carry

none

## Friction

none
