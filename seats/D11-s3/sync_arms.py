#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): one-character perturbation of every generated policy copy.

Metric: arms refused / arms run, where an arm is one file edited by one
  character in a private worktree and REFUSED means the production checker's
  --check exits non-zero:
    tools/policy/rules_sync.mjs --check      over dev/governance/rules/*.md,
                                             .claude/rules/*.md, .cursor/rules/*.mdc
                                             (+ one orphan .mdc, one deleted copy)
    tools/policy/fragments_sync.mjs --check  over every top-level `const NAME`
                                             fragment each .claude/workflows/web-*.js
                                             carries from web-fragments.md
  Count key: the checker's exit status on the edited tree, never the edit.
Null: each checker on the unedited worktree exits 0.
Expected: every arm refused (refused == arms), exact.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/sync_arms.py [--perturb]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
Perturbation (production, one line): `--perturb` makes fragments_sync.mjs's
  `if (got === want) continue` read `if (true) continue` in the worktree:
  fragment_refused falls 52 -> 0 (measured 2026-11-16); rules arms unchanged.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path.cwd()
NODE = os.environ.get("NODE", "/opt/node22/bin/node")


def git(wt, *a):
    return subprocess.run(["git", *a], cwd=wt, capture_output=True, text=True)


def check(wt, tool, env):
    r = subprocess.run([NODE, "tools/policy/%s" % tool, "--check"], cwd=wt, env=env,
                       capture_output=True, text=True, timeout=300)
    return r.returncode


def bend(text):
    """One character: the first ASCII letter after the first line becomes its case twin."""
    i = text.find("\n") + 1
    m = re.compile(r"[a-z]").search(text, i)
    if not m:
        return None
    j = m.start()
    return text[:j] + text[j].upper() + text[j + 1:]


def fragment_names(wt):
    raw = (wt / ".claude/workflows/web-fragments.md").read_text()
    block = re.search(r"\n```js\n([\s\S]*?)\n```\n", raw).group(1)
    return re.findall(r"^const (\w+)", block, re.M)


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    head = git(ROOT, "rev-parse", "HEAD").stdout.strip()
    if not head:
        raise SystemExit("needs a git checkout of the baseline")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s3-sync-"))
    wt = tmp / "wt"
    r = git(ROOT, "worktree", "add", "-q", "--detach", str(wt), head)
    if r.returncode:
        raise SystemExit(r.stderr)
    env = dict(os.environ, HPO_PLANDATA=str(tmp / "plandata"))
    (tmp / "plandata").mkdir()
    rows = []
    try:
        if "--perturb" in sys.argv:
            f = wt / "tools/policy/fragments_sync.mjs"
            s = f.read_text()
            assert s.count("      if (got === want) continue\n") == 1
            f.write_text(s.replace("      if (got === want) continue\n", "      if (true) continue\n"))
            print("PERTURBED: fragments_sync compares nothing")
        null_rules = check(wt, "rules_sync.mjs", env)
        null_frag = check(wt, "fragments_sync.mjs", env)
        print("null: rules_sync rc=%d fragments_sync rc=%d" % (null_rules, null_frag))

        def arm(name, tool, mutate):
            changed = mutate()
            if not changed:
                rows.append((name, tool, None))
                return
            rc = check(wt, tool, env)
            rows.append((name, tool, rc != 0))
            git(wt, "checkout", "-q", "--", ".")
            git(wt, "clean", "-qfd", "--", ".cursor", ".claude", "dev/governance")
            if "--perturb" in sys.argv:
                f = wt / "tools/policy/fragments_sync.mjs"
                s = f.read_text()
                if "      if (got === want) continue\n" in s:
                    f.write_text(s.replace("      if (got === want) continue\n", "      if (true) continue\n"))

        def edit(rel):
            def go():
                p = wt / rel
                t = bend(p.read_text())
                if t is None:
                    return False
                p.write_text(t)
                return True
            return go

        rule_files = sorted([p.relative_to(wt).as_posix() for d in ("dev/governance/rules", ".claude/rules")
                             for p in (wt / d).glob("*.md")]
                            + [p.relative_to(wt).as_posix() for p in (wt / ".cursor/rules").glob("*.mdc")])
        for rel in rule_files:
            arm("rules:" + rel, "rules_sync.mjs", edit(rel))

        def orphan():
            (wt / ".cursor/rules/d11s3-orphan.mdc").write_text("---\nalwaysApply: true\n---\nx\n")
            return True
        arm("rules:orphan .cursor/rules/d11s3-orphan.mdc", "rules_sync.mjs", orphan)

        def delete_copy():
            (wt / ".claude/rules/gate-scoping.md").unlink()
            return True
        arm("rules:deleted .claude/rules/gate-scoping.md", "rules_sync.mjs", delete_copy)

        names = fragment_names(wt)
        for script in sorted((wt / ".claude/workflows").glob("web-*.js")):
            rel = script.relative_to(wt).as_posix()
            text = script.read_text()
            for n in names:
                m = re.search(r"^const %s\b.*$" % re.escape(n), text, re.M)
                if not m:
                    continue

                def go(rel=rel, n=n):
                    p = wt / rel
                    t = p.read_text()
                    mm = re.search(r"^(const %s\b.*?)([a-z])" % re.escape(n), t, re.M)
                    if not mm:
                        return False
                    j = mm.start(2)
                    p.write_text(t[:j] + t[j].upper() + t[j + 1:])
                    return True
                arm("fragment:%s:%s" % (rel, n), "fragments_sync.mjs", go)
    finally:
        git(ROOT, "worktree", "remove", "--force", str(wt))
        shutil.rmtree(tmp, ignore_errors=True)
    ran = [r for r in rows if r[2] is not None]
    for name, tool, refused in rows:
        if refused is not True:
            print("NOT REFUSED: %s (%s) %s" % (name, tool, "did not apply" if refused is None else ""))
    rules = [r for r in ran if r[1] == "rules_sync.mjs"]
    frags = [r for r in ran if r[1] == "fragments_sync.mjs"]
    print("RESULT null_rules_rc=%d" % null_rules)
    print("RESULT null_fragments_rc=%d" % null_frag)
    print("RESULT rules_arms=%d count" % len(rules))
    print("RESULT rules_refused=%d count" % sum(r[2] for r in rules))
    print("RESULT fragment_arms=%d count" % len(frags))
    print("RESULT fragment_refused=%d count" % sum(r[2] for r in frags))
    print("RESULT arms_not_applied=%d count" % (len(rows) - len(ran)))
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
