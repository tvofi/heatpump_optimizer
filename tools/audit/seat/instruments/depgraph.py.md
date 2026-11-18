# `depgraph.py`

- `depgraph.py` (tools/pr/) — compares GitHub's dependency graph with the
  tree's pins: one SBOM read and one open-alerts read (`check --repo
  OWNER/NAME`), every pip, npm and actions pin against the SBOM, and every
  open alert the tree already pins past. When: Dependabot alerts that main's
  locks should have closed, or `dependency-graph.yml`'s daily `check` is red.
  Refusal: an SBOM ecosystem it does not enumerate, or an alert whose
  versions it cannot order, exits 2 rather than reading clean; an alerts read
  that fails prints `alerts: unread`, never OK.
