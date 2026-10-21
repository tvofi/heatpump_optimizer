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
| `local_seat_cap` | the most local seats the session runs at once |
| `cloud_above_cap` | whether cloud seats count above that cap (`yes` or `no`) |
| `plan_generator` | the command that regenerates the plan artifact |
| `plan_artifact` | the plan artifact's path, republished at the same path |
| `state_mirror` | the directory `state_docs.py --mirror` writes |
| `tick_alive` | the tick seat's liveness file, touched every pass |
| `tick_log` | the tick seat's log |
| `tick_brief` | the tick seat's brief, the prompt a restarted tick seat receives |
| `tick_stale_min` | minutes after which a silent tick seat is dead |
| `transcript` | the session transcript `policy_reread_check.py` reads |
| `policy_stamp` | the policy re-read stamp `policy_reread_check.py` reads and writes |
| `disk_floor_gib` | free GiB on `/` below which finished worktrees are cleaned |

<!-- sweep:begin -->
ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} first. Run each instrument from its path in the tree, from {{orch_checkout}}, with `tools/audit/seat/shims` first on PATH. Then, briefly:

(0) Policy re-read. Run `python3 -I tools/audit/seat/policy_reread_check.py --transcript {{transcript}} --stamp {{policy_stamp}}`. On OWED: `git -C {{orch_checkout}} fetch origin`, then read `CLAUDE.md`, every policy file its index names, and `tools/audit/seat/INSTRUMENTS.md` with `git -C {{orch_checkout}} show origin/main:<path>`; act on any delta against current practice; then `python3 -I tools/audit/seat/policy_reread_check.py --stamp {{policy_stamp}} --write-stamp`, and log the re-read in {{seat_ledger}}.

(1) Seats. Run at most {{local_seat_cap}} local seats; cloud seats count above that cap: {{cloud_above_cap}}. Below the cap, resume the next queued seat from {{seat_ledger}}. Seat worktrees live under {{seat_root}}, each named absolute in its brief (`dev/governance/roles/orchestrator.md` section 5). A handed-off seat is not resumed and an unblocked roster group gets a fixer (`dev/governance/roles/nudge.md` steps 14 and 16).

(2) Handoffs. Compare `git ls-remote --heads origin 'handoff/r{{round}}-*'` with the open pull-request heads, and run `tools/audit/seat/bus.sh orphans`. A handoff with no pull request gets `tools/audit/seat/open_pr.sh`; one ahead of its pull request gets `tools/audit/seat/update_pr.sh`; each runs detached under `tools/audit/seat/daemonize.py`, then `tools/pr/approve_held_runs.sh` on that branch, then `tools/audit/seat/bus.sh dispatch` and a reviewer seat at the printed head (`dev/governance/roles/orchestrator.md` section 5b; `dev/governance/roles/nudge.md` steps 1, 2 and 8).

(3) Merges. Verdicted pull requests go to one batch through `tools/audit/seat/train.sh --repo {{repo}} --mandate {{mandate}} --overlap`, its queue and `--state-dir` under {{orch_scratch}}, detached under `tools/audit/seat/daemonize.py`, never a second live train (`dev/governance/roles/nudge.md` step 3; `dev/governance/roles/orchestrator.md` section 11). Budget-file and policy heads stay off the train and merge directly under mandate {{mandate}} (`dev/governance/roles/nudge.md` steps 5 and 7; `CLAUDE.md` rule 2). A record or autofix pull request merges behind `tools/audit/seat/record_row.py --automerge-check` (`dev/governance/roles/nudge.md` step 6).

(4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #201 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), the finished seat's worktrees under {{seat_root}} and its scratch removed, `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}}`, and the plan artifact regenerated with `{{plan_generator}}` and republished at {{plan_artifact}}.

(5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one in the background whose prompt is the contents of {{tick_brief}}; it runs `tools/audit/seat/orchestrator_tick.py`. Log the restart in {{seat_ledger}}. Act on the newest actionable lines of {{tick_log}}; the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`).

(6) Verdicts and CI. Read any moved `review/*` or `probe/*` refs and the cloud runs; confirm each verdict at its exact head with `tools/audit/seat/bus.sh confirm` (`dev/governance/roles/nudge.md` step 1). A red required check at an open head goes back to its fixer with the line `tools/audit/seat/failure_logs.sh` prints (`dev/governance/roles/nudge.md` steps 4 and 15).

(7) Disk. If `df -h /` shows under {{disk_floor_gib}} GiB free, collect finished worktrees with `tools/audit/worktree_gc.sh {{repo}}`.

Keep the turn short; update {{seat_ledger}}.
<!-- sweep:end -->
