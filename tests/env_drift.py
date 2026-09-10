"""The drift gate for golden fixtures whose floats do not travel.

`valve_storage_smart_write`, `wood_two_tank`, `wood_two_tank_smart_write`,
`wood_coil` and `valve_upper_direct_slab` do not reproduce across
scipy/numpy builds — and not at the last decimal: these are the non-convex
valve/wood solves, and a different BLAS lands them in a different local
optimum (plan-shape flips, different compressor-start counts). On such a
machine `tests/golden.py` reports them as DIFF on a clean checkout of main,
which makes "fails, as expected" worthless as a review signal: a real
regression in exactly these scenarios would hide behind the label.

This script restores the signal. It captures scenarios twice in the SAME
environment — once from this working tree, once from a pristine worktree
of a reference commit (default `origin/main`) — and requires the two
computed payload sets to be byte-identical. Solver noise cancels because
both runs share the solver; anything left is this branch's doing.

    PYTHONPATH=tests/hastub python3 tests/env_drift.py [ref]          # 5 sensitive fixtures
    PYTHONPATH=tests/hastub python3 tests/env_drift.py --all [ref]    # every fixture (CI)
    PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only [ref]  # inherited + record-PR, no capture
    PYTHONPATH=tests/hastub python3 tests/env_drift.py --drop-inherited [ref]  # CI claims-autofix; empties inherited lists

`--all` is what CI runs: committed fixtures were recorded on one machine
and CI runs on another, so exact comparison against the files would cry
wolf; comparing two captures made by the same runner is environment-proof
by construction.

The baseline half of that pair is the slowest step in the whole suite and
is identical for every branch forked from the same commit, so it is cached
between runs under a key covering the baseline commit and tree, this file's
own SHA-256, the capture mode, the interpreter, the installed distribution
inventory, numpy's build configuration, a bit-exact fingerprint of this
machine's floating-point arithmetic, and the environment variables the
capture path reads. A hit prints a banner naming the key and the entry it
came from, so gate output always says when a baseline was reused rather
than recomputed. `DRIFT_NO_CACHE=1` turns the cache off; `DRIFT_CACHE_DIR`
moves it (it lives outside the repository, so it is never committed). See
"The baseline cache" below for what the key covers and why.

A branch is allowed to move fixtures — behaviour changes are sometimes
the point — but it must say so: `tests/golden/claimed_drift.txt` lists
one scenario name per line (with a reason after `#`). Listed scenarios
still print their diffs, but do not fail the gate. A claim that matched
nothing is stale and fails too, but it is counted and reported apart
from drift: nothing regressed, the list is simply out of date.

A claim describes exactly ONE diff, and two rules keep it that way:

  * The file carries a machine-read declaration line — `# claims-for:
    <version>` — which must equal the repo-root VERSION file. That is
    checked first, before any capture, in both modes, and it fails the
    run on its own.
  * In `--all` mode the claim list must also differ from the baseline's.
    The stamp only expires claims when the version *changes*, and this
    history is full of consecutive commits that share one: 7b512bc,
    401db6e and 2248f64 all carry 4.0.0, and the ten v4.0.0 T* tranche
    merges all carry 3.16.0 (the release they were building towards is
    in their titles, not in VERSION). Across any of those an inherited
    file carries a matching stamp and sails through. So if this tree
    claims exactly what the baseline
    claims — same names, same reasons — the list was written for the
    baseline's diff rather than this one, and the run fails. An empty
    list is always fine; it is a statement, not an inheritance. The same
    comparison is applied to the card claim file. A three-dot that touches
    neither integration Python nor the bundled card must leave both lists
    empty -- that is the record-PR rule, and `tests/run.sh` always runs
    `--claims-only` so `GATE_SCOPE=auto` cannot skip it the way it skipped
    `card_drift.mjs` on #493.

Staleness is only ever judged against scenarios this run actually
captured. The five-fixture mode captures SENSITIVE and nothing else, so
a claim naming any other scenario is reported as not evaluated there
rather than called stale — judging it is `--all`'s job, which is what
CI runs.

The file is committed, so without those rules it outlives the PR that
wrote it: v4.0.7, v4.2.0 and v4.3.0 each moved no goldens, inherited the
previous release's claims, and failed CI on main with N stale claims for
code that was never wrong (a push to main is compared against HEAD^1 —
the merged PR's own diff). A release that moves nothing still rewrites
the file: bump `claims-for:`, delete every claim, and the empty list is
then a statement about THIS diff instead of an inherited lie.

Scenarios that exist only on this branch (a PR adding coverage) have no
baseline to compare against; they are reported and pass — the golden
invariant layer inside `golden.py` still vets them. Scenarios that exist
only on the baseline (a PR deleting coverage) fail unless claimed.

The comparison ref must not resolve to HEAD. A tree compared against
itself is byte-identical by construction — no drift whatever the branch
did, and every claim stale — so a gate in that state proves nothing and
says so instead of passing.

Exit 0: no unclaimed drift. Exit 1: this branch moved a fixture the
reference does not move in this environment — either a regression, or a
behaviour change the PR must claim; or a claim matched nothing; or the
claim file is stamped for a different release than VERSION, or is the
baseline's list carried forward; or the ref is HEAD itself. Never
re-record the five sensitive fixtures on a machine where golden.py
already reports them as DIFF.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import textwrap
import time

SENSITIVE = (
    "valve_storage_smart_write",
    "wood_two_tank",
    "wood_two_tank_smart_write",
    "wood_coil",
    "valve_upper_direct_slab",
)

CLAIM_FILE = os.path.join("tests", "golden", "claimed_drift.txt")
CARD_CLAIM_FILE = os.path.join("tests", "golden", "card_claimed_drift.txt")
CARD_JS = os.path.join(
    "custom_components", "heatpump_optimizer", "www",
    "heatpump-optimizer-card.js",
)
CLAIM_VERSION_MARKER = "claims-for:"
#: Declares a SENSITIVE fixture whose drift is judged per machine rather than
#: per release. See `_may_drift` for why an ordinary claim cannot do this job.
MAY_DRIFT_MARKER = "may-drift:"
VERSION_FILE = "VERSION"
#: The git merge driver `.gitattributes` routes both claim files to. See
#: `merge_claim_file` for what it resolves and what it refuses.
MERGE_DRIVER_NAME = "claimnotes"
GITATTRIBUTES_FILE = ".gitattributes"

# Payload keys fixed by the forecast and baseline reference, not by which local
# optimum the solver reached. Measured 2026-09-04 (#254): committed vs local
# capture on all five SENSITIVE fixtures plus narrow_band never moves these
# four under machine noise; M01 (thermal_model.dhw_coil_draw_reduction) moves
# baseline_cost 156 -> 678 on wood_coil while they stay put. Every other key
# can move with basin noise alone and stays exempt for may-drift fixtures.
MAY_DRIFT_JUDGED_KEYS = frozenset({
    "baseline_cost",
    "outdoor_temps",
    "price_known",
    "prices",
})

# ===========================================================================
# The baseline cache
# ===========================================================================
#
# Capturing the baseline is the slowest single step in the gate: it is every
# scenario solved from a pristine worktree of the comparison ref, and it is
# byte-identical for every branch that forks from the same commit. So it is
# cached — but a stale hit would make this gate lie, and a gate that lies is
# worse than no gate. The key therefore covers everything a capture's output
# can possibly depend on, and when any of it cannot be determined the cache
# turns itself off rather than guess.
#
# What a baseline capture is a function of, read off the code that runs it:
#
#   * The baseline tree. The worktree is checked out at the resolved commit
#     SHA -- never at the ref name, see main() -- so one commit's tracked
#     content fixes every byte of tests/golden.py, tests/profiles.py,
#     tests/hastub/ and custom_components/. Both the commit and its tree SHA
#     go in the key.
#   * THIS file. `capture_tree` runs from the branch's copy of env_drift.py
#     (main() re-invokes `os.path.abspath(__file__)`), and it is what decides
#     which scenarios are captured and how -- SCENARIOS plus the coordinator
#     scenarios plus config_flow under --all, SENSITIVE without it. A branch
#     that edits the capture path changes the baseline payload without moving
#     the ref, so the file's own SHA-256 is in the key.
#   * The mode, --all or the five sensitive fixtures: different payload sets.
#   * The numeric environment. These are non-convex solves whose local optimum
#     moves with the BLAS build -- the whole reason this script exists. The key
#     carries a `numeric_probe`: a fixed, seeded numpy/scipy workload
#     (linalg.solve, svd, linprog/HiGHS, L-BFGS-B) hashed to the last bit. It
#     is a direct measurement of the floating-point environment rather than a
#     guess at which of its knobs matter, so a swapped BLAS, a rebuilt scipy or
#     a different libm changes it. The interpreter, the platform, the numpy
#     build config and the full installed distribution inventory are in the key
#     too, because a library can change behaviour without changing arithmetic.
#   * The environment variables the capture path actually reads. The only one
#     in the tree is HASTUB_TZ (tests/hastub/homeassistant/util/dt.py), but the
#     key takes the whole family of locale, timezone, BLAS-threading and
#     Python-runtime variables rather than just that one. PYTHONPATH is
#     deliberately excluded: main() overwrites it for the capture subprocess
#     with a path derived from the tree being captured, so the caller's value
#     cannot reach it.
#
# The residual risk, stated plainly: a machine change that alters float
# results but moves none of the above. It cannot pass silently. The BRANCH
# capture is always recomputed, so a baseline captured under a different
# arithmetic no longer cancels against it and the run reports drift -- it
# fails loudly and over-strictly, which is the safe direction. For a stale
# hit to HIDE a regression the environment change would have to move the
# branch's output onto the stale baseline's by exactly the regression's own
# footprint.
#
# DRIFT_NO_CACHE=1 skips the cache entirely, read and write.
#
# How this sits with the may-drift category. Those five fixtures are judged
# on whether they moved BETWEEN the two captures, and a cached baseline
# changes nothing about that: it is the bytes a capture on this machine
# already produced, under a key that pins the interpreter, the installed
# packages, numpy's build and a bit-exact fingerprint of the arithmetic. The
# category exists because the fixtures differ ACROSS machines, and the key's
# whole job is to make a hit impossible across machines. Two pieces of
# evidence rather than the assertion alone: a cold run and a warm run of
# --all against the same ref both reported the same verdict over all 55
# scenarios, the five sensitive ones included; and the optimizer's plan is
# byte-identical with BLAS threads pinned to one and left at four (12 of 12
# runs, same fingerprint), so a change in how many cores happened to be idle
# when the baseline was captured cannot move a sensitive fixture either.

CACHE_FORMAT = "1"
CACHE_DIR_ENV = "DRIFT_CACHE_DIR"
CACHE_OFF_ENV = "DRIFT_NO_CACHE"
CACHE_KEEP_ENV = "DRIFT_CACHE_KEEP"
CACHE_KEEP_DEFAULT = 24
#: Set by the push-to-main gate (issue #94). A merge to main moves every
#: open PR's merge-base at once, so they all miss the cache and each pays
#: a full cold capture -- the dominant CI cost with several PRs open.
#: With this set, the run stores the branch-side capture it already made
#: (the new main tree, captured for this run's own comparison) under the
#: key those PRs will compute, turning their next cold capture into a
#: restore. The entry goes through the same ``cache_store``, so it keeps
#: the built-in key re-check: a wrong restore is a miss, never a stale
#: baseline.
WARM_ENV = "DRIFT_WARM_CACHE"

#: Environment variables that can change what a capture computes: the tree's
#: own HASTUB_TZ, the timezone and locale beneath it, every BLAS/OpenMP
#: threading knob, and the interpreter's own switches. Prefix-matched so a
#: variable added later is covered without an edit here.
CACHE_ENV_PREFIXES = (
    "HASTUB_", "HPO_", "HEATPUMP_",
    "NPY_", "NUMPY_", "SCIPY_",
    "OPENBLAS_", "MKL_", "OMP_", "NUMEXPR_", "VECLIB_", "BLIS_", "GOTOBLAS_",
    "LC_",
)
CACHE_ENV_NAMES = (
    "TZ", "LANG", "LANGUAGE", "SOURCE_DATE_EPOCH",
    "PYTHONHASHSEED", "PYTHONOPTIMIZE", "PYTHONDONTWRITEBYTECODE",
    "PYTHONUTF8", "PYTHONWARNINGS", "PYTHONNOUSERSITE", "PYTHONSAFEPATH",
    "PYTHONINTMAXSTRDIGITS", "PYTHONFAULTHANDLER",
)


def cache_disabled() -> bool:
    """True when DRIFT_NO_CACHE asks for the baseline to be recomputed."""
    return os.environ.get(CACHE_OFF_ENV, "").strip().lower() not in ("", "0", "false", "no")


def cache_keep() -> int:
    """How many entries to keep. A garbage value falls back to the default."""
    try:
        keep = int(os.environ.get(CACHE_KEEP_ENV, CACHE_KEEP_DEFAULT))
    except ValueError:
        return CACHE_KEEP_DEFAULT
    return max(1, keep)


def cache_dir() -> str:
    """Where baseline captures live. Never inside the repo -- see main()."""
    override = os.environ.get(CACHE_DIR_ENV, "").strip()
    if override:
        return os.path.abspath(override)
    base = os.environ.get("XDG_CACHE_HOME", "").strip()
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(base, "heatpump_optimizer", "drift-baseline")


def _inside(child: str, parent: str) -> bool:
    """True when `child` is `parent` or sits under it."""
    child = os.path.realpath(child)
    parent = os.path.realpath(parent)
    return child == parent or child.startswith(parent + os.sep)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _numeric_probe() -> str:
    """A bit-exact fingerprint of this machine's floating-point arithmetic.

    Fixed seed, fixed sizes, no wall-clock and no randomness: the digest is
    stable across runs on one machine and moves when numpy, scipy, the BLAS
    behind them or the libm under those changes. It exercises the same four
    things the optimizer leans on -- dense linear algebra, an SVD, a HiGHS
    linear program and an L-BFGS-B minimisation -- and costs about 0.1 s,
    against the twenty minutes it protects.
    """
    import numpy as np
    from scipy.optimize import linprog, minimize

    h = hashlib.sha256()
    rng = np.random.default_rng(20260828)
    a = rng.standard_normal((64, 64))
    b = rng.standard_normal(64)
    h.update(np.linalg.solve(a.T @ a + 64.0 * np.eye(64), a.T @ b).tobytes())
    h.update(np.linalg.svd(a, compute_uv=False).tobytes())
    c = rng.standard_normal(40)
    a_ub = rng.standard_normal((20, 40))
    b_ub = np.abs(rng.standard_normal(20)) + 1.0
    lp = linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=[(-5.0, 5.0)] * 40, method="highs")
    h.update(struct.pack("<d", float(lp.fun)))
    h.update(np.asarray(lp.x, dtype=float).tobytes())

    def _objective(v):
        return float(np.sum((v - 0.3) ** 2) + 0.1 * np.sum(np.cos(3.0 * v)))

    res = minimize(
        _objective, np.linspace(-1.0, 1.0, 48), method="L-BFGS-B",
        bounds=[(-2.0, 2.0)] * 48,
        options={"maxiter": 200, "ftol": 1e-9, "eps": 1e-4},
    )
    h.update(struct.pack("<d", float(res.fun)))
    h.update(np.asarray(res.x, dtype=float).tobytes())
    return h.hexdigest()


def _package_inventory() -> list[str]:
    """Every installed distribution and its version, sorted."""
    from importlib.metadata import distributions

    seen = set()
    for dist in distributions():
        name = dist.metadata["Name"] if dist.metadata else None
        seen.add(f"{name or '?'}=={dist.version}")
    return sorted(seen)


def _numpy_build() -> str:
    """numpy's build configuration, including which BLAS it was linked to."""
    import numpy as np

    show = getattr(np.__config__, "show", None)
    if show is None:
        return ""
    try:
        return json.dumps(show(mode="dicts"), sort_keys=True, default=str)
    except TypeError:  # numpy < 2 has no dict mode
        return ""


def _relevant_environment() -> list[str]:
    """The environment variables a capture's output can depend on."""
    out = []
    for name, value in os.environ.items():
        if name.startswith(CACHE_ENV_PREFIXES) or name in CACHE_ENV_NAMES:
            out.append(f"{name}={value}")
    return sorted(out)


def cache_key_inputs(repo: str, ref_sha: str, everything: bool) -> dict:
    """Everything the baseline payload can depend on, as a JSON-able dict.

    Raises when any component cannot be determined: a key with a hole in it
    is worse than no cache, so the caller turns the cache off instead.
    """
    driver = os.path.abspath(__file__)
    tree = subprocess.run(
        ["git", "rev-parse", f"{ref_sha}^{{tree}}"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if not tree:
        raise ValueError(f"{ref_sha} has no tree")
    return {
        "cache_format": CACHE_FORMAT,
        "mode": "all" if everything else "sensitive",
        "sensitive": list(SENSITIVE),
        "baseline_commit": ref_sha,
        "baseline_tree": tree,
        "driver_sha256": _sha256_file(driver),
        "interpreter": {
            "executable": os.path.realpath(sys.executable),
            "version": sys.version,
            "implementation": platform.python_implementation(),
            "api_version": sys.api_version,
            "maxsize": sys.maxsize,
            "float_repr_style": sys.float_repr_style,
        },
        "platform": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "byteorder": sys.byteorder,
        },
        "packages": _package_inventory(),
        "numpy_build": _numpy_build(),
        "numeric_probe": _numeric_probe(),
        "environment": _relevant_environment(),
    }


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def cache_key(inputs: dict) -> str:
    return hashlib.sha256(_canonical(inputs).encode()).hexdigest()


def cache_component_digests(inputs: dict) -> list[tuple[str, str]]:
    """A short digest per key component, so a miss can be explained."""
    return [
        (name, hashlib.sha256(_canonical(value).encode()).hexdigest()[:12])
        for name, value in sorted(inputs.items())
    ]


def cache_entry_path(directory: str, key: str) -> str:
    return os.path.join(directory, f"{key}.json")


def cache_load(path: str, key: str) -> tuple[dict | None, str]:
    """The cached baseline payloads at `path`, or None and why not.

    Both the key the entry was written under and a digest of the capture text
    are re-checked here, so a truncated, hand-edited or half-written file is a
    miss rather than a lie.
    """
    if not os.path.exists(path):
        return None, "no entry for this key"
    try:
        with open(path) as f:
            entry = json.load(f)
    except (OSError, ValueError) as err:
        return None, f"entry unreadable ({err.__class__.__name__})"
    if entry.get("cache_format") != CACHE_FORMAT:
        return None, "entry was written by a different cache format"
    if entry.get("key") != key:
        return None, "entry does not carry this key"
    text = entry.get("capture_json")
    if not isinstance(text, str):
        return None, "entry carries no capture"
    if hashlib.sha256(text.encode()).hexdigest() != entry.get("capture_sha256"):
        return None, "entry's capture does not match its own digest"
    try:
        payloads = json.loads(text)
    except ValueError:
        return None, "entry's capture is not JSON"
    if not isinstance(payloads, dict) or not payloads:
        return None, "entry's capture is empty"
    return payloads, ""


def cache_store(path: str, key: str, inputs: dict, ref: str, capture_text: str) -> None:
    """Write one baseline capture, atomically, alongside the key that made it."""
    entry = {
        "cache_format": CACHE_FORMAT,
        "key": key,
        "ref_name": ref,
        "written_at": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "key_inputs": inputs,
        "capture_sha256": hashlib.sha256(capture_text.encode()).hexdigest(),
        "capture_json": capture_text,
    }
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    # Written to a temporary name and renamed into place, so a run that dies
    # mid-write leaves no half-entry for the next one to read. The reader
    # re-checks the digest anyway; this keeps it from having to.
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".writing-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(entry, f)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def cache_prune(directory: str, keep: int) -> None:
    """Keep the `keep` most recently written entries; drop the rest."""
    try:
        entries = [
            os.path.join(directory, n)
            for n in os.listdir(directory)
            if n.endswith(".json")
        ]
    except OSError:
        return
    if len(entries) <= keep:
        return
    dated = []
    for path in entries:
        try:
            dated.append((os.path.getmtime(path), path))
        except OSError:
            continue
    for _, path in sorted(dated, reverse=True)[keep:]:
        try:
            os.unlink(path)
        except OSError:
            pass


def _age(seconds: float) -> str:
    if seconds < 90:
        return f"{seconds:.0f} s ago"
    if seconds < 5400:
        return f"{seconds / 60:.0f} min ago"
    if seconds < 172800:
        return f"{seconds / 3600:.1f} h ago"
    return f"{seconds / 86400:.1f} days ago"


BANNER = "=" * 74


def print_cache_hit(path: str, key: str, inputs: dict, ref: str) -> None:
    """Say, unmissably, that the baseline was reused instead of recomputed."""
    try:
        written = os.path.getmtime(path)
        age = _age(max(0.0, time.time() - written))
    except OSError:
        age = "unknown age"
    print(BANNER)
    print("DRIFT BASELINE CACHE HIT -- the baseline was REUSED, not recomputed")
    print(f"  key       {key}")
    print(f"  entry     {path}")
    print(f"  ref       {ref} -> {inputs['baseline_commit']}")
    print(f"  tree      {inputs['baseline_tree']}")
    print(f"  mode      {inputs['mode']}")
    print(f"  captured  {age}")
    print("  key covers:")
    for name, digest in cache_component_digests(inputs):
        print(f"    {name:<16} {digest}")
    print(f"  bypass    {CACHE_OFF_ENV}=1 to capture the baseline from scratch")
    print(BANNER)


def print_cache_miss(reason: str, path: str, key: str, inputs: dict, ref: str) -> None:
    print(BANNER)
    print(f"DRIFT BASELINE CACHE MISS ({reason}) -- capturing {ref} from scratch")
    print(f"  key       {key}")
    print(f"  entry     {path}")
    for name, digest in cache_component_digests(inputs):
        print(f"    {name:<16} {digest}")
    print(BANNER)



def capture_tree(root: str, out_path: str, everything: bool) -> None:
    """Worker mode: capture scenarios from one repo root."""
    os.chdir(root)  # golden.py resolves its fixtures relative to cwd
    sys.path.insert(0, os.path.join(root, "tests"))
    sys.path.insert(0, os.path.join(root, "custom_components"))
    import golden

    if everything:
        payloads = {n: golden.capture(n, s) for n, s in golden.SCENARIOS.items()}
        for name, config in golden.coordinator_scenarios().items():
            payloads[name] = golden.capture_coordinator(config)
        payloads["config_flow"] = golden.capture_config_flow()
    else:
        payloads = {n: golden.capture(n, golden.SCENARIOS[n]) for n in SENSITIVE}
    # The worker writes exactly one file, and its only caller passes a
    # path inside a tempfile.mkdtemp() directory. Refuse anything outside
    # the system temp root so a mistyped or hostile --capture argument
    # cannot turn the worker into an arbitrary-file writer.
    tmp_root = pathlib.Path(tempfile.gettempdir()).resolve()
    resolved = pathlib.Path(out_path).resolve()
    if not resolved.is_relative_to(tmp_root):
        raise SystemExit(f"capture output must live under {tmp_root}: {out_path}")
    resolved.write_text(json.dumps(payloads, indent=1, sort_keys=True))


def _diff_leaves(a, b, path, out) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}.{k}: present on one side only")
            else:
                _diff_leaves(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} vs {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _diff_leaves(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append(f"{path}: {a!r} vs {b!r}")


def _payload_key(fixture: str, diff_line: str) -> str | None:
    """Top-level golden payload key from a ``_diff_leaves`` line."""
    prefix = f"{fixture}."
    if not diff_line.startswith(prefix):
        return None
    rest = diff_line[len(prefix):]
    return rest.split(".")[0].split("[")[0].split(":")[0]


def may_drift_judged_diffs(fixture: str, diffs: list[str]) -> list[str]:
    """Diff lines in ``MAY_DRIFT_JUDGED_KEYS`` — fail even on may-drift fixtures."""
    return [d for d in diffs if _payload_key(fixture, d) in MAY_DRIFT_JUDGED_KEYS]


def may_drift_exempt_diffs(fixture: str, diffs: list[str]) -> list[str]:
    """Plan and basin-sensitive diffs a may-drift fixture may carry."""
    judged = set(MAY_DRIFT_JUDGED_KEYS)
    return [d for d in diffs if _payload_key(fixture, d) not in judged]


# ===========================================================================
# The committed fixtures' own staleness gate (#347, #326)
# ===========================================================================
#
# Everything above compares COMPUTED against COMPUTED: this tree's capture
# against the reference tree's, in one environment, so solver noise cancels.
# Neither side of that comparison is the committed file. The fixtures are
# therefore guarded against CHANGING and not guarded at all against BEING
# WRONG -- and no CI lane closed the gap, because tests/run.sh skips
# tests/golden.py entirely in drift mode, which is the mode both lanes set.
#
# The root cause is not the missing comparison. It is that claiming drift
# never re-records: a claim in tests/golden/claimed_drift.txt excuses a diff
# between two trees and says nothing about the artefact, and nothing anywhere
# runs `golden.py --record`. So every claimed change widened the gap for
# good. tests/golden/config_flow.json was last re-recorded on 2026-08-28 for
# v5.3.0; PR #324 claimed config_flow drift on 2026-09-03 and left the file
# untouched. #326 was not an accident, it was the workflow working.
#
# What is checked here, and why it can sit in the blocking gate rather than
# in a nightly nobody reads. Measured at 2ab9b84, a full 55-scenario capture
# against the committed fixtures on a machine whose solver disagrees with the
# recording machine's: 34 fixtures differ, 14461 leaves in all.
#
#   LEVEL 1, exact. Only for fixtures with no float on either side -- read
#   off the payload by carries_floats(), never a hand-kept list, because a
#   list would rot exactly the way the fixtures did. Today that is
#   config_flow alone, and it is where #326 lives: ten string-valued leaves,
#   including the window_area minimum '0' -> '0.01' that PR #324 shipped and
#   never recorded. Fails the gate.
#
#   LEVEL 2, structural. Every fixture: the set of key paths and the JSON
#   type class at each. Fails the gate.
#
#   LEVEL 3, values. Every fixture, counted and reported, never failed --
#   these are the 121 length-preserving value moves that ARE the machine
#   (compressor_starts 3 -> 4, heat_pump_on_schedule True -> False,
#   optimal_setpoints 22.6 -> 20.4). Only CI can honestly re-record them; a
#   dev box would poison them, which is why claims exist instead of records.
#
# The projection in level 2 was cut to fit the measurement, one signal at a
# time, and the cuts are the whole reason it is not red on main:
#
#   key paths + type class    fires on exactly 6 of the 34: config_flow and
#                             the five coord_* -- every one of them a key the
#                             code produces and the fixture has never seen
#   + container lengths       fires on 9. narrow_band's planned DHW hours
#                             18 -> 17, wood_coil's 13 -> 18, and
#                             valve_storage_smart_write's valve target
#                             schedule 96 -> 0 are all the solver choosing a
#                             different plan, not a stale fixture
#
# So list LENGTHS are machine-sensitive in this payload set and are reported
# at level 3 rather than gated, and list elements collapse onto a single
# `[]` path for the same reason: comparing element 17 of a list whose length
# is the plan's business compares two different things. An empty array on
# either side carries no element types at all, so its subtree is dropped
# from the comparison rather than read as "the types vanished".
#
# The residual gap, said out loud: a deliberate structural change to a list's
# length is not caught here. It is caught by the tree-vs-tree comparison
# above, which is what that comparison is good at.

FIXTURE_DIR = os.path.join("tests", "golden")
#: Print level 3 in full rather than as a count. The nightly sets it: it is
#: the one run that can afford the wall of numbers, and it is the run whose
#: reader is deciding what to re-record.
VALUE_REPORT_ENV = "DRIFT_VALUE_REPORT"


def carries_floats(node) -> bool:
    """Does any leaf of this payload carry a float?

    The one question that decides whether an exact comparison against a
    committed file is honest on a machine that is not the recording one.
    """
    if isinstance(node, dict):
        return any(carries_floats(v) for v in node.values())
    if isinstance(node, list):
        return any(carries_floats(v) for v in node)
    return isinstance(node, float)


def _type_class(node) -> str:
    """The JSON type, with int and float as one class.

    They are one class on purpose: `compressor_starts: 3 -> 4` is the solver
    landing in another basin, and an int that flips is not a fixture that
    went stale.
    """
    if node is None:
        return "null"
    if isinstance(node, bool):
        return "bool"
    if isinstance(node, (int, float)):
        return "number"
    if isinstance(node, str):
        return "string"
    if isinstance(node, list):
        return "array"
    return "object"


def _collect_shape(node, path: str, shape: dict, empty: set) -> None:
    """Every path in a payload and the type class(es) found there.

    List elements all collapse onto one `[]` path and their classes are
    unioned, so nothing here depends on a list's length or on which element
    landed at which index -- both of which are the plan's business.
    """
    kind = _type_class(node)
    shape.setdefault(path, set()).add(kind)
    if kind == "object":
        for key in sorted(node):
            _collect_shape(node[key], f"{path}.{key}", shape, empty)
    elif kind == "array":
        if not node:
            empty.add(path)
        for item in node:
            _collect_shape(item, f"{path}[]", shape, empty)


def shape_diff(committed, computed, name: str = "") -> list[str]:
    """Level 2: what differs between two payloads apart from scalar values."""
    left: dict[str, set] = {}
    right: dict[str, set] = {}
    left_empty: set[str] = set()
    right_empty: set[str] = set()
    _collect_shape(committed, name, left, left_empty)
    _collect_shape(computed, name, right, right_empty)
    # An array that is empty on either side says nothing about its element
    # types, and reading that silence as "the types vanished" is exactly the
    # valve_storage_smart_write false positive (96 targets there, 0 here).
    blind = tuple(root + "[]" for root in sorted(left_empty | right_empty))
    out: list[str] = []
    for path in sorted(set(left) | set(right)):
        if blind and path.startswith(blind):
            continue
        label = path or "<payload>"
        if path not in left or path not in right:
            side = "the code produces it" if path in right else "the fixture has it"
            out.append(f"{label}: present on one side only ({side})")
        elif left[path] != right[path]:
            out.append(
                f"{label}: {'|'.join(sorted(left[path]))}"
                f" -> {'|'.join(sorted(right[path]))}"
            )
    return out


def exact_diff(committed, computed, name: str = "") -> list[str]:
    """Level 1: every differing leaf, for payloads with no float to travel."""
    out: list[str] = []
    _diff_leaves(committed, computed, name, out)
    return out


class StalenessReport:
    """What one capture says about the fixtures committed beside it."""

    def __init__(self) -> None:
        self.exact: dict[str, list[str]] = {}
        self.structural: dict[str, list[str]] = {}
        self.values: dict[str, int] = {}
        self.missing: list[str] = []
        self.checked = 0
        self.exact_checked = 0

    @property
    def failed(self) -> int:
        """Fixtures the gate fails on. Level 3 is reported, never counted."""
        return len(set(self.exact) | set(self.structural)) + len(self.missing)


def fixture_staleness(fixture_dir: str, captured: dict) -> StalenessReport:
    """Run all three levels of a capture against the committed fixtures."""
    report = StalenessReport()
    for name in sorted(captured):
        path = os.path.join(fixture_dir, f"{name}.json")
        if not os.path.exists(path):
            report.missing.append(name)
            continue
        with open(path) as handle:
            committed = json.load(handle)
        computed = captured[name]
        report.checked += 1

        structural = shape_diff(committed, computed, name)
        if structural:
            report.structural[name] = structural

        # Exact only where both sides are float-free. Both, not just the
        # committed one: a fixture that has GAINED a float is a level 2
        # failure, and comparing its floats exactly on top of that would
        # only bury the type change in noise.
        if not carries_floats(committed) and not carries_floats(computed):
            report.exact_checked += 1
            exact = exact_diff(committed, computed, name)
            if exact:
                report.exact[name] = exact

        leaves: list[str] = []
        _diff_leaves(committed, computed, name, leaves)
        if leaves:
            report.values[name] = len(leaves)
    return report


def print_staleness(report: StalenessReport, verbose: bool = False) -> None:
    """Say what the three levels found, and what they deliberately did not."""
    print()
    print("########## committed fixtures: staleness (#347) ##########")
    print(f"  {report.checked} fixture(s) compared against this tree's capture; "
          f"{report.exact_checked} of them float-free and compared exactly.")

    for name in sorted(report.exact):
        lines = report.exact[name]
        print(f"  STALE {name}: {len(lines)} leaf/leaves differ from the "
              f"committed file (exact, float-free)")
        for line in lines[:6]:
            print(f"         {line}")
        if len(lines) > 6:
            print(f"         ... and {len(lines) - 6} more")
    for name in sorted(report.structural):
        lines = report.structural[name]
        print(f"  STALE {name}: {len(lines)} path(s) differ in STRUCTURE from "
              f"the committed file")
        for line in lines[: (20 if verbose else 5)]:
            print(f"         {line}")
        if len(lines) > (20 if verbose else 5):
            print(f"         ... and {len(lines) - (20 if verbose else 5)} more")
    for name in report.missing:
        print(f"  STALE {name}: captured, but tests/golden/{name}.json does "
              f"not exist -- the scenario was never recorded")

    # Level 3. Reported in every mode and failed in none: these are the
    # machine's own numbers, and only a canonical environment can honestly
    # re-record them.
    movers = {n: c for n, c in report.values.items()
              if n not in report.exact and n not in report.structural}
    if movers:
        total = sum(movers.values())
        print(f"\n  values (reported, never failed): {len(movers)} fixture(s), "
              f"{total} leaf/leaves differ from the committed files in value "
              f"alone.")
        print("  A float-bearing fixture can only be re-recorded honestly in "
              "the environment")
        print("  that records them all; a dev box would poison it. Nothing "
              "here is failed on.")
        if verbose:
            for name in sorted(movers, key=lambda n: -movers[n]):
                print(f"    {movers[name]:6d}  {name}")

    if report.failed:
        print(f"\n{report.failed} COMMITTED FIXTURE(S) ARE STALE")
        print("The committed file no longer matches what this code produces,")
        print("and the difference is not a float. Re-record it on purpose:")
        print("  PYTHONPATH=tests/hastub python3 tests/golden.py --record "
              "--only <name>")
        print("A float-free fixture (config_flow) can be recorded on any")
        print("machine. For anything else, check first that no pre-existing")
        print("leaf moves -- `--fixtures` prints the count -- or record it")
        print("where the whole set was recorded.")
    else:
        print("  no committed fixture is stale")


def check_fixtures(repo: str, capture_path: str | None = None) -> int:
    """`--fixtures`: the three levels alone, with no reference tree at all.

    The gate runs these levels inside the drift comparison, which needs a
    baseline worktree and captures twice. This entry point captures once and
    compares against the committed files only -- which is what the nightly
    wants for level 3, and what a human wants when re-recording. Given a
    capture written earlier by `--capture`, it re-reads that instead of
    solving again.
    """
    if capture_path:
        with open(capture_path) as handle:
            captured = json.load(handle)
        print(f"read {len(captured)} scenario(s) from {capture_path}")
    else:
        tmp = tempfile.mkdtemp(prefix="env_drift_fixtures_")
        try:
            out_path = os.path.join(tmp, "branch.json")
            env = dict(os.environ)
            env["PYTHONPATH"] = os.path.join(repo, "tests", "hastub")
            subprocess.run(
                [sys.executable, os.path.abspath(__file__),
                 "--capture", repo, out_path, "--all"],
                check=True, env=env,
            )
            with open(out_path) as handle:
                captured = json.load(handle)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        print(f"captured {len(captured)} scenario(s) from {repo}")
    report = fixture_staleness(os.path.join(repo, FIXTURE_DIR), captured)
    print_staleness(report, verbose=True)
    return 1 if report.failed else 0


def _repo_version(repo: str) -> str:
    """The release this tree is, per the repo-root VERSION file."""
    path = os.path.join(repo, VERSION_FILE)
    if not os.path.exists(path):
        return ""
    return open(path).read().strip()


def _looks_like_version(text: str) -> bool:
    parts = text.split(".")
    return len(parts) == 3 and all(p.isdigit() for p in parts)


def _rev(repo: str, rev: str) -> str | None:
    """The commit `rev` names in `repo`, or None when it does not resolve."""
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=repo, capture_output=True, text=True,
    )
    return proc.stdout.strip() or None


def _parse_claims(text: str) -> tuple[str | None, dict[str, str]]:
    """Stamp and parsed claims from claim-file text. See ``_claimed``."""
    declared: str | None = None
    claims: dict[str, str] = {}
    for line in text.splitlines():
        body, _, comment = line.partition("#")
        name = body.strip()
        if name:
            claims[name] = comment.strip() or "no reason given"
            continue
        note = comment.strip()
        if declared is None and note.startswith(CLAIM_VERSION_MARKER):
            rest = note[len(CLAIM_VERSION_MARKER):].split()
            declared = rest[0] if rest else ""
    return declared, claims


def _claimed(repo: str, relpath: str = CLAIM_FILE) -> tuple[str | None, dict[str, str]]:
    """The release a claim file is stamped for, and the scenarios it claims.

    The stamp is a comment line that BEGINS with the marker and nothing
    else (`# claims-for: 5.0.0`), first one wins. Merely mentioning
    `claims-for:` does not declare anything — the file's own header prose
    talks about the rule, and an earlier draft of this parser read that
    sentence as the declaration. A claim line never declares either: it has
    a body, so its trailing reason is only a reason.
    """
    path = os.path.join(repo, relpath)
    if not os.path.exists(path):
        return None, {}
    return _parse_claims(open(path).read())


def _claimed_at(repo: str, ref: str, relpath: str) -> dict[str, str]:
    """Parsed claims for ``relpath`` at ``ref``, or empty if the path is missing."""
    proc = subprocess.run(
        ["git", "show", f"{ref}:{relpath}"],
        cwd=repo, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return {}
    return _parse_claims(proc.stdout)[1]


def _may_drift(repo: str) -> dict[str, str]:
    """SENSITIVE fixtures this branch may or may not move, and why.

    An ordinary claim asserts "this scenario moved". For the five fixtures in
    ``SENSITIVE`` that assertion is not a property of the branch at all: they
    do not reproduce across BLAS builds, so each machine solves them to a
    different local optimum, and whether a given change touches one is a fact
    about the runner rather than about the diff.

    v5.1.7 is the case that forced this. Its change relabels the
    ``classify_space_steps`` fall-through, which a plan reaches only when a
    step has no ``heat_loss_factors > 1.1``. All five sensitive fixtures run a
    profile whose factor is a constant 1.06, so every ``preheat_weather`` they
    carry is a fall-through -- and *which* steps fall through depends on the
    local optimum. On this machine only ``valve_upper_direct_slab`` has one;
    the committed fixtures, recorded elsewhere, show them in
    ``valve_storage_smart_write`` and ``wood_two_tank_smart_write`` instead.
    So a claim naming this machine's fixture is unclaimed drift on the
    recording machine, and a claim naming the recording machine's fixtures is
    a stale claim here. Both spellings fail, on different machines, for a
    change that is correct on both.

    A may-drift entry says the honest thing: this scenario is one the gate
    itself declares non-reproducible, this change plausibly touches it, and
    plan drift is printed for a human rather than judged by the runner.
    Diffs in ``MAY_DRIFT_JUDGED_KEYS`` (prices, outdoor_temps, price_known,
    baseline_cost) still fail: they are fixed by the forecast and baseline
    reference, not by which local optimum was reached. It is deliberately
    weaker than a claim for plan keys only, and confined so it cannot be
    used as one: `may_drift_error` rejects any name outside ``SENSITIVE``,
    so the exemption can never reach a fixture whose floats do travel.

    Written as comment lines (``# may-drift: <name> -- <reason>``) so that
    `_claimed`, which reads any non-comment line as a claim, is untouched --
    and so that the entries stay out of the inherited-claims comparison,
    which is right: this is a standing statement about five fixtures, not a
    claim about one release's diff, and it does not expire with VERSION.
    """
    path = os.path.join(repo, CLAIM_FILE)
    out: dict[str, str] = {}
    if not os.path.exists(path):
        return out
    for line in open(path):
        body, _, comment = line.partition("#")
        if body.strip():
            # A claim line. Its trailing text is a reason, never a marker.
            continue
        note = comment.strip()
        if not note.startswith(MAY_DRIFT_MARKER):
            continue
        rest = note[len(MAY_DRIFT_MARKER):].strip()
        name, _, reason = rest.partition("--")
        if name.strip():
            out[name.strip()] = reason.strip() or "no reason given"
    return out


def may_drift_error(
    may_drift: dict[str, str], claims: dict[str, str]
) -> str | None:
    """Why the may-drift list is not usable - None when it is.

    Two rules, and both exist to stop the category becoming a way to launder
    a real regression:

    * it may only name fixtures in ``SENSITIVE``, the ones this script
      already declares non-reproducible. Anywhere else, a moved fixture is
      the branch's doing and has to be claimed;
    * a name cannot be both claimed and may-drift, because the two say
      different things about the same scenario and only one can be checked.
    """
    stray = sorted(set(may_drift) - set(SENSITIVE))
    if stray:
        return (
            "MAY-DRIFT OUT OF SCOPE: {file} marks\n"
            "{stray} as may-drift, but that category exists only for the\n"
            "fixtures this gate declares non-reproducible across BLAS\n"
            "builds: {sensitive}.\n"
            "Everywhere else a moved fixture is this branch's doing and is\n"
            "judged per release -- claim it with a reason, or find out why\n"
            "it moved. Widening this category would let a real regression\n"
            "through under a permanent exemption."
        ).format(
            file=CLAIM_FILE,
            stray=", ".join(stray),
            sensitive=", ".join(SENSITIVE),
        )
    both = sorted(set(may_drift) & set(claims))
    if both:
        return (
            "CLAIMED AND MAY-DRIFT: {file} lists\n"
            "{both} as both. A claim asserts the scenario moved and goes\n"
            "stale when it does not; may-drift asserts nothing either way.\n"
            "Pick one -- may-drift for the sensitive fixtures, a claim for\n"
            "everything else."
        ).format(file=CLAIM_FILE, both=", ".join(both))
    return None


def claim_version_error(repo: str) -> str | None:
    """Why the claim file is not stamped for this tree — None when it is.

    Public on purpose: tests/entities.py calls it too, so the rule holds in
    every GOLDEN_MODE, including the strict runs where run.sh skips this
    script entirely because the comparison ref is unreachable.
    """
    version = _repo_version(repo)
    declared, _ = _claimed(repo)
    if not version:
        return (
            f"NO VERSION FILE: {VERSION_FILE} is missing or empty, so the\n"
            f"claim file in {CLAIM_FILE} cannot be checked against the\n"
            "release it belongs to. Restore VERSION."
        )
    # Equality alone is not enough: `claims-for: next` in a tree whose
    # VERSION also reads `next` would match itself and pass, and a stamp
    # that is not a release number expires on nothing.
    if not _looks_like_version(version):
        return (
            f"MALFORMED VERSION: {VERSION_FILE} reads '{version}', which is\n"
            f"not an X.Y.Z release number, so the '{CLAIM_VERSION_MARKER}'\n"
            f"stamp in {CLAIM_FILE} cannot be tied to a release. Fix\n"
            f"{VERSION_FILE} first."
        )
    if declared == version:
        return None
    if declared is None:
        head = (
            f"UNSTAMPED CLAIM FILE: {CLAIM_FILE} declares no release,\n"
            f"and this tree is v{version}. Every claim file must carry a\n"
            f"'# {CLAIM_VERSION_MARKER} {version}' line of its own."
        )
    elif not _looks_like_version(declared):
        head = (
            f"MALFORMED CLAIM FILE: {CLAIM_FILE} declares\n"
            f"'{CLAIM_VERSION_MARKER} {declared}', which is not a version, and\n"
            f"this tree is v{version}."
        )
    else:
        head = (
            f"STALE CLAIM FILE: {CLAIM_FILE} declares claims for\n"
            f"v{declared} but this tree is v{version}."
        )
    return (
        f"{head} A claim describes one release's diff\n"
        "and does not carry forward. Rewrite the file for this release --\n"
        f"bump the '{CLAIM_VERSION_MARKER}' line and delete claims this release\n"
        "does not move (an empty list is the right answer for a release\n"
        "that moves no goldens)."
    )


def stamp_claims_error(
    claims: dict[str, str], version: str, baseline_version: str
) -> str | None:
    """Why a release commit still carries claims — None when it does not.

    A claim describes exactly one diff. A stamp moves no fixture: it bumps
    VERSION, writes the release notes and re-stamps the claim files, so the
    list it leaves behind belongs to the release just closed and describes a
    diff that is now history. Left in place it becomes every later branch's
    inherited list, and the first branch cut from that main fails
    ``inherited_claims_error`` for a mistake it did not make. That is not
    hypothetical: it is how main went red after v6.3.2, and the branch that
    tripped over it was a one-line import hotfix.

    ``tools/release/stamp.py`` empties the list already. This rule is what
    makes that non-optional, and it fails on the stamp's OWN gate rather
    than on the next contributor's, which is the whole point.

    Fires only when this tree's VERSION is strictly ahead of the baseline's,
    which is what identifies the tree doing the stamping. A branch cut
    before a stamp and compared against a main that has since stamped has a
    version BEHIND the baseline, and may claim whatever its diff earns.
    """
    if not claims:
        return None
    if not (_looks_like_version(version) and _looks_like_version(baseline_version)):
        return None
    mine = tuple(int(part) for part in version.split("."))
    theirs = tuple(int(part) for part in baseline_version.split("."))
    if mine <= theirs:
        return None
    names = textwrap.fill(
        ", ".join(sorted(claims)), width=70, initial_indent="  ",
        subsequent_indent="  ",
    )
    return (
        f"STAMPED WITH CLAIMS: {VERSION_FILE} moves {baseline_version} ->\n"
        f"{version}, so this tree is a release stamp, and a stamp moves no\n"
        f"fixture. {CLAIM_FILE} still claims\n{names}\n"
        "\n"
        "Those claims describe the diff of the release being closed, not this\n"
        "commit. Leaving them makes them the next branch's inherited list and\n"
        "turns main red for whoever forks it next.\n"
        "\n"
        f"Empty the claim list (keep the '# {CLAIM_VERSION_MARKER}' line at\n"
        f"{version} and any '# may-drift:' lines). tools/release/stamp.py does\n"
        "this for you, and stamping by hand is what this check exists to catch."
    )


def parse_claim_map(text: str) -> dict[str, str]:
    """Scenario name -> reason, same rule `_claimed` uses on a file."""
    claims: dict[str, str] = {}
    for line in text.splitlines():
        body, _, comment = line.partition("#")
        name = body.strip()
        if name:
            claims[name] = comment.strip() or "no reason given"
    return claims


def drop_inherited_claim_lines(text: str, baseline_text: str) -> str | None:
    """Delete bare claim lines when the parsed list matches the baseline.

    Keeps the header, `claims-for:`, and `# may-drift:` lines. Returns
    None when the list is empty or not inherited — those are not a
    mechanical rewrite.
    """
    if inherited_claims_error(
        parse_claim_map(text), parse_claim_map(baseline_text), "baseline"
    ) is None:
        return None
    kept = [line for line in text.splitlines() if not line.partition("#")[0].strip()]
    return "\n".join(kept) + "\n"


def apply_inherited_claims(
    repo: str, *, baseline_dir: str | None = None, ref: str | None = None
) -> str:
    """Empty inherited solver and card claim lists in `repo`.

    `baseline_dir` is a tree that already has both files (tests). `ref`
    is a git revision whose blobs are read with `git show` (CI).

    Refuses outright when the three-dot against `ref` moves nothing a
    claim excuses. Emptying such a branch's list is what carried #569's,
    #633's and (nearly) #653's claims off `main` at squash-merge: the
    branch had no business in that file, and "empty it" is a rewrite of
    someone else's line. Only `ref` can be checked this way -- a
    `baseline_dir` is a tree, not a revision, and the tests that use it
    supply the diff's intent themselves.
    """
    kinds = {CLAIM_FILE: True, CARD_CLAIM_FILE: True}
    if ref:
        try:
            kinds = claim_kinds(three_dot_files(repo, ref))
        except GitAnswerMissing:
            return "skip-cannot-compare"
        if not any(kinds.values()):
            return "skip-moves-nothing-claimable"
    changed = False
    for rel in (CLAIM_FILE, CARD_CLAIM_FILE):
        # A list this branch cannot have written is not its to empty: the
        # emptied file squashes onto the baseline and deletes another lane's
        # claims (#608, #635). Per file kind, the same rule as the guard.
        if not kinds[rel]:
            continue
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        if baseline_dir is not None:
            base_path = os.path.join(baseline_dir, rel)
            if not os.path.exists(base_path):
                continue
            baseline = open(base_path).read()
        else:
            if not ref:
                raise ValueError("apply_inherited_claims needs baseline_dir or ref")
            proc = subprocess.run(
                ["git", "show", f"{ref}:{rel}"],
                cwd=repo, capture_output=True, text=True,
            )
            if proc.returncode != 0:
                continue
            baseline = proc.stdout
        new = drop_inherited_claim_lines(open(path).read(), baseline)
        if new is not None:
            open(path, "w").write(new)
            changed = True
    return "changed" if changed else "skip-not-inherited"


def inherited_claims_error(
    claims: dict[str, str], baseline_claims: dict[str, str], ref: str,
    claim_file: str = CLAIM_FILE,
) -> str | None:
    """Why this tree's claim list is the baseline's — None when it is not.

    The `claims-for:` stamp expires a claim per VERSION *value*, which is
    weaker than the rule it stands for: consecutive commits routinely
    share a version (7b512bc/401db6e/2248f64 at 4.0.0, the ten v4.0.0
    T* merges at 3.16.0), and across those an inherited file carries
    a matching stamp. This is the invariant itself: a claim list that is
    exactly the baseline's — same names, same reasons — was written for
    the baseline's diff, not for this one. Comparing the PARSED claims
    rather than the file's bytes means a comment or whitespace edit
    cannot launder an inherited list. An empty list claims nothing and is
    always fine.
    """
    if not claims or claims != baseline_claims:
        return None
    names = ", ".join(sorted(claims))
    return (
        f"INHERITED CLAIMS: {claim_file} claims exactly\n"
        f"what {ref} already claims -- the same {len(claims)} scenario(s),\n"
        "with the same reasons:\n"
        f"  {names}\n"
        "So this list was written for the baseline's diff and carried\n"
        "forward, not written for this one; whatever it excuses here, it\n"
        "excuses by accident. (The 'claims-for:' stamp cannot catch this:\n"
        "it only expires claims when VERSION changes, and a merge at an\n"
        "unchanged version inherits a matching stamp too.) Rewrite the\n"
        "list for THIS diff -- delete what this change does not move, and\n"
        "give what it does move a reason that describes this change. An\n"
        "empty list is the right answer for a change that moves nothing."
    )


def _claim_lines(text: str) -> list[str]:
    """Bare claim lines, in file order — the rule ``parse_claim_map`` uses."""
    return [ln for ln in text.splitlines() if ln.partition("#")[0].strip()]


def _comment_lines(text: str) -> list[str]:
    """Everything a claim line is not: header prose, the stamp, notes, blanks."""
    return [ln for ln in text.splitlines() if not ln.partition("#")[0].strip()]


def _is_may_drift(line: str) -> bool:
    body, _, note = line.partition("#")
    return not body.strip() and note.strip().startswith(MAY_DRIFT_MARKER)


def _union_comments(
    base: list[str], ours: list[str], theirs: list[str]
) -> list[str] | None:
    """Three-way union of comment lines — theirs first, then ours.

    Comment lines assert nothing: ``_parse_claims`` reads only the first
    ``claims-for:`` out of them and ignores the rest, so keeping both sides
    is always sound. ``theirs`` leads so main's accumulated notes stay in
    their order and this branch's note lands last, which is the resolution
    every seat here wrote by hand. Union is safe *here* and nowhere else in
    this file — see ``merge_claim_file``.
    """
    with tempfile.TemporaryDirectory() as td:
        paths = []
        for name, lines in (("theirs", theirs), ("base", base), ("ours", ours)):
            path = os.path.join(td, name)
            with open(path, "w") as handle:
                handle.write("".join(ln + "\n" for ln in lines))
            paths.append(path)
        proc = subprocess.run(
            ["git", "merge-file", "--union", "-L", "main", "-L", "base",
             "-L", "branch", *paths],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            return None
        return open(paths[0]).read().splitlines()


def _reassemble(comments: list[str], claims: list[str]) -> str:
    """Put the resolved claim lines back where the file keeps them.

    Claims sit after the note block and before the ``may-drift`` block, with
    a blank line between. Rebuilding rather than patching is what makes the
    round trip byte-exact when neither side moved a claim.
    """
    if not claims:
        return "".join(ln + "\n" for ln in comments)
    at = len(comments)
    for index, line in enumerate(comments):
        if _is_may_drift(line):
            at = index
            break
    while at and not comments[at - 1].strip():
        at -= 1
    return "".join(ln + "\n" for ln in comments[:at] + claims + comments[at:])


def merge_claim_file(base: str, ours: str, theirs: str) -> str | None:
    """Resolve a three-way claim-file merge; None when it must refuse.

    Every branch writes its note into the same place in both claim files, so
    every branch that merges main after another one merged conflicts there.
    The notes are comments and union cleanly. The claim list does not, and
    that asymmetry is the whole design:

    A bare claim line is value-bearing — it excuses a golden diff that would
    otherwise fail the gate, and it is written for exactly one diff. Union a
    branch's list with main's and a claim the branch deliberately deleted
    comes back, carrying the other branch's reason, ready to excuse a drift
    this branch caused. ``inherited_claims_error`` cannot catch it: the
    unioned list is no longer *exactly* the baseline's, which is the only
    shape that check fires on. Measured; `tests/entities.py` pins it.

    So the claim list may change on at most one side. When both sides
    rewrote it there is no rule that says which claim describes which diff,
    and this returns None so git keeps the markers and a human decides.
    """
    base_claims = parse_claim_map(base)
    our_claims = parse_claim_map(ours)
    their_claims = parse_claim_map(theirs)
    if our_claims == their_claims:
        claims_from = ours
    elif our_claims == base_claims:
        claims_from = theirs
    elif their_claims == base_claims:
        claims_from = ours
    else:
        return None
    if ours == theirs or base == theirs:
        return ours
    if base == ours:
        return theirs
    comments = _union_comments(
        _comment_lines(base), _comment_lines(ours), _comment_lines(theirs)
    )
    if comments is None:
        return None
    merged = _reassemble(comments, _claim_lines(claims_from))
    return None if merge_claim_defect(merged, claims_from, ours, theirs) else merged


def merge_claim_defect(
    merged: str, claims_from: str, ours: str, theirs: str
) -> str | None:
    """Why a resolved claim file may not be written — None when it may.

    The driver checks its own output before writing it, because a resolver
    that quietly produces the wrong file is the failure this repository
    keeps re-buying (#523: a job that reported success while repairing
    nothing). Every property here is one a hand resolution preserves.
    """
    if not merged or not merged.endswith("\n"):
        return "the result is empty or does not end in a newline"
    if "<<<<<<<" in merged or ">>>>>>>" in merged:
        return "conflict markers survived into the result"
    if parse_claim_map(merged) != parse_claim_map(claims_from):
        return (
            "the claim list in the result is not the one the merge decided: "
            f"{sorted(parse_claim_map(merged))} vs "
            f"{sorted(parse_claim_map(claims_from))}"
        )
    if _parse_claims(merged)[0] is None:
        return f"the '{CLAIM_VERSION_MARKER}' stamp did not survive the merge"
    kept = set(merged.splitlines())
    for side in (ours, theirs):
        for line in side.splitlines():
            if _is_may_drift(line) and line not in kept:
                return f"a may-drift line was lost: {line.strip()}"
    return None


def merge_claim_refusal(base: str, ours: str, theirs: str) -> str:
    """The message the driver prints when it will not resolve a merge."""
    base_claims = parse_claim_map(base)
    our_claims = parse_claim_map(ours)
    their_claims = parse_claim_map(theirs)
    if base_claims not in (our_claims, their_claims) and our_claims != their_claims:
        return (
            "CONFLICTING CLAIMS: both sides rewrote the claim list -- this\n"
            f"branch claims {sorted(our_claims) or '(nothing)'} and the merge\n"
            f"brings in {sorted(their_claims) or '(nothing)'}. A claim excuses\n"
            "one release's golden diff and is written for that diff alone, so\n"
            "merging two lists would reinstate a claim one side deleted and\n"
            "excuse a drift by accident. Resolve it by hand: keep the claims\n"
            "that describe THIS branch's diff and delete the rest."
        )
    return (
        "UNVERIFIED MERGE: the resolved claim file did not survive its own\n"
        "checks, so it was not written. Resolve this merge by hand."
    )


def gitattributes_error(repo: str, text: str | None = None) -> str | None:
    """Why ``.gitattributes`` does not route both claim files — None when it does."""
    if text is None:
        path = os.path.join(repo, GITATTRIBUTES_FILE)
        text = open(path).read() if os.path.exists(path) else ""
    routed = set()
    for line in text.splitlines():
        fields = line.strip().split()
        if not fields or fields[0].startswith("#"):
            continue
        if f"merge={MERGE_DRIVER_NAME}" in fields[1:]:
            routed.add(fields[0])
    missing = [f for f in (CLAIM_FILE, CARD_CLAIM_FILE) if f not in routed]
    if not missing:
        return None
    return (
        f"UNROUTED CLAIM FILE: {GITATTRIBUTES_FILE} does not send\n"
        + "".join(f"  {name}\n" for name in missing)
        + f"to the '{MERGE_DRIVER_NAME}' merge driver, so every branch that\n"
        "merges main after another branch merged conflicts there by hand.\n"
        f"Add '<path> merge={MERGE_DRIVER_NAME}' for each file listed above."
    )


def install_merge_driver(repo: str) -> str:
    """Configure the claim-file merge driver in ``repo``, and verify the write.

    Git never clones config, so `.gitattributes` alone cannot carry a custom
    driver. Two things make that tolerable. A worktree shares the checkout's
    common `.git/config`, so one install covers every worktree cut from it;
    and with no driver configured git falls back to its ordinary text merge,
    which is exactly today's behaviour — committing `.gitattributes` can
    therefore never make a clone worse than it already is.
    """
    want = {
        f"merge.{MERGE_DRIVER_NAME}.name":
            "union claim-file notes; refuse a claim list both sides rewrote",
        f"merge.{MERGE_DRIVER_NAME}.driver":
            "python3 tests/env_drift.py --merge-claim-file %O %A %B %L %P",
    }

    def _read(key: str) -> str:
        return subprocess.run(
            ["git", "config", "--get", key], cwd=repo,
            capture_output=True, text=True,
        ).stdout.strip()

    already = True
    for key, value in want.items():
        if _read(key) == value:
            continue
        already = False
        subprocess.run(
            ["git", "config", key, value], cwd=repo,
            capture_output=True, text=True, check=True,
        )
    # Read back rather than trust the writes. An installer that reports
    # success while configuring nothing is the same defect as an autofix job
    # that reports success while repairing nothing (#523).
    for key, value in want.items():
        got = _read(key)
        if got != value:
            raise RuntimeError(
                f"install_merge_driver set {key} and git reports {got!r}, "
                f"not {value!r}; the driver is NOT installed"
            )
    return "already-installed" if already else "installed"


def run_merge_driver(base_path: str, ours_path: str, theirs_path: str,
                     marker_size: str = "7", pathname: str = "") -> int:
    """git merge driver: resolve into ``ours_path``, or leave a conflict there.

    Git hands the driver ``ours`` in %A and expects the result there; on a
    refusal it does *not* write markers itself, so this does, and the merge
    then looks exactly as it does with no driver installed.
    """
    base = open(base_path).read()
    ours = open(ours_path).read()
    theirs = open(theirs_path).read()
    label = pathname or ours_path
    merged = merge_claim_file(base, ours, theirs)
    if merged is None:
        subprocess.run(
            ["git", "merge-file", f"--marker-size={marker_size}",
             "-L", f"{label} (this branch)", "-L", f"{label} (merge base)",
             "-L", f"{label} (incoming)", ours_path, base_path, theirs_path],
            capture_output=True, text=True,
        )
        print(f"MERGE-CLAIM: refused {label}\n{merge_claim_refusal(base, ours, theirs)}",
              file=sys.stderr)
        return 1
    with open(ours_path, "w") as handle:
        handle.write(merged)
    # Verify the write itself. `apply_inherited_claims`' sibling defect was a
    # rewrite that returned silently when it matched nothing; a driver that
    # reports a clean merge it did not write is the same failure, one step
    # closer to the tree.
    written = open(ours_path).read()
    if written != merged:
        print(f"MERGE-CLAIM: refused {label}\nWRITE NOT VERIFIED: the resolved "
              "file on disk is not the one that was merged.", file=sys.stderr)
        return 1
    print(f"MERGE-CLAIM: resolved {label}", file=sys.stderr)
    return 0

#: Test files whose contents decide what a capture PRODUCES, so a diff
#: touching one of them can move a fixture with no production line changed.
#: Derived from what ``capture_tree`` imports out of the tree under test --
#: ``golden.py`` itself, the scenario inputs it reads at module level, and the
#: fakes ``capture_config_flow`` builds the flow against -- rather than from a
#: judgement about which tests matter.
#:
#: #547 is the measurement. Seeding options in ``capture_config_flow`` moved
#: the ``config_flow`` fixture against the merge base while the three-dot
#: touched no production file at all, and the two checks then contradicted
#: each other: the drift comparison demanded a claim, and the record-PR guard
#: below refused it. Extend this tuple the same way -- from an import that
#: reaches a capture, with the drift actually measured -- never to quiet a
#: failure.
CAPTURE_SOURCES = (
    "tests/golden.py",
    "tests/profiles.py",
    "tests/harness.py",
)


def justifies_solver_claim(path: str) -> bool:
    """Whether ``path`` can move a solver golden this claim file excuses."""
    return (
        path.startswith("custom_components/heatpump_optimizer/")
        and path.endswith(".py")
    ) or path in CAPTURE_SOURCES


def justifies_card_claim(path: str) -> bool:
    """Whether ``path`` can move a card state this claim file excuses."""
    return path == CARD_JS


def moves_solver_claimable(changed: list[str]) -> bool:
    """Could this three-dot have moved a solver golden ``CLAIM_FILE`` excuses?"""
    return any(justifies_solver_claim(p) for p in changed)


def moves_card_claimable(changed: list[str]) -> bool:
    """Could this three-dot have moved a card state ``CARD_CLAIM_FILE`` excuses?"""
    return any(justifies_card_claim(p) for p in changed)


def moves_claimable(changed: list[str]) -> bool:
    """Could this three-dot have moved anything a claim excuses?"""
    return moves_solver_claimable(changed) or moves_card_claimable(changed)


def claim_kinds(changed: list[str]) -> dict[str, bool]:
    """Which claim file this three-dot may have written for: file -> bool.

    The two files excuse different fixtures moved by different paths, so
    the question is asked per file, never per branch. A branch that moves a
    solver file and no card file can have written the solver list and cannot
    have written the card list -- and `main` legitimately carries card claims
    between a card merge and the next stamp, so the first solver branch after
    one inherits a card list it must leave exactly as found. Judging that
    list as the branch's own is what refused W5-G9 for #735's six claims and
    offered it the one remedy #662 exists to refuse: empty a list someone
    else wrote, which a squash then applies to `main`.
    """
    return {
        CLAIM_FILE: moves_solver_claimable(changed),
        CARD_CLAIM_FILE: moves_card_claimable(changed),
    }


def foreign_claim_file_error(
    claim_file: str, claims: dict[str, str], baseline: dict[str, str], cannot: str
) -> str | None:
    """Why a three-dot that cannot move what ``claim_file`` excuses changed it.

    None when the file's parsed list is the baseline's. Same rule as
    `record_pr_claims_error`, per file: the branch has nothing to say about
    that file, so it leaves it as found -- in either direction.
    """
    if claims == baseline:
        return None
    return (
        f"RECORD PR CLAIMS: {claim_file} differs from the baseline's list, but "
        f"this branch's three-dot cannot move {cannot}, so it cannot have "
        "written that list for this diff. It is about to add or DELETE a claim "
        "it did not write -- and a squash-merge applies that deletion to the "
        "baseline. Restore the file to the baseline's content."
    )


def claims_hygiene_verdict(
    changed: list[str],
    solver: dict[str, str],
    card: dict[str, str],
    base_solver: dict[str, str],
    base_card: dict[str, str],
    ref: str,
) -> str | None:
    """The claim-file rule for one three-dot, per file kind. None when it holds.

    For each claim file: if the three-dot can move what that file excuses, an
    inherited list -- the baseline's, name for name and reason for reason --
    is refused, because it was written for another diff; if it cannot, the
    file must be exactly as found. A three-dot that can move neither is the
    record-PR case and keeps its own rule and message.
    """
    kinds = claim_kinds(changed)
    if not any(kinds.values()):
        return record_pr_claims_error(changed, solver, card, base_solver, base_card)
    for claim_file, claims, baseline, cannot in (
        (CLAIM_FILE, solver, base_solver, "a solver golden"),
        (CARD_CLAIM_FILE, card, base_card, "a card state"),
    ):
        if kinds[claim_file]:
            inherited = inherited_claims_error(claims, baseline, ref, claim_file)
        else:
            inherited = foreign_claim_file_error(claim_file, claims, baseline, cannot)
        if inherited:
            return inherited
    return None


def record_pr_claims_error(
    changed: list[str],
    solver_claims: dict[str, str],
    card_claims: dict[str, str],
    baseline_solver: dict[str, str] | None = None,
    baseline_card: dict[str, str] | None = None,
) -> str | None:
    """Why a docs/roster three-dot changed a claim file — None when it did not.

    If the three-dot touches neither integration Python nor the bundled
    card, it cannot have moved a claimed fixture, so it must leave both
    files EXACTLY AS IT FOUND THEM -- in either direction.

    The rule used to be "both lists must be empty", and that is the same
    rule whenever the baseline claims nothing, which is why every existing
    case still reads the same. It is wrong the moment the baseline claims
    something: these files are shared state that outlives the branch, and
    a squash-merge applies the branch's deletion to `main`. Measured three
    times -- #608 deleted #569's claims, #635 deleted #633's, and #658
    would have deleted #653's `config_flow` line, which is what stopped it.
    A change that moves no fixture has nothing to say about anyone's claim.
    """
    if moves_claimable(changed):
        return None
    base_solver = {} if baseline_solver is None else baseline_solver
    base_card = {} if baseline_card is None else baseline_card
    if solver_claims == base_solver and card_claims == base_card:
        return None
    if not base_solver and not base_card:
        return (
            "RECORD PR CLAIMS: three-dot touches neither card nor solver "
            "fixtures, so both claim lists must be empty. Empty the lists."
        )
    return (
        "RECORD PR CLAIMS: three-dot touches neither card nor solver "
        "fixtures, so both claim files must be left exactly as this branch "
        "found them. They differ from the baseline's, which means this "
        "branch is about to add or DELETE a claim it did not write -- and a "
        "squash-merge applies that deletion to the baseline. Restore the "
        "files to the baseline's content."
    )


class GitAnswerMissing(RuntimeError):
    """A git command this function needed did not answer."""


def three_dot_files(repo: str, ref: str) -> list[str]:
    """Paths in ``ref...HEAD`` plus uncommitted work, same shape as closure.py.

    Raises ``GitAnswerMissing`` when a git command exits non-zero. Reading
    ``stdout`` without ``returncode`` returned an EMPTY list for a failure and
    for a genuinely unchanged tree alike, and the caller reads empty as "no file
    needs a claim". Measured: a ref that RESOLVES but shares no history with
    HEAD -- a shallow clone with graft roots is exactly that, and this
    repository's own handover records the shape as trap 11 -- makes
    ``git diff ref...HEAD`` exit 128 with "no merge base", and
    ``check_claims_hygiene`` then returned None, which is its all-clear.
    The caller's ``_rev`` guard does not cover it: ``_rev`` asks whether the ref
    resolves, and this ref does.
    """
    files: list[str] = []
    for args in (
        ["git", "diff", "--name-only", f"{ref}...HEAD"],
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        proc = subprocess.run(args, cwd=repo, capture_output=True, text=True)
        if proc.returncode != 0:
            raise GitAnswerMissing(
                f"{' '.join(args)} exited {proc.returncode}: "
                f"{proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else 'no message'}"
            )
        files += [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return sorted(set(files))


def stale_claims_judged(repo: str, ref: str) -> bool:
    """May THIS branch be failed for a stale claim it did not write?

    Only if its three-dot could have moved something a claim excuses. A
    claim goes stale between two commits that are both behind a
    documentation branch; failing that branch leaves it one remedy --
    delete the line -- and a squash applies the deletion to the baseline.
    An unanswerable three-dot judges, because a gate that cannot read the
    diff must not quietly stop failing.
    """
    try:
        return moves_solver_claimable(three_dot_files(repo, ref))
    except GitAnswerMissing:
        return True


def check_claims_hygiene(repo: str, ref: str) -> str | None:
    """Inherited lists and the record-PR empty rule, or None when both hold."""
    if _rev(repo, ref) is None:
        return f"cannot resolve {ref}"
    _, solver = _claimed(repo, CLAIM_FILE)
    _, card = _claimed(repo, CARD_CLAIM_FILE)
    base_solver = _claimed_at(repo, ref, CLAIM_FILE)
    base_card = _claimed_at(repo, ref, CARD_CLAIM_FILE)
    # An unanswerable comparison is not a clean one. Returning None here would
    # be the gate reporting "no claim owed" about a tree it could not read.
    # It is computed FIRST because it decides which rule applies: a three-dot
    # that moves nothing claimable owes the files unchanged, and "unchanged"
    # is exactly what `inherited_claims_error` refuses. Running that check on
    # such a branch is the contradiction that stopped #658 -- byte-identical
    # is red, and emptied deletes another lane's line.
    try:
        changed = three_dot_files(repo, ref)
    except GitAnswerMissing as exc:
        return (
            f"CANNOT COMPARE: {exc}\n"
            f"'{ref}' resolves, but the three-dot comparison against HEAD could\n"
            "not be computed, so no statement about claims can be made from it.\n"
            "A shallow clone is the usual cause: git fetch --unshallow origin."
        )
    return claims_hygiene_verdict(changed, solver, card, base_solver, base_card, ref)


def self_comparison_error(ref: str, head: str) -> str:
    """The message for a run whose comparison ref resolves to HEAD."""
    return (
        f"SELF-COMPARISON: '{ref}' resolves to {head[:12]}, which is HEAD.\n"
        "Comparing this tree against itself proves nothing: the two\n"
        "captures are identical by construction, so no drift can ever be\n"
        f"reported and every claim in {CLAIM_FILE} is\n"
        "stale by definition -- a gate that cannot fail is not a gate.\n"
        "Point the comparison ref at the commit this tree should be\n"
        "measured against -- the merge-base with the target branch for a\n"
        "PR, HEAD^1 for a push to main -- and fail the run if that commit\n"
        "cannot be resolved instead of falling back to HEAD."
    )


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--capture":
        everything = "--all" in sys.argv[4:]
        capture_tree(sys.argv[2], sys.argv[3], everything)
        return 0

    if len(sys.argv) >= 2 and sys.argv[1] == "--fixtures":
        # Levels 1-3 against the committed fixtures and nothing else: no
        # reference tree, no baseline capture, no claim file. What the
        # nightly runs for its level 3 report, and what a human runs before
        # and after `golden.py --record`.
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rest = sys.argv[2:]
        return check_fixtures(repo, rest[0] if rest else None)

    if len(sys.argv) >= 2 and sys.argv[1] == "--cache-key":
        # Print the key a run with these arguments would look up, and
        # nothing else. CI uses it to key actions/cache; a human uses it to
        # see why two runs did or did not share a baseline. It is the same
        # function the run itself calls, so the two can never disagree.
        rest = [a for a in sys.argv[2:] if a != "--all"]
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ref = rest[0] if rest and rest[0] else "origin/main"
        ref_sha = _rev(repo, ref)
        if ref_sha is None:
            print(f"cannot resolve {ref}", file=sys.stderr)
            return 1
        print(cache_key(cache_key_inputs(repo, ref_sha, "--all" in sys.argv[2:])))
        return 0

    if len(sys.argv) >= 2 and sys.argv[1] == "--drop-inherited":
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ref = sys.argv[2] if len(sys.argv) > 2 else "origin/main"
        status = apply_inherited_claims(repo, ref=ref)
        print(f"AUTOFIX: {status}")
        return 0

    if len(sys.argv) >= 2 and sys.argv[1] == "--merge-claim-file":
        # git calls this with %O %A %B %L %P. Import-time cost is stdlib
        # only, which is what makes env_drift.py usable as a merge driver.
        rest = sys.argv[2:]
        if len(rest) < 3:
            print("--merge-claim-file needs %O %A %B [%L %P]", file=sys.stderr)
            return 2
        return run_merge_driver(
            rest[0], rest[1], rest[2],
            marker_size=rest[3] if len(rest) > 3 else "7",
            pathname=rest[4] if len(rest) > 4 else "",
        )

    if len(sys.argv) >= 2 and sys.argv[1] == "--install-merge-driver":
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"MERGE-CLAIM: {install_merge_driver(repo)}")
        problem = gitattributes_error(repo)
        if problem:
            print(problem, file=sys.stderr)
            return 1
        return 0

    if len(sys.argv) >= 2 and sys.argv[1] == "--claims-only":
        # No capture. Inherited lists and the record-PR empty rule. run.sh
        # always invokes this so GATE_SCOPE=auto cannot skip it.
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ref = sys.argv[2] if len(sys.argv) > 2 else (
            os.environ.get("GOLDEN_REF") or "origin/main"
        )
        stamp_problem = claim_version_error(repo)
        if stamp_problem:
            print(stamp_problem)
            return 1
        _declared, claims = _claimed(repo)
        may_drift = _may_drift(repo)
        scope_problem = may_drift_error(may_drift, claims)
        if scope_problem:
            print(scope_problem)
            return 1
        err = check_claims_hygiene(repo, ref)
        if err:
            print(err)
            return 1
        print(f"claims hygiene: {ref} ok")
        return 0

    args = [a for a in sys.argv[1:] if a != "--all"]
    everything = "--all" in sys.argv[1:]
    # WARM_ENV, not a CLI flag: the gate calls this script through
    # tests/run.sh, and threading a new flag through it buys nothing an
    # environment variable does not.
    warm = os.environ.get(WARM_ENV, "").strip().lower() in ("1", "true", "yes")
    ref = args[0] if args and args[0] else "origin/main"
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Before anything else, in both modes: a claim file stamped for another
    # release is wrong whatever the capture would say, and this has to fire
    # even when `ref` cannot be resolved and no baseline can be built.
    stamp_problem = claim_version_error(repo)
    if stamp_problem:
        print(stamp_problem)
        return 1
    _declared, claims = _claimed(repo)
    may_drift = _may_drift(repo)
    scope_problem = may_drift_error(may_drift, claims)
    if scope_problem:
        print(scope_problem)
        return 1

    # A ref that resolves to HEAD makes the whole gate vacuous, so say so
    # rather than reporting the "no drift" it would trivially find. (A ref
    # that resolves to nothing is left to the worktree call below, which
    # reports git's own reason for it.)
    head_sha = _rev(repo, "HEAD")
    ref_sha = _rev(repo, ref)
    if head_sha is not None and ref_sha == head_sha:
        print(self_comparison_error(ref, head_sha))
        return 1

    if everything:
        # Same checks --claims-only runs, before the capture. Solver inherited
        # used to wait for the baseline worktree; git show is enough, and the
        # card file has to be judged here too (#493 carried card claims while
        # the solver list was already empty).
        hyg = check_claims_hygiene(repo, ref)
        if hyg:
            print(hyg)
            return 1

    # Look the baseline up before building anything. A hit skips the slowest
    # step in the whole gate; a miss costs one hash of the machine and this
    # file. Every failure mode here -- no ref SHA, an unreadable cache
    # directory, numpy missing, a cache path inside the repo -- turns the
    # cache off and captures from scratch, because a key that could not be
    # computed in full is a key that cannot be trusted.
    key = key_inputs = entry_path = None
    cached_baseline = None
    if cache_disabled():
        print(f"DRIFT BASELINE CACHE OFF ({CACHE_OFF_ENV} is set): "
              f"capturing {ref} from scratch")
    elif ref_sha is None:
        pass  # unresolvable ref: the worktree call below reports git's reason
    else:
        directory = cache_dir()
        if _inside(directory, repo):
            print(f"DRIFT BASELINE CACHE OFF: {CACHE_DIR_ENV} points inside the")
            print(f"  repository ({directory}); a cache there would be committed.")
        else:
            try:
                key_inputs = cache_key_inputs(repo, ref_sha, everything)
                key = cache_key(key_inputs)
                entry_path = cache_entry_path(directory, key)
                cached_baseline, why_not = cache_load(entry_path, key)
            except Exception as err:  # noqa: BLE001 - never fail the gate for a cache
                print(f"DRIFT BASELINE CACHE OFF: could not build a key "
                      f"({err.__class__.__name__}: {err}); capturing from scratch")
                key = key_inputs = entry_path = None
            else:
                if cached_baseline is not None:
                    print_cache_hit(entry_path, key, key_inputs, ref)
                else:
                    print_cache_miss(why_not, entry_path, key, key_inputs, ref)

    tmp = tempfile.mkdtemp(prefix="env_drift_")
    worktree = os.path.join(tmp, "baseline")
    # The worktree is built even on a hit: it costs a second or two against
    # the twenty minutes the capture costs, and it keeps the inherited-claims
    # check reading the baseline's claim file from a real checkout, exactly as
    # it did before there was a cache.
    # Checked out at the SHA the key was computed from, not at the ref NAME.
    # These two are resolved a second or so apart -- long enough for a
    # `git fetch` in another worktree sharing this .git to move origin/main
    # in between, which is not hypothetical: it happened during a run while
    # this cache was being written. Building the worktree from the name
    # would then capture the NEW tree and file it under the OLD commit's
    # key, and every later run would hit that entry and compare against a
    # baseline that is not the one it names. Pinning to ref_sha closes the
    # window: the key and the checkout cannot disagree.
    subprocess.run(
        ["git", "worktree", "add", "--detach", worktree, ref_sha or ref],
        cwd=repo, check=True, capture_output=True,
    )
    try:
        # Cheapest check that needs the baseline, so it runs before the two
        # capture subprocesses rather than after half an hour of solving.
        if everything:
            stamped = stamp_claims_error(
                claims, _repo_version(repo), _repo_version(worktree)
            )
            if stamped:
                print(stamped)
                return 1

        outputs = {}
        for label, root in (("branch", repo), ("baseline", worktree)):
            if label == "baseline" and cached_baseline is not None:
                outputs[label] = cached_baseline
                print(f"  reused   {len(cached_baseline)} scenarios for baseline "
                      f"from cache key {key[:16]} (see the banner above)")
                continue
            out_path = os.path.join(tmp, f"{label}.json")
            env = dict(os.environ)
            env["PYTHONPATH"] = os.path.join(root, "tests", "hastub")
            cmd = [sys.executable, os.path.abspath(__file__),
                   "--capture", root, out_path]
            if everything:
                cmd.append("--all")
            subprocess.run(cmd, check=True, env=env)
            capture_text = open(out_path).read()
            outputs[label] = json.loads(capture_text)
            print(f"  captured {len(outputs[label])} scenarios from {label}")
            # Store the capture's own bytes, so a later hit reparses exactly
            # what this run wrote rather than something re-serialised.
            if label == "baseline" and key is not None:
                try:
                    cache_store(entry_path, key, key_inputs, ref, capture_text)
                except Exception as err:  # noqa: BLE001 - never fail for a cache
                    print(f"  NOT CACHED: {err.__class__.__name__}: {err}")
                else:
                    print(f"  cached   the {ref} baseline under key {key[:16]} "
                          f"in {entry_path}")
                    cache_prune(os.path.dirname(entry_path), cache_keep())
            if label == "branch" and warm and not cache_disabled():
                # The warm store (WARM_ENV above): this run's branch capture
                # IS the new main tree, already captured for its own
                # comparison. Storing it under the key computed for HEAD
                # costs nothing extra and is what the PRs that fork from
                # this commit will look up.
                try:
                    head_sha = _rev(repo, "HEAD")
                    if head_sha is not None:
                        w_inputs = cache_key_inputs(repo, head_sha, everything)
                        w_key = cache_key(w_inputs)
                        w_path = cache_entry_path(cache_dir(), w_key)
                        cache_store(w_path, w_key, w_inputs, head_sha, capture_text)
                        cache_prune(os.path.dirname(w_path), cache_keep())
                        print(f"  warmed   the cache for the PRs that fork "
                              f"from {head_sha[:12]} (key {w_key[:16]} in "
                              f"{w_path})")
                except Exception as err:  # noqa: BLE001 - never fail for a cache
                    print(f"  NOT WARMED: {err.__class__.__name__}: {err}")

        branch, baseline = outputs["branch"], outputs["baseline"]

        # The branch capture is a fresh computation of every scenario, so
        # the committed files can be judged against it for free -- and this
        # is the only comparison in the gate where one side is the artefact
        # rather than another computation. It runs before the drift
        # comparison because a stale fixture explains nothing about drift
        # and drift explains nothing about staleness: they are independent
        # verdicts and each is reported under its own heading.
        rot = fixture_staleness(os.path.join(repo, FIXTURE_DIR), branch)
        print_staleness(rot, verbose=bool(os.environ.get(VALUE_REPORT_ENV)))

        drifted = 0
        claimed_hits = []
        may_drift_hits: list[str] = []
        for name in sorted(set(branch) | set(baseline)):
            if name not in baseline:
                # Added by this branch, so there is nothing to compare --
                # but a PR that adds a scenario may still have claimed it,
                # and a claim that goes unrecorded here reads as stale.
                if name in claims:
                    claimed_hits.append(name)
                    print(f"  CLAIMED {name}: added by this branch, no baseline "
                          f"on {ref} ({claims[name]})")
                else:
                    print(f"  new   {name}: no baseline on {ref} (added by this branch)")
                continue
            if name not in branch:
                if name in claims:
                    claimed_hits.append(name)
                    print(f"  CLAIMED {name}: removed ({claims[name]})")
                else:
                    drifted += 1
                    print(f"  DRIFT {name}: scenario removed by this branch")
                continue
            diffs: list[str] = []
            _diff_leaves(baseline[name], branch[name], name, diffs)
            if not diffs and name in may_drift:
                # Not "ok": nothing was proved. This machine's solve of a
                # non-reproducible fixture simply did not land on the part
                # the change touches, and another machine's may.
                print(f"  may-drift {name}: did not move here ({may_drift[name]})")
            elif not diffs:
                print(f"  ok    {name} is byte-identical to {ref} here")
            elif name in may_drift:
                judged_diffs = may_drift_judged_diffs(name, diffs)
                exempt_diffs = may_drift_exempt_diffs(name, diffs)
                if judged_diffs:
                    drifted += 1
                    extra = ""
                    if exempt_diffs:
                        extra = f" ({len(exempt_diffs)} plan leaf/leaves exempt)"
                    print(f"  DRIFT {name}: {len(judged_diffs)} judged "
                          f"leaf/leaves moved vs {ref}{extra}")
                    for line in judged_diffs[:5]:
                        print(f"         {line}")
                else:
                    may_drift_hits.append(name)
                    print(f"  MAY-DRIFT {name}: {len(exempt_diffs)} leaves moved "
                          f"({may_drift[name]})")
                    for line in exempt_diffs[:10]:
                        print(f"         {line}")
            elif name in claims:
                claimed_hits.append(name)
                print(f"  CLAIMED {name}: {len(diffs)} leaves moved ({claims[name]})")
                for line in diffs[:3]:
                    print(f"         {line}")
            else:
                drifted += 1
                print(f"  DRIFT {name}: {len(diffs)} leaves moved vs {ref}")
                for line in diffs[:5]:
                    print(f"         {line}")

        # Staleness is only meaningful for scenarios this run captured. The
        # five-fixture mode captures SENSITIVE and nothing else, so a claim
        # for config_flow or a coord_* capture could never land in
        # `claimed_hits` there -- it is unjudged, not stale, and calling it
        # stale failed local strict runs on a perfectly good claim file.
        judged = set(claims) if everything else set(claims) & set(SENSITIVE)
        unjudged = sorted(set(claims) - judged)
        stale = sorted(judged - set(claimed_hits))
        for name in stale:
            print(f"  STALE claim for {name}: nothing drifted, remove it")
        for name in unjudged:
            print(f"  unjudged claim for {name}: not captured in this mode")

        if may_drift_hits:
            print(f"\n{len(may_drift_hits)} MAY-DRIFT SCENARIO(S) MOVED, plan only")
            print("These fixtures are non-reproducible across BLAS builds; only")
            print("diffs outside MAY_DRIFT_JUDGED_KEYS are exempt. Plan drift")
            print("is printed rather than judged:")
            for name in may_drift_hits:
                print(f"  {name}: {may_drift[name]}")
            print("Read the leaf diffs above. Never re-record them on a")
            print("machine where golden.py already reports them as DIFF.")

        if unjudged:
            print(f"\nNOT EVALUATED: {len(unjudged)} claim(s) name scenarios that")
            print("this mode does not capture, so they were neither honoured")
            print(f"nor called stale here: {', '.join(unjudged)}")
            print("Only the five sensitive fixtures are captured without")
            print("--all; run with --all (as CI does) to judge the rest.")

        if drifted:
            print(f"\n{drifted} UNCLAIMED DRIFT(S) vs {ref}")
            print("This branch moved scenarios the baseline does not move in")
            print("this environment: a regression, or a change that must be")
            print("claimed in tests/golden/claimed_drift.txt and justified in")
            print("the PR. Never re-record the five sensitive fixtures on a")
            print("machine where golden.py already reports them as DIFF.")
        if stale:
            # A stale claim is not drift and must not be counted as one: the
            # three historical CI failures on main printed "N UNCLAIMED
            # DRIFT(S)" and a paragraph about regressions when nothing had
            # moved at all, which is what made them so hard to read.
            print(f"\n{len(stale)} STALE CLAIM(S) vs {ref}")
            print("Nothing drifted for these -- they are entries in")
            print("tests/golden/claimed_drift.txt that matched no scenario:")
            for name in stale:
                print(f"  {name}: {claims[name]}")
            print("A claim nothing uses would silently excuse the next")
            print("accidental drift, so it fails. Delete these lines; the")
            print("behaviour they describe is already gone or never came.")
        # WHOSE STALE CLAIM IS IT? A branch whose three-dot moves nothing a
        # claim excuses did not make this one stale and cannot make it fresh:
        # the claim describes drift between two commits that are both behind
        # it. Failing such a branch leaves it one remedy -- delete the line --
        # and a squash then applies that deletion to the baseline, which is how
        # #569's and #633's claims left `main`. So it is REPORTED here and
        # judged on a branch that could have caused it, or by the deliberate
        # act that removes it. An unanswerable three-dot keeps failing closed.
        stale_is_ours = stale_claims_judged(repo, ref) if stale else True
        if stale:
            if not stale_is_ours:
                print("\nNOT THIS BRANCH'S TO REMOVE: the three-dot against")
                print(f"{ref} touches neither card nor solver fixtures, so this")
                print("branch neither caused these claims to go stale nor can")
                print("cure them, and deleting them here would carry someone")
                print("else's line onto the baseline at squash-merge. Reported,")
                print("not judged; remove them in a change that owns the file.")
        if drifted or (stale and stale_is_ours) or rot.failed:
            return 1
        n = len(set(branch) | set(baseline))
        print(f"\nNO UNCLAIMED DRIFT: {n} scenario(s) checked against {ref}")
        print(f"NO STALE FIXTURE: {rot.checked} committed fixture(s) still "
              f"match what this tree computes")
        return 0
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", worktree],
            cwd=repo, capture_output=True,
        )
        # The worktree call above unregisters the checkout but leaves the
        # mkdtemp that held it, so every run used to leave a directory
        # behind in /tmp. A gate that litters the disk it runs on is its
        # own slow failure.
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
