# Seat comms addendum, round 11 (owner ruling 2026-11-16, proposal P-R11-36)

Every cloud seat follows this beside its own brief. It adds liveness and an inbox, and it never overrides the brief.

1. **At start.** Fetch the script and initialise:

   ```
   git fetch origin f09b4d132306721b9ba65559516e079682604bfa && git show f09b4d132306721b9ba65559516e079682604bfa:seat_comms.sh > $HOME/seat_comms.sh && ROUND=11 bash $HOME/seat_comms.sh init <topic>
   ```

   `<topic>` is your dispatch topic: a fixer's or designer's topic or group id, a reviewer's `rev-<PR>`. A `snapshot <sha>` line means a previous fire left its working state there; resume from it with `git checkout <sha>`.
2. **Heartbeat.** Start `bash $HOME/seat_comms.sh loop 600` in the background with Monitor and no timeout. It beats every 10 minutes and polls the inbox. Each `CMD <n> <command>` line it prints is an orchestrator command.
3. **At each step of your brief** (a test written, a run finished, a push made): run `bash $HOME/seat_comms.sh ckpt "<the step>"`, then `bash $HOME/seat_comms.sh inbox`.
4. **Obey each command at once.**
   - `STOP`: finish the step in hand, ckpt, end the way your brief says a seat that must stop ends (a fixer: BLOCKED.md with a `Question:` line), then run `done`.
   - `RESUME`: go on.
   - `SKIP <what>`: drop that item and say so in your result.
   - `NOTE <text>`: guidance from the orchestrator, applied inside your brief.
5. **The comms ref is liveness only.** `handoff-wip/<topic>-comms` is never your return signal. The script never pushes `handoff/<topic>` or `handoff-wip/<topic>`, and nothing changes how you push those.
6. **At exit, on every path** (returned, blocked or refused): run `bash $HOME/seat_comms.sh done "<one line>"`.
7. **A failure of seat_comms.sh never blocks your work.** Name it in your result and go on.

## Open-axis rule (owner-approved 2026-11-21 under mandate 6893738184; RCA R11-RCA-3729-OPEN-AXIS)

Binds every fixer and fix reviewer from this fire until the role files carry it.

8. **Fixer: every quantified set has a rule or a category.** A class claim names, for every set it quantifies over, the rule whose output is that set, or places the whole set in the residue by a category the claim states (e.g. "any record a dependency writes when the package calls it"). A set named only by examples (a list, "such as", a census of one member) is neither: narrow the claim or state the category before handoff.
9. **Reviewer: block the axis, not its next member.** A seam that belongs to a set the claim quantifies over, read by no named rule and covered by no residue category, is one block for the set: `blocked <sha> class-open: axis <set> unenumerated (e.g. <seam>)`. Name the set; no hunt for further members is owed.
10. **Second block on the same axis escalates.** A body blocked on `class-open` on an axis already blocked once (as for a repeat `claims` block) goes to the orchestrator, which narrows the claim, splits or closes the fix; neither seat runs another round on that axis.
