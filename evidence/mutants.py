# Reviewer's mutants: the ten round-1 survivors re-planted by hand, plus mutants of the delta's new code.
import subprocess, sys, pathlib
src = pathlib.Path(sys.argv[1]); orig = src.read_text()
M = [
 ("M1-excepts-always-narrow", "{'broad' if broad else 'narrow'}", "{'narrow'}"),
 ("M2-LIFE_CALLS-dropped", 'k.startswith("async_track_") or k in LIFE_CALLS', 'k.startswith("async_track_")'),
 ("M3-entry-fn-dropped", '"async_migrate_entry", "async_update_options")\n', '"async_update_options")\n'),
 ("M4-STORE_VERSION-dropped", '(tg.id.endswith("STORE_VERSION") or (tg.id == "CONFIG_ENTRY_VERSION" and p.name == "const.py"))', '(tg.id == "CONFIG_ENTRY_VERSION" and p.name == "const.py")'),
 ("M5-no-earlier-dropped", ' or [f"upgrade {r}:{tg.id} v{v} (no earlier version)"]', ''),
 ("M8-json-with-args", 'k == "json" and isinstance(f, ast.Attribute) and not n.args', 'k == "json" and isinstance(f, ast.Attribute)'),
 ("M12-module-level-self", 't.value.id == "self" and "." in q', 't.value.id == "self"'),
 ("M18-step-shape", 're.fullmatch(r"M\\d+", str(r.get("step"))) and r.get("id")', 'r.get("step") and r.get("id")'),
 ("M25-from-package-import-name", '[tail.split(".")[0]] if tail else [a.name for a in n.names]', '[tail.split(".")[0]] if tail else []'),
 ("M27-any-async_call", 'f.attr == "async_call" and isinstance(f.value, ast.Attribute) and f.value.attr == "services"', 'f.attr == "async_call"'),
 # delta's new code
 ("N1-flow-factory-ignored", 'fname(w) in fac or fname(w) == "EntitySelector"):\n                rows.add', 'fname(w) == "EntitySelector"):\n                rows.add'),
 ("N2-flow-loop-unrolled-dropped", 'keys += loops.get(id(n), {}).get(k.id) or [k.id]', 'keys += [k.id]'),
 ("N3-flow-outside-refusal-off", 'raise Refuse(f"config_flow.py:{n.lineno}: an entity selector outside', 'pass  # (f"config_flow.py:{n.lineno}: an entity selector outside'),
 ("N4-flow-keyname-refusal-off", 'raise Refuse(f"config_flow.py:{n.lineno}: an entity selector row whose key is no name")', 'continue'),
 ("N5-wiring-dict-spread-dropped", 'keys += [kk.attr if isinstance', 'keys += [] and [kk.attr if isinstance'),
 ("N6-wiring-tests-dropped", 'tests.append((e.func.value.id == nv, fname(e), e.args[0].value))', 'pass'),
 ("N7-wiring-unreadable-test-ok", 'raise Refuse(f"entry_config.py:{e.lineno}: FACTORY_KEPT', 'continue  # (f"entry_config.py:{e.lineno}: FACTORY_KEPT'),
 ("N8-wiring-two-comps-ok", 'if len(comps) != 1 or', 'if len(comps) < 1 or'),
 ("N9-wiring-isinstance-on-name-ok", 'and getattr(e.args[0], "id", None) == kv:', ':'),
 ("N10-flow-set-union-to-flow-only", 'sorted(set(flow_slots(repo)) | set(wiring_slots(repo)))', 'sorted(set(flow_slots(repo)))'),
 ("N11-wiring-only", 'sorted(set(flow_slots(repo)) | set(wiring_slots(repo)))', 'sorted(set(wiring_slots(repo)))'),
 ("N12-wiring-reason-ignored", 'and isinstance(vv, ast.Constant) and vv.value == reason]', 'and isinstance(vv, ast.Constant)]'),
]
try:
    for name, a, b in [("NULL", "", "")] + M:
        if a:
            if orig.count(a) != 1: print(f"{name}: NOT-APPLIED (count {orig.count(a)})"); continue
            src.write_text(orig.replace(a, b))
        r = subprocess.run([sys.executable, "-I", str(src), "--self-test"], capture_output=True, text=True, cwd=src.parent.parent.parent)
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
        print(f"{name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} | {tail[0][:140]}")
        src.write_text(orig)
finally:
    src.write_text(orig)
