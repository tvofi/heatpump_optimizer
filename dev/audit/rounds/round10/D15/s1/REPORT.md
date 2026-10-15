# D15-s1 — intake, privacy gate, ingest, store replay (D15.M1-M4)

Baseline fe01b938f71b. Bundle: the live "Download diagnostics" file named in the task (read in
place). No export.py document was named and the bundle's `replay` half is null, so M5 cannot run.
Harness: `dev/audit/rounds/round10/D15/s1/intake.py` (one command, `--perturb` arms in its header).
Only counts are written here; no bundle value is reproduced (the M2 gate does not pass on the bundle).

## Method
Null control first: `tools/replay/dbg_bundle_gen.py --days 1` synthetic bundle through the same harness
(store_off_domain=0, bias_delta_tail=0.0 with 1 distinct sample in a 47-row tail, ingest fails 0).
Then the real bundle; every finding below is evaluated with baseline code.

## M1 intake and version seam
`data.debug` unwrapped; manifest version 7.0.0. One restart gap (>1 h) in 554 rows: 552 rows ran
v6.7.17 (tagged before the first row), 2 rows after the gap ran v7.0.0. All findings below are
properties of baseline code, not of an older release.

## Findings
- **D15-s1-01 (M3, medium, bug)** `tools/replay/debug_ingest.py:ingest` stage 4 re-derives the
  store-window bias from the *last N cycle rows*, but each row carries the latest accuracy sample, so
  192 tail rows hold 78 distinct samples: delta 0.115 °C, check fails (gate < 0.05). Matched by sample
  `t` the delta is 0.000. `--perturb dedupe` -> ingest fails 1 -> 0.
- **D15-s1-02 (M3, low, bug)** `debug_ingest.ingest` gates `replay-clean` on `bundle["replay"] or {}`:
  with the replay half null it passes on an empty dict (vacuous). `--perturb nonempty` -> 1 -> 0.
- **D15-s1-03 (M3, low, bug)** `debug_ingest.main --bundle` on the download as handed: 6 of 12 stages
  fail because the `hpo-debug/1` bundle sits under `data.debug`. `--perturb unwrap` -> 6 -> 1.
- **D15-s1-04 (M2, low, bug)** `tools/replay/export.py:_walk` credential-named-key rule flags a boolean
  (`diagnostics.tibber_reauth_started`, False): 1 violation on the real and on the synthetic bundle.
  `--perturb boolkey` -> 1 -> 0.
- **D15-s1-05 (M4, medium, bug)** `custom_components/heatpump_optimizer/store.py:DOMAINS` omits fields
  the writers persist: `pump_duty` `written/silent/*` (pump_arbiter `_SLOTS` has "silent") and
  `snapshots/#/learners/peak_tracker` (+ subfields): 25 undeclared leaves in the real stores,
  0 on synthetic. `--perturb declare` -> 25 -> 0.

## Non-findings
- M2 LEAK_PROBES controls 42/42 green; planted-credential arm adds 2 violations (caught).
- M2 export.violations over the whole debug bundle: 209, of which 208 are the text allowlist refusing
  benign prose/month strings; 0 match SECRET_TEXT, HOST_PATH or HEX12. Per the brief the gate fails,
  so no bundle value is written; this is an allowlist/brief mismatch (lead), not a leak.
- M4: 14 store documents, `_sanitize` idempotent on all (0 dirty), 0 refused versions;
  `--corrupt accuracy` refused by `AccuracyTracker.from_dict` (192 -> 0 samples).

## Unfinished
M5-M8 are other seats'. Within mine: M2 strictly stops the run (gate fails on benign text); M3/M4
were measured in memory with counts only.

## Exposure
None (no docs/ or GitHub read).
