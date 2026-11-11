"""Class sweep N-name-sort (R10 D14 steps 3-4): every seam where a family
declaration can home an entity into a family its own name does not lead with.

Property (D7-s3-53's phenomenon_property): an ENTITY_FAMILY_OVERRIDES entry
homes an entity only into the family its own English name leads with.

Seams enumerated:
  decl:<key>      every override entry in const.py (AST); instance when the
                  target is not the casefolded first word of the key's en name.
  gate:<file>     every non-audit file that reads the override table (text
                  search of tools/, tests/, custom_components/); instance when
                  its family block carries no name-lead comparison (static:
                  no `.split()[0]`/`split(" ")[0]` on a name within the block).
                  For archscore C6 a behavioural probe also runs: the
                  D7-s3-53 game tree (invented two-member family) must read
                  >= 1 orphan; 0 is an instance.

Run:  python3 dev/audit/rounds/round10/D14/sweep/namesort_override_seams.py [--perturb] [--null]
  baseline: decl instances 0; gate instances listed.
  --perturb: one-line re-introduction in memory -- override
             optimization_status -> 'zzpair' -- decl instances rise by 1.
  --null:    clean fixture (table of only lead-token overrides, one gate
             carrying the lead-word check) -> 0 instances.
"""
import argparse, ast, json, re, shutil, sys, tempfile
from pathlib import Path

ROOT = Path.cwd()
PKG = "custom_components/heatpump_optimizer"
LEAD = re.compile(r"split\((?:\" \"|' ')?\)\[0\]")


def overrides(root):
    for s in ast.parse((root / PKG / "const.py").read_text()).body:
        t = s.targets[0] if isinstance(s, ast.Assign) else getattr(s, "target", None)
        if isinstance(t, ast.Name) and t.id == "ENTITY_FAMILY_OVERRIDES":
            return {k.value: v.value for k, v in zip(s.value.keys, s.value.values)}
    return {}


def en_names(root):
    en = json.loads((root / PKG / "translations/en.json").read_text())["entity"]
    return {k: b["name"] for p in en.values() for k, b in p.items()}


def decl_seams(ov, names):
    out = []
    for k, v in sorted(ov.items()):
        lead = names.get(k, "").split()[0].casefold() if names.get(k) else None
        out.append((f"decl:{k}", "const.ENTITY_FAMILY_OVERRIDES", lead != v,
                    f"target {v!r}, en lead {lead!r}"))
    return out


def gate_files(root):
    hits = []
    for base in ("tools", "tests", PKG):
        for p in sorted((root / base).rglob("*.py")):
            if not p.is_file():
                continue
            s = p.read_text(errors="ignore")
            if "ENTITY_FAMILY_OVERRIDES" in s or re.search(r"\bF\.overrides\(|def overrides\(", s):
                if p.relative_to(root).as_posix().endswith("const.py"):
                    continue
                hits.append(p)
    return hits


def block(src):
    i = min([j for j in (src.find("ENTITY_FAMILY_OVERRIDES"), src.find("overrides(")) if j >= 0])
    return src[i:i + 6000]


def c6_probe(root):
    sys.path.insert(0, str(root / "tools/audit"))
    from archscore import counters as K  # noqa
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        shutil.copytree(root / PKG, t / PKG)
        c = t / PKG / "const.py"
        c.write_text(c.read_text().replace(
            "ENTITY_FAMILY_OVERRIDES: Final[dict[str, str]] = {",
            "ENTITY_FAMILY_OVERRIDES: Final[dict[str, str]] = {\n    \"optimization_status\": \"zzpair\",\n"
            "    \"solar_surplus_forecast\": \"zzpair\",", 1))
        return K.family_orphan_overrides(t)


def gate_seams(root):
    out = []
    for p in gate_files(root):
        rel = p.relative_to(root).as_posix()
        guarded = bool(LEAD.search(block(p.read_text())))
        note = "static: name-lead comparison " + ("present" if guarded else "absent")
        if rel.endswith("archscore/counters.py"):
            n = c6_probe(root)
            guarded = n >= 1
            note += f"; behavioural: invented-family orphans={n}"
        out.append((f"gate:{rel}", rel, not guarded, note))
    return out


def null_fixture(tmp):
    (tmp / PKG / "translations").mkdir(parents=True)
    (tmp / PKG / "const.py").write_text('ENTITY_FAMILY_OVERRIDES = {"a_x": "lifetime"}\n')
    (tmp / PKG / "translations/en.json").write_text(json.dumps(
        {"entity": {"sensor": {"a_x": {"name": "Lifetime A"}}}}))
    (tmp / "tests").mkdir(); (tmp / "tools").mkdir()
    (tmp / "tests/g.py").write_text("ov = const.ENTITY_FAMILY_OVERRIDES\nok = name.split()[0].casefold() == ov[k]\n")
    return tmp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--null", action="store_true")
    a = ap.parse_args()
    if a.null:
        with tempfile.TemporaryDirectory() as t:
            r = null_fixture(Path(t))
            seams = decl_seams(overrides(r), en_names(r)) + [
                (f"gate:{p.name}", p.name, not LEAD.search(block(p.read_text())), "")
                for p in gate_files(r)]
    else:
        ov = overrides(ROOT)
        if a.perturb:
            ov["optimization_status"] = "zzpair"
        seams = decl_seams(ov, en_names(ROOT)) + gate_seams(ROOT)
    for s, f, inst, note in seams:
        print(f"SEAM {s} {'INSTANCE' if inst else 'ok'} -- {note}")
    print(f"RESULT seams={len(seams)} instances={sum(1 for x in seams if x[2])}")
    print(f"RESULT decl_instances={sum(1 for x in seams if x[2] and x[0].startswith('decl:'))}")


if __name__ == "__main__":
    main()
