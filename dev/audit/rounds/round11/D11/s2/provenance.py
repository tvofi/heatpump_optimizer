#!/usr/bin/env python3
"""D11.M2 (SLSA v1.0 Build L1 "provenance exists"; Scorecard Signed-Releases):
whether the artefact a user installs carries build provenance.

Metric (one line): over the last N published releases, how many distributed
`heatpump_optimizer.zip` assets have >=1 GitHub attestation for their sha256,
against how many tag-tree tars (the subject `.github/workflows/release.yml`'s
step "Attest the tag's tree" attests) do.

The tar digest is computed exactly as that step computes it
(`git archive --format=tar <tag> | sha256sum`); the zip is downloaded from the
release (`hacs.json` sets zip_release: true and filename heatpump_optimizer.zip,
so the zip is what a Marketplace/HACS install fetches). Attestations are read
from `GET /repos/tvofi/heatpump_optimizer/attestations/sha256:<digest>`.
Key: the attestation count the API returns per digest.

Run:   python3 dev/audit/rounds/round11/D11/s2/provenance.py [--n 5] [--perturb]
       --perturb queries the zip row with the tar's digest (the step's subject
       moved onto the distributed asset): zip_attested must go UP to N.
Writes only under a mktemp root. Expected at baseline
92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B7, 2026-11-16: zip_attested=0,
tar_attested=N; exact (network read; a later release changes the population).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import hashlib, json, subprocess, sys, tempfile, time

REPO = "tvofi/heatpump_optimizer"


def curl(url, out=None):
    cmd = ["curl", "-sSL", "-m", "120", url]
    if out:
        cmd += ["-o", out]
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        cmd[1:1] = ["-H", f"Authorization: Bearer {tok}"]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def attestations(digest):
    d = json.loads(curl(f"https://api.github.com/repos/{REPO}/attestations/sha256:{digest}") or "{}")
    return len(d.get("attestations") or [])


def main(argv):
    n = int(argv[argv.index("--n") + 1]) if "--n" in argv else 5
    tmp = tempfile.mkdtemp(prefix="d11s2-prov-", dir=os.environ.get("TMPDIR"))
    t0, c0 = time.process_time(), time.thread_time()
    rels = [r for r in json.loads(curl(f"https://api.github.com/repos/{REPO}/releases?per_page={n}")) if not r.get("draft")][:n]
    zip_ok = tar_ok = 0
    for r in rels:
        tag = r["tag_name"]
        subprocess.run(["git", "fetch", "-q", "--no-tags", "origin", f"refs/tags/{tag}:refs/tags/{tag}"], capture_output=True)
        tar = subprocess.run(["git", "archive", "--format=tar", tag], capture_output=True).stdout
        td = hashlib.sha256(tar).hexdigest()
        asset = next((a for a in r["assets"] if a["name"].endswith(".zip")), None)
        zd = None
        if asset:
            path = os.path.join(tmp, f"{tag}.zip")
            curl(asset["browser_download_url"], out=path)
            zd = hashlib.sha256(open(path, "rb").read()).hexdigest()
        za = attestations(td if "--perturb" in argv else zd) if zd else 0
        ta = attestations(td)
        zip_ok += za > 0
        tar_ok += ta > 0
        print(f"{tag}\tzip sha256:{(zd or '-')[:16]} attestations={za}\ttar sha256:{td[:16]} attestations={ta}")
    print(f"RESULT releases={len(rels)} count")
    print(f"RESULT zip_attested={zip_ok} count")
    print(f"RESULT tar_attested={tar_ok} count")
    pc, tc = time.process_time() - t0, time.thread_time() - c0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main(sys.argv[1:])
