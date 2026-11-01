# `cancel_superseded.py sweep`

- `cancel_superseded.py sweep` (`python3 -I tools/pr/cancel_superseded.py sweep --repo OWNER/REPO [--dry-run]`) --
  cancels, per open same-repo pull request branch, the active (queued, in progress,
  waiting, pending, requested) `pull_request` / `workflow_dispatch` runs at a head other than the live
  one, using `candidates()`. Never a live-head run, a run on main, any other event,
  or a branch whose live head `github-actions[bot]` authored; a run on a branch with
  no open PR is a ghost, reported. Ends with one `CANCEL-SWEEP:` line.
  When: each orchestrator sweep pass (step 4e), because the in-run cancel cannot
  fire while the newer run is still queued for a runner (P266).
  API cost per sweep: 1 PR listing + 5 run listings (one per ACTIVE status; one page
  each below 100 items, at most 10 pages per listing, a still-full last page prints
  `CANCEL-SWEEP: truncated`) + one commit read per open PR with something to cancel
  + one POST per cancel.
  Refusal: none; an unreadable answer cancels nothing and exits 0.
