# `machinery_ratchet.py`

- `machinery_ratchet.py` — grades the newest `window_merges` first-parent
  merges of main against the caps in
  `dev/governance/config/machinery_budgets.json`: how many are not production
  merges, and how many nonproduct lines they changed per 1000 product lines.
  `--check --head <sha>` grades the window ending there; `--check --base <sha>
  --head <sha> --pr <N>` grades a pull request as the newest merge of its
  base's window; `--check-event` reads those three from `MACHINERY_BASE`,
  `MACHINERY_HEAD` and `MACHINERY_PR`, as `policy-docs` sets them. `--measure --window 580 --bands 150` prints both metrics and
  each band, which is how the budgets file is re-recorded. Refusal: exit 1
  names each metric past its cap plus its band; an exemption counts only when
  the merge it exempts added it (`ratchet-budgets.md`). `--self-test` —
  `governance.yml` greps its `checks, 0 failed` line.
