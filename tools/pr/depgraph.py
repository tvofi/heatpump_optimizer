#!/usr/bin/env python3
"""Keep GitHub's dependency graph equal to the tree's pins, and say when it is not.

    python3 -I tools/pr/depgraph.py snapshot --sha SHA --ref REF --job-id ID > SNAPSHOT.json
    python3 -I tools/pr/depgraph.py check --sbom SBOM.json [--alerts ALERTS.json]
    python3 -I tools/pr/depgraph.py check --repo OWNER/NAME [--no-alerts]
    python3 -I tools/pr/depgraph.py --self-test

WHY (r10-fly-depgraph-stale, 2026-10-25). The graph for the hash-locked pip
manifests under tests/ is not parsed from the files: it is the snapshot the
`Dependency Graph` dynamic workflow (a Dependabot graph job, correlator
`dependabot-pip-tests`) submits. That job ran for every manifest-touching merge
to main up to 2622b31c (2026-10-03) and for none after, though the same
account pushed the same kind of merge of the same file format; an unrelated
repository reports the same last run date on dependabot/dependabot-core#16044.
The graph kept aiohttp 3.14.3 and pillow 12.3.0 while main pinned the patched
versions, and Dependabot raised alerts from it. The scheduler is GitHub's, so
the tree submits its own snapshot instead:
.github/workflows/dependency-graph.yml runs `snapshot` on every push to main
that changes a pip manifest and POSTs it. A user submission outranks a
Dependabot graph job for the same manifest (the dependency-submission docs'
precedence), so the stale snapshot stops counting.

`snapshot` prints a Dependency Submission API body: one manifest per
tests/requirements-*.txt, named as the Dependabot job named it, every pin a
direct runtime dependency (each file is a full lock, transitive closure
included). A requirement that is not `name==version` refuses: a range has no
single version to submit.

`check` compares one SBOM (GET dependency-graph/sbom) with the tree, per
ecosystem the SBOM reports: pypi against the pip locks, npm against every
tracked package-lock.json, githubactions against every `uses:` under .github/.
Any difference is STALE (exit 1), named package by package. The census asserts
its own precondition: an SBOM ecosystem it does not enumerate refuses (exit 2)
instead of passing unread. With alerts (GET dependabot/alerts?state=open), an
open pip or npm alert whose package the tree pins at or above the alert's
first patched version is also STALE: the graph, not the tree, holds it open.
An alert whose versions this reader cannot order refuses. `--repo` makes the
two reads itself through `gh api`, one each; an alerts read that fails is
printed as unread, never as clean -- a workflow's GITHUB_TOKEN cannot read
Dependabot alerts, so CI runs `--no-alerts` and the SBOM arm alone.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIP_GLOB = "tests/requirements-*.txt"
DETECTOR = {"name": "hpo-depgraph", "version": "1",
            "url": "https://github.com/tvofi/heatpump_optimizer/blob/main/tools/pr/depgraph.py"}
CORRELATOR = "hpo-depgraph-pip-tests"
REQ_RE = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?==(?P<ver>[^\s;\\]+)")
USES_RE = re.compile(r"^\s*(?:-\s+)?uses:\s*['\"]?(?P<ref>[^'\"\s#]+)")
RELEASE_RE = re.compile(r"^\d+(?:\.\d+)*$")
IGNORED_PURL_TYPES = {"github"}  # the repository's own root package


def norm_pypi(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def pip_pins(root: Path) -> dict[str, dict[str, str]]:
    """{manifest path: {normalized name: version}} for every pip lock."""
    out: dict[str, dict[str, str]] = {}
    for f in sorted(root.glob(PIP_GLOB)):
        rel = f.relative_to(root).as_posix()
        pins: dict[str, str] = {}
        logical = re.sub(r"\\\n", " ", f.read_text())
        for line in logical.splitlines():
            line = re.sub(r"(?:^|\s)#.*$", "", line).strip()
            if not line:
                continue
            m = REQ_RE.match(line)
            if not m:
                raise ValueError(f"{rel}: {line.split()[0]!r} is not name==version; a range has no version to submit")
            pins[norm_pypi(m["name"])] = m["ver"]
        out[rel] = pins
    if not out:
        raise ValueError(f"no file matches {PIP_GLOB}")
    return out


def npm_pins(root: Path) -> set[tuple[str, str]]:
    out = set()
    for f in sorted(root.glob("**/package-lock.json")):
        if "node_modules" in f.parts:
            continue
        for key, pkg in json.loads(f.read_text()).get("packages", {}).items():
            if key and "version" in pkg and not pkg.get("link"):
                out.add((key.rsplit("node_modules/", 1)[-1], pkg["version"]))
    return out


def action_pins(root: Path) -> set[tuple[str, str]]:
    out = set()
    for f in sorted((root / ".github").rglob("*.y*ml")):
        for line in f.read_text().splitlines():
            m = USES_RE.match(line)
            if m and "@" in m["ref"] and not m["ref"].startswith(("./", "docker://")):
                name, ver = m["ref"].rsplit("@", 1)
                out.add((name, ver))
    return out


def tree_pins(root: Path) -> dict[str, set[tuple[str, str]]]:
    pip = {(n, v) for pins in pip_pins(root).values() for n, v in pins.items()}
    return {"pypi": pip, "npm": npm_pins(root), "githubactions": action_pins(root)}


def snapshot(root: Path, sha: str, ref: str, job_id: str) -> dict:
    manifests = {}
    for rel, pins in pip_pins(root).items():
        resolved = {}
        for name, ver in sorted(pins.items()):
            purl = f"pkg:pypi/{name}@{ver}"
            resolved[purl] = {"package_url": purl, "relationship": "direct", "scope": "runtime"}
        manifests["/" + rel] = {"name": "/" + rel, "file": {"source_location": rel}, "resolved": resolved}
    return {"version": 0, "sha": sha, "ref": ref,
            "job": {"correlator": CORRELATOR, "id": str(job_id)},
            "detector": DETECTOR,
            "scanned": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "manifests": manifests}


def sbom_pins(sbom: dict) -> dict[str, set[tuple[str, str]]]:
    """{purl type: {(name, version)}} over the SBOM's packages; refuses an unenumerated type."""
    out: dict[str, set[tuple[str, str]]] = {"pypi": set(), "npm": set(), "githubactions": set()}
    for pkg in sbom.get("sbom", sbom).get("packages", []):
        for ref in pkg.get("externalRefs", []):
            if ref.get("referenceType") != "purl":
                continue
            loc = ref["referenceLocator"]
            kind, _, rest = loc.partition(":")[2].partition("/")
            if kind in IGNORED_PURL_TYPES:
                continue
            if kind not in out:
                raise ValueError(f"the SBOM reports ecosystem {kind!r} ({loc}), which this census does not enumerate")
            name, _, ver = urllib.parse.unquote(rest).rpartition("@")
            out[kind].add((norm_pypi(name) if kind == "pypi" else name, ver))
    return out


def release(v: str) -> tuple[int, ...] | None:
    return tuple(int(x) for x in v.split(".")) if RELEASE_RE.match(v) else None


ALERT_ECOSYSTEM = {"pip": "pypi", "npm": "npm"}


def stale_alerts(alerts: list, tree: dict[str, set[tuple[str, str]]]) -> tuple[list[str], list[str]]:
    """(open alerts the tree already fixes, alerts this reader cannot judge)."""
    fixed, unjudged = [], []
    for a in alerts:
        if a.get("state") != "open":
            continue
        pkg = a["dependency"]["package"]
        kind = ALERT_ECOSYSTEM.get(pkg["ecosystem"])
        patched = (a["security_vulnerability"].get("first_patched_version") or {}).get("identifier")
        tag = f"#{a['number']} {pkg['ecosystem']}:{pkg['name']} (patched {patched}, {a['dependency'].get('manifest_path')})"
        if kind is None or patched is None:
            unjudged.append(tag + ": no ecosystem or patched version to compare")
            continue
        name = norm_pypi(pkg["name"]) if kind == "pypi" else pkg["name"]
        pinned = [v for n, v in tree[kind] if n == name]
        orders = [release(v) for v in pinned] + [release(patched)]
        if not pinned or None in orders:
            unjudged.append(tag + f": pinned {pinned or 'nowhere'}")
        elif all(release(v) >= release(patched) for v in pinned):
            fixed.append(tag + f": the tree pins {', '.join(sorted(pinned))}")
    return fixed, unjudged


def check(sbom: dict, alerts: list | None, root: Path) -> tuple[int, list[str]]:
    """(exit code, report lines): 0 equal, 1 STALE, 2 refused."""
    lines: list[str] = []
    try:
        graph = sbom_pins(sbom)
        tree = tree_pins(root)
    except ValueError as e:
        return 2, [f"REFUSED: {e}"]
    stale = False
    for kind in sorted(tree):
        missing, extra = tree[kind] - graph[kind], graph[kind] - tree[kind]
        stale |= bool(missing or extra)
        lines.append(f"{kind}: {len(tree[kind])} pinned, {len(graph[kind])} in the graph, "
                     f"{len(missing)} missing, {len(extra)} stale")
        lines += [f"  missing from the graph: {n}@{v}" for n, v in sorted(missing)]
        lines += [f"  in the graph, not the tree: {n}@{v}" for n, v in sorted(extra)]
    code = 1 if stale else 0
    if alerts is None:
        lines.append("alerts: unread")
    else:
        fixed, unjudged = stale_alerts(alerts, tree)
        lines.append(f"alerts: {sum(a.get('state') == 'open' for a in alerts)} open, "
                     f"{len(fixed)} fixed in the tree, {len(unjudged)} unjudged")
        lines += [f"  open, fixed in the tree: {x}" for x in fixed]
        lines += [f"  unjudged: {x}" for x in unjudged]
        if fixed:
            code = 1
        elif unjudged and code == 0:
            code = 2
    lines.append({0: "OK: the graph equals the tree", 1: "STALE: the graph differs from the tree",
                  2: "REFUSED: an alert this reader cannot judge"}[code])
    return code, lines


def gh_json(path: str) -> object:
    out = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github+json", path],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"gh api {path} exited {out.returncode}")
    return json.loads(out.stdout)


def self_test() -> int:
    bad: list[str] = []
    n = 0

    def ok(name, got, want):
        nonlocal n
        n += 1
        print(f"  {'ok  ' if got == want else 'FAIL'}  {name}" + ("" if got == want else f": {got!r} != {want!r}"))
        if got != want:
            bad.append(name)

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "tests").mkdir()
        (r / "tests/requirements-ci.txt").write_text(
            "# header\n\naiohttp==3.14.5 \\\n    --hash=sha256:aa \\\n    --hash=sha256:bb\n"
            "Pillow==13.0.0 \\\n    --hash=sha256:cc\nuv==0.13.4 ; python_version >= '3.13' \\\n    --hash=sha256:dd\n")
        (r / "tests/requirements-build.txt").write_text("certifi==2026.10.19 \\\n    --hash=sha256:ee\n")
        (r / "site").mkdir()
        (r / "site/package-lock.json").write_text(json.dumps({"packages": {
            "": {"name": "site"}, "node_modules/@scope/x": {"version": "1.2.3"},
            "node_modules/a/node_modules/b": {"version": "0.1.0"}}}))
        (r / ".github/workflows").mkdir(parents=True)
        (r / ".github/workflows/w.yml").write_text(
            "jobs:\n  j:\n    steps:\n      - uses: actions/checkout@abc # v5\n"
            "      - uses: ./.github/actions/local\n    uses: ./.github/workflows/x.yml\n")

        ok("pins: a hash-locked line, its name normalized", pip_pins(r)["tests/requirements-ci.txt"],
           {"aiohttp": "3.14.5", "pillow": "13.0.0", "uv": "0.13.4"})
        ok("npm: scoped and nested lock entries, root skipped", npm_pins(r), {("@scope/x", "1.2.3"), ("b", "0.1.0")})
        ok("actions: a pinned ref, local uses skipped", action_pins(r), {("actions/checkout", "abc")})

        def purl(p):
            return {"name": p, "externalRefs": [{"referenceType": "purl", "referenceLocator": p}]}

        good = ["pkg:pypi/aiohttp@3.14.5", "pkg:pypi/Pillow@13.0.0", "pkg:pypi/uv@0.13.4",
                "pkg:pypi/certifi@2026.10.19", "pkg:npm/%40scope/x@1.2.3", "pkg:npm/b@0.1.0",
                "pkg:githubactions/actions/checkout@abc", "pkg:github/o/r@main"]
        sb = lambda ps: {"sbom": {"packages": [purl(p) for p in ps]}}
        ok("null control: an SBOM equal to the pins is OK", check(sb(good), None, r)[0], 0)
        old = [p.replace("aiohttp@3.14.5", "aiohttp@3.14.3") for p in good]
        code, lines = check(sb(old), None, r)
        ok("a stale version is STALE", code, 1)
        ok("  and names both sides", sum("aiohttp@3.14" in x for x in lines), 2)
        ok("a pin missing from the graph is STALE", check(sb(good[1:]), None, r)[0], 1)
        ok("a graph package the tree dropped is STALE", check(sb(good + ["pkg:npm/gone@1.0.0"]), None, r)[0], 1)
        ok("an unenumerated ecosystem refuses", check(sb(good + ["pkg:cargo/x@1"]), None, r)[0], 2)

        def alert(num, eco, name, patched, state="open"):
            return {"number": num, "state": state,
                    "dependency": {"package": {"ecosystem": eco, "name": name}, "manifest_path": "tests/requirements-ci.txt"},
                    "security_vulnerability": {"first_patched_version": {"identifier": patched}}}

        ok("alerts: none open is OK", check(sb(good), [alert(1, "pip", "aiohttp", "3.14.4", "fixed")], r)[0], 0)
        ok("alerts: an open alert the tree pins past is STALE",
           check(sb(good), [alert(2, "pip", "aiohttp", "3.14.4")], r)[0], 1)
        ok("alerts: patched == pinned counts as fixed", check(sb(good), [alert(3, "pip", "pillow", "13.0.0")], r)[0], 1)
        ok("alerts: a real open alert (pinned below patched) is not staleness",
           check(sb(good), [alert(4, "pip", "aiohttp", "3.15.0")], r)[0], 0)
        ok("alerts: 2026.10.19 orders above 2026.7.22, not as text",
           check(sb(good), [alert(5, "pip", "certifi", "2026.7.22")], r)[0], 1)
        ok("alerts: an unorderable version refuses", check(sb(good), [alert(6, "pip", "uv", "0.13.4rc1")], r)[0], 2)
        ok("alerts: a package pinned nowhere refuses", check(sb(good), [alert(7, "pip", "nope", "1.0")], r)[0], 2)

        snap = snapshot(r, "f" * 40, "refs/heads/main", "7")
        ok("snapshot: one manifest per lock, named as Dependabot named it",
           sorted(snap["manifests"]), ["/tests/requirements-build.txt", "/tests/requirements-ci.txt"])
        ok("snapshot: every pin a direct purl", sorted(snap["manifests"]["/tests/requirements-ci.txt"]["resolved"]),
           ["pkg:pypi/aiohttp@3.14.5", "pkg:pypi/pillow@13.0.0", "pkg:pypi/uv@0.13.4"])
        ok("snapshot: the required fields", sorted(snap), ["detector", "job", "manifests", "ref", "scanned", "sha", "version"])

        (r / "tests/requirements-x.txt").write_text("numpy>=2\n")
        try:
            pip_pins(r)
            ok("a range refuses", "accepted", "refused")
        except ValueError:
            ok("a range refuses", "refused", "refused")

    real = pip_pins(ROOT)
    ok("the tree's pip locks parse, every one non-empty", all(real.values()) and bool(real), True)
    ok("the tree's npm locks and actions parse", bool(npm_pins(ROOT)) and bool(action_pins(ROOT)), True)
    print(f"depgraph self-test: {n} checks, {len(bad)} failed")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    flags = {a for a in argv if a == "--no-alerts"}
    rest = [a for a in argv[1:] if a not in flags]
    args = dict(zip(rest[::2], rest[1::2]))
    if len(rest) % 2:
        args = {}
    if argv[:1] == ["snapshot"] and set(args) == {"--sha", "--ref", "--job-id"}:
        print(json.dumps(snapshot(ROOT, args["--sha"], args["--ref"], args["--job-id"]), indent=1))
        return 0
    if argv[:1] == ["check"] and set(args) in ({"--sbom"}, {"--sbom", "--alerts"}) and not flags:
        sbom = json.loads(Path(args["--sbom"]).read_text())
        alerts = json.loads(Path(args["--alerts"]).read_text()) if "--alerts" in args else None
    elif argv[:1] == ["check"] and set(args) == {"--repo"}:
        repo = args["--repo"]
        sbom = gh_json(f"repos/{repo}/dependency-graph/sbom")
        alerts = None
        if not flags:
            try:
                alerts = gh_json(f"repos/{repo}/dependabot/alerts?state=open&per_page=100")
            except RuntimeError as e:
                print(f"alerts read failed: {e}")
            if alerts is not None and len(alerts) == 100:
                print("alerts: a full page of 100; this one read may not hold every open alert")
    else:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    code, lines = check(sbom, alerts, ROOT)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
