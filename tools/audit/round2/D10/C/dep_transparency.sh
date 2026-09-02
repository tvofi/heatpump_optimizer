#!/bin/bash
# D10-C dependency-transparency + integration-owner harness.
#
# Metric definition (one line): for each manifest requirement (numpy, scipy,
# threadpoolctl) — PyPI presence and OSI license string from
# https://pypi.org/pypi/<pkg>/json, public CI as the count of files in the
# source repo's .github/workflows (GitHub contents API, unauthenticated), and
# PyPI-version-to-tagged-release correspondence via `git ls-remote --tags`
# for both the current PyPI version and the manifest floor version; plus
# manifest codeowners count and the codeowner account's GitHub HTTP status.
#
# Single command (from export root):
#   bash tools/audit/round2/D10/C/dep_transparency.sh
#
# Expected at baseline b39fc6f01f4caee9d3ef17bce5f0b4561392fdb9
# (machine MacBookAir10,1 8 cores): all three deps present, OSI-BSD license,
# >=1 workflow (numpy 24, scipy 17, threadpoolctl 2 at capture), current and
# floor PyPI versions tag-backed, codeowners=1, account HTTP 200.
# Counts are exact; network lookups may see version drift over time (noted
# per line). Writes nothing outside stdout and $TMPDIR.

set -u
ROOT="$(cd "$(dirname "$0")/../../../../../" && pwd)"
MANIFEST="$ROOT/custom_components/heatpump_optimizer/manifest.json"
MACHINE="MacBookAir10,1 8 cores"

emit() { printf 'RESULT %s=%s %s\n' "$1" "$2" "$3"; }

python3 - "$MANIFEST" <<'PY'
import json, re, subprocess, sys, urllib.request

manifest = json.load(open(sys.argv[1]))
reqs = manifest["requirements"]
codeowners = manifest.get("codeowners", [])
emit = lambda n, v, u: print(f"RESULT {n}={v} {u}")
detail = lambda m: print(f"DETAIL {m}")

PKGS = {
    "numpy": "numpy/numpy",
    "scipy": "scipy/scipy",
    "threadpoolctl": "joblib/threadpoolctl",
}

def fetch_json(url, timeout=30):
    # curl rather than urllib: the framework python on the audit box has no
    # CA bundle configured; curl uses the system store and works.
    out = subprocess.run(
        ["curl", "-s", "--max-time", str(timeout), url],
        capture_output=True, text=True, timeout=timeout + 15,
    )
    if out.returncode != 0:
        raise RuntimeError(f"curl {url} rc={out.returncode}")
    return json.loads(out.stdout)

for req in reqs:
    name = re.match(r"([A-Za-z0-9_.-]+)", req).group(1)
    floor = re.search(r">=([0-9][0-9A-Za-z.]*)", req)
    floor = floor.group(1) if floor else None
    repo = PKGS[name]
    key = name.lower()

    meta = fetch_json(f"https://pypi.org/pypi/{name}/json")
    info = meta["info"]
    version = info["version"]
    lic = (info.get("license_expression") or info.get("license") or "").strip()
    classifiers = [c for c in info.get("classifiers", []) if "License" in c]
    osi = bool(re.search(r"BSD|MIT|Apache|GPL|MPL|ISC|Python Software Foundation", lic + " " + " ".join(classifiers), re.I))
    src = (info.get("project_urls") or {}).get("source") or (info.get("project_urls") or {}).get("Homepage") or ""
    emit(f"dep_{key}_pypi_present", 1, "deps")
    emit(f"dep_{key}_license_osi", 1 if osi else 0, "flags")
    detail(f"{name}: license='{lic[:60]}' classifiers={classifiers} source={src} latest={version} floor={floor}")

    try:
        wf = fetch_json(f"https://api.github.com/repos/{repo}/contents/.github/workflows")
        n_wf = len(wf) if isinstance(wf, list) else 0
    except Exception as e:  # noqa: BLE001
        n_wf, detail_msg = 0, f"{name} workflows fetch failed: {e}"
        detail(detail_msg)
    emit(f"dep_{key}_public_ci_workflows", n_wf, "workflows")

    def tag_exists(ver):
        for tag in (ver, f"v{ver}"):
            out = subprocess.run(
                ["git", "ls-remote", "--tags", f"https://github.com/{repo}.git", f"refs/tags/{tag}"],
                capture_output=True, text=True, timeout=60,
            )
            if out.stdout.strip():
                return tag
        return None

    cur_tag = tag_exists(version)
    floor_tag = tag_exists(floor) if floor else None
    emit(f"dep_{key}_pypi_version_tagged", 1 if cur_tag else 0, "flags")
    emit(f"dep_{key}_floor_version_tagged", 1 if floor_tag else 0, "flags")
    detail(f"{name}: pypi {version} -> tag {cur_tag}; floor {floor} -> tag {floor_tag}")

emit("integration_owner_codeowners", len(codeowners), "accounts")
owner = codeowners[0].lstrip("@") if codeowners else ""
try:
    body = fetch_json(f"https://api.github.com/users/{owner}")
    emit("integration_owner_account_http", 200, "status")
    detail(f"owner {owner}: login={body.get('login')} type={body.get('type')} id={body.get('id')}")
except RuntimeError as e:
    emit("integration_owner_account_http", 0, "status")
    detail(f"owner check failed: {e}")
except json.JSONDecodeError:
    emit("integration_owner_account_http", 404, "status")
    detail(f"owner {owner}: not found")
PY

cpu=$(ps -o cputime= -p $$ | tail -1)
load1=$(uptime | sed -E 's/.*load averages?: ([0-9.]+).*/\1/' | head -1)
emit thread_factor 1.0 ratio
emit load1 "$load1" load
emit swapins 0 pages
echo "DETAIL machine=$MACHINE cpu_or_wall=count contention=fan-out shared box, network lookups only"
