# Architect-planner seat: round-11 plan revision 3 (objective re-plan, hybrid)

Repository tvofi/heatpump_optimizer. Model: Fable. Owner order, 2026-11-18: redo the round-11 plan so that it takes decision 0018's objective into account, starting from the current state, because work has already started. Treat this as a potentially catastrophic slip and make the best of the situation.

## Why this exists
`plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75 holds revision 2: `dev/audit/rounds/round11/PLAN/`. It was cut at fork 92d38ecb64, before main's `dev/governance/roles/architect-planner.md` gained this clause on 2026-11-17: "Decision 0018's objective ranks the work and the target is its floor: the plan's `objective` block predicts each term, ranks and keys each group and pins the projection; `plan_audit.py objective-check` passes before the push."

Revision 2's PLAN.json has no `objective` block, and objective-check was never run. The fix wave was dispatched on revision 2 and is running.

## Your contract
Read these, from origin/main and verbatim:
- `dev/governance/roles/architect-planner.md` (you are this seat)
- decision 0018 under `docs/decisions/`
- `dev/audit/config/objective.json`
- `tools/audit/seat/instruments/plan_audit.py.md`, which holds the objective grammar, ranks, edges and the floor cost

Also read revision 2's PLAN.md, REVIEW.md (the third plan review, `revise`) and the mandate decisions recorded in PLAN.md's "Open points" and "Applied 2026-11-18". Those decisions stand unless the objective forces a change; name each one you change.

## The current state you must plan from (re-measure it; do not trust this list)
- **Roster:** `origin/handoff/audit-r11-roster`, the newest `dev/programme/rosters/wave-r11-groups.json`. Every group's `resume.stage`.
- **Merged since the fork:** `git log --first-parent 92d38ecb64..origin/main`.
- **Open PRs and their heads:** `gh pr list` if you have gh, else `git ls-remote origin 'refs/heads/fix/*'`.
- **Designs in flight:** `design/*` and `design-verdict/*` refs.
- **Fixers in flight:** `handoff-wip/*` and `dispatch/fixer-*` refs.

Done work stays done. In-flight work is re-ordered or stopped only where the objective gains more than the work already spent, and you state the numbers. Prefer a hybrid: keep revision 2's groups, edges and moves where they survive, and change rank, order, edges or scope only where 0018 requires it.

## What you produce
1. **Revision 3** under `dev/audit/rounds/round11/PLAN/`, as a fast-forward of `plan/r11`. Never force-push.
   - PLAN.json gains the `objective` block in exactly the grammar of `plan_audit.py`'s OBJECTIVE_KEYS: baseline, pin, terms, groups with their rank and keys, edges, dispositions.
   - The pin's `--start` is now, not the fork.
   - PLAN.md states what the objective changed.
2. **`python3 -I tools/audit/seat/plan_audit.py objective-check --ref <your plan SHA> --write`** passes at your final SHA. The PROJECTION.json it writes is committed. Paste its output into `dev/audit/rounds/round11/PLAN/OBJECTIVE-CHECK.txt`.
3. **`dev/audit/rounds/round11/PLAN/CHANGES-R3.md`**: one row per change against revision 2, in a table with these columns:
   - group or edge or move
   - before
   - after
   - the objective term and rank reason
   - the effect on in-flight work (a PR, design or fixer to stop, re-order, re-scope or leave alone)
   - the hours it costs or saves

   "No change" rows are not needed. End the file with the dS target's standing after the changes: the score target is the floor.
4. Keep the score-target analysis of revision 2 valid, or restate it where your changes move it.

## Rules
- **No production code**, no PR, no seat dispatch, no roster edit. Changes to the roster are the orchestrator's, from your CHANGES-R3.md.
- **Identity:** before your first commit run `git config user.name tvofi` and `git config user.email 70032254+tvofi@users.noreply.github.com`. No Claude Code footer, no Co-Authored-By or Claude-Session trailer, and no claude.ai link in any commit. Check with `git log --format=%B` before each push.
- **Privacy:** never write a home-directory path or a host name into anything you push.
- **Cloud comms:**
  - Checkpoint each verified step by fast-forward to `refs/heads/handoff-wip/plan-r11-objective`.
  - Heartbeat at least every 20 minutes by pushing a commit there.
  - Poll `refs/heads/inbox/plan-r11-objective` (file INBOX) every 15 minutes. Its newest line rules.
  - Resume from `handoff-wip/plan-r11-objective` if it exists when you start.
- **Finish:** push revision 3 to `plan/r11` (fast-forward). Then write `DONE <plan SHA>` as the last commit message on `handoff-wip/plan-r11-objective`.
- **If you are blocked:** write BLOCKED.md with a `Question:` line on `handoff-wip/plan-r11-objective` and keep polling the inbox.
- Run heavy commands in the background, and never wait more than 240 s in one tool call.
