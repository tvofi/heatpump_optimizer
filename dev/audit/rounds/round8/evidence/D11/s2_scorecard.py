#!/usr/bin/env python3
"""D11-s2: OpenSSF Scorecard checks evaluated by hand over the tree's workflows,
using Scorecard's own rule text as the bar (the tool cannot run here: no network
path to its API from the seat and no gh binary).

Metric (one line, the finding's): number of dependency-install commands in
non-comment `run:` lines of .github/workflows/*.yml that Scorecard's
Pinned-Dependencies check counts as unpinned -- `pip install` without
`--require-hashes` (a `-r FILE` is hash-pinned only if every line of FILE carries
`--hash=`), `npm install`/`npm i` (only `npm ci` counts as pinned), `npx`, and
`uses:` refs not pinned to a 40-hex commit.

Count key: the command text as the workflow YAML delivers it to the runner.

Other RESULT lines (scorecard rows, reported per check, never aggregated):
  token_permissions_top_level_write  -- top-level `permissions:` entries set to write
  dangerous_workflow_untrusted_run   -- untrusted free-text contexts (Scorecard's list:
                                        *.title, *.body, head_ref, *.label, commits
                                        messages, author email/name, head.ref) inside run:
  dangerous_workflow_triggers        -- pull_request_target / workflow_run triggers
  sast_workflows                     -- workflows invoking github/codeql-action/analyze
  security_policy_has_contact        -- SECURITY.md carries a URL or e-mail
  write_jobs_executing_pr_checkout   -- jobs with a write grant, running on pull_request,
                                        whose checkout is the PR head (OWASP LLM06 row)

Perturbation: `--perturb` appends ` --require-hashes` to the first `pip install -r`
line of tests.yml in memory before counting (the file is untouched) -> the
Pinned-Dependencies count goes down by exactly 1. The judge may make the same
one-line edit on disk.

Run (from the tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D11/s2_scorecard.py [--perturb]
Expected at baseline cdf82da: pinned_deps_unpinned=12 commands (exact), uses_unpinned=0.
Machine: 4-vCPU cloud container (round 8 BASELINE.md); counts are contention-immune.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, glob, re, sys, time
import yaml

UNTRUSTED = re.compile(r"github\.event\.(issue\.title|issue\.body|pull_request\.title|pull_request\.body|"
                       r"comment\.body|review\.body|review_comment\.body|pages\.[^ ]*page_name|"
                       r"commits\.[^ ]*message|head_commit\.message|head_commit\.author\.(email|name)|"
                       r"commits\.[^ ]*author\.(email|name)|pull_request\.head\.ref|pull_request\.head\.label|"
                       r"pull_request\.head\.repo\.default_branch)|github\.head_ref")


def strip_comments(s):
    return "\n".join(l for l in s.splitlines() if not l.lstrip().startswith("#"))


def req_file_hashed(path):
    try:
        lines = [l.strip() for l in open(path) if l.strip() and not l.lstrip().startswith("#")]
    except OSError:
        return False
    return bool(lines) and all("--hash=" in l for l in lines)


def pip_unpinned(cmd):
    if "--require-hashes" in cmd:
        return False
    m = re.search(r"-r\s+(\S+)", cmd)
    if m and not m.group(1).startswith("\"$") and req_file_hashed(m.group(1)):
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    unpinned, uses_unpinned, top_write, untrusted, bad_trig, sast, write_pr = [], [], [], [], [], 0, []
    perturbed = False
    for f in sorted(glob.glob(".github/workflows/*.yml")):
        d = yaml.safe_load(open(f))
        on = d.get(True, d.get("on")) or {}
        trig = list(on) if isinstance(on, dict) else ([on] if isinstance(on, str) else list(on))
        bad_trig += [f"{f}:{t}" for t in trig if t in ("pull_request_target", "workflow_run")]
        for k, v in (d.get("permissions") or {}).items() if isinstance(d.get("permissions"), dict) else []:
            if v == "write":
                top_write.append(f"{f}:{k}")
        for jn, j in d["jobs"].items():
            perms = j.get("permissions") if isinstance(j.get("permissions"), dict) else None
            has_write = any(v == "write" for v in (perms or {}).values())
            pr_checkout = False
            for st in j.get("steps", []):
                u = st.get("uses")
                if u:
                    if "@" in u and not re.search(r"@[0-9a-f]{40}$", u.split()[0]):
                        uses_unpinned.append(f"{f}:{jn}:{u}")
                    if "codeql-action/analyze" in u:
                        sast += 1
                    if u.startswith("actions/checkout") and "head_ref" in str((st.get("with") or {}).get("ref", "")):
                        pr_checkout = True
                run = strip_comments(st.get("run", "") or "")
                # join shell continuations so one command is one line
                run = re.sub(r"\\\n\s*", " ", run)
                for line in run.splitlines():
                    if UNTRUSTED.search(line):
                        untrusted.append(f"{f}:{jn}:{line.strip()[:80]}")
                    for m in re.finditer(r"(?:^|[;&|]\s*|\s)((?:\S*python\S*\s+-m\s+)?pip3?\s+install\s[^;&|]*)", line):
                        cmd = m.group(1)
                        if a.perturb and not perturbed and f.endswith("tests.yml") and "-r " in cmd:
                            cmd += " --require-hashes"; perturbed = True
                        if pip_unpinned(cmd):
                            unpinned.append(f"{f}:{jn}:{cmd.strip()[:70]}")
                    for m in re.finditer(r"\bnpm\s+(install|i)\b[^;&|]*|\bnpx\s[^;&|]*", line):
                        unpinned.append(f"{f}:{jn}:{m.group(0).strip()[:70]}")
            on_pr = "pull_request" in trig
            if has_write and on_pr and pr_checkout:
                write_pr.append(f"{f}:{jn}:{sorted(k for k, v in perms.items() if v == 'write')}")
    for u in unpinned:
        print("  UNPINNED", u)
    for u in write_pr:
        print("  WRITE+PR-CODE", u)
    for u in top_write:
        print("  TOP-LEVEL-WRITE", u)
    sec = open("SECURITY.md").read() if os.path.exists("SECURITY.md") else ""
    print("RESULT pinned_deps_unpinned=%d commands" % len(unpinned))
    print("RESULT uses_unpinned=%d refs" % len(uses_unpinned))
    print("RESULT token_permissions_top_level_write=%d grants" % len(top_write))
    print("RESULT dangerous_workflow_untrusted_run=%d lines" % len(untrusted))
    print("RESULT dangerous_workflow_triggers=%d" % len(bad_trig))
    print("RESULT sast_workflows=%d" % sast)
    print("RESULT security_policy_has_contact=%d" % int(bool(re.search(r"https?://|@\w+\.\w+", sec))))
    print("RESULT write_jobs_executing_pr_checkout=%d jobs" % len(write_pr))
    print("RESULT perturbed=%d" % int(perturbed))
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print("RESULT thread_factor=%.3f" % (tp / tt if tt else 1.0))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    print("RESULT swapins=%s" % sw)


if __name__ == "__main__":
    main()
