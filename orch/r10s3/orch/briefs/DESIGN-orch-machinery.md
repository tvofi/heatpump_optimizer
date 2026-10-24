# Design seat — the orchestration machinery: inventory, timing model, and an improved structure

Role: **design / pre-study seat** (not a fixer, not a reviewer). Repository `tvofi/heatpump_optimizer`.
Read from the tree, at your worktree's head: `CLAUDE.md` (the policy index), `dev/governance/roles/orchestrator.md`,
`dev/governance/roles/nudge.md`, `tools/audit/seat/INSTRUMENTS.md`, `dev/governance/rules/*.md`, and
`dev/governance/roles/fixer.md` only for what it says about instruments and self-tests.

**This is a LOCAL seat. Cloud dispatch is forbidden in this session.**

## The ask (owner, tvofi, 2026-10-20)

Map the **existing mechanical machinery** — the timing, sync and update mechanisms: the tick
(`tick_loop.sh`, `orchestrator_tick.py`), the relay (`cloud_relay.sh pass`, its handoff and probe arms), the beat
(`state_docs.py beat`), the sweep (`sweep_template.md`, `sweep_render.py`), the record beat (`record_row.py`), the
bus (`bus.sh`), the train (`merge_train.py`, `train.sh`), the PR openers/updaters (`open_pr.sh`, `update_pr.sh`,
`handoff_push.sh`, `delivery_row.sh`), the gate lease (`tests/gate_lock.py`), `wt_sync.sh`, `daemonize.py`, the
roster machinery (`roster_lib.py`, `roster_edit.py`), and the state/record surfaces (the plan ref, the state
mirror, `#201`, `dev/programme/delivery/`). Then **sketch an improved structure that is more robust, more elegant,
and harder to slip** — where "slip" means the process quietly stops doing its job, or does it twice, or reports a
state it does not have.

Not a list of bug reports. A design, with the evidence that motivates each element.

## Method

1. **Inventory from the tree and the live processes, never from a document's account of them.** For every
   mechanism: what starts it (cron, timer, a human turn, a GitHub event, a merge), its cadence and its timeout,
   the state it reads, the state it writes, whether it is level-triggered or edge-triggered, what it does when a
   read fails (fails open / fails closed / prints a pass), how it is stopped, and what survives a crash of the
   session that started it. Derive the counts; do not carry them.
2. **Draw the timing graph.** Which mechanisms can run concurrently, which assume exclusivity (the gate lease,
   the train pidfile, a branch's `upd-<branch>.lock`), where two writers touch the same file or ref, and where a
   read-then-write has no lease at all. Name the races you can actually construct, and construct them where cheap.
3. **Explain the observed slips.** These are inputs to verify, not conclusions to accept — each was recorded in
   this round and all but the first were seen by the orchestrator directly:
   - a 3.8 MB tick board and a 30,001-line dispatch list, produced entirely by re-printed OWED lines for refs whose
     work had long merged (`cloud_relay.log` had 29,741 lines; 200 residue refs were disposed in one pass);
   - roster `resume.stage` drifting silently (a group sat `not-started` while a seat worked it; another `planned`
     while its fixer was in round 3);
   - the tick's owner-gated age check counting `mandated approval under <id>` groups as "blocked on owner
     disposition" (9 of 14), which no owner act can unblock;
   - seats that stop writing and hold no child process for an hour while the harness still calls them running;
   - instruments dead after a session crash, restarted by hand;
   - `/usr/bin/git` breaking under a session (missing CommandLineTools) and every instrument silently depending on it;
   - an `update_pr.sh` starved for 30+ minutes in prepr under load, with no timeout and no progress signal.
   For each: name the mechanism that should have caught it, and why it did not.
4. **Design.** Propose the structure, and state for each element: the concern it owns (one owner per concern), the
   failure it makes impossible rather than detected, the default when a read fails, and its cost (seconds per pass,
   lines of code, lines of policy). Requirements the design must meet:
   - **fail closed** on an unreadable state, never print a pass it did not earn;
   - **level-triggered** obligations that repeat until disposed, with a disposal that cannot silently widen;
   - **bounded** output (a log line per event, a level line per pass — never a re-print per pass of a historical record);
   - **crash recovery** as a property of the state, not of a restart ritual;
   - **no parallel mechanism** where one exists: extend the tree's instrument rather than adding a second;
   - **instruments in the tree** (`tools/`, with `--self-test`), never in scratch (decision 0013);
   - every new check demonstrated failing on the defect it exists for, and passing once fixed (`defect-root-cause.md`);
   - **policy changes are the owner's**: propose them, name which of the four process states each addresses, and do
     not land them.
5. **Alternatives.** State at least two designs you rejected and why.
6. **Migration.** What lands first, what depends on what, what needs owner approval before merging, and what the
   existing rosters already own — the CI restructure (R10-CI-LAYOUT) and `roster_edit`'s ops (R10-ROSTER-OPS) are
   **given inputs, not yours to redesign**; name the seam where your design meets each.

## Environment

- Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/orch-design` (create it); worktree under it:
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/orch-design/wt -B handoff/orch-machinery origin/main`
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`.
- Live processes are part of your evidence: `ps`, the state dir `~/.local/state/hpo`, the orchestration scratch
  `/Users/timmalmstrom/hpo-orch/r10s3/orch` (read-only; do not write another seat's files). The relay log is
  `~/.local/state/hpo/cloud-relay.log`; the disposed ledger is `~/.local/state/hpo/cloud-disposed`.
- Do not stop, restart or edit any running instrument. Reading is yours; changing the live machinery is not.
- The box is heavily loaded; take wall-clock numbers with `load1` beside them, and prefer counts and structural
  facts over timings.

## Deliverables

1. `DESIGN.md` — the inventory table, the timing graph, the slip analysis, the design, the rejected alternatives,
   and the migration sketch. Every quantified claim names the command that produced it.
2. `EVIDENCE.md` — the commands and their output, including the perturbation or null control for each claim that a
   structure is or is not doing its job.
3. Push both on the body ref and report its SHA:
   `tools/audit/seat/body_push.sh` is for a handoff's BODY.md; for this deliverable push a branch instead:
   commit `DESIGN.md` and `EVIDENCE.md` under `dev/audit/design/orch-machinery/` in the worktree and
   `git push origin HEAD:handoff/orch-machinery`. Push refs only — no pull request, no GitHub write.
4. Report back: the ref SHA, the inventory's row count with its derivation, the three changes you consider
   load-bearing, and anything you could not establish.

A design-review seat reviews this adversarially afterwards; write it to survive a reviewer who re-runs every
command and plants a perturbation under every claimed mechanism.
