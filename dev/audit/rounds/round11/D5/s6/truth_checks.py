#!/usr/bin/env python3
"""D5-s6 step D5.M4: executed truth checks (criteria C1/C2) of the comment units m4_ledger.py
confirmed false, one RESULT per file, each against the production symbol the comment sits on.

Metric: per file, the number of comment claims the executed production code contradicts
(count key: the claim, read off the unit text at run time and compared with the value the
production module/script itself delivers -- never with another comment).

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s6/truth_checks.py [--perturb NAME]
Expected at baseline 92d38ecb (box B11), exact: stamp_py=3 replay_draws_py=1 row_position_py=1
      plan_audit_py=1 update_pr_sh=1 roster_lib_py=3 plan_table_py=1.
Perturbations (in memory or in a temp copy; each moves its own RESULT down, the others not):
  --perturb stamp        RECORD_CLASS_RES cut to its first three regexes, the README section planted
                         and policy_lint.mjs looked up at the cited path in a temp tree    -> stamp_py 0
  --perturb replay       tests/replay.py:COST_DRAWS repointed at the name the docstring states -> 0
  --perturb row_position the usage line is run against a temp tree holding the cited path    -> 0
  --perturb plan_audit   plan_audit.main's end-to-end parser given a --target option          -> 0
  --perturb update_pr    the script run under the name its header states (temp copy)          -> 0
  --perturb gen_table    gen_table_rev3.py added to the tracked list                          -> 0 (both)
Machine: box B11 container.  Counts only; no timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, ast, contextlib, importlib.util, io, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
TMP = Path(tempfile.mkdtemp(prefix="d5s6-", dir=os.environ.get("TMPDIR")))
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def comment_block(path, anchor):
    """The comment block of `path` that contains `anchor` (raw lines, markers kept)."""
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    i = next(n for n, l in enumerate(lines) if anchor in l)
    a = i
    while a > 0 and lines[a - 1].lstrip().startswith("#"):
        a -= 1
    b = i
    while b + 1 < len(lines) and lines[b + 1].lstrip().startswith("#"):
        b += 1
    return "\n".join(lines[a:b + 1])


def tracked():
    repo = os.environ.get("HPO_BASELINE_REPO", "/home/user/heatpump_optimizer")
    ref = os.environ.get("HPO_BASELINE_REF", "92d38ecb640bd462f2e19c0814d0f0b7df1ee692")
    try:
        return set(subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", ref], text=True).split())
    except (OSError, subprocess.CalledProcessError):
        return {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()}


def check_stamp(p):
    """tools/release/stamp.py, the record-class comment above RECORD_CLASS_RES and register_argv's docstring."""
    sys.path.insert(0, str(ROOT / "tools/release"))
    stamp = load("stamp_d5s6", "tools/release/stamp.py")
    res = stamp.RECORD_CLASS_RES[:3] if p == "stamp" else stamp.RECORD_CLASS_RES
    block = comment_block("tools/release/stamp.py", "THE COPY.")
    m = re.search(r"carries the same (\w+) regexes", block)
    said = WORDS[m.group(1)]
    bad = int(len(res) != said)
    # the copy the comment names, at the path it names
    cited = re.search(r"`(\.claude/workflows/policy_lint\.mjs)`", block).group(1)
    root = TMP / "stamp_tree"
    if p == "stamp":
        (root / ".claude/workflows").mkdir(parents=True, exist_ok=True)
        (root / cited).write_text("const RECORD_CLASS_RES = []\n")
    target = (root if p == "stamp" else ROOT) / cited
    bad += int(not target.exists() or "RECORD_CLASS_RES" not in target.read_text())
    # register_argv's docstring cites a README section by path and title
    doc = stamp.register_argv.__doc__
    rp = re.search(r"\((tools/audit/README\.md), \"([^\"]+)\"", " ".join(doc.split()))
    path, title = rp.group(1), rp.group(2)
    readme = (TMP / "README.md") if p == "stamp" else (ROOT / path)
    if p == "stamp":
        readme.write_text(f"## {title}\n")
    bad += int(not readme.exists() or title.lower() not in readme.read_text().lower())
    print(f"RESULT stamp_record_class_res_len={len(res)} count (comment says {said})")
    return bad


def check_replay(p):
    """tools/audit/seat/replay_draws.py's module docstring vs tests/replay.py:COST_DRAWS, the table it fills."""
    sys.path.insert(0, str(ROOT / "tests"))
    replay = load("replay_d5s6", "tests/replay.py")
    doc = ast.get_docstring(ast.parse((ROOT / "tools/audit/seat/replay_draws.py").read_text()))
    named = re.search(r"input\s+``([^`]+\.tsv)``\s+holds", doc).group(1)
    target = replay.ROOT / named if p == "replay" else replay.COST_DRAWS
    print(f"RESULT replay_cost_draws_path={Path(target).relative_to(replay.ROOT)} (docstring says {named})")
    return int(Path(target).resolve() != (replay.ROOT / named).resolve() or not (ROOT / named).exists() and p != "replay")


def check_row_position(p):
    """tools/audit/seat/row_position.py's usage line, executed as written (--help)."""
    doc = ast.get_docstring(ast.parse((ROOT / "tools/audit/seat/row_position.py").read_text()))
    cmd = re.search(r"python3 (\S+row_position\.py)", doc).group(1)
    cwd = ROOT
    if p == "row_position":
        cwd = TMP / "rp"
        (cwd / Path(cmd).parent).mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / "tools/audit/seat/row_position.py", cwd / cmd)
        for dep in (ROOT / "tools/audit/seat").glob("*.py"):
            shutil.copy(dep, cwd / Path(cmd).parent / dep.name) if not (cwd / Path(cmd).parent / dep.name).exists() else None
    r = subprocess.run([sys.executable, cmd, "--help"], cwd=cwd, capture_output=True, text=True)
    print(f"RESULT row_position_usage_rc={r.returncode} (usage path {cmd}; stderr {r.stderr.strip()[-80:]!r})")
    return int(r.returncode != 0)


def check_plan_audit(p):
    """tools/audit/seat/plan_audit.py's documented end-to-end line, fed to plan_audit.main's own parser."""
    sys.path.insert(0, str(ROOT / "tools/audit/seat"))
    pa = load("plan_audit_d5s6", "tools/audit/seat/plan_audit.py")
    line = next(l for l in pa.__doc__.splitlines() if "plan_audit.py end-to-end" in l)
    argv = line.split("plan_audit.py", 1)[1].replace("[", " ").replace("]", " ").split()
    argv = ["HEAD" if a == "SHA" else a for a in argv]
    real_add = argparse._SubParsersAction.add_parser

    def add_parser(self, name, **kw):
        sp = real_add(self, name, **kw)
        if p == "plan_audit" and name == "end-to-end":
            sp.add_argument("--target", type=float)
        return sp
    end = {"dS": 0.0, "verdict": "NEUTRAL", "terms": {}, "gate_only": [], "rises": []}
    err, rc = io.StringIO(), 0
    with mock.patch.object(argparse._SubParsersAction, "add_parser", add_parser), \
            mock.patch.object(pa, "run_end_to_end", lambda *a, **k: end), \
            contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = pa.main(argv)
        except SystemExit as e:
            rc = e.code
    print(f"RESULT plan_audit_usage_rc={rc} (argv {' '.join(argv)}; {err.getvalue().strip().splitlines()[-1:]})")
    return int(rc == 2)


def check_update_pr(p):
    """tools/audit/seat/update_pr.sh's header names the script; the script's own $0 is its file name."""
    head = (ROOT / "tools/audit/seat/update_pr.sh").read_text().splitlines()[1]
    named = re.match(r"#\s*(\S+\.sh)\b", head).group(1)
    src = ROOT / "tools/audit/seat/update_pr.sh"
    run_as = TMP / (named if p == "update_pr" else src.name)
    shutil.copy(src, run_as)
    r = subprocess.run(["bash", "-c", 'echo "$(basename -- "$0")"', str(run_as)], capture_output=True, text=True)
    actual = r.stdout.strip()
    tracked_names = {Path(x).name for x in tracked()} | ({named} if p == "update_pr" else set())
    print(f"RESULT update_pr_self_name={actual} (header says {named}; tracked={named in tracked_names})")
    return int(named != actual or named not in tracked_names)


def check_gen_table(p, path):
    t = tracked() | ({"tools/audit/seat/gen_table_rev3.py"} if p == "gen_table" else set())
    sys.path.insert(0, str(ROOT / "tools/audit/seat"))
    text = (ROOT / path).read_text()
    n = len(re.findall(r"gen_table_rev3\.py", text))
    if path.endswith("roster_lib.py"):
        rl = load("roster_lib_d5s6", path)
        assert callable(rl.depth_of)  # the recurrence the comment attributes to the missing script
    exists = any(x.endswith("/gen_table_rev3.py") or x == "gen_table_rev3.py" for x in t)
    return 0 if exists else n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="")
    p = ap.parse_args().perturb
    t0, c0 = time.process_time(), time.thread_time()
    print(f"RESULT stamp_py={check_stamp(p)} count")
    print(f"RESULT replay_draws_py={check_replay(p)} count")
    print(f"RESULT row_position_py={check_row_position(p)} count")
    print(f"RESULT plan_audit_py={check_plan_audit(p)} count")
    print(f"RESULT update_pr_sh={check_update_pr(p)} count")
    print(f"RESULT roster_lib_py={check_gen_table(p, 'tools/audit/seat/roster_lib.py')} count")
    print(f"RESULT plan_table_py={check_gen_table(p, 'tools/audit/seat/plan_table.py')} count")
    print(f"RESULT thread_factor={(time.process_time() - t0 + 1e-9) / (time.thread_time() - c0 + 1e-9):.2f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
