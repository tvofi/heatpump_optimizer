# Proposal triage, session s10, batch 48 (P236)

One entry: V150, written by the orchestrator s10 on 2026-10-28 and numbered by this seat, quoted
from `proposals.md` as it stands. Every other id up to V149 has a ruling on `origin/main`
(batches 35-46) or in batch 47 (#2906, P235). Facts read at origin/main `6d86acc90`; roster at
`origin/main`'s `dev/programme/rosters/wave-r10-groups.json`.

## P236: two orchestrator sessions resume one round after a host reboot, and nothing refuses the second

Verdict: ACCEPT narrowed -- carried to **R10-ORCH-BEATD** (`resume.stage` `not-started`, 35
carries, design re-cut in progress). Its brief already owns "single-instance locks" so that "the
double start the design names cannot occur", and its carry 22 (P97) owns the duplicate *standing
seat*. The orchestrator session is the one process neither covers. Three narrowings, each forced
by a measurement below:
1. **Liveness by the session's own long-lived pid, matched by command, never by stop lines.** A
   reboot leaves no stop line (`seat-launch.sh`'s own header: "A crash leaves no stop line"), so
   a stop-line test reads the dead pre-reboot session as live at every resume -- the false
   DUPLICATE that header warns trains a reader to ignore the real one.
2. **Not `$PPID`.** The launch line's `sup=` is the calling shell, which dies with the call: the
   four `sup=` values of session s10's own launch lines are all dead while that session lives.
3. **At resume, before the first dispatch, not at a later sweep.** In the instance the earlier
   session dispatched within about 22 minutes of starting; a check at the first sweep may come
   after that. The later session refuses and stops; the earlier one proceeds.

Source: `proposals.md` V150 (orchestrator s10, 2026-10-28).

Instances: one, verified.
- `~/hpo-orch/r10s6/s7/ORCH-QUEUE.md:5002` (the orchestrator's queue): after the reboot at about
  07:07Z, pid 10472 started 08:16Z, wrote a resume block at 08:31Z and dispatched s9 seats at
  about 08:38Z. Pid 21371 started 08:19Z. On the owner's instruction 10472 was killed with its
  process tree, its s9 seats died with it, and nine seats were relaunched from 21371 as s10.
- The orchestrator's launch ledger has nine `post-crash relaunch` lines at 08:44:41Z (lines 53-61)
  and no `orchestrator` role line at all (`awk '$3=="orchestrator"' launch-ledger.txt` prints
  nothing). That is the gap the filing names.
- `ps -o etime= -p 21371` gives 57:48 at 09:17Z, so the start time is 08:19Z, and the process is
  `claude`. `ps -p` on 10472, 67903, 69863, 88215 and 90379 finds none of them; the last four
  are the `sup=` of s10's launch lines at 08:44, 09:01, 09:04 and 09:12Z.
- Host reboots this round: two. `seat-ledger.md:1058` records "host rebooted ~13:38Z" on
  2026-10-26, and `ORCH-QUEUE.md:5002` records about 07:07Z on 2026-10-28. One of the two
  produced a double resume.

Cost: inside R10-ORCH-BEATD, one more holder of the single-instance lock the group already
builds. That is a pid-and-start record that the resume step takes before its first dispatch, a
liveness read (`ps -p <pid> -o command=` names the session binary), a self-test, and a mutant.
At run time it is one local read per resume, with no GitHub API and no standing CPU. The
out-of-tree half (`seat-launch.sh`, `orch_sweep.sh` under the orchestrator's state directory;
`git ls-files | grep -c 'seat-launch\|orch_sweep'` = 0) is not a tree change. It is the
orchestrator's to make now, with narrowings 1-3, as P230 ruled for the same script. It is sent to
the orchestrator, not carried.

Binding: the measured cost of one instance is about 28 minutes of two live sessions (08:16 to
08:44Z), one session's dispatched seats lost, nine relaunched, and an owner intervention. Two
reboots in three days give one double resume. The tree cost is one lock holder on a mechanism
the owning group builds anyway, so the trade is clear. As filed it would not hold: stop-line
liveness and `$PPID` both misread, and a sweep-time check can come after the dispatch it should
prevent. Hence the ACCEPT is narrowed.
