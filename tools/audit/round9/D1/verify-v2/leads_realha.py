"""Shared helper for verifier V2's leads harnesses (imported, never run alone).

Locates an extracted Home Assistant 2026.2.3 wheel and its dependencies, never installed
into the venv. Build it once (any temp root; pass it as LEADS_HA_ROOT):
  R=$(mktemp -d); python3 -m pip download homeassistant==2026.2.3 --no-deps --ignore-requires-python -d $R/wheel
  python3 -c "import zipfile,glob;zipfile.ZipFile(glob.glob('$R/wheel/*.whl')[0]).extractall('$R/ha')"
  then `python3 -m pip install --no-deps --ignore-requires-python --target $R/deps --python-version 3.14
  --implementation cp --abi cp314 --abi abi3 --abi none --platform manylinux_2_28_x86_64
  --platform manylinux2014_x86_64 --only-binary=:all: <each module the import reports missing>`
  (the set used: python-slugify aiozoneinfo ciso8601 atomicwrites-homeassistant ulid-transform
  awesomeversion requests urllib3 certifi async-interrupt jinja2 markupsafe lru-dict
  voluptuous-serialize annotatedyaml==1.0.2 webrtc-models mashumaro typing-extensions PyJWT
  packaging bcrypt cryptography cffi pycparser ifaddr hass-nabucasa boto3 botocore s3transfer
  python-dateutil six jmespath pycognito envs icmplib snitun acme josepy pyOpenSSL pyrfc3339
  sentence-stream regex aiohttp-cors).
Compat shim, stated: CPython 3.14 removed typing.ByteString, which mashumaro (a webrtc_models
dependency pulled in by homeassistant.core) still names at import; it is aliased to bytes before
the import. It touches no code path these harnesses measure (storage, util.dt, update_coordinator).
"""
import os
import subprocess
import sys

VENV_PY = "/home/claude/venv314/bin/python"


def root():
    r = os.environ.get("LEADS_HA_ROOT")
    if not r or not os.path.isdir(os.path.join(r, "ha", "homeassistant")):
        sys.exit("LEADS_HA_ROOT must point at the extracted HA 2026.2.3 root (see leads_realha.py)")
    return r


def run_real(code: str, stdin: str = "") -> str:
    """Run `code` in a subprocess whose `homeassistant` is the real 2026.2.3 package."""
    r = root()
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([os.path.join(r, "ha"), os.path.join(r, "deps")])
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[v] = "1"
    pre = "import typing\ntyping.ByteString = bytes\nimport warnings\nwarnings.filterwarnings('ignore')\n"
    p = subprocess.run([VENV_PY, "-c", pre + code], input=stdin, capture_output=True, text=True,
                       env=env, cwd=os.getcwd(), timeout=600)
    if p.returncode:
        sys.stderr.write(p.stderr[-4000:])
        raise SystemExit(f"real-HA subprocess failed rc={p.returncode}")
    return p.stdout


def real_module_path(rel: str) -> str:
    return os.path.join(root(), "ha", "homeassistant", rel)


def child_cpu():
    ru = __import__("resource").getrusage(__import__("resource").RUSAGE_CHILDREN)
    return ru.ru_utime + ru.ru_stime
