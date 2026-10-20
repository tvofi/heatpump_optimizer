#!/usr/bin/env python3
"""Reviewer's planted case: a real directory emptied FILE BY FILE under a ref
namespace, and a live line citing the emptied directory. Runs production
`guard()` from tests/layout.py at the head on a throwaway repo."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.home() / "hpo-seats/r10s3/rev-2488"
sys.path.insert(0, str(ROOT / "tests"))
import layout  # noqa: E402
from throwaway_git import throwaway_git_init  # noqa: E402

MANIFEST = {"categories": [{"name": "docs", "globs": ["docs/*.md"], "why": "t"},
                           {"name": "tools", "globs": ["tools/**"], "why": "t"}],
            "historical": [],
            "ref_namespaces": ["ns/"],
            "retired": [{"old": "ns/sub/deep/a.md", "new": "tools/a.md", "since": "1"},
                        {"old": "ns/sub/deep/b.md", "new": "tools/b.md", "since": "1"}]}
BASE = {"docs/a.md": "intro\n", "ns/sub/deep/a.md": "", "ns/sub/deep/b.md": ""}

g = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
tmp = Path(tempfile.mkdtemp(prefix="hpo-r2488-refns-"))
try:
    env = throwaway_git_init(tmp, "-q")
    for p, t in {**BASE, layout.MANIFEST: json.dumps(MANIFEST)}.items():
        (tmp / p).parent.mkdir(parents=True, exist_ok=True)
        (tmp / p).write_text(t)
    subprocess.run([*g, "add", "-A"], cwd=tmp, check=True, env=env)
    subprocess.run([*g, "commit", "-qm", "base"], cwd=tmp, check=True, env=env)
    sha = layout.git(tmp, "rev-parse", "HEAD").decode().strip()
    # the move lands file by file; a live doc cites the emptied directory
    subprocess.run([*g, "rm", "-q", "ns/sub/deep/a.md", "ns/sub/deep/b.md"], cwd=tmp, check=True, env=env)
    (tmp / "tools").mkdir(exist_ok=True)
    (tmp / "tools/a.md").write_text("")
    (tmp / "tools/b.md").write_text("")
    (tmp / "docs/a.md").write_text("git diff -- ns/sub/deep/ now\n")
    subprocess.run([*g, "add", "-A"], cwd=tmp, check=True, env=env)
    got = layout.guard(tmp, MANIFEST, sha)
    print(f"RESULT planted deep manufactured parent, citation of ns/sub/deep/: {len(got)} refusal(s)")
    for f in got:
        print("   ", f)
    landed = layout.landed(layout.tracked(tmp), MANIFEST["retired"], MANIFEST["ref_namespaces"])
    print("RESULT landed entries here:", [e["old"] for e in landed])
finally:
    import shutil
    shutil.rmtree(tmp)
