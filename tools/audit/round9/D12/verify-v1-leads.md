# D12 verify-v1, leads unit (round 9, lens V1 reproduce), box G2-V1

Tree: /home/claude/wt/leads at evidence 96b89163. Finder's harness re-run unmodified with PYTHONPATH=tests/hastub; perturbations in memory; no harness written.

## D12-s3-81 -- Grid-fee bounds are SEK numbers, unenterable for a 0.05 EUR/kWh fee in HUF/ISK/JPY/KRW (vote: verify, medium)
- Re-run: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/leads/l4_fee_bound.py` -> blocked_verdicts=8, blocked_currencies=4 of 12 (HUF, ISK, JPY, KRW), null_blocked=0 of 4. The finder's value is 8, so exact. load1=1.68, thread_factor=1.000.
- Perturbation `--perturb` (IMPLAUSIBLE_FEE_SEK_PER_KWH 10 -> 1e6 in memory, grid_fee's and the coordinator's imported copy): blocked_verdicts 8 -> 4. Seams a (rules refusal) and c (repair raised) drop to 0; seam b (the fixed selector max `_number(0, 5, ...)`, independent of the constant) stays 4. Finder's observed 4, direction down.
- Null control: SEK/EUR/NOK/DKK -> 0 of 4 blocked, matching the finder.
- Leave-one-out: dropping HUF or KRW (3 of 8 verdicts each) leaves blocked_verdicts=5, blocked_currencies=3.
- Fee sensitivity: `--fee 0.03` gives blocked_verdicts=6, blocked_currencies=2 (HUF, KRW); not an artefact of the 0.05 EUR choice.
- Method attacks: exact count, contention-immune (load1 1.68-1.70); reach checked in source: `grid_fee.py:70` IMPLAUSIBLE_FEE_SEK_PER_KWH = 10.0 and `config_flow.py:1720` `_number(0, 5, 0.01, ...)` for grid_fee_fixed are production constants.
- Metric (finder's): seam verdicts refusing or capping a 0.05 EUR/kWh fee expressed in each of 12 currencies at the stated exchange-rate table.
- Severity medium: blocks entering an ordinary fee in 4 currencies; no data loss.
