open_pr.sh creates the pull request before every later step has passed, so a failure in the second push of the delivery row leaves a PR the tick sees with no row. Create the PR only after the body contract passes, and close the draft with a comment saying why when a later step still fails.

Roster group: `R10-FLY-OPENPR-ATOMIC`. Part of #201.
