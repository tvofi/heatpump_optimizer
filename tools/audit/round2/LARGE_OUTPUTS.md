# The large harness outputs are not committed

Five files under `round2/` are bulk harness output: together they are 250,000
lines and 4 MB, they are regenerated exactly by the command in their harness's
own header, and no finding rests on reading them by hand — every finding
quotes its decisive number in `report.json` and in its issue.

Committing them made the register's pull request 408,000 lines, which nobody
can review, and contradicted this register's own archive section, which had
already recorded two of them as deliberately excluded.

| Not committed | Regenerate with |
|---|---|
| `D4/results.json` (88,060 lines) | `node tools/audit/round2/D4/card_geometry.mjs` |
| `D4/shots/` (182 PNGs, 14 MB) | `node tools/audit/round2/D4/card_geometry.mjs --shots` |
| `D8/matrix_results.json` (77,268 lines) | `python3 tools/audit/round2/D8/matrix.py` |
| `D3/pool.json` (37,521 lines) | `python3 tools/audit/round2/D3/candidates.py` |
| `D0/out/*.json` (74,000 lines over 4 files) | `python3 tools/audit/round2/D0/race_grid.py` |
| `quiet/D0-race_grid_24h_baseline.quiet.json` | the same, in the quiet window |

Everything a reader needs is still here: every harness, every `REPORT.md`,
every `report.json`, every `verify-*.md`, every `panel.json`, the quiet-window
logs and `JUDGE.md`.
