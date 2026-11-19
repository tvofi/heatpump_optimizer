import importlib.util, sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
M = [
 ("R1 dict non-widget value ignored", "(found.add(bounds(v)) if is_num(v) else presented.append(v))", "(found.add(bounds(v)) if is_num(v) else None)"),
 ("R2 arg-after-key ignored", "presented += [a for a in n.args[i + 1:i + 2] if not is_num(a)]", "pass"),
 ("R3 default= keyword ignored", 'presented += [k.value for k in n.keywords if k.arg == "default"]', "pass"),
 ("R4 no_default ignored", 'if isinstance(v, ast.Name) and v.id in (row.get("no_default") or []):', "if False:"),
 ("R5 unreadable default skipped", "raise ValueError(f\"{key}'s default at {f} line {v.lineno} does not read: {e}\")", "continue"),
 ("R6 empty defaults accepted", "if not defaults:\n                raise", "if False:\n                raise"),
 ("R7 only first default compared", "else defaults):", "else defaults[:1]):"),
 ("R8 unknown row field accepted", 'if set(row) - {"field", "key", "no_default"}:', "if False:"),
 ("R9 two args after key", "n.args[i + 1:i + 2]", "n.args[i + 1:i + 3]"),
 ("R10 default vs max", "else defaults):", "else [(None, hi)]):"),
]
def run(text, tag):
    p = pathlib.Path(sys.argv[2]) / "cs_mut.py"; p.write_text(text)
    spec = importlib.util.spec_from_file_location("cs_mut_" + str(abs(hash(tag))), p); m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m); r = m.population_self_test()
    except Exception as e:
        return f"CRASH {type(e).__name__}: {e}"[:150]
    bad = [k for k, v in r.items() if not v]
    return f"{len(r)-len(bad)}/{len(r)} held; red: {bad[:2]}"
print("UNMUTATED", run(src, "base"))
for name, o, n in M:
    if src.count(o) != 1:
        print(name, "SKIP count", src.count(o)); continue
    res = run(src.replace(o, n), name)
    print(name, "SURVIVED" if res.startswith("28/28") else "KILLED", "|", res)
