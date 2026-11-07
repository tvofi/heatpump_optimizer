# Proposal triage, session s12, batch 131 (P402)

The rolling batch after batch 130. Facts were read at origin/main `be813ecd4` and at the roster branch `a791d7843`, and in the orchestration logs. The logs are host-local, so another seat re-runs those commands only on the host that holds them.

## P402: stamp-flush-train-hold-deadlock, the record flush waits on a train hold it never names

Verdict: ACCEPT narrowed. The proposal has two halves, and only the first one passes.
- **The flush half: ACCEPT, changed.** The flush must name the hold, but it must not refuse because of it. It must also stop spending its dispatches while a hold blocks them.
- **The train.sh trap half: REJECT.** An EXIT and TERM trap that releases the hold is already in the tree. A trap cannot catch the one signal that the tree does not already cover.

The destination is a new fly-in group, R10-FLY-STAMP-FLUSH-HOLD (S, `tools/release/stamp.py`). No group that is still open owns `stamp.py`'s flush. This ACCEPT is not taken on the >10 % exemption.

Source: the orchestrator's queue line `s12-stamp-flush-train-hold-deadlock`, 2026-11-07.

Instances:
- **The flush (origin/main `tools/release/stamp.py`):**
  - `record_flush` (line 2410) dispatches `nightly.yml` once.
  - It then polls `record_merges_since` every `FLUSH_POLL_S = 60` s.
  - It re-dispatches only when `record_pr_green()` holds and the last dispatch is at least `FLUSH_REDISPATCH_S = 900` s old, up to `FLUSH_MAX_DISPATCHES = 3`.
  - It gives up at `FLUSH_TIMEOUT_S = 7200` s with `record flush: no record merge landed within 7200s of N dispatch(es)`.
  - `flush_before_tag` (line 2487) prints that message and stamps without the flush.
  - No line in either function reads `train-hold` (`git show origin/main:tools/release/stamp.py | grep -c train-hold` gives 0).
- **Where the beat honours the hold:** `.github/workflows/nightly.yml`, from line 1063, reads `GET /commits/train-hold`.
  - A hold younger than `HOLD_MAX_AGE_S=3600` makes the beat print `::notice::a merge train is live` and exit 0 as `skip-train-hold`. That happens after the guard and the review, and before the merge.
  - A hold at or past the bound is stale, and the beat merges.
  - The dispatches the flush sends during a live hold each end in `skip-train-hold` and merge nothing.
- **The deadlock, from the constants:**
  - The three dispatches go out at about 0, 900 and 1800 s. A hold that stays live past the third one leaves the flush with no dispatch left.
  - A killed train's hold stays live for up to 3600 s after its last refresh.
  - From then on, only an unrelated push to main or the 00:37 cron (`nightly.yml` line 28) can merge the record PR. In a stamp window, main is quiet.
  - So the worst case is the whole 7200 s, ended by a message that names no hold.
- **The trap half, in the tree:**
  - `train.sh` lines 432 to 440 install `pr_exit_trap` (`pr_args.sh` line 253) as an EXIT trap.
  - `pr_reap` TERMs the lead first (`pr_lead_stop`, at most `PR_REAP_LEAD_TENTHS=300`, 30 s), and the lead is `merge_train.py` itself (line 480, `PR_REAP_LEAD=$!` after `exec`).
  - `merge_train.py` `stop_on_signal` (line 306) turns TERM and HUP into `SystemExit`. `Train.train`'s `finally` (line 2459) and the batch path's `finally` (line 3184) both call `hold_release`, which DELETEs the ref.
  - SIGKILL and a host crash remain, and no trap runs on either. The beat's 3600 s bound already covers both.
- **The incidents:**
  - `seat-ledger.md` line 4442, `SLIP 2026-11-07T06:22:50Z stale-train-hold-deadlocks-stamp`, says the merge seat killed train 37335 (batch `20261107-061538`, `TRAIN HOLD refs/heads/train-hold b588ae95` in `tick.txt` line 6). The hold paused the beat that the v7.1.5 flush waited on, and the orchestrator deleted it by hand.
  - `s12/seat-merge-STATE-HANDOFF.md` line 54 records the earlier case, on 2026-11-06 at 21:30Z. A train was killed by PID (74476 and 74529), and its orphan hold was deleted by hand.
  - That is two orphan holds in about 9 h, and both came from kills.
  - The queue line's figures are 23 min and then a second stall. They come from the orchestrator and were not re-measured here, because the stamp log `s12/stamp-715.log` holds one line and no flush line.
  - The flush has existed since 2026-11-06T07:24Z (`git log -1 --format=%cI origin/main -- tools/release/stamp.py`). One stamp, v7.1.4, ran it cleanly. The next stamp hit this case.
  - `git ls-remote origin refs/heads/train-hold` is empty at 06:26Z.
- **A likely gap, not measured:** in both cases the kill went to the process, not to train.sh's own stop.
  - On 2026-11-06 both PIDs were killed together. That way `merge_train.py` receives a second TERM from train.sh's `pr_lead_stop` while it is already unwinding.
  - `unwind` raises `SystemExit` again inside whichever `finally` is running at the time, for example in `release_worktrees` before `hold_release`. That would leave the ref behind on a plain TERM.
  - No self-test drives a signal through `hold_release`. The nearest arm, `merge_train.py` line 4853, is a train stopped mid-queue by a `Stop`, not by a signal.
  - This is the binding's first probe. It is not ruled as fact.
- **The rule on the instance:** with the change, the 11-07 stall prints `refs/heads/train-hold b588ae95 ... pid=37335` at the first poll, within 60 s, instead of after 23 min with no line. A dispatch sent under a live hold is not counted, so the flush dispatches again once the hold clears. The hold commit's own message, `train hold pid=<n>` (`merge_train.py` line 2415), names the train. With the stale bound, the flush still lands by itself at no later than about 3600 s plus one poll, with no hand deletion. Today it can run the whole 7200 s and then stamp without the flush.

Cost:
- About 25 lines in `record_flush`:
  - a `held` collaborator injected like `ready`;
  - one printed line when the hold appears, changes or clears;
  - a dispatch sent under a live hold is not counted toward `FLUSH_MAX_DISPATCHES`, and the next one goes out when the hold clears;
  - the timeout message names a hold that is still live.
- About 20 lines of self-test arms in the existing flush block (from line 1858), for these cases:
  - a planted live hold is named, and no dispatch is spent under it;
  - a stale hold is ignored;
  - an absent hold behaves exactly as today, which is the null control;
  - a mutant that counts the held dispatch must exhaust at 3, and the arm catches it.
- **The hold read costs no REST call.** `record_merges_since` already runs `git fetch origin` every poll. `git ls-remote origin refs/heads/train-hold` tells whether the ref is present, and the fetched object's committer date gives its age. That avoids the shared `FETCH_HEAD` and a pruned ref left as stale. The flush adds no load to the account's 5000-an-hour core budget, which the train and the relay share.
- `HOLD_MAX_AGE_S` must have one source. `stamp.py` reads it from `nightly.yml`'s `HOLD_MAX_AGE_S=` line by a source read, the way `train.sh` reads `RECOMMENDED`. It does not get a second literal 3600.
- `stamp.py` had 7 commits on origin/main since 2026-10-24, so it is not hot. No `tests/structure_budgets.json` metric reads `tools/` (`PACKAGE_DIR` is `custom_components/heatpump_optimizer`), and `stamp.py` is not a `policy_lint.mjs --budgets` row.
- It is an S fly-in: a sonnet fixer and one opus review.
- **Benefit:**
  - On the 11-07 instance, detection drops from 23 min to at most 1 min. That is 22 min off the stamp's critical path, or 22 % of the flush's own p90 wait of 6129 s, the figure `FLUSH_TIMEOUT_S` was sized from.
  - A killed-train hold no longer turns a flush into a 7200 s timeout followed by a stamp without the flush. It becomes a wait of at most 3600 s that recovers by itself.
  - Two orphan holds in 9 h make this a recurring case, not a one-off.
- **Why it narrows instead of refusing:**
  - A live train legitimately holds the beat, and with `--bot-prs` the train merges the record PR itself. A refusal would turn that wait into a full stamp re-run.
  - A held flush that names the hold, and recovers once the hold clears, makes the same information actionable without that cost.

Binding:
- New fly-in group R10-FLY-STAMP-FLUSH-HOLD: lane F, S, files `tools/release/stamp.py` and `tools/audit/seat/merge_train.py`, fixer sonnet, reviewer opus, effort medium. The brief text: `From triage batch 131 (triage: dev/programme/triage/s6-batch131.md#P402 at <roster sha>): stamp.py record_flush waits for a record merge while refs/heads/train-hold, younger than nightly.yml HOLD_MAX_AGE_S=3600, makes every beat it dispatches exit skip-train-hold; its 3 dispatches (0, 900, 1800 s) are spent under the hold and it times out at 7200 s naming no hold. Inject a held collaborator into record_flush, defaulting to a zero-REST git read (ls-remote origin refs/heads/train-hold for presence, the fetched commit committer date for age, the commit message pid), with the bound read from nightly.yml by source read, never a second literal. Print one line naming the hold sha, age, pid and bound when it appears, changes or clears; do not count a dispatch sent under a live hold toward FLUSH_MAX_DISPATCHES, and dispatch again when it clears; name a still-live hold in the timeout message; never refuse on a hold. Self-test arms in the existing flush block: a planted live hold is named and spends no dispatch, a stale hold is ignored, an absent hold is unchanged (null control), a mutant counting the held dispatch exhausts at 3 and is caught. First, before the stamp change: probe merge_train.py with a stubbed gh, TERM both the train.sh pid and the merge_train.py pid at once mid-run, and record whether the hold DELETE is issued; if a second TERM during the unwind skips hold_release, make the unwind ignore further TERM and HUP once it starts (as pr_reap does) with a self-test arm and a mutant; if the DELETE is issued, record that as a non-finding and change nothing there. No train.sh trap change: pr_exit_trap already TERMs merge_train.py first.`
- The fixer re-measures the constants, the line numbers and the orphan-hold instances at its own base and does not carry them.
