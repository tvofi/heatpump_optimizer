# `approve_held_runs.sh`

- `approve_held_runs.sh` — approves the workflow runs GitHub holds
  `action_required` on a branch. When: after the App pushes, the `pull_request`
  workflows it created are held because the pusher is an App; a green gate
  never starts until these are approved. Refusal: `--dry-run` lists what would
  be approved; a branch with no held runs is a no-op, not an error to retry.
