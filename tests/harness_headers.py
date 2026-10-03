#!/usr/bin/env python3
"""#817: a harness header's EXPECTED RESULT lines must match what it prints.

The headers are hand-maintained. Round 3's judge discarded sound instruments
because a header disagreed with the run. This script executes the cheap
harnesses that issue named and compares each EXPECTED RESULT to the printed
RESULT. Playwright and stress harnesses are not run here.

    PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py
"""
from __future__ import annotations

import os
import re
import resource
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "tests")
from harness import Results

R = Results("harness header EXPECTED vs RESULT (#817)")

ROOT = Path(__file__).resolve().parents[1]
RESULT = re.compile(r"RESULT\s+([A-Za-z0-9_]+)=(\S+)")
SKIP = {"thread_factor", "load1", "swapins", "concurrent_stress_procs"}

# Every harness whose header carries EXPECTED RESULT lines is executed and
# its printed numbers compared against the header. The static tuple this
# replaced named three files, and a fourth harness drifted on main for a day
# behind that limit (#987's review of the claims.py header): a header nobody
# executes is a header nobody re-records. Discovery is dynamic so a harness
# with a RESULT header joins the check the moment it lands. Discovered in
# main() below. #951's qs_rules.py joins via its live-header marker;
# its declared_mismatch line is the quality-scale register's drift alarm, and
# its two coverage-bearing rows are pinned by tests/entities.py against
# tests/coverage_budgets.json instead (they need a coverage payload).


def header_lines(path: Path) -> list[str]:
    """The harness header: every line before the first import / from that is
    not inside the opening docstring or comment block. The one reader of the
    header's extent; ``tools/audit/judge_batch.py`` takes its JUDGE-* lines
    from it rather than parsing the header a second way."""
    text = path.read_text()
    head = []
    in_doc = False
    for line in text.splitlines():
        if line.startswith('"""') or line.startswith("'''"):
            in_doc = not in_doc or line.count('"""') == 1 or line.count("'''") == 1
            if line.strip() in ('"""', "'''") and head:
                in_doc = False
            head.append(line)
            continue
        if in_doc or line.startswith("#") or line.startswith("//"):
            head.append(line)
            continue
        if line.startswith("import ") or line.startswith("from "):
            break
        head.append(line)
    return head


def expected_from(path: Path) -> dict[str, str]:
    found = {}
    for line in header_lines(path):
        for m in RESULT.finditer(line):
            if m.group(1) not in SKIP:
                found[m.group(1)] = m.group(2)
    return found


def _discover() -> tuple[str, ...]:
    # A harness header is executed only when the harness declares itself a
    # live instrument: a `live-header` line in the header. The corpus holds
    # two kinds of harness and executing both was measured wrong (#987's
    # review found the drift; extending execution to every header found
    # 30-of-145 red on round 4 alone): finder harnesses are FROZEN EVIDENCE
    # -- their headers record the finding's baseline, so on a fixed main
    # they print the fixed numbers and a forced comparison reds on success
    # -- while a few instruments are MAINTAINED (their keepers re-record
    # the header as the tree moves: claims.py, the D6-03 doc probe). The
    # marker makes that convention executable: a seat that re-records a
    # header as part of a fix marks the harness live, and from then on the
    # gate notices the next drift itself.
    #
    # THE WHOLE FILE, NOT A WINDOW (#1148). This read used to be
    # `p.read_text()[:4000]`, and the marker is the LAST line of a header
    # that grows: claims.py -- the harness this comment names first --
    # declared `live-header` at byte 3501 on 2026-09-15's merge and at 5224
    # on 2026-09-17's, so the check silently stopped executing the one
    # instrument it was written for, on a commit that never touched the
    # marker. It went unnoticed for the same reason it is a defect: the
    # gate stayed GREEN, and a register drifted from its generator behind
    # it (nine rows at #1148's measurement). The window was also measured
    # to buy nothing -- 7.1 ms median reading whole files against 8.2 ms
    # capped, over the 214-file corpus, because the read dominates and the
    # slice only adds work.
    live = {
        "tools/audit/round3/D2/dst_window_factors.py",
        "tools/audit/round3/D2/window_size_sweep.py",
        "tools/audit/round3/D5/option_doc_coverage.py",
    }
    marked = tuple(
        sorted(
            str(p.relative_to(ROOT))
            for p in (ROOT / "tools" / "audit").glob("round*/D*/*.py")
            if p.name != "__init__.py"
            and "live-header" in p.read_text()
            and p.relative_to(ROOT).as_posix() not in live
        )
    )
    return tuple(sorted(live)) + marked


# The directories the executed harnesses WRITE into. A generator whose output
# disagrees with what is committed is a stale register BY CONSTRUCTION, and this
# is the arm that catches it (#1148): regenerating the D6 register moves nine
# rows, and C125's `36 selects` moves NO header aggregate, so the header
# comparison in main() cannot see it -- the RCA that proposed this arm measured
# exactly that instance. One `git status` over the generators' own output is
# the whole check; no per-generator wiring, no threshold.
#
# NOT the whole tree. This script is `run_always`, so it runs in a seat's
# worktree, where uncommitted work is the ordinary state; a check that reds on
# every dirty tree is one a seat learns to route around -- and a seat that
# routes around this one loses the header comparison with it.
REGISTER_DIRS = ("tools/audit/round4/D6",)


def dirty_registers() -> tuple[bool, str]:
    """``(clean, detail)`` for the committed output of the executed harnesses."""
    p = subprocess.run(
        ["git", "status", "--porcelain", "--", *REGISTER_DIRS],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        # FAIL CLOSED. An unreadable status is not a pass: "I could not ask"
        # and "nothing here is dirty" leave the same empty stdout behind.
        return False, f"git status failed rc={p.returncode}: {p.stderr.strip()[-200:]}"
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    return (not lines), "clean" if not lines else "uncommitted: " + "; ".join(lines)


def declared_live() -> list[str]:
    """Every harness in the corpus that declares ``live-header`` ANYWHERE.

    Written as an independent re-derivation of the corpus, deliberately not by
    calling the predicate ``_discover()`` uses: the discovery carried a 4000-byte
    window, and a file whose header grew past it left the executed set with the
    marker still in place and nothing reporting it (#1148 -- measured: the
    marker sat at byte 3501 on 2026-09-15's merge and at 5224 on 2026-09-17's,
    so the check silently stopped executing claims.py between the two, on a
    commit that never touched the marker).
    """
    return sorted(
        str(p.relative_to(ROOT))
        for p in (ROOT / "tools" / "audit").glob("round*/D*/*.py")
        if p.name != "__init__.py" and "live-header" in p.read_text()
    )


def printed_from(stdout: str) -> dict[str, str]:
    found = {}
    for line in stdout.splitlines():
        m = RESULT.search(line)
        if m and m.group(1) not in SKIP:
            found[m.group(1)] = m.group(2)
    return found


# The hang bound is CPU seconds, not wall seconds (F10.11). The harness that
# runs longest, tools/audit/round4/D7/sysid_estimator_frontier.py, costs about
# 100 CPU-s on one core; a wall-clock bound of 240 s sat at 2.4x that, and the
# mutation lane's parallel pool (four trees, four drivers) stretched it past
# 240 s of wall without it doing any more work: the TimeoutExpired crashed this
# script and "killed" the comment-only null control, refusing the table on #1808
# twice. A CPU limit does not move with machine load, and keeps hang detection
# for a spinning harness at the same 240 s. A harness blocked on I/O spends no
# CPU, so the wall cap below is what bounds that one, sized for the slowest
# runner under the pool, below mutation_table.py's 1200 s per-driver timeout.
CPU_LIMIT_S = 240
WALL_LIMIT_S = 900
CPU_HEADROOM = 0.5


# RLIMIT_CPU sums the CPU of every thread, so a BLAS pool of N threads spends the
# limit N times as fast as the work it does: the frontier harness passed in 260 s
# of wall on one runner and was SIGXCPU'd at 293 s on another (mutation-nightly,
# run 37050037132). Every child runs single-threaded, here, whatever its caller's
# env or the workflow step says, so one place owns the pin.
BLAS_THREAD_PINS = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
}


def _children_cpu_s() -> float:
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    return ru.ru_utime + ru.ru_stime


def run_bounded(cmd: list[str], env: dict[str, str], cpu_s: int, wall_s: int):
    """``(returncode, stdout, stderr, cpu_used_s)``; rc -9/-24 is the kernel's
    SIGKILL/SIGXCPU on the CPU limit, and a wall overrun returns rc 124 and says
    so on stderr. ``cpu_used_s`` is the reaped child's own CPU, killed or not."""
    env = {**env, **BLAS_THREAD_PINS}

    def limit() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s + 5))

    before = _children_cpu_s()
    try:
        p = subprocess.run(
            cmd, cwd=ROOT, env=env, shell=False, capture_output=True, text=True,
            timeout=wall_s, preexec_fn=limit,
        )
    except subprocess.TimeoutExpired:
        return 124, "", f"wall limit {wall_s}s exceeded", _children_cpu_s() - before
    return p.returncode, p.stdout, p.stderr, _children_cpu_s() - before


def run_harness(rel: str) -> str:
    env = dict(os.environ)
    env["PYTHONPATH"] = "tests/hastub:custom_components:tests"
    rc, stdout, stderr, cpu = run_bounded(
        [sys.executable, rel], env, CPU_LIMIT_S, WALL_LIMIT_S
    )
    # A child the kernel kills on RLIMIT_CPU prints nothing of its own (run
    # 37108891698: `rc=-24 stderr=`), so the bound names itself and the CPU the
    # child had spent; every child's cost is printed, killed or not.
    print(f"  {rel}: cpu={cpu:.1f}s of the {CPU_LIMIT_S}s bound")
    why = {-24: f"SIGXCPU: the {CPU_LIMIT_S} CPU-s bound was spent",
           -9: f"SIGKILL: past the {CPU_LIMIT_S} CPU-s bound's hard limit"}
    R.check(
        f"{rel} exits 0",
        rc == 0,
        f"rc={rc} {why.get(rc, '')} cpu={cpu:.1f}s stderr={stderr[-300:]}",
    )
    # The bound is a hang detector, so a harness doing its ordinary work must
    # sit far below it; this reds on the cost, with the number, before the
    # kernel kills on it without one.
    R.check(
        f"{rel} costs at most {CPU_HEADROOM:.0%} of the CPU bound",
        cpu <= CPU_LIMIT_S * CPU_HEADROOM,
        f"cpu={cpu:.1f}s against {CPU_LIMIT_S * CPU_HEADROOM:.0f}s "
        f"({CPU_HEADROOM:.0%} of the {CPU_LIMIT_S}s bound)",
    )
    return stdout


def main() -> int:
    # Discovered here, not at import: tools/audit/judge_batch.py imports this
    # module for header_lines/expected_from, and a discovery at import would
    # put the whole harness corpus in every importer's measured closure.
    EXECUTE = _discover()
    declared = declared_live()
    R.check(
        "every harness declaring live-header anywhere in its file is executed",
        set(declared) <= set(EXECUTE),
        "declares the marker and is not executed: "
        + ", ".join(sorted(set(declared) - set(EXECUTE))),
    )
    for rel in EXECUTE:
        path = ROOT / rel
        R.check(f"{rel} exists", path.is_file(), rel)
        exp = expected_from(path)
        R.check(
            f"{rel} header names at least one EXPECTED RESULT",
            bool(exp),
            "header has no RESULT name=value the checker can execute",
        )
        out = run_harness(rel)
        got = printed_from(out)
        for name, want in exp.items():
            R.check(
                f"{rel} RESULT {name} matches header",
                got.get(name) == want,
                f"header={want!r} printed={got.get(name)!r}",
            )
    # The bound's own controls, seconds each: a child that idles past the CPU
    # limit is NOT killed (load cannot kill a harness that does no work), a
    # spinning child is, and an idle child past the wall cap reports 124.
    env = dict(os.environ)
    idle = [sys.executable, "-c", "import time; time.sleep(3)"]
    spin = [sys.executable, "-c", "while True: pass"]
    R.check("an idle child past the CPU limit is not killed by it",
            run_bounded(idle, env, 1, 30)[0] == 0, "load-independence lost")
    R.check("a spinning child is killed at the CPU limit",
            run_bounded(spin, env, 1, 30)[0] < 0, "hang detection lost")
    R.check("an idle child past the wall cap reports 124",
            run_bounded(idle, env, 30, 1)[0] == 124, "wall cap lost")
    # The children carry the BLAS thread pins whatever the caller's env says:
    # RLIMIT_CPU sums every thread, so an unpinned BLAS pool bills N threads'
    # CPU against the one limit (rc=-24 on the frontier harness, run 37050037132).
    names = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
    echo = [sys.executable, "-c",
            f"import os;print(*(os.environ.get(k, '') for k in {names!r}))"]
    rc, out, _, _ = run_bounded(echo, {**env, **dict.fromkeys(names, "8")}, 30, 30)
    R.check("a bounded child runs with every BLAS pool pinned to one thread",
            rc == 0 and out.split() == ["1", "1", "1"],
            f"rc={rc} OMP/OPENBLAS/MKL={out.split()!r}")
    clean, detail = dirty_registers()
    R.check(
        "the executed harnesses leave their committed output byte-identical",
        clean,
        detail,
    )
    return R.close("HARNESS HEADER CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
