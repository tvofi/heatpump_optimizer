Question: derive_closures --single tests/entities.py refuses; the repair needs tests/closure.py (INERT / INERT_EXCEPT) edited, which the brief forbids. May the seat edit tests/closure.py?

Merge of origin/main f38ac9a7c0 into 02df7d11 was clean (a8b07f2332). Verbatim derive output:
```
  heavy slot: taken slot=0 label=derive-8149 expires_at=2026-11-12T08:55:05.151181+00:00
  [08:25:05] record tests/entities.py
  [08:44:07] done   tests/entities.py (exit 0)

closure: tests/entities.py would drop 2 file(s) the committed closure listed; keeping them.
    tests/golden/card_claimed_drift.txt
    tools/pr/figure_registry.json
closure: files on the INERT list are actually read by tests:
  tools/audit/seat/seat_gen.py
  tools/audit/seat/seat_gen_selftest.py
  remove them from INERT in tests/closure.py, or except them,
  then re-run this merge -- check refuses this pair on CI.
```
