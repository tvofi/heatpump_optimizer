# D15 verify — round 10 (one verifier, V1+V2+V3)

Worktree: detached at handoff/audit-r10-register 9355f107d. Bundle: newest live "Download diagnostics"
file (config_entry-...-4.json, 2026-10-14 20:12). Counts only; load1 28.96-30.78, thread_factor 1.000
(counts are contention-immune). Own harnesses: `D15/verify/mine.py` (all five), `D15/verify/cov.py` (01).
Command: `PYTHONPATH=tests/hastub <venv-ci python3> dev/audit/rounds/round10/D15/verify/mine.py <bundle>`.
Null control: `dbg_bundle_gen.py --days 1` bundle through the finder's harness: fails 0/0, replay present,
bias_delta_tail 0.0 (1 distinct sample in 47-row tail), off-domain 0, credential violation 1 (bool key also
present in synthetic). No seam_rule was supplied with any finding; seam enumeration below is mine.

| id | V1 (finder harness, perturbation) | V2 (own metric) | V3 | vote |
|---|---|---|---|---|
| s1-01 | delta_tail 0.115, by_t 0.000; dedupe: fails 1->0 | rows carry 97 distinct samples, store 192, intersect 97; dedupe-only (last N distinct rows vs full store) bias 0.112 vs 0.221: delta 0.109, still fails | real bundle, tools path; class I4 | weaken |
| s1-02 | replay_clean_passed_on_absent_replay 1; nonempty: 1->0 | debugger.py:494 always writes "replay": None; export.violations({})==[] | every real bundle; I4/N-silent-zero -> N-silent-zero | verify |
| s1-03 | wrapped 6, unwrapped 1; unwrap: 6->1 | top-level has no schema; data.debug.schema=hpo-debug/1; my ingest 6 vs 1 | every real download; synthetic generator emits unwrapped (why CI misses it); I4 | verify |
| s1-04 | cred viol 1; boolkey: 1->0 | 1 bool under SECRET_KEY in whole bundle (tibber_reauth_started); `_collect_strings` skips bool, `_walk` does not | real; I4 | verify |
| s1-05 | off-domain 25; declare: 25->0 | 25 undeclared: pump_duty written/silent 3, snapshots learners/peak_tracker 22 | silent: current writer (pump_arbiter _SLOTS). peak_tracker: NOT written by current code (coordinator.py:9254 "deliberately absent") — legacy snapshots only; sanitize dirty 0, consequence a debug log + sweep gap | weaken |

## s1-01 attack
The finder's by-t metric restricts BOTH sides to the 97 intersecting samples (`bias_by_t` builds `sub`
from store samples whose t is in the rows), and the dedupe perturbation also truncates the store to them:
0.000 is near-tautological. Repetition is real (457 consecutive repeat rows of 554) but not sufficient:
deduplication alone leaves delta 0.109 > 0.05 because the bundle's rows cover 97 of the store's 192
samples. The false-fail stands; the stated mechanism is incomplete (window coverage is the larger cause).
Severity low (dev tool false-fail, no runtime effect).

## s1-05 attack
Count reproduces (25) and enumerates all stores. But "writer fields" holds only for silent (3 leaves);
22 of 25 are peak_tracker in snapshots persisted before peak_tracker was removed from learner payloads.
Leave-one-out: without snapshots the count is 3. Severity low (diagnostic log only; no data refused).
