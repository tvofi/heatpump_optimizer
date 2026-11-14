# R11-PRE-PARALLEL-PIPELINE: appendix to the design note

The note is `design.md` on `design/R11-PRE-PARALLEL-PIPELINE`. This directory
is its evidence and never merges (`designer.md` step 8).

| file | carries |
|---|---|
| `STUDY.md` | appendix A: public designs and standards, GitHub behaviour verified and not, sources |
| `BASELINE.md` | appendix B: round 10's measured baseline, figures B1 to B24 with enumerators |
| `COST.md` | appendix C: candidates, both replays, the cost test against the bar |
| `carries/` | one carry text per destination roster group |
| `harness/` | the enumerators and the two replays; `PD_REPO`, `PD_DATA`, `PD_STATE` and `HPO_STATE_DIR` name their inputs |
| `data/` | the inputs taken from git and from GitHub on 2026-11-14 |
| `out/` | each script's recorded output |

Re-run, from the repository root, with a checkout that holds the bus refs:

    PD_REPO=<checkout> python3 dev/audit/rounds/round10/pipeline-design/harness/segments.py
    PD_REPO=<checkout> python3 dev/audit/rounds/round10/pipeline-design/harness/replay_pipeline.py 45 60 105
    PD_REPO=<checkout> python3 dev/audit/rounds/round10/pipeline-design/harness/replay_programme.py

`fetch_runs.sh`, `fetch_prs.py` and `fetch_main_gate.py` are the only scripts
that read GitHub; the others read `data/` and git.
