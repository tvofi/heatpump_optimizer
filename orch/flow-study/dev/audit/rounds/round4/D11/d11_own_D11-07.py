#!/usr/bin/env python3
"""VERIFIER-OWN harness for D11-07 (round 4, verifier seat 1).

METRIC (my own definition):
  recent_releases        -- the 10 most recent LIVE releases (not 5), with
                            asset counts and whether any asset name matches a
                            provenance/signature pattern
                            (*.intoto.jsonl, *.sig, *.asc, *. attest).
  releases_with_assets   -- how many of those carry >=1 asset.
  provenance_mentions    -- occurrences of attest-build-provenance /
                            cosign / slsa in .github/workflows/** (static).
  uses_total / uses_pinned -- distinct `uses:` actions across workflows, and
                            how many are pinned by a 40-hex SHA (static,
                            my own regex over the raw YAML).

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/d11_own_D11-07.py

EXPECTED (tolerance: exact at head 0855277 + live releases):
  recent_releases=10 releases_with_assets=0 uses_pinned=2 uses_total=9
MACHINE: verifier seat 1 worktree audit-r4-verify-D11-1, 2026-09-12.

PERTURBATION. Add `uses: hacs/action@0000...` (40-hex) to a scratch YAML and
re-run the classifier: uses_pinned must rise by one.
"""

import json
import os
import re
import subprocess

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()
REPO = "tvofi/heatpump_optimizer"
PIN = re.compile(r"@[0-9a-f]{40}$")
PROV = re.compile(r"attest-build-provenance|cosign|slsa", re.I)


def classify_uses(texts):
    # `^\s*-?\s*uses:` -- a step's uses lives on a `- uses:` list line; a
    # first-draft `^\s*uses:` missed those (setup-node/setup-python) and the
    # scratch perturbation alike. Instrument defect, fixed in place.
    uses = sorted(set(m.group(1).strip()
                      for t in texts.values()
                      for m in re.finditer(r"^\s*-?\s*uses:\s*(\S+)", t, re.M)))
    pinned = [u for u in uses if PIN.search(u)]
    return uses, pinned


def main():
    p = subprocess.run(["gh", "api", f"repos/{REPO}/releases?per_page=10"],
                       capture_output=True, text=True)
    rels = json.loads(p.stdout)
    with_assets = 0
    print("recent live releases:")
    for r in rels:
        assets = [a["name"] for a in r.get("assets", [])]
        prov = [a for a in assets if PROV.search(a) or a.endswith((".sig", ".asc", ".intoto.jsonl"))]
        if assets:
            with_assets += 1
        print(f"  {r['tag_name']}: assets={assets or 'NONE'} provenance_like={prov or 'none'}")

    wf = os.path.join(ROOT, ".github/workflows")
    texts = {f: open(os.path.join(wf, f), encoding="utf-8").read()
             for f in sorted(os.listdir(wf)) if f.endswith((".yml", ".yaml"))}
    uses, pinned = classify_uses(texts)
    prov_mentions = [(f, i) for f, t in texts.items()
                     for i, line in enumerate(t.split("\n"), 1) if PROV.search(line)]
    print(f"\ndistinct uses: {len(uses)}; pinned by 40-hex SHA: {len(pinned)}")
    for u in uses:
        print(f"  {'PINNED ' if PIN.search(u) else 'mutable'} {u}")
    print(f"provenance mentions in workflows: {prov_mentions or 'none'}")

    # perturbation on scratch YAML
    scratch = "/tmp/d11-own-07-scratch.yml"
    open(scratch, "w").write("jobs:\n  x:\n    steps:\n      - uses: nosuch/action@" + "0" * 40 + "\n")
    t2 = dict(texts)
    t2["scratch.yml"] = open(scratch).read()
    _, p2 = classify_uses(t2)
    print(f"perturbation: uses_pinned {len(pinned)} -> {len(p2)}")

    print()
    print(f"RESULT recent_releases={len(rels)}")
    print(f"RESULT releases_with_assets={with_assets}")
    print(f"RESULT uses_total={len(uses)}")
    print(f"RESULT uses_pinned={len(pinned)}")
    print(f"RESULT uses_mutable={len(uses) - len(pinned)}")
    print(f"RESULT provenance_steps={len(prov_mentions)}")
    print(f"RESULT perturbation_pinned_delta={len(p2) - len(pinned)}")


if __name__ == "__main__":
    main()
