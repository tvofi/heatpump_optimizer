# `flow_metrics.py`

- `flow_metrics.py` — a round's flow over one window, from git alone:
  roster groups added and closed per hour (`--roster REF:PATH`, `--prefix`),
  records' share of main's PR merges (`--record-prefix`), first-pass yield of
  the merged fix PRs on the bus, main absorbs per fix branch, merge-to-merge
  re-reviews of an unchanged PR diff (patch-id), and the share of hours with
  a merge. When: a flow guardrail or a round's close reads throughput.
  Refusal: a re-review whose heads git does not hold prints `unresolved`,
  never counted; no round constant in code.
