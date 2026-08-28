#!/usr/bin/env python3
"""Derive and apply the scoped gate's dependency closures.

The gate is the throughput bottleneck: a full run is about forty minutes,
and a change to the card genuinely needs about five seconds of it. This
module lets ``tests/run.sh`` run only the scripts a change can affect --
without anyone ever writing down, by hand, what a script depends on.

The closures are MEASURED, never declared. ``closure.py record`` runs a test
script for real under two instruments at once:

  * a ``sys.addaudithook`` hook that records every ``open`` the run performs,
    every ``compile``/``exec`` of a file, and every subprocess it spawns; and
  * ``sys.modules`` at the end of the run, filtered to files inside the repo.

The union of those, expressed as repo-relative paths, is the closure. That
catches the things an import graph cannot see -- ``tests/golden/*.json``,
``strings.json``, ``services.yaml``, ``manifest.json``, ``VERSION``, the
translations, ``tests/harness.py``, the plan payload -- because the run
actually opened them. Node scripts (``tests/card.mjs``) are recorded the same
way under ``strace``, since they have no audit hook.

A hand-maintained table would rot on the first refactor and nobody would
notice. This one cannot rot silently either: the post-merge gate on ``main``
re-records every closure while it runs the full suite anyway and fails if the
committed file misses anything a real run touched (``closure.py check``).

Commands
--------
  record <script> --out-dir DIR   run one script instrumented, write its record
  merge  --in-dir DIR             fold records into tests/closures.json
  check  --in-dir DIR             fail if the committed closures under-approximate
  select --files ... | --diff REF decide which scripts a change needs
  show                            print the committed closures

Nothing here imports the integration; recording does, by running the tests.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLOSURES = ROOT / "tests" / "closures.json"

# Scripts that are shared plumbing or are driven by another script, and so are
# never selected on their own. Mirrors the exclusions in tests/run.sh.
NOT_A_TEST = {"harness.py", "profiles.py", "closure.py", "setup_qa_render.mjs"}
# dst_checks.py is a test, but features.py runs it in a subprocess; it is
# recorded so its closure can be folded into features.py's, never selected.
DRIVEN_BY_OTHERS = {"dst_checks.py": "features.py"}

# A dependency of a different kind: not "what can change this script's
# answer" but "what has to run first for this script to run at all".
# plan_view.py WRITES the plan payload card.mjs reads, so a scope that picks
# card.mjs and drops plan_view.py leaves the card with no payload -- or, worse
# on a developer's box, with a stale one another run left behind. Selecting
# card.mjs selects its producer too.
PRODUCERS = {"tests/card.mjs": ["tests/plan_view.py"]}

# ---------------------------------------------------------------------------
# Paths that no test can read, so a change to them cannot break one. This is
# the ONLY hand-written list in the file, it is deliberately tiny, and it is
# checked: `merge` fails if any of these turns up inside a recorded closure,
# because that would mean a test does read it.
#
# Everything else that is not in any closure forces a FULL run. "No test reads
# it" is not something to assume about a file nobody measured.
# It is deliberately shorter than it looks like it should be. Two entries were
# taken off it by measurement rather than by argument:
#
#   README.md, RELEASE_NOTES.md — tests/entities.py reads both, checking the
#     documented behaviour against the code. They are dependencies.
#   the integration's icon and brand images — inside custom_components/, so
#     they are inside env_drift.py's rule-widened closure whatever anyone
#     thinks about them, and claiming otherwise here is just an inconsistency
#     waiting to be believed.
#
# Both were rejected by the check below, which is why they are gone.
INERT = (
    "LICENSE",
    "NOTICE",
    "icon.png",
    "docs/",
    "tests/README.md",
    ".gitignore",
)

# Changing the gate itself, or how the closures are derived, invalidates every
# closure at once: run everything.
GATE_FILES = (
    "tests/run.sh",
    "tests/closure.py",
    "tests/closures.json",
    "tests/requirements-ci.txt",
    ".github/workflows/",
)


def is_inert(rel: str) -> bool:
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in INERT)


def is_gate_file(rel: str) -> bool:
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in GATE_FILES)


def test_scripts() -> list[str]:
    """Every runnable test script, as repo-relative paths."""
    out = []
    for p in sorted(list((ROOT / "tests").glob("*.py")) + list((ROOT / "tests").glob("*.mjs"))):
        if p.name in NOT_A_TEST:
            continue
        out.append(str(p.relative_to(ROOT)))
    return out


def selectable_scripts() -> list[str]:
    return [s for s in test_scripts() if Path(s).name not in DRIVEN_BY_OTHERS]


# ---------------------------------------------------------------------------
# recording


def _rel(path: str) -> str | None:
    """Repo-relative path, or None when the path is outside the repo."""
    if not path:
        return None
    try:
        p = Path(path)
        if not p.is_absolute():
            p = Path.cwd() / p
        p = Path(os.path.normpath(str(p)))
        rel = p.relative_to(ROOT)
    except (ValueError, OSError):
        return None
    s = str(rel)
    if s.startswith(".git/") or s == ".git":
        return None
    if "__pycache__" in s:
        return None
    # The instrument is not a dependency of what it measures.
    if s in ("tests/closure.py", "tests/closures.json"):
        return None
    return s


def _exec_record(script: str, out_path: str, extra_args: list[str]) -> int:
    """Run `script` in this process under an audit hook and dump its record."""
    opened: set[str] = set()
    spawned: list[list[str]] = []

    def hook(event, args):  # noqa: ANN001 - audit hook signature
        try:
            if event == "open":
                p = args[0]
                if isinstance(p, (str, bytes, os.PathLike)):
                    r = _rel(os.fsdecode(p))
                    if r:
                        opened.add(r)
            elif event in ("compile", "exec"):
                pass
            elif event in ("subprocess.Popen", "os.exec", "os.posix_spawn"):
                argv = args[1] if event == "subprocess.Popen" else args[1]
                try:
                    spawned.append([os.fsdecode(a) for a in argv])
                except Exception:
                    pass
        except Exception:
            pass

    started = time.time()
    rc = 0
    sys.argv = [script, *extra_args]
    sys.addaudithook(hook)
    import runpy

    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        rc = int(exc.code or 0) if not isinstance(exc.code, str) else 1
    except BaseException:  # noqa: BLE001 - a failing test still has a closure
        import traceback

        traceback.print_exc()
        rc = 1

    modules = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f:
            r = _rel(f)
            if r:
                modules.add(r)

    # Any repo path that showed up on a subprocess command line is a real
    # dependency too -- that is how features.py reaches tests/dst_checks.py.
    for argv in spawned:
        for a in argv:
            r = _rel(a)
            if r and (ROOT / r).exists():
                opened.add(r)

    record = {
        "script": _rel(str(Path(script).resolve())),
        "rc": rc,
        "seconds": round(time.time() - started, 1),
        "files": sorted(opened | modules),
        "spawned": [" ".join(a) for a in spawned][:200],
        "how": "audithook+sys.modules",
        "argv": [script, *extra_args],
    }
    Path(out_path).write_text(json.dumps(record, indent=1))
    return rc


_STRACE_OPEN = re.compile(r'openat\([^,]+,\s*"([^"]+)"')


def _record_node(script: str, out_path: str, env: dict) -> int:
    """Record a node script's file reads with strace; node has no audit hook."""
    trace = Path(out_path).with_suffix(".strace")
    started = time.time()
    cmd = ["strace", "-f", "-qq", "-e", "trace=openat", "-o", str(trace),
           "node", script]
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    files = set()
    for line in trace.read_text(errors="replace").splitlines():
        m = _STRACE_OPEN.search(line)
        if m:
            r = _rel(m.group(1))
            if r and (ROOT / r).exists():
                files.add(r)
    trace.unlink(missing_ok=True)
    record = {
        "script": script,
        "rc": proc.returncode,
        "seconds": round(time.time() - started, 1),
        "files": sorted(files),
        "spawned": [],
        "how": "strace",
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }
    Path(out_path).write_text(json.dumps(record, indent=1))
    return proc.returncode


def record(script: str, out_dir: Path, args: list[str] | None = None) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (Path(script).name + ".json")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "tests" / "hastub") + os.pathsep + env.get("PYTHONPATH", "")
    if script.endswith(".mjs"):
        return _record_node(script, str(out), env)
    cmd = [sys.executable, str(ROOT / "tests" / "closure.py"), "--exec-record", script,
           str(out), *(args or [])]
    proc = subprocess.run(cmd, cwd=ROOT, env=env)
    return proc.returncode


# ---------------------------------------------------------------------------
# merging and rules


def _is_real_file(rel: str) -> bool:
    """Keep files that exist. A trace also catches directory opens (`tests`,
    `golden`) and paths a run probed and did not find; neither is something a
    change can be made to, and a directory in a closure would match nothing."""
    p = ROOT / rel
    return p.is_file()


def _fold(records: dict[str, dict]) -> dict[str, list[str]]:
    """Records -> closures, applying the rules a trace cannot know.

    Filtering happens here rather than in the tracer so that it applies
    identically to every record, including ones taken before the filter
    existed.
    """
    closures: dict[str, set[str]] = {}
    for name, rec in records.items():
        closures[name] = {f for f in rec["files"] if _is_real_file(f)}
        # The script's own file is a dependency of itself, even if the tracer
        # somehow missed the read.
        closures[name].add(name)

    # A script another script drives contributes its whole closure to its
    # driver, and is not selectable on its own.
    for child, parent in DRIVEN_BY_OTHERS.items():
        c, p = f"tests/{child}", f"tests/{parent}"
        if c in closures and p in closures:
            closures[p] |= closures[c]
            del closures[c]

    # plan_view.py writes the payload card.mjs reads: anything that can change
    # the payload can change what the card is tested against.
    if "tests/card.mjs" in closures and "tests/plan_view.py" in closures:
        closures["tests/card.mjs"] |= closures["tests/plan_view.py"]

    # RULE: env_drift compares BEHAVIOUR between two checkouts, in a
    # subprocess, in a worktree outside this repo. No tracer in this process
    # can see which integration files that behaviour depends on, so the
    # closure is the whole integration -- never a file-name argument.
    ed = "tests/env_drift.py"
    if ed in closures:
        for p in sorted((ROOT / "custom_components").rglob("*")):
            rel = str(p.relative_to(ROOT))
            if p.is_file() and "__pycache__" not in rel:
                closures[ed].add(rel)
        for p in sorted((ROOT / "tests" / "golden").glob("*")):
            if p.is_file():
                closures[ed].add(str(p.relative_to(ROOT)))
    # golden.py stands in for env_drift in strict mode and captures the same
    # scenarios, so it carries the same closure.
    g = "tests/golden.py"
    if g in closures and ed in closures:
        closures[g] |= closures[ed]

    return {k: sorted(v) for k, v in sorted(closures.items())}


def merge(in_dir: Path, out: Path, allow_failures: bool = False) -> int:
    records = {}
    for f in sorted(in_dir.glob("*.json")):
        rec = json.loads(f.read_text())
        name = rec["script"]
        records[name] = rec
    missing = [s for s in test_scripts() if s not in records]
    if missing:
        print(f"closure: no recording for {', '.join(missing)}", file=sys.stderr)
        return 1
    # A recording that ended early records only what the run reached before it
    # stopped, which is an UNDER-approximation -- exactly the direction that
    # makes the gate skip a script it should have run. Refuse it.
    broken = sorted(k for k, r in records.items() if r["rc"] != 0)
    if broken and not allow_failures:
        print("closure: these scripts failed while being recorded, so their",
              file=sys.stderr)
        print("closure is only what they reached before stopping:", file=sys.stderr)
        for b in broken:
            print(f"  {b} (exit {records[b]['rc']}) -- see the run output",
                  file=sys.stderr)
        print("Fix them, or re-run with --allow-failures if you have checked",
              file=sys.stderr)
        print("that the run still exercised every import and every file read.",
              file=sys.stderr)
        return 1
    closures = _fold(records)
    bad = sorted({f for files in closures.values() for f in files if is_inert(f)})
    if bad:
        print("closure: files on the INERT list are actually read by tests:", file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        print("  remove them from INERT in tests/closure.py.", file=sys.stderr)
        return 1
    payload = {
        "_comment": (
            "MEASURED, not written by hand. Regenerate with "
            "tests/derive_closures.sh; the post-merge gate on main re-records "
            "these and fails if this file misses anything a real run touched."
        ),
        "recorded": {k: {"seconds": records[k]["seconds"], "rc": records[k]["rc"]}
                     for k in sorted(records)},
        "closures": closures,
    }
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"closure: wrote {out} ({len(closures)} scripts)")
    for k, v in closures.items():
        print(f"  {k:26s} {len(v):4d} files")
    return 0


def check(in_dir: Path) -> int:
    """Fail if the committed closures MISS anything a fresh run touched.

    Under-approximation is the dangerous direction: it is what makes the gate
    skip a script it should have run. Over-approximation only costs time, so
    it is reported and tolerated.
    """
    if not CLOSURES.exists():
        print("closure: tests/closures.json is missing", file=sys.stderr)
        return 1
    committed = json.loads(CLOSURES.read_text())["closures"]
    records = {}
    for f in sorted(in_dir.glob("*.json")):
        rec = json.loads(f.read_text())
        records[rec["script"]] = rec
    if not records:
        print("closure: no fresh recordings to check against", file=sys.stderr)
        return 1
    fresh = _fold(records) if len(records) == len(test_scripts()) else {
        k: sorted(set(v["files"]) | {k}) for k, v in records.items()
    }
    failed = 0
    for name, files in sorted(fresh.items()):
        have = set(committed.get(name, ()))
        if name not in committed:
            print(f"UNDER-SCOPED: {name} has no committed closure")
            failed += 1
            continue
        missing = sorted(set(files) - have)
        if missing:
            print(f"UNDER-SCOPED: {name} really reads {len(missing)} file(s) "
                  f"the committed closure does not list:")
            for m in missing:
                print(f"    {m}")
            failed += 1
        extra = sorted(have - set(files))
        if extra:
            print(f"note: {name} lists {len(extra)} file(s) this run did not "
                  f"touch (safe: over-scoped)")
    if failed:
        print()
        print(f"{failed} closure(s) are stale. Regenerate with "
              f"tests/derive_closures.sh and commit tests/closures.json.")
        return 1
    print("closure: committed closures cover every file this run touched")
    return 0


# ---------------------------------------------------------------------------
# selection


def changed_files(diff_ref: str) -> list[str]:
    base = subprocess.run(["git", "merge-base", diff_ref, "HEAD"], cwd=ROOT,
                          capture_output=True, text=True)
    ref = base.stdout.strip() if base.returncode == 0 else diff_ref
    out = subprocess.run(["git", "diff", "--name-only", f"{ref}...HEAD"], cwd=ROOT,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"closure: cannot diff against {diff_ref}: {out.stderr.strip()}")
    files = [l.strip() for l in out.stdout.splitlines() if l.strip()]
    # Uncommitted work counts too, so a local `run.sh` scopes to what is
    # actually on disk.
    for extra in (["git", "diff", "--name-only", "HEAD"],
                  ["git", "ls-files", "--others", "--exclude-standard"]):
        o = subprocess.run(extra, cwd=ROOT, capture_output=True, text=True)
        files += [l.strip() for l in o.stdout.splitlines() if l.strip()]
    return sorted(set(files))


def select(files: list[str]) -> dict:
    """Decide what to run. Returns a plan; every decision carries its reason."""
    if not CLOSURES.exists():
        return {"mode": "full", "reason": "tests/closures.json is missing",
                "run": selectable_scripts(), "skip": {}, "changed": files}
    closures = json.loads(CLOSURES.read_text())["closures"]

    scripts = selectable_scripts()
    unknown = sorted(k for k in closures if k not in scripts)
    if unknown:
        return {"mode": "full",
                "reason": f"closures.json describes scripts that no longer exist: "
                          f"{', '.join(unknown)}",
                "run": scripts, "skip": {}, "changed": files}
    uncovered = [s for s in scripts if s not in closures]
    if uncovered:
        return {"mode": "full",
                "reason": f"no closure recorded for {', '.join(uncovered)}",
                "run": scripts, "skip": {}, "changed": files}

    if not files:
        return {"mode": "full", "reason": "no changed files could be determined",
                "run": scripts, "skip": {}, "changed": files}

    for f in files:
        if is_gate_file(f):
            return {"mode": "full",
                    "reason": f"{f} changes the gate itself, so every closure is suspect",
                    "run": scripts, "skip": {}, "changed": files}

    known = {f for files_ in closures.values() for f in files_}
    unmapped = [f for f in files if f not in known and not is_inert(f)]
    if unmapped:
        return {"mode": "full",
                "reason": ("no recorded closure mentions "
                           + ", ".join(unmapped[:6])
                           + (" ..." if len(unmapped) > 6 else "")
                           + " -- an unmeasured file is not a safe skip"),
                "run": scripts, "skip": {}, "changed": files}

    touched_integration = [f for f in files
                           if f.startswith("custom_components/") ]

    run, skip = [], {}
    for s in scripts:
        hits = sorted(set(files) & set(closures[s]))
        if hits:
            run.append(s)
            continue
        if s == "tests/env_drift.py" and touched_integration:
            run.append(s)
            continue
        skip[s] = {"closure_size": len(closures[s]),
                   "reason": "no changed file is in its measured closure"}

    # Pull in whatever the selected scripts need to have run before them.
    for consumer, producers in PRODUCERS.items():
        if consumer in run:
            for prod in producers:
                if prod in skip:
                    del skip[prod]
                    run.append(prod)
    run = [s for s in scripts if s in run]      # back into suite order

    return {"mode": "scoped", "reason": "", "run": run, "skip": skip,
            "changed": files, "closure_sizes": {s: len(closures[s]) for s in scripts}}


def print_plan(plan: dict, stream=sys.stdout) -> None:
    """The plan, written so a human scanning the log cannot misread it."""
    w = stream.write
    w("########## scoped gate ##########\n")
    if plan["mode"] == "full":
        w("  MODE: FULL -- every test script runs, nothing is scoped out.\n")
        w(f"  reason: {plan['reason']}\n")
        return
    w(f"  MODE: SCOPED -- {len(plan['run'])} script(s) run, "
      f"{len(plan['skip'])} scoped out.\n")
    w(f"  changed files ({len(plan['changed'])}), measured against the "
      f"recorded closures in tests/closures.json:\n")
    for f in plan["changed"][:60]:
        w(f"      {f}\n")
    if len(plan["changed"]) > 60:
        w(f"      ... and {len(plan['changed']) - 60} more\n")
    w("\n")
    for s_ in plan["run"]:
        w(f"      RUN   {s_}\n")
    w("\n")
    for s_, info in plan["skip"].items():
        w(f"      SKIP  {s_}  (closure: {info['closure_size']} files, "
          f"{info['reason']})\n")
    w("\n")
    w("  A skipped script is a claim that no changed file is in its measured\n")
    w("  closure. The claim is re-checked by the FULL unscoped suite that runs\n")
    w("  on every push to main, so a wrong closure turns main red within one\n")
    w("  gate. Set GATE_SCOPE=full to run everything here and now.\n")


def write_plan(plan: dict, workdir: Path) -> None:
    """Emit the plan as three files run.sh can read without parsing JSON."""
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "scope.json").write_text(json.dumps(plan, indent=1))
    if plan["mode"] == "full":
        (workdir / "scope.run").write_text("")   # empty == no scoping
    else:
        (workdir / "scope.run").write_text("\n".join(plan["run"]) + "\n")
    lines = []
    for s, info in plan.get("skip", {}).items():
        lines.append(f"{s}\t{info['closure_size']}\t{info['reason']}")
    (workdir / "scope.skip").write_text("\n".join(lines) + ("\n" if lines else ""))
    import io
    buf = io.StringIO()
    print_plan(plan, buf)
    (workdir / "scope.txt").write_text(buf.getvalue())


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--exec-record":
        return _exec_record(sys.argv[2], sys.argv[3], sys.argv[4:])
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record"); r.add_argument("script"); r.add_argument("--out-dir", required=True)
    # REMAINDER, not "*": the arguments being forwarded start with dashes
    # (--only, --cache-key), and argparse reads those as options of its own.
    # That silently recorded nothing for golden.py and env_drift.py once.
    r.add_argument("--args", nargs=argparse.REMAINDER, default=[])
    m = sub.add_parser("merge"); m.add_argument("--in-dir", required=True)
    m.add_argument("--out", default=str(CLOSURES))
    m.add_argument("--allow-failures", action="store_true")
    c = sub.add_parser("check"); c.add_argument("--in-dir", required=True)
    s = sub.add_parser("select")
    s.add_argument("--files", nargs="*"); s.add_argument("--diff")
    s.add_argument("--json", action="store_true")
    s.add_argument("--workdir")
    sub.add_parser("show")
    a = ap.parse_args()
    if a.cmd == "record":
        return record(a.script, Path(a.out_dir), a.args)
    if a.cmd == "merge":
        return merge(Path(a.in_dir), Path(a.out), a.allow_failures)
    if a.cmd == "check":
        return check(Path(a.in_dir))
    if a.cmd == "show":
        print(CLOSURES.read_text())
        return 0
    files = list(a.files or [])
    if a.diff:
        files += changed_files(a.diff)
    plan = select(sorted(set(files)))
    if a.workdir:
        write_plan(plan, Path(a.workdir))
    if a.json:
        print(json.dumps(plan, indent=1))
    else:
        print_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
