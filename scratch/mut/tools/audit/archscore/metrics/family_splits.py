"""family_splits: declared entity families whose names do not sort together.

Definition (RCA-BULK-4's ``name_sort_families.py`` / ``family_check.py``,
with the declaration production now carries). Over every
entity name the shipped catalogue publishes (``translations/{en,sv}.json`` ->
``entity.<platform>.<translation_key>.name``, all platforms in one list, the
way the entity registry's default view sorts), a FAMILY is the set of
entities sharing the first underscore token of the translation_key (the one
in-code family declaration: ``entity_id = <platform>.heat_pump_optimizer_<key>``),
with >= 2 members across platforms -- unless ``const.ENTITY_FAMILY_OVERRIDES``
(the production declaration #1668 / #1760 landed, read here from const.py's
AST) homes the key in another family. A family is SPLIT in a language when its
members do not form one contiguous run in that language's name sort (en:
``casefold()``; sv: ``casefold()`` with a-ring < a-umlaut < o-umlaut after z,
approximating Intl.Collator('sv')).

Headline: split declared families in en + in sv. Details: the same count on
the raw lead token without overrides (bulk4's original KEY arm), the TRAIL
partition (last English word) for reference only -- the owner declined
renames for it at #797 -- and the extra runs.

Reads the two catalogues (JSON) and const.py (AST); stdlib only.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from . import common as C

SV_TAIL = str.maketrans({"å": "z\u0001", "ä": "z\u0002", "ö": "z\u0003"})


def sort_key(lang: str):
    if lang == "sv":
        return lambda n: n.casefold().translate(SV_TAIL)
    return lambda n: n.casefold()


def runs(order: list, members: set) -> int:
    pos = [i for i, row in enumerate(order) if row in members]
    if len(pos) < 2:
        return 0
    return 1 + sum(1 for a, b in zip(pos, pos[1:]) if b != a + 1)


def overrides(root: Path) -> dict[str, str]:
    import ast
    p = Path(root) / C.PKG_REL / "const.py"
    if not p.exists():
        return {}
    for s in ast.parse(p.read_text()).body:
        tgt = s.targets[0] if isinstance(s, ast.Assign) else getattr(s, "target", None)
        if isinstance(tgt, ast.Name) and tgt.id == "ENTITY_FAMILY_OVERRIDES" and isinstance(s.value, ast.Dict):
            return {k.value: v.value for k, v in zip(s.value.keys, s.value.values)
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant)}
    return {}


OV: dict[str, str] = {}


def families(rows, how):
    fam: dict[str, set] = {}
    for plat, key, en, _sv in rows:
        if how == "DECLARED":
            tok = OV.get(key, key.split("_")[0])
        else:
            tok = key.split("_")[0] if how == "KEY" else en.split()[-1].strip("()").casefold()
        fam.setdefault(tok, set()).add((plat, key))
    return {k: v for k, v in fam.items() if len(v) >= 2}


def split(rows, how, lang):
    idx = 2 if lang == "en" else 3
    order = [(p, k) for p, k, *_ in sorted(rows, key=lambda r: sort_key(lang)(r[idx]))]
    out = []
    for tok, members in sorted(families(rows, how).items()):
        r = runs(order, members)
        if r > 1:
            out.append((tok, r, sorted(row[idx] for row in rows if (row[0], row[1]) in members)))
    return out


def load_rows(root: Path):
    d = Path(root) / C.PKG_REL / "translations"
    en = json.loads((d / "en.json").read_text())["entity"]
    sv = json.loads((d / "sv.json").read_text())["entity"]
    return [(plat, key, body["name"], sv.get(plat, {}).get(key, {}).get("name", "~" + key))
            for plat, ents in en.items() for key, body in ents.items()]


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    rows = load_rows(root)
    OV.clear()
    OV.update(overrides(root))
    res = {}
    for how in ("DECLARED", "KEY", "TRAIL"):
        for lang in ("en", "sv"):
            res[(how, lang)] = split(rows, how, lang)
    key_en, key_sv = res[("DECLARED", "en")], res[("DECLARED", "sv")]
    return {
        "metric": "family_splits",
        "value": len(key_en) + len(key_sv),
        "details": {
            "names": len(rows),
            "declared_families": len(families(rows, "DECLARED")),
            "overrides": len(OV),
            "raw_lead_token_splits_en_sv": [len(res[("KEY", "en")]), len(res[("KEY", "sv")])],
            "declared_split_en": [f"{t} ({r} runs): {n}" for t, r, n in key_en],
            "declared_split_sv": [f"{t} ({r} runs): {n}" for t, r, n in key_sv],
            "extra_runs": sum(r - 1 for _, r, _ in key_en + key_sv),
            "trail_split_en_reference": len(res[("TRAIL", "en")]),
            "trail_split_sv_reference": len(res[("TRAIL", "sv")]),
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }

