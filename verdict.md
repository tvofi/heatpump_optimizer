Design review: approve df30edfb8b25171dcb746acfad79e0fc9a0c035e

Reviewed design/R11-SEAM-money at df30edfb8b25171dcb746acfad79e0fc9a0c035e (round 1) from a detached worktree. Code read at the note's base origin/main bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f. Plan read at plan/r11 819aa2e354b4e5baaf824b8568fd72bea8168a75 (PLAN.md, ADR-001, ADR-002, ADR-006). Roster row read on handoff/audit-r10-roster (size L, no after edge).

Checked with no point raised:
- Seam: one owner per concern holds at the base. ledger.py owns month_hours, coverage_factor and pro_rata_factor (ledger.py:132-163), and its one caller is savings_months (ledger.py:513). price_model.py reads the source test (price_model.py:853). The coordinator copies it twice: _entity_price_source (coordinator.py:3397) and the 6969 read. figure_currency in currency.py stays duck-typed, and price_feed sits in price_model, so no upward edge is added (alternative 3 is correct).
- Shape against findings: every changed behaviour is named by D8-s1-02, D2-s3-07 (open-month floor, real DST hours), D14-s1-03 (feed-first currency in config_flow._money:619, _fee_placeholders:2106 and _grid_fee_errors:3973), or the ADR-001 arms day and entry. The new waiting_for code follows from the floor. savings_months is called with dt_util.now() (coordinator.py:8104), which is local, so tz-aware month_hours moves the March case.
- Sibling sites: resolve_currency has six calls, and the note accounts for all six (the coordinator notice's two reads at 2885/2898 are kept on purpose). The card's currency() (heatpump-optimizer-card.js:6916) is already feed-first. sweep-N-partial-window-extrapolation's beyond-finding site, ledger.pro_rata_factor, is covered by the floor on the fallback. power_guard.project_window_mean at the base is the mean-so-far plus current remainder, not an extrapolation.
- Evidence plan: the three failing tests fail on today's code (2688 row, 1.001346, SEK labels). The harnesses are the finders'. The goldens claim nothing, which is right: there is no tariff, solver or currency change on golden paths.
- Sibling designs: no open design/* note names the currency, price-feed or projection functions. design/R11-VALVE-REFERENCE edits ledger.REFERENCE_BASIS only, which is a different concern and a rebase at most.
- Cost: about six production files plus tests/features.py, which fits size L.

Rulings on the designer's three questions (relayed by the orchestrator as the owner's rulings of 2026-11-18; they agree with this review's own reading):
1. D2-s3-03, -04, -05, -06 and D17-s1-05: these are not reproduced at main, and they are not sent back to the judge. JUDGE.md marks each as "planted copy". The class sweeps confirm the base already reads both Tibber periods (price_model.py:720), weekday() (grid_fee.py:162), kw > best, and sort[-k:] (tariff.py:918). Each gets a regression test in tests/features.py that fails on the harness's --perturb inverse. The PR records each as "not reproduced at main, pinned". There is no production edit.
2. D5-s3-01 moves out of this group into R11-SEAM-kernel-layering, whose ADR-002 part 1 edit to currency.py is the change that makes grid_fee's docstring true. No edge is added. decision: orchestrator (roster edit).
3. ADR-006 part 2 is approved as the ADR states it: conditional. Part 1 already holds at the base (tariff.py:918), so D2-s3-06 is a pin only. The fixer tries part 2 under the ADR's own condition (tests/stress.py solve time, goldens byte-identical, prototypes.py --only topk). If it fails, the fixer drops and records it, citing tariff.py:951-953's one-row overhead. If part 2 drops, the PLAN's dS row for money reads 14 to 12, not 14 to 11, and the orchestrator records that. The owner still holds part 2 open, and nothing here withdraws it in advance.

Notes for the fixer:
- Drop D5-s3-01 from section 1's table, section 6's ha_free.py harness line and section 7's closure sentence once the roster moves it. Carry: R11-SEAM-money (item d5-move)
- The five pins: name in each test the --perturb that re-plants the inverse, and run the finder's harness at both ends (0 to 0) as the record. Carry: R11-SEAM-money (item pin-not-reproduced)
- Re-anchor or re-record the tests/mutation_ledger/killed_by/ledger.py rows for coverage_factor, month_hours and pro_rata_factor when their bodies move. Carry: R11-SEAM-money (item mutation-anchors)
- Test month_hours on a tz with DST (Europe/Stockholm, March 743 and October 745), and on a UTC-aware now (744). Carry: R11-SEAM-money (item dst-both-ways)

Seat token count: not reported by this harness.
