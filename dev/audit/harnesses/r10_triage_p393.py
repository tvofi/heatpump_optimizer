#!/usr/bin/env python3
"""Triage batch 127 (P393, P396): the measurements behind two rulings.

WHY IT EXISTS. The owner's bar (2026-11-05) needs a measured figure, cited to
the command that prints it. Each figure in dev/programme/triage/s6-batch127.md
is printed by one arm here, so another seat re-derives it.

    python3 -I dev/audit/harnesses/r10_triage_p393.py stale  EVENTS.tsv
    python3 -I dev/audit/harnesses/r10_triage_p393.py bodies MERGED.json

`stale` (P393) fetches every `verdict/*` and `review/*` head into the private
namespace refs/p393scan/ of the clone it runs in, then walks each verdict ref
oldest first. An instance is a `merge <head>` verdict after a `blocked <head>`
verdict at the same head: the orchestrator's enumerator rule. Each verdict's
bus-nonce is read from VERDICT.md at the review SHA its `bus-confirmed:`
trailer names, and the nonce's first dispatch time from the seat events log
(`reviewer-fire` rows, `nonce=<8 hex>`), a host-local file another seat reads
only if it holds the log. STALE: the merge verdict's nonce was dispatched
before the blocked verdict's. LATER: dispatched after. SAME: one nonce posted
both. UNKNOWN: a dispatch time is missing (the log starts 2026-10-28).

`bodies` (P396) reads a `gh pr list --state merged --json number,body,mergedAt`
dump and counts bodies whose `## Forward-carry` section holds a `Carry:` line
that the triage gate's PROPOSAL_RE matches with no RULING_CITE_RE citation.
Both regexes are imported from tools/audit/seat/roster_edit.py, not copied.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
sys.path.insert(0, str(ROOT / "tools" / "audit"))

SUBJ = re.compile(r"^verdict: #(\d+) Fix review: (merge|blocked) ([0-9a-f]{40})")
CONF = re.compile(r"^bus-confirmed: .*\(review/\d+ at ([0-9a-f]{40})\)", re.M)
NONCE = re.compile(r"bus-nonce:\s*([0-9a-f]{8})")
NS = "refs/p393scan"


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *a],
                          capture_output=True, text=True).stdout


def dispatch_times(events: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in Path(events).read_text().splitlines():
        f = line.split("\t")
        if len(f) >= 6 and f[2] == "reviewer-fire":
            m = re.search(r"nonce=([0-9a-f]{8})", f[5])
            if m:
                out.setdefault(m.group(1), f[1])
    return out


def nonce_of(body: str) -> str | None:
    m = CONF.search(body)
    if not m:
        return None
    n = NONCE.search(git("show", f"{m.group(1)}:VERDICT.md"))
    return n.group(1) if n else None


def stale(events: str) -> int:
    subprocess.run(["git", "-C", str(ROOT), "fetch", "-q", "origin",
                    f"+refs/heads/verdict/*:{NS}/verdict/*",
                    f"+refs/heads/review/*:{NS}/review/*"], check=True)
    disp = dispatch_times(events)
    counts = {"STALE": 0, "LATER": 0, "SAME": 0, "UNKNOWN": 0}
    refs = git("for-each-ref", "--format=%(refname)", f"{NS}/verdict").split()
    for ref in refs:
        blocked: dict[str, str | None] = {}
        seen: set[str] = set()
        for ent in git("log", "--reverse", "--format=%H%x00%B%x01", ref).split("\x01"):
            if "\x00" not in ent:
                continue
            body = ent.strip("\n").split("\x00", 1)[1].strip()
            m = SUBJ.match(body)
            if not m:
                continue
            pr, verdict, head = m.groups()
            if verdict == "blocked":
                blocked[head] = nonce_of(body)
                continue
            if head not in blocked or head in seen:
                continue
            seen.add(head)
            mn, bn = nonce_of(body), blocked[head]
            mt, bt = disp.get(mn or ""), disp.get(bn or "")
            if mn and mn == bn:
                tag = "SAME"
            elif mt and bt:
                tag = "STALE" if mt < bt else "LATER"
            else:
                tag = "UNKNOWN"
            counts[tag] += 1
            print(f"{tag} pr={pr} head={head[:8]} merge={mn}@{mt} blocked={bn}@{bt}")
    print(f"verdict refs={len(refs)} instances={sum(counts.values())} "
          + " ".join(f"{k.lower()}={v}" for k, v in counts.items()))
    return 0


def bodies(dump: str) -> int:
    import roster_edit
    rows = sorted(json.loads(Path(dump).read_text()), key=lambda x: x["mergedAt"])
    hits = []
    for row in rows:
        m = re.search(r"^## Forward-carry\s*$(.*?)(?=^## |\Z)", row["body"] or "",
                      re.M | re.S)
        if not m:
            continue
        bad = [ln for ln in m.group(1).splitlines()
               if "Carry:" in ln and roster_edit.PROPOSAL_RE.search(ln)
               and not roster_edit.RULING_CITE_RE.search(ln)]
        if bad:
            hits.append(row["number"])
    print(f"merged bodies={len(rows)} window={rows[0]['mergedAt']}..{rows[-1]['mergedAt']} "
          f"uncited proposal-sourced carry bodies={len(hits)} {hits}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "stale":
        sys.exit(stale(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] == "bodies":
        sys.exit(bodies(sys.argv[2]))
    sys.exit(__doc__)
