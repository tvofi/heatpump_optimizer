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

## P94: a git or gh read from a non-repo cwd reads blank and is reported as a state (S6-V29)
Verdict: ACCEPT NARROWED. (a) The one in-tree cause, the sweep template's unpinned `git ls-remote`, is a carry into R10-ORCH-BEATD, which owns `tools/audit/seat/sweep_template.md` under P45. (b) The out-of-tree cause, the roster seat's pass script, gets a no-code fix: the orchestrator edits its seat scripts. A general fail-closed wrapper for every read is REJECTED.
Source: s6 `proposals.md` `## V29`.
Instances: 2, from the orchestrator's account:
- The orchestrator's 23:49Z sweep ran `git ls-remote origin ...` from the r10s6 state directory and got "'origin' does not appear to be a git repository", so the probe and handoff refs went unread that sweep.
- The roster seat's pass script (w12) ran `gh pr view` outside a repository, got blank results, and for several passes reported #2761 and #2767 as "OPEN" without a real read.
Cause, read in the tree and in the s6 files:
- (1) `sweep_template.md` step (2) says to compare `git ls-remote --heads origin 'handoff/r{{round}}-*'` with the open heads, with no `-C`. Step (0) of the same template already pins `git -C {{orch_checkout}}`, so the placeholder exists and step (2) simply does not use it. The rendered s6 sweep line 9 carries the same unpinned command.
- (2) The s6 `roster-pass.sh` line 9 reads `s=$(gh pr view $n --json state,mergedAt ... 2>/dev/null)`. That has no `--repo`, so it depends on the cwd. Its errors are discarded, so a failed read is an empty string that the script then reports.
The in-tree instruments already pin and fail closed: `pulse.py` and `orchestrator_tick.py` take `--repo` and print UNREADABLE for an input they could not read. Both instances are prose or hand-written scripts, not instruments.
Cost:
- (a) One placeholder in one template line (`git -C {{orch_checkout}} ls-remote ...`), plus a `sweep_render.py` fixture row asserting that every `git ` command in the rendered sweep carries `-C`. The rendered sweep's other git and gh lines go through instruments.
- (b) Two edits to the out-of-tree `roster-pass.sh`: `--repo tvofi/heatpump_optimizer`, and a non-zero exit or an empty answer prints UNREADABLE in place of a state word. It is not in the tree, so it needs no PR.
Binding: each instance cost a sweep's refs or several passes of false state, and both causes are one line each, so the narrow fixes clearly pay. A general wrapper that every seat script must call for every git and gh read is REJECTED: the instruments already fail closed, and a wrapper binds only the scripts that remember to use it, so it would add a file without closing the class for hand-written scripts. The fixture row is the mechanical part for the template. For out-of-tree seat scripts, the standing rule is the one `INSTRUMENTS.md` already gives: use an instrument before hand-rolling a read loop.
What would change the answer: a third instance in a hand-written seat script after (b). That would mean seat scripts need an instrument, a read-only `--repo`-pinned state reader. Re-rule then.
Carry text (for `roster_edit.py append-carry R10-ORCH-BEATD`, citing `triage: dev/programme/triage/s6-batch20.md#P94`): "tools/audit/seat/sweep_template.md step (2): pin the handoff listing to the orchestrator's checkout, `git -C {{orch_checkout}} ls-remote --heads origin 'handoff/r{{round}}-*'`, as step (0) already does with `-C {{orch_checkout}}`. Evidence: the 2026-10-24 23:49Z sweep ran it from the state directory, got \"'origin' does not appear to be a git repository\", and read no probe or handoff refs that sweep. Controls: a tools/audit/seat/sweep_render.py fixture row asserting that every `git ` command in the rendered sweep carries `-C` (null: the old step (2) text fails the row); one mutant drops the `-C`."
