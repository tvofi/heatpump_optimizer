#!/usr/bin/env python3
"""D11-s2: code a REQUIRED check executes from the pull request's own checkout,
outside the CODEOWNERS owner surface, and whether an edit to it flips the verdict.

Metric (one line): number of distinct tracked code files that a required-context
job executes from the PR checkout (entry scripts named in non-comment `run:` lines
plus their transitive local imports, minus files a prior step restores from the
base commit) which no CODEOWNERS pattern assigns an owner (last match wins).

Count key: the file path as `.claude/workflows/...` / `tests/...` resolved from the
import graph the production scripts themselves declare -- never a label the harness
assigns.

Second RESULT (dynamic): of those unowned files that `policy_lint.mjs` loads, how
many flip `pr-contract`'s own command (policy_lint.mjs --pr-body ...) on an EMPTY
body from rc=1 to rc=0 when one line is appended to the unowned file. Each
edit is reverted in `finally` and the file is checked byte-identical.

Null control: the same one-line append to a tracked file policy_lint.mjs does not
load (.claude/workflows/web-fix-wave.js) -> rc stays 1. The restored-from-base set
of `policy-docs`' grading steps is printed as the design contrast (not PR-editable).

Perturbation: add `/.claude/workflows/counts.mjs @tvofi`,
`/.claude/workflows/render_md.mjs @tvofi` and `/.claude/workflows/vendor/ @tvofi`
to .github/CODEOWNERS (or `--extra-owner PATH` repeated) -> unowned count goes to 0
for pr-contract and briefs (direction: to_zero).

Run (from the tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D11/s2_owner_closure.py [--no-dynamic] [--extra-owner PATH ...]
Expected at baseline cdf82da: unowned_required_closure=8 files (exact; 5 governance
  scripts + 3 test modules), pr_contract_flips=3 of 3 (exact),
  null_control_unloaded_file_rc=1 (exact). Perturbation arm with all 8 owned -> 0.
Machine: 4-vCPU cloud container (round 8 BASELINE.md); counts are contention-immune.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, fnmatch, glob, json, re, subprocess, sys, tempfile, time
import yaml

ROOT = os.getcwd()
WF = ".github/workflows"
FIXTURE = ".claude/workflows/fixtures/required-contexts.json"
TMP = os.environ.get("TMPDIR") or tempfile.gettempdir()


def owners_rules(extra):
    rules = []
    for line in open(".github/CODEOWNERS"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        rules.append((parts[0], parts[1:]))
    for p in extra:
        rules.append((p, ["@extra"]))
    return rules


def matches(pat, path):
    anchored = pat.startswith("/")
    p = pat.lstrip("/")
    if p.endswith("/"):
        return path.startswith(p) if anchored else ("/" + path).find("/" + p) >= 0
    if any(c in p for c in "*?["):
        return fnmatch.fnmatch(path, p) if anchored else fnmatch.fnmatch(os.path.basename(path), p)
    return path == p if anchored else path.endswith("/" + p) or path == p


def owned(path, rules):
    who = []
    for pat, o in rules:  # last matching pattern wins
        if matches(pat, path):
            who = o
    return bool(who)


def job_for_context(ctx, jobs):
    base = re.sub(r"\s*\(.*\)$", "", ctx)
    if ctx.startswith("Analyze ("):
        base = "analyze"
    for (wf, jn), j in jobs.items():
        name = j.get("name") or jn
        if jn == base or name == ctx or re.sub(r"\s*\(.*\)$", "", str(name)) == base:
            return (wf, jn)
    return None


ENTRY_RE = re.compile(r"(?:^|[\s\"'=(])((?:\./)?(?:\.claude|tests|tools|\.github)/[\w./-]+\.(?:mjs|js|py|sh))")
PY_HEREDOC_IMPORT = re.compile(r"^\s*(?:import|from)\s+([\w.]+)", re.M)


def js_imports(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    out = set()
    for m in re.finditer(r"""(?:from\s+|import\s*\(\s*|require\(\s*)['"](\.{1,2}/[^'"]+)['"]""", src):
        out.add(os.path.normpath(os.path.join(os.path.dirname(path), m.group(1))))
    return out


def py_imports(path, extra_dirs):
    src = open(path, encoding="utf-8", errors="replace").read()
    out = set()
    for m in PY_HEREDOC_IMPORT.finditer(src):
        mod = m.group(1).split(".")[0]
        for d in [os.path.dirname(path)] + extra_dirs:
            cand = os.path.normpath(os.path.join(d, mod + ".py"))
            if os.path.isfile(cand):
                out.add(cand)
    return out


def closure(entries):
    seen, todo = set(), list(entries)
    while todo:
        f = todo.pop()
        if f in seen or not os.path.isfile(f):
            continue
        seen.add(f)
        if f.endswith((".mjs", ".js")):
            todo += list(js_imports(f))
        elif f.endswith(".py"):
            todo += list(py_imports(f, ["tests"]))
    return seen


def strip_comments(run):
    return "\n".join(l for l in run.splitlines() if not l.lstrip().startswith("#"))


def job_closure(job):
    """Return (from_pr, from_base): files executed from the PR checkout vs from base."""
    restored = []  # globs restored from the base commit by an earlier step
    from_pr, from_base = set(), set()
    for st in job.get("steps", []):
        run = strip_comments(st.get("run", "") or "")
        m = re.search(r"git checkout\s+\"?\$\w+\"?\s+--\s+(.+)", run, re.S)
        if m:
            restored += re.findall(r"'([^']+)'", m.group(1))
            continue
        entries = {os.path.normpath(e) for e in ENTRY_RE.findall(run)}
        # a `python - <<PY` heredoc importing tests/ modules
        if "sys.path.insert(0, \"tests\")" in run:
            for mod in PY_HEREDOC_IMPORT.findall(run):
                c = os.path.join("tests", mod.split(".")[0] + ".py")
                if os.path.isfile(c):
                    entries.add(c)
        for f in closure(entries):
            rel = os.path.relpath(f, ROOT)
            base = any(fnmatch.fnmatch(rel, g) or rel.startswith(g.rstrip("/") + "/") for g in restored)
            (from_base if base else from_pr).add(rel)
    return from_pr, from_base


def tracked(path):
    return subprocess.run(["git", "ls-files", "--error-unmatch", path], capture_output=True).returncode == 0


def pr_contract_rc(tmp):
    body = os.path.join(tmp, "empty-body.md"); open(body, "w").close()
    files = os.path.join(tmp, "files.txt")
    open(files, "w").write("custom_components/heatpump_optimizer/const.py\n")
    r = subprocess.run(["node", ".claude/workflows/policy_lint.mjs", "--pr-body", body,
                        "--head", "cdf82da", "--title", "fix: x", "--author", "hpo-author",
                        "--paths-file", files], capture_output=True, text=True)
    return r.returncode


INJECT = "\n;{ const __hpoExit = process.exit; process.exit = () => __hpoExit(0) }\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra-owner", action="append", default=[])
    ap.add_argument("--no-dynamic", action="store_true")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    rules = owners_rules(a.extra_owner)
    jobs = {}
    for f in sorted(glob.glob(WF + "/*.yml")):
        d = yaml.safe_load(open(f))
        for jn, j in d["jobs"].items():
            jobs[(os.path.basename(f), jn)] = j
    ctxs = json.load(open(FIXTURE))["contexts"]
    req = {}
    for c in ctxs:
        k = job_for_context(c, jobs)
        if k:
            req.setdefault(k, []).append(c)
    unowned_all = set()
    graded_null = set()
    for k in sorted(req):
        from_pr, from_base = job_closure(jobs[k])
        code = sorted(p for p in from_pr if tracked(p))
        un = [p for p in code if not owned(p, rules)]
        print(f"JOB {k[0]}:{k[1]} contexts={req[k]} executed_from_pr={len(code)} "
              f"restored_from_base={len(from_base)} unowned={un}")
        unowned_all |= set(un)
        if k == ("governance.yml", "policy-docs"):
            graded_null = {p for p in from_base if not owned(p, rules)}
    tree_code = [p for p in subprocess.run(["git", "ls-files", ".claude/workflows/*.mjs", ".claude/workflows/*.js",
                  ".claude/workflows/vendor/*"], capture_output=True, text=True).stdout.split()]
    print("RESULT required_jobs_mapped=%d jobs" % len(req))
    print("RESULT required_contexts=%d contexts" % len(ctxs))
    print("RESULT unowned_required_closure=%d files" % len(unowned_all))
    for p in sorted(unowned_all):
        print("  UNOWNED", p)
    # null control: policy-docs's grading steps run base copies -> an unowned
    # file there cannot be changed by the PR; so the PR-editable count is 0.
    print(f"INFO policy-docs grading steps restored from base (not PR-editable): {sorted(graded_null)}")
    if not a.no_dynamic:
        base_rc = pr_contract_rc(TMP)
        print("RESULT pr_contract_rc_empty_body_unperturbed=%d" % base_rc)
        loaded = sorted(p for p in unowned_all
                        if p in closure({".claude/workflows/policy_lint.mjs"}) or
                        os.path.relpath(p) in {os.path.relpath(x) for x in closure({".claude/workflows/policy_lint.mjs"})})
        flips = 0
        for p in loaded:
            orig = open(p, "rb").read()
            try:
                open(p, "ab").write(INJECT.encode())
                rc = pr_contract_rc(TMP)
                print(f"  FLIP-ARM {p}: rc {base_rc} -> {rc}")
                flips += int(base_rc != 0 and rc == 0)
            finally:
                open(p, "wb").write(orig)
                assert open(p, "rb").read() == orig, p
        print("RESULT pr_contract_flips=%d of %d unowned files policy_lint.mjs loads" % (flips, len(loaded)))
        # NULL CONTROL: the same one-line append to a tracked .claude/workflows file
        # policy_lint.mjs does NOT load must leave rc unchanged (the flip is the
        # import, not the harness).
        ctl = ".claude/workflows/web-fix-wave.js"
        orig = open(ctl, "rb").read()
        try:
            open(ctl, "ab").write(INJECT.encode())
            rc = pr_contract_rc(TMP)
        finally:
            open(ctl, "wb").write(orig)
            assert open(ctl, "rb").read() == orig, ctl
        print("RESULT null_control_unloaded_file_rc=%d (must equal unperturbed %d)" % (rc, base_rc))
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print("RESULT thread_factor=%.3f" % (tp / tt if tt else 1.0))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print("RESULT swapins=%s" % sw)


if __name__ == "__main__":
    main()
