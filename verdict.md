Design review: revise f0f0469294c95f39b399c1392c1d393bebc4985c class-open

Reviewed: `dev/programme/designs/R10-ORCH-BEATD.md` at `design/R10-ORCH-BEATD` f0f046929, round 3 of 3. I read it from a detached worktree at that SHA. Code was read at the note's base `6d86acc90`. The prior verdicts read were `d93e1b1f2` (round 1) and `810697a5a` (round 2). The spike was re-run on this host (git 2.38.1, macOS): it reproduces the note's §3 table row for row. Token count: not reported by this harness.

This is the third `revise`. By `design-review.md` there is no fourth note: the designer re-cuts to the minimal shape the fixer can start from, and these points become carries. Each point below states the fix it wants, so the re-cut can carry it as written.

## Round-2 points

1. **Ref lock: answered in mechanism.** A retrying `git` shim on every beat job's `PATH`, measured against the two-real-fetcher race: B exits 0 with a retry, the null exits 1, and `HPO_GIT_RETRIES=0` exits 1. Inheritance through children, the `-C` skip mutant, and the dropped lock-timeout claims all hold. `git push` was also checked, as a further writer of remote-tracking refs: under the same held lock it exits 0, so the shim needs no push arm. The shim's PATH discovery is new revise point 2.
2. **`handoff-ahead`: answered.** It is in `KINDS`, written at the iteration's end at 421, 428, 442 and 443 (cloud_relay.sh, re-read), never on an rc 0 update, and the tick prints unflagged until 1200 s with 1200/1201 fixtures. One refinement is a carry below.
3. **Rows: answered.** The (b) rows' argv exist or land in (b), `phase` is dropped, and dispatch is `bus.sh dispatch-owed`, owned by the registry's owner. The heartbeat row's placeholder is a carry below.
4. **Hand launches: the grep is answered, its disposition is not** (revise point 1).
5. **(d): answered.** Merge is the only seat left. The (d1) and (d3) dismissals hold against `pulse.py:91` and `merge_train.py:721` and `:845`. The pulse attribution that (c) leaves stale is new revise point 3.

## Revise points

1. **class-open: two hand runs of the `state-docs` job's script survive the beat, and the note's count does not match its own command.**
   - **The count.** §5's command at `6d86acc90` prints 70 lines. Its launch-word filter prints **19**, not the note's 11. Eight of the 19 have no disposition (`evidence/hand_runs.txt`).
   - **The two hand runs that write.**
     - `dev/governance/roles/nudge.md:109`: the orchestrator runs `state_docs.py` "with its push flag" whenever the roster or PR set changes.
     - `dev/governance/roles/standing-merge.md:13`: the merge seat, which survives (c), runs `state_docs.py --push` after each merge. That line has no launch word, so the filter cannot catch it.
   - **Effect.** Each run pushes `handoff/audit-r<N>-plan` beside the beat's `state-docs` job, so the double-writer class of round-2 point 4 stays open. Neither run takes `orch-checkout`.
   - **Fix wanted:**
     - (c) rewrites both sites to "the beat's `state-docs` job runs it".
     - Or `state_docs.py --push` takes the `state-docs` job lock while `beatd.py held`, with a failing test, a null control (lock free) and a mutant.
     - Dispose of every line the filter prints, and widen the filter to an imperative `run`, or dispose of the whole name grep.
     - (c)8's control covers these sites, not only the eight rewritten ones.

2. **architecture-unsound / harness: the shim's real-git discovery loops forever, and it reaches the orchestrator's own `git`, which the note says it does not.**
   - **Discovery.** §3's rule, "the first `git` on `PATH` outside its own directory", compares strings. `evidence/shim_discovery.sh` and `.out` run the spike's `shims/git` (`git --version` under a 5 s timeout):
     - one absolute copy: rc 0;
     - a relative entry: rc 124;
     - a trailing slash: rc 124;
     - two copies of the shim directory: rc 124.

     Each 124 is an endless `exec` loop. On a fetch, the same loop forks without end.
   - **Reach.** `tools/audit/seat/sweep_template.md:51` tells the orchestrator to run "with `tools/audit/seat/shims` first on PATH". Once arm (a) puts `git` in that directory, every git call of the orchestrator's sweep goes through the shim. §3 says the shim "does not reach the orchestrator's hand fetches". The template's own wording, a relative path, is one of the hanging cases.
   - **Second copy.** `roster_queue.py:95-97` prepends `<edit-checkout>/tools/audit/seat/shims`. That is a second copy whenever the edit checkout is not the beat's checkout under the same spelling.
   - **Fix wanted:**
     - Resolve the real git once. Either `beatd.py` exports it, or the shim skips every candidate that is itself a shim (compared canonically, or by marker) and fails rc 127 instead of looping.
     - Either put the git shim in a directory of its own that only `beatd.py` prepends, or state and accept its reach into the sweep.
     - (a)6 gains the four cases above. Fixed: each returns within 5 s. Mutant: the string compare.

3. **class-open: after (c), `pulse.py` names retired seats.** `ARM_SEAT = {"opener": "dispatch", "state-beat": "merge"}` (pulse.py:92) and `seat_of` (201-211) prefix every STOPPED origin arm with `seat <name>:` (217-219). (c) changes `STANDING` and adds `RETIRED`, but names neither.
   - **What (c) leaves.**
     - A stopped opener and a stopped non-merge verdict both read `seat dispatch:`, a seat (c) retires.
     - A stopped state-beat reads `seat merge:`, but the state docs are now the `state-docs` job.
   - **Why it matters.** `pulse.py` is the off-host complement (§2), so the off-host alarm points at a seat that no longer exists (`evidence/pulse_arm_seat.txt`).
   - **Fix wanted:**
     - (c) routes `seat_of` through `RETIRED` to `job <name>` (and the state-beat arm to `job state-docs`), with one fixture per arm.
     - Mutant: leave `ARM_SEAT` as it is.
     - (c)'s pulse self-test, which compares contracts with `STANDING ∪ RETIRED`, also covers `ARM_SEAT`'s values.

## Notes for the fixer (carries)

- Triage P241 rules that `ledger.py` `review_owed` skips record and autofix PRs. The design does not contradict it: `bus.sh dispatch-owed` takes its pairs only from the board through `ledger.py owed-pairs`, and the board's `REVIEW OWED` lines are `review_owed`'s. That keeps one predicate. Do not add a second owed derivation in `bus.sh`. Add a (c)4 case: once P241 has landed, a board built from an open `record/` or autofix PR yields no dispatch. Carry: R10-ORCH-BEATD (item dr3-p241-record-skip)
- The `heartbeat` row's argv is `heartbeat.sh --once --message "BEAT <status line>"`. Nothing expands the placeholder, and the dr1 carry says the job calls `beatd.py status` itself, which `heartbeat.sh` does not. Make the row's argv a real one: a `beatd.py heartbeat` subcommand, or a `heartbeat.sh --message-file` that a beatd pre-step writes. (b)'s every-row flag check then tests it. Carry: R10-ORCH-BEATD (item dr3-heartbeat-argv)
- An rc 0 update that leaves the new head `nh` still not containing `hs` writes no `handoff-ahead` line, so it never alarms. Test `merge-base --is-ancestor "$hs" "$nh"` after the head read, and write the line when it fails. A failed update already writes `handoff-update`, which the tick flags at once. Say whether the 1200 s `handoff-ahead` line beside it is wanted. Carry: R10-ORCH-BEATD (item dr3-ahead-after-rc0)
- The spike `race.sh` fails under macOS `/bin/bash` 3.2 (`e[@]: unbound variable`: `set -u` with an empty array). The beat host is a Mac. The shim itself ran there, but (a)6's fixtures must run under bash 3.2. Carry: R10-ORCH-BEATD (item dr3-bash32)
- `orch-checkout` waits 60 s and then records `busy`, while `tick` holds the class for up to 900 s. Measure the tick's pass duration at main. If it routinely exceeds 60 s, `relay-probe` (every 120 s) goes `busy` whenever it overlaps a tick. Then either lengthen the wait or, now that the shim covers the race, drop `relay-probe` from the class. Carry: R10-ORCH-BEATD (item dr3-class-wait)
