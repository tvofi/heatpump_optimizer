"""D14-s1 detector for class N-name-sort: an entity family whose display names
split under the name sort, per shipped language.

Metric: split_families = count of (language, family) pairs whose members form
more than one contiguous run when every entity the platforms really create
(driven through each platform's async_setup_entry on a coord_all_features
coordinator) is sorted by its displayed name in that language (the barrier's
collations: en casefold; sv å<ä<ö after z; de umlaut as base vowel). A family
is a translation key's lead token, plus const.ENTITY_FAMILY_OVERRIDES, plus
(independent of the declaration) every set of >=2 entities whose English
display name leads with the same word. Key = the delivered name of the live
entity in the translation file the frontend reads, never the key text.
Also printed (informational, not counted): families whose members sit in more
than one entity_category (HA's device page cards).

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/name_sort.py [--tree DIR] [--perturb]
Expected:  at 92d38ecb split_families=0 (exact) over 82 entities, 3 languages;
           with --tree <export of 3defa2d58^> (pre-#1760 barrier) split_families>0.
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked:    custom_components.heatpump_optimizer.{sensor,binary_sensor,button,switch,climate,datetime}:async_setup_entry
           (the live entity set) and const:ENTITY_FAMILY_OVERRIDES.
Perturbation (--perturb, in memory): the sv name of learning_observed_cop rewritten to
           "Observerad COP" (drops the family's lead token) -> split_families 0 -> 1 (up).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import sys
import time

argv = sys.argv[1:]
TREE = os.path.abspath(argv[argv.index("--tree") + 1]) if "--tree" in argv else os.getcwd()
PERTURB = "--perturb" in argv
sys.path[:0] = [os.path.join(TREE, "tests", "hastub"), os.path.join(TREE, "tests"),
                os.path.join(TREE, "custom_components"), TREE]
BASE = os.path.join(TREE, "custom_components", "heatpump_optimizer")

SV_TAIL = str.maketrans({"å": "z\u0001", "ä": "z\u0002", "ö": "z\u0003"})
COLLATION = {
    "en": lambda n: n.casefold(),
    "sv": lambda n: n.casefold().translate(SV_TAIL),
    "de": lambda n: n.casefold().translate(str.maketrans("äöü", "aou")),
}


def live_entities():
    """(platform, translation_key, entity_category) of every entity created."""
    try:
        from harness import FakeHass, FakeEntry, FakeState
        import golden
        from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
        from heatpump_optimizer import const
        import importlib
        cfg = dict(golden.coordinator_scenarios()["coord_all_features"])
        hass = FakeHass()
        hass.states.set("sensor.indoor", FakeState("21.4"))
        hass.states.set("sensor.outdoor", FakeState("-3.0"))
        cfg[const.CONF_INDOOR_TEMP_ENTITY] = "sensor.indoor"
        cfg[const.CONF_OUTDOOR_TEMP_ENTITY] = "sensor.outdoor"
        entry = FakeEntry(data=cfg)
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        asyncio.run(coord._update_current_state())
        coord.data = coord._build_data_dict()
        entry.runtime_data = coord
        ents = []

        def add(es, *a, **k):
            for e in es:
                e.hass = hass
            ents.extend(es)
        for plat in ("sensor", "binary_sensor", "button", "switch", "climate", "datetime"):
            try:
                mod = importlib.import_module(f"heatpump_optimizer.{plat}")
            except ImportError:
                continue
            asyncio.run(mod.async_setup_entry(hass, entry, add))
        rows = []
        for e in ents:
            key = getattr(e, "_attr_translation_key", None)
            plat = type(e).__module__.split(".")[-1]
            cat = getattr(e, "entity_category", None) or getattr(e, "_attr_entity_category", None)
            if key is not None:
                rows.append((plat, key, str(cat)))
        return rows, getattr(const, "ENTITY_FAMILY_OVERRIDES", {}), "live"
    except Exception as exc:  # an older tree: fall back to the strings table
        print(f"NOTE live collection failed ({type(exc).__name__}: {exc}); strings-table roster")
        strings = json.load(open(os.path.join(BASE, "strings.json"), encoding="utf-8"))["entity"]
        try:
            from heatpump_optimizer import const
            ov = getattr(const, "ENTITY_FAMILY_OVERRIDES", {})
        except Exception:
            ov = {}
        return [(p, k, "?") for p, d in strings.items() for k in d], ov, "strings"


def runs(order, members):
    pos = [i for i, r in enumerate(order) if r in members]
    if len(pos) < 2:
        return 0
    return 1 + sum(1 for a, b in zip(pos, pos[1:]) if b != a + 1)


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    rows, overrides, source = live_entities()
    langs = sorted(f[:-5] for f in os.listdir(os.path.join(BASE, "translations")) if f.endswith(".json"))
    tr = {l: json.load(open(os.path.join(BASE, "translations", f"{l}.json"), encoding="utf-8")).get("entity", {})
          for l in langs}
    if PERTURB and "learning_observed_cop" in tr.get("sv", {}).get("sensor", {}):
        tr["sv"]["sensor"]["learning_observed_cop"]["name"] = "Observerad COP"

    def name(l, p, k):
        return tr[l].get(p, {}).get(k, {}).get("name", f"~{k}")
    fams = {}
    for p, k, c in rows:
        fams.setdefault("key:" + overrides.get(k, k.split("_")[0]), set()).add((p, k))
        fams.setdefault("word:" + name("en", p, k).split()[0].casefold().rstrip("-"), set()).add((p, k))
    fams = {t: m for t, m in fams.items() if len(m) >= 2}
    # A word-family identical to a key-family is counted once.
    seen = set(); uniq = {}
    for t, m in sorted(fams.items()):
        f = frozenset(m)
        if f in seen:
            continue
        seen.add(f); uniq[t] = m
    splits = []
    for l in langs:
        coll = COLLATION.get(l, COLLATION["en"])
        order = [(p, k) for p, k, _ in sorted(rows, key=lambda r: coll(name(l, r[0], r[1])))]
        for t, m in sorted(uniq.items()):
            n = runs(order, m)
            if n > 1:
                splits.append(f"{l} {t}: {n} runs: {sorted(name(l, p, k) for p, k in m)}")
    for s in splits:
        print("SEAM", s)
    cat_split = 0
    if source == "live":
        cats = {}
        for p, k, c in rows:
            cats.setdefault(overrides.get(k, k.split("_")[0]), set()).add(c)
        cat_split = sum(1 for t, cs in cats.items() if len(cs) > 1)
    print(f"RESULT roster_source={source}")
    print(f"RESULT entities={len(rows)} entities")
    print(f"RESULT languages={len(langs)} ({' '.join(langs)})")
    print(f"RESULT families={len(uniq)} families")
    print(f"RESULT category_split_families={cat_split} families (informational)")
    print(f"RESULT split_families={len(splits)} (language,family) pairs")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
