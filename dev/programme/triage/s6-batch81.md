# Proposal triage, session s8, batch 81 (P318)

The rolling batch (V182) after batch 80 (handoff `triage-s8-batch80`). Facts were read at
origin/main `2376d3f9e`, on the roster branch, and in the `handoff-body/*` refs on origin.

## P318: tests/entities.py dies on macOS at the heartbeat sampler, hiding every later check

Verdict: ACCEPT narrowed, option (a), a carry on **R10-NIGHTLY-HB-RESPAWN** (`queued`, S). That
group owns the heartbeat lane's sampler seam (`tests/nightly_ha.py`), its after-edge
R10-NIGHTLY-PYSPY-RETRY is `done`, and it is dispatchable now. The carry adds `tests/entities.py`
to its files and may be dispatched alone, ahead of the group's other carries.
- **The rule.** The module-level arm at `tests/entities.py:18392`
  (`if _nightly.importlib.util.find_spec("_remote_debugging") is not None:`) runs
  `_hb_stdlib_reads` (line 18368), which samples a live child process. When that raises
  `PermissionError` on Darwin, the arm prints one named line,
  `SKIP stdlib sampler control: macOS denies the task port (<message>)`, and the module goes on.
  Every later check still runs.
- **The skip is that narrow on purpose.** It applies on `sys.platform == "darwin"` with
  `PermissionError` only. On Linux, where CI runs the arm, the error still fails, so the arm keeps
  its power where it is graded.
- **REJECTED (b), routing `entities.py` to a cloud or Linux run whenever the local host is
  Darwin.** It moves a 40,000-line script's whole run off-host to save one arm. Every local
  fixer's scoped gate would pay a cloud round trip, and local runs are the cheap path the gate is
  built on.
- **REJECTED (c), a seat-preamble note.** The run still dies at the same line, and every check
  after it is still unread. That is the exact cost below, which a note does not remove.

Source: the orchestrator s8's message of 2026-10-31 (a recurring slip, 3 instances on
2026-10-30/31).

Instances:
- **The defect, read at main.** `_hb_stdlib_reads` (`tests/entities.py:18368`) spawns a child and
  runs `_nightly._STDLIB_SAMPLE` against its pid. Its own docstring says a sampler of another
  process needs a privilege "which the heartbeat container is given and this host is not". The arm
  at line 18392 runs it at module top level with no handler, so the exception ends the script.
- **In fixer bodies.** Of the `handoff-body/*` tips on origin, four record the local death:
  - `r10-cop-partload-p2`: "the nightly lane's stdlib sample dies with `PermissionError: Cannot get
    task port` (macOS task-port entitlement). The same 44 FAIL li[nes at the merge base]".
  - `r10-fly-beat-fetch-race`: "Local run caveat ...".
  - `r10-hotfix-learner-inputs`: "Both runs then stop on the same ...".
  - `r10-ux-health-p2`: "`entities.py`'s heartbeat arm a task port for its own child".
- **The cost, by the orchestrator's account.** #3022 went red in CI on `entities.py`'s R10
  N-log-flood barrier, a one-line classification a full local run catches in about 6 min. The
  local run had died first, so the fixer read the base's identical death as "fails the same way
  on the base". That cost one review round and a hotfix delay.
- **Origin.** The arm arrived in `120cd1bb6` (2026-10-29, "nightly-ha: sample heartbeat stalls with
  CPython's own remote unwinder where it ships one", R10-FLY-NIGHTLY-HB, done). That is why the
  three instances cluster on 2026-10-30/31.

Cost:
- About 6 lines: a `try`/`except PermissionError` around the arm, gated on Darwin, printing the
  named SKIP. Add one self-test row.
- No new file, check or CI change. `tests/entities.py` is not a capped file.
- The scoped gate keeps running `entities.py` locally.

Binding: four fixer runs in two days lost every check after line 18392, and one of those misses
cost a review round on a hotfix, against a 6-line guard. Clearly positive. The guard is that narrow
so CI's Linux run still grades the sampler.

Carry text (for `roster_edit.py append-carry R10-NIGHTLY-HB-RESPAWN`, citing
`triage: dev/programme/triage/s6-batch81.md#P318`): "P318 (orchestrator 2026-10-31, recurring
slip). Adds tests/entities.py to this group's files. May be dispatched alone, ahead of this group's
other carries.
- The module-level arm at `tests/entities.py:18392` (at 2376d3f9e), which runs `_hb_stdlib_reads`
  (line 18368) against a live child, catches `PermissionError` only when
  `sys.platform == "darwin"`. It prints `SKIP stdlib sampler control: macOS denies the task port
  (<message>)` and lets the module continue.
- On any other platform, or any other exception, behaviour is unchanged: the arm still fails.
- Observed 2026-10-30/31: four fixer bodies record the local run dying there
  (`handoff-body/r10-cop-partload-p2`, `r10-fly-beat-fetch-race`, `r10-hotfix-learner-inputs`,
  `r10-ux-health-p2`). #3022 then went red in CI on a later `entities.py` check a full local run
  would have caught.
- Self-test rows:
  - With the sampler patched to raise `PermissionError` and the platform forced to `darwin`, the
    module reaches its final summary and prints the SKIP line once.
  - Null: forced to `linux`, the same raise still fails the run.
- One mutant: drop the platform condition, and the linux row passes when it must fail."
