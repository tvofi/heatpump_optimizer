#!/usr/bin/env python3
"""R10-CI-LAYOUT P2a U0a: the design's oracles driving tools/ci/gate.py, not the model.

    python3 dev/audit/harnesses/r10_ci_gate_core.py replay [--model] [--no-b3-fill]
    python3 dev/audit/harnesses/r10_ci_gate_core.py sim [--model]       # about 8 min
    python3 dev/audit/harnesses/r10_ci_gate_core.py b3 [--plant]
    python3 dev/audit/harnesses/r10_ci_gate_core.py mutants

The oracles are DESIGN-P2 4.4's `measure/rev/gate_replay2.py` and
`measure/rev/gate_sim.py` at the approved design commit DESIGN (fetch
`probe/design-ci-rev4` if the object is missing). Each imports `gate_model` as
G; this registers a module under that name whose every symbol is the PORT's
(gate.gate, gate.judging, prelude.derive/title/workset, the unit names), so the
oracle's own verdicts judge tools/ci/gate.py. `--model` runs the oracle on the
model itself, the null whose output the port's must equal.

gate_sim's ablations assign `G.judging`; the shim's `gate` installs whatever
G.judging holds into the port for the call, so an ablation reaches the port.

B3 FILL. The model predates amendment B3: its push rows carry no
`tests / coverage`, `coverage-ratchet` or `ci-ratchet` job, which the port
now requires on push. By default the shim adds each of those three, green,
to a push run that lacks it (never over one it has); `--no-b3-fill` drops the
fill, and the push rows must then fail naming exactly those names.

U5B FILL. The model predates P2b's `tests / arch-instrument` too, which the
port requires wherever `tests` runs and which is no ruleset context: the shim
keeps it out of the model's names and adds it, green, to any run carrying a
`tests / *` job that lacks it (this run's and every run at the head),
always: `--no-b3-fill` keeps it, so its null stays B3's. The port's own
self-test is this name's null (a run without it FAILs naming it).

`b3` enumerates, from this tree's `.github/workflows/tests.yml` (the file the
port's REQUIRED is paired with; origin/main's until P2b), every job whose failure
reddens the Tests push run (it runs on push and is not continue-on-error)
and compares it with REQUIRED["push"]'s `tests / *` names; `--plant` drops
`ci-ratchet` from REQUIRED first, and the parity must go red.

`mutants` plants each predicate mutant below in tools/ci/gate.py, runs the
port's self-test and the replay, and prints KILLED or SURVIVED; the file's
bytes are restored, and a dirty file refuses first.
"""
from __future__ import annotations

import contextlib
import io
import re
import runpy
import subprocess
import sys
import tarfile
import tempfile
import types
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
DESIGN = "1371a0a6"
GATE = ROOT / "tools" / "ci" / "gate.py"
sys.path.insert(0, str(GATE.parent))
import gate as port  # noqa: E402
import prelude  # noqa: E402

B3_NAMES = tuple(f"tests / {n}" for n in port.PUSH_ONLY["tests"])
U5B_NAMES = ("tests / arch-instrument",)


def u5b_fill(jobs: dict) -> dict:
    if not any(k.startswith("tests / ") for k in jobs):
        return jobs
    return {**{n: ("completed", "success") for n in U5B_NAMES}, **jobs}


def extract(dest: Path) -> Path:
    blob = subprocess.run(["git", "archive", DESIGN, "measure/rev", "measure/p2/raw"], cwd=ROOT,
                          capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(blob)) as t:
        t.extractall(dest, filter="data")
    return dest / "measure"


def shim(b3_fill: bool = True) -> types.ModuleType:
    G = types.ModuleType("gate_model")
    G.CODE = {u: [x for x in n if f"{u} / {x}" not in U5B_NAMES] for u, n in port.CODE.items()}
    G.BODY = {u: list(n) for u, n in port.BODY.items()}
    G.REQUIRED = {**G.CODE, **G.BODY}
    G.BODY_ON_EDIT, G.BODY_ON_REVIEW = set(prelude.BODY_ON_EDIT), set(prelude.BODY_ON_REVIEW)
    G.ATTEMPT_CAP = port.ATTEMPT_CAP
    G.derive, G.title, G.parse_title, G.title_sha = prelude.derive, prelude.title, prelude.parse_title, prelude.title_sha
    G.workset = lambda kind, pr: prelude.workset(kind, pr)
    _judging = port.judging                            # the original: gate() below swaps port.judging
    G.judging = lambda run: _judging({**run, "jobs": u5b_fill(run.get("jobs") or {})})

    def gate(ctx, api):
        if b3_fill and ctx["event_name"] == "push":
            api = {**api, "jobs": {**{n: ("completed", "success") for n in B3_NAMES}, **api["jobs"]}}
        api = {**api, "jobs": u5b_fill(api["jobs"]),
               "runs_at_head": [{**r, "jobs": u5b_fill(r.get("jobs") or {})} for r in api["runs_at_head"]]}
        saved, port.judging = port.judging, G.judging
        try:
            return port.gate(ctx, api)
        finally:
            port.judging = saved
    G.gate = gate
    return G


def run_oracle(script: str, args: list[str], model: bool, b3_fill: bool) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as d:
        m = extract(Path(d))
        sys.modules.pop("gate_model", None)
        if not model:
            sys.modules["gate_model"] = shim(b3_fill)
        argv, sys.argv = sys.argv, [str(m / "rev" / script)] + [str(m / a) for a in args]
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                runpy.run_path(str(m / "rev" / script), run_name="__main__")
            rc = 0
        except SystemExit as e:
            rc = int(e.code or 0)
        finally:
            sys.argv = argv
            sys.modules.pop("gate_model", None)
    return rc, buf.getvalue()


def recorded(name: str) -> str:
    return subprocess.run(["git", "show", f"{DESIGN}:measure/rev/{name}"], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def oracle_arm(script: str, args: list[str], out_name: str, opts: list[str]) -> int:
    rc, out = run_oracle(script, args, "--model" in opts, "--no-b3-fill" not in opts)
    sys.stdout.write(out)
    same = out == recorded(out_name)
    print(f"{script} over {'the MODEL' if '--model' in opts else 'tools/ci/gate.py'}: rc {rc}; "
          f"output {'IDENTICAL to' if same else 'DIFFERS from'} {DESIGN}:measure/rev/{out_name}")
    return rc


def b3_enumerate(text: str) -> list[str]:
    """Every job of tests.yml whose failure reddens a push run, named as GitHub names its check."""
    import yaml
    jobs = yaml.safe_load(text)["jobs"]
    out = []
    for jid, j in jobs.items():
        if j.get("continue-on-error") is True or not runs_on_push(str(j.get("if", "true"))):
            continue
        name = j.get("name") or jid
        matrix = (j.get("strategy") or {}).get("matrix") or {}
        if not matrix:
            out.append(name)
            continue
        if len(matrix) != 1 or not isinstance(next(iter(matrix.values())), list):
            raise SystemExit(f"b3: {jid} runs on push with a matrix this enumeration cannot name: {matrix}")
        out += [f"{name} ({v})" for v in next(iter(matrix.values()))]
    return sorted(out)


def runs_on_push(cond: str) -> bool:
    """A job `if:` evaluated for a push to main: every term this cannot decide reads as
    true (the job may run, so its failure may redden the run); an unknown token refuses."""
    e = cond.replace("${{", "").replace("}}", "")
    e = re.sub(r"github\.event_name\s*==\s*'([\w-]+)'", lambda m: str(m.group(1) == "push"), e)
    e = re.sub(r"github\.ref\s*==\s*'refs/heads/main'", "True", e)
    e = re.sub(r"!\s*cancelled\(\)", "True", e)
    e = re.sub(r"(needs|github\.event|inputs)\.[\w.-]+\s*(==|!=)\s*('[^']*'|github\.repository)", "True", e)
    e = e.replace("&&", " and ").replace("||", " or ").replace("!", " not ")
    if re.search(r"[^\sA-Za-z()]", e) or set(re.findall(r"[A-Za-z]+", e)) - {"True", "False", "and", "or", "not", "true"}:
        raise SystemExit(f"b3: cannot evaluate if: {cond!r} (left {e!r})")
    return bool(eval(e.replace("true", "True")))      # only True/False/and/or/not remain


def b3_arm(opts: list[str]) -> int:
    text = (ROOT / ".github" / "workflows" / "tests.yml").read_text()
    enumerated = b3_enumerate(text)
    required = [n.split(" / ", 1)[1] for n in port.REQUIRED["push"] if n.startswith("tests / ")]
    if "--plant" in opts:
        required = [n for n in required if n != "ci-ratchet"]
    print(f"b3: enumerated from .github/workflows/tests.yml: {enumerated}")
    print(f"b3: REQUIRED['push'] tests / * {'(PLANT: ci-ratchet dropped) ' if '--plant' in opts else ''}: {sorted(required)}")
    ok = enumerated == sorted(required)
    print(f"b3: parity {'GREEN' if ok else 'RED'}; only in tests.yml {sorted(set(enumerated) - set(required))}, "
          f"only in REQUIRED {sorted(set(required) - set(enumerated))}")
    return 0 if ok else 1


# name, old (exactly once in gate.py), new: each removes or inverts one rule of the predicate.
MUTANTS = [
    ("M1 prelude conclusion", 'if pre.get("conclusion") != "success":', 'if False:'),
    ("M2 prelude cross-check", 'if (pre.get("kind"), pre.get("pr", "")) != (kind, pr):', 'if False:'),
    ("M3 attempt cap", 'if int(ctx.get("run_attempt", 1)) >= ATTEMPT_CAP:', 'if False:'),
    ("M4 unnamed dispatch at a PR head", 'elif ctx["sha"] in api.get("open_pr_heads", set()):', 'elif False:'),
    ("M5 fork PR (R3-4)", 'if lp.get("same_repo") is not True:', 'if False:'),
    ("M6 live base", 'judge_base = lp["base_ref"]', 'judge_base = base'),
    ("M7 defer rule", 'if busy:\n', 'if False:\n'),
    ("M8 judging: listed gate", 'if "gate" not in jobs or not all(', 'if not all('),
    ("M9 judging: owed jobs (R3-2)", '            if st is None or st[0] != "completed":\n                return False\n    return True',
     '            pass\n    return True'),
    ("M10 skipped is not success", 'elif st[1] != "success":', 'elif st[1] not in ("success", "skipped"):'),
    ("M11 source must judge the live base", 'if t[1] != pr or t[2] != judge_base or unit not in workset(t[0], t[1]):',
     'if t[1] != pr or unit not in workset(t[0], t[1]):'),
    ("M12 own unit always counts", 'if r is me or all(j is not None and j[0] == "completed" for j in js):',
     'if all(j is not None and j[0] == "completed" for j in js):'),
    ("M13 D-2 arch-score", 'return "pr-cc" if reaches_cc else "pr"', 'return "pr"'),
    ("M14 held run is no source", '            if r["status"] == "action_required":\n                continue\n',
     ''),
    ("M15 unreadable title", '                bad.append(f"run {r[\'id\']}: unreadable title {r[\'title\']!r}")\n', ''),
    ("M16 B3 on push", 'extra=PUSH_ONLY),', 'extra=None),'),
]


def mutants_arm() -> int:
    if subprocess.run(["git", "diff", "--quiet", "--", str(GATE)], cwd=ROOT).returncode:
        print(f"mutants: {GATE} has uncommitted edits; the restore would erase them")
        return 2

    def verdicts() -> tuple[int, int]:
        st = subprocess.run([sys.executable, "-I", str(GATE), "--self-test"], capture_output=True).returncode
        rp = subprocess.run([sys.executable, __file__, "replay"], capture_output=True).returncode
        return st, rp
    base = verdicts()
    print(f"mutants: unmutated self-test rc {base[0]}, replay rc {base[1]}")
    if base != (0, 0):
        return 1
    orig = GATE.read_bytes()
    survived = 0
    for name, old, new in MUTANTS:
        text = orig.decode()
        if text.count(old) != 1:
            print(f"  {name}: NOT RUN, pattern found {text.count(old)} times")
            survived += 1
            continue
        GATE.write_text(text.replace(old, new))
        try:
            st, rp = verdicts()
        finally:
            GATE.write_bytes(orig)
        killed = st or rp
        survived += not killed
        print(f"  {name}: {'KILLED' if killed else 'SURVIVED'} (self-test rc {st}, replay rc {rp})")
    print(f"RESULT mutants={len(MUTANTS)} survivors={survived}")
    return 1 if survived else 0


def main(argv: list[str]) -> int:
    arm, opts = (argv or ["?"])[0], argv[1:]
    if arm == "replay":
        return oracle_arm("gate_replay2.py", ["p2/raw", "rev/reaches_cc.txt"], "gate_replay2.txt", opts)
    if arm == "sim":
        return oracle_arm("gate_sim.py", [], "gate_sim.txt", opts)
    if arm == "b3":
        return b3_arm(opts)
    if arm == "mutants":
        return mutants_arm()
    print(__doc__.strip().splitlines()[2:7], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
