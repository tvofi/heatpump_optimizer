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
| `mandate` | the comment id of the owner's mandate in force on #201 or #3394 |
| `seat_root` | the directory the session's seat worktrees live under |
| `orch_scratch` | the orchestration scratch directory (not a worktree) |
| `orch_checkout` | the orchestrator's own checkout, fetched before every re-read |
| `seat_ledger` | the session's seat ledger file, updated every sweep |
| `plan_slots` | `replan.py --slots`: concurrent fixer slots the plan schedules (10 unless the owner set another) |
| `plan_seats` | `replan.py --seats`: seats the plan may use (99 unless the owner set another) |
| `plan_coordinator_cap` | `replan.py --coordinator-cap`: the plan's coordinator cap (replan's own default when absent) |
| `plan_json` | the plan JSON `replan.py --out` writes and `state_docs.py --plan` draws |
| `plan_page` | the plan page, `PLAN.html` in the state mirror (`state_docs.py --plan` writes it), republished at the same path |
| `state_mirror` | the directory `state_docs.py --mirror` writes |
| `tick_log` | the tick board, the file `tools/audit/seat/tick_loop.sh --out` writes and the beat's `tick-digest` row reads; never a tick seat's own log |
| `digest` | the beat's digest directory, `$HPO_STATE_DIR/digest`, which `tools/audit/seat/beat_jobs.py` alone writes |
| `transcript` | the session transcript `policy_reread_check.py` reads |
| `policy_stamp` | the policy re-read stamp `policy_reread_check.py` reads and writes |
| `disk_floor_gib` | free GiB on `/` below which finished worktrees are cleaned |
| `seat_queues` | `pulse.py`'s `--seat-queue SEAT=FILE` arguments, one per standing seat's session queue file |
| `seat_alives` | optional: `SEAT=FILE[:MIN]` entries, one per standing seat the session runs, whitespace-separated or a JSON list; each renders as `pulse.py --seat-alive ENTRY` (`FILE.d/<id>` holds the per-process entries). A seat listed with no alive file reads `UNREADABLE`, never skipped; none listed leaves the flag out |
| `intake_since` | the UTC time the outside intake starts from (the round's opening); the beat's `outside-intake` row keeps its own cursor past it |
| `launch_ledger` | optional: the launch ledger file (`<ts> <nonce> <role> ...` and `<ts> <nonce> stop` lines) for `pulse.py --launch-ledger`; empty leaves the flag out |
| `train_state` | optional: the merge train's state dir; the `cancel-sweep` row passes it as `--train-state`, so a pull request in the train's queue or spool is never cancelled for a priority run; empty leaves the flag out |
| `gantt_roster` | the roster the beat's `gantt` row reads, as `<branch>:<path>` (fetched to `refs/gantt/roster`, never a local branch) |
| `gantt_acks` | the Gantt acks file `sweep_gantt.py --acks` reads, one `<ISO> <KEY> act\|defer\|accept [until=<ISO>] <reason>` line per answered slip |
| `fire_ledger` | the session's fire ledger, one line per seat fired with its leading UTC stamp, which the `gantt` and `verdict-audit` rows hand on as `--fired` (a line within 12 h holds the pull request or topic it names) |
| `sweep_record` | optional: the day's sweep record file, rendered `scorecard.py --sweep-record FILE`; whose `recycle` lines of the standing dispatch and triage seats the `scorecard` row counts as K (absent: K prints unread) |
| `train_glob` | the glob of live train logs `verdict_audit.py --train-glob` reads (a log modified within 3 h holds its queued pull requests) |
| `train_log` | the live merge train's `train.log` (`$HOME/.local/state/hpo/merge_train/train.log`), which the beat's `bottleneck` and `plan-beat` rows hand on as `--train-log` (the skip-share alert and the plan page's train-skips table) |
| `unheld_skip` | the skip file `verdict_audit.py --skip` reads, one `#<N> <ruling>` line per pull request held by an owner ruling |

<!-- sweep:begin -->
ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} first. Run each instrument from its path in the tree, from {{orch_checkout}}, with `tools/audit/seat/shims` first on PATH. Then, briefly:

(0) Policy re-read. Run `python3 -I tools/audit/seat/policy_reread_check.py --transcript {{transcript}} --stamp {{policy_stamp}}`. On OWED: `git -C {{orch_checkout}} fetch origin`, then read `CLAUDE.md`, every policy file its index names, and `tools/audit/seat/INSTRUMENTS.md` with `git -C {{orch_checkout}} show origin/main:<path>`; act on any delta against current practice; then `python3 -I tools/audit/seat/policy_reread_check.py --stamp {{policy_stamp}} --write-stamp`, and log the re-read in {{seat_ledger}}. While the check prints OWED (exit 1), that is, until `--write-stamp` ran after the newest compaction, this sweep is not clean, whatever the rest of the board says.

(1) Seats. Cloud seats are uncapped. A fixer for a NEW roster group is dispatched only while fewer than 3 handoffs wait without a pull request and 6 to 10 pull requests are open (owner ruling, 2026-10-28; `tools/audit/seat/pr_cap.py` `dispatch-gate` measures its WIP arm); reviews, repairs and openers are never capped, and a ready critical-path group dispatches past every cap (`dev/governance/roles/orchestrator.md` section 5). Resume the next queued seat from {{seat_ledger}}. Dispatch a record pull request's reviewer (triage, roster batches) on sonnet, and a design, code or architecture pull request's reviewer on opus. Seat worktrees live under {{seat_root}}, each named absolute in its brief (`dev/governance/roles/orchestrator.md` section 5). A handed-off seat is not resumed and an unblocked roster group gets a fixer (`dev/governance/roles/nudge.md` steps 14 and 16).

(1b) Standing-seat liveness. The two standing seats are `dev/governance/roles/standing-merge.md` and `dev/governance/roles/standing-dispatch.md`. Run `python3 -I tools/audit/seat/pulse.py --repo {{repo}} {{seat_queues}} {{seat_alives}} {{launch_ledger}}`; a seat that is absent from {{seat_ledger}}, that finished with work still owed, or that a `PULSE` line reports `STOPPED` (`seat <name>:`, `DUPLICATE seat <name>:` or `FOREIGN <name>:`, a beat by a process that is not the seat) is restarted in this sweep on its contract with its queue, and the restart is logged in {{seat_ledger}}. Routine work goes to these seats as queue lines, never inline (`dev/governance/roles/orchestrator.md` section 5).

(2) Handoffs. The beat's `opener` and `head-watch` rows (`tools/audit/seat/beat_jobs.py`, run by `tools/audit/seat/beatd.py`) open each handoff that has no pull request through `tools/audit/seat/open_driver.py` and record each moved head: act on every `OWED ... open-refused`, `NEEDS-TITLE`, `STARVED` and `STUCK` line of {{digest}}/digest.txt and every `HEAD-MOVED` and `STUCK` line of {{digest}}/events.txt. Cross-check `git -C {{orch_checkout}} ls-remote --heads origin 'handoff/r{{round}}-*'` against the open pull-request heads, and run `tools/audit/seat/bus.sh orphans`. A handoff ahead of its pull request gets `tools/audit/seat/update_pr.sh`, and one the opener refused or left `STUCK` gets `tools/audit/seat/open_pr.sh` once its reason is answered; each runs detached under `tools/audit/seat/daemonize.py`, then `tools/pr/approve_held_runs.sh` on that branch, then `tools/audit/seat/bus.sh dispatch` and a reviewer seat at the printed head; a `HEAD-MOVED` line at a reviewed head owes the same at the new head (`dev/governance/roles/orchestrator.md` section 5b; `dev/governance/roles/nudge.md` steps 1, 2 and 8).

(3) Merges. Verdicted pull requests go to one train on the hourly pitch: `tools/audit/seat/merge_train.py sweep --state-dir {{orch_scratch}} --mandate {{mandate}}` (detached under `tools/audit/seat/daemonize.py`; `tools/audit/seat/tick_loop.sh --sweep` runs it from the tick loop) builds the queue from the verdict bus and `add`s each verdicted head, starting `tools/audit/seat/train.sh` with `--overlap --approval-carry --skip-bad --free-holders --bot-prs --pre-flight --mandate {{mandate}}`, the recommended default (`dev/governance/roles/standing-merge.md`), when no train is running and otherwise loading that train's next batch, never a second live train (`dev/governance/roles/nudge.md` step 3; `dev/governance/roles/orchestrator.md` section 11). The open record or autofix pull request merges inside that train through `--bot-prs`, not between pitches. A budget-file or policy head goes the batch's serial route, where `--pre-flight` parks a budget raise or a policy head the owner has not approved at that head under an open mandate (`Train.raise_hold`, `Train.policy_gate`); a parked one merges directly under mandate {{mandate}} (`dev/governance/roles/nudge.md` steps 5 and 7; `CLAUDE.md` rule 2). Between pitches, a record or autofix pull request merges by hand only behind `tools/audit/seat/record_row.py --automerge-check` (`dev/governance/roles/nudge.md` step 6).

(4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #3394 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), and the finished seat's worktrees under {{seat_root}} and its scratch removed.

(4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given.

(4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first. The beat's `verdict-audit` row (`tools/audit/seat/verdict_audit.py`, reading {{fire_ledger}}, the train logs {{train_glob}} and the skip file {{unheld_skip}}) prints an `UNHELD` line in {{digest}}/digest.txt for each pull request whose next step nobody holds: give each a holder this sweep, or put a pull request held by an owner ruling on {{unheld_skip}} (owner ruling, 2026-11-06: no pull request waits unheld). The beat's `bottleneck` row (`tools/audit/seat/bottleneck_check.py`, reading the train log {{train_log}} and the cap {{plan_slots}}) prints a `BOTTLENECK:` line in {{digest}}/digest.txt once per trip of a flow metric past the owner's threshold, with a suggested action: decide whether to act on it this sweep; the line takes no action itself (owner request, tvofi 2026-11-07). A `BOTTLENECK-UNREADABLE:` line is a metric the alert cannot see.

(4d) Queue priority, for the train, review, fixer and CI queues alike: a push to main; then hotfix; then accepted outside issues and contributions (a roster group with `source: outside`, which `roster_edit.py set-source` writes) together with the critical path, one rank unordered between them (owner rulings tvofi 2026-11-07, triage P420, and 2026-11-08); then production pull requests with instrument pull requests saving 12 h or more; then other instruments by savings. A group's critical-path standing is the roster's `critical` list (`tools/audit/seat/roster_lib.py` `critical_path`); hotfix and top-rank standing are `roster_lib.dispatch_rank`'s, which `tools/pr/gate_priority.py` (hotfix the lease's top band, outside and critical path the next) and the tick's OWED order apply; `open_driver.py`, the train's drain and `tools/plan/replan.py`'s `dispatch_tier` (the plan page's tier) hold the same order from `roster_lib.is_outside`.

(4e) CI capacity. The beat's `cancel-sweep` row runs `tools/pr/cancel_superseded.py sweep --repo {{repo}}` every 10 minutes: it cancels each superseded workflow run, one whose head is no longer its pull request's head, for every open pull request in one pass, never a main or push-event run and never a bot-authored live head; `tools/pr/cancel_superseded.py` does the same from inside one workflow run. Act on each of its failure lines in {{digest}}/digest.txt. Never cancel a run on main or on a critical-path or hotfix pull request's live head by hand.

(5) Tick digest. Read {{digest}}/digest.txt whole, never truncated: the beat's `tick-digest` row writes there the board {{tick_log}}'s actionable family, every `OWED`, `REVIEW OWED`, `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:` line among it, and its `owed-check` row the `UNACTIONED` lines of `tools/audit/seat/owed_unactioned.py`, which runs there once per sweep and never by hand (it counts every run as a sweep). Give every line an action this sweep, and print `grep -c '^-> ' {{tick_log}}` and `grep -c 'OWED' {{tick_log}}` beside the actions taken: an `OWED` line is a level re-printed every pass, not a diff; the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`). A disposition that defers a line to a seat names that seat's ledger id or PID, and the next sweep re-checks it; one naming no seat is not a disposition. The `pulse.py` lines step (1b) printed name each consumer whose owed input is waiting on it (opener, verdict router or train, state beat, a standing seat's queue): drive that consumer before the rest of the sweep, and log it in {{seat_ledger}}; `UNREADABLE` is not a clean board. Each `UNACTIONED` line gets its action this sweep, or an `OWED-ACK` line in {{seat_ledger}} naming its next action and what it waits on; an acknowledgement lapses after its ttl, so the next sweep re-checks the handling. The sweep is not done while the digest holds an `UNACTIONED` line, and `owed-check: UNREADABLE` is never clean (`dev/audit/rca/R10-RCA-OWED-UNACTIONED.md`).

(5b) Outside intake. The beat's `outside-intake` row runs `tools/audit/seat/outside_intake.py list --since {{intake_since}}` with its cursor and writes its `OUTSIDE` lines to {{digest}}/digest.txt (`dev/governance/roles/orchestrator.md` section 5): an `owed=triage` line gets a triage or design seat this sweep and ends wired into a roster group through the `roster-drain` queue, with that group's `source` set by a queued `set-source <GROUP> outside` (the plan's top tier reads it), or refused with `outside_intake.py refuse`; an `owed=answer` line is queued to the dispatch seat, which runs `outside_intake.py answer`; an `owed=reply` line is read and answered; `OUTSIDE plan-page UNAVAILABLE` is the public plan page not answering (the `plan-beat` row's Pages dispatch, `tools/audit/seat/plan_public.py`).

(6) Verdicts and CI. Read any moved `review/*` or `probe/*` refs and the cloud runs; confirm each verdict at its exact head with `tools/audit/seat/bus.sh confirm` (`dev/governance/roles/nudge.md` step 1). A red required check at an open head goes back to its fixer with the line `tools/audit/seat/failure_logs.sh` prints (`dev/governance/roles/nudge.md` steps 4 and 15).

(7) Proposals. A process, tooling or instrument proposal this sweep met (a seat's result, a verdict's optimisation note, your own) is sent to triage on `dev/governance/roles/proposal-triage.md`, never implemented or routed before its ruling; an ACCEPT reaches the roster through the roster seat, citing its ruling.

(8) Disk. The beat's `disk` row runs `tools/audit/worktree_gc.sh {{repo}}` whenever `/` has under {{disk_floor_gib}} GiB free; a `disk:` line in {{digest}}/digest.txt is a floor still not met after it: remove finished seat worktrees under {{seat_root}} by hand.

Keep the turn short; update {{seat_ledger}}.
<!-- sweep:end -->
