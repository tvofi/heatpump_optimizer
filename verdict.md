Design review: approve 32e249d2ed66bd8dfd7f158efedeb93b306edac5

Reviewed: `dev/programme/designs/R10-ORCH-BEATD.md` at `design/R10-ORCH-BEATD` 32e249d2e. This is the re-cut after the third `revise` (`1d5cdad0f`), and the first review of that re-cut. It is a fast-forward of `f0f046929`.
- I read it from a detached worktree at that SHA.
- Code was read at the note's base `6d86acc90`/`0b8f8b585` (`git diff --stat` empty over the policy and seat paths, confirmed).
- Every spike and fixture was run on this host under macOS `/bin/bash` 3.2.57.
- Token count: not reported by this harness.

As the re-cut rule directs, arm (a) is judged as the minimal start, and points that belong to (b) or (c) are carries, not blockers.

## Round-3 points

1. **Hand runs: answered.**
   - **Coverage.** The note disposes of the whole name grep, 23 rewritten and 47 kept. I compared it by `file:line` against the grep's 70 lines at `6d86acc90`: it is an exact cover, with nothing undisposed and nothing extra (`evidence/hand_run_cover.txt`).
   - **The four state-docs hand runs.** All four are real: `nudge.md:89` and `:109`, `standing-merge.md:13`, and `sweep_template.md:63`.
   - **Stays.** I spot-read the 32 `INSTRUMENTS.md` stays: each describes an instrument and instructs no launch.
   - **(b)8's rc-75 refusal is sound.**
     - It is keyed on `held` plus `HPO_BEATD_JOB != state-docs`, so the job's own push inside `beat` (265) passes.
     - `--mirror` alone is never refused.
     - Its second mutant, `held` alone, is the right one, because it would refuse the job itself.
     - It is closed twice, by mechanism and by text.
2. **Shim discovery and reach: answered** (`evidence/shim_rerun.out`).
   - **Re-run.** The re-cut `beatd_shims/git` returns rc 0 within 5 s on every case of my `1d5cdad0f` `shim_discovery.sh`: relative entry, trailing slash, two copies. The spike's `discovery.sh` reproduces its table, and no real git gives rc 127, not a loop.
   - **Marker read.** The line-2 marker is read with `read` only, so the no-`head` mutant is real.
   - **Poisoned `HPO_REAL_GIT`:**
     - a shim copy, the shim itself, a relative path to it, a missing file and empty all fall back to the PATH walk, rc 0;
     - **a directory gives rc 126**, and an arbitrary executable is trusted (both are carries below).
   - **Reach.** A directory of its own that only `beatd.py` prepends keeps the shim out of `sweep_template.md:51` and `roster_queue.py:95-97`, and it closes the reach point.
3. **`pulse.py` seat names: answered.** `seat_of` is routed through `RETIRED`, with one fixture per arm in (c)9. The `ARM_SEAT` mutant and the self-test widened to `ARM_SEAT` values are what point 3 asked for.

## The designer's three flagged decisions

1. **`handoff-ahead` only on rc 0 and still behind; rc ≠ 0 writes `handoff-update` only: sound, with one gap.** One alarm per cause holds for 443 (failed) and 421 (recorded skip), because both already carry a `handoff-update` line that the tick flags at once. But "rc ≠ 0" also reads as excluding busy rc 75 (442) and no body (428). Neither writes any level line today, and round 3 had both writing `handoff-ahead`. Read that way, a perpetually busy branch or a missing body never alarms, which is item 18 (a)'s case. That is carry dr4-ahead-busy-nobody, owned by (b).
2. **`relay-probe` leaves `orch-checkout` if the tick's p90 is over 60 s: sound.** The class existed for the fetch race, which the shim now covers, and the level writes are behind `level_rmw`. The measurement source is the weak part. A `TICK-PASS` line carries only the pass's end time, so a duration is the gap between lines less the sleep interval (tick_loop.sh:113-114, 233), or a direct timing of `orchestrator_tick.py`. Name the derivation (carry dr4-tick-duration).
3. **(b)/(c) cite round-3 text at `f0f046929`: accepted.** It is what `design-review.md`'s re-cut prescribes, the minimal shape plus carries. `f0f046929` is an ancestor of this head on the design ref, and the note states that its own points override that text. The (b) and (c) fixers' briefs must cite the SHA, never the ref.

## Notes for the fixer (carries)

- Arm (a). The shim accepts `HPO_REAL_GIT` on `-x` and not a shim. A directory passes `-x`, so the shim `exec`s it and returns rc 126. Require `-f`, as the PATH walk's `! -d` already does. `beatd.py` is the only setter, and it should also confirm that its resolved git answers `--version` with `git version`, because the shim trusts any executable it is handed (`/bin/echo` gives rc 0). Add both to (a)6's discovery cases. Carry: R10-ORCH-BEATD (item dr4-real-git-validate)
- Arm (b). `handoff-ahead`: the busy (442, rc 75) and no-body (428) ends write no other level line, so they keep writing `handoff-ahead` with `since=`. Only 421 and 443, which already write `handoff-update`, skip it. The (b)4 fixtures are each end separately. Carry: R10-ORCH-BEATD (item dr4-ahead-busy-nobody)
- Arm (b). For the class-wait measurement, state how a pass duration is derived. `TICK-PASS` holds only the end time (tick_loop.sh:113-114), so a duration is either the gap less `--interval` or a direct timing of `orchestrator_tick.py` over N runs. Put the command and N in the body. Carry: R10-ORCH-BEATD (item dr4-tick-duration)
- Arm (b). The grep's scope is the policy corpus, but the tick's own board still tells the reader to run the push that (b)8 refuses: orchestrator_tick.py:1593 renders "run python3 tools/audit/seat/state_docs.py --push" and :1653 "record beat owed: state_docs.py --push". The docstring at :1556 also argues that "a timer push would race merge beats", which is moot once the merge seat no longer pushes. In (b), rewrite them to name the `state-docs` job, together with the self-test assertion at :2969. Also give the refusal message a pointer to `beatd.py status`, so a failing `state-docs` job is diagnosed rather than hand-pushed around. Carry: R10-ORCH-BEATD (item dr4-tick-state-text)
- Arm (c). Main moved after `0b8f8b585`: `b9a66d28d` adds 2 lines to `INSTRUMENTS.md` at 400, so every `INSTRUMENTS.md` citation past 400 in §5 is off by 2 at `71fe1f7fc`. (c)8 keys on text, which is correct; re-derive the line list at (c)'s merge base, and never pin line numbers in the control. Carry: R10-ORCH-BEATD (item dr4-instruments-shift)
- Arms (b) and (c). Each fixer's brief cites the round-3 reference text as `f0f046929` §3 and §6 by SHA, and this note's overrides by `32e249d2e`. Carry: R10-ORCH-BEATD (item dr4-cite-by-sha)
