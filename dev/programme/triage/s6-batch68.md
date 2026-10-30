# Proposal triage, session s8, batch 68 (P299)

The rolling batch (V182) after batch 67 (#2983, merged at `b646e8306`). Facts were read at
origin/main `b646e8306`, in the orchestrator's state directory (`seat-ledger.md`,
`s7/launch-ledger.txt`, `s7/orch_sweep.sh`, `s7/seat-launch.sh`, `s7/HANDOVER-s8.md`) and from
`ps`.

## P299: a standing seat's alive file is fresh while no seat exists

Verdict: ACCEPT narrowed. Two halves, because the instrument the filing names is out of the tree.
(a) In tree: one carry on **R10-ORCH-BEATD** (`in-progress`), amending its P97 carry
(`s6-batch21.md#P97`), the `--seat-alive` per-seat-id arm of `tools/audit/seat/pulse.py`. It is
not a new group. (b) Out of tree: the orchestrator makes the filing's nonce check in its own
`orch_sweep.sh` and seat briefs now, as P236 ruled for the same scripts (`s6-batch48.md#P236`).
That half is sent to the orchestrator and not carried. The filing's form is narrowed in two ways.
The nonce is compared with the newest launch of the role that has no stop line, never with "any
live launch". The board's `ok` wording changes, because a fresh file was never a seat.

Source: `s7/triage-queue-s7.txt` line 13 (orchestrator s8, 2026-10-30T09:33:31Z, slip).
`orch_sweep.sh` printed `ok merge seat beat 50s ago` while no merge seat existed. An orphaned
41 h-old zsh loop, pid 29401, left behind by a past seat's Bash call, kept touching
`s7/merge.alive`. The live train ran across a session handover with no seat watching it.

Instances. This is the same class as P188 (`s6-batch32.md`) and P204 (`s6-batch36.md`): an alive
file written by a process that is not the seat the board names.
- **This one.** `seat-ledger.md:2463` reads `orch s8: stopped orphan beat loop pid 29401 (touched
  merge.alive with no seat); launched merge seat e9e6d824886e8e82` at 09:33:22Z. A loop 41 h old
  at 09:33Z started about 16:30Z on 2026-10-28. That is before the last s7 merge launch,
  `8741ed6aeec213f0` at 21:31:35Z (`awk '$3=="merge"' s7/launch-ledger.txt`). So it was a
  predecessor's loop, the case step (1d) of the sweep's P188 interim says to stop by PID at
  relaunch (`sweep.md:47`). That step was not taken at the 21:31Z relaunch.
- **The window it masked, measured.** The merge seat's last own line is `seat-ledger.md:2454`
  (`merge s7 SLIP for triage`, after 08:29:43Z). `s7/HANDOVER-s8.md` dates the handover about
  09:20Z, and the relaunch is 09:33:16Z. The s8 sweep's ListAgents step found the missing seat
  13 min after the handover. The board's `ok` line covered at most about 1 h. In that time the
  train ran on and merged #2981, #2982 and #2983. The s8 seat's first pass then found
  `#2978/#2973 verdicts name old heads, left out` (`seat-ledger.md:2464`).
- **P188, two instances (2026-10-25).** The w41 `loop.sh` touched `dispatch.alive` with its agent
  gone, for up to 22 min, and an hour after w43 had replaced it. `roster.alive` was fresh with no
  roster process.
- **P204 (2026-10-27).** Two triage writers shared `triage.alive` for 90 min.
- **Count.** Four instances in round 10, so this is an audit class (`defect-root-cause.md`). It
  owes a barrier, not a refusal. The barrier is already owned in tree: R10-ORCH-BEATD carries P46
  (`--seat-alive`), P97 (one alive entry per seat id, DUPLICATE) and P63 (a generation token).
  This ruling closes the one gap in those carries that the instance shows.
- **The gap in P97.** P97 reads one alive entry per seat id "beside the per-role file". It does
  not say what a role reads when the per-role file is fresh and no id entry is. That is pid
  29401's shape: an unattributed writer, and no seat.
- **The launch ledger is itself red right now.** `seat-launch.sh --dup merge` prints `DUPLICATE: 2
  live launches for role 'merge'` (8741ed6a, e9e6d824). `--dup triage` prints the same
  (25222de4, ef0ff4b2). No `--stop` was written for the dead s7 nonces at the s8 relaunches,
  though `seat-launch.sh`'s header names that as the dispatcher's obligation. "Newest launch
  without a stop" is still well defined under that noise. "The live launch" is not, which is
  narrowing 1.

Cost:
- (a) is XS inside an L group already in progress. It is about 10 lines in the `--seat-alive` arm
  and three fixture rows. There is no new file, check, API call or standing CPU. `pulse.py` is not
  a capped file.
- (b) is about 10 lines in `orch_sweep.sh`'s standing-seats loop, plus one word per standing
  brief (`echo <nonce> >` in place of `touch`). It is out of tree
  (`git ls-files | grep -c 'orch_sweep\|seat-launch'` = 0). It adds no review round.
- No capped file is touched. The `--budgets` rows of the files nearest the seam stay as they are,
  and this ruling adds nothing to them:
  - `dev/governance/roles/standing-merge.md` 37/37 lines, 507/507 words.
  - `standing-roster.md` 27/27, 368/368.
  - `standing-dispatch.md` 39/39, 509/509.
  - `proposal-triage.md` 36/36, 489/489.
  The nonce reaches each seat through its brief, which is out of tree.

Binding:
- **Benefit.** Four instances of one class in one round. The newest put a false `ok` on the board
  for up to about 1 h over a live train. A false `ok` is the failure this check exists for
  (`orch_sweep.sh`'s own header: the 10 h dead merge seat). Its cost is a few lines in a group
  already being built. That is clearly positive, and the class rule binds anyway.
- **Rejected in the filing's form: "the nonce of the newest live seat-launch.sh entry".** "Live"
  in `seat-launch.sh` means "no stop line". The ledger reads DUPLICATE for two roles today, so it
  is ambiguous. Narrowed to the newest launch line for the role with no stop line, compared by
  equality.
- **Recorded limit, not carried.** A nonce does not tell a seat from its own orphaned loop: P188's
  first 22 min, where the agent died and its `loop.sh` went on writing w41's id. P63's generation
  token and P51's rule (a seat waits in a `run_in_background` job it re-arms on its own turn,
  never a detached `while` loop) already own that sub-case.

Carry text (for `roster_edit.py append-carry R10-ORCH-BEATD`, citing
`triage: dev/programme/triage/s6-batch68.md#P299`): "Amends carry P97 (the `--seat-alive`
per-seat-id arm of `tools/audit/seat/pulse.py`); P299, queue 2026-10-30T09:33Z.
- The per-role `<role>.alive` file alone never makes a role live. Liveness is read only from id
  entries.
- A role whose per-role file is fresh while no id entry is fresh prints `FOREIGN <role>:
  unattributed beat`.
- A fresh id entry whose id is not the newest launch line for the role without a stop line, in the
  launch ledger `pulse.py` is given (`--launch-ledger FILE`, the `<ts> <nonce> <role> ...` /
  `<ts> <nonce> stop` format of the orchestrator's `seat-launch.sh`), prints `FOREIGN <role>:
  <id> (newest launch <nonce>)`.
- Both forms are a STOPPED-class line for the role, never `ok`.
- Observed 2026-10-30: pid 29401, a 41 h-old zsh loop from a merge seat launched before
  `8741ed6aeec213f0`, kept `merge.alive` fresh with no merge seat. The orchestrator's board
  printed `ok merge seat beat 50s ago` across the s7 to s8 handover.
- Controls:
  - A fresh per-role file with no id entry gives FOREIGN.
  - A fresh entry under an id older than the newest unstopped launch gives FOREIGN.
  - Null control: a fresh entry under the newest unstopped launch is ok. That holds even when an
    older launch of the role has no stop line, which is the DUPLICATE-noise case P97's arm
    reports separately.
  - One mutant per arm: the per-role fallback restored, and the newest-launch comparison
    dropped."

To the orchestrator, not carried (out of tree, P236 precedent):
1. Each standing brief has its seat write its launch nonce into `<role>.alive` on every pass.
   `orch_sweep.sh`'s standing-seats loop then reads the content and compares it with the newest
   unstopped launch for the role (`awk '$3==r' launch-ledger.txt | tail -1`, less stopped
   nonces). A mismatch or an empty file prints `FOREIGN BEAT <role>` with rc=1. The `ok` line
   reads `ok <role> beat <n>s ago, nonce <8>` and names presence as ListAgents' (step 1d).
2. Write `seat-launch.sh --stop` for the dead s7 nonces now: merge `8741ed6aeec213f0` and triage
   `ef0ff4b26c23dd66`. Until then the board's seat-launches section reads DUPLICATE for both roles
   on every sweep.
