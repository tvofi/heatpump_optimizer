#!/usr/bin/env python3
"""Shared guard for a mutant harness that rewrites a tracked file in place.

A harness that mutates a tracked file and restores it in `finally` leaves the
mutant behind when it is killed (a tool timeout is SIGTERM), so the next run
measures the mutant or refuses on a dirty tree. `guarded(paths)` closes that:

  start   every path must equal `git show HEAD:<path>` byte for byte, else the
          harness exits 2 naming the file, before any mutant is applied;
  signal  SIGTERM and SIGINT restore every path from HEAD's blob, then exit
          128+signal;
  exit    the normal exit restores too; each file's sha256 is then compared with
          HEAD's blob and a mismatch exits 1, naming the file.

`scratch=` lists untracked files the harness writes beside the source (a
`_mutant_*.py` copy, a probe); they are removed on restore and need not exist.
The mutants stay in the working tree: a `git archive` copy fails the #363
recorded_at check on every mutant.

    from mutant_guard import arm, guarded
    arm(["tools/x.py"])            # at the top of main(); the exit hook restores
    with guarded(["tools/x.py"]):  # or around a block
        ...mutate, run, restore as before...

    python3 dev/audit/harnesses/mutant_guard.py --self-test
"""
from __future__ import annotations

import atexit
import contextlib
import hashlib
import os
import signal
import subprocess
import sys
from pathlib import Path



def _repo_root() -> Path:
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    here = Path(__file__).resolve().parent
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise SystemExit("mutant_guard: no repo root above " + str(here))


ROOT = _repo_root()
REFUSE_RC = 2
MISMATCH_RC = 1


def _die(msg: str, rc: int) -> None:
    print(msg, file=sys.stderr, flush=True)
    os._exit(rc)


def _head_blob(rel: str, root: Path) -> bytes:
    r = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"], capture_output=True)
    if r.returncode:
        _die(f"mutant_guard: {rel} is not tracked at HEAD", REFUSE_RC)
    return r.stdout


def _rel(p: str | Path, root: Path) -> str:
    p = Path(p)
    return str(p.relative_to(root) if p.is_absolute() else p)


def restore(rels: list[str], scratch: list[Path], root: Path = ROOT) -> list[str]:
    """Write HEAD's blob back to each path; return those whose sha256 still differs."""
    bad = []
    for rel in rels:
        blob = _head_blob(rel, root)
        target = root / rel
        if not target.exists() or target.read_bytes() != blob:
            target.write_bytes(blob)
        if hashlib.sha256(target.read_bytes()).hexdigest() != hashlib.sha256(blob).hexdigest():
            bad.append(rel)
    for s in scratch:
        Path(s).unlink(missing_ok=True)
    return bad


def arm(paths, scratch=(), root: Path = ROOT):
    """Check, install the handlers and the exit hook; return the `finish` that restores and verifies.

    A harness whose `main` has many returns calls `arm(...)` first and relies
    on the exit hook; `guarded` is the same around a block."""
    root = Path(root)
    rels = [_rel(p, root) for p in paths]
    scr = [Path(s) for s in scratch]
    dirty = [r for r in rels if not (root / r).exists() or (root / r).read_bytes() != _head_blob(r, root)]
    if dirty:
        _die("mutant_guard: refusing, differs from HEAD (a killed run left a mutant?): "
             + ", ".join(dirty), REFUSE_RC)
    old = {}

    def finish():
        if not old:
            return
        bad = restore(rels, scr, root)
        for sg, h in old.items():
            signal.signal(sg, h)
        old.clear()
        if bad:
            _die("mutant_guard: sha256 differs from HEAD after restore: " + ", ".join(bad), MISMATCH_RC)

    def on_signal(signum, _frame):
        bad = restore(rels, scr, root)
        _die("mutant_guard: signal %d, restored %s%s" % (signum, ", ".join(rels),
             "; MISMATCH: " + ", ".join(bad) if bad else ""), MISMATCH_RC if bad else 128 + signum)

    old.update({sg: signal.signal(sg, on_signal) for sg in (signal.SIGTERM, signal.SIGINT)})
    atexit.register(finish)
    return finish


@contextlib.contextmanager
def guarded(paths, scratch=(), root: Path = ROOT):
    finish = arm(paths, scratch, root)
    try:
        yield
    finally:
        finish()


def _self_test() -> int:
    import shutil
    import tempfile
    import time
    fails = 0

    def check(name: str, ok: bool) -> None:
        nonlocal fails
        fails += not ok
        print(("  ok   " if ok else "  FAIL ") + name)

    tmp = Path(tempfile.mkdtemp(prefix="mutguard-"))
    try:
        sys.path.insert(0, str(ROOT / "tests"))
        from throwaway_git import throwaway_git_init
        env = throwaway_git_init(tmp, "-q")
        git = lambda *a: subprocess.run(["git", "-C", str(tmp), *a], check=True, capture_output=True, env=env)  # noqa: E731
        (tmp / "f.txt").write_text("clean\n")
        git("add", "f.txt")
        git("commit", "-q", "-m", "x")
        head = hashlib.sha256(b"clean\n").hexdigest()
        here = str(Path(__file__).resolve().parent)

        def drive(body: str, sig=None, start_dirty=False):
            if start_dirty:
                (tmp / "f.txt").write_text("MUTANT\n")
            code = ("import sys, time\nsys.path.insert(0, %r)\nfrom mutant_guard import guarded\n"
                    "from pathlib import Path\nroot = Path(%r)\nwith guarded(['f.txt'], root=root):\n%s\n"
                    % (here, str(tmp), body))
            p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if sig:
                for _ in range(100):
                    if (tmp / "f.txt").read_text() == "MUTANT\n":
                        break
                    time.sleep(0.1)
                p.send_signal(sig)
            _out, err = p.communicate(timeout=60)
            return p.returncode, err

        sha = lambda: hashlib.sha256((tmp / "f.txt").read_bytes()).hexdigest()  # noqa: E731
        rc, _ = drive("    (root/'f.txt').write_text('MUTANT\\n')\n    (root/'f.txt').write_text('clean\\n')")
        check("null: a clean tree runs and ends at HEAD's digest", rc == 0 and sha() == head)
        rc, _ = drive("    (root/'f.txt').write_text('MUTANT\\n')")
        check("a body that never restores is restored on exit", rc == 0 and sha() == head)
        rc, _ = drive("    (root/'f.txt').write_text('MUTANT\\n'); time.sleep(60)", sig=signal.SIGTERM)
        check("SIGTERM mid-mutant leaves the file at HEAD's digest, rc 143", rc == 143 and sha() == head)
        rc, _ = drive("    (root/'f.txt').write_text('MUTANT\\n'); time.sleep(60)", sig=signal.SIGINT)
        check("SIGINT mid-mutant leaves the file at HEAD's digest, rc 130", rc == 130 and sha() == head)
        rc, err = drive("    print('RAN')", start_dirty=True)
        check("a planted leftover mutant refuses rc 2 naming the file", rc == 2 and "f.txt" in err)
        check("the refusal leaves the planted file as found", (tmp / "f.txt").read_text() == "MUTANT\n")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("MUTANT GUARD SELF-TEST " + ("FAILED" if fails else "PASSED"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_self_test() if sys.argv[1:] == ["--self-test"] else 0)
