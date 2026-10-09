"""Reviewer re-derivation of the nightly bound arithmetic at PR #2074's head.

Uses the tree's OWN functions only (driver_timeout, seed_pool_seconds,
pool_seconds, recorded_entries via a per-head closures.json), never a
re-implementation. Prints RESULT lines.
"""
import json
import subprocess
import sys

sys.path.insert(0, "/Users/timmalmstrom/hpo-seats/review-2074/wt/tests")
import mutation_table as mt  # noqa: E402

WT = "/Users/timmalmstrom/hpo-seats/review-2074/wt"
SCRIPT = "tests/boost_drift_replay.py"
HEADS = ["2e569748a", "fb11a0172", "a1da8d381", "be0cb8213", "816547efe",
         "b2b6acd64"]

print(f"TIMEOUT_SCALE={mt.TIMEOUT_SCALE}  POOL_SECONDS_NAME={mt.POOL_SECONDS_NAME}")
print(f"FLOOR used by the nightly (--timeout): 1200")


def recorded_at(ref: str) -> dict:
    raw = subprocess.run(["git", "-C", WT, "show", f"{ref}:tests/closures.json"],
                         capture_output=True, text=True, check=True).stdout
    return {s: r for s, r in json.loads(raw).get("recorded", {}).items()
            if isinstance(r, dict)}


def bound(solo: float | None, pool: dict[str, float], floor: int = 1200) -> int:
    """The head's bound for one driver, exactly as main() computes it:
    driver_timeout(floor, seed_pool_seconds(recorded_seconds(), pool)[script])."""
    rec = {SCRIPT: solo} if solo is not None else {}
    seeded = mt.seed_pool_seconds(rec, pool)
    return mt.driver_timeout(floor, seeded.get(SCRIPT, 0.0))


print("\n--- (a) the RCA's reproduced bounds, NO pool file (the fix's fallback) ---")
for h in HEADS:
    ent = recorded_at(h).get(SCRIPT)
    solo = ent.get("seconds") if ent else None
    b = bound(solo, {})
    print(f"  {h}: committed solo={solo} rc={ent.get('rc') if ent else None} "
          f"-> bound {b}")

print("\n--- (b) same inputs WITH the measured pool cost seeded ---")
for pool_sec, label in [(1573.0, "10-07/08 measured pool 1573 s"),
                        (800.2, "pool == solo (no pool pressure)"),
                        (2400.0, "pool 2400 s")]:
    b = bound(800.2, {SCRIPT: pool_sec})
    print(f"  solo=800.2 pool={pool_sec} ({label}) -> bound {b}")

print("\n--- (c) the three claims the dispatch names, checked by equality ---")
checks = [
    ("no recording -> 1200", bound(None, {}), 1200),
    ("525.3 -> 1576", bound(525.3, {}), 1576),
    ("800.2 -> 2401", bound(800.2, {}), 2401),
    ("1489.6 (current main) -> 4469", bound(1489.6, {}), 4469),
    ("seed never lowers: solo 1489.6 vs pool 100", bound(1489.6, {SCRIPT: 100.0}), 4469),
    ("pool 1573 covers 3x pool", bound(800.2, {SCRIPT: 1573.0}), 4719),
]
ok = True
for name, got, want in checks:
    flag = "ok " if got == want else "FAIL"
    ok = ok and got == want
    print(f"  {flag} {name}: got {got} want {want}")
print("RESULT bound-arithmetic: " + ("ALL-EQUAL" if ok else "MISMATCH"))

print("\n--- (d) seed_pool_seconds monotonicity (never lowers a bound) ---")
bad = 0
for solo in (0.0, 0.6, 199.0, 525.3, 800.2, 1489.6, 2000.0):
    for pool in (0.0, 1.0, 100.0, 730.0, 1573.0, 5000.0):
        base = mt.driver_timeout(1200, solo)
        seeded = mt.driver_timeout(1200, mt.seed_pool_seconds({SCRIPT: solo}, {SCRIPT: pool})[SCRIPT])
        if seeded < base:
            bad += 1
            print(f"  LOWERS at solo={solo} pool={pool}: {base} -> {seeded}")
print(f"RESULT seed-never-lowers: {'PASS' if bad == 0 else f'{bad} regressions'}")

print("\n--- (e) fail-soft: pool_seconds(None|missing|malformed) -> {} ---")
print(f"  pool_seconds(None)          = {mt.pool_seconds(None)}")
print(f"  pool_seconds(missing path)  = {mt.pool_seconds('/tmp/review2074-nope.json')}")
for body in ["", "{not json", "[]", '{"seconds": "x"}', '{"seconds": null}',
             '{"seconds": {"a": -5}}', '{"seconds": {"a": true}}', '"a string"',
             '{"nope": 1}', '{"seconds": [1,2]}']:
    p = "/tmp/review2074_malformed.json"
    with open(p, "w") as fh:
        fh.write(body)
    r = mt.pool_seconds(p)
    print(f"  {body[:24]!r:28} -> {r}")
print("RESULT fail-soft: read above; every case must be {} (or drop only bad rows)")

print("\n--- (f) round-trip: write_pool_seconds -> pool_seconds ---")
w = "/tmp/review2074_pool.json"
mt.write_pool_seconds({SCRIPT: 1573.0, "tests/features.py": 772.0}, w, head="d7c830c2f")
back = mt.pool_seconds(w)
print(f"  wrote 1573.0/772.0 -> read back {back}")
print(f"  file: {open(w).read().strip()}")
print(f"RESULT round-trip: {'PASS' if back == {SCRIPT: 1573.0, 'tests/features.py': 772.0} else 'FAIL'}")

print("\n--- (g) does a seeded pool value ever LOWER vs. no-file? ---")
# every driver: bound with pool file must be >= bound without it
rec = mt.recorded_entries()
solo_all = {s: float(r.get("seconds", 0.0)) for s, r in rec.items()}
fake_pool = {s: v * 1.3 for s, v in solo_all.items()}
worse = [s for s in solo_all
         if mt.driver_timeout(1200, mt.seed_pool_seconds(solo_all, fake_pool)[s])
         < mt.driver_timeout(1200, solo_all.get(s, 0.0))]
print(f"  drivers at head: {len(solo_all)}; drivers whose bound would lower: {len(worse)}")
print(f"RESULT monotone-over-committed-table: {'PASS' if not worse else worse}")
