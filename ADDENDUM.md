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
