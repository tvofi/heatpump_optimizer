"""Token-permission set per job: the second half of each unit's null control.

    python3 -I measure/permset.py RAW_DIR RUN_ID[,RUN_ID..] [--strip-prefix]

For every executed job of the named runs (raw/jobs_<id>.json), reads the saved
'Set up job' header raw/logs/head_<job id>.txt and prints
`job | Permission: level ...` plus `Secret source:`. --strip-prefix drops a
reusable workflow's `<caller> / ` so a before (standalone) and an after (called)
run compare by the callee's job name. Compare two outputs with `diff`: a unit's
null control is an empty diff.
"""
import json, re, sys
from pathlib import Path

raw = Path(sys.argv[1]); strip = "--strip-prefix" in sys.argv
for rid in sys.argv[2].split(","):
    for j in json.loads((raw / f"jobs_{rid}.json").read_text())["jobs"]:
        if j["conclusion"] == "skipped": continue
        f = raw / "logs" / f"head_{j['id']}.txt"
        name = j["name"].split(" / ", 1)[-1] if strip else j["name"]
        if not f.exists() or not f.stat().st_size:
            print(f"{name} | UNREAD"); continue
        t = f.read_text(errors="replace")
        m = re.search(r"##\[group\]GITHUB_TOKEN Permissions\n(.*?)##\[endgroup\]", t, re.S)
        perms = [re.sub(r"^\S+Z ", "", l).strip() for l in m.group(1).splitlines()] if m else ["NO-BLOCK"]
        src = re.search(r"Secret source: (\S+)", t)
        print(f"{name} | {', '.join(perms)} | secrets {src.group(1) if src else '?'}")
