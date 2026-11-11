# D9-s2 report (round 10, baseline 17f1c55fad1b)

Cells: D9.M1, axes retained_bytes and payload_bytes, all files. Exposure: none (no docs/, no GitHub).

## Method
- `payload.py`: one solved cycle of `coord_all_features` (FakeHass, frozen clock),
  every enabled-by-default entity through the real `async_setup_entry`, JSON bytes of
  `_build_data_dict` and of each `extra_state_attributes` key split by `_unrecorded_attributes`.
- `retained.py`: closed-loop cycles with the clock advancing 30 min/cycle, deep size of every
  coordinator `__dict__` attribute at N/2 and N, plus tracemalloc slope.

## Findings
None. No mechanism in these cells survived to a falsifiable defect.

## Non-findings
- Payload: data dict 81,227 B / 169 keys; 61 enabled-by-default entities; recorded
  attributes 3,476 B/cycle vs 84,458 B unrecorded (recorded share 3.95 %); upper bound
  166,848 B/day recorded at 48 cycles/day. Perturbation `--drop-unrecorded-guard` moves
  recorded to 87,934 B/cycle, so the exclusion set does the work it claims. Largest recorded
  attribute: `PlanNarrativeSensor.items` 538 B; `TotalCostSensor.period/split_method` are
  recorded on purpose (class comment, sensor.py TotalCostSensor).
- Retained: 96 cycles (2 days) -> coordinator deep size 622,885 B, slope 748 B/cycle, of
  which `_accuracy` 762 B/cycle. Bounded in code: `accuracy.py` samples deque(maxlen=672),
  `lead_pending` capped at 512, promises at 2 days. Extrapolated plateau ~0.5 MB at 14 days
  (672 x ~760 B, an assumption from the measured slope) — bounded, not a leak. tracemalloc
  slope 981 B/cycle. 16-cycle run: 1,040 B/cycle, same top attribute.

## Unfinished
- ru_maxrss in a subprocess not taken; a >672-cycle run to observe the `_accuracy` plateau
  directly was not run (about 3 h at the box's load1 of 40-80).

## Harnesses
- dev/audit/rounds/round10/D9/s2/payload.py
- dev/audit/rounds/round10/D9/s2/retained.py (output: retained_96.out)
