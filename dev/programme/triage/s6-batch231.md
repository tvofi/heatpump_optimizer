# Proposal triage, session s14, batch 231

Source: the orchestrator's brief to triage seat s14-40 (2026-11-12), jobs 1-3, ruled as P700-P702.
Line numbers are at origin/main 2ced371c1a. Roster read at handoff/audit-r10-roster 85bfbf3557.
Rulings are the orchestrator's under mandate 6715477401 (scope all), made by triage s14-40.

## P700: R10-FIXER-MD-SPELLING-CORPUS has no pending carry; set it done

Verdict: NO-OP
Evidence: all seven carries end in a mark roster_lib's `_CARRY_MARK` reads (0, 1, 3, 4, 5 dismissed;
2 and 6 `[moved: R10-ROUND-PLAYBOOK-FINAL]`), and `pending_carries` counts a moved carry as
discharged. Both moved carries exist at the destination: R10-ROUND-PLAYBOOK-FINAL carry 28 cites
body items 1d630dea and a629d56d, the items of carries 2 and 6. The earlier `set-stage ... done`
(s14-38, batch 229) landed the group at carries-open because it ran before those marks.
Ops: set-stage R10-FIXER-MD-SPELLING-CORPUS done --at-sha 046736a49f (the merge it already cites).

## P701: R10-COMBI-TANK-PR-B carries 0-3, 6, 7 after PR B merged (cbd23f1c)

Verdict: MIXED (dismiss 0-3, move 6, implemented 7)
Evidence and ruling per carry:
- 0 (owner ruling 11-06 ~22:02Z, physically sound and general design): it bound the design note,
  its review and PR B's build. The design was approved and PR B merged; nothing further is built
  under it. Dismissed: spent at the merge.
- 1 (owner ruling 11-06 ~22:12Z, a 10-round design waiver): a waiver on design-revision rounds;
  the design is approved and built. Dismissed: spent at the merge.
- 2 (owner request 11-06 ~22:55Z, web verification before PR B): a precondition on PR B starting;
  the verification report is carry 3 and PR B has merged. Dismissed: spent at the merge.
- 3 (web verification figures): items 2-6 are on main from PR B. const.py:994 internal_coil eps
  0.89 note, :997 IEA SHC Task 26 store C 228 l and the 0.88 / 0.58 station range;
  translations/en.json:834 "S / 45 K (a 20 °C room assumed)"; DVGW W 551 named in const.py.
  Item 1 corrects an MFS 600 S preset and a "39 l" help example: no MFS preset or that example
  exists on main (grep MFS, 572, 2.87, 39 l over custom_components: none), so item 1 has no site.
  Dismissed with that reason.
- 6 (item exchange-accounting, cc665630): PR B's card and payload diff touches only the setup
  diagram (combi caption, buffer-to-DHW pipe) and one payload flag; the DHW kWh tile and savings
  attribution were not changed. Destination: R10-SAV-VALUATION-RESIDUE (in-progress, owns
  ledger.py and the savings residual attribution, the seam this carry names). Severity: an
  accounting double-count risk, not measured here; the harness figure it cites (22.135 vs 5.327
  kWh) is the carry's own. Basis: carry_receivable is true for the destination.
- 7 (item exo-seed-census-only, c45c9022): PR B keeps the `combi_flux_live` census
  (tests/features.py at cbd23f1c; at main :11876). The clause on later planner stages is held by
  that census test itself. Implemented at cbd23f1c.
Ops: mark-carry dismissed on 0-3, append-carry R10-SAV-VALUATION-RESIDUE (carries/b231-P701.txt)
then mark-carry moved on 6, mark-carry implemented cbd23f1c on 7, then set-stage
R10-COMBI-TANK-PR-B done --at-sha cbd23f1c.

## P702: no-op record for queue lines 4679-4690

Verdict: NO-OP
Evidence: none of 4679-4690 had drained at roster tip 85bfbf3557 (its last drain result is line
4678); they are pending, not refused. Nothing re-queued.
