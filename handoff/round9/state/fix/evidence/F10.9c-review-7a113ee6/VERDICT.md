Fix review: merge 7a113ee6f5cde689dd8ae919747022366c674d3c

Round 1, PR #1824 (stage 3), code head 7a113ee6. Live head 3e74c871 = c1ee65df (main 411368b6 merged in;
its tree equals git merge-tree 411368b6 7a113ee6 exactly) + docs/delivery/1824.md. That is a clean carry.

CHECKED
- The covkey BASE on push is git rev-parse HEAD, and the staging marker writes the same SHA, so the push
  run's entry is trusted. A PR save, a missing marker, or main's marker at another commit is discarded and
  every script is measured (the entities check runs both steps' own run: scripts).
- A trust check that is skipped or distrusts leaves trusted empty, so the run measures everything (fails
  closed). runner.os is in the key.
- Cache poisoning: a PR head that edits tests.yml can forge the marker, as the step's comment says. This is
  acceptable because coverage and coverage-ratchet are not in the 17 required contexts, and main's push runs
  them unscoped. No required barrier is lost.
- codeowners_gap --check: uncovered_files=0.
UNRUN: CI on the head (no check runs reported yet; merge only on green), typing, real-HA.
