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
    list is always fine; it is a statement, not an inheritance.

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
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import time

SENSITIVE = (
    "valve_storage_smart_write",
    "wood_two_tank",
    "wood_two_tank_smart_write",
    "wood_coil",
    "valve_upper_direct_slab",
)

CLAIM_FILE = os.path.join("tests", "golden", "claimed_drift.txt")
CLAIM_VERSION_MARKER = "claims-for:"
#: Declares a SENSITIVE fixture whose drift is judged per machine rather than
#: per release. See `_may_drift` for why an ordinary claim cannot do this job.
MAY_DRIFT_MARKER = "may-drift:"
VERSION_FILE = "VERSION"

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
#   * The baseline tree. `git worktree add --detach <ref>` checks out exactly
#     the tracked content of one commit, so the commit SHA fixes every byte
#     of tests/golden.py, tests/profiles.py, tests/hastub/ and
#     custom_components/. Both the commit and its tree SHA go in the key.
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

CACHE_FORMAT = "1"
CACHE_DIR_ENV = "DRIFT_CACHE_DIR"
CACHE_OFF_ENV = "DRIFT_NO_CACHE"
CACHE_KEEP_ENV = "DRIFT_CACHE_KEEP"
CACHE_KEEP_DEFAULT = 24

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
    with open(out_path, "w") as f:
        json.dump(payloads, f, indent=1, sort_keys=True)


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


def _claimed(repo: str) -> tuple[str | None, dict[str, str]]:
    """The release a claim file is stamped for, and the scenarios it claims.

    The stamp is a comment line that BEGINS with the marker and nothing
    else (`# claims-for: 5.0.0`), first one wins. Merely mentioning
    `claims-for:` does not declare anything — the file's own header prose
    talks about the rule, and an earlier draft of this parser read that
    sentence as the declaration. A claim line never declares either: it has
    a body, so its trailing reason is only a reason.
    """
    path = os.path.join(repo, CLAIM_FILE)
    declared: str | None = None
    claims: dict[str, str] = {}
    if not os.path.exists(path):
        return declared, claims
    for line in open(path):
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
    the diff is printed for a human rather than judged by the runner. It is
    deliberately weaker than a claim, and confined so it cannot be used as
    one: `may_drift_error` rejects any name outside ``SENSITIVE``, so the
    exemption can never reach a fixture whose floats do travel.

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


def inherited_claims_error(
    claims: dict[str, str], baseline_claims: dict[str, str], ref: str
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
        f"INHERITED CLAIMS: {CLAIM_FILE} claims exactly\n"
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

    args = [a for a in sys.argv[1:] if a != "--all"]
    everything = "--all" in sys.argv[1:]
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
    subprocess.run(
        ["git", "worktree", "add", "--detach", worktree, ref],
        cwd=repo, check=True, capture_output=True,
    )
    try:
        # Cheapest check that needs the baseline, so it runs before the two
        # capture subprocesses rather than after half an hour of solving.
        if everything:
            _, baseline_claims = _claimed(worktree)
            inherited = inherited_claims_error(claims, baseline_claims, ref)
            if inherited:
                print(inherited)
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

        branch, baseline = outputs["branch"], outputs["baseline"]
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
                may_drift_hits.append(name)
                print(f"  MAY-DRIFT {name}: {len(diffs)} leaves moved "
                      f"({may_drift[name]})")
                # Printed in full rather than truncated at three: nobody can
                # judge these from a runner's verdict, so the log is the only
                # place the evidence exists.
                for line in diffs[:10]:
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
            print(f"\n{len(may_drift_hits)} MAY-DRIFT SCENARIO(S) MOVED, unjudged")
            print("These are the fixtures this gate declares non-reproducible")
            print("across BLAS builds, so a diff in them is not evidence about")
            print("this branch either way and is printed rather than judged:")
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
        if drifted or stale:
            return 1
        n = len(set(branch) | set(baseline))
        print(f"\nNO UNCLAIMED DRIFT: {n} scenario(s) checked against {ref}")
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
