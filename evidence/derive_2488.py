#!/usr/bin/env python3
"""Reviewer's own harness for PR #2488 (fix-review step 1/2/8).

Reads production `landed`/`guard`/`stale_lines` from tests/layout.py at the
head and prints RESULT lines. Never writes into the review worktree.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.home() / "hpo-seats/r10s3/rev-2488"
BASE = "76bb45628745ff8843f61c1708641f271643a224"
sys.path.insert(0, str(ROOT / "tests"))
import layout  # noqa: E402

manifest = json.loads((ROOT / "tests/layout.json").read_text())
tracked = layout.tracked(ROOT)
skip = (layout.MANIFEST, *manifest["historical"], *layout.GUARD_EXEMPT)


def result(name, value):
    print(f"RESULT {name}: {value}")


# --- landed, with and without the mechanism -------------------------------
now = layout.landed(tracked, manifest["retired"], manifest.get("ref_namespaces", ()))
none = layout.landed(tracked, manifest["retired"], ())
result("landed.head.with_key", f"{len(now)} entries; handoff/ present={any(e['old'] == 'handoff/' for e in now)}")
result("landed.head.without_key", f"{len(none)} entries; handoff/ present={any(e['old'] == 'handoff/' for e in none)}")
result("landed.without_key.moved_under_handoff",
       sorted(e["old"] for e in none if e["old"].startswith("handoff/")))

# --- guard with the clause deleted (mutation proof) -----------------------
m_no = dict(manifest)
m_no.pop("ref_namespaces", None)
found_no = layout.guard(ROOT, m_no, BASE)
found_yes = layout.guard(ROOT, manifest, BASE)
result("guard.head.deleted_clause", len(found_no))
result("guard.head.with_clause", len(found_yes))
for f in found_yes:
    print(f"  WITH-CLAUSE {f}")

# --- citations the exemption spares: branch names under handoff/ ----------
def citations(entries, old):
    """Every live line in the index citing `old` (skip dirs excluded)."""
    files = [f":{p}" for p in tracked if not p.startswith(skip)]
    texts = layout.blobs(ROOT, files)
    hits = []
    for k, t in texts.items():
        if not t:
            continue
        for o, line in layout.stale_lines(t, entries):
            if o == old:
                hits.append((k[1:], line.strip()[:100]))
    return hits


h_hits = citations(none, "handoff/")
r_hits = citations(none, "handoff/round9/")
result("sweep_without_key.handoff", f"{len(h_hits)} citation(s) in {len({f for f, _ in h_hits})} file(s)")
result("sweep_without_key.handoff_round9", f"{len(r_hits)} citation(s) in {len({f for f, _ in r_hits})} file(s)")
result("sweep_with_key.handoff", len(citations(now, "handoff/")))
result("sweep_with_key.handoff_round9", len(citations(now, "handoff/round9/")))

# --- the same over the BASE tree's live files (the un-swept state) -------
def base_blobs(paths):
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, check=True,
                          capture_output=True, input="".join(f"{BASE}:{p}\n" for p in paths).encode())
    out, buf = {}, proc.stdout
    for p in paths:
        head, _, buf = buf.partition(b"\n")
        if head.endswith(b" missing"):
            out[p] = None
            continue
        size = int(head.rsplit(b" ", 1)[1])
        data, buf = buf[:size], buf[size + 1:]
        out[p] = None if b"\0" in data[:8000] else data.decode(errors="replace")
    return out


base_live = [p for p in tracked if not p.startswith(skip)]
# files exist at head and base for the swept ones; read base text for those present there
base_text = base_blobs(base_live)
rb = Counter()
for p, t in base_text.items():
    if not t:
        continue
    for o, line in layout.stale_lines(t, none):
        if o == "handoff/round9/":
            rb[p] += 1
result("base_live_files.handoff_round9", f"{sum(rb.values())} citation(s) in {len(rb)} file(s)")
for p, n in sorted(rb.items()):
    print(f"  BASE-UNSWEPT {n:2d} {p}")

# --- distinct files for the handoff/ 322 claim ----------------------------
per_file = Counter(f for f, _ in h_hits)
result("handoff_citations_files", len(per_file))
result("handoff_citations_lines", sum(per_file.values()))
for f, n in per_file.most_common(8):
    print(f"  BRANCH-CITE {n:4d} {f}")
