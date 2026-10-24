# Proposal triage, session s6, batch 20 (P93-)

Rulings from the s6 `proposals.md`, collected 4 or 5 to a pull request under
tvofi's batching rule of 2026-10-24 (one PR per ruling only when it unblocks
critical-path work). Numbering continues after `s6-batch19.md` (P88-P92, #2767,
unmerged at this base).

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P93: pulse --seat-queue prints UNREADABLE for every standing seat at every sweep (S6-V28)
Verdict: DEFER -> R10-ORCH-BEATD, which already owns the fix as P46's `--seat-alive` arm. Interim, no code: the orchestrator stops passing `--seat-queue` in its sweep and judges the seats by `<seat>.alive` age, as it already does. Making pulse accept the queues' format is REJECTED.
Source: s6 `proposals.md` `## V28`.
Instances: pulse at 20:09:44Z and 21:29:48Z both printed `seat-merge/roster/dispatch UNREADABLE: its queue could not be read`, from the orchestrator's account. This is the recurrence P46 (`s6-batch2.md`) predicted: "the same misreading is scheduled to repeat every sweep".
Cause, measured in the s6 queue files: `read_queue` in `tools/audit/seat/pulse.py` takes each non-blank line as `int(line.split()[0])`, so one non-epoch line makes the whole file UNREADABLE (`ValueError`). In the three queue files, counting non-blank lines whose first field is not an integer epoch:

| file | non-blank lines | non-epoch lines |
|---|---|---|
| `merge-queue.txt` | 35 | 11 |
| `roster-queue.txt` | 244 | 226 |
| `dispatch-queue.txt` | 9 | 2 |

The non-epoch lines are `#` header comments and ISO-8601 stamps such as `2026-10-24T07:50Z ...`.
The queues are also append logs. `judge_queue` assumes the seat removes a line when it acts ("an input the orchestrator queued and the seat removes when it acts"), but the roster queue alone holds 244 lines for the day. So even a format-tolerant reader would read every seat as STOPPED by its oldest line.
Cost: the interim costs nothing, one argument fewer in the orchestrator's sweep. The real fix is P46's: about 15 lines for a `--seat-alive SEAT=FILE[:MIN]` arm judged on the `.alive` mtime, plus fixtures and mutants. It is already carried into R10-ORCH-BEATD (the carry citing `s6-batch2.md#P46`).
Binding: the arm judges nothing today. It cannot raise a STOPPED, so a dead seat is caught only by the `.alive` age the orchestrator reads anyway; running it each sweep costs output and attention for no signal. Making `read_queue` accept `#` lines and ISO stamps is REJECTED: on append-log queues it would turn the false UNREADABLE into false STOPPEDs, and a false STOPPED makes the sweep restart a live seat (P46's worst case, a duplicate merge seat). Rewriting every seat's queue habit to remove acted lines is the four-seat contract change P46 already REJECTED on cost.
What would change the answer: R10-ORCH-BEATD waits behind R10-ORCH-DISPATCH-REG (not started), R10-POLICY-FIXER-MD (in progress) and R10-ORCH-REVIEW-PACKET (not started), on the roster branch. If the orchestrator wants the alive arm before those land, P46 already named the split: item 2 alone as an XS group (`pulse.py`, `INSTRUMENTS.md`) after the drain, carrying P46's text unchanged.
