import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from spec import S
W = Path(sys.argv[1])
TPL = (Path(__file__).parent / "probe_template.py.tmpl").read_text()
for key, (line, old, new, metric, kind, inputs, direction, _n) in S.items():
    body = (TPL.replace("@KEY@", key).replace("@LINE@", str(line)).replace("@METRIC@", metric).replace("@KIND@", kind)
            .replace("@DIR@", direction).replace("@OLDTXT@", old).replace("@NEWTXT@", new)
            .replace("@SPEC@", repr({"old": old, "new": new, "inputs": inputs})))
    (W / "probes" / f"probe_{key}.py").write_text(body)
print(len(S))
