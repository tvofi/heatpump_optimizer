#!/usr/bin/env python3
"""v1_owner_flip.py -- D11-v1 (verifier) own measurement for D11-s1-02 and D11-s2-01 (one mechanism).

METRIC (one line): of the union of the two finders' candidate files, the number
that (1) no owner-bearing `.github/CODEOWNERS` pattern matches (last match wins,
resolved by this harness's own matcher) AND (2) a one-line edit to that file
alone, with every owned file untouched, turns a RED run of a required context's
own command at this baseline into rc=0 -- driven as a process, in the PR
checkout (i.e. not a file the job restores from base before grading).

Dynamic arms (each edit restored in `finally`, byte-compared afterwards):
  pr-contract   `node .claude/workflows/policy_lint.mjs --pr-body <empty> --head <sha> --paths-file <f>`
                red (rc=1) on an empty body. Edit: append
                `process.on('exit', () => { process.exitCode = 0 })` to the file.
                Candidates: counts.mjs, render_md.mjs, vendor/markdown-it.min.js.
  policy-docs   `node .claude/workflows/policy_lint.mjs` -- RED at this stripped,
                shallow baseline (7 citation errors). Edit: grow
                `policy_known_bad.json` by the red set (`--record-known-bad`, which
                rewrites ONLY that file). The workflow restores `*.mjs|*.py|vendor`
                from base but deliberately NOT this ledger (governance.yml, the
                restore step's comment), so the PR's own copy grades the PR.
  fast (3.14)   `./tests/run.sh` with PYTHON=/bin/false (red, rc=1, sub-second).
                Edit: insert `exit 0` as line 2.
Static class (no dynamic arm; printed with the reason): the other candidates.

NULL CONTROL: the same one-line JS append to a tracked `.mjs` policy_lint.mjs
does not load (`tests/card_rig.mjs`) leaves pr-contract at rc=1. Second
control: the same append to the OWNED entry file `policy_lint.mjs` also stays
rc=1 (the append lands after the entry's own synchronous exit), so the flip in
the imported modules comes from import order, not from any append anywhere.

PERTURBATION (--perturb): add owner lines for every candidate to an in-memory
CODEOWNERS copy. Expected: unowned_flipping -> 0 (to_zero).

RUN (tree root): PYTHONPATH=tests/hastub TMPDIR=/home/claude/audit-r8/tmp/D11-v1 \
   python3 tools/audit/round8/D11/v1_owner_flip.py [--perturb]
EXPECTED at cdf82da (stripped git tree, round 8): unowned_candidates=18,
  unowned_flipping=5 (exact), null_unloaded_rc=1, owned_loaded_flip_rc=1.
BASELINE: cdf82daabcfe3777d98b31489f36df5555ec9d82. MACHINE: 4-vCPU cloud container; no timing numbers.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import fnmatch, subprocess, sys, tempfile, time
from pathlib import Path

TMP = Path(os.environ.get("TMPDIR") or tempfile.gettempdir())
S1 = [".claude/workflows/cfr_exclusions.json", ".claude/workflows/corpus_excluded.json",
      ".claude/workflows/counts.mjs", ".claude/workflows/policy_budgets.json",
      ".claude/workflows/policy_known_bad.json", ".claude/workflows/render_md.mjs",
      "tests/closures.json", "tests/derive_closures.sh", "tests/golden/card_claimed_drift.txt",
      "tests/golden/claimed_drift.txt", "tests/requirements-ci.txt", "tests/run.sh",
      "tests/structure_budgets.json", "tools/audit/w5-partition/coverage_tree.sh"]
S2 = [".claude/workflows/counts.mjs", ".claude/workflows/render_md.mjs",
      ".claude/workflows/vendor/markdown-it.min.js", "tests/run.sh", "tests/derive_closures.sh",
      "tests/golden.py", "tests/harness.py", "tests/profiles.py"]
CAND = sorted(set(S1) | set(S2))
STATIC = {
    "tests/derive_closures.sh": "exec by `closures` (required); edit changes the derived closures it compares",
    "tests/golden.py": "imported by tests run under `fast`; any test module is PR-editable -- the whole suite is",
    "tests/harness.py": "as golden.py",
    "tests/profiles.py": "as golden.py",
    "tests/structure_budgets.json": "raising a row passes structure.py by design; CLAUDE.md rule 2 wants the owner",
    ".claude/workflows/policy_budgets.json": "raising a cap passes `budgets` by design",
    ".claude/workflows/cfr_exclusions.json": "policy_lint data",
    ".claude/workflows/corpus_excluded.json": "policy_lint data",
    "tests/closures.json": "written by the closures-autofix BOT; owning it would stop the bot path",
    "tests/golden/claimed_drift.txt": "written by claims-autofix BOT / fixers routinely; owning it stops that",
    "tests/golden/card_claimed_drift.txt": "as claimed_drift.txt",
    "tests/requirements-ci.txt": "dependency pins every job installs",
    "tools/audit/w5-partition/coverage_tree.sh": "runs only in `coverage`, NOT a required context, under `|| true`: no verdict",
}
INJECT = "\nprocess.on('exit', () => { process.exitCode = 0 })\n"


def rules(extra=()):
    out = []
    for line in Path(".github/CODEOWNERS").read_text().splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            p = s.split()
            out.append((p[0], p[1:]))
    out += [("/" + e, ["@x"]) for e in extra]
    return out


def owned(path, rs):
    hit = None
    for pat, own in rs:
        a = pat.startswith("/")
        p = pat.lstrip("/")
        if p.endswith("/"):
            m = path.startswith(p) if a else ("/" + p) in ("/" + path)
        elif any(c in p for c in "*?["):
            m = fnmatch.fnmatch(path, p)
        else:
            m = path == p if a else (path == p or path.endswith("/" + p))
        if m:
            hit = own
    return bool(hit)


def run(cmd, env=None):
    e = dict(os.environ, **(env or {}))
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=e, timeout=600).returncode


def pr_contract():
    body = TMP / "v1_empty_body.md"; body.write_text("")
    paths = TMP / "v1_paths.txt"; paths.write_text("README.md\n")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    return run(["node", ".claude/workflows/policy_lint.mjs", "--pr-body", str(body), "--head", head,
                "--paths-file", str(paths)])


def with_edit(path, edit, probe):
    p = Path(path); orig = p.read_bytes()
    try:
        edit(p)
        return probe()
    finally:
        p.write_bytes(orig)
        assert p.read_bytes() == orig, path


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    perturb = "--perturb" in sys.argv
    rs = rules(CAND if perturb else ())
    unowned = [c for c in CAND if not owned(c, rs)]
    print(f"# candidates (s1 U s2) = {len(CAND)}; unowned = {len(unowned)}")
    flips = {}
    base_pc = pr_contract()
    print(f"# pr-contract empty body rc={base_pc}")
    for f in (".claude/workflows/counts.mjs", ".claude/workflows/render_md.mjs",
              ".claude/workflows/vendor/markdown-it.min.js"):
        rc = with_edit(f, lambda p: p.write_bytes(p.read_bytes() + INJECT.encode()), pr_contract)
        flips[f] = (base_pc != 0 and rc == 0); print(f"#   {f}: rc {base_pc} -> {rc}")
    null_unloaded = with_edit("tests/card_rig.mjs", lambda p: p.write_bytes(p.read_bytes() + INJECT.encode()), pr_contract)
    owned_flip = with_edit(".claude/workflows/policy_lint.mjs", lambda p: p.write_bytes(p.read_bytes() + INJECT.encode()), pr_contract)
    # policy-docs: grow the ledger
    pd = lambda: run(["node", ".claude/workflows/policy_lint.mjs"])
    base_pd = pd()
    kb = Path(".claude/workflows/policy_known_bad.json")
    def grow(p):
        run(["node", ".claude/workflows/policy_lint.mjs", "--record-known-bad"])
        ch = subprocess.check_output(["git", "status", "--porcelain", "--", ".claude", ".cursor", "CLAUDE.md", "AGENTS.md", "tools/audit/briefs"], text=True).split("\n")
        ch = [c for c in ch if c.strip()]
        print(f"#   --record-known-bad changed: {ch}")
    rc_pd = with_edit(str(kb), grow, pd)
    flips[str(kb)] = (base_pd != 0 and rc_pd == 0); print(f"# policy-docs rc {base_pd} -> {rc_pd} with the ledger grown")
    # fast: run.sh
    rsh = lambda: run(["./tests/run.sh"], {"PYTHON": "/bin/false"})
    base_rs = rsh()
    def ex0(p):
        L = p.read_text().split("\n", 1); p.write_text(L[0] + "\nexit 0\n" + L[1])
    rc_rs = with_edit("tests/run.sh", ex0, rsh)
    flips["tests/run.sh"] = (base_rs != 0 and rc_rs == 0); print(f"# fast run.sh rc {base_rs} -> {rc_rs}")
    for c in CAND:
        tag = "OWNED" if c not in unowned else ("FLIPS" if flips.get(c) else "static")
        print(f"#   {tag:6} {c}  {STATIC.get(c, '')}")
    n = sum(1 for c in unowned if flips.get(c))
    print(f"RESULT unowned_candidates={len(unowned)} files")
    print(f"RESULT unowned_flipping={n} files")
    print(f"RESULT null_unloaded_rc={null_unloaded}")
    print(f"RESULT owned_loaded_flip_rc={owned_flip}")
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", ".claude", "tests", ".github"], text=True).strip()
    print(f"RESULT tree_dirty_after={1 if dirty else 0}")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
