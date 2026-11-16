#!/usr/bin/env python3
"""D6-s5 M2: one executed check per hand-selected claim of the seat's cells, against the code deciding it.

Metric: per checked unit, the verdict of an executed check against the production symbol that
decides the claim (true / false / stale / unverifiable); RESULT false_or_stale_<file> counts the
units of one document whose stated fact the executed code contradicts.  Count key: the value the
production seam delivers (gate_lock.needs_lease's answer, closure.is_handover's set, brief_lint's
symbolInTree answer, the script's own refusal), never the document's wording.

Command (from the export root; --repo is the clone holding the baseline commit):
  PYTHONPATH=tests/hastub PYTHONUTF8=1 ~/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s5/claims.py \
      --repo /home/user/heatpump_optimizer [--ref 92d38ecb...] [--rows OUT.tsv] [--perturb NAME]
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B13): the RESULT lines REPORT.md
records, exact (counts).
Perturbations (--perturb, each in memory or in this harness's own temp tree; direction to_zero
for its file's false_or_stale count):
  mock_suite        tests/*.py restricted to the one script the README names -> mock_users 5 -> 1
  needs_lease       gate_lock.MACHINE_MEASURING = ("tests/stress.py",), every recorded time 0 s
                    -> leased_or_slotted_besides_stress goes to 0
  handover_docs     closure.HANDOVER_DIRS = ("docs/",) with the handover at docs/HANDOVER.md
  brief_exclude     temp tree's brief_lint.mjs SYMBOL_GREP_EXCLUDE gains ':!tools/audit/round2'
  worktree_apply    temp tree's worktree_gc.sh accepts --apply as a no-op
  instruments_dirs  temp tree gets the record directories INSTRUMENTS.md lists under tools/audit/seat/
  event_hub         look up the harness's actual basename instead of the cited one -> files 0 -> 1 (up)
  round4_d6         closure.INERT_EXCEPT's round4/D6 entries respelled at tools/audit/round4/D6/
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, ast, atexit, importlib, json, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402

SHA = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
ARGS = None
_TREE = {}


def base_tree():
    """A clean temp tree of the baseline commit (git archive), a git repo of its own."""
    if "p" not in _TREE:
        d = tempfile.mkdtemp(prefix="d6s5-", dir=os.environ.get("TMPDIR"))
        atexit.register(shutil.rmtree, d, True)
        arch = subprocess.run(["git", "-C", ARGS.repo, "archive", ARGS.ref], capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", d], input=arch, check=True)
        for c in (["init", "-q"], ["add", "-A"], ["-c", "user.email=s@x", "-c", "user.name=s", "commit", "-qm", "b"]):
            subprocess.run(["git", "-C", d, *c], check=True, capture_output=True)
        _TREE["p"] = d
    return _TREE["p"]


def sh(cmd, cwd=None, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env={**os.environ, **(env or {})}, timeout=1200)
    return r.returncode, (r.stdout + r.stderr)


def scripts():
    """The suite as the gate enumerates it: closure.test_scripts()."""
    import closure
    return closure.test_scripts()


# ---- the checks: each returns (command, result, verdict, truth) -------------------------------

def c_mock():
    users = []
    for s in [x for x in scripts() if x.endswith(".py")]:
        if ARGS.perturb == "mock_suite" and s != "tests/optimality.py":
            continue
        tree = ast.parse(Path(s).read_text())
        if any(isinstance(n, ast.ImportFrom) and n.module == "unittest" and any(a.name == "mock" for a in n.names)
               or isinstance(n, ast.Import) and any(a.name == "unittest.mock" for a in n.names) for n in ast.walk(tree)):
            users.append(s)
    RES["mock_users"] = len(users)
    ok = users == ["tests/optimality.py"]
    return ("ast over closure.test_scripts() .py entries: modules importing unittest.mock", f"{len(users)}: {', '.join(users)}",
            "true" if ok else "false", "" if ok else f"{len(users)} suite scripts use unittest.mock: {', '.join(users)}")


def _needs(script):
    import gate_lock
    with tempfile.NamedTemporaryFile("w", suffix=".scope", delete=False) as f:
        f.write(script + "\n")
    try:
        return gate_lock.needs_lease(f.name)
    finally:
        os.unlink(f.name)


def c_unleased():
    import gate_lock
    if ARGS.perturb == "needs_lease":
        gate_lock.MACHINE_MEASURING = ("tests/stress.py",)
        gate_lock.SLOT_MIN_SECONDS = 10 ** 9
        gate_lock._recorded_seconds = lambda name: 0.0
    ans = {s: _needs(s) for s in scripts()}
    other = {s: a for s, a in ans.items() if s != "tests/stress.py" and a != "none"}
    RES["leased_or_slotted_besides_stress"] = len(other)
    lease = sorted(s for s, a in other.items() if a == "lease")
    slot = sorted(s for s, a in other.items() if a == "slot")
    return ("gate_lock.needs_lease(<scope file naming one script>) for every closure.test_scripts() entry",
            f"besides stress.py: lease={lease} slot={len(slot)} ({', '.join(slot[:6])}...)",
            "false" if other else "true",
            f"run.sh leases {len(lease)} other script(s) exclusively ({', '.join(lease)}) and runs {len(slot)} in the heavy slots; only scripts answering `none` run unleased" if other else "")


def c_measuring():
    import gate_lock
    a, b = _needs("tests/stress.py"), _needs("tests/harness_headers.py")
    ok = a == b == "lease" and gate_lock.HEAVY_SLOTS == 4 and gate_lock.SLOTS_ENV == "HPO_HEAVY_SLOTS"
    return ("gate_lock.needs_lease for stress.py and harness_headers.py; gate_lock.HEAVY_SLOTS, SLOTS_ENV",
            f"{a}, {b}; slots {gate_lock.HEAVY_SLOTS} via {gate_lock.SLOTS_ENV}", "true" if ok else "false", "" if ok else "differs")


def c_slots():
    import gate_lock
    ok = gate_lock.HEAVY_SLOTS == 4 and gate_lock.SLOTS_ENV == "HPO_HEAVY_SLOTS"
    return ("gate_lock.HEAVY_SLOTS, SLOTS_ENV", f"{gate_lock.HEAVY_SLOTS}, {gate_lock.SLOTS_ENV}", "true" if ok else "false", "" if ok else "differs")


def c_lease_minutes():
    import gate_lock
    ok = gate_lock.LEASE_SECONDS == 1800
    return ("gate_lock.LEASE_SECONDS", str(gate_lock.LEASE_SECONDS), "true" if ok else "false", "" if ok else "not 30 min")


def c_rcs():
    import gate_lock
    ok = gate_lock.RENEW_REFUSED_RC == 75 and gate_lock.WAIT_BOUND_RC == 76
    return ("gate_lock.RENEW_REFUSED_RC, WAIT_BOUND_RC", f"{gate_lock.RENEW_REFUSED_RC}, {gate_lock.WAIT_BOUND_RC}", "true" if ok else "false", "" if ok else "differs")


def c_lockdir():
    import gate_lock
    ok = str(gate_lock.DEFAULT_LOCK_DIR) == "/tmp/hpo-gate.lock" or bool(os.environ.get("HPO_GATE_LOCK_DIR"))
    return ("gate_lock.DEFAULT_LOCK_DIR", str(gate_lock.DEFAULT_LOCK_DIR), "true" if ok else "false", "" if ok else "differs")


def c_python_order():
    t = Path("tests/run.sh").read_text()
    ok = 'PYTHON="${PYTHON:-}"' in t and "if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=python3; fi" in t
    rc, out = sh(["bash", "-c", 'PYTHON=; if [ -z "$PYTHON" ]; then if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=python3; fi; fi; echo $PYTHON'])
    return ("tests/run.sh PYTHON fallback lines, executed", out.strip(), "true" if ok else "false", "" if ok else "fallback differs")


def c_scope_default():
    rc, out = sh(["bash", "-c", "unset GATE_SCOPE; " + next(l for l in Path("tests/run.sh").read_text().splitlines() if l.startswith('GATE_SCOPE="${GATE_SCOPE:-')) + "; echo $GATE_SCOPE"])
    ok = out.strip() == "full"
    return ("tests/run.sh GATE_SCOPE default line, executed", out.strip(), "true" if ok else "false", "" if ok else "default is not full")


def c_mode_lines():
    import closure
    src = Path(closure.__file__).read_text()
    ok = "MODE: FULL -- every test script runs" in src and "MODE: SCOPED -- {len(plan['run'])} script(s) run" in src
    return ("closure.py select's mode lines", "both present" if ok else "missing", "true" if ok else "false", "" if ok else "mode line differs")


def c_full_orphan():
    ok = "these force the FULL suite when touched" in Path("tests/entities.py").read_text()
    return ("grep tests/entities.py", "present" if ok else "absent", "true" if ok else "false", "" if ok else "message absent")


def c_budget_count():
    keys = [k for k in json.loads(Path("tests/structure_budgets.json").read_text()) if k != "recorded_at"]
    rc, out = sh([sys.executable, "tests/structure.py"], cwd=base_tree(), env={"PYTHONPATH": "tests/hastub", "PYTHONUTF8": "1"})
    oks = len(re.findall(r"^\s+ok\b", out, re.M))
    RES["structure_metrics"] = len(keys)
    RES["structure_ok_lines"] = oks
    ok = rc == 0 and oks != len(keys)
    return ("tests/structure.py in a clean baseline tree; budget keys less recorded_at", f"metrics={len(keys)} ok_lines={oks} rc={rc}",
            "true" if ok else "false", "" if ok else "counts equal or run failed")


def c_tables():
    claude = Path("CLAUDE.md").read_text()
    out = []
    rows = [l.split("|")[1] for l in claude.splitlines() if l.startswith("| `")]
    for d, pat in (("dev/governance/rules", r"`([\w-]+\.md)`"), ("dev/governance/roles", r"`([\w-]+\.md)`"),
                   ("dev/governance/dimensions", r"`(D\d+\.md)`")):
        files = {p.name for p in Path(base_tree(), d).glob("*.md")}
        named = {n for r in rows for n in re.findall(pat, r)}
        out.append(f"{d}: files={len(files)} unnamed={sorted(files - named)} named_missing={sorted(n for n in named if n not in files and Path(d, n).exists() is False and n in files)}")
    crit = {p.name for p in Path(base_tree(), "dev/governance/dimensions/criteria").glob("*.md")}
    named_c = set(re.findall(r"`(D\d+-criteria\.md)`", claude))
    out.append(f"criteria files={sorted(crit)} named={sorted(named_c)}")
    ok = all("unnamed=[]" in o for o in out[:3]) and crit == named_c
    return ("CLAUDE.md tables vs the baseline commit's dev/governance/{rules,roles,dimensions,dimensions/criteria}", " | ".join(out), "true" if ok else "false", "" if ok else "a policy file is not tabled")


def c_rules_sync():
    rc, out = sh(["node", "tools/policy/rules_sync.mjs", "--check"], cwd=base_tree())
    return ("node tools/policy/rules_sync.mjs --check", f"rc={rc} {out.strip()[:120]}", "true" if rc == 0 else "false", "" if rc == 0 else "drift")


def c_claimnotes():
    t = Path(base_tree(), ".gitattributes").read_text()
    ok = all(re.search(rf"^{re.escape(f)} merge=claimnotes$", t, re.M) for f in ("tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt"))
    rc, out = sh([sys.executable, "tests/env_drift.py", "--help"])
    flag = "--install-merge-driver" in Path("tests/env_drift.py").read_text()
    ok = ok and flag
    return (".gitattributes merge= lines; env_drift.py --install-merge-driver", f"routed={ok} flag={flag}", "true" if ok else "false", "" if ok else "not routed")


def c_main_guards():
    names = ["golden", "env_drift", "closure", "frontend", "manual_plan", "stress", "structure"]
    bad = [n for n in names if not any(isinstance(x, ast.If) and "__main__" in ast.unparse(x.test) for x in ast.parse(Path(f"tests/{n}.py").read_text()).body)]
    return ("ast: top-level `if __name__ == '__main__'` in each named script", f"without guard: {bad}", "true" if not bad else "false", "" if not bad else f"no guard: {bad}")


def c_import_exit():
    names = ["entities", "features", "rolling", "backtest", "optimality"]
    bad = []
    for n in names:
        body = ast.parse(Path(f"tests/{n}.py").read_text()).body
        guard = any(isinstance(x, ast.If) and "__main__" in ast.unparse(x.test) for x in body)
        exits = any("sys.exit" in ast.unparse(x) for x in body if not isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
        if guard or not exits:
            bad.append(n)
    return ("ast: no __main__ guard and a module-level sys.exit", f"not so: {bad}", "true" if not bad else "false", "" if not bad else f"{bad}")


def c_topologies():
    import golden
    names = list(golden.coordinator_scenarios())
    want = ["coord_minimal", "coord_dhw", "coord_two_zone", "coord_grid_fee", "coord_all_features"]
    ok = names == want
    return ("golden.coordinator_scenarios()", ", ".join(names), "true" if ok else "false", "" if ok else f"{names}")


def c_profiles():
    import profiles
    want_p = ["winter_typical", "winter_extreme", "summer_typical", "summer_negative", "shoulder", "winter_narrow", "winter_moderate", "flat"]
    want_w = ["winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder"]
    import datetime as dt
    start = dt.datetime(2026, 1, 5, tzinfo=dt.timezone.utc)
    def accepted(fn, name):
        try:
            a = fn(name, start)
        except Exception:
            return False
        try:
            b = fn("no_such_profile_d6s5", start)
        except Exception:
            return True
        return repr(a) != repr(b)
    bad = [p for p in want_p if not accepted(profiles.prices, p)] + [w for w in want_w if not accepted(profiles.weather, w)]
    return ("profiles.prices/weather(name) vs an unknown name", f"not accepted: {bad}", "true" if not bad else "false", "" if not bad else f"{bad}")


def c_slow_gated():
    import closure
    t = Path("tests/entities.py").read_text()
    hits = [l for l in t.splitlines() if "SLOW_GATED" in l and not l.strip().startswith("#")]
    asserting = [l for l in hits if "run.sh" in l or "SLOW=" in l]
    ok = not asserting
    return ("tests/entities.py code lines naming SLOW_GATED and run.sh", f"{len(hits)} code lines, {len(asserting)} asserting the run.sh gate; SLOW_GATED={sorted(closure.SLOW_GATED)}",
            "true" if ok else "false", "" if ok else "the assertion exists")


def c_gil():
    p = Path("custom_components/heatpump_optimizer/optimizer.py")
    tree = ast.parse(p.read_text())
    where = []
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("sleep") and n.args and ast.unparse(n.args[0]) == "0.002":
                    where.append(fn.name)
    inner = sorted(set(where))
    ok = {"_multi_start_minimize", "_lbfgsb_restart"} <= set(where) and len(where) == 3
    return ("ast over optimizer.py: enclosing defs of sleep(0.002)", f"{len(where)} calls in {inner}", "true" if ok else "false", "" if ok else f"{where}")


def c_judge_sha():
    r = subprocess.run(["git", "-C", ARGS.repo, "cat-file", "-e", "d5d8c4a72fa7be7aebecc9e58d55002be17cac08:tools/audit/round2/JUDGE.md"])
    ok = r.returncode == 0
    return ("git cat-file -e d5d8c4a:tools/audit/round2/JUDGE.md", f"rc={r.returncode}", "true" if ok else "false", "" if ok else "absent at the SHA")


def c_fix_review_j5():
    hits = [str(p) for p in Path("dev/governance").rglob("*.md") if "j5_gil" in p.read_text()]
    briefs = Path("briefs/fix-review.md").exists() or Path("tools/audit/briefs/fix-review.md").exists()
    RES["fix_review_j5_refs"] = len(hits)
    ok = briefs or bool(hits)
    return ("exists briefs/fix-review.md; grep j5_gil dev/governance/**.md", f"briefs/fix-review.md exists={briefs}; contracts naming j5_gil={hits}",
            "true" if ok else "stale", "" if ok else "there is no briefs/fix-review.md; dev/governance/roles/fix-review.md names no j5_gil.py, so no section 9 sends a reviewer to it")


def c_handover_docs():
    import closure
    files = [l for l in sh(["git", "-C", base_tree(), "ls-files"])[1].splitlines()]
    if ARGS.perturb == "handover_docs":
        closure.HANDOVER_DIRS = ("docs/",)
        files = [("docs/HANDOVER.md" if f == "dev/programme/HANDOVER.md" else f) for f in files]
    hand = sorted(f for f in files if closure.is_handover(f))
    under_docs = [f for f in hand if f.startswith("docs/")]
    RES["handovers_under_docs"] = len(under_docs)
    ok = len(under_docs) == 1
    return ("closure.is_handover over the baseline's tracked files", f"handovers={hand}; under docs/={under_docs}",
            "true" if ok else "false", "" if ok else f"entities.py requires exactly {hand} (closure.HANDOVER_DIRS={closure.HANDOVER_DIRS}); the one handover is dev/programme/HANDOVER.md, none is under docs/")


def c_brief_exclude():
    d = base_tree()
    for sub, sym in (("tools/audit/round2", "zzdsfive_probe_round2"), (".claude", "zzdsfive_probe_claude")):
        Path(d, sub).mkdir(parents=True, exist_ok=True)
        Path(d, sub, "d6s5_probe.md").write_text(f"{sym}\n")
    bl = Path(d, "tools/policy/brief_lint.mjs")
    orig = bl.read_text()
    if ARGS.perturb == "brief_exclude":
        bl.write_text(orig.replace("const SYMBOL_GREP_EXCLUDE = [':!.claude']", "const SYMBOL_GREP_EXCLUDE = [':!.claude', ':!tools/audit/round2']"))
    sh(["git", "-C", d, "add", "-A"])
    js = ("import('./tools/policy/brief_lint.mjs').then(m=>{console.log(JSON.stringify({round2:m.symbolInTree('zzdsfive_probe_round2'),"
          "claude:m.symbolInTree('zzdsfive_probe_claude')}))})")
    rc, out = sh(["node", "--input-type=module", "-e", js], cwd=d)
    bl.write_text(orig)
    try:
        got = json.loads(out.strip().splitlines()[-1])
    except Exception:
        got = {"round2": None, "claude": None}
    RES["round2_symbol_found"] = int(bool(got["round2"]))
    RES["claude_symbol_found_null_control"] = int(bool(got["claude"]))
    ok = got["round2"] is False
    return ("brief_lint.mjs symbolInTree on a symbol planted only under tools/audit/round2/ (and, as control, only under .claude/)", json.dumps(got),
            "true" if ok else "stale", "" if ok else "symbolInTree finds a symbol under tools/audit/round2/: SYMBOL_GREP_EXCLUDE is [':!.claude'] alone; the round2 entry was deleted")


def c_worktree_apply():
    d = base_tree()
    p = Path(d, "tools/audit/worktree_gc.sh")
    orig = p.read_text()
    if ARGS.perturb == "worktree_apply":
        p.write_text(orig.replace("    --keep-dir)", "    --apply) ;;\n    --keep-dir)", 1))
    rc, out = sh(["bash", "-c", "PATH=/nonexistent-gh:$PATH; bash tools/audit/worktree_gc.sh --apply --dry-run o/r </dev/null 2>&1 | head -3; exit ${PIPESTATUS[0]}"], cwd=d)
    p.write_text(orig)
    refused = "unknown option '--apply'" in out
    RES["worktree_gc_apply_refused"] = int(refused)
    return ("bash tools/audit/worktree_gc.sh --apply --dry-run o/r", f"rc={rc} {out.strip()[:120]}", "stale" if refused else "true",
            "worktree_gc.sh has no --apply: it REFUSEs it as an unknown option; collecting is its default and --dry-run the preview" if refused else "")


def c_instrument_dirs():
    t = Path("tools/audit/seat/INSTRUMENTS.md").read_text()
    m = re.search(r"Directories here that are records, not instruments:(.*?)\(sub-tools", t, re.S)
    listed = re.findall(r"`([\w*.-]+)/`", m.group(1))
    names = []
    for n in listed:
        if n == "round3":
            names += [f"round{i}" for i in range(3, 10)]
        elif n != "round9":
            names.append(n)
    seat = Path(base_tree(), "tools/audit/seat")
    if ARGS.perturb == "instruments_dirs":
        for n in names:
            (seat / n).mkdir(exist_ok=True)
    present = [n for n in names if (seat / n).is_dir()]
    RES["instrument_record_dirs_listed"] = len(names)
    RES["instrument_record_dirs_absent"] = len(names) - len(present)
    ok = len(present) == len(names)
    return ("is_dir tools/audit/seat/<each record directory INSTRUMENTS.md lists>", f"listed={len(names)} present={len(present)}",
            "true" if ok else "stale", "" if ok else f"{len(names) - len(present)} of {len(names)} listed record directories are not in tools/audit/seat/ (the records live under dev/audit/rounds/ and dev/governance/)")


def c_round4_d6():
    import closure
    inert = list(closure.INERT_EXCEPT)
    if ARGS.perturb == "round4_d6":
        inert = [x.replace("dev/audit/rounds/round4/D6/", "tools/audit/round4/D6/") for x in inert]
    rewritten = [x for x in inert if "round4/D6/" in x]
    at_doc = [x for x in rewritten if x.startswith("tools/audit/round4/D6/")]
    RES["round4_d6_rewritten_at_doc_path"] = len(at_doc)
    ok = bool(at_doc)
    return ("closure.INERT_EXCEPT entries for the claims harness the gate re-runs", f"{rewritten}", "true" if ok else "stale",
            "" if ok else "the gate's live-header check re-runs dev/audit/rounds/round4/D6/claims.py, which rewrites dev/audit/rounds/round4/D6/claims.{json,md}; tools/audit/round4/D6/ does not exist")


def c_event_hub():
    name = "r10_livestate_event_hub_writes.py" if ARGS.perturb == "event_hub" else "event_hub_writes.py"
    found = [l for l in sh(["git", "-C", ARGS.repo, "ls-tree", "-r", "--name-only", ARGS.ref])[1].splitlines() if l.rsplit("/", 1)[-1] == name]
    RES["event_hub_cited_name_files"] = len(found)
    exact = bool(found)
    near = sorted(str(p) for p in Path("dev/audit/harnesses").glob("*event_hub_writes*.py"))
    return ("find event_hub_writes.py", f"exact={exact} nearest={near}", "true" if exact else "stale",
            "" if exact else f"no file event_hub_writes.py; the control is {near}")


CHECKS = [
    ("dev/audit/README.md", "the third is the only `unittest.mock` use in the suite", c_mock),
    ("dev/audit/README.md", "`briefs/fix-review.md` §9 sends a fix reviewer to it", c_fix_review_j5),
    ("dev/audit/README.md", "`golden.py`, `env_drift.py`, `closure.py`, `frontend.py`, `manual_plan.py`", c_main_guards),
    ("dev/audit/README.md", "`entities.py`, `features.py`, `rolling.py`, `backtest.py` and", c_import_exit),
    ("dev/audit/README.md", "5 topologies (`coord_minimal`", c_topologies),
    ("dev/audit/README.md", "price profiles `winter_typical`", c_profiles),
    ("dev/audit/README.md", "comment places in", c_slow_gated),
    ("dev/audit/README.md", "GIL yields are its `sleep(0.002)` calls", c_gil),
    ("dev/audit/README.md", "**`d5d8c4a72fa7be7aebecc9e58d55002be17cac08`**", c_judge_sha),
    ("tests/README.md", "every other script runs unleased", c_unleased),
    ("tests/README.md", "`GATE_SCOPE=full` is the default in every context", c_scope_default),
    ("tests/README.md", "`renew` exits 75 while one waits", c_rcs),
    ("tests/README.md", "The owner file at `/tmp/hpo-gate.lock/owner`", c_lockdir),
    ("dev/governance/rules/gate-scoping.md", "A gate run rewrites `tools/audit/round4/D6/`", c_round4_d6),
    ("dev/governance/rules/gate-scoping.md", "`lease`, exclusive, measuring the machine", c_measuring),
    ("dev/governance/rules/gate-scoping.md", "It runs `$PYTHON`, else `.venv/bin/python`, else `python3`", c_python_order),
    ("dev/governance/rules/gate-scoping.md", "The owner file carries your label and a 30-minute", c_lease_minutes),
    ("dev/governance/rules/gate-scoping.md", "`renew` exits 75 while another label", c_rcs),
    ("dev/governance/rules/claim-files.md", "`.gitattributes` routes both to the", c_claimnotes),
    ("dev/governance/rules/writing-for-agents.md", "exactly one handover under `docs/`", c_handover_docs),
    ("dev/governance/rules/brief-citations.md", "(not `.claude/` or `tools/audit/round2/`)", c_brief_exclude),
    ("tools/audit/seat/INSTRUMENTS.md", "Directories here that are records, not instruments", c_instrument_dirs),
    ("dev/programme/HANDOVER.md", "`worktree_gc.sh --apply` collects", c_worktree_apply),
    ("tools/audit/archscore/ABOUT.md", "R10-LIVESTATE carries the 41 -> 38 control", c_event_hub),
    ("CLAUDE.md", "**derive the count, do not carry", c_budget_count),
    ("CLAUDE.md", "**`MODE: SCOPED -- 0 script(s) run` and `MODE: FULL` both print zero", c_mode_lines),
    ("CLAUDE.md", "fails with *\"these force the FULL suite when touched\"*", c_full_orphan),
    ("CLAUDE.md", "`.cursor/rules/*.mdc` is each rule below", c_rules_sync),
    ("CLAUDE.md", "One per dimension, under `dev/governance/dimensions/`", c_tables),
    ("AGENTS.md", "a hand edit of either copy is drift `--check` refuses", c_rules_sync),
]
RES = {}


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", default=SHA)
    ap.add_argument("--rows")
    ap.add_argument("--perturb")
    ap.add_argument("--only")
    ARGS = ap.parse_args()
    t0 = time.process_time()
    rows, per_file = [], {}
    for doc, needle, fn in CHECKS:
        if ARGS.only and ARGS.only not in fn.__name__:
            continue
        units = [u for u in text_ledger.units_of(doc, text_ledger.read(".", doc), "D6") if needle in " ".join(u[3].split())]
        if len(units) != 1:
            print(f"ANCHOR {doc} {needle!r} matched {len(units)} units", file=sys.stderr)
            if not units:
                continue
        uid, line, _k, _t = units[0]
        cmd, res, verdict, truth = fn()
        rows.append([uid, str(line), "claim", f"claims.py:{fn.__name__}: {cmd}", res.replace("\t", " ").replace("\n", " ")[:800], verdict, truth])
        per_file.setdefault(doc, 0)
        per_file[doc] += verdict in ("false", "stale")
        print(f"CHECK {verdict:6} {uid} {fn.__name__}: {res[:160]}")
    for k, v in sorted(RES.items()):
        print(f"RESULT {k}={v}")
    for d, n in sorted(per_file.items()):
        print(f"RESULT false_or_stale[{d}]={n}")
    print(f"RESULT checked_units={len(rows)}")
    if ARGS.rows:
        Path(ARGS.rows).write_text("".join("\t".join(r) + "\n" for r in rows))
    import resource
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    print(f"RESULT cpu_s={time.process_time() - t0:.2f} provisional")


if __name__ == "__main__":
    main()
