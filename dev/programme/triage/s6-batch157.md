# Proposal triage, session s14, batch 157 (P569)

This batch rules `s7/triage-queue-s7.txt` line 252, which arrived after batch 156. The bar and the
denominators are batch 141's.

Sources:
- origin/main `444cf62fab` (line numbers);
- `gh api rate_limit`, which costs nothing against the core bucket: the batch 155 sampler's log
  `s14/seat/triage/s14-4/rate.log` (20 s samples, 02:22:42Z to 02:40:28Z) and my own reads at
  03:01:26Z and 03:04:06Z;
- `S/tick-loop.log` (TICK-RELAY `started=` and TICK-PASS lines) and `S/beatd/journal.log` (PASS lines);
- `ps`, `lsof` and `ls` on this host.

## P569: S14-API-BUDGET-EXHAUSTED

Verdict: DEFER on (a) and (c), because neither benefit is measured, and the measurement the queue
line asks for cannot be taken: the instrument that splits calls by caller is not installed. (b): a
standing 600 s interval is REJECTED. Return the tick to 300 s once the bucket resets at 03:24:36Z.
The premise that the tick's 120 s interval was a material contributor is corrected below.

Source: queue line 252 (2026-11-11T02:59:52Z, the orchestrator).

Instances:
- **The exhaustion is real.**
  - `gh api rate_limit` read core `used 5000, remaining 0, reset 1794367476` (03:24:36Z) at
    03:01:26Z and again at 03:04:06Z.
  - The window opened at 02:24:36Z: rate.log reads 4759 used at 02:24:25Z and 5 at 02:24:45Z.
  - A false premise would have looked like remaining above 0.
- **The split cannot be taken: `gh_calls.py --top` has no log to read.**
  - The shim that writes the log (`tools/audit/seat/shims/seat-gh`, P284) is not installed.
    `~/.local/state/hpo/bin` holds only `python` and `python3`, dated 2026-10-14. Both are
    byte-identical to `shims/seat-python{,3}` on main.
  - `seat_venv.sh --install-shims` has installed the shim as `gh` since P284. That install was
    never re-run here, so `which gh` is `/opt/homebrew/bin/gh` for every caller whose PATH
    starts with that directory.
  - `$HPO_STATE_DIR/gh-calls.log` does not exist. `~/.local/state/hpo/gh-calls.log` holds 3
    lines, all from 2026-11-09T22:42Z to 22:43Z.
  - A false premise would have looked like a log with lines after 02:24Z.
- **What can be measured without the shim: an unexplained burst after 02:40Z.**
  - The model: about 36 calls a minute baseline (batch 155, with neither tick nor relay running)
    plus about 290 a tick pass, most of it in the pass's first 3 minutes (batch 155, 02:29:33Z to
    02:36:43Z).
  - The model fits 02:24:36Z to 02:40:28Z.
    - Predicted: 15.9 min x 36 = 572, plus the pass started 02:29:25Z (about 290), plus the first
      part of the pass started 02:38:47Z (about 100), about 960 in all.
    - Read: 979 used at 02:40:28Z (rate.log).
  - The model fails from 02:40:28Z to the first symptom at 02:58:45Z.
    - Predicted: 18.3 min x 36 = 659, plus the rest of the 02:38:47Z pass (about 190), plus the
      pass started 02:52:29Z (about 290), about 1140.
    - Read: at least 4021 (5000 - 979).
    - The excess is at least about 2880 calls in 18 min, at least about 157 a minute that neither
      the baseline nor the tick explains.
  - The beat is not the source. Its job mix from 02:24Z to 02:59Z (journal PASS lines: head-watch
    18, roster-drain 18, tick-digest 9, opener 8, pulse 7, cancel-sweep 4, one each of the rest)
    is the same per-hour mix as 01:00Z to 02:59Z (head-watch 61, roster-drain 53, pulse 24).
  - What the window does hold is seat work, by file modification time in `s14/seat/`:
    - dispatch packets and briefs for PRs 3404, 3429, 3430, 3431 and 3423, plus a `ppr` repair, at
      02:45Z to 02:57Z;
    - the remerge of PR 3377 (`push3377.log`, 02:57:35Z);
    - and the train (`train.log`).
  - Cloud seats spend the same token from another host. No log on this host sees them (the
    `gh_calls.py.md` blind spot).
  - The split among these is unmeasured.
- **Correction to the line's first-named contributor.** The 120 s interval was not material.
  - Pass starts (TICK-RELAY `started=`) were 02:20:46Z, 02:29:25Z, 02:38:47Z and 02:52:29Z. The
    120 s sleeps were 02:27:21Z to 02:29:25Z and 02:36:43Z to 02:38:47Z. The loop went back to
    300 s at 02:47:26Z to 02:52:29Z.
  - At 300 s throughout, the same window would have started passes at about 02:32Z, 02:45Z and
    02:58Z. The last would still have been in its first minute at the exhaustion. So at most one
    pass's spend differs: about 290 calls, about 6% of the 5000.
  - A false premise would have looked like a window whose excess over the baseline is mostly
    tick passes. The tick explains about 580 of at least 4021 calls after 02:40Z.
- **(a)'s partial guards already exist.**
  - `ci_probe.py` refuses below 20% remaining (lines 83 and 143-152).
  - `sweep_driver.py` backs off below 20% until the reset (lines 29 and 89-94).
  - `orchestrator_tick.py` reads `rate_limit` only at the end of its pass, after the spend. It
    warns below `RATE_FLOOR` 0.2 and never backs off (lines 165-166 and 1755-1765).
- **(c)'s capacity is not the binding one.**
  - At 03:01:26Z the GraphQL bucket read 288 used of 5000.
  - `app_mint.sh` mints only `hpo-author` (hard-coded file names), revokes the token on exit, and
    keeps it only in a mode-700 directory for one call's life.

Cost:
- (a) The minimal form, if it is accepted: move the tick's existing free `rate_limit` read to the
  start of the pass, and below the floor sleep to the reset instead of passing. The same check
  goes at the head of `beat_jobs.py`'s API-spending jobs. Both files belong to R10-TICK-RESIDUE
  (PR 3425, in progress, PART 2 prefix).
  - It guards only scheduled callers. This window's excess came from somewhere else: the tick
    explains about 580 of at least 4021 calls after 02:40Z, and the beat's mix did not change. So
    the guard would have delayed this exhaustion by minutes, not prevented it.
  - Ad hoc seat loops (`watch2.sh`, `wait6.sh` and the like) are scripts no code change reaches.
    Their bound is the 240 s poll floor the seat block already states.
- (b) Measured at 300 s, cycle gaps of 11:04 to 15:39, mean 12.2 min, give about 4.9 passes an
  hour, about 1420 calls.
  - At 600 s: about 3.5 passes an hour, about 1010 calls. That saves about 410 an hour, 8% of the
    bucket.
  - The price is a +5 min owed-line latency on every cycle, all day, on the orchestrator's main
    detector.
  - The headroom at 300 s is about 5000 - 2160 - 1420, about 1420 an hour. This window's burst
    (at least 2880) exceeds it at 600 s too (about 1830). So 600 s would not have prevented this
    exhaustion either.
- (c) It needs a read role for `hpo-runs` or `hpo-approver`. Decision 0011 assigns each App one
  duty, so this is an identity-policy change, with the owner's approval before merging.
  - It needs a cached installation token held across calls. That is a new secret at rest:
    `app_mint.sh` today never keeps one past its caller.
  - Every poll script would have to opt in.
  - It doubles capacity without naming the spender, so an avoidable loop stays hidden.
- No capped file is touched by this ruling. `tick_loop.sh`, `beat_jobs.py` and
  `orchestrator_tick.py` have no row in `tests/structure_budgets.json`.

Binding: the measurement comes first, and it costs no code.
- What changes (a): one exhausting or near-exhausting window (above 80% used) read through the
  installed shim with `gh_calls.py --top --since <window start>`.
  - If the scheduled callers (tick, beat, relay) are at least half of that window's spend, the
    start-of-pass guard passes as a carry to R10-TICK-RESIDUE.
  - If seat or ad hoc loops dominate, the remedy is the named loop, not a guard.
- What changes (c): after the spenders are attributed and duplicate loops are removed, a measured
  necessary read load still above about 4000 an hour. The route is then an owner-approved change
  to decision 0011.
- (b): the tick goes back to `--interval 300` after the 03:24:36Z reset. At 0 remaining, 600 s
  saves nothing until then.

Owed to the orchestrator, outside the roster:
- Install the shim with `tools/audit/seat/seat_venv.sh --install-shims ~/.local/state/hpo/bin`,
  run from a tools tree that will not be rotated away.
  - The install bakes that tree's `tools/pr/gh_comment.py` path into the shim's record-issue
    comment guard. If the tree is removed, the guard refuses every sanctioned post, which fails
    closed.
  - Installing also turns on that guard. It is not live today, for the same reason: the shim is
    not installed.
  - `gh_calls.py --coverage` reads `/proc`, which is Linux-only. Here, coverage is read off which
    parents show up in the log.
