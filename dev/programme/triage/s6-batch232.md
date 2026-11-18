# Proposal triage, session s14, batch 232

Source: batch 231's P701 move of R10-COMBI-TANK-PR-B carry 6, stated as its own ACCEPT so the
append-carry's citation reads as one (a MIXED entry does not). Line numbers are at origin/main
2ced371c1a. Rulings are the orchestrator's under mandate 6715477401 (scope all), made by triage s14-40.

## P703: combi store charge read as one channel in the DHW tile and savings attribution

Verdict: ACCEPT
Scope: custom_components/heatpump_optimizer/ledger.py (savings attribution) and the card's DHW kWh
tile, for a combi store (dhw_source "combi").
Evidence: R10-COMBI-TANK-PR-B carry 6 (body item cc665630 of the PR A record): in combi the hot-water
channel buys the heat the space side draws from the store (harness exchange_dhw_kwh=22.135 against
null_dhw_kwh=5.327 on the same day). PR B (cbd23f1c) changed only the setup diagram and one payload
flag on the card side; neither the DHW kWh tile nor the attribution reads the store as one channel.
Destination and severity: carry on R10-SAV-VALUATION-RESIDUE (in-progress, owns ledger.py and the
savings residual attribution), normal. Figure against 20%: the carry's own day shows the DHW channel
at about 4x its null figure (22.135 vs 5.327 kWh) on a combi store, far past 20% for that tile; the
share of the savings residual it explains is unmeasured, which is the destination's measure-first.
Fix shape: read the store's charge as one channel, or label which split the tile shows; re-measure
with the harness's exchange arm at PR B's merge base. Control: the null arm on the same day.
