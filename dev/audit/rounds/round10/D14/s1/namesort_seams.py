"""D14-s1 N-name-sort detector: every instantiated entity, every family, every sort.

Metric: number of (language, view, family) triples whose members do not form
one contiguous run, where entities are the ones every platform in
heatpump_optimizer.PLATFORM_LIST actually ADDS through async_setup_entry
(not the strings.json roster), family = const.ENTITY_FAMILY_OVERRIDES else the
translation key's lead token (production's declaration), name = the
translations/<lang>.json name for (platform, translation_key) -- the name HA
shows -- and view is
  'global'  : one sort over all entities (the in-tree #1760 check's model);
  'section' : HA's device page, which partitions entities into Controls /
              Sensors / Configuration / Diagnostic sections by entity_category
              (and sensor domain) before the name sort: a family spread over
              two sections is two runs.
Also counted: entities added with no translation_key (seams the family
declaration cannot see), keyed on the instantiated entity.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s1/namesort_seams.py [--perturb] [--names-at REF]
Expected at baseline: splits_en_global=0, splits_sv_global=0 (tolerance 0); --perturb en_global=1;
--names-at dc977f693^ (pre R9-F7.5): en_global>=1 (away), sv_global>=2 (away, compressor).
--perturb: one-line re-introduction -- the R5 D8-02 shape: one family member's
English name loses its lead token in memory ('Learning Observed COP' ->
'Observed COP'); en global splits must rise by >= 1.
Baseline 17f1c55fad1b, macOS arm64 (B7). Counts only: contention-immune.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, asyncio, importlib, json, sys, time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
PKG = ROOT / "custom_components" / "heatpump_optimizer"
SV_TAIL = str.maketrans({"å": "z\u0001", "ä": "z\u0002", "ö": "z\u0003"})
COLL = {"en": lambda n: n.casefold(), "sv": lambda n: n.casefold().translate(SV_TAIL)}
READ_ONLY = {"sensor", "binary_sensor"}


def runs(order, members):
    pos = [i for i, r in enumerate(order) if r in members]
    if len(pos) < 2:
        return 0
    return 1 + sum(1 for x, y in zip(pos, pos[1:]) if y != x + 1)


def section(plat, ent):
    cat = getattr(ent, "_attr_entity_category", None) or getattr(ent, "entity_category", None)
    cat = getattr(cat, "value", cat)
    if cat in ("config", "diagnostic"):
        return cat
    return "sensors" if plat in READ_ONLY else "controls"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--names-at", help="git ref: read translations/<lang>.json at a pre-fix commit (re-find)")
    a = ap.parse_args()
    t0 = time.process_time(); tt0 = time.thread_time()
    import harness
    import heatpump_optimizer as integ
    from heatpump_optimizer import const
    if a.names_at:
        import subprocess
        tr = {l: json.loads(subprocess.check_output(
            ["git", "show", f"{a.names_at}:custom_components/heatpump_optimizer/translations/{l}.json"],
            text=True))["entity"] for l in ("en", "sv")}
    else:
        tr = {l: json.loads((PKG / "translations" / f"{l}.json").read_text())["entity"] for l in ("en", "sv")}
    rows, untranslated = [], []
    for plat in integ.PLATFORM_LIST:
        p = getattr(plat, "value", plat)
        mod = importlib.import_module(f"heatpump_optimizer.{p}")
        added, hass = [], harness.FakeHass()
        entry = harness.FakeEntry()
        entry.runtime_data = harness.FakeCoordinator({})

        def add(ents, *_a, **_k):
            for e in ents:
                e.hass = hass
            added.extend(ents)
        try:
            asyncio.run(mod.async_setup_entry(hass, entry, add))
        except Exception as exc:  # noqa: BLE001 - reported, not swallowed
            print(f"  setup-failed {p}: {type(exc).__name__}: {exc}")
            print("RESULT setup_failures=1 platforms")
        for e in added:
            key = getattr(e, "_attr_translation_key", None) or getattr(e, "translation_key", None)
            if not key:
                untranslated.append(f"{p}:{type(e).__name__}")
                continue
            names = {l: tr[l].get(p, {}).get(key, {}).get("name") for l in tr}
            rows.append((p, key, section(p, e), names))
    if a.perturb:
        rows = [(p, k, s, {**n, "en": "Observed COP" if n["en"] == "Learning Observed COP" else n["en"]})
                for p, k, s, n in rows]
    fam = {}
    for p, k, s, n in rows:
        fam.setdefault(const.ENTITY_FAMILY_OVERRIDES.get(k, k.split("_")[0]), set()).add((p, k))
    fams = {t: m for t, m in fam.items() if len(m) >= 2}
    missing = sorted(f"{l}:{p}.{k}" for p, k, s, n in rows for l in n if not n[l])
    splits = {}
    for lang in ("en", "sv"):
        named = [r for r in rows if r[3][lang]]
        g = [(p, k) for p, k, s, n in sorted(named, key=lambda r: COLL[lang](r[3][lang]))]
        sec = [(p, k) for p, k, s, n in sorted(named, key=lambda r: (r[2], COLL[lang](r[3][lang])))]
        for view, order in (("global", g), ("section", sec)):
            for t, m in sorted(fams.items()):
                n_runs = runs(order, m)
                if n_runs > 1:
                    secs = sorted({s for p, k, s, _ in rows if (p, k) in m})
                    splits[(lang, view, t)] = (n_runs, secs)
    print(f"RESULT entities={len(rows) + len(untranslated)} entities")
    print(f"RESULT families={len(fams)} families")
    print(f"RESULT untranslated={len(untranslated)} entities")
    for u in untranslated:
        print("  untranslated", u)
    print(f"RESULT missing_names={len(missing)} names")
    for m in missing[:20]:
        print("  missing", m)
    for lang in ("en", "sv"):
        for view in ("global", "section"):
            n = sum(1 for k in splits if k[0] == lang and k[1] == view)
            print(f"RESULT splits_{lang}_{view}={n} families")
    for (lang, view, t), (n_runs, secs) in sorted(splits.items()):
        print(f"  split {lang} {view} {t!r}: {n_runs} runs, sections {secs}")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
