# Box D3-g13 working notes (pre-gate step-4 analysis)
- keyinfo.json holds, per key, the class the key takes if its gate does not kill it, the inputs tried, the check that
  should have failed, and the candidate finding text; probes/probe_<key>.py (and probes/<key>/) are the harnesses,
  all executed at the baseline from a clean worktree before the gates (22:00Z 2026-11-22).
- Pre-gate probe classes: candidate = 24d9995ccee4252e, 8297234e122897ff, 681130c48add1573, c61a89f42607c92b,
  df4de55e12588fdf; equivalent-candidate = the other 11.
- build_records.py writes results/<key>.json after each gate (re-runs the probe); build_report.py writes REPORT.{json,md}.
- Inbox NOTE 1 and 2 (owner rulings: continuous checkpoints; probes saved under probes/<key>/ with INDEX.md) obeyed:
  ckptloop.sh checkpoints every 10 min (probes/_scratch/ckptloop.sh).
