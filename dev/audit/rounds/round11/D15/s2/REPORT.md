# D15-s2 — round 11, D15.M5 (timeline replay) and D15.M6 (monitor re-run)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B8 (shared: load1 12–290). Interpreter: venv-ci python3, `PYTHONPATH=tests/hastub:tests:custom_components`.

**Input.** The owner's 2026-11-16 Download diagnostics file, read in place:
- `hpo-debug/1`, final, 662 cycle rows covering 2026-11-08..15, written by releases 7.1.8 to 10.0.0.
- Replay half filled: `hpo-replay/1`, 2026-11-14T21:07Z..2026-11-15T21:07Z, time_zone Europe/Stockholm, 16 stores.

**Null control.** `dbg_bundle_gen.py --days 1/7` in a private temp directory.

**Method.**
- **M5 universe:** `m5_enumerate.py` lists 96 replay cycles and 16 seeded stores.
- **M5 seeding:** the 16 stores were checked with `m5_seed_ids.py` (finding 01) and `m5_seed_age.py` (finding 02).
- **M5 judges:** cycles ran through all 8 lane judges with `m5_judges.py`, in 2-hour re-seeded chunks over hours 1–19. Hour 0 ran inside both `m5_zone.py` arms.
- **M5 clock zone:** the zone question was measured with `m5_zone.py` (finding 04).
- **M6 universe:** `m6_monitor.py --enumerate` lists 9 local-day windows, 2 anchors and the stored latch.
- **M6 rebuild:** the live accuracy deque is rebuilt in time order from row and store samples. A restart (a version change, or a gap of at least 3 intervals) reloads the 192-sample slice that `as_dict` persists.
- **M6 checks:** the rebuild is anchored on the self-test and the 11-11 snapshot. `observe_bias` is then folded over the fully known counting days. Controls: `no-restart`, `band=0.1`, and `--fresh` on the synthetic bundle (finding 03, `m6_null_ring.py`).

**Findings:** D15-s2-01 to -07, as in the table above; the JSON is in `findings/`.

**Checks that held:**
- Self-test anchor: count 0, bias 0.0 and MAE 0.0 off; the no-restart control moves these to 318 and 0.103.
- latch_match=1 over 5 days; the issue agrees with the latch; band=0.1 control gives latch_match=0.
- restart_flip_days=0.
- Cycle, finite, unit, agreement, away and cycle_cost judges were 0 in the 76 examined cycles.
- The replay is deterministic once `_ms` attributes are dropped (`--null`: 0 of 8).

**Window statistics (M6, stated per local day):**

| day | samples | bias °C | MAE °C | live bias at counting tick °C |
|---|---|---|---|---|
| 11-08 | 9 | 0.551 | 0.551 | 0.632 (partial) |
| 11-09 | 80 | 0.511 | 0.511 | 0.551 (partial) |
| 11-10 | 68 | −0.012 | 0.303 | 0.515 (partial) |
| 11-11 | 82 | 0.429 | 0.434 | 0.279 (partial) |
| 11-12 | 51 | 0.541 | 0.541 | 0.32 |
| 11-13 | 88 | 0.477 | 0.487 | 0.321 |
| 11-14 | 92 | 0.353 | 0.529 | 0.475 |
| 11-15 | 76 | −0.103 | 0.342 | 0.447 |
| 11-16 | 59 | 0.2 | 0.206 | 0.228 |

"Partial" means the live deque still held samples from before the collection, whose values are unknown.

**Not finished:** M5's last 20 cycles; the zone comparison on the real bundle covers 1 hour only.

**Leads:** as listed above.

**Exposure:** none.
