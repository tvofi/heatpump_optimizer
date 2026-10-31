Triage batch 81 rules the orchestrator s8's recurring-slip proposal of 2026-10-31. `tests/entities.py` dies locally on macOS with `PermissionError: Cannot get task port` in its heartbeat stdlib-sampler arm, so every check after it is never run. #3022 then went red in CI on a check a full local run would have caught. This is the next rolling batch under V182, after batch 80. It holds one ruling and one held roster op.

- **P318: ACCEPT narrowed (option (a)), a carry on R10-NIGHTLY-HB-RESPAWN.** That group is queued and S, owns the heartbeat sampler seam, and its after-edge is done. The carry may be dispatched alone.
  - The module-level arm at `tests/entities.py:18392` catches `PermissionError` only on Darwin, prints a named `SKIP stdlib sampler control: macOS denies the task port`, and lets every later check run. On Linux, where CI grades it, the arm still fails.
  - REJECTED (b): routing `entities.py` off-host on Darwin, a cloud round trip for one arm on every local scoped gate.
  - REJECTED (c): a preamble note, which leaves the run dying at the same line.
  - Instances: four `handoff-body/*` tips record the local death (`r10-cop-partload-p2`, `r10-fly-beat-fetch-race`, `r10-hotfix-learner-inputs`, `r10-ux-health-p2`). The arm arrived in `120cd1bb6` on 2026-10-29.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`90b1324e39dfaa76bd76cd0d0051a81b8325eb2a`; the file is the whole diff against `2376d3f9e`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P318 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch81.md#P318`: it returns None.
- With `Verdict: ACCEPT narrowed` changed to `Verdict: REJECT narrowed`, the same carry is refused: `dev/programme/triage/s6-batch81.md#P318 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main. The carry, appended to the live roster, gives `brief_lint.mjs` `TOTAL: 0 error(s)`.

## Figures

- `git show origin/main:tests/entities.py` at `2376d3f9e`: `def _hb_stdlib_reads` at line 18368, and the module-level `if _nightly.importlib.util.find_spec("_remote_debugging") is not None:` at line 18392.
- `git log -S'_hb_stdlib_reads' origin/main -- tests/entities.py` names `120cd1bb6` (2026-10-29).
- `git show <ref>:BODY.md | grep -iE 'task port|task-port'` over every `handoff-body/*` tip gives the four bodies named above.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
