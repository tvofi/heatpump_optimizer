"""Per-unit null control, revision 1 (review item 9): a STATIC half, a refusing
runtime half, and matched events.

    python3 -I measure/rev/unitcheck2.py static BEFORE.yml AFTER.yml[+MORE.yml] [--map MAP.json]
    python3 -I measure/rev/unitcheck2.py runtime RAW --before ID --after ID [--ignore J,..]
    python3 -I measure/rev/unitcheck2.py self-test BEFORE.yml RAW BEFORE_RUN_ID

STATIC compares the unit's workflow file before (main's) and after (the probe
ref's callee), parsed, never as text: per job one row for the job itself, hashing
its `if`, `needs`, `permissions`, `environment`, `strategy`, `outputs`, `runs-on`,
`timeout-minutes`, `env`, `defaults`, `services`, `container`,
`continue-on-error`, `concurrency` and `name`; and one row per step, keyed
`<job>|<step name>` (an unnamed step: `run:<first line>` or `uses:<action>`; a
repeated key gets `#2`, `#3`), hashing its `run`, `uses`, `with`, `if`, `env`,
`shell`, `working-directory`, `id`, `continue-on-error` and `timeout-minutes`; and,
revision 2 (round-2 item N3), one `<job>|order` row: the ORDERED list of the step
keys both sides keep (after the map's renames, less its drops and gains), so a guard
moved after what it guards, or a restore moved after the program it restores, is
refused while an admitted drop or gain moves only its own row. It
sees every step whether or not any run executed it: a deleted job, a deleted step
that BEFORE skipped, and a body gutted under its old name all move it (the three
plants the review seat put past phase 2's unitcheck). MAP.json is the closed list
of intended moves: {"renames": {"old": "new"}, "dropped": [...], "gained": [...],
"changed": [...]} over those keys (job rows are keyed `<job>|`). Exit 0 only when
the mapped sets are equal; every listed `changed` row prints its before/after so
the reviewer reads exactly the edits the map admits. Two file-level rows ride
along: `|floor` (top-level `permissions`, `env`, `defaults`: what a callee job
without its own block receives, review item 12(e)) and `|triggers` (`on`,
`concurrency`), which every unit's map lists as `changed`.

RUNTIME is phase 2's executed-step and token-permission comparison with two
refusals added: a job whose 'Set up job' header was not read (UNREAD) is exit 2,
never a match; and the two runs must have the same event and sender class
(phase 1's own rule, P1 section 4), read from any saved runs listing in RAW, or it
is exit 2.

SELF-TEST plants, into a copy of BEFORE.yml, the review's three defects, three
more, and round 2's step-order plants (Q1, Q1b; with their mapped and dropped nulls), and shows the static half refusing each while the null and a key-order
reserialisation pass; then shows the runtime half refusing UNREAD and an event
mismatch.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

JOB_KEYS = ("if", "needs", "permissions", "environment", "strategy", "outputs", "runs-on", "timeout-minutes",
            "env", "defaults", "services", "container", "continue-on-error", "concurrency", "name", "uses", "with",
            "secrets")
STEP_KEYS = ("run", "uses", "with", "if", "env", "shell", "working-directory", "id", "continue-on-error",
             "timeout-minutes")
RUNNER = {"Set up job", "Complete job"}
SHA = re.compile(r"\b[0-9a-f]{40}\b")


def h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:12]


def load(paths) -> dict:
    """One file, or several joined by '+': their jobs merged into one mapping (a job id
    already taken is keyed `<file stem>:<job>`; a composite action's steps become the
    pseudo-job `action:<its directory>`); file-level rows come from the first.
    yaml 1.1 reads the key `on` as True; rows() accepts either."""
    files = str(paths).split("+")
    doc = yaml.safe_load(Path(files[0]).read_text())
    for f in files[1:]:
        more = yaml.safe_load(Path(f).read_text())
        if "runs" in more and "jobs" not in more:          # a composite action: one pseudo-job
            more = {"jobs": {f"action:{Path(f).parent.name}": {"steps": more["runs"].get("steps", [])}}}
        for jid, job in (more.get("jobs") or {}).items():
            doc.setdefault("jobs", {})[jid if jid not in doc["jobs"] else f"{Path(f).stem}:{jid}"] = job
    return doc


def rows(doc: dict) -> dict[str, tuple[str, dict]]:
    out = {}
    floor = {k: doc.get(k) for k in ("permissions", "env", "defaults") if k in doc}
    out["|floor"] = (h(floor), floor)                     # 12(e): the callee's own top-level floor
    trig = {"on": doc.get("on", doc.get(True)), "concurrency": doc.get("concurrency")}
    out["|triggers"] = (h(trig), trig)
    for jid, job in (doc.get("jobs") or {}).items():
        body = {k: job.get(k) for k in JOB_KEYS if k in job}
        out[f"{jid}|"] = (h(body), body)
        order: list[str] = []
        out[f"{jid}|order"] = (h(order), order)          # filled below; static() compares the kept steps' order
        seen: dict[str, int] = {}
        for st in job.get("steps") or []:
            name = st.get("name") or (f"run:{str(st['run']).strip().splitlines()[0]}" if "run" in st
                                      else f"uses:{st.get('uses')}")
            name = SHA.sub("<sha>", name)
            seen[name] = seen.get(name, 0) + 1
            key = f"{jid}|{name}" + (f"#{seen[name]}" if seen[name] > 1 else "")
            body = {k: st.get(k) for k in STEP_KEYS if k in st}
            out[key] = (h(body), body)
            order.append(key)
        out[f"{jid}|order"] = (h(order), order)
    return out


def static(before: dict, after: dict, m: dict, quiet=False) -> int:
    b, a = rows(before), rows(after)
    ren = m.get("renames", {})
    dropped = set(m.get("dropped", []))
    b = {ren.get(k, k): v for k, v in b.items() if k not in dropped}
    for k, (hb, ob) in list(b.items()):                  # N3: the order of the steps both sides keep
        if not k.endswith("|order"):
            continue
        new = ren.get(k[:-len("order")], k[:-len("order")]) + "order"
        del b[k]
        if new not in a:
            b[new] = (hb, ob)
            continue
        kept = [ren.get(x, x) for x in ob if x not in dropped]
        common = set(kept) & set(a[new][1])
        sb, sa = [x for x in kept if x in common], [x for x in a[new][1] if x in common]
        b[new], a = (h(sb), sb), {**a, new: (h(sa), sa)}
    rc = 0
    lost = sorted(set(b) - set(a))
    gained = sorted(k for k in set(a) - set(b) if k not in set(m.get("gained", [])))
    changed = sorted(k for k in set(a) & set(b) if a[k][0] != b[k][0])
    admitted = set(m.get("changed", []))
    for k in lost:
        rc = 1; quiet or print(f"  LOST     {k}")
    for k in gained:
        rc = 1; quiet or print(f"  GAINED   {k}")
    for k in changed:
        if k in admitted:
            quiet or print(f"  CHANGED (mapped) {k}\n    before {json.dumps(b[k][1], sort_keys=True)[:300]}\n"
                           f"    after  {json.dumps(a[k][1], sort_keys=True)[:300]}")
        else:
            rc = 1; quiet or print(f"  CHANGED  {k}  {b[k][0]} -> {a[k][0]}")
            if k.endswith("|order") and not quiet:
                i = next(i for i, (x, y) in enumerate(zip(b[k][1], a[k][1])) if x != y)
                print(f"    first difference at step {i}: before {b[k][1][i]!r}, after {a[k][1][i]!r}")
    print(f"  STATIC rows {len(b)}->{len(a)} lost {len(lost)} gained {len(gained)} "
          f"changed {len(changed)} (mapped {len(set(changed) & admitted)}) rc {rc}")
    return rc


# ---- runtime half -----------------------------------------------------------------
def jobs(raw: Path, ids: str) -> list:
    out = []
    for i in str(ids).split(","):
        out += json.loads((raw / f"jobs_{i}.json").read_text())["jobs"]
    return out


def perms(raw: Path, j: dict, logs=None) -> str:
    if logs is not None:
        return logs.get(j["id"], "UNREAD")
    f = raw / "logs" / f"head_{j['id']}.txt"
    if not f.exists() or not f.stat().st_size:
        return "UNREAD"
    m = re.search(r"##\[group\]GITHUB_TOKEN Permissions\n(.*?)##\[endgroup\]", f.read_text(errors="replace"), re.S)
    return ",".join(sorted(x for x in (re.sub(r"^\S+Z ", "", ln).strip() for ln in m.group(1).splitlines()) if x)) \
        if m else "NO-BLOCK"


def run_meta(raw: Path, rid: str):
    for f in raw.glob("*runs*.json"):
        try:
            data = json.loads(f.read_text())
        except ValueError:
            continue
        for r in data.get("workflow_runs", []) if isinstance(data, dict) else []:
            if str(r["id"]) == str(rid):
                actor = r["actor"]["login"]
                cls = "actions-bot" if actor == "github-actions[bot]" else ("app" if actor.endswith("[bot]") else "human")
                return r["event"], cls
    return None


def runtime(raw: Path, before: str, after: str, ignore: set, logs_b=None, logs_a=None, meta=None) -> int:
    mb = meta[0] if meta else [run_meta(raw, i) for i in before.split(",")]
    ma = meta[1] if meta else [run_meta(raw, i) for i in after.split(",")]
    if None in mb or None in ma or len(set(mb) | set(ma)) != 1:
        print(f"  REFUSE   event/sender: before {mb} after {ma} (each pair must match; P1 section 4)")
        return 2
    sb, pb = sets(raw, jobs(raw, before), ignore, logs_b)
    sa, pa = sets(raw, jobs(raw, after), ignore, logs_a)
    unread = sorted({j for j, p in pb | pa if p == "UNREAD"})
    if unread:
        print(f"  REFUSE   permission header UNREAD for: {', '.join(unread)}")
        return 2
    rc = 0
    for label, x, y in (("step", sb, sa), ("perm", pb, pa)):
        for k in sorted(x - y):
            print(f"  LOST   {label}  {' | '.join(k)}"); rc = 1
        for k in sorted(y - x):
            print(f"  GAINED {label}  {' | '.join(k)}"); rc = 1
    print(f"  RUNTIME steps {len(sb)}->{len(sa)} perms {len(pb)}->{len(pa)} rc {rc}")
    return rc


def sets(raw, js, ignore, logs=None):
    st, pm = set(), set()
    for j in js:
        name = j["name"].split(" / ", 1)[-1]
        if name in ignore or j["conclusion"] == "skipped":
            continue
        pm.add((name, perms(raw, j, logs)))
        for s in j.get("steps") or []:
            if s["conclusion"] in ("success", "failure") and s["name"] not in RUNNER and not s["name"].startswith("Post "):
                st.add((name, SHA.sub("<sha>", s["name"])))
    return st, pm


# ---- self-test ----------------------------------------------------------------------
def self_test(before_yml: Path, raw: Path, run_id: str) -> int:
    B = load(before_yml)
    results = []

    def plant(label, fn, want, m=None):
        A = copy.deepcopy(B); fn(A)
        print(f"{label}:")
        rc = static(B, A, m or {}, quiet=False)
        ok = (rc == 0) == (want == 0)
        results.append(ok)
        print(f"  -> {'ok' if ok else 'BAD'} (want rc {want})")

    def del_job(name):
        return lambda A: A["jobs"].pop(name)

    def del_cond_steps(job):
        def f(A):
            A["jobs"][job]["steps"] = [s for s in A["jobs"][job]["steps"] if "if" not in s]
        return f

    def gut(job, idx):
        def f(A):
            A["jobs"][job]["steps"][idx]["run"] = "true"
        return f

    def reorder(A):
        A["jobs"] = dict(reversed(list(A["jobs"].items())))
        for j in A["jobs"].values():
            for k in list(j):
                j[k] = j.pop(k)

    first_run = lambda job: next(i for i, s in enumerate(B["jobs"][job]["steps"]) if "run" in s)  # noqa: E731
    plant("null: the file against itself", lambda A: None, 0)
    plant("null: re-serialised (job order reversed, keys re-inserted)", reorder, 0)
    plant("P1 (review): job closures-autofix deleted", del_job("closures-autofix"), 1)
    n0 = len(B["jobs"]["fast"]["steps"])
    plant(f"P2 (review): every conditional step of fast deleted ({n0} steps before)", del_cond_steps("fast"), 1)
    plant("P3 (review): a closures step's body gutted under its old name", gut("closures", first_run("closures")), 1)
    plant("P4: a job's if: changed (browser runs on every event)", lambda A: A["jobs"]["browser"].update({"if": "always()"}), 1)
    plant("P5: a job's grant widened (nightly-status gets contents: write)",
          lambda A: A["jobs"]["nightly-status"].setdefault("permissions", {}).update({"contents": "write"}), 1)
    plant("P8: the top-level permission floor widened", lambda A: A.update({"permissions": {"contents": "write"}}), 1)
    def swap(job, i):
        def f(A):
            st = A["jobs"][job]["steps"]
            st[i - 1], st[i] = st[i], st[i - 1]
        return f

    def to_end(job, i):
        def f(A):
            st = A["jobs"][job]["steps"]
            st.append(st.pop(i))
        return f

    cov = B["jobs"]["coverage"]["steps"]
    plant(f"Q1 (round 2): two coverage steps swapped ({cov[2].get('name')!r} <-> {cov[3].get('name')!r})",
          swap("coverage", 3), 1)
    plant(f"Q1b (round 2): {cov[3].get('name')!r} moved to the end of coverage", to_end("coverage", 3), 1)
    plant("Q1c: the Q1 swap admitted by the map as `coverage|order` passes and is printed", swap("coverage", 3), 0,
          {"changed": ["coverage|order"]})
    plant("Q1d: a step dropped by the map leaves the kept steps' order unchanged",
          lambda A: A["jobs"]["coverage"]["steps"].pop(2), 0,
          {"dropped": [f"coverage|{cov[2]['name']}"]})
    plant("P6: a dropped job admitted by the map is not a defect", del_job("closures-autofix"), 0,
          {"dropped": [k for k in rows(B) if k.startswith("closures-autofix|")]})
    plant("P7: a gutted step admitted only as `changed` passes and is printed",
          gut("closures", first_run("closures")), 0,
          {"changed": [next(k for k in rows(B) if k.startswith("closures|") and not k.endswith(("|", "|order"))
                            and rows(B)[k][1].get("run"))]})
    print("runtime half: UNREAD permission headers refuse (exit 2)")
    rc_u = runtime(raw, run_id, run_id, set(), logs_b={}, logs_a={}, meta=([("x", "y")], [("x", "y")]))
    results.append(rc_u == 2)
    print("runtime half: a dispatch BEFORE against a pull_request AFTER refuses (exit 2)")
    rc_e = runtime(raw, run_id, run_id, set(), meta=([("workflow_dispatch", "actions-bot")], [("pull_request", "app")]))
    results.append(rc_e == 2)
    ok = all(results)
    print(f"SELF-TEST {'ok' if ok else 'BAD'} ({sum(results)}/{len(results)})")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("static"); s.add_argument("before"); s.add_argument("after"); s.add_argument("--map")
    r = sub.add_parser("runtime"); r.add_argument("raw", type=Path); r.add_argument("--before", required=True)
    r.add_argument("--after", required=True); r.add_argument("--ignore", default="prelude,gate,gate-hold,cancel-superseded")
    t = sub.add_parser("self-test"); t.add_argument("before"); t.add_argument("raw", type=Path); t.add_argument("run")
    a = ap.parse_args()
    if a.cmd == "static":
        return static(load(a.before), load(a.after), json.loads(Path(a.map).read_text()) if a.map else {})
    if a.cmd == "runtime":
        return runtime(a.raw, a.before, a.after, set(a.ignore.split(",")))
    return self_test(Path(a.before), a.raw, a.run)


if __name__ == "__main__":
    sys.exit(main())
