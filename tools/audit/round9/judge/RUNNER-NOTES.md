# Round 9 judge batch: notes for runners R1 and R2

JUDGE-INPUT.json holds the 148 canonical findings (dedup in DEDUP.md), each carrying a
`judge_batch` override (run, perturb, null, metric, tolerance) written by the judge, because no
round-9 harness has JUDGE-* header lines. `judge_expected` and `judge_notes` beside each finding are
for the judge, not for judge_batch.py. Run exactly the command in R1.md / R2.md.

**Write nothing into the clone while the batch runs.** judge_batch.py restores the tree after every
command and deletes any untracked file that appeared meanwhile (that includes your own notes). Write
`--out-json`/`--out-md` targets and runner-N.md only as the batch's own outputs or after it exits.

Setup (once, before the batch; record it in runner-N.md):
- venv /home/claude/venv314: CPython 3.14, numpy 2.4.6, scipy 1.17.1, aiohttp 3.14.3,
  voluptuous 0.16.0, pyyaml, threadpoolctl 3.6.0, **orjson** (D1-s1-51 imports it).
  Symlink /home/claude/venv and /home/claude/venv-r9 to it; several commands name those paths.
- node 22 (D4-s1, D5-s1-04, D5-s2-01, D11-s1-71, D13): D5-s2-01 names /opt/node22/bin/node;
  if absent, symlink your node there. D4-s1-* need Playwright + Chromium under
  NODE_PATH=/home/claude/pwlane/node_modules with PLAYWRIGHT_BROWSERS_PATH=/root/.cache/pw-browsers.
  If you cannot provide them, those rows fail and the judge takes them by hand. Do not improvise.
- network: D5-s1-04 runs `npm install markdown-it@14.1.0`; D6-s1-81 downloads two Home Assistant
  core wheels with pip. If the network refuses, the row fails; leave it.
- strace on PATH (D14-s5-01).
- D13-s1-01 runs `git update-ref refs/remotes/origin/main 1936d5ca...` in YOUR clone. That is
  intended (its harness reads origin/main). Push nothing but your rows branch.

By-hand rows (the run is an `echo 'by-hand: ...'`): the 8 D3 mutation findings (quiet window not run,
tvofi rule), D7-s1-02 (mutation pool), D11-s1-01 and D11-s1-04 (live GitHub API). They cost nothing.

Many rows print the perturbed or null arm in the SAME run under another RESULT name; the row's
`other` dict carries it and `perturbation` reads by-hand. That is expected, not a failure.
Long rows: D14-s3-02 (~10 min), D9-s2-03 (stress sweep arms, 10-20 min), D0-s2-01 and D0-s2-02
(multi-minute). Keep the box quiet.

Judge smoke test before push (this box, load1 ~1): D2-s2-03 end_mismatch 6 -> 0 moved;
D6-s2-05 simulate_plan_schema_only 5 -> 0 moved; D1-s1-51 divergent=6 once orjson is installed.

## Scope change (tvofi, 2026-09-26T13:39Z: "Contested only")
JUDGE-INPUT.json is now **batch A only: 46 findings** (the 3 disputed and 40 split findings less
D3-s2-01, plus D6-s2-05 and D9-s2-02 whose verifiers flagged the metric or perturbation, plus the
provisional CPU/timing findings D1-s2-05, D9-s1-01..04). Run it whole, sharded 1/2 and 2/2 as before.
JUDGE-INPUT-B.json (102 unanimous findings, plus the 8 D3 mutation findings the judge sanity-checks
by hand under tvofi's 13:41Z rule) is a record only: runners do not run it.
