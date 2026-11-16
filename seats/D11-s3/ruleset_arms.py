#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): the main ruleset's only in-tree reader, perturbed arm by arm.

Metric: number of `required-contexts` error findings that
  tools/policy/counts.mjs:requiredContextsDrift returns when fed what
  tools/policy/counts.mjs:liveRequiredContexts reads through `gh api`, per arm.
  Count key: the findings the production comparator emits on the production
  reader's output (never on the arm's own labels).
How: a fake `gh` on PATH serves the API reads captured live on 2026-11-16
  (data/*.json, GET rules/branches/main, rulesets/{id}); each arm edits one
  field of that capture in a private temp dir, then a fresh node process runs
  the real reader and comparator against the committed fixture
  tools/policy/fixtures/required-contexts.json.
Arms: null (capture as read); controls on main-protect-checks 23698884 (an
  added bypass actor, code-owner review off, `gate` dropped); and the same
  class of change on main-protect 22628467 (deletion + non_fast_forward
  dropped; a bypass actor added; enforcement disabled) and on
  release-tags-protect 23937752 (tag rules dropped).
Expected: control arms > null arm; each 22628467 / 23937752 arm == null arm
  (the reader fetches only rulesets carrying required_status_checks), exact.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/ruleset_arms.py [--perturb]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
Perturbation (production, one line): in counts.mjs:liveRequiredContexts, collect
  `ids.add(r.ruleset_id)` for every branch rule, not only required_status_checks:
  the 22628467 arms then move up (and the null arm too, until the fixture records it).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path.cwd()
NODE = os.environ.get("NODE", "/opt/node22/bin/node")
DATA = HERE / "data"

FAKE_GH = r'''#!/usr/bin/env python3
import os, sys
d = os.environ["FAKE_GH_DIR"]
a = sys.argv[1:]
if a[:1] != ["api"]:
    sys.exit(2)
p = a[1]
name = {"rules/branches/main": "rules_branches_main.json"}
for suffix, f in name.items():
    if p.endswith(suffix):
        sys.stdout.write(open(os.path.join(d, f)).read()); sys.exit(0)
if "/rulesets/" in p:
    rid = p.rsplit("/", 1)[1]
    fp = os.path.join(d, "ruleset_%s.json" % rid)
    if os.path.exists(fp):
        sys.stdout.write(open(fp).read()); sys.exit(0)
sys.stderr.write("fake gh: no capture for %s\n" % p); sys.exit(1)
'''

DRIVER = r'''
const m = await import(process.argv[2]);
const fs = await import('node:fs');
const fixture = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const live = m.liveRequiredContexts();
const why = m.liveRequiredContextsWhy();
const errs = live ? m.requiredContextsDrift('fixture', fixture, live) : [];
console.log(JSON.stringify({ok: !!live, why, read: live ? live.rulesets : null,
  errors: errs.length, msgs: errs.map((e) => e.message.slice(0, 140))}));
'''


def load(name):
    return json.loads((DATA / name).read_text())


def arms():
    base = {
        "rules_branches_main.json": load("rules_branches_main.json"),
        "ruleset_22628467.json": load("ruleset_22628467.json"),
        "ruleset_23698884.json": load("ruleset_23698884.json"),
        "ruleset_23937752.json": load("ruleset_23937752.json"),
    }
    out = {"null": base}

    def arm(name, fn):
        d = copy.deepcopy(base)
        fn(d)
        out[name] = d

    def ctl_bypass(d):
        d["ruleset_23698884.json"]["bypass_actors"].append(
            {"actor_id": 1, "actor_type": "RepositoryRole", "bypass_mode": "always"})

    def ctl_codeowner(d):
        for r in d["ruleset_23698884.json"]["rules"]:
            if r["type"] == "pull_request":
                r["parameters"]["require_code_owner_review"] = False
        for r in d["rules_branches_main.json"]:
            if r["type"] == "pull_request":
                r["parameters"]["require_code_owner_review"] = False

    def ctl_gate(d):
        for src in (d["ruleset_23698884.json"]["rules"], d["rules_branches_main.json"]):
            for r in src:
                if r["type"] == "required_status_checks":
                    r["parameters"]["required_status_checks"] = [
                        c for c in r["parameters"]["required_status_checks"] if c["context"] != "gate"]

    def mp_rules(d):
        d["ruleset_22628467.json"]["rules"] = []
        d["rules_branches_main.json"] = [r for r in d["rules_branches_main.json"]
                                         if r.get("ruleset_id") != 22628467]

    def mp_bypass(d):
        d["ruleset_22628467.json"]["bypass_actors"].append(
            {"actor_id": 1, "actor_type": "RepositoryRole", "bypass_mode": "always"})

    def mp_disabled(d):
        d["ruleset_22628467.json"]["enforcement"] = "disabled"
        d["rules_branches_main.json"] = [r for r in d["rules_branches_main.json"]
                                         if r.get("ruleset_id") != 22628467]

    def tag_rules(d):
        d["ruleset_23937752.json"]["rules"] = []
        d["ruleset_23937752.json"]["enforcement"] = "disabled"

    arm("control_23698884_bypass_added", ctl_bypass)
    arm("control_23698884_codeowner_off", ctl_codeowner)
    arm("control_23698884_gate_dropped", ctl_gate)
    arm("gap_22628467_deletion_nonff_dropped", mp_rules)
    arm("gap_22628467_bypass_added", mp_bypass)
    arm("gap_22628467_enforcement_disabled", mp_disabled)
    arm("gap_23937752_tag_rules_dropped", tag_rules)
    return out


def counts_path(tmp):
    """The production comparator, or with --perturb a copy whose reader collects
    every branch rule's ruleset id (the one-line perturbation in the header)."""
    if "--perturb" not in sys.argv:
        return ROOT / "tools/policy/counts.mjs"
    proot = tmp / "proot"
    (proot / "tools/policy/fixtures").mkdir(parents=True, exist_ok=True)
    (proot / "tests").mkdir(exist_ok=True)
    src = (ROOT / "tools/policy/counts.mjs").read_text()
    old = "      if (r.type !== 'required_status_checks') continue\n      if (r.ruleset_id != null) ids.add(r.ruleset_id)\n"
    new = "      if (r.ruleset_id != null) ids.add(r.ruleset_id)\n      if (r.type !== 'required_status_checks') continue\n"
    if old not in src:
        raise SystemExit("perturbation did not apply")
    (proot / "tools/policy/counts.mjs").write_text(src.replace(old, new))
    for rel in ("tests/layout.json", "tools/policy/fixtures/required-contexts.json"):
        (proot / rel).write_text((ROOT / rel).read_text())
    print("PERTURBED: counts.mjs reader collects every branch rule's ruleset id")
    return proot / "tools/policy/counts.mjs"


def run_arm(tmp, name, files):
    d = pathlib.Path(tempfile.mkdtemp(prefix=name[:20], dir=tmp))
    for f, obj in files.items():
        (d / f).write_text(json.dumps(obj))
    env = dict(os.environ, PATH="%s:%s" % (tmp / "bin", os.environ.get("PATH", "")),
               FAKE_GH_DIR=str(d), HPO_PLANDATA=str(tmp / "plandata"))
    drv = tmp / "driver.mjs"
    r = subprocess.run([NODE, str(drv), str(COUNTS),
                        str(ROOT / "tools/policy/fixtures/required-contexts.json")],
                       env=env, capture_output=True, text=True, cwd=ROOT, timeout=120)
    line = [l for l in r.stdout.splitlines() if l.startswith("{")]
    if not line:
        print(r.stdout, r.stderr)
        raise SystemExit("driver produced no result for %s" % name)
    return json.loads(line[-1])


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s3-ruleset-"))
    (tmp / "bin").mkdir()
    (tmp / "plandata").mkdir()
    gh = tmp / "bin" / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(0o755)
    (tmp / "driver.mjs").write_text(DRIVER)
    global COUNTS
    COUNTS = counts_path(tmp)
    res = {}
    for name, files in arms().items():
        res[name] = run_arm(tmp, name, files)
        print("arm %-40s read=%s errors=%d %s" % (name, res[name]["read"], res[name]["errors"],
                                                 res[name]["msgs"][:1]))
    null = res["null"]["errors"]
    for name, r in res.items():
        print("RESULT %s_errors=%d count" % (name, r["errors"]))
    gaps = [n for n in res if n.startswith("gap_") and res[n]["errors"] == null]
    ctls = [n for n in res if n.startswith("control_") and res[n]["errors"] > null]
    print("RESULT controls_fired=%d count" % len(ctls))
    print("RESULT gap_arms_unmoved=%d count" % len(gaps))
    print("RESULT rulesets_read=%d count" % len(res["null"]["read"] or []))
    print("RESULT rulesets_on_repo=%d count" % len(load("rulesets_list.json")))
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print("RESULT thread_factor=%.3f ratio" % (tp / tt if tt else 1.0))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    sw = 0
    try:
        for l in open("/proc/vmstat"):
            if l.startswith("pswpin "):
                sw = int(l.split()[1])
    except OSError:
        pass
    print("RESULT swapins=%d count" % sw)


if __name__ == "__main__":
    sys.exit(main())
