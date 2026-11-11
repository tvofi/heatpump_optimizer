# Round 10 D3 quiet window

Instrument: `dev/audit/rounds/round10/intake/quiet.sh` (header carries the command). Baseline `17f1c55fad1b`; each arm is a worktree at the baseline with its one-line mutant committed (NULL: an empty marker commit), then `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh` under gate lease `quiet-r10`, BLAS threads at 1, Darwin arm64 8-core, python 3.14 seat venv. Every arm ran 54 sections (the full suite, `env_drift --all` and `stress.py` included) and printed `ALL TEST SCRIPTS PASSED`; no log carries a SIGTERM/143 (the 03:10Z machine-wide pkill fell inside M01, which passed). A mutant is killed only by a script red on its arm and green on NULL; NULL had none red.

| mutant | site | finding id | survived | killed_by | rc | load1 (start/end) | gate seconds |
|---|---|---|---|---|---|---|---|
| NULL | `-` | (null arm) | n/a | — | 0 | 2.96/4.08 | 1520 |
| M08 | `custom_components/heatpump_optimizer/coordinator.py:6522` | D3-s1-01 | yes | — | 0 | 3.99/3.86 | 1442 |
| M01 | `custom_components/heatpump_optimizer/optimizer.py:5541` | D3-s1-02 | yes | — | 0 | 3.79/6.10 | 1613 |
| M03 | `custom_components/heatpump_optimizer/optimizer.py:5557` | D3-s1-02 | yes | — | 0 | 6.10/3.79 | 1654 |
| M35 | `custom_components/heatpump_optimizer/ledger.py:306` | D3-s2-01 | yes | — | 0 | 3.79/3.05 | 1438 |
| M26 | `custom_components/heatpump_optimizer/snapshots.py:239` | D3-s2-01 | yes | — | 0 | 3.29/5.09 | 1462 |

Logs (about 0.9 MB each) are not committed; they were under the intake seat's scratch `quiet/` directory.
