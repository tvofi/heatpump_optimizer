Fix review: merge 653996c3fb8d85826c70efee82b2719ae6a91b1a
bus-nonce: 703d75291d647a4b860487b1d883cfbe

Delta review of #3731 against the previously reviewed head 04117e2e7d285855bd7864a29dce431072017720.
The delta is one merge commit, parents 04117e2e7d (branch) and 8ab5dc566f (main, #3726).

Checks run:
- git show --remerge-diff 653996c3fb (ev/remerge-diff.txt). The only hand-resolved hunk is the import
  block in custom_components/heatpump_optimizer/config_flow.py. tests/structure_budgets.json was
  resolved by the ledger merge driver and shows no hand edits. No other file differs from the
  automatic merge.
- Resolution: it keeps the branch thermal_model import (ThermalParameters, dhw_enabled_from_config,
  partload_derate_limit, two_zone_from_config) and the main-side "from .currency import
  figure_currency, money_scale" plus "from .price_model import price_feed". It drops the branch
  resolve_currency import. That is correct: all three resolve_currency call sites auto-merged to
  figure_currency(..., price_feed(...)), so resolve_currency has 0 uses at the head, and the
  main-side private _dhw_enabled_from_config is not referenced anywhere in custom_components.
- Every name in the block is used at the head. The two unused names left in config_flow.py
  (CONF_AWAY_RETURN_ENTITY, PRICE_SOURCE_TIBBER) are already in both parents, so the merge did not add
  them. The module compiles, and importing heatpump_optimizer.config_flow resolves all seven names.
- tests/config_flow_steps.py fails locally with the same FakeConfigEntries.async_get_known_entry
  AttributeError at the head and at main 8ab5dc566f (null control, ev/*.log). The cause is the local HA
  version, not this delta. CI is the authority there.
- Live checks could not be re-read at verdict time because the GitHub API was rate-limited. The packet
  digest was pending, and the train classify step reads CI before merging.

No findings.
