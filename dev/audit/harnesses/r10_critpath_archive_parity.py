#!/usr/bin/env python3
"""R10-FLOW-TOOLKIT-MEASURE: ci_critpath.py against the CI design archive's own V1 numbers.

    python3 dev/audit/harnesses/r10_critpath_archive_parity.py

The brief asks the critical-path instrument to reuse the method behind the
archive's phase-2 measurement (tag archive/probe/design-ci-rev4, measure/p2)
rather than write a second one. This holds it to that: the archive's
c1_counterfactual.py and ci_critpath.py run over the archive's recorded jobs
(measure/p2/raw), and every run's V1 "drop C1" gain must agree to the second.
ci_critpath reads each run's needs from its head's tests.yml, so the heads
must be in the local clone (`git fetch --unshallow`); the API is never read
(`--max-reads 0`).

NULL CONTROL. The same comparison with V1's 239.1 s charge left out must
disagree on at least one run (on every run where closures stays on the
counterfactual's path; the others end on a job the charge cannot reach): a
comparison that cannot fail would print parity either way. Then
workflow_needs (ci_critpath's line reader of `jobs:`) is compared with
PyYAML on every workflow under .github/workflows and each archived head's
tests.yml, and a reader whose field rule no longer reads `needs:` must
disagree on at least one file.

Prints `PARITY <agree>/<runs>`, `NULL <disagree>/<runs>` and `NEEDS <files>
files, <differ> differ; mutant differs on <n>`; exit 1 unless every run
agrees, the null disagrees on one or more, and the needs reader agrees
with its mutant caught.
"""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
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
TAG = "archive/probe/design-ci-rev4"
sys.path.insert(0, str(ROOT / "tools/audit/seat"))
import ci_critpath  # noqa: E402

V1 = ["--drop-edge", "coverage:closures", "--delete-job", "composed-proof"]


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout


def gains(text: str) -> dict[str, int]:
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"run (\d+):", line)
        cur = m[1] if m else cur
        g = re.search(r"gain (-?\d+) s;", line)
        if g:
            out[cur] = int(g[1])
    return out


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        tar = subprocess.run(["git", "-C", str(ROOT), "archive", TAG, "measure/p2"], capture_output=True, check=True)
        tarfile.open(fileobj=io.BytesIO(tar.stdout)).extractall(d, filter="data")
        raw, cache = Path(d) / "measure/p2/raw", Path(d) / "cache"
        cache.mkdir()
        arch = subprocess.run([sys.executable, "-I", str(Path(d) / "measure/p2/c1_counterfactual.py"), str(raw)],
                              capture_output=True, text=True, check=True).stdout
        want = {m[1]: int(m[2]) for m in re.finditer(r"^(\d{11})\s+\d+\s+(-?\d+)", arch, re.M)}
        heads = []
        for r in json.loads((raw / "tests_runs_pull_request.json").read_text())["workflow_runs"]:
            if str(r["id"]) in want:
                (cache / f"run_{r['id']}.json").write_text(json.dumps(r))
                jobs = json.loads((raw / f"tests_jobs_{r['id']}.json").read_text())["jobs"]
                (cache / f"jobs_{r['id']}.json").write_text(json.dumps(jobs))
                heads.append(r["head_sha"])

        def run(*extra: str) -> dict[str, int]:
            buf = io.StringIO()
            from contextlib import redirect_stdout
            with redirect_stdout(buf):
                ci_critpath.main(["--repo", "o/r", "--cache", str(cache), "--max-reads", "0",
                                  *(x for i in want for x in ("--run", i)), *V1, *extra])
            return gains(buf.getvalue())

        got, null = run("--charge", "closures=239.1"), run()
        agree = sum(got.get(k) == v for k, v in want.items())
        differ = sum(null.get(k) != v for k, v in want.items())
        print(f"PARITY {agree}/{len(want)}")
        print(f"NULL {differ}/{len(want)}")
        texts = [p.read_text() for p in sorted((ROOT / ".github/workflows").glob("*.yml"))]
        texts += [git("show", f"{h}:.github/workflows/tests.yml") for h in sorted(set(heads))]
        try:
            import yaml
        except ImportError:
            print("NEEDS not compared: no PyYAML here")
            return 1
        def ref(t: str) -> dict:
            out = {}
            for k, v in ((yaml.safe_load(t) or {}).get("jobs") or {}).items():
                n, nm = v.get("needs") or [], v.get("name")
                if isinstance(nm, str) and nm.endswith(")") and " (${{" in nm:
                    nm = nm.split(" (${{")[0]
                elif not isinstance(nm, str) or "${{" in nm:
                    nm = None
                out[k] = dict(name=nm, needs=[n] if isinstance(n, str) else list(n))
            return out
        bad = sum(ci_critpath.workflow_needs(t) != ref(t) for t in texts)
        keep = ci_critpath.FIELD_RE
        ci_critpath.FIELD_RE = re.compile(r"^    (name):\s*(.*?)\s*(?:#.*)?$")
        caught = sum(ci_critpath.workflow_needs(t) != ref(t) for t in texts)
        ci_critpath.FIELD_RE = keep
        print(f"NEEDS {len(texts)} files, {bad} differ; mutant differs on {caught}")
        ok = agree == len(want) > 0 and differ > 0 and bad == 0 and caught > 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
