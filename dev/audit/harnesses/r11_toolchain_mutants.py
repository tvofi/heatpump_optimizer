#!/usr/bin/env python3
"""R11-PRE-TOOLCHAIN-PIN: each rule of the stable tools ref dies alone.

Each mutant is one exact one-occurrence replacement in a COPY of tools/
(never the tree); the mutated file's own `--self-test` is then run in the copy
and must FAIL. Null control: M0 of each file, nothing mutated, must print
failed=0. A pattern not found exactly once aborts.

tools/audit/seat/toolchain.py:
  M-absent-behind   behind no longer refuses an absent ref.
  M-paths           behind counts every commit, not the seat paths.
  M-from            behind ignores --from.
  M-fetch           behind --fetch reads nothing from origin.
  M-direction       behind counts what the checkout holds over the ref.
  M-absent-promote  promote with no ref and no --init goes on.
  M-init-present    --init is accepted while the ref exists.
  M-offmain         a commit not on origin/main may be promoted.
  M-ff              the fast-forward refusal is dropped (git's own push refusal then answers).
  M-green-sha       promote <sha> no longer needs MACHINERY green.
  M-green-walk      the walk takes its first concluded run, whatever it reads.
  M-concluded       the walk reads a run that has not concluded.
  M-stop-at-ref     the walk reads runs the ref already holds.
  M-machinery       promotion reads PRODUCT, not MACHINERY.
  M-held-count      one bad run is a hold.
  M-held-any        a hold needs only one bad run among the newest three.
  M-readback        a push that moved nothing is believed.
  M-current-sha     promote <sha> at the ref's own commit is not CURRENT.
  M-sha-filter      promote <sha> trusts the listing's head_sha filter.
tools/audit/seat/prune_refs.py:
  M-keep            the toolchain/* keep is dropped: the merged-ref rule deletes the tools ref.
tools/ci/gate.py:
  G-empty           the machinery tuple is empty.
  G-unread-green    an unread verdict reads green.
  G-skip-required   a skipped required member is not red.
  G-cancelled-red   a cancelled member is red, not unread.
  G-na              a skipped instrument-self-tests is read, not set aside.
  G-neither         one required name is in neither verdict.
tools/audit/seat/cloud_dispatch.py (carry 10: the payload names the approved design):
  D-design-line     a fixer's payload names no design.
  D-part-clause     a part's design line says nothing of the two cuts.
  D-part-always     an unsplit group's design line speaks of parts.
  D-order           the design line follows the part line.
  D-stale-approval  an approval of a design that has since moved is one.
  D-no-verdict      a design with no verdict ref reads the verdict fetched last.
tools/audit/seat/cloud-setup.sh (carry 11: a check read under each kernel class):
  K-pin-kept        --kernels runs the command under the seat's pinned class every time.
  K-probe           a class OpenBLAS does not load is run and counted.
  K-red             a red class is not counted red.
  K-none            no class run exits 0.
  K-list            KERNELS is the pinned class alone.

    python3 dev/audit/harnesses/r11_toolchain_mutants.py

EXPECTED RESULT mutants=37
EXPECTED RESULT survived=0
"""
from __future__ import annotations

import shutil
import subprocess
import sys
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
TOOLCHAIN, PRUNE, GATE = "tools/audit/seat/toolchain.py", "tools/audit/seat/prune_refs.py", "tools/ci/gate.py"
DISPATCH, SETUP = "tools/audit/seat/cloud_dispatch.py", "tools/audit/seat/cloud-setup.sh"
#: What a copy holds: the targets' own directories and what their self-tests read (`bus.sh`, which
#: the dispatcher's reviewer path runs, refuses without `tools/pr`'s poster beside it).
COPIED = ("tools/audit/seat", "tools/ci", "tools/policy", "tools/pr", "tests/throwaway_git.py", "tests/throwaway_git.sh",
          "tests/closures.json", ".github/workflows")
#: A plant is (file, old, new).
PLANTS = {
    "M-absent-behind": (TOOLCHAIN, '    if git("rev-parse", "-q", "--verify", f"{TRACKING}^{{commit}}")[0]:\n', "    if False:\n"),
    "M-paths": (TOOLCHAIN, '*(() if every else ("--", *SEAT_PATHS)))', "*())"),
    "M-from": (TOOLCHAIN, 'f"{frm}..{TRACKING}", *', 'f"HEAD..{TRACKING}", *'),
    "M-fetch": (TOOLCHAIN, "    if fetch:\n", "    if False:\n"),
    "M-direction": (TOOLCHAIN, 'f"{frm}..{TRACKING}", *', 'f"{TRACKING}..{frm}", *'),
    "M-absent-promote": (TOOLCHAIN, "    if not old and not create:\n", "    if False:\n"),
    "M-init-present": (TOOLCHAIN, "    if old and create:\n", "    if False:\n"),
    "M-offmain": (TOOLCHAIN, '        if not SHA.fullmatch(new) or not ok("merge-base", "--is-ancestor", new, f"origin/{BASE}"):\n',
                  "        if not SHA.fullmatch(new):\n"),
    "M-ff": (TOOLCHAIN, '        if old and not ok("merge-base", "--is-ancestor", old, new):\n', "        if False:\n"),
    "M-green-sha": (TOOLCHAIN, "        if v != gate_py().GREEN:\n", "        if False:\n"),
    "M-green-walk": (TOOLCHAIN, "        if v == gate_py().GREEN:\n", "        if True:\n"),
    "M-concluded": (TOOLCHAIN, '    for run in [r for r in runs if r.get("status") == "completed"][:SCAN_RUNS]:\n',
                    "    for run in runs[:SCAN_RUNS]:\n"),
    "M-stop-at-ref": (TOOLCHAIN, '        if at_or_behind(run.get("head_sha") or ""):\n', "        if False:\n"),
    "M-machinery": (TOOLCHAIN, 'for j in jobs}, "push")[1]', 'for j in jobs}, "push")[0]'),
    "M-held-count": (TOOLCHAIN, "    return len(read) >= HELD_RUNS and all(", "    return len(read) >= 1 and all("),
    "M-held-any": (TOOLCHAIN, "HELD_RUNS and all(v != gate_py().GREEN", "HELD_RUNS and any(v != gate_py().GREEN"),
    "M-readback": (TOOLCHAIN, "        if rc or listed.split()[:1] != [new]:\n", "        if rc:\n"),
    "M-current-sha": (TOOLCHAIN, "    if sha == old and sha:\n", "    if False:\n"),
    "M-sha-filter": (TOOLCHAIN, ' and r.get("head_sha") == sha]', "]"),
    "M-keep": (PRUNE, "    if name == MAIN_REF or name.startswith(TOOLCHAIN_PREFIX):\n", "    if name == MAIN_REF:\n"),
    "G-empty": (GATE, 'MACHINERY_JOBS = ("tests / arch-instrument", "tests / briefs", "tests / closures", "governance / policy-docs",\n'
                      '                  "governance / wave-script", "governance / env-matrix", "governance / instrument-self-tests")\n',
                "MACHINERY_JOBS = ()\n"),
    "G-unread-green": (GATE, 'j[1] == "success" for j in ran) else UNREAD\n', 'j[1] == "success" for j in ran) else GREEN\n'),
    "G-skip-required": (GATE, "               if n in REQUIRED[cls] or (jobs.get(n)", "               if (jobs.get(n)"),
    "G-cancelled-red": (GATE, 'j[1] not in ("success", "cancelled") for j in ran)', 'j[1] not in ("success",) for j in ran)'),
    "G-na": (GATE, '(jobs.get(n) or ("", ""))[1] != "skipped"]', "True]"),
    "G-neither": (GATE, "    return verdict([n for n in REQUIRED[cls] if n not in MACHINERY_JOBS]), verdict(MACHINERY_JOBS)\n",
                  "    return verdict([n for n in REQUIRED[cls] if n not in MACHINERY_JOBS][1:]), verdict(MACHINERY_JOBS)\n"),
    "D-design-line": (DISPATCH, "        dline = design_line(group_id, approved, bool(pline))\n", '        dline = ""\n'),
    "D-part-clause": (DISPATCH, '    if part:\n        line += (" Its parts', '    if False:\n        line += (" Its parts'),
    "D-part-always": (DISPATCH, '    if part:\n        line += (" Its parts', '    if True:\n        line += (" Its parts'),
    "D-order": (DISPATCH, "for ln in (dline, pline) if ln),", "for ln in (pline, dline) if ln),"),
    "D-stale-approval": (DISPATCH, '    return tip if first == f"Design review: approve {tip}" else ""\n', "    return tip\n"),
    "D-no-verdict": (DISPATCH, '    if not _git(repo_dir, "ls-remote", "origin", vref).split():\n        return ""\n',
                     '    if not _git(repo_dir, "ls-remote", "origin", vref).split():\n        pass\n'),
    "K-pin-kept": (SETUP, '    rc=0; OPENBLAS_CORETYPE=$k "$@" || rc=$?\n', '    rc=0; "$@" || rc=$?\n'),
    "K-probe": (SETUP, '    if [ "$got" != "$k" ]; then\n', "    if false; then\n"),
    "K-red": (SETUP, '    ran="$ran $k"; [ "$rc" = 0 ] || red="$red $k"\n', '    ran="$ran $k"\n'),
    "K-none": (SETUP, '  [ -n "$ran" ] || return 2\n', ""),
    "K-list": (SETUP, 'KERNELS="SkylakeX Haswell Sandybridge Nehalem"\n', 'KERNELS="Haswell"\n'),
}


def selftest(tree: Path, target: str) -> tuple:
    run = ["bash"] if target.endswith(".sh") else [sys.executable, "-I"]
    r = subprocess.run([*run, str(tree / target), "--self-test"], capture_output=True, text=True)
    out = r.stdout + r.stderr
    return r.returncode, sum(1 for ln in out.splitlines() if ln.lstrip().startswith("FAIL"))


def copy(tmp: str, name: str) -> Path:
    tree = Path(tmp) / name
    for rel in COPIED:
        src, dst = ROOT / rel, tree / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if src.is_dir() else shutil.copy)(src, dst)
    return tree


def main() -> int:
    survived = 0
    with tempfile.TemporaryDirectory() as tmp:
        for target in (TOOLCHAIN, PRUNE, GATE, DISPATCH, SETUP):
            rc, failed = selftest(copy(tmp, "M0-" + Path(target).stem), target)
            print(f"RESULT mutant=M0 file={target} failed={failed} verdict={'null-ok' if rc == 0 and not failed else 'NULL-RED'}")
            if rc or failed:
                return 2
        for name, (target, old, new) in PLANTS.items():
            tree = copy(tmp, name)
            p = tree / target
            s = p.read_text()
            if s.count(old) != 1:
                print(f"ABORT {name}: pattern occurs {s.count(old)} times")
                return 2
            p.write_text(s.replace(old, new))
            rc, failed = selftest(tree, target)
            dead = rc != 0 and failed > 0
            survived += not dead
            print(f"RESULT mutant={name} failed={failed} verdict={'killed' if dead else 'SURVIVED'}")
            shutil.rmtree(tree)
    print(f"RESULT mutants={len(PLANTS)}")
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
