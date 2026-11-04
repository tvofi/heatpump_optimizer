# The orchestrator sweep, as a template

This is a usage guide, not policy, in the sense `tools/audit/seat/INSTRUMENTS.md`
states for itself: it adds no obligation. It orders the recurring sweep a
Claude Code orchestrator session runs on a timer, names the instrument each step
runs by its tree path, and cites the rule file each step carries out. The role
is `dev/governance/roles/orchestrator.md`; the turn it names is
`dev/governance/roles/nudge.md`, which binds a Cursor orchestrator and is the
reference for any other agent's timer. Where this file and either of those
disagree, they are the rule and this file is the bug.

Render it, never hand-copy it:

    python3 -I tools/audit/seat/sweep_render.py --overlay <overlay.json> [--out <prompt.txt>]

The overlay is one JSON object holding every placeholder below, and nothing
else. It is the session's, so it stays out of the tree: it carries the dated
mandate and the host's own paths, which `nudge.md` keeps out of tracked text
for the same reason ("a date and a seat id in this file outlive the session
that measured them"). The renderer refuses a placeholder the overlay leaves
unfilled, an overlay key or a placeholder this table does not declare, a
declared placeholder the sweep never uses, and a home-directory path in the
rendered text that no overlay value supplied.

## Placeholders

| name | what the session supplies |
|---|---|
| `round` | the round number, as the `handoff/r<N>-*` refs spell it |
| `repo` | the repository as `<owner>/<name>` |
| `mandate` | the comment id of the owner's mandate in force on #201 |
| `seat_root` | the directory the session's seat worktrees live under |
| `orch_scratch` | the orchestration scratch directory (not a worktree) |
| `orch_checkout` | the orchestrator's own checkout, fetched before every re-read |
| `seat_ledger` | the session's seat ledger file, updated every sweep |
| `plan_slots` | `replan.py --slots`: concurrent fixer slots the plan schedules (10 unless the owner set another) |
| `plan_seats` | `replan.py --seats`: seats the plan may use (99 unless the owner set another) |
| `plan_json` | the plan JSON `replan.py --out` writes and `state_docs.py --plan` draws |
| `plan_page` | the plan page, `PLAN.html` in the state mirror (`state_docs.py --plan` writes it), republished at the same path |
| `state_mirror` | the directory `state_docs.py --mirror` writes |
| `tick_alive` | the tick seat's liveness file, touched every pass |
| `tick_log` | the tick seat's log |
| `tick_brief` | the tick seat's brief, the prompt a restarted tick seat receives |
| `tick_stale_min` | minutes after which a silent tick seat is dead |
| `transcript` | the session transcript `policy_reread_check.py` reads |
| `policy_stamp` | the policy re-read stamp `policy_reread_check.py` reads and writes |
| `disk_floor_gib` | free GiB on `/` below which finished worktrees are cleaned |
| `seat_queues` | `pulse.py`'s `--seat-queue SEAT=FILE` arguments, one per standing seat's session queue file |
| `seat_alives` | optional: `SEAT=FILE[:MIN]` entries, one per standing seat the session runs, whitespace-separated or a JSON list; each renders as `pulse.py --seat-alive ENTRY` (`FILE.d/<id>` holds the per-process entries). A seat listed with no alive file reads `UNREADABLE`, never skipped; none listed leaves the flag out |
| `launch_ledger` | optional: the launch ledger file (`<ts> <nonce> <role> ...` and `<ts> <nonce> stop` lines) for `pulse.py --launch-ledger`; empty leaves the flag out |

<!-- sweep:begin -->
ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} first. Run each instrument from its path in the tree, from {{orch_checkout}}, with `tools/audit/seat/shims` first on PATH. Then, briefly:

(0) Policy re-read. Run `python3 -I tools/audit/seat/policy_reread_check.py --transcript {{transcript}} --stamp {{policy_stamp}}`. On OWED: `git -C {{orch_checkout}} fetch origin`, then read `CLAUDE.md`, every policy file its index names, and `tools/audit/seat/INSTRUMENTS.md` with `git -C {{orch_checkout}} show origin/main:<path>`; act on any delta against current practice; then `python3 -I tools/audit/seat/policy_reread_check.py --stamp {{policy_stamp}} --write-stamp`, and log the re-read in {{seat_ledger}}. While the check prints OWED (exit 1), that is, until `--write-stamp` ran after the newest compaction, this sweep is not clean, whatever the rest of the board says.

(1) Seats. Cloud seats are uncapped. A fixer for a NEW roster group is dispatched only while fewer than 3 handoffs wait without a pull request and 6 to 10 pull requests are open (owner ruling, 2026-10-28; `tools/audit/seat/pr_cap.py` `dispatch-gate` measures its WIP arm); reviews, repairs and openers are never capped, and a ready critical-path group dispatches past every cap (`dev/governance/roles/orchestrator.md` section 5). Resume the next queued seat from {{seat_ledger}}. Dispatch a record pull request's reviewer (triage, roster batches) on sonnet, and a design, code or architecture pull request's reviewer on opus. Seat worktrees live under {{seat_root}}, each named absolute in its brief (`dev/governance/roles/orchestrator.md` section 5). A handed-off seat is not resumed and an unblocked roster group gets a fixer (`dev/governance/roles/nudge.md` steps 14 and 16).

(1b) Standing-seat liveness. The four standing seats are `dev/governance/roles/standing-tick.md`, `dev/governance/roles/standing-merge.md`, `dev/governance/roles/standing-dispatch.md` and `dev/governance/roles/standing-roster.md`. Run `python3 -I tools/audit/seat/pulse.py --repo {{repo}} {{seat_queues}} {{seat_alives}} {{launch_ledger}}`; a seat that is absent from {{seat_ledger}}, that finished with work still owed, or that a `PULSE` line reports `STOPPED` (`seat <name>:`, `DUPLICATE seat <name>:` or `FOREIGN <name>:`, a beat by a process that is not the seat) is restarted in this sweep on its contract with its queue, and the restart is logged in {{seat_ledger}}. Routine work goes to these seats as queue lines, never inline (`dev/governance/roles/orchestrator.md` section 5).

(2) Handoffs. Compare `git ls-remote --heads origin 'handoff/r{{round}}-*'` with the open pull-request heads, and run `tools/audit/seat/bus.sh orphans`. A handoff with no pull request gets `tools/audit/seat/open_pr.sh`; one ahead of its pull request gets `tools/audit/seat/update_pr.sh`; each runs detached under `tools/audit/seat/daemonize.py`, then `tools/pr/approve_held_runs.sh` on that branch, then `tools/audit/seat/bus.sh dispatch` and a reviewer seat at the printed head (`dev/governance/roles/orchestrator.md` section 5b; `dev/governance/roles/nudge.md` steps 1, 2 and 8).

(3) Merges. Verdicted pull requests go to one train on the hourly pitch: `tools/audit/seat/merge_train.py sweep --state-dir {{orch_scratch}} --mandate {{mandate}}` (detached under `tools/audit/seat/daemonize.py`; `tools/audit/seat/tick_loop.sh --sweep` runs it from the tick loop) builds the queue from the verdict bus and `add`s each verdicted head, starting `tools/audit/seat/train.sh` with `--overlap --approval-carry --skip-bad --free-holders --bot-prs --pre-flight --mandate {{mandate}}`, the recommended default (`dev/governance/roles/standing-merge.md`), when no train is running and otherwise loading that train's next batch, never a second live train (`dev/governance/roles/nudge.md` step 3; `dev/governance/roles/orchestrator.md` section 11). The open record or autofix pull request merges inside that train through `--bot-prs`, not between pitches. A budget-file or policy head goes the batch's serial route, where `--pre-flight` parks a budget raise or a policy head the owner has not approved at that head under an open mandate (`Train.raise_hold`, `Train.policy_gate`); a parked one merges directly under mandate {{mandate}} (`dev/governance/roles/nudge.md` steps 5 and 7; `CLAUDE.md` rule 2). Between pitches, a record or autofix pull request merges by hand only behind `tools/audit/seat/record_row.py --automerge-check` (`dev/governance/roles/nudge.md` step 6).

(4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #201 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), and the finished seat's worktrees under {{seat_root}} and its scratch removed.

(4b) Record beat, every sweep, merge or none: `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, which publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. Exit 1 there is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): re-run the replan, never hand-run `plan_page.py` around the refusal.

(4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first.

(4d) Queue priority, for the train, review, fixer and CI queues alike: a push to main; then critical path and hotfix; then production pull requests with instrument pull requests saving 12 h or more; then other instruments by savings. A group's critical-path standing is the roster's `critical` list (`tools/audit/seat/roster_lib.py` `critical_path`); the gate order is `tools/pr/gate_priority.py`'s.

(4e) CI capacity. Cancel each superseded workflow run, one whose head is no longer its pull request's head: read `gh run list --json databaseId,headSha,headBranch,status,event` against each open pull request's `headRefOid`, and `gh run cancel` the stale ones. Never cancel a run on main or on a critical-path or hotfix pull request's live head. `tools/pr/cancel_superseded.py` does the same from inside one workflow run, and its `sweep --repo R` does it from here, for every open pull request in one pass (never a main or push-event run, never a bot-authored live head).

(5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one in the background on `dev/governance/roles/standing-tick.md`, whose prompt is the contents of {{tick_brief}}; it runs `tools/audit/seat/orchestrator_tick.py`. Log the restart in {{seat_ledger}}. Read {{tick_log}}'s newest pass unfiltered: every `OWED`, `REVIEW OWED`, `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:` line, none truncated, and give each an action this sweep (`dev/governance/roles/standing-tick.md`); the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`). The `pulse.py` lines step (1b) printed name each consumer whose owed input is waiting on it (opener, verdict router or train, state beat, a standing seat's queue): drive that consumer before the rest of the sweep, and log it in {{seat_ledger}}; `UNREADABLE` is not a clean board. Then run `python3 -I tools/audit/seat/owed_unactioned.py --tick {{tick_log}} --state {{orch_scratch}}/owed-unactioned.json --acks {{seat_ledger}}`: it reads the tick's whole owed family (never a `grep | head` or `tail` of it) and exits 1 on each owed line that has stood two sweeps with no live `OWED-ACK` line. Each such line gets its action this sweep, or an `OWED-ACK` line in {{seat_ledger}} naming its next action and what it waits on; an acknowledgement lapses after its ttl, so the next sweep re-checks the handling. The sweep is not done while it exits 1, and its 2 is `UNREADABLE`, never clean (`dev/audit/rca/R10-RCA-OWED-UNACTIONED.md`).

(6) Verdicts and CI. Read any moved `review/*` or `probe/*` refs and the cloud runs; confirm each verdict at its exact head with `tools/audit/seat/bus.sh confirm` (`dev/governance/roles/nudge.md` step 1). A red required check at an open head goes back to its fixer with the line `tools/audit/seat/failure_logs.sh` prints (`dev/governance/roles/nudge.md` steps 4 and 15).

(7) Proposals. A process, tooling or instrument proposal this sweep met (a seat's result, a verdict's optimisation note, your own) is sent to triage on `dev/governance/roles/proposal-triage.md`, never implemented or routed before its ruling; an ACCEPT reaches the roster through the roster seat, citing its ruling.

(8) Disk. If `df -h /` shows under {{disk_floor_gib}} GiB free, collect finished worktrees with `tools/audit/worktree_gc.sh {{repo}}`.

Keep the turn short; update {{seat_ledger}}.
<!-- sweep:end -->
