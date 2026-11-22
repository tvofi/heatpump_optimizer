import json, sys
from pathlib import Path
SP = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
hdr = json.loads((SP / "headers.json").read_text()) if (SP / "headers.json").exists() else {}
common = (SP / "common.py").read_text()
extra = {"override": "_override_common.txt", "weather": "_weather_common.txt", "lead": "_lead_common.txt"}
groups = {"218ac218da41d87d": "override", "bcf290164a0edeeb": "override", "375376c4733a1a51": "override",
          "2699efc070f5d4e3": "override", "cc7e5a62ec1ea4d0": "override", "d05457b7adf4d691": "weather",
          "d943cc9f7670a834": "weather", "894b4e70a336f8fa": "lead", "2d6701afc323e1e8": "lead",
          "8cfd8cf0d8a58c83": "lead", "e02e1ac8cc0b714a": "lead", "ba1c58ad6dabbebd": "lead"}
for body in sorted((SP / "parts").glob("*.py")):
    key = body.stem
    h = hdr.get(key, "# header pending\n")
    parts = ["#!/usr/bin/env python3\n", h, common]
    if key in groups:
        parts.append("\n" + (SP / "parts" / extra[groups[key]]).read_text())
    parts.append("\n\n" + body.read_text())
    (out / f"probe_{key}.py").write_text("".join(parts))
print("assembled", len(list((SP / "parts").glob("*.py"))))
