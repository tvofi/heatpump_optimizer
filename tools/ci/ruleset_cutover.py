#!/usr/bin/env python3
"""Cut ruleset 23698884's required contexts over from the 17 to `gate`, and back.

    python3 -I tools/ci/ruleset_cutover.py --dry-run [--staged F --head H --pr N]
    python3 -I tools/ci/ruleset_cutover.py --apply --rollback-file /abs/path.json \\
        --staged F --head H --pr N
    python3 -I tools/ci/ruleset_cutover.py --rollback /abs/path.json
    python3 -I tools/ci/ruleset_cutover.py --self-test

WHO RUNS IT. `--apply` and `--rollback` are tvofi's, as the repository owner,
at PR 2's merge (plans/ci-layout PLAN.md section 3; DESIGN-REVIEW.md section
4). CI runs only `--self-test`, offline over tools/ci/fixtures/ruleset/. All
I/O is `gh api` as the caller, through one injectable runner, so the
self-test drives every arm with a fake and no network.

FAIL CLOSED. Every step raises `Refuse` on anything unexpected -- a non-zero
`gh`, unparseable JSON, a missing key, a count that is not 17 -- and the run
stops there with rc 2: `set -euo pipefail` semantics. The rollback copy is
written only from a GET that parsed and holds exactly 17 contexts, to a new
file at an absolute path (never over an existing one), so a failed GET
leaves no file at all rather than an empty one.

THE PAYLOAD is the rollback copy's six writable keys with one change:
`required_status_checks = [{"context": "gate", "integration_id": 15368}]`.
The `pull_request` rule, both bypass actors (the DeployKey with
`actor_id: null`, as the GET returns it), `strict` and the rest are carried
through untouched.

THE READ-BACK has two halves, both required: the PUT result equals the
payload (and a fresh GET requires `gate` alone); and everything except
`required_status_checks` in that GET equals the rollback copy -- the half
that proves the PUT changed nothing else. Together they make the GET equal
to the payload. A PUT the API refuses (a 4xx) changes nothing; the instrument then
reads the ruleset back and reports whether it still equals the rollback copy.
`--rollback` PUTs the copy's six keys and reads all six back.
"""
from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
RULESET_ID = 23698884
RULESET = f"repos/{REPO}/rulesets/{RULESET_ID}"
GATE_APP_ID = 15368  # the GitHub Actions App: `gate` is a job of a workflow
OWNER = "tvofi"
OLD_CONTEXTS = 17  # required-contexts.json `contexts`, the layout P2 replaces
KEYS = ("name", "target", "enforcement", "conditions", "bypass_actors", "rules")
RSC = "required_status_checks"
NEW_CHECKS = [{"context": "gate", "integration_id": GATE_APP_ID}]
MAIN_RUN_PATHS = (".github/workflows/tests.yml", ".github/workflows/ci.yml")
PAGE = 100  # a full page cannot prove the list is complete, so it refuses
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "ruleset"

TRIGGERS = """\
ROLLBACK TRIGGERS (DESIGN-REVIEW.md section 4 item 6). Roll back if any holds:
  1. PR {pr} is not merged within 15 min of this PUT;
  2. main's push `gate` is not green within 75 min;
  3. the trigger-path check (DESIGN-P2 7 step 3a) fails and its own rollback
     (disable gate-sweep.yml, run sweep_driver.py) does not hold.
ORDER: the ruleset FIRST --
  python3 -I tools/ci/ruleset_cutover.py --rollback {rollback}
then open and merge the revert of PR {pr}. The other way round deadlocks: the
revert's head writes no `gate`, so under [gate] it could never merge."""


class Refuse(Exception):
    """A step that did not hold. The run stops; nothing after it executes."""


def gh_subprocess(args: list[str], stdin: str | None = None) -> tuple[int, str]:
    p = subprocess.run(["gh", "api", *args], input=stdin, capture_output=True, text=True)
    return p.returncode, p.stdout if p.returncode == 0 else p.stdout + p.stderr


def call(gh, args: list[str], stdin: str | None = None):
    """One `gh api` call, parsed; any failure is a refusal naming the call."""
    rc, out = gh(args, stdin)
    if rc != 0:
        raise Refuse(f"gh api {' '.join(args)} exited {rc}: {out.strip()[:300]}")
    try:
        return json.loads(out)
    except ValueError as e:
        raise Refuse(f"gh api {' '.join(args)} returned no JSON: {e}") from None


def six(ruleset: dict) -> dict:
    missing = [k for k in KEYS if k not in ruleset]
    if missing:
        raise Refuse(f"ruleset lacks {missing}")
    return {k: ruleset[k] for k in KEYS}


def rsc_rule(sixk: dict) -> dict:
    rules = [r for r in sixk["rules"] if r.get("type") == RSC]
    if len(rules) != 1:
        raise Refuse(f"{len(rules)} {RSC} rules, expected exactly 1")
    return rules[0]


def contexts(sixk: dict) -> list[dict]:
    return rsc_rule(sixk)["parameters"][RSC]


def without_checks(sixk: dict) -> dict:
    """The six keys with the one list the cut-over changes taken out."""
    out = copy.deepcopy(sixk)
    del rsc_rule(out)["parameters"][RSC]
    return out


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, indent=2) + "\n"


def digest(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def assert_old(sixk: dict, what: str) -> None:
    n = len(contexts(sixk))
    if n != OLD_CONTEXTS:
        raise Refuse(f"{what} holds {n} required contexts, expected exactly {OLD_CONTEXTS}")


def payload(rollback: dict) -> dict:
    out = copy.deepcopy(six(rollback))
    rsc_rule(out)["parameters"][RSC] = copy.deepcopy(NEW_CHECKS)
    return out


def diff(a: dict, b: dict, la: str, lb: str) -> str:
    return "".join(difflib.unified_diff(canon(a).splitlines(True), canon(b).splitlines(True), la, lb))


def preconditions(gh, live: dict, staged: dict | None, head: str | None, pr: int | None):
    """(name, ok, detail) for each of DESIGN-REVIEW.md 4 item 3's five reads."""
    out = []
    if staged is None:
        out.append(("staged-hash", None, "not evaluated: no --staged"))
    else:
        a, b = digest(six(live)), digest(six(staged))
        out.append(("staged-hash", a == b, f"live {a[:16]} staged {b[:16]}"))
    if head is None:
        out.append(("gate-at-head", None, "not evaluated: no --head"))
    else:
        runs = call(gh, [f"repos/{REPO}/commits/{head}/check-runs"
                         f"?check_name=gate&filter=all&per_page={PAGE}"])
        cr = [r for r in runs.get("check_runs", []) if r.get("name") == "gate"]
        if not cr or len(cr) >= PAGE:
            out.append(("gate-at-head", False, f"{len(cr)} gate check runs at {head}"))
        else:
            n = max(cr, key=lambda r: r["id"])
            ok = (n.get("conclusion") == "success" and (n.get("app") or {}).get("id") == GATE_APP_ID
                  and n.get("head_sha") == head)
            out.append(("gate-at-head", ok, f"newest id {n['id']}: {n.get('conclusion')} "
                        f"app {(n.get('app') or {}).get('id')} head {n.get('head_sha')}"))
    login = call(gh, ["user"]).get("login")
    out.append(("caller-is-owner", login == OWNER, f"gh api user reads {login!r}"))
    wr = call(gh, [f"repos/{REPO}/actions/runs?branch=main&event=push&status=in_progress&per_page={PAGE}"])
    runs = wr.get("workflow_runs", [])
    busy = [f"{r.get('name')} {r.get('id')}" for r in runs
            if r.get("path") in MAIN_RUN_PATHS or r.get("name") == "Tests"]
    full = len(runs) >= PAGE or wr.get("total_count", 0) > len(runs)
    out.append(("main-push-idle", not busy and not full,
                f"in progress: {busy or 'none'}" + (" (list incomplete)" if full else "")))
    pulls = call(gh, [f"repos/{REPO}/pulls?state=open&per_page={PAGE}"])
    others = [p["number"] for p in pulls if p.get("number") != pr]
    full = len(pulls) >= PAGE
    besides = f" besides #{pr}" if pr else ""
    out.append(("queue-drained", not others and not full,
                f"open{besides}: {others or 'none'}" + (" (list incomplete)" if full else "")))
    return out


def print_preconditions(rows) -> bool:
    for name, ok, detail in rows:
        print(f"PRECONDITION {name}: {'PASS' if ok else 'SKIP' if ok is None else 'FAIL'} -- {detail}")
    return all(ok is not False for _, ok, _ in rows)


def save_rollback(gh, path: str) -> dict:
    """GET the live ruleset and write it to a NEW absolute path, or refuse."""
    p = Path(path)
    if not p.is_absolute():
        raise Refuse(f"--rollback-file {path!r} is not an absolute path")
    if p.exists():
        raise Refuse(f"{path} exists; a rollback copy is never overwritten")
    live = call(gh, [RULESET])
    assert_old(six(live), "the live ruleset")
    tmp = p.with_name(p.name + ".partial")
    tmp.write_text(json.dumps(live, indent=2) + "\n")
    os.replace(tmp, p)
    back = json.loads(p.read_text())
    if back != live:
        raise Refuse(f"{path} does not read back as the GET")
    assert_old(six(back), f"the rollback file {path}")
    print(f"ROLLBACK saved {path} ({OLD_CONTEXTS} contexts, sha256 {digest(six(back))[:16]})")
    return back


def apply(gh, rollback_file: str, staged: dict, head: str, pr: int) -> int:
    rollback = save_rollback(gh, rollback_file)
    live = call(gh, [RULESET])
    if six(live) != six(rollback):
        raise Refuse("the ruleset changed between the rollback GET and the precondition read")
    if not print_preconditions(preconditions(gh, live, staged, head, pr)):
        raise Refuse("a precondition failed; nothing was written")
    want = payload(rollback)
    rc, out = gh(["-X", "PUT", RULESET, "--input", "-"], json.dumps(want))
    if rc != 0:
        after = six(call(gh, [RULESET]))
        state = ("is UNCHANGED (reads back equal to the rollback copy)" if after == six(rollback)
                 else "DIFFERS from the rollback copy:\n" + diff(six(rollback), after, "rollback", "live"))
        raise Refuse(f"the PUT was refused ({out.strip()[:300]}); the ruleset {state}")
    try:
        put = six(json.loads(out))
    except ValueError:
        raise Refuse("the PUT returned no JSON") from None
    after = six(call(gh, [RULESET]))
    if put != want or contexts(after) != NEW_CHECKS:
        raise Refuse("READBACK half 1 FAILED: the PUT result is not the payload\n"
                     + diff(want, put, "payload", "put"))
    print("READBACK half 1 OK: the PUT result equals the payload; the GET requires only gate")
    if without_checks(after) != without_checks(six(rollback)):
        raise Refuse("READBACK half 2 FAILED: the PUT changed more than required_status_checks\n"
                     + diff(without_checks(six(rollback)), without_checks(after), "rollback", "live"))
    print("READBACK half 2 OK: everything but required_status_checks equals the rollback copy")
    print(TRIGGERS.format(pr=pr, rollback=rollback_file))
    return 0


def rollback(gh, path: str) -> int:
    p = Path(path)
    if not p.is_absolute():
        raise Refuse(f"--rollback {path!r} is not an absolute path")
    try:
        want = six(json.loads(p.read_text()))
    except (OSError, ValueError) as e:
        raise Refuse(f"cannot read the rollback copy {path}: {e}") from None
    assert_old(want, f"the rollback copy {path}")
    rc, out = gh(["-X", "PUT", RULESET, "--input", "-"], json.dumps(want))
    if rc != 0:
        raise Refuse(f"the rollback PUT was refused: {out.strip()[:300]}")
    after = six(call(gh, [RULESET]))
    if after != want:
        raise Refuse("ROLLBACK READBACK FAILED\n" + diff(want, after, "rollback", "live"))
    print(f"ROLLBACK READBACK OK: all six keys equal {path}; now revert PR 2")
    return 0


def dry_run(gh, staged: dict | None, head: str | None, pr: int | None) -> int:
    live = call(gh, [RULESET])
    assert_old(six(live), "the live ruleset")
    want = payload(live)
    print("PAYLOAD (PUT " + RULESET + "):")
    print(canon(want), end="")
    print("DIFF (live six keys -> payload):")
    print(diff(six(live), want, "live", "payload"), end="")
    same = without_checks(want) == without_checks(six(live))
    print(f"OUTSIDE required_status_checks: {'IDENTICAL' if same else 'DIFFERS'}")
    ok = print_preconditions(preconditions(gh, live, staged, head, pr)) and same
    print(f"DRY-RUN {'OK' if ok else 'REFUSED'}: nothing was written")
    return 0 if ok else 1


def load(path: str | None):
    if path is None:
        return None
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        raise Refuse(f"cannot read {path}: {e}") from None


def main(argv: list[str], gh=gh_subprocess) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--rollback", metavar="FILE")
    mode.add_argument("--self-test", action="store_true")
    ap.add_argument("--rollback-file", help="absolute path the --apply GET is saved to")
    ap.add_argument("--staged", help="the ruleset JSON staged in PR 2's body")
    ap.add_argument("--head", help="PR 2's head SHA, H")
    ap.add_argument("--pr", type=int, help="PR 2's number")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    try:
        if a.dry_run:
            return dry_run(gh, load(a.staged), a.head, a.pr)
        if a.rollback:
            return rollback(gh, a.rollback)
        if None in (a.rollback_file, a.staged, a.head, a.pr):
            raise Refuse("--apply needs --rollback-file, --staged, --head and --pr")
        return apply(gh, a.rollback_file, load(a.staged), a.head, a.pr)
    except Refuse as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2


# ---------------------------------------------------------------- self-test


class FakeGh:
    """`gh api` over the saved fixtures: GETs by path prefix, PUT by behaviour."""

    def __init__(self, ruleset: dict, green: dict, put="ok", after=None, fail_get=False):
        self.state, self.green, self.put, self.after = copy.deepcopy(ruleset), green, put, after
        self.fail_get, self.puts = fail_get, []

    def __call__(self, args, stdin=None):
        if args[:2] == ["-X", "PUT"]:
            self.puts.append(json.loads(stdin))
            if self.put == "4xx":
                if self.after is not None:
                    self.state = self.after(copy.deepcopy(self.state))
                return 1, '{"message":"Validation Failed"} gh: HTTP 422'
            body = json.loads(stdin)
            self.state = {**self.state, **body}
            if self.after is not None:
                self.state = self.after(copy.deepcopy(self.state))
            return 0, json.dumps(body if self.put == "ok" else self.after(copy.deepcopy(body)))
        path = args[0]
        if path == RULESET:
            return (1, "gh: HTTP 502") if self.fail_get else (0, json.dumps(self.state))
        g = self.green
        for prefix, key in ((f"repos/{REPO}/commits/", "check_runs"), ("user", "user"),
                            (f"repos/{REPO}/actions/runs", "runs"), (f"repos/{REPO}/pulls", "pulls")):
            if path.startswith(prefix):
                return 0, json.dumps(g[key])
        return 1, f"gh: no fixture for {path}"


def self_test() -> int:
    import contextlib
    import io
    import tempfile

    ruleset = json.loads((FIXTURES / "ruleset_23698884.json").read_text())
    green = json.loads((FIXTURES / "green.json").read_text())
    H, PR = green["head"], green["pr"]
    checks = failed = 0

    def check(name, ok, detail=""):
        nonlocal checks, failed
        checks += 1
        if not ok:
            failed += 1
            print(f"FAIL {name} {detail}")

    def run(fake, argv):
        o, e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            rc = main(argv, gh=fake)
        return rc, o.getvalue() + e.getvalue()

    with tempfile.TemporaryDirectory() as td, contextlib.chdir(td):
        staged = os.path.join(td, "staged.json")
        Path(staged).write_text(json.dumps(ruleset))
        n = iter(range(10**6))

        def apply_argv(**over):
            v = {"--rollback-file": os.path.join(td, f"rb-{next(n)}.json"),
                 "--staged": staged, "--head": H, "--pr": str(PR), **over}
            return ["--apply", *[x for kv in v.items() for x in kv]], v["--rollback-file"]

        def variant(**edits):
            g = copy.deepcopy(green)
            for k, f in edits.items():
                g[k] = f(copy.deepcopy(g[k]))
            return g

        # Null: the all-green moment passes --dry-run, writing nothing.
        f = FakeGh(ruleset, green)
        rc, out = run(f, ["--dry-run", "--staged", staged, "--head", H, "--pr", str(PR)])
        check("null: all-green --dry-run passes", rc == 0 and "DRY-RUN OK" in out, out)
        check("null: --dry-run writes nothing", f.puts == [])
        lines = out.splitlines()
        check("dry-run prints the payload and only the 17 -> gate diff",
              sum(x.startswith("+ ") and '"context": "gate"' in x for x in lines) == 1
              and sum(x.startswith("- ") and '"context"' in x for x in lines) == OLD_CONTEXTS
              and "PAYLOAD" in out and "IDENTICAL" in out, out)

        # The all-green --apply: one PUT, the GET-shaped payload, both halves, triggers.
        f = FakeGh(ruleset, green)
        argv, rb = apply_argv()
        rc, out = run(f, argv)
        check("apply: all green succeeds", rc == 0, out)
        check("apply: exactly one PUT", len(f.puts) == 1)
        put = f.puts[0] if f.puts else {}
        check("payload sets required_status_checks to [gate@15368]",
              put and contexts(put) == NEW_CHECKS)
        check("payload keeps everything else byte-identical, DeployKey actor_id null included",
              put and without_checks(put) == without_checks(six(ruleset))
              and {"actor_id": None, "actor_type": "DeployKey", "bypass_mode": "always"}
              in put["bypass_actors"])
        check("apply: the rollback copy holds the 17", os.path.exists(rb)
              and len(contexts(six(json.loads(Path(rb).read_text())))) == OLD_CONTEXTS)
        check("apply: both read-back halves and the triggers print",
              "half 1 OK" in out and "half 2 OK" in out and "ruleset FIRST" in out, out)

        # Plants: each precondition violated refuses, before any PUT.
        def gate(**kv):
            return lambda c: {**c, "check_runs": [*c["check_runs"],
                              {"id": 900003, "name": "gate", "head_sha": H, "status": "completed",
                               "conclusion": "success", "app": {"id": GATE_APP_ID}, **kv}]}
        plants = {
            "gate newest failure": variant(check_runs=gate(conclusion="failure")),
            "gate from another app": variant(check_runs=gate(app={"id": 99})),
            "gate at another head": variant(check_runs=gate(head_sha="0" * 40)),
            "no gate at all": variant(check_runs=lambda c: {"total_count": 0, "check_runs": []}),
            "caller not tvofi": variant(user=lambda u: {"login": "hpo-author[bot]"}),
            "Tests push run in progress": variant(runs=lambda r: {**r, "workflow_runs": [
                *r["workflow_runs"], {"id": 1, "name": "Tests", "path": MAIN_RUN_PATHS[0]}]}),
            "ci.yml push run in progress": variant(runs=lambda r: {**r, "workflow_runs": [
                *r["workflow_runs"], {"id": 2, "name": "CI", "path": MAIN_RUN_PATHS[1]}]}),
            "runs list incomplete": variant(runs=lambda r: {**r, "total_count": 101}),
            "another PR open": variant(pulls=lambda p: [*p, {"number": 2701}]),
            "PR list a full page": variant(pulls=lambda p: [{"number": PR}] * PAGE),
        }
        for name, g in plants.items():
            f = FakeGh(ruleset, g)
            argv, rb = apply_argv()
            rc, out = run(f, argv)
            check(f"plant {name}: --apply refuses", rc == 2 and "FAIL" in out, out)
            check(f"plant {name}: no PUT", f.puts == [])
            rc, out = run(FakeGh(ruleset, g), ["--dry-run", "--staged", staged, "--head", H, "--pr", str(PR)])
            check(f"plant {name}: --dry-run refuses", rc == 1, out)
        moved = copy.deepcopy(ruleset)
        moved["enforcement"] = "evaluate"
        Path(staged + ".old").write_text(json.dumps(moved))
        f = FakeGh(ruleset, green)
        argv, _ = apply_argv(**{"--staged": staged + ".old"})
        rc, out = run(f, argv)
        check("plant staged hash differs: refuses, no PUT",
              rc == 2 and f.puts == [] and "staged-hash: FAIL" in out, out)

        # The rollback copy: absolute, new, from a GET that worked, exactly 17.
        f = FakeGh(ruleset, green, fail_get=True)
        argv, rb = apply_argv()
        rc, out = run(f, argv)
        check("failed GET: refuses and leaves no rollback file",
              rc == 2 and f.puts == [] and not os.path.exists(rb)
              and not os.path.exists(rb + ".partial"), out)
        rc, out = run(FakeGh(ruleset, green), apply_argv(**{"--rollback-file": "rb.json"})[0])
        check("relative rollback path: refuses", rc == 2 and "absolute" in out, out)
        Path(td, "exists.json").write_text("{}")
        f = FakeGh(ruleset, green)
        rc, out = run(f, apply_argv(**{"--rollback-file": os.path.join(td, "exists.json")})[0])
        check("existing rollback path: refuses, file untouched",
              rc == 2 and Path(td, "exists.json").read_text() == "{}" and f.puts == [], out)
        short = copy.deepcopy(ruleset)
        contexts(short).pop()
        f = FakeGh(short, green)
        argv, rb = apply_argv()
        rc, out = run(f, argv)
        check("16 live contexts: refuses before writing or PUT",
              rc == 2 and f.puts == [] and not os.path.exists(rb), out)

        # A refused PUT leaves the ruleset unchanged, and the read-back says so.
        f = FakeGh(ruleset, green, put="4xx")
        rc, out = run(f, apply_argv()[0])
        check("4xx PUT: refuses and reads back UNCHANGED", rc == 2 and "UNCHANGED" in out, out)
        f = FakeGh(ruleset, green, put="4xx", after=lambda s: {**s, "enforcement": "disabled"})
        rc, out = run(f, apply_argv()[0])
        check("4xx PUT over a ruleset that moved: refuses and says it DIFFERS",
              rc == 2 and "DIFFERS" in out and "UNCHANGED" not in out, out)

        # Each read-back half catches what only it can see.
        def flip_pr_rule(s):
            for r in s["rules"]:
                if r["type"] == "pull_request":
                    r["parameters"]["require_code_owner_review"] = False
            return s
        f = FakeGh(ruleset, green, put="echo-other", after=lambda s: {**s, "enforcement": "disabled"})
        rc, out = run(f, apply_argv()[0])
        check("half 1: a PUT that is not the payload refuses", rc == 2 and "half 1 FAILED" in out, out)
        f = FakeGh(ruleset, green, after=flip_pr_rule)
        rc, out = run(f, apply_argv()[0])
        check("half 2: a PUT that changed the pull_request rule refuses",
              rc == 2 and "half 1 OK" in out and "half 2 FAILED" in out, out)

        # --rollback: PUT the copy's six keys, all six read back.
        f = FakeGh(payload(ruleset) | {"id": RULESET_ID}, green)
        argv, rb = apply_argv()
        Path(rb).write_text(json.dumps(ruleset))
        rc, out = run(f, ["--rollback", rb])
        check("rollback: restores the 17 and reads all six back",
              rc == 0 and f.puts == [six(ruleset)] and "ROLLBACK READBACK OK" in out, out)
        f = FakeGh(payload(ruleset), green, after=lambda s: {**s, "name": "renamed"})
        rc, out = run(f, ["--rollback", rb])
        check("rollback: a read-back mismatch refuses", rc == 2 and "ROLLBACK READBACK FAILED" in out, out)
        rc, out = run(FakeGh(ruleset, green), ["--rollback", "relative.json"])
        check("rollback: a relative path refuses", rc == 2, out)

    print(f"ruleset_cutover self-test: {checks} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
